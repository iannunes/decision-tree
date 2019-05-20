import CART
import math
import numpy as np
import datetime
import random
import sys
from scipy.stats import ttest_1samp, wilcoxon, ttest_ind, mannwhitneyu

#def getNextSolution(solutions, count, lastvalue:-1):
#    minMismatch = sys.maxsize
#    minNodes = sys.maxsize
#    indice = -1
#    nodelist = []
#    splitAtributelist = []
#    printString = ""
#    lastValueIgnored = False
#    if (count % 3 == 0):
#        printString = "SOLUCAO ALEATÓRIA"
#        for i in range(0,len(solutions)):
#            s = random.randint(0,len(solutions)-1)
#            misclassified=solutions[s].calculateMisclassifiedSamples()
#            if ((lastvalue>0)and (lastvalue==misclassified)):
#                continue
#            minMismatch = misclassified
#            nodes,nodetostring = solutions[s].countNodes()
#            minNodes=nodes
#            indice = s
#            break
#    else:
#        printString = "MELHOR SOLUCAO   "

#        for i in range(0,len(solutions)):
#            misclassified = solutions[i].calculateMisclassifiedSamples()
#            if (misclassified <= minMismatch):
#                if ((lastvalue>=0)and (lastvalue==misclassified)):
#                    lastValueIgnored = True
#                    continue
#                nodes,nodetostring = solutions[i].countNodes()
#                if (misclassified==minMismatch):
#                    if (nodes<minNodes):
#                        minNodes = nodes
#                        indice = i
#                        minMismatch = misclassified
#                else:
#                    minNodes = nodes
#                    indice = i
#                    minMismatch = misclassified

#                if (minMismatch == 0):
#                    break

#    sol = solutions.pop(indice)
#    for l in range(0, len(sol.tree)):
#        if (sol.tree[l].nodeType != CART.NodeType.NODE_NULL):
#            splitAtributelist.append(sol.tree[l].splitAttribute)
#            if (sol.tree[l].nodeType != CART.NodeType.NODE_INTERNAL):
#                continue
#            nodelist.append(l)
    
#    print(printString + " - TROCANDO SOLUCAO - ", minMismatch, " - ", minNodes," NÓS - SOLS POSSIVEIS ", len(solutions), " - ULTIMO IGNORADO", lastValueIgnored)
#    return sol, nodelist, splitAtributelist

#def eliminateWorstCandidateSolutions(solutions, delta):
#    newSolutions = []
#    minMismatch = sys.maxsize

#    for i in range(0,len(solutions)):
#        misclassified = solutions[i].calculateMisclassifiedSamples()
#        if (misclassified < minMismatch):
#            minMismatch = misclassified

#    for i in range(0,len(solutions)):
#        min=solutions[i].calculateMisclassifiedSamples()
#        if (minMismatch*delta>min):
#            newSolutions.append(solutions[i])
    
#    if (len(newSolutions)==0):
#        min = minMismatch
#        minMismatch = sys.maxsize
#        for i in range(0,len(solutions)):
#            misclassified = solutions[i].calculateMisclassifiedSamples()
#            if ((misclassified < minMismatch) and (misclassified > min)):
#                minMismatch = misclassified
#        for i in range(0,len(solutions)):
#            if (minMismatch*delta>solutions[i].calculateMisclassifiedSamples()):
#                newSolutions.append(solutions[i])

#    return newSolutions

#def executeOLD(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug):
#    solutions = []
#    allsolutions = {}
#    tabu = {}
#    tabuValorMisClassified = {}
#    counttabuValorMisClassified = 0
#    random.seed(seedRNG)
    
#    countTests = 1
#    print("----- STARTING DECISION TREE OPTIMIZATION")
#    params = CART.Params(pathData,pathOutput,seedRNG, maxDepth, maxTime)
#    sol = CART.Solution(params, countTests)

#    # 		// Run the greedy algorithm
#    print("----- STARTING DECISION TREE OPTIMIZATION")

#    params.startTime = datetime.datetime.now()
#    greedy = CART.Greedy(params)
#    sol = greedy.recursiveConstruction(0,0,"",1,sol,allsolutions)
#    nodeCount, nodeToString = sol.countNodes()
#    #solutions.append(sol)
#    #allsolutions[nodeToString] = sol

##// Printing the solution and exporting statistics (also export results into a file)
#    sol.printAndExport(pathOutput)

#    nbSearchChildren = 2
#    if params.nbAttributes<30:
#        nbSearchChildren = 3
#    elif params.nbAttributes<20:
#        nbSearchChildren = 4
#    elif params.nbAttributes<10:
#        nbSearchChildren = 5

#    #for i in range(0,int(params.nbAttributes)):
#    #    countTests += 1
#    #    solution = CART.Solution(params,countTests)
#    #    greedy = CART.Greedy(params)
#    #    att = i

#    #    solution = greedy.recursiveConstruction(0,0,att,nbSearchChildren,solution,allsolutions)
#    #    tabu["0_"+str(att)] = countTests

#    #    nodeCount, nodeToString = solution.countNodes()
#    #    allsolutions[nodeToString] = solution
#    #    if (debug):
#    #        print("ROOT WITH ATTRIBUTE ", att," MISCLASSIFIED: ", solution.calculateMisclassifiedSamples()," USING ", nodeCount ," NODES - TIME: " ,solution.getTime())

#    for i,s in allsolutions.items():
#        solutions.append(s)

