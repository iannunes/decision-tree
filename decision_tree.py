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
    lastValueIgnored = False
    if (count % 3 == 0):
        printString = "SOLUCAO ALEATÓRIA"
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
        printString = "MELHOR SOLUCAO   "

        for i in range(0,len(solutions)):
            misclassified = solutions[i].calculateMisclassifiedSamples()
            if (misclassified <= minMismatch):
                if ((lastvalue>=0)and (lastvalue==misclassified)):
                    lastValueIgnored = True
                    continue
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
    
    print(printString + " - TROCANDO SOLUCAO - ", minMismatch, " - ", minNodes," NÓS - SOLS POSSIVEIS ", len(solutions), " - ULTIMO IGNORADO", lastValueIgnored)
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
        nbSearchChildren = 4
    elif params.nbAttributes<10:
        nbSearchChildren = 5

    #for i in range(0,int(params.nbAttributes)):
    #    countTests += 1
    #    solution = CART.Solution(params,countTests)
    #    greedy = CART.Greedy(params)
    #    att = i

    #    solution = greedy.recursiveConstruction(0,0,att,nbSearchChildren,solution,allsolutions)
    #    tabu["0_"+str(att)] = countTests

    #    nodeCount, nodeToString = solution.countNodes()
    #    allsolutions[nodeToString] = solution
    #    if (debug):
    #        print("ROOT WITH ATTRIBUTE ", att," MISCLASSIFIED: ", solution.calculateMisclassifiedSamples()," USING ", nodeCount ," NODES - TIME: " ,solution.getTime())

    for i,s in allsolutions.items():
        solutions.append(s)

    countSkippedTests = 0
    countSkippedAtrributes = 0
    sol = None
    lastValue = -1
    countTests=0
    print("SOLUCOES INICIAIS: ", len(allsolutions))
    while (datetime.datetime.now()-params.startTime).seconds<maxTime:
        if (len(solutions)==0):
            print("GERANDO NOVA SOLUCAO INCIAL")
            sol = CART.Solution(params, countTests)
            greedy = CART.Greedy(params)
            sol = greedy.recursiveConstruction(0,0,random.randint(0,params.nbAttributes-1),3,sol,allsolutions)
            for i,s in allsolutions.items():
                solutions.append(s)
            #if (debug):
            #    print("GERANDO NOVA SOLUCAO INCIAL")

        if (sol == None):
            tabu = {}
            countSkippedTests=0

            solutions = eliminateWorstCandidateSolutions(solutions, 1.5)
            if (len(solutions)==0):
                if (debug):
                    print("SEM MAIS SOLUCOES A EXPLORAR")
                break

            sol, nodelist, splitAtributelist = getNextSolution(solutions, countTests, lastValue)

            if len(nodelist)==0:
                sol = None
                continue

            if (sol!=None):
                lastValue = sol.calculateMisclassifiedSamples()

        for i in range(0, len(nodelist)):
            if (datetime.datetime.now()-params.startTime).seconds>maxTime:
                print("TEMPO LIMITE ALCANCADO")
                break
            #if (countSkippedTests > 10):
            #    if (len(solutions)==0):
            #        break
            #    sol=None
            #    break
            for attrib in range(0,params.nbAttributes):
                countTests += 1

                if (sol==None):
                    break
                if (countTests %50 == 0):
                    solutions=[]
                    sol=None
                    break

                

                node = nodelist[i]
                solution = sol.partialCopy(random.randint(300000000,900000000),node)

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
                            #solutions.append(stemp)
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

