
import cplex
from cplex.exceptions import CplexSolverError
import sys
import random
import math
import itertools
import time
import datetime
import heapq
from cplex.callbacks import HeuristicCallback


num_clients = 500
num_locations = 20
num_types = 20
num_copies = 10
num_bands = 5

clients = []
for i in range(num_clients):
	clients.append(i)
locations = []
for j in range(num_locations):
	locations.append(j)
types = []
for l in range(num_types):
	types.append(l)
copies = []
for c in range(num_copies):
	copies.append(c)
bands = []
for m in range(num_bands):
	bands.append(m)

demand = [53, 92, 86, 69, 38, 57, 63, 6, 55, 36, 88, 58, 39, 81, 85, 99, 21, 43, 67, 74, 61, 48, 32, 19, 2, 49, 82, 100, 33, 3, 67, 40, 32, 38, 97, 33, 79, 21, 99, 72, 63, 51, 80, 31, 44, 38, 73, 26, 95, 4, 93, 39, 32, 69, 53, 85, 23, 43, 14, 7, 20, 67, 40, 57, 99, 60, 86, 60, 94, 85, 91, 27, 28, 14, 53, 43, 27, 32, 94, 100, 87, 59, 14, 9, 66, 61, 75, 26, 28, 25, 96, 98, 70, 78, 93, 95, 36, 41, 36, 69, 94, 39, 41, 34, 58, 38, 31, 34, 50, 83, 64, 84, 94, 68, 83, 8, 92, 55, 59, 88, 20, 5, 43, 3, 34, 19, 26, 72, 46, 51, 74, 74, 91, 35, 75, 43, 29, 12, 53, 91, 59, 32, 81, 13, 14, 10, 12, 70, 90, 85, 70, 1, 19, 84, 89, 70, 56, 58, 82, 53, 25, 83, 58, 46, 62, 83, 49, 35, 28, 57, 41, 33, 11, 88, 40, 4, 86, 30, 76, 23, 65, 51, 64, 18, 77, 92, 8, 95, 86, 94, 15, 87, 61, 29, 44, 67, 37, 60, 55, 74, 31, 35, 67, 99, 29, 53, 33, 15, 80, 97, 11, 53, 81, 83, 1, 29, 45, 44, 48, 15, 88, 49, 64, 76, 43, 36, 48, 54, 56, 16, 43, 82, 36, 29, 65, 59, 35, 69, 61, 97, 28, 20, 87, 27, 99, 38, 46, 25, 25, 69, 48, 97, 64, 92, 97, 98, 16, 83, 47, 22, 59, 49, 50, 72, 63, 74, 40, 85, 46, 26, 69, 27, 87, 89, 44, 61, 6, 73, 50, 34, 63, 41, 60, 15, 90, 24, 1, 22, 14, 85, 55, 32, 69, 7, 3, 34, 68, 81, 66, 80, 54, 83, 66, 10, 100, 48, 64, 68, 23, 93, 21, 89, 53, 10, 4, 15, 85, 59, 96, 41, 36, 55, 84, 39, 37, 70, 23, 4, 73, 53, 87, 17, 8, 23, 30, 36, 82, 52, 59, 55, 20, 14, 88, 43, 66, 98, 69, 76, 2, 8, 12, 73, 95, 67, 64, 71, 69, 50, 94, 71, 82, 46, 70, 65, 42, 49, 29, 54, 44, 49, 61, 57, 29, 77, 9, 65, 22, 35, 78, 9, 53, 21, 1, 90, 67, 76, 33, 39, 10, 4, 64, 35, 6, 28, 1, 8, 96, 50, 33, 24, 45, 80, 7, 65, 64, 95, 45, 34, 54, 2, 5, 77, 3, 49, 33, 88, 37, 97, 67, 99, 82, 16, 75, 4, 66, 68, 81, 43, 9, 58, 31, 27, 48,68, 29, 28, 39, 74, 83, 37, 76, 54, 72, 74, 29, 6, 45, 88, 57, 78, 23, 71, 67, 29, 89, 25, 59, 18, 17, 52, 71, 95, 93, 7, 69, 25, 7, 75, 11, 33, 95, 97, 55, 65, 19, 30, 87, 17, 18, 3, 82, 37, 62, 49, 37, 85, 92, 61, 59, 56, 45, 18, 66, 67, 30, 31, 90, 4, 51, 100]
opening_cost = [1570, 1690, 990, 2330, 1450, 1620, 1910, 1120, 1220, 2500, 1790, 770, 1820, 2020, 800, 1690, 2290, 1390, 2040, 1050]