#    countSkippedTests = 0
#    countSkippedAtrributes = 0
#    sol = None
#    lastValue = -1
#    countTests=0
#    print("SOLUCOES INICIAIS: ", len(allsolutions))
#    while (datetime.datetime.now()-params.startTime).seconds<maxTime:
#        if (len(solutions)==0):
#            print("GERANDO NOVA SOLUCAO INCIAL")
#            sol = CART.Solution(params, countTests)
#            greedy = CART.Greedy(params)
#            sol = greedy.recursiveConstruction(0,0,random.randint(0,params.nbAttributes-1),3,sol,allsolutions)
#            for i,s in allsolutions.items():
#                solutions.append(s)
#            #if (debug):
#            #    print("GERANDO NOVA SOLUCAO INCIAL")

#        if (sol == None):
#            tabu = {}
#            countSkippedTests=0

#            solutions = eliminateWorstCandidateSolutions(solutions, 1.5)
#            if (len(solutions)==0):
#                if (debug):
#                    print("SEM MAIS SOLUCOES A EXPLORAR")
#                break

#            sol, nodelist, splitAtributelist = getNextSolution(solutions, countTests, lastValue)

#            if len(nodelist)==0:
#                sol = None
#                continue

#            if (sol!=None):
#                lastValue = sol.calculateMisclassifiedSamples()

#        for i in range(0, len(nodelist)):
#            if (datetime.datetime.now()-params.startTime).seconds>maxTime:
#                print("TEMPO LIMITE ALCANCADO")
#                break
#            #if (countSkippedTests > 10):
#            #    if (len(solutions)==0):
#            #        break
#            #    sol=None
#            #    break
#            for attrib in range(0,params.nbAttributes):
#                countTests += 1

#                if (sol==None):
#                    break
#                if (countTests %50 == 0):
#                    solutions=[]
#                    sol=None
#                    break

                

#                node = nodelist[i]
#                solution = sol.partialCopy(random.randint(300000000,900000000),node)

#                #attrib = random.randint(0,params.nbAttributes - 1)
#                #while (attrib in splitAtributelist):
#                #    attrib = random.randint(0,params.nbAttributes - 1)
#                #    countSkippedAtrributes+=1
#                #    if (countSkippedAtrributes > 20):
#                #        break

#                countSkippedAtrributes = 0
#                testedKey = str(node)+"_"+str(attrib)
#                if (testedKey in tabu):
#                    countSkippedTests+=1
#                    if (countTests-tabu[testedKey]<100):
#                        if (debug):
#                            print("----------------SOLUCAO TABU----------------")
#                        continue
#                    tabu[testedKey] = countTests

#                greedy = CART.Greedy(params)
#                allsolutionstemp = {}
#                solution = greedy.recursiveConstruction(node, sol.tree[node].level, attrib, nbSearchChildren, solution, allsolutionstemp)

#                nodeCount, nodeToString = solution.countNodes()

#                if (nodeToString in allsolutions):
#                    for itemp,stemp in allsolutionstemp.items():
#                        if (itemp not in allsolutions):
#                            allsolutions[itemp] = stemp
#                            #solutions.append(stemp)
#                    countSkippedTests+=1
#                    if (debug):
#                        print("----------------SOLUCAO JA TESTADA----------------")
#                    continue

#                for itemp,stemp in allsolutionstemp.items():
#                    if (itemp not in allsolutions):
#                        allsolutions[itemp] = stemp

#                tabu[testedKey] = countTests
            
#                if (debug):
#                    print("N", node ," LEVEL ",solution.tree[node].level, "ATTRIBUTE ",attrib," - MISCLASSIFIED: ",solution.calculateMisclassifiedSamples(),"  USING ", nodeCount ," NODES - TIME: " ,solution.getTime())
#                solutions.append(solution)
            
#                #allsolutions[nodeToString] = solution

#                if (datetime.datetime.now()-params.startTime).seconds>maxTime:
#                    print("TEMPO LIMITE ALCANCADO")
#                    break

#    params.endTime = datetime.datetime.now()
#    print("----- END OF ALGORITHM")

#    bestSolutionMisclassified = params.nbSamples
#    bestSolution = ""
#    bestNodeCount = 2**(params.maxDepth+1)-1
#    for i,s in allsolutions.items():
#        sMissclassified = s.calculateMisclassifiedSamples()
#        if (sMissclassified < bestSolutionMisclassified):
#            bestSolutionMisclassified = sMissclassified 
#            bestSolution = s
#            bestNodeCount = s.countNodes()
#            #s.printAndExport(pathOutput)
#        elif (sMissclassified == bestSolutionMisclassified):
#            if (s.countNodes() < bestNodeCount):
#                bestSolutionMisclassified = sMissclassified 
#                bestSolution = s
#                bestNodeCount = s.countNodes()
#                #s.printAndExport(pathOutput)

#    print("----- BEST SOLUTION")
#    bestSolution.printAndExport(pathOutput)

#    print("----- DECISION TREE OPTIMIZATION COMPLETED IN ", (params.endTime - params.startTime), "(s)")

#def executeRandom(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug):
#    solutions = []
#    allsolutions = {}
#    tabu = {}
#    tabuValorMisClassified = {}
#    counttabuValorMisClassified = 0
#    random.seed(seedRNG)
    
