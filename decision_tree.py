import CART
import math
import numpy as np
import datetime
import random
import sys

def getNextSolution(solutions, count, lastvalue:-1):
    minMismatch = sys.maxsize
    minNodes = sys.maxsize
    indice = -1
    nodelist = []
    splitAtributelist = []
    printString = ""
    if (count % 3 == 0):
        printString = "SOLUCAO ALEATÓRIA           "
        for i in range(0,len(solutions)):
            s = random.randint(0,len(solutions)-1)
            misclassified=solutions[s].calculateMisclassifiedSamples()
            if ((lastvalue>0)and (lastvalue==misclassified)):
                continue
            minMismatch = misclassified
            nodes,nodetostring = solutions[s].countNodes()
            minNodes=nodes
            indice = s
            break
    else:
        printString = "MELHOR SOLUCAO ATE O MOMENTO"

        for i in range(0,len(solutions)):
            misclassified = solutions[i].calculateMisclassifiedSamples()
            if ((lastvalue>0)and (lastvalue==misclassified)):
                continue
            if (misclassified <= minMismatch):
                nodes,nodetostring = solutions[i].countNodes()
                if (misclassified==minMismatch):
                    if (nodes<minNodes):
                        minNodes = nodes
                        indice = i
                        minMismatch = misclassified
                else:
                    minNodes = nodes
                    indice = i
                    minMismatch = misclassified

                if (minMismatch == 0):
                    break

    sol = solutions.pop(indice)
    for l in range(0, len(sol.tree)):
        if (sol.tree[l].nodeType != CART.NodeType.NODE_NULL):
            splitAtributelist.append(sol.tree[l].splitAttribute)
            if (sol.tree[l].nodeType != CART.NodeType.NODE_INTERNAL):
                continue
            nodelist.append(l)
    
    print(printString + " - TROCANDO SOLUCAO BASE - ", minMismatch, " - COM ", minNodes," NÓS - SOLUCOES POSSIVEIS ", len(solutions))
    return sol, nodelist, splitAtributelist

def eliminateWorstCandidateSolutions(solutions, delta):
    newSolutions = []
    minMismatch = sys.maxsize

    for i in range(0,len(solutions)):
        misclassified = solutions[i].calculateMisclassifiedSamples()
        if (misclassified < minMismatch):
            minMismatch = misclassified

    for i in range(0,len(solutions)):
        min=solutions[i].calculateMisclassifiedSamples()
        if (minMismatch*delta>min):
            newSolutions.append(solutions[i])
    
    if (len(newSolutions)==0):
        min = minMismatch
        minMismatch = sys.maxsize
        for i in range(0,len(solutions)):
            misclassified = solutions[i].calculateMisclassifiedSamples()
            if ((misclassified < minMismatch) and (misclassified > min)):
                minMismatch = misclassified
        for i in range(0,len(solutions)):
            if (minMismatch*delta>solutions[i].calculateMisclassifiedSamples()):
                newSolutions.append(solutions[i])

    return newSolutions

def execute(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug):
    solutions = []
    allsolutions = {}
    tabu = {}
    tabuValorMisClassified = {}
    counttabuValorMisClassified = 0
    random.seed(seedRNG)
    
    countTests = 1
    print("----- STARTING DECISION TREE OPTIMIZATION")
    params = CART.Params(pathData,pathOutput,seedRNG, maxDepth, maxTime)
    sol = CART.Solution(params, countTests)

    # 		// Run the greedy algorithm
    print("----- STARTING DECISION TREE OPTIMIZATION")

    params.startTime = datetime.datetime.now()
    greedy = CART.Greedy(params)
    sol = greedy.recursiveConstruction(0,0,"",1,sol,allsolutions)
    nodeCount, nodeToString = sol.countNodes()
    #solutions.append(sol)
    #allsolutions[nodeToString] = sol

