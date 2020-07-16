from __future__ import division
import cplex
from cplex.exceptions import CplexSolverError
import sys
import random
import itertools
import time
import math
import datetime

################ 1. Sets ###############################################################################

################ 1.1. Number of slots #####################################
num_clients = 91
################ 1.2. Number of printer types #############################
num_types = 33
################ 1.3. Number of copies of same type printers ##############
num_copies = 10
################ 1.4. Number of Clusters ##################################
num_locations = 91
################ 1.5. Number of bands #####################################
num_bands = 12
###########################################################################

#####################################################################################################
print "Instance 1 Dataset"
print "-------------------------------------------------------------------------------"
################ 2. Parameters #########################################################################

################ 2.1. Demands #############################################
slot_list = []
for i in range(num_clients):
	slot_list.append(i)

demand_1 = [9043,18949,36,4150,316,3962,1936,53,696,14555,2854,21709,154,2828,3836,3295,4058,155,50,3999,3495,135,33,657,50,16500,50,50,849,50,11988,215,3694,1588,2854,2379,13632,50,50,50,50,50,37455,19254,11834,11934,31796,3658,25348,8644,3500,1046,141,500,9677,1503,4008,8754,7414,10,50,5045,5934,6504,2231,4784,2202,5393,854,125,2114,3101,11300,763,941,4145,56,6971,9495,127,1589,1108,2771,213,2999,1082,1896,1051,5329,4823,2500,1000] #Black & White copies monthly demand
demand_2 = [0,0,202,0,178,0,0,340,0,0,0,0,0,3398,0,0,0,297,0,0,0,656,0,0,0,0,0,0,0,0,0,0,0,310,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4000,0,0,0,0,0,0,0,0,50,100,0,0,0,1326,0,0,0,2013,0,0,0,0,4227,0,0,376,0,0,589,0,0,0,0,0,0,0,1543,5648,0,0,500] #Colour copies monthly demand

bw_demand = []
for n in range(2):
	bw_demand.append([])
for i in range(num_clients):
	if demand_2[i] == 0:
		bw_demand[0].append(demand_1[i])
		bw_demand[1].append(i)

colour_demand = []
for n in range(2):
	colour_demand.append([])
for i in range(num_clients):
	if demand_2[i] > 0:
		colour_demand[0].append(demand_2[i] + demand_1[i])
		colour_demand[1].append(i)


################ 2.2. Bands boundaries ####################################
lcap = [1200000,300000,100000,100000,1000000,1000000,3600000,3600000,3600000,3600000,6000000,6000000,2000000,2000000,1000000,2000000,2000000,2000000,1000000,1000000,50000,1000000,1000000,400000,600000,50000,500000,500000,300000,300000,6000000,6000000,300000]
for l in range(num_types):
	lcap[l] = int(lcap[l]/48)

cap1 = [1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 20000, 40000, 36000, 46000]
cap2 = [2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 20000, 40000, 37000, 47000]
cap3 = [3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 20000, 40000, 38000, 48000]

upper_bound = []
for n in range(11):
	upper_bound.append(cap1)
	upper_bound.append(cap2)
	upper_bound.append(cap3)

lower_bound = []
for l in range(num_types):
	lower_bound.append([1])
	for m in range(num_bands-1):
		lower_bound[l].append(upper_bound[l][m]+1)

################ 2.3. Printers attributes #################################
buying_cost = [2696.32,676.37,1659.00,2209.82,1392.32,1969.43,3281.42,4598.96,3046.63,3954.53,6353.00,5445.00,5703.00,4591.00,2401.00,2946.00,3628.00,4625.00,3131.00,2536.00,325.74,363.72,503.68,1885.00,930.00,279.82,1242.00,1465.00,542.00,575.00,4819.00,3447.00,465.00] #Buying cost per type
isColor = [1,0,1,1,0,0,1,1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0] #Whether printer prints colour copies (1) or not (0)


facility_number = []
for j in range(num_locations):
	facility_number.append([])
	for n in range(1):
		facility_number[j].append(n+1)
################ 2.4. Printing cost Function ##############################
production_cost = []
for l in range(num_types):
	production_cost.append([])

for l in range(0, num_types, 3):
	production_cost[l].append([0.640, 0.602, 0.514, 0.456, 0.460, 0.560, 0.516, 0.567, 0.535, 0.504, 0.490, 0.478, 0.478, 0.478])
	production_cost[l].append([1.373, 1.372, 1.556, 1.296, 1.299, 1.385, 1.306, 1.524, 1.466, 1.344, 1.320, 1.290, 1,333, 1.345]) 

