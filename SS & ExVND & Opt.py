
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


num_clients = 150
num_locations = 10
num_types = 15
num_copies = 15
num_bands = 10

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

demand = []
for i in range(num_clients):
	demand.append(random.randint(1,100))
total_demand = 0
for i in range(num_clients):
	total_demand = total_demand + demand[i]

lower_bound = []
lb = 1
for l in range(num_types):
	lower_bound.append([])
	for m in range(num_bands):
		lower_bound[l].append(lb+m*300)

upper_bound = []
ub = 300
for l in range(num_types):
	upper_bound.append([])
	for m in range(num_bands):
		upper_bound[l].append(ub+m*300)

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

opening_cost = []
for j in range(num_locations):
	opening_cost.append(10*random.randint(75, 250))



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
								#print str(contribution[i])+" "+str(cost)
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
								#print str(contribution[i])+" "+str(cost)
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
								#print str(contribution[i])+" "+str(cost)
								if contribution[i] >= cost:
									budget = budget + cost
									budget_demand = budget_demand + demand[clients[i]]
						if budget >= int(0.1*opening_cost[j]):
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
new_solution = singlestage_cost
used_types = []
for l in range(num_types):
	if any(fac_vol[l][c] > 0 for c in range(num_copies)):
		used_types.append(l)