#// Printing the solution and exporting statistics (also export results into a file)
    sol.printAndExport(pathOutput)

    nbSearchChildren = 2
    if params.nbAttributes<30:
        nbSearchChildren = 3
    elif params.nbAttributes<20:
        nbSearchChildren = 5
    elif params.nbAttributes<10:
        nbSearchChildren = 6

    for i in range(0,int(params.nbAttributes)):
        countTests += 1
        solution = CART.Solution(params,countTests)
        greedy = CART.Greedy(params)
        att = i

        solution = greedy.recursiveConstruction(0,0,att,nbSearchChildren,solution,allsolutions)

        tabu["0_"+str(att)] = countTests

        nodeCount, nodeToString = solution.countNodes()
        #solutions.append(solution)
        allsolutions[nodeToString] = solution
        if (debug):
            print("ROOT WITH ATTRIBUTE ", att," MISCLASSIFIED: ", solution.calculateMisclassifiedSamples()," USING ", nodeCount ," NODES - TIME: " ,solution.getTime())
    #   #solution.printAndExport(pathOutput)

    for i,s in allsolutions.items():
        solutions.append(s)

    countSkippedTests = 0
    countSkippedAtrributes = 0
    sol = None

    while (datetime.datetime.now()-params.startTime).seconds<maxTime:
        if (len(solutions)==0):
            if (debug):
                print("SEM MAIS SOLUCOES A EXPLORAR")
            break

        if (sol == None):
            tabu = {}
            countSkippedTests=0

            lastValue = -1
            if (sol!=None):
                lastValue = sol.calculateMisclassifiedSamples()
            solutions = eliminateWorstCandidateSolutions(solutions, 1.5)
            if (len(solutions)==0):
                if (debug):
                    print("SEM MAIS SOLUCOES A EXPLORAR")
                break

            sol, nodelist, splitAtributelist = getNextSolution(solutions, countTests, lastValue)

            if len(nodelist)==0:
                sol = None
                continue

        for i in range(1, len(nodelist)):
            if (datetime.datetime.now()-params.startTime).seconds>maxTime:
                print("TEMPO LIMITE ALCANCADO")
                break
            if (countSkippedTests > 10):
                if (len(solutions)==0):
                    break
                sol=None
                break
            for attrib in range(0,params.nbAttributes):
                countTests += 1
                if (countSkippedTests > 10):
                    if (len(solutions)==0):
                        break
                    sol=None
                    break

                node = nodelist[i]
                solution = sol.copy(countTests)

                #attrib = random.randint(0,params.nbAttributes - 1)
                #while (attrib in splitAtributelist):
                #    attrib = random.randint(0,params.nbAttributes - 1)
                #    countSkippedAtrributes+=1
                #    if (countSkippedAtrributes > 20):
                #        break

                countSkippedAtrributes = 0
                testedKey = str(node)+"_"+str(attrib)
                if (testedKey in tabu):
                    countSkippedTests+=1
                    if (countTests-tabu[testedKey]<100):
                        if (debug):
                            print("----------------SOLUCAO TABU----------------")
                        continue
                    tabu[testedKey] = countTests

                greedy = CART.Greedy(params)
                allsolutionstemp = {}
                solution = greedy.recursiveConstruction(node, sol.tree[node].level, attrib, nbSearchChildren, solution, allsolutionstemp)

                nodeCount, nodeToString = solution.countNodes()

                if (nodeToString in allsolutions):
                    for itemp,stemp in allsolutionstemp.items():
                        if (itemp not in allsolutions):
                            allsolutions[itemp] = stemp
                    countSkippedTests+=1
                    if (debug):
                        print("----------------SOLUCAO JA TESTADA----------------")
                    continue

                for itemp,stemp in allsolutionstemp.items():
                    if (itemp not in allsolutions):
                        allsolutions[itemp] = stemp

                tabu[testedKey] = countTests
            
                if (debug):
                    print("N", node ," LEVEL ",solution.tree[node].level, "ATTRIBUTE ",attrib," - MISCLASSIFIED: ",solution.calculateMisclassifiedSamples(),"  USING ", nodeCount ," NODES - TIME: " ,solution.getTime())
                solutions.append(solution)
            
                #allsolutions[nodeToString] = solution

                if (datetime.datetime.now()-params.startTime).seconds>maxTime:
                    print("TEMPO LIMITE ALCANCADO")
                    break

    params.endTime = datetime.datetime.now()
    print("----- END OF ALGORITHM")

    bestSolutionMisclassified = params.nbSamples
    bestSolution = ""
    bestNodeCount = 2**(params.maxDepth+1)-1
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

