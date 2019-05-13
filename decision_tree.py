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
        if (count % 2 == 0):
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
    solutions[str(sol.calculateMisclassifiedSamples())+nodeToString] = sol
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
        solutions[str(solution.calculateMisclassifiedSamples())+nodeToString] = solution
        allsolutions[nodeToString] = solution
        print("ROOT WITH ATTRIBUTE ", i," MISCLASSIFIED: ", solution.calculateMisclassifiedSamples()," USING ", nodeCount ," NODES - TIME: " ,solution.getTime())
    #   #solution.printAndExport(pathOutput)

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

            countTests += 1
            if (countSkippedTests > 3):
                countSkippedTests=0
                nodelist = []
                splitAtributelist = []
                tabu = {}
                if len(solutions)==0:
                    break
                sol = getNextSolution(solutions, countTests)
                print("TROCANDO SOLUCAO BASE - ", sol.calculateMisclassifiedSamples(), " - SOLUCOES POSSIVEIS ", len(solutions))
                for l in range(0, len(sol.tree)):
                    if (sol.tree[l].nodeType != CART.NodeType.NODE_NULL):
                        nodelist.append(l)
                        splitAtributelist.append(sol.tree[l].splitAttribute)
                break

            if (sol.tree[i].nodeType != CART.NodeType.NODE_INTERNAL):
                continue

            solution = sol.copy(countSolutions)

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

            greedy = CART.Greedy(params, solution, False)
            greedy.recursiveConstruction(node, sol.tree[node].level, attrib)

            nodeCount, nodeToString = solution.countNodes()
            
            #solutionsTested[testedKey]= solution
            tabu[testedKey] = countTests
            
            #solution.printAndExport(pathOutput);
            if (str(solution.calculateMisclassifiedSamples())+nodeToString not in allsolutions):
                print(solution.tree[node].nodeType," ", node ," LEVEL ",solution.tree[node].level, "ATTRIBUTE ",attrib," - MISCLASSIFIED: ",solution.calculateMisclassifiedSamples(),"  USING ", nodeCount ," NODES - TIME: " ,solution.getTime())
                solutions[str(solution.calculateMisclassifiedSamples())+nodeToString] = solution
            
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
levels = 5
maxExecutionTime=180

#file = "p01.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
#file = "p02.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
#file = "p03.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
#file = "p04.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
#file = "p05.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
#file = "p06.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
#file = "p07.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
#file = "p08.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
#file = "p09.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)
file = "p10.txt"
execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime)