for s in range(len(neighborhoods)):
	#################################################################################################################
	model = cplex.Cplex()
	model.set_results_stream(None)
	model.parameters.workdir.set("/home/avgerinosi/NodeFiles")
	model.parameters.workmem.set(1024)
	model.parameters.mip.strategy.file.set(2)
	#model.parameters.mip.tolerances.mipgap.set(0.1)
	############ 1. Define variables ################################################################################################
	start_model = time.time()
	############ 1.1. dj variable #####################################################################
	###################################################################################################

	############ 1.2. Yjln variable ###################################################################
	Yjln = []
	for j in range(len(neighborhoods[s])):
		Yjln.append([])
		for l in range(len(used_types)):
			Yjln[j].append([])
			for n in range(1, num_copies+1):
				Yjln[j][l].append("Y" + str(j) + "," + str(l) + "," +  str(n))

	for j in range(len(neighborhoods[s])):
		for l in range(len(used_types)):
			for n in range(num_copies):
				indices = model.variables.add(obj = [setup_cost[neighborhoods[s][j]][used_types[l]][n]], 
				      	lb = [0], 
				      	ub = [1],
				      	types = ["B"],
				      	names = [Yjln[j][l][n]])

	X_var = []
	for i in range(num_clients):
		X_var.append([])
		for l in range(num_types):
			X_var[i].append([])
			for c in range(num_copies):
				X_var[i][l].append([])
				for m in range(num_bands):
					if assignments[i][0] == l and assignments[i][1] == c:
						if fac_vol[l][c] >= lower_bound[l][m] and fac_vol[l][c] < upper_bound[l][m]:
							X_var[i][l][c].append(1.0)
						else:
							X_var[i][l][c].append(0.0)
					else:
						X_var[i][l][c].append(0.0)
	facility_band = []
	for l in range(num_types):
		facility_band.append([])
		for c in range(num_copies):
			facility_band[l].append([])
			for m in range(num_bands):
				if fac_vol[l][c] >= lower_bound[l][m] and fac_vol[l][c] < upper_bound[l][m]:
					facility_band[l][c].append(1.0)
				else:
					facility_band[l][c].append(0.0)
	############ 1.5. Zjpm variable ###################################################################
	Zjcm = []
	for j in range(len(neighborhoods[s])):
		Zjcm.append([])
		for l in range(len(used_types)):
			Zjcm[j].append([])
			for c in range(num_copies):
				Zjcm[j][l].append([])
				for m in range(num_bands):
					Zjcm[j][l][c].append("Z" + str(j+1) + "," + str(c+1) + "," + str(l+1) + "," + str(m+1))

	for j in range(len(neighborhoods[s])):
		for l in range(len(used_types)):
			for c in range(num_copies):
				for m in range(num_bands):
						indices = model.variables.add(obj = [0.0], 
				  	 	lb = [0], 
				  		ub = [facility_band[used_types[l]][c][m]], 
				  		types = ["B"],
				  		names = [Zjcm[j][l][c][m]])

	############ 1.3. Xipm variable ###################################################################
	
	###################################################################################################

	############ 1.4. tij variable ####################################################################
	tij = []
	for i in range(num_clients):
		tij.append([])
		for j in range(len(neighborhoods[s])):
			tij[i].append("tij" + str(i) + "," + str(j))

	for i in range(num_clients):
		for j in range(len(neighborhoods[s])):
			indices = model.variables.add(obj = [transport_cost[i][neighborhoods[s][j]]*demand[i]],
								lb = [0],
								ub = [1],
								types = ["B"],
								names = [tij[i][j]])
	###################################################################################################

	###################################################################################################
	dummy = []
	for j in range(len(neighborhoods[s])):
		dummy.append("v"+str(j+1))
	for j in range(len(neighborhoods[s])):
		indices = model.variables.add(obj = [0.0],
							lb = [0.0],
							ub = [cplex.infinity],
							names = [dummy[j]])
	#################################################################################################################################
	#indices = model.MIP_starts.add([vars, values], model.MIP_starts.effort_level.check_feasibility)
	############ 2. Set constraints #################################################################################################

	############ 2.1. Every client has to be assigned. ################################################

	###################################################################################################

	############ 2.2. Set the proper band based on upper bound ########################################
	for l in range(len(used_types)):
		for c in range(num_copies):
			for m in range(num_bands):
				rhs_value = 0
				for i in range(num_clients):
					rhs_value = rhs_value + X_var[i][used_types[l]][c][m]*demand[i]       
				constraint_2 = cplex.SparsePair(ind = [Zjcm[j][l][c][m] for j in range(len(neighborhoods[s]))],
				   val = [upper_bound[used_types[l]][m]] * len(neighborhoods[s]))
				model.linear_constraints.add(lin_expr = [constraint_2],
				  senses = ["G"], 
				  rhs = [rhs_value]);
	###################################################################################################

	############ 2.3. Set the proper band based on lower bound ########################################
	for l in range(len(used_types)):
		for c in range(num_copies):
			for m in range(num_bands): 
				rhs_value = 0
				for i in range(num_clients):
					rhs_value = rhs_value + X_var[i][used_types[l]][c][m]*demand[i]      
				constraint_2 = cplex.SparsePair(ind = [Zjcm[j][l][c][m] for j in range(len(neighborhoods[s]))],
				   val = [lower_bound[used_types[l]][m]] * len(neighborhoods[s]))
				model.linear_constraints.add(lin_expr = [constraint_2],
				  senses = ["L"], 
				  rhs = [rhs_value]);
	###################################################################################################

	############ 2.4. Every unit is located to a single location ######################################
	for j in range(len(neighborhoods[s])):
		for l in range(len(used_types)):
			constraint_5 = cplex.SparsePair(ind = [Yjln[j][l][n] for n in range(num_copies)],
											val = [1.0] * (num_copies))
			model.linear_constraints.add(lin_expr = [constraint_5],
										senses = ["L"],
										rhs = [1.0])
	###################################################################################################

	############ 2.5. Define the number of n in j and l ###############################################
	for j in range(len(neighborhoods[s])):
		for l in range(len(used_types)):
			constraint_5 = cplex.SparsePair(ind = [Zjcm[j][l][c][m] for c, m in itertools.product(list(range(num_copies)), list(range(num_bands)))] + [Yjln[j][l][n] for n in range(num_copies)],
											val = [1.0] * num_bands * num_copies + [-facility_number[neighborhoods[s][j]][n] for n in range(num_copies)])
			model.linear_constraints.add(lin_expr = [constraint_5],
										senses = ["L"],
										rhs = [0.0])
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
		for l in range(len(used_types)):
			for j in range(len(neighborhoods[s])):
				constraint_7 = cplex.SparsePair(ind = [Zjcm[j][l][c][m] for m in range(num_bands)],
												val = [1.0] * num_bands)
				model.linear_constraints.add(lin_expr = [constraint_7],
											senses = ["L"],
											rhs = [1.0])
	###################################################################################################


	############ 2.8. Set the tij variable. ###########################################################
	for j in range(len(neighborhoods[s])):
		for i in range(num_clients):
			for c in range(num_copies):
				for l in range(len(used_types)):
					rhs_value = 0
					for m in range(num_bands):
						rhs_value = rhs_value + X_var[i][used_types[l]][c][m]
					constraint_9 = cplex.SparsePair(ind = [Zjcm[j][l][c][m] for m in range(num_bands)] + [tij[i][j]],
													val = [1.0] * num_bands + [-1.0])
					model.linear_constraints.add(lin_expr = [constraint_9],
												senses = ["L"],
												rhs = [1.0 - rhs_value])
	###################################################################################################

	############ 2.9. Each facility can be assigned to one and only band ##############################
	for c in range(num_copies):
		for l in range(len(used_types)):
			constraint_11 = cplex.SparsePair(ind = [Zjcm[j][l][c][m] for j, m in itertools.product(list(range(len(neighborhoods[s]))), list(range(num_bands)))],
												val = [1.0] * len(neighborhoods[s]) * num_bands)
			model.linear_constraints.add(lin_expr = [constraint_11],
											senses = ["L"],
											rhs = [1.0])
	###################################################################################################

	test_list = []
	for i in range(num_clients):
		for m in range(num_bands):
			test_list.append(demand[i])

	############ 2.10. The capacity constraints have to be respected ##################################

	#for j in range(num_locations):
	#		constraint_8 = cplex.SparsePair(ind = [tij[i][j] for i in range(num_clients)],
	#										val = [demand[i] for i in range(num_clients)])
	#		model.linear_constraints.add(lin_expr = [constraint_8],
	#									senses = ["L"],
	#									rhs = [capacity[j]])
	###################################################################################################
	for j in range(len(neighborhoods[s])):
		constraint_20 = cplex.SparsePair(ind = [dummy[j]] + [tij[i][j] for i in range(num_clients)],
										val = [1.0] + [-demand[i] for i in range(num_clients)])
		model.linear_constraints.add(lin_expr = [constraint_20],
									senses = ["E"],
									rhs = [0.0])

	for j in range(len(neighborhoods[s])):
		constraint_21 = cplex.SparsePair(ind = [dummy[j]],
										val = [1.0])
		model.linear_constraints.add(lin_expr = [constraint_21],
									senses = ["L"],
									rhs = [capacity[neighborhoods[s][j]]])

	constraint_22 = cplex.SparsePair(ind = [dummy[j] for j in range(len(neighborhoods[s]))],
									val = [1.0] * len(neighborhoods[s]))
	model.linear_constraints.add(lin_expr = [constraint_22],
								senses = ["E"],
								rhs = [total_demand])

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
					if X_var[i][l][c][m] > 0.9:
						fac_vol[l][c] = fac_vol[l][c] + demand[i]
	for i in range(num_clients):
		for j in range(len(neighborhoods[s])):
			if model.solution.get_values(tij[i][j]) > 0.9:
				cost = cost + transport_cost[i][neighborhoods[s][j]]*demand[i]
	for l in range(len(used_types)):
		for c in range(num_copies):
			cost = cost + production_cost_function(fac_vol[used_types[l]][c], used_types[l])
	for j in range(len(neighborhoods[s])):
		for l in range(len(used_types)):
			for n in range(num_copies):
				if model.solution.get_values(Yjln[j][l][n]) > 0.9:
					cost = cost + setup_cost_function(n, neighborhoods[s][j], used_types[l])
	for j in range(len(neighborhoods[s])):
			cost = cost + opening_cost[neighborhoods[s][j]]

	if round(cost,2) < round(new_solution,2):
		new_solution = cost
		better_solution = True
		for i in range(num_clients):
			for j in range(len(neighborhoods[s])):
				if model.solution.get_values(tij[i][j]) > 0.9:
					assignments[i][2] = neighborhoods[s][j]
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
if better_solution == True:
	print(("Local Search (Stage 1) found a better solution: "+str(round(new_solution,2))))
	print(("Cost reduced by "+str(round(100*(singlestage_cost - (new_solution))/singlestage_cost,2))+" %"))
	singlestage_cost = new_solution
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