#    countTests = 1
#    print("----- STARTING DECISION TREE OPTIMIZATION")
#    params = CART.Params(pathData,pathOutput,seedRNG, maxDepth, maxTime)
#    sol = CART.Solution(params, countTests)

#    # 		// Run the greedy algorithm
#    print("----- STARTING DECISION TREE OPTIMIZATION")

#    params.startTime = datetime.datetime.now()
#    greedy = CART.Greedy(params)
#    sol = greedy.recursiveConstructionrandom(0,0,"",5,sol,allsolutions)
#    nodeCount, nodeToString = sol.countNodes()

#    sol.printAndExport(pathOutput)

#    for i,s in allsolutions.items():
#        solutions.append(s)

#    countSkippedTests = 0
#    countSkippedAtrributes = 0
#    sol = None
#    lastValue = -1
#    countTests=0
#    print("SOLUCOES INICIAIS: ", len(allsolutions))
#    while (datetime.datetime.now()-params.startTime).seconds<maxTime:
#        if (len(solutions)==0):
#            print("GERANDO NOVA SOLUCAO INCIAL")
#            sol = CART.Solution(params, countTests)
#            greedy = CART.Greedy(params)
#            sol = greedy.recursiveConstructionrandom(0,0,random.randint(0,params.nbAttributes-1),5,sol,allsolutions)
#            for i,s in allsolutions.items():
#                solutions.append(s)

#        if (countSkippedTests>100):
#            sol=None
#            countSkippedTests=0
#            print("TROCANDO SOLUCAO POR EXCESSO DE SOLUCOES REPETIDAS")

#        if (sol == None):
#            tabu = {}
#            countSkippedTests=0

#            solutions = eliminateWorstCandidateSolutions(solutions, 1.5)
#            if (len(solutions)==0):
#                if (debug):
#                    print("SEM MAIS SOLUCOES A EXPLORAR")
#                break

#            sol, nodelist, splitAtributelist = getNextSolution(solutions, countTests, lastValue)

#            if len(nodelist)==0:
#                sol = None
#                continue

#            if (sol!=None):
#                lastValue = sol.calculateMisclassifiedSamples()
#            else:
#                continue

#        i = random.randint(0,len(nodelist)-1)

#        attrib =  random.randint(0,params.nbAttributes-1)
#        countTests += 1

#        if (sol==None):
#            continue

#        if (countTests %500 == 0):
#            solutions=[]
#            sol=None
#            continue

#        node = nodelist[i]
#        solution = sol.partialCopy(random.randint(300000000,900000000),node)

#        countSkippedAtrributes = 0
#        greedy = CART.Greedy(params)
#        allsolutionstemp = {}
#        solution = greedy.recursiveConstructionrandom(node, sol.tree[node].level, attrib, 5, solution, allsolutionstemp)

#        nodeCount, nodeToString = solution.countNodes()

#        if (nodeToString in allsolutions):
            
#            countSkippedTests+=1
            
#            continue

#        if (nodeToString in allsolutions):
#            for itemp,stemp in allsolutionstemp.items():
#                if (itemp not in allsolutions):
#                    allsolutions[itemp] = stemp
#                    solutions.append(stemp)
#            countSkippedTests+=1
#            if (debug):
#                print("----------------SOLUCAO JA TESTADA----------------")
#            continue

#        for itemp,stemp in allsolutionstemp.items():
#            if (itemp not in allsolutions):
#                allsolutions[itemp] = stemp

#        if (debug):
#            print("N", node ," LEVEL ",solution.tree[node].level, "ATTRIBUTE ",attrib," - MISCLASSIFIED: ",solution.calculateMisclassifiedSamples(),"  USING ", nodeCount ," NODES - TIME: " ,solution.getTime())
#        solutions.append(solution)
            
#        #allsolutions[nodeToString] = solution

#        if (datetime.datetime.now()-params.startTime).seconds>maxTime:
#            print("TEMPO LIMITE ALCANCADO")
#            break

#    params.endTime = datetime.datetime.now()
#    print("----- END OF ALGORITHM")

#    bestSolutionMisclassified = params.nbSamples
#    bestSolution = ""
#    bestNodeCount = 2**(params.maxDepth+1)-1
#    for i,s in allsolutions.items():
#        sMissclassified = s.calculateMisclassifiedSamples()
#        if (sMissclassified < bestSolutionMisclassified):
#            bestSolutionMisclassified = sMissclassified 
#            bestSolution = s
#            bestNodeCount = s.countNodes()
#            #s.printAndExport(pathOutput)
#        elif (sMissclassified == bestSolutionMisclassified):
#            if (s.countNodes() < bestNodeCount):
#                bestSolutionMisclassified = sMissclassified 
#                bestSolution = s
#                bestNodeCount = s.countNodes()
#                #s.printAndExport(pathOutput)

#    print("----- BEST SOLUTION")
#    bestSolution.printAndExport(pathOutput)

#    print("----- DECISION TREE OPTIMIZATION COMPLETED IN ", (params.endTime - params.startTime), "(s)")

