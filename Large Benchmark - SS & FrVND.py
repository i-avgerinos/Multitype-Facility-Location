
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


num_clients = 1000
num_locations = 15
num_types = 15
num_copies = 15
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

demand = [30, 52, 41, 2, 1, 88, 49, 44, 69, 73, 37, 21, 37, 26, 95, 79, 29, 23, 93, 28, 34, 95, 68, 97, 96, 83, 40, 23, 74, 32, 23, 56, 80, 70, 64, 23, 36, 11, 86, 44, 38, 39, 68, 21, 56, 35, 13, 43, 2, 81, 99, 39, 77, 62, 34, 17, 51, 84, 11, 91, 78, 93, 52, 32, 100, 92, 89, 35, 44, 48, 36, 33, 85, 34, 9, 22, 27, 44, 50, 73, 58, 92, 38, 61, 98, 76, 80, 78, 67, 78, 50, 91, 81, 21, 8, 7, 37, 58, 90, 95, 91, 81, 54, 38, 76, 20, 59, 56, 77, 22, 88, 78, 26, 60, 9, 21, 99, 46, 90, 44, 90, 25, 70, 88, 72, 36, 62, 49, 24, 50, 9, 84, 20, 40, 49, 25, 46, 36, 44, 57, 57, 67, 21, 89, 50, 98, 32, 51, 96, 79, 75, 26, 27, 32, 83, 4, 53, 72, 9, 10, 38, 89, 10, 5, 58, 99, 84, 64, 63, 54, 28, 94, 79, 55, 42, 36, 95, 77, 30, 63, 71, 26, 90, 81, 61, 46, 68, 48, 72, 74, 43, 71, 67, 14, 63, 12, 72, 1, 40, 22, 14, 33, 77, 80, 9, 8, 58, 51, 35, 90, 68, 53, 72, 17, 36, 14, 79, 96, 9, 72, 35, 9, 54, 55, 50, 4, 37, 92, 27, 22, 49, 100, 58, 53, 40, 31, 51, 58, 14, 11, 33, 17, 84, 63, 24, 88, 2, 33, 55, 100, 84, 53, 74, 86, 84, 34, 16, 77, 47, 88, 10, 44, 89, 93, 64, 44, 65, 89, 59, 43, 45, 97, 85, 72, 97, 14, 71, 15, 18, 36, 83, 63, 82, 99, 68, 36, 76, 3, 98, 1, 6, 11, 32, 72, 88, 66, 3, 34, 73, 90, 90, 18, 44, 33, 48, 72, 12, 24, 5, 71, 76, 63, 92, 84, 85, 69, 81, 98, 57, 52, 81, 13, 11, 42, 26, 76, 83, 71, 32, 41, 1, 51, 3, 48, 43, 38, 26, 58, 1, 34, 46, 87, 45, 89, 84, 93, 88, 18, 26, 5, 37, 2, 67, 15, 67, 98, 20, 23, 64, 81, 90, 43, 70, 62, 57, 92, 80, 77, 51, 79, 50, 43, 95, 12, 15, 82, 65, 16, 59, 9, 61, 12, 76, 49, 70, 59, 12, 97, 48, 26, 76, 92, 45, 15, 90, 30, 20, 7, 95, 95, 48, 97, 23, 88, 15, 56, 10, 32, 40, 47, 37, 86, 54, 9, 39, 25, 14, 87, 51, 48, 11, 31, 5, 90, 88, 71, 21, 37, 91, 93, 70, 79, 14, 42, 43, 69, 56, 48, 77, 4, 33, 79, 9, 39, 38, 91, 49, 96, 1, 50, 41, 82, 87, 22, 74, 35, 38, 23, 57, 52, 38, 29, 52, 16, 24, 6, 61, 65, 2, 50, 85, 75, 82, 26, 8, 6, 21, 38, 88, 95, 44, 84, 91, 41, 33, 20, 37, 35, 12, 18, 72, 34, 43, 32, 21, 67, 52, 72, 18, 56, 36, 92, 65, 12, 94, 97, 7, 58, 70, 30, 66, 11, 45, 44, 68, 10, 60, 55, 81, 76, 86, 82, 25, 39, 41, 25, 70, 100, 84, 33, 42, 39, 71, 71, 68, 83, 37, 95, 51, 75, 66, 89, 70, 76, 73, 72, 86, 2, 37, 21, 48, 66, 22, 36, 82, 37, 95, 98, 29, 53, 20, 27, 76, 78, 100, 70, 45, 73, 98, 3, 70, 72, 60, 7, 60, 42, 56, 34, 12, 48, 52, 43, 65, 64, 56, 80, 30, 93, 67, 64, 24, 54, 39, 19, 87, 26, 45, 43, 66, 66, 4, 49, 13, 66, 71, 96, 89, 77, 50, 31, 54, 37, 57, 14, 77, 88, 81, 34, 94, 29, 18, 88, 77, 39, 98, 84, 48, 98, 58, 47, 64, 8, 53, 85, 23, 15, 29, 71, 7, 57, 11, 42, 10, 87, 71, 50, 87, 32, 8, 77, 15, 42, 79, 5, 85, 32, 74, 65, 76, 3, 20, 73, 59, 51, 66, 51, 75, 88, 98, 59, 42, 71, 88, 65, 83, 44, 56, 97, 84, 100, 98, 76, 97, 78, 53, 4, 63, 40, 25, 54, 11, 66, 71, 46, 1, 97, 33, 25, 60, 43, 91, 45, 5, 35, 98, 61, 75, 55, 10, 48, 94, 81, 44, 67, 18, 41, 100, 81, 31, 84, 16, 14, 53, 71, 18, 20, 80, 11, 54, 99, 16, 20, 96, 20, 4, 88, 7, 46, 75, 80, 74, 8, 63, 83, 55, 9, 1, 56, 94, 99, 31, 27, 25, 5, 97, 34, 76, 100, 77, 64, 54, 58, 89, 90, 54, 11, 54, 73, 10, 97, 65, 17, 31, 64, 89, 61, 48, 26, 46, 25, 49, 26, 33, 10, 36, 83, 41, 18, 46, 40, 52, 45, 8, 3, 52, 28, 80, 17, 57, 3, 34, 96, 39, 52, 49, 37, 42, 97, 42, 100, 1, 61, 80, 73, 76, 45, 46, 61, 88, 20, 3, 11, 41, 44, 15, 34, 10, 44, 94, 11, 72, 62, 46, 51, 14, 30, 54, 58, 35, 100, 83, 55, 43, 62, 29, 43, 61, 80, 36, 64, 73, 16, 47, 30, 2, 5, 47, 8, 87, 15, 28, 19, 44, 38, 46, 69, 32, 22, 5, 70, 9, 96, 95, 5, 87, 98, 78, 50, 81, 4, 49, 12, 83, 76, 5, 5, 21, 34, 82, 53, 90, 35, 71, 75, 82, 3, 33, 8, 32, 65, 44, 59, 57, 4, 100, 59, 24, 15, 97, 78, 36, 83, 82, 77, 47, 48, 53, 75, 51, 37, 56, 90, 28, 99, 11, 42, 76, 25, 22, 7, 83, 91, 77, 13, 64, 88, 68, 52, 31, 83, 74, 70, 47, 80, 8, 22, 100, 92, 8, 63, 15, 34, 65, 62, 71, 47, 39, 69, 99, 64, 82, 89, 45, 6, 12, 31, 69, 100, 56, 61, 100, 99, 44, 20, 24, 15, 51, 28, 53, 28, 45, 60, 48, 22, 58, 85, 88, 72, 8, 48, 33, 96, 97, 53, 8, 9, 66, 84, 76, 4]
opening_cost = [1180, 1160, 2460, 1470, 1910, 2310, 1620, 1860, 1490, 1190, 2350, 1100, 1050, 2480, 950]

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
	facility_cap.append(random.Random(l).randint(100, 500))

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