better_solution = False

used_locations = []
for j in range(num_locations):
	if location_vol[j] > 0:
		used_locations.append(j)

model = cplex.Cplex()
model.set_results_stream(None)
model.parameters.workdir.set("/home/avgerinosi/NodeFiles")
model.parameters.workmem.set(1024)
model.parameters.mip.strategy.file.set(2)
#model.parameters.mip.tolerances.mipgap.set(0.1)
############ 1. Define variables ################################################################################################
start_model = time.time()
############ 1.1. dj variable #####################################################################

###################################################################################################

############ 1.2. Yjln variable ###################################################################
Yjln = []
for j in range(len(used_locations)):
	Yjln.append([])
	for l in range(num_types):
		Yjln[j].append([])
		for n in range(1, num_copies+1):
			Yjln[j][l].append("Y" + str(j) + "," + str(l) + "," +  str(n))

for j in range(len(used_locations)):
	for l in range(num_types):
		for n in range(num_copies):
			indices = model.variables.add(obj = [setup_cost[used_locations[j]][l][n]], 
			      	lb = [0], 
			      	ub = [1],
			      	types = ["B"],
			      	names = [Yjln[j][l][n]])

############ 1.5. Zjpm variable ###################################################################
Zjcm = []
for j in range(len(used_locations)):
	Zjcm.append([])
	for c in range(num_copies):
		Zjcm[j].append([])
		for l in range(num_types):
			Zjcm[j][c].append([])
			for m in range(num_bands):
				Zjcm[j][c][l].append("Z" + str(j+1) + "," + str(c+1) + "," + str(l+1) + "," + str(m+1))