for l in range(1, num_types, 3):
	production_cost[l].append([0.514, 0.456, 0.460, 0.560, 0.516, 0.519, 0.535, 0.504, 0.487, 0.498, 0.512, 0.499, 0.499, 0.499])
	production_cost[l].append([1.269, 1.439, 1.310, 1.388, 1.327, 1.381, 1.469, 1.416, 1.314, 1.319, 1.325, 1.331, 1.346, 1.322])
for l in range(2, num_types, 3):
	production_cost[l].append([0.390, 0.560, 0.516, 0.519, 0.491, 0.504, 0.487, 0.464, 0.472, 0.515, 0.530, 0.535, 0.535, 0.535])
	production_cost[l].append([1.241, 1.388, 1.327, 1.333, 1.336, 1.416, 1.314, 1.284, 1.466, 1.416, 1.389, 1.402, 1.400, 1.404]) 

################ 2.5. Printers setup cost function ########################
def setup_cost_function(x, j, l): #Printers setup cost function
	y = buying_cost[l]*math.pow(x, 0.8)
	return y

setup_cost = [] #Printers setup cost linearization
for j in range(num_locations):
	setup_cost.append([])
	for l in range(num_types):
		setup_cost[j].append(int(round(setup_cost_function(1, j, l),2)/48))


################ 2.6. Clusters attributes #################################
eligible_printers = [[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,0,22,23,2,3,6,7,12,13,18,19,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,0,22,23,2,3,6,7,12,13,18,19,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,0,22,23,2,3,6,7,12,13,18,19,24],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,26,27,28,29,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,30,31,12,13,14,15,16,17,18,19,26,27,32,28,29,24],
					[0,2,3,6,7,12,13,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,0,22,23,2,3,6,7,12,13,18,19,24],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,30,31,12,13,14,15,16,17,18,19,26,27,32,28,29,24],
					[0,2,3,6,7,12,13,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,0,22,23,2,3,6,7,12,13,18,19,24],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,30,31,12,13,14,15,16,17,18,19,26,27,32,28,29,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,26,27,29,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,1],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,26,27,29,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,0,22,23,2,3,6,7,12,13,18,19,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,2,3,6,7,12,13,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,2,3,6,7,12,13,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,30,31,12,13,14,15,16,17,18,19,26,27,32,28,29,24],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,26,27,29,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,26,27,29,24],
					[0,2,3,6,7,12,13,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,0,22,23,2,3,6,7,12,13,18,19,24],
					[20,21,0,22,23,2,3,6,7,12,13,18,19,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,2,3,6,7,12,13,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,0,22,23,2,3,6,7,12,13,18,19,24],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,30,31,12,13,14,15,16,17,18,19,26,27,32,28,29,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,0,22,23,2,3,6,7,12,13,18,19,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,26,27,29,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,0,22,23,2,3,6,7,12,13,18,19,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,26,27,29,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[20,21,25,0,22,23,1,2,3,4,5,6,7,8,9,10,11,30,31,12,13,14,15,16,17,18,19,26,27,32,28,29,24],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,2,3,6,7,12,13,18,19],
					[0,2,3,6,7,12,13,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
					[0,2,3,6,7,12,13,18,19]]

eligibility_matrix = []
for j in range(num_locations):
	eligibility_matrix.append([])
	for l in range(num_types):
		eligibility_matrix[j].append(0)

for j in range(num_locations):
	for l in range(len(eligible_printers[j])):
		eligibility_matrix[j][eligible_printers[j][l]] = 1

slot_to_cluster = []
for i in range(num_clients):
	slot_to_cluster.append(i)

slots_assignments = []
for i in range(num_clients):
	slots_assignments.append([])
	for j in range(num_locations):
		slots_assignments[i].append(0)

for i in range(num_clients):
	slots_assignments[i][slot_to_cluster[i]] = 1
########################################################################################################

model = cplex.Cplex()
#model.set_results_stream(None)
model.parameters.workdir.set("C:\\Users\\Administrator\\Desktop\\Node files")
model.parameters.workmem.set(128)
model.parameters.mip.strategy.file.set(3)
#model.parameters.timelimit.set(2500)
################ 3. Variables ##########################################################################

################ 3.1. Yjln - n number of l type printers located to cluster j
Yjln = []
for j in range(num_locations):
	Yjln.append([])
	for l in range(num_types):
		Yjln[j].append("Y" + str(j) + "," + str(l))

for j in range(num_locations):
	for l in range(num_types):
		model.variables.add(obj = [setup_cost[j][l]], 
		                	lb = [0], 
		                	ub = [1],
		                	types = ["B"],
		                	names = [Yjln[j][l]])

###################################################################################################