############ 3. Solve the model #################################################################################################
model = cplex.Cplex()
model.set_results_stream(sys.stdout)
#model.set_results_stream(None)
model.parameters.workdir.set("/home/avgerinosi/NodeFiles")
model.parameters.workmem.set(1024)
model.parameters.mip.strategy.file.set(2)
model.parameters.mip.limits.repairtries.set(50)


############ 1. Define variables ################################################################################################
start_model = time.time()
############ 1.1. dj variable #####################################################################
dj = []
for j in range(num_locations):
	dj.append("d" + str(j))

for j in range(num_locations):
	indices = model.variables.add(obj = [opening_cost[j]], 
		      lb = [0], 
		      ub = [1], 
		      names = [dj[j]])
###################################################################################################

############ 1.2. Yjln variable ###################################################################
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
			      	names = [Yjln[j][l][n]])

############ 1.5. Zjpm variable ###################################################################
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
		  		names = [Zjcm[j][c][l][m]])

############ 1.3. Xipm variable ###################################################################
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
			  	names = [Xicm[i][c][l][m]])
###################################################################################################

############ 1.4. tij variable ####################################################################
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
############ 2. Set constraints #################################################################################################
linear_expressions = []
all_senses = []
all_rhs = []
############ 2.1. Every client has to be assigned. ################################################
for i in range(num_clients):        
    constraint_1 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for c, l, m in itertools.product(list(range(num_copies)), list(range(num_types)), list(range(num_bands)))],
      val = [1.0] * num_copies * num_types * num_bands)
    linear_expressions.append(constraint_1)
    all_senses.append("E")
    all_rhs.append(1.0)