for j in range(len(used_locations)):
	for c in range(num_copies):
		for l in range(num_types):
			for m in range(num_bands):
				indices = model.variables.add(obj = [0.0], 
		  	 	lb = [0], 
		  		ub = [1], 
		  		types = ["B"],
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
			  	types = ["B"],
			  	names = [Xicm[i][c][l][m]])
###################################################################################################

############ 1.4. tij variable ####################################################################
t_var = []
for i in range(num_clients):
	t_var.append([])
	for j in range(len(used_locations)):
		if assignments[i][2] == used_locations[j]:
			t_var[i].append(1.0)
		else:
			t_var[i].append(0.0)

###################################################################################################

###################################################################################################

#################################################################################################################################
############ 2. Set constraints #################################################################################################

############ 2.1. Every client has to be assigned. ################################################
for i in range(num_clients):        
    constraint_1 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for c, l, m in itertools.product(list(range(num_copies)), list(range(num_types)), list(range(num_bands)))],
      val = [1.0] * num_copies * num_types * num_bands)
    model.linear_constraints.add(lin_expr = [constraint_1],
  senses = ["E"], 
  rhs = [1.0]);
###################################################################################################

############ 2.2. Set the proper band based on upper bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for i in range(num_clients)] + [Zjcm[j][c][l][m] for j in range(len(used_locations))],
			   val = [demand[i] for i in range(num_clients)] + [-upper_bound[l][m]] * len(used_locations))
			model.linear_constraints.add(lin_expr = [constraint_2],
			  senses = ["L"], 
			  rhs = [0.0]);
###################################################################################################

############ 2.3. Set the proper band based on lower bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for i in range(num_clients)] + [Zjcm[j][c][l][m] for j in range(len(used_locations))],
			   val = [demand[i] for i in range(num_clients)] + [-lower_bound[l][m]] * len(used_locations))
			model.linear_constraints.add(lin_expr = [constraint_2],
			  senses = ["G"], 
			  rhs = [0.0]);
###################################################################################################

############ 2.4. Every unit is located to a single location ######################################
for j in range(len(used_locations)):
	for l in range(num_types):
		constraint_5 = cplex.SparsePair(ind = [Yjln[j][l][n] for n in range(num_copies)],
										val = [1.0] * (num_copies))
		model.linear_constraints.add(lin_expr = [constraint_5],
									senses = ["L"],
									rhs = [1.0])
###################################################################################################

############ 2.5. Define the number of n in j and l ###############################################
for j in range(len(used_locations)):
	for l in range(num_types):
		constraint_5 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for c, m in itertools.product(list(range(num_copies)), list(range(num_bands)))] + [Yjln[j][l][n] for n in range(num_copies)],
										val = [1.0] * num_bands * num_copies + [-facility_number[used_locations[j]][n] for n in range(num_copies)])
		model.linear_constraints.add(lin_expr = [constraint_5],
									senses = ["L"],
									rhs = [0.0])
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
		for j in range(len(used_locations)):
			constraint_7 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for m in range(num_bands)],
											val = [1.0] * num_bands)
			model.linear_constraints.add(lin_expr = [constraint_7],
										senses = ["L"],
										rhs = [1.0])
###################################################################################################


############ 2.8. Set the tij variable. ###########################################################
for j in range(len(used_locations)):
	for i in range(num_clients):
		for c in range(num_copies):
			for l in range(num_types):
				constraint_9 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for m in range(num_bands)] + [Xicm[i][c][l][m] for m in range(num_bands)],
												val = [1.0] * num_bands + [1.0] * num_bands)
				model.linear_constraints.add(lin_expr = [constraint_9],
											senses = ["L"],
											rhs = [1.0 + t_var[i][j]])
###################################################################################################

############ 2.9. Each facility can be assigned to one and only band ##############################
for c in range(num_copies):
	for l in range(num_types):
		constraint_11 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for j, m in itertools.product(list(range(len(used_locations))), list(range(num_bands)))],
											val = [1.0] * len(used_locations) * num_bands)
		model.linear_constraints.add(lin_expr = [constraint_11],
										senses = ["L"],
										rhs = [1.0])
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
		model.linear_constraints.add(lin_expr = [constraint_12],
									senses = ["L"],
									rhs = [facility_cap[l]])

#for j in range(num_locations):
#		constraint_8 = cplex.SparsePair(ind = [tij[i][j] for i in range(num_clients)],
#										val = [demand[i] for i in range(num_clients)])
#		model.linear_constraints.add(lin_expr = [constraint_8],
#									senses = ["L"],
#									rhs = [capacity[j]])
###################################################################################################

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
	for j in range(len(used_locations)):
		if t_var[i][j] > 0.9:
			cost = cost + transport_cost[i][used_locations[j]]*demand[i]