def executeRandom(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug):
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
    sol = greedy.recursiveConstructionrandom(0,0,"",5,sol,allsolutions)
    nodeCount, nodeToString = sol.countNodes()

    sol.printAndExport(pathOutput)

    for i,s in allsolutions.items():
        solutions.append(s)

    countSkippedTests = 0
    countSkippedAtrributes = 0
    sol = None
    lastValue = -1
    countTests=0
    print("SOLUCOES INICIAIS: ", len(allsolutions))
    while (datetime.datetime.now()-params.startTime).seconds<maxTime:
        if (len(solutions)==0):
            print("GERANDO NOVA SOLUCAO INCIAL")
            sol = CART.Solution(params, countTests)
            greedy = CART.Greedy(params)
            sol = greedy.recursiveConstructionrandom(0,0,random.randint(0,params.nbAttributes-1),5,sol,allsolutions)
            for i,s in allsolutions.items():
                solutions.append(s)

        if (countSkippedTests>100):
            sol=None
            countSkippedTests=0
            print("TROCANDO SOLUCAO POR EXCESSO DE SOLUCOES REPETIDAS")

        if (sol == None):
            tabu = {}
            countSkippedTests=0

            solutions = eliminateWorstCandidateSolutions(solutions, 1.5)
            if (len(solutions)==0):
                if (debug):
                    print("SEM MAIS SOLUCOES A EXPLORAR")
                break

            sol, nodelist, splitAtributelist = getNextSolution(solutions, countTests, lastValue)

            if len(nodelist)==0:
                sol = None
                continue

            if (sol!=None):
                lastValue = sol.calculateMisclassifiedSamples()
            else:
                continue

        i = random.randint(0,len(nodelist)-1)

        attrib =  random.randint(0,params.nbAttributes-1)
        countTests += 1

        if (sol==None):
            continue

        if (countTests %500 == 0):
            solutions=[]
            sol=None
            continue

        node = nodelist[i]
        solution = sol.partialCopy(random.randint(300000000,900000000),node)

        countSkippedAtrributes = 0
        greedy = CART.Greedy(params)
        allsolutionstemp = {}
        solution = greedy.recursiveConstructionrandom(node, sol.tree[node].level, attrib, 5, solution, allsolutionstemp)

        nodeCount, nodeToString = solution.countNodes()

        if (nodeToString in allsolutions):
            
            countSkippedTests+=1
            
            continue

        if (nodeToString in allsolutions):
            for itemp,stemp in allsolutionstemp.items():
                if (itemp not in allsolutions):
                    allsolutions[itemp] = stemp
                    solutions.append(stemp)
            countSkippedTests+=1
            if (debug):
                print("----------------SOLUCAO JA TESTADA----------------")
            continue

        for itemp,stemp in allsolutionstemp.items():
            if (itemp not in allsolutions):
                allsolutions[itemp] = stemp

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

def executeLookAhead(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug):
    random.seed(seedRNG)
    countTests = 0
    allsolutions = {}
    # definir solucao inicial
    if debug:
        print("----- STARTING DECISION TREE OPTIMIZATION")
    params = CART.Params(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug)
    solution = CART.Solution(params, countTests)
    if debug:
        print("----- STARTING DECISION TREE OPTIMIZATION")
    greedy = CART.Greedy(params)
    solution = greedy.recursiveConstruction(0,0,"",1,solution,allsolutions)
    greedySolution = solution
    if debug:
        solution.printAndExport(pathOutput)
    params.startTime = datetime.datetime.now()

    # executar a LS na solucao inicial
    if debug:
        print("----- STARTING LS ON FIRST SOLUTION")
    countTests = 1
    solution = CART.Solution(params,countTests)
    solution = greedy.recursiveConstruction(0,0,"",3,solution,allsolutions)
    nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
    # com a melhor solução iniciar ITL até completar o maxTime
    bestSolution = solution
    bestMisclassified = solution.calculateMisclassifiedSamples()
    bestNodes,bestNodesToString = solution.countNodes()
    if debug:
        print("----- STARTING ILS")
    lapTimes = []
    while True:
        initialTime = datetime.datetime.now()
        countTests += 1
        # - perturbar
        node = nodelist[random.randint(0,len(nodelist)-1)]
        attrib = random.randint(0,params.nbAttributes-1)
        solLS = solution.partialCopy(countTests,node)
        # - executar LS
        nbSearchChildren = 3
        if (len(nodelist)<10):
            nbSearchChildren = 5
        if (params.nbAttributes<10):
            nbSearchChildren = 5
        if (solLS.tree[node].level>0):
            nbSearchChildren = 5
        elif (solLS.tree[node].level>1):
            nbSearchChildren = 5

        solLS = greedy.recursiveConstruction(node, solLS.tree[node].level, attrib, nbSearchChildren, solLS, allsolutions)
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

    timeSum = 0
    for time in lapTimes:
        timeSum+=time
    if debug:
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
    if debug:
        bestSolution.printAndExport(pathOutput)

    return greedySolution , bestSolution