###################################################################################################

############ 2.2. Set the proper band based on upper bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for i in range(num_clients)] + [Zjcm[j][c][l][m] for j in range(num_locations)],
			   val = [demand[i] for i in range(num_clients)] + [-upper_bound[l][m]] * num_locations)
			linear_expressions.append(constraint_2)
			all_senses.append("L")
			all_rhs.append(0.0)
###################################################################################################

############ 2.3. Set the proper band based on lower bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for i in range(num_clients)] + [Zjcm[j][c][l][m] for j in range(num_locations)],
			   val = [demand[i] for i in range(num_clients)] + [-lower_bound[l][m]] * num_locations)
			linear_expressions.append(constraint_2)
			all_senses.append("G")
			all_rhs.append(0.0)
###################################################################################################

############ 2.4. Every unit is located to a single location ######################################
for j in range(num_locations):
	for l in range(num_types):
		constraint_5 = cplex.SparsePair(ind = [Yjln[j][l][n] for n in range(num_copies)],
										val = [1.0] * (num_copies))
		linear_expressions.append(constraint_5)
		all_senses.append("L")
		all_rhs.append(1.0)	

###################################################################################################

############ 2.5. Define the number of n in j and l ###############################################
for j in range(num_locations):
	for l in range(num_types):
		constraint_5 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for c, m in itertools.product(list(range(num_copies)), list(range(num_bands)))] + [Yjln[j][l][n] for n in range(num_copies)],
										val = [1.0] * num_bands * num_copies + [-facility_number[j][n] for n in range(num_copies)])
		linear_expressions.append(constraint_5)
		all_senses.append("L")
		all_rhs.append(0.0)

###################################################################################################

############ 2.6. dj = 1 if the location j is chosen ##############################################
#for j in range(num_locations):
#	for c in range(num_copies):
#		for l in range(num_types):
#			constraint_6 = cplex.SparsePair(ind = [dj[j]] + [Zjcm[j][c][l][m] for m in range(num_bands)],
#											val = [1.0] + [-1.0] * num_bands)
#			model.linear_constraints.add(lin_expr = [constraint_6],
#										senses = ["G"],
#										rhs = [0.0])
###################################################################################################