for l in range(num_types):
	for c in range(num_copies):
		cost = cost + production_cost_function(fac_vol[l][c], l)
for j in range(len(used_locations)):
	for l in range(num_types):
		for n in range(num_copies):
			if model.solution.get_values(Yjln[j][l][n]) > 0.9:
				cost = cost + setup_cost_function(n, used_locations[j], l)
for j in range(num_locations):
	if location_vol[j] > 0:
		cost = cost + opening_cost[j]

if round(cost,2) < round(new_solution,2):
	new_solution = cost
	better_solution = True
	for i in range(num_clients):
		for c in range(num_copies):
			for l in range(num_types):
				for m in range(num_bands):
					if model.solution.get_values(Xicm[i][c][l][m]) > 0.9:
						assignments[i][0] = l
						assignments[i][1] = c
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
if better_solution == True:
	print(("Local Search (Stage 2) found a better solution: "+str(round(new_solution,2))))
	print(("Cost reduced by "+str(round(100*(singlestage_cost - (new_solution))/singlestage_cost,2))+" %"))
	singlestage_cost = new_solution
	print("-------------------------------------------------------------")

used_types = []
for l in range(num_types):
	if any(fac_vol[l][c] > 0 for c in range(num_copies)):
		used_types.append(l)
########### PHASE 3: CLIENTS ################################################################################
better_solution = False

###################################################################################################
model = cplex.Cplex()
model.set_results_stream(None)
model.parameters.workdir.set("/home/avgerinosi/NodeFiles")
model.parameters.workmem.set(1024)
model.parameters.mip.strategy.file.set(2)
############ 1.2. Yjln variable ###################################################################
Y_var = []
for j in range(len(used_locations)):
	Y_var.append([])
	for l in range(len(used_types)):
		Y_var[j].append([])
		for n in range(num_copies):
			if level[used_locations[j]][used_types[l]] == n+1:
				Y_var[j][l].append(1.0)
			else:
				Y_var[j][l].append(0.0)

############ 1.5. Zjpm variable ###################################################################
Zjcm = []
for j in range(len(used_locations)):
	Zjcm.append([])
	for l in range(len(used_types)):
		Zjcm[j].append([])
		for c in range(num_copies):
			Zjcm[j][l].append([])
			for m in range(num_bands):
				Zjcm[j][l][c].append("Z" + str(j+1) + "," + str(c+1) + "," + str(l+1) + "," + str(m+1))

for j in range(len(used_locations)):
	for l in range(len(used_types)):
		for c in range(num_copies):
			for m in range(num_bands):
				if fac_vol[used_types[l]][c] > 0:
					indices = model.variables.add(obj = [0.0], 
			  	 	lb = [0], 
			  		ub = [1], 
			  		types = ["B"],
			  		names = [Zjcm[j][l][c][m]])
				if fac_vol[used_types[l]][c] == 0:
			  		indices = model.variables.add(obj = [0.0], 
			  	 	lb = [0], 
			  		ub = [0], 
			  		types = ["B"],
			  		names = [Zjcm[j][l][c][m]])

############ 1.3. Xipm variable ###################################################################
Xicm = []
for i in range(num_clients):
	Xicm.append([])
	for l in range(len(used_types)):
		Xicm[i].append([])
		for c in range(num_copies):
			Xicm[i][l].append([])
			for m in range(num_bands):
					Xicm[i][l][c].append("X" + str(i) + "," + str(c) + "," + str(l) + "," + str(m))

for i in range(num_clients):
	for l in range(len(used_types)):
		for c in range(num_copies):
			for m in range(num_bands):
				if fac_vol[used_types[l]][c] > 0:
					indices = model.variables.add(obj = [production_cost[used_types[l]][m]*demand[i]], 
				  	lb = [0], 
				  	ub = [1], 
				  	types = ["B"],
				  	names = [Xicm[i][l][c][m]])
				if fac_vol[used_types[l]][c] == 0:
					indices = model.variables.add(obj = [production_cost[used_types[l]][m]*demand[i]], 
				  	lb = [0], 
				  	ub = [0], 
				  	types = ["B"],
				  	names = [Xicm[i][l][c][m]])
###################################################################################################

############ 1.4. tij variable ####################################################################
tij = []
for i in range(num_clients):
	tij.append([])
	for j in range(len(used_locations)):
		tij[i].append("tij" + str(i) + "," + str(j))

for i in range(num_clients):
	for j in range(len(used_locations)):
		indices = model.variables.add(obj = [transport_cost[i][used_locations[j]]*demand[i]],
							lb = [0],
							ub = [1],
							types = ["B"],
							names = [tij[i][j]])
###################################################################################################
dummy = []
for j in range(len(used_locations)):
	dummy.append("v"+str(j+1))