total_demand = 0
for i in range(num_clients):
	total_demand = total_demand + demand[i]

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

def production_cost_function(x, l):
	b = random.Random(l).uniform(0.1, 0.4)
	if x == 0:
		y = 0
	else:
		y = (b*math.pow(0.9,math.log(x,2)))*x
	return y
###################################################################################################

############ Define setup cost function ###########################################################
def setup_cost_function(x, j, l):
	b1 = random.Random(j).uniform(100, 450)
	b2 = random.Random(l).uniform(0, 50)
	if x == 0:
		y = 0
	else:
		y = ((b1+b2)*math.pow(0.9,math.log(x,2)))*x
	return y

production_cost = []
for l in range(num_types):
	production_cost.append([])
	for m in range(num_bands):
		production_cost[l].append(production_cost_function(upper_bound[l][m], l)/upper_bound[l][m])

######### Define maximum number of units per Location #############################################
facility_number = []
for j in range(num_locations):
	facility_number.append([])
	for n in range(1,num_copies+1):
		facility_number[j].append(n)

###################################################################################################

############ Define setup cost ####################################################################
setup_cost = []
for j in range(num_locations):
	setup_cost.append([])
	for l in range(num_types):
		setup_cost[j].append([])
		for n in range(1, num_copies+1):
			setup_cost[j][l].append(round(setup_cost_function(n, j, l),2))
###################################################################################################

transport_cost = []
for i in range(num_clients):
	transport_cost.append([])
	for j in range(num_locations):
		cost1 = random.Random(i).uniform(0.05, 0.2)
		cost2 = random.Random(j).uniform(0.05, 0.2)
		transport_cost[i].append(cost1 + cost2)

capacity = []
for j in range(num_locations):
	capacity.append(random.Random(j).randint(5000, 14000))

facility_cap = []
for l in range(num_types):
	facility_cap.append(random.Random(l).randint(1000, 3000))

######### SingleStage Algorithm ###################################################################
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
#print str(ss_opening)+" "+str(ss_service)+" "+str(ss_setup)+" "+str(ss_transport)
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


start_model = time.time()
############## PHASE 1: LOCATION NEIGHBORHOODS ##############################################################################
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

better_solution = False
iteration = 0
while iteration < 20:
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
			better_solution = True
		if better_solution == False:
			iteration = 50
if better_solution == True:
	print(("Local Search (Stage 1) found a better solution: "+str(ss_opening + ss_setup + ss_transport + ss_service)))
	print(("Cost reduced by "+str(round(100*(singlestage_cost - (ss_opening + ss_setup + ss_transport + ss_service))/singlestage_cost,2))+" %"))
	singlestage_cost = ss_opening + ss_setup + ss_transport + ss_service
	print("-------------------------------------------------------------")

############ PHASE 2: FACILITY TYPES ########################################################################################
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
	better_solution = False
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

								better_solution = True
								break
					if better_solution == True:
						break
				if better_solution == True:
					break
		if better_solution == True:
			break
	iteration = iteration + 1
	if better_solution == False:
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
		
########### PHASE 3: CLIENTS ################################################################################
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


fac_vol = []
for l in range(num_types):
	fac_vol.append([])
	for c in range(num_copies):
		fac_vol[l].append(0.0)
location_vol = []
for j in range(num_locations):
	location_vol.append(0.0)
for i in range(num_clients):
	fac_vol[assignments[i][0]][assignments[i][1]] = fac_vol[assignments[i][0]][assignments[i][1]] + demand[i]
	location_vol[assignments[i][2]] = location_vol[assignments[i][2]] + demand[i]
locations = []
for j in range(num_locations):
	locations.append([])
for i in range(num_clients):
	if [assignments[i][0], assignments[i][1]] not in locations[assignments[i][2]]:
		locations[assignments[i][2]].append([assignments[i][0], assignments[i][1]])