############ 2.7. Every unit is assigned to a single band #########################################
for c in range(num_copies):
	for l in range(num_types):
		for j in range(num_locations):
			constraint_7 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for m in range(num_bands)],
											val = [1.0] * num_bands)
			linear_expressions.append(constraint_7)
			all_senses.append("L")
			all_rhs.append(1.0)

###################################################################################################


############ 2.8. Set the tij variable. ###########################################################
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

############ 2.9. Each facility can be assigned to one and only band ##############################
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

############ 2.10. The capacity constraints have to be respected ##################################
for l in range(num_types):
	for c in range(num_copies):
		constraint_12 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for i, m in itertools.product(list(range(num_clients)), list(range(num_bands)))],
										val = test_list)
		linear_expressions.append(constraint_12)
		all_senses.append("L")
		all_rhs.append(facility_cap[l])


#for j in range(num_locations):
#		constraint_8 = cplex.SparsePair(ind = [tij[i][j] for i in range(num_clients)],
#										val = [demand[i] for i in range(num_clients)])
#		model.linear_constraints.add(lin_expr = [constraint_8],
#									senses = ["L"],
#									rhs = [capacity[j]])
###################################################################################################
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



############ 3. Solve the model #################################################################################################
model.objective.set_sense(model.objective.sense.minimize)
model.solve()


end_model = time.time()
optimal_time = end_model - start_model
print("LP solution calculated: "+str(round(model.solution.get_objective_value(),2))+" - in "+str(round(optimal_time,2))+" seconds")
print("-------------------------------------------------------------------------")

