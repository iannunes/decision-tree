import CART
import math
import numpy as np
import datetime
import random
import sys

#params = CART.Params("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\p10.txt","",30,4,5)
#solution = CART.Solution(params)                
#greedy = CART.Greedy(params, solution)
#%%

def getNextSolution(solutions, count):
    maxMismatch = sys.maxsize
    sol = ""
    indice = -1
    
    for i,s in solutions.items():
        indice=i
        if (count % 4 == 0):
            print("SOLUCAO ALEATÓRIA")
            return solutions.pop(indice)
        m = s.calculateMisclassifiedSamples()
        if (m<maxMismatch):
            sol=s
            maxMismatch = m
        if (m==0):
            break
    print("SOLUCAO MELHOR ATE O MOMENTO")
    return solutions.pop(indice)


def execute(pathData,pathOutput,seedRNG, maxDepth, maxTime):
    solutions = {}
    allsolutions = {}
    tabu = {}
    
    countTests = 1
    countSolutions = 1
    print("----- STARTING DECISION TREE OPTIMIZATION")
    params = CART.Params(pathData,pathOutput,seedRNG, maxDepth, maxTime)
    sol = CART.Solution(params, countSolutions)
    countSolutions +=1

    # 		// Run the greedy algorithm
    print("----- STARTING DECISION TREE OPTIMIZATION")

    params.startTime = datetime.datetime.now()
    greedy = CART.Greedy(params, sol, True)
 		    #// Printing the solution and exporting statistics (also export results into a file)

    sol.printAndExport(pathOutput)
    nodes, nodeToString = sol.countNodes()
    solutions[nodeToString] = sol
    allsolutions[nodeToString] = sol

    solutionsTested = {}

    for i in range(0,params.nbAttributes):
        countTests += 1
        solution = CART.Solution(params,countSolutions)
        countSolutions +=1
        greedy = CART.Greedy(params, solution, False)
        greedy.recursiveConstruction(0,0,i)

        solutionsTested[str(solution.id)+"_0_"+str(i)]= solution
        tabu[str(solution.id)+"_0_"+str(i)] = countTests

        nodeCount, nodeToString = solution.countNodes()
        solutions[nodeToString] = solution
        allsolutions[nodeToString] = solution
        #print("ROOT WITH ATTRIBUTE ", i," MISCLASSIFIED: ", solution.calculateMisclassifiedSamples()," USING ", nodeCount ," NODES - TIME: " ,solution.getTime())
    #    #solution.printAndExport(pathOutput)

    nodelist = []
    splitAtributelist = []
    for k in range(0, len(sol.tree)):
        if (sol.tree[k].nodeType != CART.NodeType.NODE_NULL):
            nodelist.append(k)
            splitAtributelist.append(sol.tree[k].splitAttribute)
    
    #misclassified, sol = solutions.pop(0)
    sol = getNextSolution(solutions,countTests)
    countSkippedTests = 0
    countSkippedAtrributes = 0
    while (datetime.datetime.now()-params.startTime).seconds<maxTime:
        if len(nodelist)==0:
            break
        
        for i in range(0, len(nodelist)):
            if (sol.tree[i].nodeType == CART.NodeType.NODE_LEAF):
                continue
            countTests += 1
            if (countSkippedTests > 3):
                countSkippedTests=0
                nodelist = []
                splitAtributelist = []
                tabu = {}
                if len(solutions)==0:
                    break
                sol = getNextSolution(solutions,countTests)
                print("TROCANDO SOLUCAO BASE - ", sol.calculateMisclassifiedSamples(), " - SOLUCOES POSSIVEIS ", len(solutions))
                for l in range(0, len(sol.tree)):
                    if (sol.tree[l].nodeType != CART.NodeType.NODE_NULL):
                        nodelist.append(l)
                        splitAtributelist.append(sol.tree[l].splitAttribute)
                break

            solution = CART.Solution(params, countSolutions)
            countSolutions +=1

            attrib = random.randint(0,params.nbAttributes - 1)
            while (attrib in splitAtributelist):
                attrib = random.randint(0,params.nbAttributes - 1)
                countSkippedAtrributes+=1
                if (countSkippedAtrributes > 20):
                    break

            countSkippedAtrributes = 0
            testedKey = str(i)+"_"+str(attrib)
            if (testedKey in tabu):
                #if (tabu[testedKey]+50<countTests):
                countSkippedTests+=1
                tabu[testedKey] = countTests
                continue

            node = nodelist[i]
            for j in range(len(nodelist)):
                node2 = nodelist[j]
                if (solution.tree[node2].nbSamplesNode > 0):
                    solution.tree[node2].resetNode()
                for sample in sol.tree[node2].samples:
                    solution.tree[node2].addSample(sample)
                solution.tree[node2].nodeType = sol.tree[node2].nodeType
                solution.tree[node2].splitAttribute = sol.tree[node2].splitAttribute
                solution.tree[node2].splitValue = sol.tree[node2].splitValue
                solution.tree[node2].entropy = sol.tree[node2].entropy
                solution.tree[node2].level = sol.tree[node2].level
                solution.tree[node2].majorityClass = sol.tree[node2].majorityClass
                solution.tree[node2].evaluate()

            greedy = CART.Greedy(params, solution, False)
            greedy.recursiveConstruction(node, sol.tree[node].level, attrib)

            nodeCount, nodeToString = solution.countNodes()
            
            #solutionsTested[testedKey]= solution
            tabu[testedKey] = countTests
            
            #solution.printAndExport(pathOutput);
            if (nodeToString not in allsolutions):
                #print("NODE ", node ," LEVEL ",solution.tree[node].level, "ATTRIBUTE ",attrib," - MISCLASSIFIED: ",solution.calculateMisclassifiedSamples(),"  USING ", nodeCount ," NODES - TIME: " ,solution.getTime())
                solutions[nodeToString] = solution
            
            allsolutions[nodeToString] = solution

            if (datetime.datetime.now()-params.startTime).seconds>maxTime:
                break

    params.endTime = datetime.datetime.now()
    print("----- END OF ALGORITHM")

    bestSolutionMisclassified = params.nbSamples
    bestSolution = ""
    bestNodeCount = len(sol.tree)
    for i,s in allsolutions.items():
        sMissclassified = s.calculateMisclassifiedSamples()
        if (sMissclassified < bestSolutionMisclassified):
            bestSolutionMisclassified = sMissclassified 
            bestSolution = s
            bestNodeCount = s.countNodes()
            #s.printAndExport(pathOutput)
        elif (sMissclassified == bestSolutionMisclassified):
            if (s.countNodes() < bestNodeCount):
                bestSolutionMisclassified = sMissclassified 
                bestSolution = s
                bestNodeCount = s.countNodes()
                #s.printAndExport(pathOutput)

    print("----- BEST SOLUTION")
    bestSolution.printAndExport(pathOutput)

    print("----- DECISION TREE OPTIMIZATION COMPLETED IN ", (params.endTime - params.startTime), "(s)")