def execute(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug, lookaheadProportion, nbBestTries):
    random.seed(seedRNG)
    countTests = 0
    allsolutions = {}
    # definir solucao inicial
    if debug:
        print("----- STARTING DECISION TREE OPTIMIZATION")
    params = CART.Params(pathData, pathOutput, seedRNG, maxDepth, maxTime, lookaheadProportion, nbBestTries, debug)
    solution = CART.Solution(params, countTests)
    if debug:
        print("----- STARTING DECISION TREE OPTIMIZATION")
    greedy = CART.Greedy(params)
    solution = greedy.recursiveConstruction(0,0,"",1, solution, allsolutions, nbBestTries)
    greedySolution = solution
    solution.printAndExport(pathOutput)
    params.startTime = datetime.datetime.now()

    # executar a LS na solucao inicial

    if debug:
        print("----- STARTING LS ON FIRST SOLUTION")
    countTests = 1
    solution = CART.Solution(params,countTests)
    solution = greedy.recursiveConstructionBestNatNode(0,0,"",nbBestTries,solution,allsolutions)
    nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
    # com a melhor solução iniciar ITL até completar o maxTime
    bestSolution = solution
    bestMisclassified = solution.calculateMisclassifiedSamples()
    bestNodes,bestNodesToString = solution.countNodes()
    if debug:
        print("----- STARTING ILS")
    lapTimes = []
    numberMod = 0
    if (lookaheadProportion>0):
        numberMod = int(math.ceil(1/lookaheadProportion))
    while True:
        initialTime = datetime.datetime.now()
        countTests += 1
        # - perturbar
        node = nodelist[random.randint(0,len(nodelist)-1)]
        attrib = random.randint(0,params.nbAttributes-1)
        solLS = solution.partialCopy(countTests,node)
        # - executar LS
        executeLookAhead = True
        if (lookaheadProportion==0):
            executeLookAhead = False
        else:
            if (countTests%numberMod != 0):
                executeLookAhead = False

        if (executeLookAhead):
            nbSearchChildren = 3
            if (solLS.tree[node].level==1):
                nbSearchChildren = 5
            elif (solLS.tree[node].level>1):
                nbSearchChildren = 7
            solLS = greedy.recursiveConstruction(node, solLS.tree[node].level, attrib, nbSearchChildren, solLS, allsolutions, nbBestTries)
        else:
            solLS = greedy.recursiveConstructionBestNatNode(node, solLS.tree[node].level, attrib, nbBestTries, solLS, allsolutions)
        # substituir a melhor solucao se for o caso
        misclassified = solLS.calculateMisclassifiedSamples()
        nodes, nodestostring = solLS.countNodes()
        if (misclassified <= bestMisclassified):
            if (misclassified == bestMisclassified):
                if (nodes<bestNodes):
                    bestSolution = solLS
                    bestMisclassified = misclassified
                    bestNodes = nodes
                    if debug:
                        print("BEST SOLUTION FOUND - ",bestMisclassified, " NODES - ", nodes)
            else:
                bestSolution = solLS
                bestMisclassified = misclassified
                bestNodes = nodes
                if debug:
                    print("BEST SOLUTION FOUND - ",bestMisclassified, " NODES - ", nodes)
            

        if (solution.id != bestSolution.id):
            solution = bestSolution
            nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
        if debug:
            initialTime = datetime.datetime.now()-initialTime
            lapTimes.append(initialTime.seconds*1000000+initialTime.microseconds)

        if (datetime.datetime.now()-params.startTime).seconds>maxTime:
            break
    params.endTime = datetime.datetime.now()

    if debug:
        timeSum = 0
        for time in lapTimes:
            timeSum+=time
        print("----- ITERATION MED TIME(microseconds): ", timeSum/len(lapTimes))

    for i,s in allsolutions.items():
        misclassified = s.calculateMisclassifiedSamples()
        if (misclassified <= bestMisclassified):
            nodes, nodestostring = s.countNodes()
            if (misclassified == bestMisclassified):
                if (nodes<bestNodes):
                    bestSolution = s
                    bestMisclassified = misclassified
                    bestNodes = nodes
            else:
                bestSolution = s
                bestMisclassified = misclassified
                bestNodes = nodes
    
    bestSolution.printAndExport(pathOutput)

    return greedySolution , bestSolution