alpha_lower_bound = 0
alpha_upper_bound = 0.9
iteration = 0
running = True
cost1 = 0
cost2 = 0
while(running == True):
	if int(iteration*0.5) == iteration*0.5:
		alpha = alpha_lower_bound
	if int(iteration*0.5) != iteration*0.5:
		alpha = alpha_upper_bound
	metric_costs = []
	dict_costs = []
	for i in range(num_clients):
		for l in range(num_types):
			for c in range(num_copies):
				metric_costs.append(round(production_cost_function(demand[i],l),2))
				dict_costs.append([i,l,c])
	metric_costs.sort()
	dictionary = [x for _, x in sorted(zip(metric_costs, dict_costs))]

	ci_a = []
	for i in range(num_clients):
		sum_x = 0
		for k in range(len(metric_costs)):
			for m in range(num_bands):
				if dictionary[k][0] == i:
					sum_x = sum_x + model.solution.get_values(Xicm[i][dictionary[k][2]][dictionary[k][1]][m])
					if sum_x > alpha:
						ci_a.append(metric_costs[k])
						break
			if sum_x > alpha:
				break

	a_i = []
	for i in range(num_clients):
		sum_x = 0
		for l in range(num_types):
			for c in range(num_copies):
				if round(production_cost_function(demand[i],l),2) <= ci_a[i]:
					for m in range(num_bands):
						sum_x = sum_x + model.solution.get_values(Xicm[i][c][l][m])
		a_i.append(sum_x)

	new_Xicm = []
	for i in range(num_clients):
		covered = False
		new_Xicm.append([])
		for c in range(num_copies):
			new_Xicm[i].append([])
			for l in range(num_types):
				new_Xicm[i][c].append([])
				for m in range(num_bands):
					if round(production_cost_function(demand[i],l),2) < ci_a[i] and a_i[i] > 0:
						new_Xicm[i][c][l].append(model.solution.get_values(Xicm[i][c][l][m])/a_i[i])
						covered = True
					else:
						new_Xicm[i][c][l].append(0.0)
		if covered == False:
			maximum = 0
			for c in range(num_copies):
				for l in range(num_types):
					for m in range(num_bands):
						if model.solution.get_values(Xicm[i][c][l][m]) > maximum:
							maximum = model.solution.get_values(Xicm[i][c][l][m])
			for c in range(num_copies):
				for l in range(num_types):
					for m in range(num_bands):
						if model.solution.get_values(Xicm[i][c][l][m]) == maximum:
							new_Xicm[i][c][l][m] = model.solution.get_values(Xicm[i][c][l][m])
							break
					if model.solution.get_values(Xicm[i][c][l][m]) == maximum:
						break
				if model.solution.get_values(Xicm[i][c][l][m]) == maximum:
					break

	int_Xicm = []
	for i in range(num_clients):
		int_Xicm.append([])
		for c in range(num_copies):
			int_Xicm[i].append([])
			for l in range(num_types):
				int_Xicm[i][c].append(0.0)
	assigned_clients = []
	for i in range(num_clients):
		assigned_clients.append(False)
	assigned_demand = []
	for l in range(num_types):
		assigned_demand.append([])
		for c in range(num_copies):
			assigned_demand[l].append(0)
			for i in range(num_clients):
				if assigned_clients[i] == False:
					if any(new_Xicm[i][c][l][m] > 0.0 for m in range(num_bands)) and assigned_demand[l][c] + demand[i] <= facility_cap[l]:
						int_Xicm[i][c][l] = 1.0
						assigned_clients[i] = True
						assigned_demand[l][c] = assigned_demand[l][c] + demand[i]
	for i in range(num_clients):
		if assigned_clients[i] == False:
			for l in range(num_types):
				for c in range(num_copies):
					if assigned_demand[l][c] > 0 and assigned_demand[l][c] + demand[i] <= facility_cap[l]:
						int_Xicm[i][c][l] = 1.0
						assigned_clients[i] = True
						assigned_demand[l][c] = assigned_demand[l][c] + demand[i]
		if assigned_clients[i] == False:
			for l in range(num_types):
				for c in range(num_copies):
					if assigned_demand[l][c] + demand[i] <= facility_cap[l]:
						int_Xicm[i][c][l] = 1.0
						assigned_demand[l][c] = assigned_demand[l][c] + demand[i]
						assigned_clients[i] = True

	for i in range(num_clients):
		sum_i = 0
		for l in range(num_types):
			for c in range(num_copies):
				sum_i = sum_i + int_Xicm[i][c][l]
		if sum_i > 1.0:
			counter = 0
			for l in range(num_types):
				for c in range(num_copies):
					if int_Xicm[i][c][l] == 1.0 and counter > 0:
						int_Xicm[i][c][l] = 0.0
						counter = counter + 1
						assigned_demand[l][c] = assigned_demand[l][c] - demand[i]
					if int_Xicm[i][c][l] == 1.0 and counter == 0:
						counter = counter + 1
					

	metric_costs = []
	dict_costs = []
	for l in range(num_types):
		for c in range(num_copies):
			for j in range(num_locations):
				t_cost = 0
				for i in range(num_clients):
					if int_Xicm[i][c][l] == 1.0:
						t_cost = t_cost + round(demand[i]*transport_cost[i][j])
				metric_costs.append(round(setup_cost_function(1,j,l),2)+t_cost)
				dict_costs.append([l,c,j])
	metric_costs.sort()
	dictionary = [x for _, x in sorted(zip(metric_costs, dict_costs))]

	ci_a = []
	for l in range(num_types):
		ci_a.append([])
		for c in range(num_copies):
			sum_x = 0
			if all(int_Xicm[i][c][l] == 0.0 for i in range(num_clients)):
				ci_a[l].append(0.0)
			for k in range(len(metric_costs)):
				for m in range(num_bands):
					if dictionary[k][0] == l and dictionary[k][1] == c:
						sum_x = sum_x + model.solution.get_values(Zjcm[dictionary[k][2]][c][l][m])
						if sum_x > alpha:
							ci_a[l].append(metric_costs[k])
							break
				if sum_x > alpha:
					break
			if sum_x <= alpha:
				ci_a[l].append(0.0)

	a_i = []
	for l in range(num_types):
		a_i.append([])
		for c in range(num_copies):
			sum_x = 0
			for j in range(num_locations):
				for i in range(num_clients):
					if int_Xicm[i][c][l] == 1.0:
						t_cost = t_cost + round(demand[i]*transport_cost[i][j])
				if round(setup_cost_function(1,j,l),2) + t_cost <= ci_a[l][c]:
					for m in range(num_bands):
						sum_x = sum_x + model.solution.get_values(Zjcm[j][c][l][m])
				a_i[l].append(sum_x)

	new_Zjcm = []
	for l in range(num_types):
		new_Zjcm.append([])
		for c in range(num_copies):
			covered = False
			new_Zjcm[l].append([])
			for j in range(num_locations):
				new_Zjcm[l][c].append([])
				t_cost = 0
				for i in range(num_clients):
					if int_Xicm[i][c][l] == 1.0:
						t_cost = t_cost + round(demand[i]*transport_cost[i][j],2)
				for m in range(num_bands):
					if round(setup_cost_function(1,j,l),2) + t_cost < ci_a[l][c] and a_i[l][c] > 0:
						new_Zjcm[l][c][j].append(model.solution.get_values(Zjcm[j][c][l][m])/a_i[l][c])
						covered = True
					else:
						new_Zjcm[l][c][j].append(0.0)
			if covered == False:
				maximum = 0
				for j in range(num_locations):
					for m in range(num_bands):
						if model.solution.get_values(Zjcm[j][c][l][m]) > maximum:
							maximum = model.solution.get_values(Zjcm[j][c][l][m])
				for j in range(num_locations):
					for m in range(num_bands):
						if model.solution.get_values(Zjcm[j][c][l][m]) == maximum:
							new_Zjcm[l][c][j][m] = model.solution.get_values(Zjcm[j][c][l][m])
							break
						if model.solution.get_values(Zjcm[j][c][l][m]) == maximum:
							break
					if model.solution.get_values(Zjcm[j][c][l][m]) == maximum:
						break

	int_Zjcm = []
	for j in range(num_locations):
		int_Zjcm.append([])
		for l in range(num_types):
			int_Zjcm[j].append([])
			for c in range(num_copies):
				int_Zjcm[j][l].append(0.0)

	assigned_facilities = []
	for l in range(num_types):
		assigned_facilities.append([])
		for c in range(num_copies):
			if assigned_demand[l][c] == 0.0:
				assigned_facilities[l].append(True)
			else:
				assigned_facilities[l].append(False)

	location_demand = []
	for j in range(num_locations):
		location_demand.append(0)
	for j in range(num_locations):
		for l in range(num_types):
			for c in range(num_copies):
				if all(int_Zjcm[x][l][c] == 0.0 for x in range(num_locations)):
					if any(new_Zjcm[l][c][j][m] > 0.0 for m in range(num_bands)) and location_demand[j] + assigned_demand[l][c] <= capacity[j] and assigned_demand[l][c] > 0:
						int_Zjcm[j][l][c] = 1.0
						location_demand[j] = location_demand[j] + assigned_demand[l][c]
						assigned_facilities[l][c] = True

	for l in range(num_types):
		for c in range(num_copies):
			if all(int_Zjcm[x][l][c] == 0.0 for x in range(num_locations)) and assigned_demand[l][c] > 0:
				for j in range(num_locations):
					if location_demand[j] > 0 and location_demand[j] + assigned_demand[l][c] <= capacity[j]:
						assigned_facilities[l][c] = True
						int_Zjcm[j][l][c] = 1.0
						location_demand[j] = location_demand[j] + assigned_demand[l][c]
	for l in range(num_types):
		for c in range(num_copies):
			if assigned_facilities[l][c] == False:
				for j in range(num_locations):
					if location_demand[j] + assigned_demand[l][c] <= capacity[j] and location_demand[j] > 0:
						int_Zjcm[j][l][c] = 1.0
						assigned_facilities[l][c] = True
						location_demand[j] = location_demand[j] + assigned_demand[l][c]
			if assigned_facilities[l][c] == False:
				f_cost = 10000000
				for j in range(num_locations):
					if round(setup_cost_function(1,j,l),2) + opening_cost[j] <= f_cost and location_demand[j] + assigned_demand[l][c] <= capacity[j]:
						f_cost = round(setup_cost_function(1,j,l),2) + opening_cost[j]
				for j in range(num_locations):
					if round(setup_cost_function(1,j,l),2) + opening_cost[j] == f_cost and location_demand[j] + assigned_demand[l][c] <= capacity[j]:
						int_Zjcm[j][l][c] = 1.0
						assigned_facilities[l][c] = True
						location_demand[j] = location_demand[j] + assigned_demand[l][c]


	ss_service = 0
	for l in range(num_types):
		for c in range(num_copies):
			ss_service = ss_service + round(production_cost_function(assigned_demand[l][c], l),2)
	ss_opening = 0
	for j in range(num_locations):
		if location_demand[j] > 0:
			ss_opening = ss_opening + opening_cost[j]
	ss_setup = 0
	level = []
	for j in range(num_locations):
		level.append([])
		for l in range(num_types):
			level[j].append(0)
	for j in range(num_locations):
		for l in range(num_types):
			for c in range(num_copies):
				if int_Zjcm[j][l][c] == 1.0:
					level[j][l] = level[j][l] + 1
	for j in range(num_locations):
		for l in range(num_types):
			ss_setup = ss_setup + round(setup_cost_function(level[j][l], j, l),2)
	ss_transport = 0
	for i in range(num_clients):
		for j in range(num_locations):
			for l in range(num_types):
				for c in range(num_copies):
					if int_Zjcm[j][l][c] == 1.0 and int_Xicm[i][c][l] == 1.0:
						ss_transport = ss_transport + round(demand[i]*transport_cost[i][j])
	cost = ss_transport + ss_service + ss_setup + ss_opening
	if alpha == alpha_lower_bound:
		cost1 = cost
	if alpha == alpha_upper_bound:
		cost2 = cost
	iteration = iteration + 1
	if iteration > 1:
		if cost2 > cost1:
			alpha_upper_bound = (alpha_upper_bound + alpha_lower_bound)/2
		if cost2 < cost1:
			alpha_lower_bound = (alpha_upper_bound + alpha_lower_bound)/2
		if cost2 == cost1:
			running = False
	if iteration == 10:
		running = False