level = []
for j in range(num_locations):
	level.append([])
	for l in range(num_types):
		level[j].append(0.0)
for j in range(num_locations):
	for s in range(len(locations[j])): 
		level[j][locations[j][s][0]] = level[j][locations[j][s][0]] + 1

vars = []
values = []

d_var = []
for j in range(num_locations):
	if len(locations[j]) == 0:
		d_var.append(0.0)
		values.append(0.0)
	else:
		d_var.append(1.0)
		values.append(1.0)
	vars.append("d" + str(j))

Y_var = []
for j in range(num_locations):
	Y_var.append([])
	for l in range(num_types):
		Y_var[j].append([])
		for n in range(num_copies):
			if level[j][l] == n+1:
				Y_var[j][l].append(1.0)
				values.append(1.0)
			else:
				Y_var[j][l].append(0.0)
				values.append(0.0)
			vars.append("Y" + str(j) + "," + str(l) + "," +  str(n+1))



Z_var = []
for j in range(num_locations):
	Z_var.append([])
	for c in range(num_copies):
		Z_var[j].append([])
		for l in range(num_types):
			Z_var[j][c].append([])
			for m in range(num_bands):
				if fac_vol[l][c] > lower_bound[l][m] and fac_vol[l][c] <= upper_bound[l][m] and [l,c] in locations[j]:
					Z_var[j][c][l].append(1.0)
					values.append(1.0)
				else:
					Z_var[j][c][l].append(0.0)
					values.append(0.0)
				vars.append("Z" + str(j+1) + "," + str(c+1) + "," + str(l+1) + "," + str(m+1))


X_var = []
for i in range(num_clients):
	X_var.append([])
	for c in range(num_copies):
		X_var[i].append([])
		for l in range(num_types):
			X_var[i][c].append([])
			for m in range(num_bands):
				if assignments[i][0] == l and assignments[i][1] == c:
					if fac_vol[l][c] >= lower_bound[l][m] and fac_vol[l][c] < upper_bound[l][m]:
						X_var[i][c][l].append(1.0)
						values.append(1.0)
					else:
						X_var[i][c][l].append(0.0)
						values.append(0.0)
				else:
					X_var[i][c][l].append(0.0)
					values.append(0.0)
				vars.append("X" + str(i) + "," + str(c) + "," + str(l) + "," + str(m))


t_var = []
for i in range(num_clients):
	t_var.append([])
	for j in range(num_locations):
		if assignments[i][2] == j:
			t_var[i].append(1.0)
			values.append(1.0)
		else:
			t_var[i].append(0.0)
			values.append(0.0)
		vars.append("tij" + str(i) + "," + str(j))


dummy_var = []
for j in range(num_locations):
	dummy_var.append(location_vol[j])
	values.append(location_vol[j])
	vars.append("v"+str(j+1))

######### MIP Formulation ######################################################################################
model = cplex.Cplex()
#model.set_results_stream(None)
model.parameters.workdir.set("/home/avgerinosi/NodeFiles")
model.parameters.workmem.set(4096)
model.parameters.mip.strategy.file.set(2)
model.parameters.mip.tolerances.mipgap.set(0.1) #MIP terminates if the 10% Gap is reached
model.parameters.mip.limits.repairtries.set(50)


start_model = time.time()
############ dj variable #####################################################################
dj = []
for j in range(num_locations):
	dj.append("d" + str(j))

for j in range(num_locations):
	indices = model.variables.add(obj = [opening_cost[j]], 
		      lb = [0], 
		      ub = [1], 
		      types = ["B"],
		      names = [dj[j]])
###################################################################################################

############ Yjln variable ###################################################################
Yjln = []
for j in range(num_locations):
	Yjln.append([])
	for l in range(num_types):
		Yjln[j].append([])
		for n in range(1, num_copies+1):
			Yjln[j][l].append("Y" + str(j) + "," + str(l) + "," +  str(n))

for j in range(num_locations):
	for l in range(num_types):
		for n in range(num_copies):
			indices = model.variables.add(obj = [setup_cost[j][l][n]], 
			      	lb = [0], 
			      	ub = [1],
			      	types = ["B"],
			      	names = [Yjln[j][l][n]])

