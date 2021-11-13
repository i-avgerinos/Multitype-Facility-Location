import cplex
from cplex.exceptions import CplexSolverError
import sys
import random
import math
import itertools
import time
import datetime
import heapq

num_clients = 500
num_locations = 20
num_types = 20
num_copies = 10
num_bands = 5

######### Random data generators ###############################################################################

######### Demand generator #####################################################################################
demand = []
for i in range(num_clients):
	demand.append(random.randint(1,100))
total_demand = 0
for i in range(num_clients):
	total_demand = total_demand + demand[i]

######### Band intervals generator #############################################################################
lower_bound = []
lb = 1
for l in range(num_types):
	lower_bound.append([])
	for m in range(num_bands):
		lower_bound[l].append(lb+m*600)
upper_bound = []
ub = 600
for l in range(num_types):
	upper_bound.append([])
	for m in range(num_bands):
		upper_bound[l].append(ub+m*600)

######### Service/Production cost function #####################################################################
def production_cost_function(x, l):
	b = random.Random(l).uniform(0.1, 0.4)
	if x == 0:
		y = 0
	else:
		y = (b*math.pow(0.9,math.log(x,2)))*x
	return y

######### Setup cost function ##################################################################################
def setup_cost_function(x, j, l):
	b1 = random.Random(j).uniform(100, 450)
	b2 = random.Random(l).uniform(0, 50)
	if x == 0:
		y = 0
	else:
		y = ((b1+b2)*math.pow(0.9,math.log(x,2)))*x
	return y

######### Production/Service cost linearization ################################################################
production_cost = []
for l in range(num_types):
	production_cost.append([])
	for m in range(num_bands):
		production_cost[l].append(production_cost_function(upper_bound[l][m], l)/upper_bound[l][m])

facility_number = []
for j in range(num_locations):
	facility_number.append([])
	for n in range(1,num_copies+1):
		facility_number[j].append(n)

######### Setup cost linearization #############################################################################
setup_cost = []
for j in range(num_locations):
	setup_cost.append([])
	for l in range(num_types):
		setup_cost[j].append([])
		for n in range(1, num_copies+1):
			setup_cost[j][l].append(round(setup_cost_function(n, j, l),2))

######### Transportation cost generator ########################################################################
transport_cost = []
for i in range(num_clients):
	transport_cost.append([])
	for j in range(num_locations):
		cost1 = random.Random(i).uniform(0.05, 0.2)
		cost2 = random.Random(j).uniform(0.05, 0.2)
		transport_cost[i].append(cost1 + cost2)

######### Opening cost generator ###############################################################################
opening_cost = []
for j in range(num_locations):
	opening_cost.append(10*random.randint(75, 250))

######### Location capacities ##################################################################################
capacity = []
for j in range(num_locations):
	capacity.append(random.Random(j).randint(5000, 14000))

######### Facility capacities ##################################################################################
facility_cap = []
for l in range(num_types):
	facility_cap.append(random.Random(l).randint(1000, 3000))

######### SingleStage Greedy Algorithm #########################################################################
print("Searching for an upper bound . . . . . . .")
start_model = time.time()

clients = []
assignments = []
for i in range(num_clients):
	clients.append(i)
	assignments.append([])
	for n in range(3):
		assignments[i].append(None)

facilities = []
service = []
for l in range(num_types):
	facilities.append([])
	service.append([])
	for c in range(num_copies):
		facilities[l].append(None)
		service[l].append(0)

locations = []
volume = []
level = []
for j in range(num_locations):
	locations.append(False)
	volume.append(0)
	level.append([])
	for l in range(num_types):
		level[j].append(0)