def execute50bestLocalSearch(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug):
    random.seed(seedRNG)
    countTests = 0
    allsolutions = {}
    # definir solucao inicial
    if debug:
        print("----- STARTING DECISION TREE OPTIMIZATION")
    params = CART.Params(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug)
    solution = CART.Solution(params, countTests)
    if debug:
        print("----- STARTING DECISION TREE OPTIMIZATION")
    greedy = CART.Greedy(params)
    solution = greedy.recursiveConstruction(0,0,"",1,solution,allsolutions)
    greedySolution = solution
    if debug:
        solution.printAndExport(pathOutput)
    params.startTime = datetime.datetime.now()

    # executar a LS na solucao inicial
    if debug:
        print("----- STARTING LS ON FIRST SOLUTION")
    countTests = 1
    solution = CART.Solution(params,countTests)
    solution = greedy.recursiveConstructionBestNatNode(0,0,"",50,solution,allsolutions)
    nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
    # com a melhor solução iniciar ITL até completar o maxTime
    bestSolution = solution
    bestMisclassified = solution.calculateMisclassifiedSamples()
    bestNodes,bestNodesToString = solution.countNodes()
    if debug:
        print("----- STARTING ILS")
    lapTimes = []
    while True:
        initialTime = datetime.datetime.now()
        countTests += 1
        # - perturbar
        node = nodelist[random.randint(0,len(nodelist)-1)]
        attrib = random.randint(0,params.nbAttributes-1)
        solLS = solution.partialCopy(countTests,node)
        # - executar LS
        solLS = greedy.recursiveConstructionBestNatNode(node, solLS.tree[node].level, attrib, 50, solLS, allsolutions)
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

    timeSum = 0
    for time in lapTimes:
        timeSum+=time
    if debug:
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
    if debug:
        bestSolution.printAndExport(pathOutput)

    return greedySolution , bestSolution

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

        solution = sol.partialCopy(countTests,node)

        greedy = CART.Greedy(params)
        solution = greedy.recursiveConstruction(node, solution.tree[node].level, attrib, 3, solution, allsolutions)

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
maxExecutionTime=300
debug=False

instances = ["p01","p02","p03","p04","p05","p06","p07","p08","p09","p10"]
seeds = [19,30,1945,1091230814,-100]
greedySolutions = {}
lookAheadSolutions = {}
greedyResults= []
lookAheadResults= []
best50LocalSearchResults=[]
best50LocalSearchSolutions={}