############ Zjpm variable ###################################################################
Zjcm = []
for j in range(num_locations):
	Zjcm.append([])
	for c in range(num_copies):
		Zjcm[j].append([])
		for l in range(num_types):
			Zjcm[j][c].append([])
			for m in range(num_bands):
				Zjcm[j][c][l].append("Z" + str(j+1) + "," + str(c+1) + "," + str(l+1) + "," + str(m+1))

for j in range(num_locations):
	for c in range(num_copies):
		for l in range(num_types):
			for m in range(num_bands):
				indices = model.variables.add(obj = [0.0], 
		  	 	lb = [0], 
		  		ub = [1], 
		  		types = ["B"],
		  		names = [Zjcm[j][c][l][m]])

############ Xipm variable ###################################################################
Xicm = []
for i in range(num_clients):
	Xicm.append([])
	for c in range(num_copies):
		Xicm[i].append([])
		for l in range(num_types):
			Xicm[i][c].append([])
			for m in range(num_bands):
					Xicm[i][c][l].append("X" + str(i) + "," + str(c) + "," + str(l) + "," + str(m))

for i in range(num_clients):
	for c in range(num_copies):
		for l in range(num_types):
			for m in range(num_bands):
				indices = model.variables.add(obj = [production_cost[l][m]*demand[i]], 
			  	lb = [0], 
			  	ub = [1], 
			  	types = ["B"],
			  	names = [Xicm[i][c][l][m]])
###################################################################################################

############ tij variable ####################################################################
tij = []
for i in range(num_clients):
	tij.append([])
	for j in range(num_locations):
		tij[i].append("tij" + str(i) + "," + str(j))

for i in range(num_clients):
	for j in range(num_locations):
		indices = model.variables.add(obj = [transport_cost[i][j]*demand[i]],
							lb = [0],
							ub = [1],
							types = ["B"],
							names = [tij[i][j]])
###################################################################################################

###################################################################################################
dummy = []
for j in range(num_locations):
	dummy.append("v"+str(j+1))
for j in range(num_locations):
	indices = model.variables.add(obj = [0.0],
						lb = [0.0],
						ub = [cplex.infinity],
						names = [dummy[j]])
#################################################################################################################################
indices = model.MIP_starts.add([vars, values], model.MIP_starts.effort_level.check_feasibility) #The upper bound solution is used.
############ 2. Set constraints #################################################################################################
linear_expressions = []
all_senses = []
all_rhs = []
############ Every client has to be assigned. ################################################
for i in range(num_clients):        
    constraint_1 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for c, l, m in itertools.product(list(range(num_copies)), list(range(num_types)), list(range(num_bands)))],
      val = [1.0] * num_copies * num_types * num_bands)
    linear_expressions.append(constraint_1)
    all_senses.append("E")
    all_rhs.append(1.0)

###################################################################################################

############ Set the proper band based on upper bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for i in range(num_clients)] + [Zjcm[j][c][l][m] for j in range(num_locations)],
			   val = [demand[i] for i in range(num_clients)] + [-upper_bound[l][m]] * num_locations)
			linear_expressions.append(constraint_2)
			all_senses.append("L")
			all_rhs.append(0.0)
###################################################################################################

############ et the proper band based on lower bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for i in range(num_clients)] + [Zjcm[j][c][l][m] for j in range(num_locations)],
			   val = [demand[i] for i in range(num_clients)] + [-lower_bound[l][m]] * num_locations)
			linear_expressions.append(constraint_2)
			all_senses.append("G")
			all_rhs.append(0.0)
###################################################################################################

############ Every unit is located to a single location ######################################
for j in range(num_locations):
	for l in range(num_types):
		constraint_5 = cplex.SparsePair(ind = [Yjln[j][l][n] for n in range(num_copies)],
										val = [1.0] * (num_copies))
		linear_expressions.append(constraint_5)
		all_senses.append("L")
		all_rhs.append(1.0)	

###################################################################################################

############ Define the number of n in j and l ###############################################
for j in range(num_locations):
	for l in range(num_types):
		constraint_5 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for c, m in itertools.product(list(range(num_copies)), list(range(num_bands)))] + [Yjln[j][l][n] for n in range(num_copies)],
										val = [1.0] * num_bands * num_copies + [-facility_number[j][n] for n in range(num_copies)])
		linear_expressions.append(constraint_5)
		all_senses.append("L")
		all_rhs.append(0.0)