end_model = time.time()
singlestage_cost = ss_transport + ss_service + ss_setup + ss_opening
print("------------------------------------------------------------------")
print(("Filtering Solution (before LS) for a = "+str(round(alpha,2))+": "+str(round(singlestage_cost,2)))+" in "+str(round(end_model - start_model,2))+" seconds")
print("------------------------------------------------------------------") 
############ 3. Solve the model #################################################################################################

end_model = time.time()

start_model = time.time()

assignments = []
for i in range(num_clients):
	assignments.append([])
	for n in range(3):
		assignments[i].append(None)
for i in range(num_clients):
	for l in range(num_types):
		for c in range(num_copies):
			for j in range(num_locations):
				if int_Zjcm[j][l][c] == 1.0 and int_Xicm[i][c][l] == 1.0:
					assignments[i][0] = l
					assignments[i][1] = c
					assignments[i][2] = j
fac_vol = []
for l in range(num_types):
	fac_vol.append([])
	for c in range(num_copies):
		fac_vol[l].append(assigned_demand[l][c])
location_vol = []
for j in range(num_locations):
	location_vol.append(location_demand[j])
facilities = []
for l in range(num_types):
	facilities.append([])
	for c in range(num_copies):
		facilities[l].append(False)
for l in range(num_types):
	for c in range(num_copies):
		for j in range(num_locations):
			if int_Zjcm[j][l][c] == 1.0:
				facilities[l][c] = j
locations = []
for j in range(num_locations):
	locations.append([])
	for l in range(num_types):
		for c in range(num_copies):
			if int_Zjcm[j][l][c] == 1.0:
				locations[j].append([l,c])


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
print("")

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
print("")