def executeNew(pathData, pathOutput, seedRNG, maxDepth, maxTime, debug, nbSplits):
    random.seed(seedRNG)
    countTests = 0
    allsolutions = {}
    # definir solucao inicial
    if debug:
        print("----- STARTING DECISION TREE OPTIMIZATION")
    params = CART.Params(pathData, pathOutput, seedRNG, maxDepth, maxTime, 0, 0, debug)
    solution = CART.Solution(params, countTests)
    if debug:
        print("----- STARTING DECISION TREE OPTIMIZATION")
    greedy = CART.Greedy(params)
    solution = greedy.recursiveConstruction(0,0,"",1,solution,allsolutions,nbSplits)
    greedySolution = solution
    solution.printAndExport(pathOutput)

    solution = CART.Solution(params, countTests)
    if debug:
        print("----- STARTING DECISION TREE OPTIMIZATION")
    solution = CART.Solution(params, countTests)
    greedy = CART.Greedy(params)
    solution = greedy.recursiveConstruction(0,0,"",3,solution,allsolutions,nbSplits)

    params.startTime = datetime.datetime.now()

    # executar a LS na solucao inicial
    if debug:
        print("----- STARTING LS ON FIRST SOLUTION")
    countTests = 1
    solution = greedy.localsearch(0,solution, nbSplits)
       #recursiveConstructionBestNatNode(0,0,"",nbBestTries,solution,allsolutions)
    nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
    # com a melhor solução iniciar ITL até completar o maxTime
    bestSolution = solution
    bestMisclassified = solution.calculateMisclassifiedSamples()
    bestNodes,bestNodesToString = solution.countNodes()
    if debug:
        print("----- STARTING ILS")
    lapTimes = []
    numberMod = 0
    while True:
        initialTime = datetime.datetime.now()
        countTests += 1
        # - perturbar
        node = nodelist[random.randint(0,len(nodelist)-1)]
        attrib = random.randint(0,params.nbAttributes-1)
        solLS = solution.partialCopy(countTests,node)
        solLS = greedy.recursiveConstruction(node,solLS.tree[node].level,attrib,3,solution,allsolutions,nbSplits)
        # - executar LS
        solLS = greedy.localsearch(node,solLS,nbSplits)
        # substituir a melhor solucao se for o caso
        misclassified = solLS.calculateMisclassifiedSamples()
        nodes, nodestostring = solLS.countNodes()
        if (misclassified <= bestMisclassified):
            if (misclassified == bestMisclassified):
                if (nodes<bestNodes):
                    bestSolution = solLS
                    bestMisclassified = misclassified
                    bestNodes = nodes
                    if debug:
                        print("BEST SOLUTION FOUND - ",bestMisclassified, " NODES - ", nodes)
            else:
                bestSolution = solLS
                bestMisclassified = misclassified
                bestNodes = nodes
                if debug:
                    print("BEST SOLUTION FOUND - ",bestMisclassified, " NODES - ", nodes)

        if (solution.id != bestSolution.id):
            solution = bestSolution
            nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
        if debug:
            initialTime = datetime.datetime.now()-initialTime
            lapTimes.append(initialTime.seconds*1000000+initialTime.microseconds)

        if (datetime.datetime.now()-params.startTime).seconds>maxTime:
            break
    params.endTime = datetime.datetime.now()

    if debug:
        timeSum = 0
        for time in lapTimes:
            timeSum+=time
        print("----- ITERATION MED TIME(microseconds): ", timeSum/len(lapTimes))

    for i,s in allsolutions.items():
        misclassified = s.calculateMisclassifiedSamples()
        if (misclassified <= bestMisclassified):
            nodes, nodestostring = s.countNodes()
            if (misclassified == bestMisclassified):
                if (nodes<bestNodes):
                    bestSolution = s
                    bestMisclassified = misclassified
                    bestNodes = nodes
            else:
                bestSolution = s
                bestMisclassified = misclassified
                bestNodes = nodes
    
    bestSolution.printAndExport(pathOutput)

    return greedySolution , bestSolution

#def execute50bestLocalSearch(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug):
#    random.seed(seedRNG)
#    countTests = 0
#    allsolutions = {}
#    # definir solucao inicial
#    if debug:
#        print("----- STARTING DECISION TREE OPTIMIZATION")
#    params = CART.Params(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug)
#    solution = CART.Solution(params, countTests)
#    if debug:
#        print("----- STARTING DECISION TREE OPTIMIZATION")
#    greedy = CART.Greedy(params)
#    solution = greedy.recursiveConstruction(0,0,"",1,solution,allsolutions)
#    greedySolution = solution
#    if debug:
#        solution.printAndExport(pathOutput)
#    params.startTime = datetime.datetime.now()

#    # executar a LS na solucao inicial
#    if debug:
#        print("----- STARTING LS ON FIRST SOLUTION")
#    countTests = 1
#    solution = CART.Solution(params,countTests)
#    solution = greedy.recursiveConstructionBestNatNode(0,0,"",50,solution,allsolutions)
#    nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
#    # com a melhor solução iniciar ITL até completar o maxTime
#    bestSolution = solution
#    bestMisclassified = solution.calculateMisclassifiedSamples()
#    bestNodes,bestNodesToString = solution.countNodes()
#    if debug:
#        print("----- STARTING ILS")
#    lapTimes = []
#    while True:
#        initialTime = datetime.datetime.now()
#        countTests += 1
#        # - perturbar
#        node = nodelist[random.randint(0,len(nodelist)-1)]
#        attrib = random.randint(0,params.nbAttributes-1)
#        solLS = solution.partialCopy(countTests,node)
#        # - executar LS
#        solLS = greedy.recursiveConstructionBestNatNode(node, solLS.tree[node].level, attrib, 50, solLS, allsolutions)
#        # substituir a melhor solucao se for o caso
#        misclassified = solLS.calculateMisclassifiedSamples()
#        nodes, nodestostring = solLS.countNodes()
#        if (misclassified <= bestMisclassified):
#            if (misclassified == bestMisclassified):
#                if (nodes<bestNodes):
#                    bestSolution = solLS
#                    bestMisclassified = misclassified
#                    bestNodes = nodes
#                    if debug:
#                        print("BEST SOLUTION FOUND - ",bestMisclassified, " NODES - ", nodes)
#            else:
#                bestSolution = solLS
#                bestMisclassified = misclassified
#                bestNodes = nodes
#                if debug:
#                    print("BEST SOLUTION FOUND - ",bestMisclassified, " NODES - ", nodes)
            

#        if (solution.id != bestSolution.id):
#            solution = bestSolution
#            nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
#        if debug:
#            initialTime = datetime.datetime.now()-initialTime
#            lapTimes.append(initialTime.seconds*1000000+initialTime.microseconds)

#        if (datetime.datetime.now()-params.startTime).seconds>maxTime:
#            break
#    params.endTime = datetime.datetime.now()