############ Every unit is assigned to a single band #########################################
for c in range(num_copies):
	for l in range(num_types):
		for j in range(num_locations):
			constraint_7 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for m in range(num_bands)],
											val = [1.0] * num_bands)
			linear_expressions.append(constraint_7)
			all_senses.append("L")
			all_rhs.append(1.0)

###################################################################################################


############ Set the tij variable. ###########################################################
for j in range(num_locations):
	for i in range(num_clients):
		for c in range(num_copies):
			for l in range(num_types):
				constraint_9 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for m in range(num_bands)] + [Xicm[i][c][l][m] for m in range(num_bands)] + [tij[i][j]],
												val = [1.0] * num_bands + [1.0] * num_bands + [-1.0])
				linear_expressions.append(constraint_9)
				all_senses.append("L")
				all_rhs.append(1.0)

###################################################################################################

############ Each facility can be assigned to one and only band ##############################
for c in range(num_copies):
	for l in range(num_types):
		constraint_11 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for j, m in itertools.product(list(range(num_locations)), list(range(num_bands)))],
											val = [1.0] * num_locations * num_bands)
		linear_expressions.append(constraint_11)
		all_senses.append("L")
		all_rhs.append(1.0)

###################################################################################################

test_list = []
for i in range(num_clients):
	for m in range(num_bands):
		test_list.append(demand[i])

############ The capacity constraints have to be respected ##################################
for l in range(num_types):
	for c in range(num_copies):
		constraint_12 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for i, m in itertools.product(list(range(num_clients)), list(range(num_bands)))],
										val = test_list)
		linear_expressions.append(constraint_12)
		all_senses.append("L")
		all_rhs.append(facility_cap[l])


for j in range(num_locations):
	constraint_20 = cplex.SparsePair(ind = [dummy[j]] + [tij[i][j] for i in range(num_clients)],
									val = [1.0] + [-demand[i] for i in range(num_clients)])
	linear_expressions.append(constraint_20)
	all_senses.append("E")
	all_rhs.append(0.0)

for j in range(num_locations):
	constraint_21 = cplex.SparsePair(ind = [dummy[j]] + [dj[j]],
									val = [1.0] + [-capacity[j]])
	linear_expressions.append(constraint_21)
	all_senses.append("L")
	all_rhs.append(0.0)

constraint_22 = cplex.SparsePair(ind = [dummy[j] for j in range(num_locations)],
								val = [1.0] * num_locations)
linear_expressions.append(constraint_22)
all_senses.append("E")
all_rhs.append(total_demand)

model.linear_constraints.add(lin_expr = linear_expressions,
							senses = all_senses,
							rhs = all_rhs)


######### Solve MIP ############################################################################################
model.objective.set_sense(model.objective.sense.minimize)
model.solve()

cost = 0
fac_vol = []
for l in range(num_types):
	fac_vol.append([])
	for c in range(num_copies):
		fac_vol[l].append(0)
for i in range(num_clients):
	for c in range(num_copies):
		for l in range(num_types):
			for m in range(num_bands):
				if model.solution.get_values(Xicm[i][c][l][m]) > 0.9:
					fac_vol[l][c] = fac_vol[l][c] + demand[i]
for i in range(num_clients):
	for j in range(num_locations):
		if model.solution.get_values(tij[i][j]) > 0.9:
			cost = cost + transport_cost[i][j]*demand[i]
for l in range(num_types):
	for c in range(num_copies):
		cost = cost + production_cost_function(fac_vol[l][c], l)
for j in range(num_locations):
	for l in range(num_types):
		for n in range(num_copies):
			if model.solution.get_values(Yjln[j][l][n]) > 0.9:
				cost = cost + setup_cost_function(n+1, j, l)
for j in range(num_locations):
	if model.solution.get_values(dj[j]) > 0.9:
		cost = cost + opening_cost[j]

end_model = time.time()
optimal_time = end_model - start_model
print("ILP solution calculated (10-gap): "+str(round(cost,2))+" - in "+str(round(optimal_time,2))+" seconds")
print("-------------------------------------------------------------------------")

model.parameters.mip.tolerances.mipgap.set(0.05) #MIP terminates if the 5% Gap is reached
model.solve()