############ 1.3. Xipm variable ###################################################################
Xbw = []
for i in range(len(bw_demand[0])):
	Xbw.append([])
	for c in range(num_copies):
		Xbw[i].append([])
		for l in range(num_types):
			Xbw[i][c].append([])
			for m in range(num_bands):
					Xbw[i][c][l].append("Xbw" + str(i) + "," + str(c) + "," + str(l) + "," + str(m))

for i in range(len(bw_demand[0])):
	for c in range(num_copies):
		for l in range(num_types):
			for m in range(num_bands):
				model.variables.add(obj = [production_cost[l][0][m]*bw_demand[0][i]], 
			                      	lb = [0], 
			                      	ub = [1],
			                      	types = ["B"],
			                      	names = [Xbw[i][c][l][m]])

Xc = []
for i in range(len(colour_demand[0])):
	Xc.append([])
	for c in range(num_copies):
		Xc[i].append([])
		for l in range(num_types):
			Xc[i][c].append([])
			for m in range(num_bands):
					Xc[i][c][l].append("Xc" + str(i) + "," + str(c) + "," + str(l) + "," + str(m))

for i in range(len(colour_demand[0])):
	for c in range(num_copies):
		for l in range(num_types):
			for m in range(num_bands):
				model.variables.add(obj = [production_cost[l][1][m]*colour_demand[0][i]], 
			                      	lb = [0], 
			                      	ub = [1],
			                      	types = ["B"],
			                      	names = [Xc[i][c][l][m]])
###################################################################################################

############ 1.5. Zjpm variable ###################################################################
Zbw = []
for c in range(num_copies):
	Zbw.append([])
	for l in range(num_types):
		Zbw[c].append([])
		for m in range(num_bands):
			Zbw[c][l].append("Zbw"+ str(c) + "," + str(l) + "," + str(m))

for c in range(num_copies):
	for l in range(num_types):
		for m in range(num_bands):
			model.variables.add(obj = [0.0], 
	                      	 	lb = [0], 
	                      		ub = [1],
	                      		types = ["B"],
	                      		names = [Zbw[c][l][m]])
###################################################################################################

#################################################################################################################################

############ 2. Set constraints #################################################################################################

############ 2.1. Every client has to be assigned. ################################################
for i in range(len(bw_demand[0])):        
    constraint_1 = cplex.SparsePair(ind = [Xbw[i][c][l][m] for c, l, m in itertools.product(range(num_copies), range(num_types), range(num_bands))],
                                    val = [1.0] * num_copies * num_types * num_bands)
    model.linear_constraints.add(lin_expr = [constraint_1],                    
                                senses = ["E"], 
                                rhs = [1.0]);
for i in range(len(colour_demand[0])):        
    constraint_1 = cplex.SparsePair(ind = [Xc[i][c][l][m] for c, l, m in itertools.product(range(num_copies), range(num_types), range(num_bands))],
                                    val = [1.0] * num_copies * num_types * num_bands)
    model.linear_constraints.add(lin_expr = [constraint_1],                    
                                senses = ["E"], 
                                rhs = [1.0]);
###################################################################################################

############ 2.2. Set the proper band based on upper bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xbw[i][c][l][m] for i in range(len(bw_demand[0]))] + [Zbw[c][l][m]],
			                                 val = [bw_demand[0][i] for i in range(len(bw_demand[0]))] + [-upper_bound[l][m]])
			model.linear_constraints.add(lin_expr = [constraint_2],                    
			                                senses = ["L"], 
			                                rhs = [0.0]);
###################################################################################################

############ 2.3. Set the proper band based on lower bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		for m in range(num_bands):       
			constraint_2 = cplex.SparsePair(ind = [Xbw[i][c][l][m] for i in range(len(bw_demand[0]))] + [Zbw[c][l][m]],
			                                 val = [bw_demand[0][i] for i in range(len(bw_demand[0]))] + [-lower_bound[l][m]])
			model.linear_constraints.add(lin_expr = [constraint_2],                    
			                                senses = ["G"], 
			                                rhs = [0.0]);
###################################################################################################

############ 2.2. Set the proper band based on upper bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		if isColor[l] == 1:
			for m in range(num_bands):       
				constraint_2 = cplex.SparsePair(ind = [Xc[i][c][l][m] for i in range(len(colour_demand[0]))] + [Zbw[c][l][m]],
				                                 val = [colour_demand[0][i] for i in range(len(colour_demand[0]))] + [-upper_bound[l][m]])
				model.linear_constraints.add(lin_expr = [constraint_2],                    
				                                senses = ["L"], 
				                                rhs = [0.0]);
###################################################################################################