#    timeSum = 0
#    for time in lapTimes:
#        timeSum+=time
#    if debug:
#        print("----- ITERATION MED TIME(microseconds): ", timeSum/len(lapTimes))

#    for i,s in allsolutions.items():
#        misclassified = s.calculateMisclassifiedSamples()
#        if (misclassified <= bestMisclassified):
#            nodes, nodestostring = s.countNodes()
#            if (misclassified == bestMisclassified):
#                if (nodes<bestNodes):
#                    bestSolution = s
#                    bestMisclassified = misclassified
#                    bestNodes = nodes
#            else:
#                bestSolution = s
#                bestMisclassified = misclassified
#                bestNodes = nodes
#    if debug:
#        bestSolution.printAndExport(pathOutput)

#    return greedySolution , bestSolution

#def executeILS(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug):
#    random.seed(seedRNG)
#    countTests=1
#    allsolutions = {}
#    print("----- STARTING DECISION TREE OPTIMIZATION")
#    params = CART.Params(pathData,pathOutput,seedRNG, maxDepth, maxTime)
#    sol = CART.Solution(params, countTests)

#    # 		// Run the greedy algorithm
#    print("----- STARTING DECISION TREE OPTIMIZATION")

#    params.startTime = datetime.datetime.now()
#    greedy = CART.Greedy(params)
#    sol = greedy.recursiveConstruction(0,0,"",1,sol,allsolutions)
#    nodeCount, nodeToString = sol.countNodes()
#    sol.printAndExport(pathOutput)

#    nodelist = []
#    for i in range(0,len(sol.tree)):
#        if (sol.tree[i].nodeType==CART.NodeType.NODE_INTERNAL):
#            nodelist.append(i)
#    bestSolution = sol
#    bestMisclassified = sol.calculateMisclassifiedSamples()
#    bestNodes = nodeCount
#    history = {}
    
#    skippedTests = 0
#    while (datetime.datetime.now()-params.startTime).seconds < maxTime:
#        countTests+=1
#        node = nodelist[random.randint(0,len(nodelist)-1)]
#        attrib = random.randint(0,params.nbAttributes-1)

#        key = str(sol.id)+""+str(node)+""+str(attrib)

#        if (key in history):
#            if (debug):
#                print("SOLUCAO TESTADA")
#            skippedTests+=1
#            if (skippedTests > 10):
#                sol = random.choice(list(allsolutions.values()))
#                skippedTests = 0
#                continue
#            continue

#        history[key] = 1

#        solution = sol.partialCopy(countTests,node)

#        greedy = CART.Greedy(params)
#        solution = greedy.recursiveConstruction(node, solution.tree[node].level, attrib, 3, solution, allsolutions)

#        misclassified = solution.calculateMisclassifiedSamples()
#        nodeCount, nodeToString = solution.countNodes()

#        if ((misclassified>3*bestMisclassified) and (bestSolution.id!=sol.id)):
#            if (debug):
#                print("RETORNANDO PARA MELHOR SOLUCAO ENCONTRADA")
#            sol = bestSolution
#        elif (misclassified <= bestMisclassified):
#            best = False
#            if (misclassified==bestMisclassified):
#                if (nodeCount<bestNodes):
#                    bestSolution = solution
#                    bestMisclassified = misclassified
#                    bestNodes = nodeCount
#                    best=True
#            else:
#                best=True
#                bestSolution = solution
#                bestMisclassified = misclassified
#                bestNodes = nodeCount

#            if best:
#                sol = solution
#                if (debug):
#                    print("MELHOR SOLUCAO ENCONTRADA")
#                nodelist = []
#                for i in range(0,len(sol.tree)):
#                    if (sol.tree[i].nodeType==CART.NodeType.NODE_INTERNAL):
#                        nodelist.append(i)

#        elif random.randint(0,sys.maxsize)%20==0:
#            if (debug):
#                print("PERTURBANDO!!!")
#            sol = solution
#            nodelist = []
#            for i in range(0,len(sol.tree)):
#                if (sol.tree[i].nodeType==CART.NodeType.NODE_INTERNAL):
#                    nodelist.append(i)

#        if (debug):
#            print("N", node ," LEVEL ",solution.tree[node].level, "ATTRIBUTE ",attrib," - MISCLASSIFIED: ",solution.calculateMisclassifiedSamples(),"  USING ", nodeCount ," NODES - TIME: " ,solution.getTime())
#    params.endTime = datetime.datetime.now()
#    print("----- BEST SOLUTION")
#    bestSolution.printAndExport(pathOutput)

#    print("----- DECISION TREE OPTIMIZATION COMPLETED IN ", (params.endTime - params.startTime), "(s)")