for instance in instances:
    file = instance+".txt"
    for seed in seeds:
        greedy, lookAheadSolution = executeLookAhead("Datasets\\"+file,"Solutions\\LookAhead_"+fileTime+"_seed"+str(seed)+"_"+file,seed,levels,maxExecutionTime,debug)
        greedySolutions[instance]=greedy
        lookAheadSolutions[instance+"_"+str(seed)]=lookAheadSolution
        lookAheadSolutionMisclassified = lookAheadSolution.calculateMisclassifiedSamples()
        lookAheadSolutionNodes, nodesToString = lookAheadSolution.countNodes()
        lookAheadResults.append(lookAheadSolutionMisclassified)

        greedy, best50LocalSearchSolution = execute50bestLocalSearch("Datasets\\"+file,"Solutions\\Best50_"+fileTime+"_seed"+str(seed)+"_"+file,seed,levels,maxExecutionTime,debug)
        greedySolutions[instance]=greedy
        best50LocalSearchSolutions[instance+"_"+str(seed)]=best50LocalSearchSolution
        best50LocalSearchSolutionMisclassified = best50LocalSearchSolution.calculateMisclassifiedSamples()
        best50LocalSearchSolutionNodes, nodesToString = best50LocalSearchSolution.countNodes()
        best50LocalSearchResults.append(best50LocalSearchSolutionMisclassified)

        greedyMisclassified = greedy.calculateMisclassifiedSamples()
        greedyNodes, nodesToString = greedy.countNodes()
        greedyResults.append(greedyMisclassified)
        with open("Solutions\\Final_"+fileTime+"_SUMARY.txt", mode='a') as fp:
            fp.write("INSTANCE: " + instance + "; GREEDY_MISCLASSIFIED: " + str(greedyMisclassified) + "; GREEDY_NODES: " + str(greedyNodes) + "; LOOKAHEAD_SOLUTION: " + str(lookAheadSolutionMisclassified) + "; LOOKAHEAD_SOLUTION_NODES: " + str(lookAheadSolutionNodes)+ "; SEED: " + str(seed) + " \n")
            fp.write("INSTANCE: " + instance + "; GREEDY_MISCLASSIFIED: " + str(greedyMisclassified) + "; GREEDY_NODES: " + str(greedyNodes) + "; BEST50_SOLUTION:    " + str(best50LocalSearchSolutionMisclassified) + "; BEST50_SOLUTION_NODES:    " + str(best50LocalSearchSolutionNodes) + "; SEED: " + str(seed) + " \n")

with open("Solutions\\Final_"+fileTime+"_SUMARY.txt", mode='a') as fp:
    fp.write("GREEDYRESULTS:   " + str(greedyResults)+" \n")
    fp.write("LOOKAHEADRESULTS:" + str(lookAheadResults)+" \n")
    fp.write("BEST50RESULTS:   " + str(best50LocalSearchResults)+" \n")

#file = "p02.txt"
#executeFinal("Datasets\\"+file,"Solutions\\Final_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p03.txt"
#executeFinal("Datasets\\"+file,"Solutions\\Final_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p04.txt"
#executeFinal("Datasets\\"+file,"Solutions\\Final_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p05.txt"
#executeFinal("Datasets\\"+file,"Solutions\\Final_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p06.txt"
#executeFinal("Datasets\\"+file,"Solutions\\Final_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p07.txt"
#executeFinal("Datasets\\"+file,"Solutions\\Final_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p08.txt"
#executeFinal("Datasets\\"+file,"Solutions\\Final_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p09.txt"
#executeFinal("Datasets\\"+file,"Solutions\\Final_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p10.txt"
#executeFinal("Datasets\\"+file,"Solutions\\Final_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)

#file = "p01.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p02.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p03.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p04.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p05.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p06.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p07.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p08.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p09.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p10.txt"
#executeILS("Datasets\\"+file,"Solutions\\ILS_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)

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

#file = "p03.txt"
#executeRandom("Datasets\\"+file,"Solutions\\random_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p04.txt"
#executeRandom("Datasets\\"+file,"Solutions\\random_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p05.txt"
#executeRandom("Datasets\\"+file,"Solutions\\random_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p06.txt"
#executeRandom("Datasets\\"+file,"Solutions\\random_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p07.txt"
#executeRandom("Datasets\\"+file,"Solutions\\random_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p08.txt"
#executeRandom("Datasets\\"+file,"Solutions\\random_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p09.txt"
#executeRandom("Datasets\\"+file,"Solutions\\random_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)
#file = "p10.txt"
#executeRandom("Datasets\\"+file,"Solutions\\random_"+fileTime+"_"+file,30,levels,maxExecutionTime,debug)


