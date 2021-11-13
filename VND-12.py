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
num_locations = 15
num_types = 20
num_copies = 20
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


######### Filtering & Rounding Algorithm: LP relaxation ########################################################
model = cplex.Cplex()
model.set_results_stream(sys.stdout)
model.set_results_stream(None)
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
start_model = time.time()

######### Filtering & Rounding Algorithm #######################################################################
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


######### Meta-heuristic - GreedyVND ###########################################################################
start_model = time.time()
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

better_solution = 0
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
		


		





				
			