def execution(instances, seeds, levels, maxExecutionTime, nbBestTries, proportionLookAhead, debug):
    fileTime = str(datetime.datetime.now().year) + str(datetime.datetime.now().month)+str(datetime.datetime.now().day)+str(datetime.datetime.now().hour)+str(datetime.datetime.now().minute)+str(datetime.datetime.now().second)
    greedySolutions = {}
    solutions = {}
    greedyResults= []
    results= []
    with open("Solutions\\SUMMARY_"+fileTime+ "_splits" + str(nbBestTries)  + "_LA" + str(proportionLookAhead*100)+".txt", mode='a') as fp:
        fp.write("SEEDS: "+str(seeds)+" \n")
        fp.write("INSTANCES: "+str(instances)+" \n")
        fp.write("RUNNING TIME: "+str(maxExecutionTime)+" SECONDS\n")
        #fp.write("NUMBER OF SPLITS: "+str(nbBestTries)+" \n")
        fp.write("NUMBER OF BEST TRIES: "+str(nbBestTries)+" \n")
        fp.write("LOOK AHEAD ON: "+str(proportionLookAhead*100)+"% \n")

    for instance in instances:
        file = instance+".txt"
        for seed in seeds:
            print("INSTANCE: "+instance+" SEED:" + str(seed)+" NUMBER OF BEST TRIES: "+str(nbBestTries)+" LOOK AHEAD ON: "+str(proportionLookAhead*100)+"%  - "+ str(datetime.datetime.now()))
            #print("INSTANCE: "+instance+" SEED:" + str(seed)+" NUMBER OF SPLITS: "+str(nbBestTries)+ " " + str(datetime.datetime.now()))
            #greedy, lookAheadSolution = executeNew("Datasets\\" + file,"Solutions\\Final_" + fileTime + "_splits" + str(nbBestTries) + "_"  + file, seed, levels, maxExecutionTime, debug, nbBestTries)
            greedy, lookAheadSolution = execute("Datasets\\" + file,"Solutions\\Final_" + fileTime + "_splits" + str(nbBestTries)  + "_LA" + str(proportionLookAhead*100)+ "_"  + file, seed, levels, maxExecutionTime, debug, proportionLookAhead,nbBestTries)
            greedySolutions[instance]=greedy
            solutions[instance+"_"+str(seed)]=lookAheadSolution
            solutionMisclassified = lookAheadSolution.calculateMisclassifiedSamples()
            solutionNodes, nodesToString = lookAheadSolution.countNodes()
            results.append(solutionMisclassified)
        
            greedyMisclassified = greedy.calculateMisclassifiedSamples()
            greedyNodes, nodesToString = greedy.countNodes()
            greedyResults.append(greedyMisclassified)
            with open("Solutions\\SUMMARY_"+fileTime+ "_splits" + str(nbBestTries) + "_LA" + str(proportionLookAhead*100) +".txt", mode='a') as fp:
                fp.write("INSTANCE: " + instance + "; GREEDY_MISCLASSIFIED: " + str(greedyMisclassified) + "; GREEDY_NODES: " + str(greedyNodes) + "; SOLUTION: " + str(solutionMisclassified) + "; SOLUTION_NODES: " + str(solutionNodes)+ "; SEED: " + str(seed) + " \n")

    with open("Solutions\\SUMMARY_"+fileTime+ "_splits" + str(nbBestTries) + "_LA" + str(proportionLookAhead*100) +".txt", mode='a') as fp:
        fp.write("GREEDY_RESULTS: " + str(greedyResults)+" \n")
        fp.write("RESULTS[BEST"+str(nbBestTries)+"LA"+str(proportionLookAhead*100)+"]:        " + str(results)+" \n")

instances = ['p01', 'p02', 'p03', 'p04', 'p05', 'p06', 'p07', 'p08', 'p09', 'p10', 'p28', 'p39', 'p40', 'p43', 'p50', 'p51', 'p52', 'p53', 'p54'] 
maxTime = 300

seeds = [19, 30, 1945, 1091230814, -100] 

execution(instances,seeds, 5, maxTime , 25, 0, False)
execution(instances,seeds, 5, maxTime , 50, 0, False)
execution(instances,seeds, 5, maxTime , 100, 0, False)
execution(instances,seeds, 5, maxTime , 200, 0, False)

execution(instances,seeds, 5, maxTime , 25, 0.05, False)
execution(instances,seeds, 5, maxTime , 50, 0.05, False)
execution(instances,seeds, 5, maxTime , 100, 0.05, False)
execution(instances,seeds, 5, maxTime , 200, 0.05, False)

execution(instances,seeds, 5, maxTime , 25, 0.2, False)
execution(instances,seeds, 5, maxTime , 50, 0.2, False)
execution(instances,seeds, 5, maxTime , 100, 0.2, False)
execution(instances,seeds, 5, maxTime , 200, 0.2, False)

execution(instances,seeds, 5, maxTime , 35, 0, False)

execution(instances,seeds, 5, maxTime , 25, 0.5, False)
execution(instances,seeds, 5, maxTime , 50, 0.5, False)
execution(instances,seeds, 5, maxTime , 100, 0.5, False)
execution(instances,seeds, 5, maxTime , 200, 0.5, False)
execution(instances,seeds, 5, maxTime , 0, 1, False)