for j in range(len(used_locations)):
	indices = model.variables.add(obj = [0.0],
						lb = [0.0],
						ub = [cplex.infinity],
						names = [dummy[j]])
###################################################################################################

############ 2. Set constraints #################################################################################################

############ 2.1. Every client has to be assigned. ################################################
for i in range(num_clients):        
    constraint_1 = cplex.SparsePair(ind = [Xicm[i][l][c][m] for c, l, m in itertools.product(list(range(num_copies)), list(range(len(used_types))), list(range(num_bands)))],
      val = [1.0] * num_copies * len(used_types) * num_bands)
    model.linear_constraints.add(lin_expr = [constraint_1],
  senses = ["E"], 
  rhs = [1.0]);
###################################################################################################

############ 2.2. Set the proper band based on upper bound ########################################
for c in range(num_copies):
	for l in range(len(used_types)):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xicm[i][l][c][m] for i in range(num_clients)] + [Zjcm[j][l][c][m] for j in range(len(used_locations))],
			   val = [demand[i] for i in range(num_clients)] + [-upper_bound[used_types[l]][m]] * len(used_locations))
			model.linear_constraints.add(lin_expr = [constraint_2],
			  senses = ["L"], 
			  rhs = [0.0]);
###################################################################################################

############ 2.3. Set the proper band based on lower bound ########################################
for c in range(num_copies):
	for l in range(len(used_types)):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xicm[i][l][c][m] for i in range(num_clients)] + [Zjcm[j][l][c][m] for j in range(len(used_locations))],
			   val = [demand[i] for i in range(num_clients)] + [-lower_bound[used_types[l]][m]] * len(used_locations))
			model.linear_constraints.add(lin_expr = [constraint_2],
			  senses = ["G"], 
			  rhs = [0.0]);
###################################################################################################

############ 2.4. Every unit is located to a single location ######################################
for j in range(len(used_locations)):
	for l in range(len(used_types)):
		rhs_value = 0
		for n in range(num_copies):
			rhs_value = rhs_value + facility_number[used_locations[j]][n]*Y_var[j][l][n]
		constraint_5 = cplex.SparsePair(ind = [Zjcm[j][l][c][m] for c, m in itertools.product(list(range(num_copies)), list(range(num_bands)))],
										val = [1.0] * num_bands * num_copies)
		model.linear_constraints.add(lin_expr = [constraint_5],
									senses = ["L"],
									rhs = [rhs_value])
###################################################################################################

############ 2.5. Define the number of n in j and l ###############################################

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
	for l in range(len(used_types)):
		for j in range(len(used_locations)):
			constraint_7 = cplex.SparsePair(ind = [Zjcm[j][l][c][m] for m in range(num_bands)],
											val = [1.0] * num_bands)
			model.linear_constraints.add(lin_expr = [constraint_7],
										senses = ["L"],
										rhs = [1.0])
###################################################################################################


############ 2.8. Set the tij variable. ###########################################################
for j in range(len(used_locations)):
	for i in range(num_clients):
		for c in range(num_copies):
			for l in range(len(used_types)):
				constraint_9 = cplex.SparsePair(ind = [Zjcm[j][l][c][m] for m in range(num_bands)] + [Xicm[i][l][c][m] for m in range(num_bands)] + [tij[i][j]],
												val = [1.0] * num_bands + [1.0] * num_bands + [-1.0])
				model.linear_constraints.add(lin_expr = [constraint_9],
											senses = ["L"],
											rhs = [1.0])
###################################################################################################

############ 2.9. Each facility can be assigned to one and only band ##############################
for c in range(num_copies):
	for l in range(len(used_types)):
		constraint_11 = cplex.SparsePair(ind = [Zjcm[j][l][c][m] for j, m in itertools.product(list(range(len(used_locations))), list(range(num_bands)))],
											val = [1.0] * len(used_locations) * num_bands)
		model.linear_constraints.add(lin_expr = [constraint_11],
										senses = ["L"],
										rhs = [1.0])
###################################################################################################

test_list = []
for i in range(num_clients):
	for m in range(num_bands):
		test_list.append(demand[i])

############ 2.10. The capacity constraints have to be respected ##################################
for l in range(len(used_types)):
	for c in range(num_copies):
		constraint_12 = cplex.SparsePair(ind = [Xicm[i][l][c][m] for i, m in itertools.product(list(range(num_clients)), list(range(num_bands)))],
										val = test_list)
		model.linear_constraints.add(lin_expr = [constraint_12],
									senses = ["L"],
									rhs = [facility_cap[used_types[l]]])