t = 0
while len(clients) > 0:
	initial_len = len(clients)
	iteration_costs = []
	heapq.heapify(iteration_costs)

	contribution = []
	for i in range(len(clients)):
		contribution.append(t)

	for j in range(num_locations):
		if locations[j] == True:
			for l in range(num_types):
				for c in range(num_copies):
					if facilities[l][c] == j:
						loop_assignments = []
						for i in range(len(clients)):
							if service[l][c] + demand[clients[i]] <= facility_cap[l] and volume[j] + demand[clients[i]] <= capacity[j]:
								cost = int(production_cost_function(service[l][c] + demand[i], l)) - int(production_cost_function(service[l][c], l)) + int(transport_cost[clients[i]][j]*demand[clients[i]])
								cost = int(0.1*cost)
								heapq.heappush(iteration_costs,cost)
								#print(str(contribution[i])+" "+str(cost))
								if contribution[i] == cost:
									loop_assignments.append(clients[i])
									assignments[clients[i]][0] = l
									assignments[clients[i]][1] = c
									assignments[clients[i]][2] = j
									volume[j] = volume[j] + demand[clients[i]]
									service[l][c] = service[l][c] + demand[clients[i]]
						for n in range(len(loop_assignments)):
							clients.remove(loop_assignments[n])
					if facilities[l][c] == None:
						loop_assignments = []
						for i in range(len(clients)):
							if service[l][c] + demand[clients[i]] <= facility_cap[l] and volume[j] + demand[clients[i]] <= capacity[j]:
								cost = int(production_cost_function(service[l][c] + demand[i], l)) - int(production_cost_function(service[l][c], l)) + int(setup_cost_function(level[j][l]+1, j, l)) - int(setup_cost_function(level[j][l], j, l)) + int(transport_cost[clients[i]][j]*demand[clients[i]])
								cost = int(0.1*cost)
								heapq.heappush(iteration_costs,cost)
								#print(str(contribution[i])+" "+str(cost))
								if contribution[i] == cost:
									loop_assignments.append(clients[i])
									assignments[clients[i]][0] = l
									assignments[clients[i]][1] = c
									assignments[clients[i]][2] = j
									volume[j] = volume[j] + demand[clients[i]]
									service[l][c] = service[l][c] + demand[clients[i]]
						if len(loop_assignments) > 0:
							facilities[l][c] = j
							level[j][l] = level[j][l] + 1
						for n in range(len(loop_assignments)):
							clients.remove(loop_assignments[n])
		if locations[j] == False:
			for l in range(num_types):
				for c in range(num_copies):
					if facilities[l][c] == None:
						budget = 0
						budget_demand = 0
						for i in range(len(clients)):
							if service[l][c] + budget_demand + demand[clients[i]] <= facility_cap[l] and volume[j] + budget_demand + demand[clients[i]] <= capacity[j]:
								cost = int(production_cost_function(service[l][c] + demand[i], l)) - int(production_cost_function(service[l][c], l)) + int(setup_cost_function(level[j][l]+1, j, l)) - int(setup_cost_function(level[j][l], j, l)) + int(transport_cost[clients[i]][j]*demand[clients[i]])
								cost = int(0.1*cost)
								heapq.heappush(iteration_costs,cost)
								#print(str(contribution[i])+" "+str(cost))
								if contribution[i] >= cost:
									budget = budget + cost
									budget_demand = budget_demand + demand[clients[i]]
						if budget >= int(opening_cost[j]):
							loop_assignments = []
							for i in range(len(clients)):
								if contribution[i] >= cost:
									if service[l][c] + demand[clients[i]] <= facility_cap[l] and volume[j] + demand[clients[i]] <= capacity[j]:
										loop_assignments.append(clients[i])
										assignments[clients[i]][0] = l
										assignments[clients[i]][1] = c
										assignments[clients[i]][2] = j
										volume[j] = volume[j] + demand[clients[i]]
										service[l][c] = service[l][c] + demand[clients[i]]
							if len(loop_assignments) > 0:
								facilities[l][c] = j
								locations[j] = True
								level[j][l] = level[j][l] + 1
							for n in range(len(loop_assignments)):
								clients.remove(loop_assignments[n])

	final_len = len(clients)

	if final_len != initial_len:
		#print clients
		t = heapq.heappop(iteration_costs)
	#if final_len == initial_len:
	t = t + 1
	if t == 1:
		t = heapq.heappop(iteration_costs)

end_model = time.time()