FINAL_RESULTS={}
INSTANCE_SAMPLES = [120,120,120,120,120,120,120,120,120,120,625,625,625,625,625,1372,1372,1372,1372,1372,748,748,748,748,748,569,569,569,569,569,198,198,198,198,198,699,699,699,699,699,1728,1728,1728,1728,1728,3196,3196,3196,3196,3196,150,150,150,150,150,1055,1055,1055,1055,1055,210,210,210,210,210,4601,4601,4601,4601,4601,3772,3772,3772,3772,3772,215,215,215,215,215,958,958,958,958,958,5456,5456,5456,5456,5456,178,178,178,178,178]
GREEDY_RESULTS= [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 181, 181, 181, 181, 181, 24, 24, 24, 24, 24, 151, 151, 151, 151, 151, 9, 9, 9, 9, 9, 28, 28, 28, 28, 28, 21, 21, 21, 21, 21, 282, 282, 282, 282, 282, 189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 163, 163, 163, 163, 163,6, 6, 6, 6, 6, 434, 434, 434, 434, 434, 12, 12, 12, 12, 12,3, 3, 3, 3, 3, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0,0, 0, 0, 0, 0] 
FINAL_RESULTS["BEST50LA0"] =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 150, 8, 8, 8, 8, 10, 138, 141, 141, 141, 140, 8, 9, 9, 8, 9, 19, 24, 23, 22, 22, 15, 18, 18, 18, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST50LA5"] =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 148, 8, 8, 10, 8, 10, 138, 141, 141, 141, 140, 8, 7, 9, 9, 8, 18, 19, 19, 23, 22, 15, 15, 18, 18, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST50LA20"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 10, 9, 11, 8, 10, 140, 141, 140, 140, 141, 9, 8, 8, 7, 8, 23, 21, 22, 22, 24, 15, 18, 18, 18, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST50LA50"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 8, 10, 8, 8, 8, 141, 141, 140, 140, 140, 7, 8, 8, 7, 9, 17, 21, 23, 24, 21, 18, 17, 17, 17, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST200LA0"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 150, 8, 10, 8, 23, 8, 140, 140, 139, 139, 141, 9, 9, 8, 9, 9, 22, 27, 25, 25, 23, 17, 15, 17, 18, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST200LA5"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 148, 8, 10, 8, 23, 8, 140, 140, 139, 139, 142, 9, 9, 8, 9, 9, 24, 27, 25, 23, 23, 17, 15, 17, 18, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST200LA20"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 8, 7, 8, 20, 7, 139, 141, 138, 140, 141, 9, 9, 9, 9, 8, 22, 26, 26, 22, 26, 17, 17, 17, 17, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST200LA50"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 11, 16, 8, 20, 7, 140, 140, 139, 140, 143, 9, 9, 9, 9, 7, 25, 25, 25, 25, 24, 17, 18, 17, 15, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST25LA0"] =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 148, 10, 8, 11, 10, 9, 141, 141, 139, 139, 141, 8, 8, 8, 8, 8, 25, 18, 22, 20, 24, 18, 15, 18, 15, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 139, 154, 138, 150, 154,6, 6, 6, 6, 6, 432, 434, 434, 434, 434, 11, 12, 11, 12, 11,3, 2, 3, 3, 3, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
FINAL_RESULTS["BEST25LA5"] =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 148, 10, 8, 8, 10, 9, 141, 140, 139, 139, 141, 8, 8, 8, 7, 8, 20, 20, 22, 24, 25, 18, 15, 18, 15, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST25LA20"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 8, 8, 8, 8, 8, 140, 140, 140, 141, 141, 8, 9, 7, 7, 8, 23, 21, 22, 25, 23, 18, 18, 18, 15, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST25LA50"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 8, 8, 8, 11, 15, 140, 140, 140, 140, 140, 8, 8, 8, 9, 8, 23, 24, 16, 19, 24, 18, 18, 15, 17, 17, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST100LA0"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 150, 10, 11, 9, 9, 9, 141, 138, 141, 140, 139, 9, 9, 9, 9, 9, 24, 24, 22, 23, 23, 17, 15, 17, 18, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST100LA5"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 148, 10, 8, 8, 9, 10, 141, 138, 141, 140, 139, 9, 8, 9, 9, 8, 24, 25, 25, 22, 20, 17, 15, 17, 18, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST100LA20"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 10, 11, 8, 8, 11, 139, 139, 141, 140, 139, 9, 9, 9, 9, 8, 22, 24, 22, 22, 23, 17, 17, 17, 17, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST100LA50"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 7, 10, 8, 10, 22, 140, 140, 139, 140, 140, 8, 8, 8, 8, 8, 24, 17, 21, 24, 23, 17, 18, 17, 15, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST0LA100"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 10, 8, 8, 10, 8, 141, 141, 141, 141, 141, 8, 7, 8, 9, 8, 25, 25, 25, 23, 25, 15, 18, 17, 18, 18, 258, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
FINAL_RESULTS["BEST30LA10"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148,8, 8, 8, 10, 10, 140, 139, 140, 139, 139, 9, 8, 6, 7, 7,25, 23, 25, 22, 25, 15, 17, 15, 15, 15, 238, 238, 238, 238, 238,189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 139, 140, 136, 147, 139,6, 6, 6, 6, 6, 432, 423, 434, 433, 432, 11, 11, 11, 11, 11,3, 3, 3, 3, 2, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0,0, 0, 0, 0, 0] 

print (len(GREEDY_RESULTS), len(FINAL_RESULTS["BEST25LA0"]), len(FINAL_RESULTS["BEST30LA10"]))

min = sys.maxsize
minIndex = ""
for i,r in FINAL_RESULTS.items():
    base = []
    res  = []

    for j in range(0,len(r)):
        base.append(100*(INSTANCE_SAMPLES[j]-GREEDY_RESULTS[j])/INSTANCE_SAMPLES[j])
        res.append(100*(INSTANCE_SAMPLES[j]-r[j])/INSTANCE_SAMPLES[j])
    temp=wilcoxon(base,res,zero_method="wilcox", correction=True)
    wresult = temp.pvalue
    if (wresult<min):
        min = wresult
        minIndex=i
    print(i,wilcoxon(base,res,zero_method="wilcox", correction=True))

print(minIndex,min)