cost = 0
fac_vol = []
for l in range(num_types):
	fac_vol.append([])
	for c in range(num_copies):
		fac_vol[l].append(0)
for i in range(num_clients):
	for c in range(num_copies):
		for l in range(num_types):
			for m in range(num_bands):
				if model.solution.get_values(Xicm[i][c][l][m]) > 0.9:
					fac_vol[l][c] = fac_vol[l][c] + demand[i]
for i in range(num_clients):
	for j in range(num_locations):
		if model.solution.get_values(tij[i][j]) > 0.9:
			cost = cost + transport_cost[i][j]*demand[i]
for l in range(num_types):
	for c in range(num_copies):
		cost = cost + production_cost_function(fac_vol[l][c], l)
for j in range(num_locations):
	for l in range(num_types):
		for n in range(num_copies):
			if model.solution.get_values(Yjln[j][l][n]) > 0.9:
				cost = cost + setup_cost_function(n+1, j, l)
for j in range(num_locations):
	if model.solution.get_values(dj[j]) > 0.9:
		cost = cost + opening_cost[j]

end_model = time.time()
optimal_time = end_model - start_model
print("ILP solution calculated (5-gap): "+str(round(cost,2))+" - in "+str(round(optimal_time,2))+" seconds")
print("-------------------------------------------------------------------------")

model.parameters.mip.tolerances.mipgap.set(0.02) #MIP terminates if the 2% Gap is reached
model.solve()

cost = 0
fac_vol = []
for l in range(num_types):
	fac_vol.append([])
	for c in range(num_copies):
		fac_vol[l].append(0)
for i in range(num_clients):
	for c in range(num_copies):
		for l in range(num_types):
			for m in range(num_bands):
				if model.solution.get_values(Xicm[i][c][l][m]) > 0.9:
					fac_vol[l][c] = fac_vol[l][c] + demand[i]
for i in range(num_clients):
	for j in range(num_locations):
		if model.solution.get_values(tij[i][j]) > 0.9:
			cost = cost + transport_cost[i][j]*demand[i]
for l in range(num_types):
	for c in range(num_copies):
		cost = cost + production_cost_function(fac_vol[l][c], l)
for j in range(num_locations):
	for l in range(num_types):
		for n in range(num_copies):
			if model.solution.get_values(Yjln[j][l][n]) > 0.9:
				cost = cost + setup_cost_function(n+1, j, l)
for j in range(num_locations):
	if model.solution.get_values(dj[j]) > 0.9:
		cost = cost + opening_cost[j]

end_model = time.time()
optimal_time = end_model - start_model
print("ILP solution calculated (2-gap): "+str(round(cost,2))+" - in "+str(round(optimal_time,2))+" seconds")
print("-------------------------------------------------------------------------")

model.parameters.mip.tolerances.mipgap.set(0.00) #MIP terminates if the optimal solution is reached
model.solve()

cost = 0
fac_vol = []
for l in range(num_types):
	fac_vol.append([])
	for c in range(num_copies):
		fac_vol[l].append(0)
for i in range(num_clients):
	for c in range(num_copies):
		for l in range(num_types):
			for m in range(num_bands):
				if model.solution.get_values(Xicm[i][c][l][m]) > 0.9:
					fac_vol[l][c] = fac_vol[l][c] + demand[i]
for i in range(num_clients):
	for j in range(num_locations):
		if model.solution.get_values(tij[i][j]) > 0.9:
			cost = cost + transport_cost[i][j]*demand[i]
for l in range(num_types):
	for c in range(num_copies):
		cost = cost + production_cost_function(fac_vol[l][c], l)
for j in range(num_locations):
	for l in range(num_types):
		for n in range(num_copies):
			if model.solution.get_values(Yjln[j][l][n]) > 0.9:
				cost = cost + setup_cost_function(n+1, j, l)
for j in range(num_locations):
	if model.solution.get_values(dj[j]) > 0.9:
		cost = cost + opening_cost[j]

end_model = time.time()
optimal_time = end_model - start_model
print("ILP solution calculated (Opt): "+str(round(cost,2))+" - in "+str(round(optimal_time,2))+" seconds")
print("-------------------------------------------------------------------------")