######### SingleStage solution calculation #####################################################################
singlestage_cost = 0
ss_opening = 0
for j in range(num_locations):
	if locations[j] == True:
		ss_opening = ss_opening + opening_cost[j]
ss_service = 0
for l in range(num_types):
	for c in range(num_copies):
		ss_service = ss_service + round(production_cost_function(service[l][c], l),2)
ss_setup = 0
for j in range(num_locations):
	for l in range(num_types):
		ss_setup = ss_setup + round(setup_cost_function(level[j][l], j, l),2)
ss_transport = 0
for i in range(num_clients):
	ss_transport = ss_transport + int(transport_cost[i][assignments[i][2]]*demand[i])
singlestage_cost = ss_opening + ss_service + ss_setup + ss_transport

clients = []
for i in range(num_clients):
	clients.append(assignments[i])
locations = []
for j in range(num_locations):
	locations.append([])
	for l in range(num_types):
		for c in range(num_copies):
			if facilities[l][c] == j:
				locations[j].append([l,c])	
location_vol = []
for j in range(num_locations):
	location_vol.append(volume[j])
for l in range(num_types):
	for c in range(num_copies):
		if facilities[l][c] == None:
			facilities[l][c] = False
fac_vol = []
for l in range(num_types):
	fac_vol.append([])
	for c in range(num_copies):
		fac_vol[l].append(service[l][c])

print("------------------------------------------------------------------")
print(("Solution before LS: "+str(round(singlestage_cost,2)))+" in "+str(round(end_model - start_model,2))+" seconds")
print("------------------------------------------------------------------")

######### Meta-heuristic - GreedyVND ###########################################################################
start_model = time.time()


######### Stage 2: Facility Types Neighborhoods ################################################################
assigned_facilities = []
for l in range(num_types):
	assigned_facilities.append([])
	for c in range(num_copies):
		if fac_vol[l][c] > 0:
			assigned_facilities[l].append(True)
		if fac_vol[l][c] == 0:
			assigned_facilities[l].append(False)

iteration = 0
while(iteration < 50):
	better_solution = 0
	for j in range(num_locations):
		if len(locations[j]) > 0:
			for m in range(len(locations[j])):
				for l in range(num_types):
					for c in range(num_copies):
						if assigned_facilities[l][c] == False:
							cost = 0
							if l != locations[j][m][0]:
								cost = cost + setup_cost_function(level[j][l] + 1, j, l) - setup_cost_function(level[j][l], j, l) + setup_cost_function(level[j][locations[j][m][0]] - 1, j, locations[j][m][0]) - setup_cost_function(level[j][locations[j][m][0]], j, locations[j][m][0])
							cost = cost + production_cost_function(fac_vol[locations[j][m][0]][locations[j][m][1]], l) - production_cost_function(fac_vol[locations[j][m][0]][locations[j][m][1]], locations[j][m][0])
							if cost < 0 and facility_cap[l] >= fac_vol[locations[j][m][0]][locations[j][m][1]]:
								assigned_facilities[l][c] = True
								assigned_facilities[locations[j][m][0]][locations[j][m][1]] = False

								fac_vol[l][c] = fac_vol[locations[j][m][0]][locations[j][m][1]]
								fac_vol[locations[j][m][0]][locations[j][m][1]] = 0

								for i in range(num_clients):
									if assignments[i][0] == locations[j][m][0] and assignments[i][1] == locations[j][m][1]:
										assignments[i][0] = l
										assignments[i][1] = c

								facilities[l][c] = j
								facilities[locations[j][m][0]][locations[j][m][1]] = False

								if l != locations[j][m][0]:
									level[j][l] = level[j][l] + 1
									level[j][locations[j][m][0]] = level[j][locations[j][m][0]] - 1

								locations[j][m][0] = l
								locations[j][m][1] = c

								better_solution = better_solution + 1
								break
					if better_solution == 3:
						break
				if better_solution == 3:
					break
		if better_solution == 3:
			break
	iteration = iteration + 1
	if better_solution == 3:
		iteration = 50

ss_opening = 0
for j in range(num_locations):
	if location_vol[j] > 0:
		ss_opening = ss_opening + round(opening_cost[j],2)