#for j in range(num_locations):
#		constraint_8 = cplex.SparsePair(ind = [tij[i][j] for i in range(num_clients)],
#										val = [demand[i] for i in range(num_clients)])
#		model.linear_constraints.add(lin_expr = [constraint_8],
#									senses = ["L"],
#									rhs = [capacity[j]])
###################################################################################################
for j in range(len(used_locations)):
	constraint_20 = cplex.SparsePair(ind = [dummy[j]] + [tij[i][j] for i in range(num_clients)],
									val = [1.0] + [-demand[i] for i in range(num_clients)])
	model.linear_constraints.add(lin_expr = [constraint_20],
								senses = ["E"],
								rhs = [0.0])

for j in range(len(used_locations)):
	constraint_21 = cplex.SparsePair(ind = [dummy[j]],
									val = [1.0])
	model.linear_constraints.add(lin_expr = [constraint_21],
								senses = ["L"],
								rhs = [capacity[used_locations[j]]])

constraint_22 = cplex.SparsePair(ind = [dummy[j] for j in range(len(used_locations))],
								val = [1.0] * len(used_locations))
model.linear_constraints.add(lin_expr = [constraint_22],
							senses = ["E"],
							rhs = [total_demand])
			

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
		for l in range(len(used_types)):
			for m in range(num_bands):
				if model.solution.get_values(Xicm[i][l][c][m]) > 0.9:
					fac_vol[used_types[l]][c] = fac_vol[used_types[l]][c] + demand[i]
for i in range(num_clients):
	for j in range(len(used_locations)):
		if model.solution.get_values(tij[i][j]) > 0.9:
			cost = cost + transport_cost[i][used_locations[j]]*demand[i]
for l in range(num_types):
	for c in range(num_copies):
		cost = cost + production_cost_function(fac_vol[l][c], l)
for j in range(len(used_locations)):
	for l in range(len(used_types)):
		for n in range(num_copies):
			if Y_var[j][l][n] > 0.9:
				cost = cost + setup_cost_function(n, used_locations[j], used_types[l])
for j in range(len(used_locations)):
	if model.solution.get_values(dummy[j]) > 0.9:
		cost = cost + opening_cost[used_locations[j]]

if round(cost,2) < round(new_solution,2):
	new_solution = cost
	better_solution = True
	for i in range(num_clients):
		for c in range(num_copies):
			for l in range(len(used_types)):
				for m in range(num_bands):
					if model.solution.get_values(Xicm[i][l][c][m]) > 0.9:
						assignments[i][0] = used_types[l]
						assignments[i][1] = c
		for j in range(len(used_locations)):
			if model.solution.get_values(tij[i][j]) > 0.9:
				assignments[i][2] = used_locations[j]
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

if better_solution == True:
	print(("Local Search (Stage 3) found a better solution: "+str(round(new_solution,2))))
	print(("Cost reduced by "+str(round(100*(singlestage_cost - (new_solution))/singlestage_cost,2))+" %"))
	singlestage_cost = new_solution
	print("-------------------------------------------------------------")

end_model = time.time()
print((str(round(end_model - start_model,2))))
print("")
############ 3. Solve the model #################################################################################################
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

#################################################################################################################
model = cplex.Cplex()

model.set_results_stream(sys.stdout)
model.parameters.mip.tolerances.mipgap.set(0.1)
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
		      types = ["B"],
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
			      	types = ["B"],
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
		  		types = ["B"],
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
			  	types = ["B"],
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
indices = model.MIP_starts.add([vars, values], model.MIP_starts.effort_level.check_feasibility)
############ 2. Set constraints #################################################################################################

############ 2.1. Every client has to be assigned. ################################################
for i in range(num_clients):        
    constraint_1 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for c, l, m in itertools.product(list(range(num_copies)), list(range(num_types)), list(range(num_bands)))],
      val = [1.0] * num_copies * num_types * num_bands)
    model.linear_constraints.add(lin_expr = [constraint_1],
  senses = ["E"], 
  rhs = [1.0]);
###################################################################################################

############ 2.2. Set the proper band based on upper bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for i in range(num_clients)] + [Zjcm[j][c][l][m] for j in range(num_locations)],
			   val = [demand[i] for i in range(num_clients)] + [-upper_bound[l][m]] * num_locations)
			model.linear_constraints.add(lin_expr = [constraint_2],
			  senses = ["L"], 
			  rhs = [0.0]);
###################################################################################################

############ 2.3. Set the proper band based on lower bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xicm[i][c][l][m] for i in range(num_clients)] + [Zjcm[j][c][l][m] for j in range(num_locations)],
			   val = [demand[i] for i in range(num_clients)] + [-lower_bound[l][m]] * num_locations)
			model.linear_constraints.add(lin_expr = [constraint_2],
			  senses = ["G"], 
			  rhs = [0.0]);
###################################################################################################