fileTime = str(datetime.datetime.now().year) + str(datetime.datetime.now().month)+str(datetime.datetime.now().day)+str(datetime.datetime.now().hour)+str(datetime.datetime.now().minute)+str(datetime.datetime.now().second)
levels = 4
maxExecutionTime=1200
file = "p01.txt"
execute("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\"+file,"C:\\Users\\iannu\\\Documents\\doutorado\\\codigo\\metaheuristicas\\decision-tree\\decision-tree\\Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
file = "p02.txt"
execute("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\"+file,"C:\\Users\\iannu\\\Documents\\doutorado\\\codigo\\metaheuristicas\\decision-tree\\decision-tree\\Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
file = "p03.txt"
execute("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\"+file,"C:\\Users\\iannu\\\Documents\\doutorado\\\codigo\\metaheuristicas\\decision-tree\\decision-tree\\Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
file = "p04.txt"
execute("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\"+file,"C:\\Users\\iannu\\\Documents\\doutorado\\\codigo\\metaheuristicas\\decision-tree\\decision-tree\\Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
file = "p05.txt"
execute("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\"+file,"C:\\Users\\iannu\\\Documents\\doutorado\\\codigo\\metaheuristicas\\decision-tree\\decision-tree\\Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
file = "p06.txt"
execute("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\"+file,"C:\\Users\\iannu\\\Documents\\doutorado\\\codigo\\metaheuristicas\\decision-tree\\decision-tree\\Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
file = "p07.txt"
execute("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\"+file,"C:\\Users\\iannu\\\Documents\\doutorado\\\codigo\\metaheuristicas\\decision-tree\\decision-tree\\Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
file = "p08.txt"
execute("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\"+file,"C:\\Users\\iannu\\\Documents\\doutorado\\\codigo\\metaheuristicas\\decision-tree\\decision-tree\\Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
file = "p09.txt"
execute("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\"+file,"C:\\Users\\iannu\\\Documents\\doutorado\\\codigo\\metaheuristicas\\decision-tree\\decision-tree\\Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
file = "p10.txt"
execute("C:\\Users\\iannu\\Dropbox\\doutorado\\metaheuristics\\decision-tree\\Datasets\\"+file,"C:\\Users\\iannu\\\Documents\\doutorado\\\codigo\\metaheuristicas\\decision-tree\\decision-tree\\Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)