ss_transport = 0
for i in range(num_clients):
	ss_transport = ss_transport + round(transport_cost[i][assignments[i][2]]*demand[i],2)
ss_setup = 0
for j in range(num_locations):
	for l in range(num_types):
		ss_setup = ss_setup + round(setup_cost_function(level[j][l], j, l),2)
ss_service = 0
for l in range(num_types):
	for c in range(num_copies):
		ss_service = ss_service + round(production_cost_function(fac_vol[l][c], l),2)
if singlestage_cost > ss_opening + ss_setup + ss_transport + ss_service:
	print(("Local Search (Stage 2) found a better solution: "+str(ss_opening + ss_setup + ss_transport + ss_service)))
	print(("Cost reduced by "+str(round(100*(singlestage_cost - (ss_opening + ss_setup + ss_transport + ss_service))/singlestage_cost,2))+" %"))
	singlestage_cost = ss_opening + ss_setup + ss_transport + ss_service
	print("-------------------------------------------------------------")
######### Stage 1: Location Neighborhoods ######################################################################
potential_locations = []
for j in range(num_locations):
	potential_locations.append(j)
combinations = []
for j in range(len(potential_locations)+1):
	for subset in itertools.combinations(potential_locations,j):
		combinations.append(subset)

feasible_neighborhoods = []
for l in range(len(combinations)):
	total_capacity = 0
	feasible_neighborhoods.append([])
	for s in range(len(combinations[l])):
		if total_capacity + capacity[combinations[l][s]] >= total_demand:
			feasible_neighborhoods[l].append(combinations[l][s])
			total_capacity = total_capacity + capacity[combinations[l][s]]
			break
		if total_capacity + capacity[combinations[l][s]] < total_demand:
			feasible_neighborhoods[l].append(combinations[l][s])
			total_capacity = total_capacity + capacity[combinations[l][s]]
new_neighborhoods = []
for l in feasible_neighborhoods:
	if l not in new_neighborhoods:
		new_neighborhoods.append(l)

neighborhoods = []
for s in range(len(new_neighborhoods)):
	sum = 0
	if len(new_neighborhoods) > 0:
		for l in range(len(new_neighborhoods[s])):
			sum = sum + capacity[new_neighborhoods[s][l]]
		if sum >= total_demand:
			neighborhoods.append(new_neighborhoods[s])

better_solution = 0
for s in range(len(neighborhoods)):
	cost = 0
	unassigned_clients = []
	for i in range(num_clients):
		unassigned_clients.append(False)
	new_volume = []
	for j in range(num_locations):
		new_volume.append(0)
	new_level = []
	for j in range(num_locations):
		new_level.append([])
		for l in range(num_types):
			new_level[j].append(0)
	new_locations = []
	for j in range(num_locations):
		new_locations.append([])
	t_costs = []
	while any(unassigned_clients[i] == False for i in range(num_clients)):
		for i in range(num_clients):
			t_costs.append([])
			for j in range(len(neighborhoods[s])):
				if new_volume[neighborhoods[s][j]] + demand[i] <= capacity[neighborhoods[s][j]] and unassigned_clients[i] == False:
					t_costs[i].append(transport_cost[i][neighborhoods[s][j]])
			for j in range(len(neighborhoods[s])):
				if transport_cost[i][neighborhoods[s][j]] == min(t_costs[i]) and new_volume[neighborhoods[s][j]] + demand[i] <= capacity[neighborhoods[s][j]]:
					new_volume[neighborhoods[s][j]] = new_volume[neighborhoods[s][j]] + demand[i]
					cost = cost + transport_cost[i][neighborhoods[s][j]]*demand[i]
					unassigned_clients[i] = True
					if [assignments[i][0], assignments[i][1]] not in new_locations[neighborhoods[s][j]]:
						new_locations[neighborhoods[s][j]].append([assignments[i][0], assignments[i][1]])
	for j in range(num_locations):
		for m in range(len(new_locations[j])):
			new_level[j][new_locations[j][m][0]] = new_level[j][new_locations[j][m][0]] + 1
	for j in range(num_locations):
		for l in range(num_types):
			cost = cost + setup_cost_function(new_level[j][l], j, l)
	for j in range(num_locations):
		if new_volume[j] > 0:
			cost = cost + opening_cost[j]
	if cost < ss_transport + ss_opening + ss_setup:
		level = new_level
		location_vol = new_volume
		locations = new_locations
		facilities = []
		for l in range(num_types):
			facilities.append([])
			for c in range(num_copies):
				facilities[l].append(None)
				for j in range(num_locations):
					for m in range(len(locations[j])):
						if locations[j][m] == [l,c]:
							facilities[l][c] = j
		for i in range(num_clients):
			assignments[i][2] = facilities[assignments[i][0]][assignments[i][1]]
		ss_opening = 0
		for j in range(num_locations):
			if location_vol[j] > 0:
				ss_opening = ss_opening + round(opening_cost[j],2)
		ss_transport = 0
		for i in range(num_clients):
			ss_transport = ss_transport + round(transport_cost[i][assignments[i][2]]*demand[i],2)
		ss_setup = 0
		for j in range(num_locations):
			for l in range(num_types):
				ss_setup = ss_setup + round(setup_cost_function(level[j][l], j, l),2)
		iteration = iteration + 1
		better_solution = better_solution + 1
	else:
		iteration = iteration + 1
	if better_solution == 3:
		break