############ 2.4. Every unit is located to a single location ######################################
for j in range(num_locations):
	for l in range(num_types):
		constraint_5 = cplex.SparsePair(ind = [Yjln[j][l][n] for n in range(num_copies)],
										val = [1.0] * (num_copies))
		model.linear_constraints.add(lin_expr = [constraint_5],
									senses = ["L"],
									rhs = [1.0])
###################################################################################################

############ 2.5. Define the number of n in j and l ###############################################
for j in range(num_locations):
	for l in range(num_types):
		constraint_5 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for c, m in itertools.product(list(range(num_copies)), list(range(num_bands)))] + [Yjln[j][l][n] for n in range(num_copies)],
										val = [1.0] * num_bands * num_copies + [-facility_number[j][n] for n in range(num_copies)])
		model.linear_constraints.add(lin_expr = [constraint_5],
									senses = ["L"],
									rhs = [0.0])
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
			model.linear_constraints.add(lin_expr = [constraint_7],
										senses = ["L"],
										rhs = [1.0])
###################################################################################################


############ 2.8. Set the tij variable. ###########################################################
for j in range(num_locations):
	for i in range(num_clients):
		for c in range(num_copies):
			for l in range(num_types):
				constraint_9 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for m in range(num_bands)] + [Xicm[i][c][l][m] for m in range(num_bands)] + [tij[i][j]],
												val = [1.0] * num_bands + [1.0] * num_bands + [-1.0])
				model.linear_constraints.add(lin_expr = [constraint_9],
											senses = ["L"],
											rhs = [1.0])
###################################################################################################

############ 2.9. Each facility can be assigned to one and only band ##############################
for c in range(num_copies):
	for l in range(num_types):
		constraint_11 = cplex.SparsePair(ind = [Zjcm[j][c][l][m] for j, m in itertools.product(list(range(num_locations)), list(range(num_bands)))],
											val = [1.0] * num_locations * num_bands)
		model.linear_constraints.add(lin_expr = [constraint_11],
										senses = ["L"],
										rhs = [1.0])
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
		model.linear_constraints.add(lin_expr = [constraint_12],
									senses = ["L"],
									rhs = [facility_cap[l]])

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
	model.linear_constraints.add(lin_expr = [constraint_20],
								senses = ["E"],
								rhs = [0.0])

for j in range(num_locations):
	constraint_21 = cplex.SparsePair(ind = [dummy[j]] + [dj[j]],
									val = [1.0] + [-capacity[j]])
	model.linear_constraints.add(lin_expr = [constraint_21],
								senses = ["L"],
								rhs = [0.0])

constraint_22 = cplex.SparsePair(ind = [dummy[j] for j in range(num_locations)],
								val = [1.0] * num_locations)
model.linear_constraints.add(lin_expr = [constraint_22],
							senses = ["E"],
							rhs = [total_demand])



############ 3. Solve the model #################################################################################################
start_model = time.time()
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
				cost = cost + setup_cost_function(n, j, l)
for j in range(num_locations):
	if model.solution.get_values(dj[j]) > 0.9:
		cost = cost + opening_cost[j]

end_model = time.time()
optimal_time = end_model - start_model
print("ILP solution calculated (10-gap): "+str(round(cost,2))+" - in "+str(round(optimal_time,2))+" seconds")
print("-------------------------------------------------------------------------")
model.parameters.mip.tolerances.mipgap.set(0.05)
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
				cost = cost + setup_cost_function(n, j, l)
for j in range(num_locations):
	if model.solution.get_values(dj[j]) > 0.9:
		cost = cost + opening_cost[j]

end_model = time.time()
optimal_time = end_model - start_model
print("ILP solution calculated (5-gap): "+str(round(cost,2))+" - in "+str(round(optimal_time,2))+" seconds")
print("-------------------------------------------------------------------------")
model.parameters.mip.tolerances.mipgap.set(0.02)
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
				cost = cost + setup_cost_function(n, j, l)
for j in range(num_locations):
	if model.solution.get_values(dj[j]) > 0.9:
		cost = cost + opening_cost[j]

end_model = time.time()
optimal_time = end_model - start_model
print("ILP solution calculated (2-gap): "+str(round(cost,2))+" - in "+str(round(optimal_time,2))+" seconds")
print("-------------------------------------------------------------------------")
model.parameters.mip.tolerances.mipgap.set(0)
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
				cost = cost + setup_cost_function(n, j, l)
for j in range(num_locations):
	if model.solution.get_values(dj[j]) > 0.9:
		cost = cost + opening_cost[j]

end_model = time.time()
optimal_time = end_model - start_model
print("ILP solution calculated (0-gap): "+str(round(cost,2))+" - in "+str(round(optimal_time,2))+" seconds")
print("-------------------------------------------------------------------------")




			

















									

										
									
									