############ 2.3. Set the proper band based on lower bound ########################################
for c in range(num_copies):
	for l in range(num_types):
		if isColor[l] == 1:
			for m in range(num_bands):       
				constraint_2 = cplex.SparsePair(ind = [Xc[i][c][l][m] for i in range(len(colour_demand[0]))] + [Zbw[c][l][m]],
				                                 val = [colour_demand[0][i] for i in range(len(colour_demand[0]))] + [-lower_bound[l][m]])
				model.linear_constraints.add(lin_expr = [constraint_2],                    
				                                senses = ["G"], 
				                                rhs = [0.0]);
###################################################################################################
############ 2.4. Every unit is located to a single location ######################################

###################################################################################################

############ 2.5. Define the number of n in j and l ###############################################
for i in range(len(bw_demand[0])):
	for l in range(num_types):
		if eligibility_matrix[bw_demand[1][i]][l] != 0:
			constraint_5 = cplex.SparsePair(ind = [Xbw[i][c][l][m] for c, m in itertools.product(range(num_copies), range(num_bands))] + [Yjln[bw_demand[1][i]][l]],
											val = [1.0] * num_bands * num_copies + [-1.0])
			model.linear_constraints.add(lin_expr = [constraint_5],
										senses = ["L"],
										rhs = [0.0])
for i in range(len(colour_demand[0])):
	for l in range(num_types):
		if eligibility_matrix[colour_demand[1][i]][l] != 0:
			if isColor[l] == 1:
				constraint_5 = cplex.SparsePair(ind = [Xc[i][c][l][m] for c, m in itertools.product(range(num_copies), range(num_bands))] + [Yjln[colour_demand[1][i]][l]],
												val = [1.0] * num_bands * num_copies + [-1.0])
				model.linear_constraints.add(lin_expr = [constraint_5],
											senses = ["L"],
											rhs = [0.0])
###################################################################################################

############ 2.7. Every unit is assigned to a single band #########################################
for c in range(num_copies):
	for l in range(num_types):
		constraint_7 = cplex.SparsePair(ind = [Xbw[i][c][l][m] for i, m in itertools.product(range(len(bw_demand[0])), range(num_bands))],
										val = [1.0] * num_bands * len(bw_demand[0]))
		model.linear_constraints.add(lin_expr = [constraint_7],
									senses = ["L"],
									rhs = [1.0])
for c in range(num_copies):
	for l in range(num_types):
		constraint_7 = cplex.SparsePair(ind = [Xc[i][c][l][m] for i, m in itertools.product(range(len(colour_demand[0])), range(num_bands))],
										val = [1.0] * num_bands * len(colour_demand[0]))
		model.linear_constraints.add(lin_expr = [constraint_7],
									senses = ["L"],
									rhs = [1.0])
###################################################################################################


############ 2.9. Set the tij variable. ###########################################################

###################################################################################################

test_list1 = []
for i in range(len(bw_demand[0])):
	for m in range(num_bands):
		test_list1.append(bw_demand[0][i])
test_list2 = []
for i in range(len(colour_demand[0])):
	for m in range(num_bands):
		test_list2.append(colour_demand[0][i])

for l in range(num_types):
	for c in range(num_copies):
		constraint_12 = cplex.SparsePair(ind = [Xbw[i][c][l][m] for i, m in itertools.product(range(len(bw_demand[0])), range(num_bands))] + [Xc[i][c][l][m] for i, m in itertools.product(range(len(colour_demand[0])), range(num_bands))],
										val = test_list1 + test_list2)
		model.linear_constraints.add(lin_expr = [constraint_12],
									senses = ["L"],
									rhs = [lcap[l]])

#for i in range(len(bw_demand[0])):
#	for l in range(num_types):
#		if eligibility_matrix[bw_demand[1][i]][l] == 0:
#			constraint_13 = cplex.SparsePair(ind = [Xbw[i][c][l][m] for c, m in itertools.product(range(num_copies), range(num_bands))],
#											val = [1.0] * num_copies * num_bands)
#			model.linear_constraints.add(lin_expr = [constraint_13],
#										senses = ["E"],
#										rhs = [0])

#for i in range(len(colour_demand[0])):
#	for l in range(num_types):
#		if isColor[l] == 0:
#			if eligibility_matrix[bw_demand[1][i]][l] == 0:
#				constraint_14 = cplex.SparsePair(ind = [Xc[i][c][l][m] for c, m in itertools.product(range(num_copies), range(num_bands))],
#												val = [1.0] * num_copies * num_bands)
#				model.linear_constraints.add(lin_expr = [constraint_14],
#											senses = ["E"],
#											rhs = [0])

############ 3. Solve the model #################################################################################################

model.objective.set_sense(model.objective.sense.minimize)
model.solve()
print "----------------------------------------------------------------------------------"
print "Total Cost: "+str(round(model.solution.get_objective_value(),2))+" euros"
print "----------------------------------------------------------------------------------"

start_model = time.time()