def executeILS(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug):
    random.seed(seedRNG)
    countTests=1
    allsolutions = {}
    print("----- STARTING DECISION TREE OPTIMIZATION")
    params = CART.Params(pathData,pathOutput,seedRNG, maxDepth, maxTime)
    sol = CART.Solution(params, countTests)

    # 		// Run the greedy algorithm
    print("----- STARTING DECISION TREE OPTIMIZATION")

    params.startTime = datetime.datetime.now()
    greedy = CART.Greedy(params)
    sol = greedy.recursiveConstruction(0,0,"",1,sol,allsolutions)
    nodeCount, nodeToString = sol.countNodes()
    sol.printAndExport(pathOutput)

    nodelist = []
    for i in range(0,len(sol.tree)):
        if (sol.tree[i].nodeType==CART.NodeType.NODE_INTERNAL):
            nodelist.append(i)
    bestSolution = sol
    bestMisclassified = sol.calculateMisclassifiedSamples()
    bestNodes = nodeCount
    history = {}
    
    skippedTests = 0
    while (datetime.datetime.now()-params.startTime).seconds < maxTime:
        countTests+=1
        node = nodelist[random.randint(0,len(nodelist)-1)]
        attrib = random.randint(0,params.nbAttributes-1)

        key = str(sol.id)+""+str(node)+""+str(attrib)

        if (key in history):
            if (debug):
                print("SOLUCAO TESTADA")
            skippedTests+=1
            if (skippedTests > 10):
                sol = random.choice(list(allsolutions.values()))
                skippedTests = 0
                continue
            continue

        history[key] = 1

        solution = sol.copy(countTests)

        greedy = CART.Greedy(params)
        solution = greedy.recursiveConstruction(node, solution.tree[node].level, attrib, 5, solution, allsolutions)

        misclassified = solution.calculateMisclassifiedSamples()
        nodeCount, nodeToString = solution.countNodes()

        if ((misclassified>3*bestMisclassified) and (bestSolution.id!=sol.id)):
            if (debug):
                print("RETORNANDO PARA MELHOR SOLUCAO ENCONTRADA")
            sol = bestSolution
        elif (misclassified <= bestMisclassified):
            best = False
            if (misclassified==bestMisclassified):
                if (nodeCount<bestNodes):
                    bestSolution = solution
                    bestMisclassified = misclassified
                    bestNodes = nodeCount
                    best=True
            else:
                best=True
                bestSolution = solution
                bestMisclassified = misclassified
                bestNodes = nodeCount

            if best:
                sol = solution
                if (debug):
                    print("MELHOR SOLUCAO ENCONTRADA")
                nodelist = []
                for i in range(0,len(sol.tree)):
                    if (sol.tree[i].nodeType==CART.NodeType.NODE_INTERNAL):
                        nodelist.append(i)

        elif random.randint(0,sys.maxsize)%20==0:
            if (debug):
                print("PERTURBANDO!!!")
            sol = solution
            nodelist = []
            for i in range(0,len(sol.tree)):
                if (sol.tree[i].nodeType==CART.NodeType.NODE_INTERNAL):
                    nodelist.append(i)

        if (debug):
            print("N", node ," LEVEL ",solution.tree[node].level, "ATTRIBUTE ",attrib," - MISCLASSIFIED: ",solution.calculateMisclassifiedSamples(),"  USING ", nodeCount ," NODES - TIME: " ,solution.getTime())
    params.endTime = datetime.datetime.now()
    print("----- BEST SOLUTION")
    bestSolution.printAndExport(pathOutput)

    print("----- DECISION TREE OPTIMIZATION COMPLETED IN ", (params.endTime - params.startTime), "(s)")

fileTime = str(datetime.datetime.now().year) + str(datetime.datetime.now().month)+str(datetime.datetime.now().day)+str(datetime.datetime.now().hour)+str(datetime.datetime.now().minute)+str(datetime.datetime.now().second)
levels = 5
maxExecutionTime=120
debug=True


#file = "p01.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p02.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
file = "p03.txt"
executeILS("Datasets\\"+file,"Solutions\\ILS"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
file = "p04.txt"
executeILS("Datasets\\"+file,"Solutions\\ILS"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
file = "p05.txt"
executeILS("Datasets\\"+file,"Solutions\\ILS"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p06.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p07.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p08.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p09.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p10.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)

#file = "p01.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p02.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p03.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p04.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p05.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p06.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p07.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p08.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p09.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p10.txt"
#execute("Datasets\\"+file,"Solutions\\"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)