if better_solution == 3:
	print(("Local Search (Stage 1) found a better solution: "+str(ss_opening + ss_setup + ss_transport + ss_service)))
	print(("Cost reduced by "+str(round(100*(singlestage_cost - (ss_opening + ss_setup + ss_transport + ss_service))/singlestage_cost,2))+" %"))
	singlestage_cost = ss_opening + ss_setup + ss_transport + ss_service
	print("-------------------------------------------------------------")		
######### Stage 3: Improved Client Assignment ##################################################################
iteration = 0
while(iteration < num_clients):
	client_costs = []
	for i in range(num_clients):
		client_costs.append([])
		for l in range(num_types):
			client_costs[i].append([])
			for c in range(num_copies):
				client_costs[i][l].append(0)
	for i in range(num_clients):
		for l in range(num_types):
			for c in range(num_copies):
				if assigned_facilities[l][c] == False:
					client_costs[i][l][c] = 10000
				if assigned_facilities[l][c] == True:
					if assignments[i][0] == l and assignments[i][1] == c:
						if assignments[i][2] == facilities[l][c]:
							client_costs[i][l][c] = 0
					if assignments[i][0] != l or assignments[i][1] != c:
						if fac_vol[l][c] + demand[i] > facility_cap[l]:
							client_costs[i][l][c] = 10000
						if fac_vol[l][c] + demand[i] <= facility_cap[l]:
							if assignments[i][2] == facilities[l][c]:
								client_costs[i][l][c] = client_costs[i][l][c] + production_cost_function(fac_vol[l][c] + demand[i], l) - production_cost_function(fac_vol[l][c], l)
								client_costs[i][l][c] = client_costs[i][l][c] + production_cost_function(fac_vol[assignments[i][0]][assignments[i][1]] - demand[i], assignments[i][0]) - production_cost_function(fac_vol[assignments[i][0]][assignments[i][1]], assignments[i][0])
								if fac_vol[assignments[i][0]][assignments[i][1]] - demand[i] == 0 and level[assignments[i][2]][assignments[i][0]] - 1 >= 0:
									client_costs[i][l][c] = client_costs[i][l][c] + setup_cost_function(level[assignments[i][2]][assignments[i][0]] - 1, assignments[i][2], assignments[i][0]) - setup_cost_function(level[assignments[i][2]][assignments[i][0]], assignments[i][2], assignments[i][0])
									if location_vol[assignments[i][2]] - demand[i] == 0:
										client_costs[i][l][c] = client_costs[i][l][c] - opening_cost[assignments[i][2]]
							if assignments[i][2] != facilities[l][c] and location_vol[facilities[l][c]] + demand[i] > capacity[facilities[l][c]]:
								client_costs[i][l][c] = 10000
							if assignments[i][2] != facilities[l][c] and location_vol[facilities[l][c]] + demand[i] <= capacity[facilities[l][c]]:
								client_costs[i][l][c] = client_costs[i][l][c] + production_cost_function(fac_vol[l][c] + demand[i], l) - production_cost_function(fac_vol[l][c], l)
								client_costs[i][l][c] = client_costs[i][l][c] + production_cost_function(fac_vol[assignments[i][0]][assignments[i][1]] - demand[i], assignments[i][0]) - production_cost_function(fac_vol[assignments[i][0]][assignments[i][1]], assignments[i][0])
								client_costs[i][l][c] = client_costs[i][l][c] + transport_cost[i][facilities[l][c]]*demand[i] - transport_cost[i][assignments[i][2]]*demand[i]


	better_solution = False
	for i in range(num_clients):
		for l in range(num_types):
			for c in range(num_copies):
				if client_costs[i][l][c] == min(client_costs[i][x][y] for x in range(num_types) for y in range(num_copies)) and client_costs[i][l][c] < 0:
					fac_vol[l][c] = fac_vol[l][c] + demand[i]
					fac_vol[assignments[i][0]][assignments[i][1]] = fac_vol[assignments[i][0]][assignments[i][1]] - demand[i]
					if fac_vol[assignments[i][0]][assignments[i][1]] == 0:
						level[assignments[i][2]][assignments[i][0]] = level[assignments[i][2]][assignments[i][0]] - 1
						if [assignments[i][0],assignments[i][1]] in locations[j]:
							locations[j].remove([assignments[i][0],assignments[i][1]])
					location_vol[facilities[l][c]] = location_vol[facilities[l][c]] + demand[i]
					location_vol[assignments[i][2]] = location_vol[assignments[i][2]] - demand[i]
					assignments[i][0] = l
					assignments[i][1] = c
					assignments[i][2] = facilities[l][c]
					better_solution = True
					break
			if better_solution == True:
				break
		if better_solution == True:
			break
	if better_solution == True:
		iteration = iteration + 1
	if better_solution == False:
		iteration = num_clients
