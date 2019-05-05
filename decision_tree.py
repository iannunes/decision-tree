import CART
import math
import numpy as np
import datetime

#params = CART.Params("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\p10.txt","",30,4,5)
#solution = CART.Solution(params)                
#greedy = CART.Greedy(params, solution)
#%%
print("----- STARTING DECISION TREE OPTIMIZATION")
params = CART.Params("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\p10.txt","",30,4,5)
sol = CART.Solution(params)

# 		// Run the greedy algorithm
print("----- STARTING DECISION TREE OPTIMIZATION")
# 		std::cout << "----- STARTING DECISION TREE OPTIMIZATION" << std::endl;

params.startTime = datetime.datetime.now()
greedy = CART.Greedy(params,sol)
# 		Greedy solver(&params,&solution);
# 		solver.run();
params.endTime = datetime.datetime.now()
print("----- DECISION TREE OPTIMIZATION COMPLETED IN ", (params.endTime - params.startTime), "(s)")
 		#// Printing the solution and exporting statistics (also export results into a file)
sol.printAndExport("");
print("----- END OF ALGORITHM")
#%%