ss_opening = 0
for j in range(num_locations):
	if location_vol[j] > 0:
		ss_opening = ss_opening + round(opening_cost[j],2)
ss_transport = 0
for i in range(num_clients):
	ss_transport = ss_transport + round(transport_cost[i][assignments[i][2]]*demand[i],2)
level = []
for j in range(num_locations):
	level.append([])
	for l in range(num_types):
		level[j].append(0)
test_locations = []
for j in range(num_locations):
	test_locations.append([])
	if facilities[l][c] == j:
		test_locations[j].append([l,c])

for j in range(num_locations):
	if len(test_locations[j]) > 0:
		for m in range(len(test_locations[j])):
			for l in range(num_types):
				for c in range(num_copies):
					if fac_vol[l][c] == 0 and test_locations[j][m][0] == l and test_locations[j][m][1] == c:
						if [l,c] in locations[j]:
							locations[j].remove([l,c])
for j in range(num_locations):
	for m in range(len(locations[j])):
		for l in range(num_types):
			if locations[j][m][0] == l:
				level[j][l] = level[j][l] + 1

ss_setup = 0
for j in range(num_locations):
	for l in range(num_types):
		ss_setup = ss_setup + round(setup_cost_function(level[j][l], j, l),2)
ss_service = 0
for l in range(num_types):
	for c in range(num_copies):
		ss_service = ss_service + round(production_cost_function(fac_vol[l][c], l),2)

if singlestage_cost > ss_opening + ss_setup + ss_transport + ss_service:
	print(("Local Search (Stage 3) found a better solution: "+str(ss_opening + ss_setup + ss_transport + ss_service)))
	print(("Cost reduced by "+str(round(100*(singlestage_cost - (ss_opening + ss_setup + ss_transport + ss_service))/singlestage_cost,2))+" %"))
	singlestage_cost = ss_opening + ss_setup + ss_transport + ss_service
	print("-------------------------------------------------------------")
end_model = time.time()
print((str(round(end_model - start_model,2))))
