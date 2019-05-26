import CART
import math
import numpy as np
import datetime
import random
import sys
from scipy.stats import ttest_1samp, wilcoxon, ttest_ind, mannwhitneyu

def execute(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug, lookaheadProportion, nbBestTries):
    random.seed(seedRNG)
    countTests = 0
    allsolutions = {}
    # define solucao inicial
    params = CART.Params(pathData, pathOutput, seedRNG, maxDepth, maxTime, lookaheadProportion, nbBestTries, debug)
    solution = CART.Solution(params, countTests)
    greedy = CART.Greedy(params)
    solution = greedy.recursiveConstruction(0,0,"",1, solution, allsolutions, nbBestTries)
    greedySolution = solution
    solution.printAndExport(pathOutput)
    params.startTime = datetime.datetime.now()
    # end define solucao inicial

    # executa a LS bestInformationGains na solucao inicial
    countTests = 1
    solution = CART.Solution(params,countTests)
    solution = greedy.recursiveConstructionBestNatNode(0,0,"",nbBestTries,solution,allsolutions)
    nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
    
    bestSolution = solution
    bestMisclassified = solution.calculateMisclassifiedSamples()
    bestNodes,bestNodesToString = solution.countNodes()
    # end executa a LS bestInformationGains na solucao inicial

    lapTimes = []
    numberMod = 0
    if (lookaheadProportion>0):
        numberMod = int(math.ceil(1/lookaheadProportion))

    # com a melhor solução iniciar ILS até completar o maxTime
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
        elif (countTests%numberMod != 0):
            executeLookAhead = False

        if (executeLookAhead):
            # parametrizo a quantidade de solucoes devem ser avaliadas pelo Look Ahead de acordo com o nivel da arvore
            nbSearchChildren = 3
            if (solLS.tree[node].level==1):
                nbSearchChildren = 5
            elif (solLS.tree[node].level>1):
                nbSearchChildren = 7
            # essa chamada a funcao faz simultaneamente a perturbação e na sequecia executa a busca local look ahead avaliando a 
            # quantidade de nos nbSearchChildren para todos os nós filhos nó passado como referencia
            solLS = greedy.recursiveConstruction(node, solLS.tree[node].level, attrib, nbSearchChildren, solLS, allsolutions, nbBestTries)
        else:
            # essa chamada a funcao faz simultaneamente a perturbação e na sequecia executa a busca local olhando para os melhors nbBestTries
            # splits apenas no nó passado como referencia. 
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
            
        if (misclassified <= bestMisclassified*1.1):
            solution = solLS
            nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
        else: #if (solution.id != bestSolution.id):
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

def execute2(pathData,pathOutput,seedRNG, maxDepth, maxTime, debug, lookaheadProportion, nbBestTries):
    random.seed(seedRNG)
    countTests = 0
    allsolutions = {}
    # define solucao inicial
    params = CART.Params(pathData, pathOutput, seedRNG, maxDepth, maxTime, lookaheadProportion, nbBestTries, debug)
    solution = CART.Solution(params, countTests)
    greedy = CART.Greedy(params)
    solution = greedy.recursiveConstruction(0,0,"",1, solution, allsolutions, nbBestTries)
    greedySolution = solution
    solution.printAndExport(pathOutput)
    params.startTime = datetime.datetime.now()
    # end define solucao inicial

    # executa a LS bestInformationGains na solucao inicial
    countTests = 1
    #solution = CART.Solution(params,countTests)
    #solution = greedy.recursiveConstructionBestNatNode(0,0,"",nbBestTries,solution,allsolutions)
    #nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)

    bestSolution = solution
    bestMisclassified = solution.calculateMisclassifiedSamples()
    bestNodes, nodestostring = solution.countNodes()

    for i in range(0, params.nbAttributes):
        solution = CART.Solution(params, countTests)
        greedy = CART.Greedy(params)
        solution = greedy.recursiveConstruction(0,0,i,1, solution, allsolutions, nbBestTries)
    
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

    print("BEST INITIAL SOLUTION: "+str(bestMisclassified))
    nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
    solution = bestSolution
    # end executa a LS bestInformationGains na solucao inicial

    lapTimes = []
    numberMod = 0
    if (lookaheadProportion>0):
        numberMod = int(math.ceil(1/lookaheadProportion))

    # com a melhor solução iniciar ILS até completar o maxTime
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
        elif (countTests%numberMod != 0):
            executeLookAhead = False

        if (executeLookAhead):
            # parametrizo a quantidade de solucoes devem ser avaliadas pelo Look Ahead de acordo com o nivel da arvore
            nbSearchChildren = 3
            if (solLS.tree[node].level==1):
                nbSearchChildren = 4
            elif (solLS.tree[node].level==2):
                nbSearchChildren = 8
            elif (solLS.tree[node].level==3):
                nbSearchChildren = 15
            # essa chamada a funcao faz simultaneamente a perturbação e na sequecia executa a busca local look ahead avaliando a 
            # quantidade de nos nbSearchChildren para todos os nós filhos nó passado como referencia
            solLS = greedy.recursiveConstruction(node, solLS.tree[node].level, attrib, nbSearchChildren, solLS, allsolutions, nbBestTries)
        else:
            # essa chamada a funcao faz simultaneamente a perturbação e na sequecia executa a busca local olhando para os melhors nbBestTries
            # splits apenas no nó passado como referencia. 
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
            
        if (misclassified <= bestMisclassified*1.1):
            solution = solLS
            nodelist = solution.getNodeList(False,CART.NodeType.NODE_INTERNAL)
        else: #if (solution.id != bestSolution.id):
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

    print("TESTES: "+str(countTests)+" solucoes diferentes: "+str(len(allsolutions)))

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
        fp.write("NUMBER OF BEST TRIES: "+str(nbBestTries)+" \n")
        fp.write("LOOK AHEAD ON: "+str(proportionLookAhead*100)+"% \n")

    for instance in instances:
        file = instance+".txt"
        for seed in seeds:
            print("INSTANCE: "+instance+" SEED:" + str(seed)+" NUMBER OF BEST TRIES: "+str(nbBestTries)+" LOOK AHEAD ON: "+str(proportionLookAhead*100)+"%  - "+ str(datetime.datetime.now()))
            greedy, lookAheadSolution = execute2("Datasets\\" + file,"Solutions\\Final_" + fileTime + "_splits" + str(nbBestTries)  + "_LA" + str(proportionLookAhead*100)+ "_"  + file, seed, levels, maxExecutionTime, debug, proportionLookAhead,nbBestTries)
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
#instances = ['p03', 'p04', 'p05', 'p06', 'p07']
#instances = ['p08', 'p09', 'p10', 'p28', 'p39']
#instances = ['p40', 'p43', 'p50', 'p51', 'p52']
maxTime = 300

seeds = [19, 30, 1945, 1091230814, -100] 
seeds = [57, 25, 1990, 0, -56446] 

#execution(instances,seeds, 5, maxTime , 15, 100, True)
#execution(instances,seeds, 5, maxTime , 30, 0.05, True)
#execution(instances,seeds, 5, maxTime , 30, 0.2, True)

#execution(instances,seeds, 5, maxTime , 40, 0.1, False)

#execution(instances,seeds, 5, maxTime , 25, 0, False)
#execution(instances,seeds, 5, maxTime , 50, 0, False)
#execution(instances,seeds, 5, maxTime , 100, 0, False)
#execution(instances,seeds, 5, maxTime , 200, 0, False)

#execution(instances,seeds, 5, maxTime , 25, 0.05, False)
#execution(instances,seeds, 5, maxTime , 50, 0.05, False)
#execution(instances,seeds, 5, maxTime , 100, 0.05, False)
#execution(instances,seeds, 5, maxTime , 200, 0.05, False)

#execution(instances,seeds, 5, maxTime , 25, 0.2, False)
#execution(instances,seeds, 5, maxTime , 50, 0.2, False)
#execution(instances,seeds, 5, maxTime , 100, 0.2, False)
#execution(instances,seeds, 5, maxTime , 200, 0.2, False)

#execution(instances,seeds, 5, maxTime , 30, 10, False)
#execution(instances,seeds, 5, maxTime , 35, 0, False)

#execution(instances,seeds, 5, maxTime , 25, 0.5, False)
#execution(instances,seeds, 5, maxTime , 50, 0.5, False)

#execution(instances,seeds, 5, maxTime , 100, 0.5, False) #BEST ONE!

#execution(instances,seeds, 5, maxTime , 200, 0.5, False)
#execution(instances,seeds, 5, maxTime , 0, 1, False)

FINAL_RESULTS={}
INSTANCE_SAMPLES = [120,120,120,120,120,120,120,120,120,120,625,625,625,625,625,1372,1372,1372,1372,1372,748,748,748,748,748,569,569,569,569,569,198,198,198,198,198,699,699,699,699,699,1728,1728,1728,1728,1728,3196,3196,3196,3196,3196,150,150,150,150,150,1055,1055,1055,1055,1055,210,210,210,210,210,4601,4601,4601,4601,4601,3772,3772,3772,3772,3772,215,215,215,215,215,958,958,958,958,958,5456,5456,5456,5456,5456,178,178,178,178,178]
GREEDY_RESULTS= [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 181, 181, 181, 181, 181, 24, 24, 24, 24, 24, 151, 151, 151, 151, 151, 9, 9, 9, 9, 9, 28, 28, 28, 28, 28, 21, 21, 21, 21, 21, 282, 282, 282, 282, 282, 189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 163, 163, 163, 163, 163,6, 6, 6, 6, 6, 434, 434, 434, 434, 434, 12, 12, 12, 12, 12,3, 3, 3, 3, 3, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0,0, 0, 0, 0, 0] 
#FINAL_RESULTS["BEST50LA0"] =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 150, 8, 8, 8, 8, 10, 138, 141, 141, 141, 140, 8, 9, 9, 8, 9, 19, 24, 23, 22, 22, 15, 18, 18, 18, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST50LA5"] =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 148, 8, 8, 10, 8, 10, 138, 141, 141, 141, 140, 8, 7, 9, 9, 8, 18, 19, 19, 23, 22, 15, 15, 18, 18, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST50LA20"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 10, 9, 11, 8, 10, 140, 141, 140, 140, 141, 9, 8, 8, 7, 8, 23, 21, 22, 22, 24, 15, 18, 18, 18, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST50LA50"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 8, 10, 8, 8, 8, 141, 141, 140, 140, 140, 7, 8, 8, 7, 9, 17, 21, 23, 24, 21, 18, 17, 17, 17, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST200LA0"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 150, 8, 10, 8, 23, 8, 140, 140, 139, 139, 141, 9, 9, 8, 9, 9, 22, 27, 25, 25, 23, 17, 15, 17, 18, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST200LA5"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 148, 8, 10, 8, 23, 8, 140, 140, 139, 139, 142, 9, 9, 8, 9, 9, 24, 27, 25, 23, 23, 17, 15, 17, 18, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST200LA20"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 8, 7, 8, 20, 7, 139, 141, 138, 140, 141, 9, 9, 9, 9, 8, 22, 26, 26, 22, 26, 17, 17, 17, 17, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST200LA50"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 11, 16, 8, 20, 7, 140, 140, 139, 140, 143, 9, 9, 9, 9, 7, 25, 25, 25, 25, 24, 17, 18, 17, 15, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST25LA0"] =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 148, 10, 8, 11, 10, 9, 141, 141, 139, 139, 141, 8, 8, 8, 8, 8, 25, 18, 22, 20, 24, 18, 15, 18, 15, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 139, 154, 138, 150, 154,6, 6, 6, 6, 6, 432, 434, 434, 434, 434, 11, 12, 11, 12, 11,3, 2, 3, 3, 3, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
#FINAL_RESULTS["BEST25LA5"] =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 148, 10, 8, 8, 10, 9, 141, 140, 139, 139, 141, 8, 8, 8, 7, 8, 20, 20, 22, 24, 25, 18, 15, 18, 15, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST25LA20"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 8, 8, 8, 8, 8, 140, 140, 140, 141, 141, 8, 9, 7, 7, 8, 23, 21, 22, 25, 23, 18, 18, 18, 15, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST25LA50"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 8, 8, 8, 11, 15, 140, 140, 140, 140, 140, 8, 8, 8, 9, 8, 23, 24, 16, 19, 24, 18, 18, 15, 17, 17, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST100LA0"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 150, 10, 11, 9, 9, 9, 141, 138, 141, 140, 139, 9, 9, 9, 9, 9, 24, 24, 22, 23, 23, 17, 15, 17, 18, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST100LA5"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 148, 10, 8, 8, 9, 10, 141, 138, 141, 140, 139, 9, 8, 9, 9, 8, 24, 25, 25, 22, 20, 17, 15, 17, 18, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST100LA20"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 10, 11, 8, 8, 11, 139, 139, 141, 140, 139, 9, 9, 9, 9, 8, 22, 24, 22, 22, 23, 17, 17, 17, 17, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST100LA50"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 7, 10, 8, 10, 22, 140, 140, 139, 140, 140, 8, 8, 8, 8, 8, 24, 17, 21, 24, 23, 17, 18, 17, 15, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 134, 158, 157, 134, 153, 6, 6, 6, 6, 6, 434, 434, 434, 434, 434, 12, 12, 12, 12, 12, 2, 3, 2, 3, 3, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
#FINAL_RESULTS["BEST0LA100"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 10, 8, 8, 10, 8, 141, 141, 141, 141, 141, 8, 7, 8, 9, 8, 25, 25, 25, 23, 25, 15, 18, 17, 18, 18, 258, 238, 238, 238, 238, 189, 189, 189, 189, 189] 
#FINAL_RESULTS["BEST30LA10"] =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148,8, 8, 8, 10, 10, 140, 139, 140, 139, 139, 9, 8, 6, 7, 7,25, 23, 25, 22, 25, 15, 17, 15, 15, 15, 238, 238, 238, 238, 238,189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 139, 140, 136, 147, 139,6, 6, 6, 6, 6, 432, 423, 434, 433, 432, 11, 11, 11, 11, 11,3, 3, 3, 3, 2, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0,0, 0, 0, 0, 0] 
#FINAL_RESULTS["BEST35LA0"]  =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 148, 148, 148, 148, 8, 10, 10, 8, 8, 139, 139, 139, 138, 142, 8, 9, 8, 9, 9, 24, 23, 25, 21, 25, 18, 17, 18, 15, 18, 238, 238, 238, 238, 238,189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 138, 148, 150, 152, 145, 6, 6, 6, 6, 6, 427, 434, 434, 434, 434, 11, 11, 12, 11, 11, 2, 2, 3, 3, 3, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
FINAL_RESULTS["BEST15LA0"]=     [0,0,0,0,0,0,0,0,0,0,150, 150, 150, 150, 150, 8, 8, 8, 8, 8, 146, 146, 146, 146, 146, 4, 4, 4, 4, 4, 15, 15, 15, 15, 15, 15, 18, 15, 15, 15, 238, 238, 238, 238, 238, 187, 189, 189, 189, 189, 1, 1, 1, 1, 1, 125, 124, 123, 126, 125, 2, 2, 2, 2, 2, 432, 432, 432, 432, 432, 11, 11, 11, 11, 11, 0, 0, 0, 0, 0, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
FINAL_RESULTS["BEST15LA10000"]= [0,0,0,0,0,0,0,0,0,0,148, 148, 148, 148, 148, 8, 8, 8, 8, 8, 142, 142, 142, 142, 142, 4, 4, 4, 4, 6, 15, 15, 15, 15, 15, 18, 15, 15, 18, 18, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 125, 122, 125, 125, 123, 2, 2, 2, 2, 2, 432, 432, 432, 432, 432, 11, 11, 11, 11, 11, 0, 0, 0, 0, 0, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
FINAL_RESULTS["BEST30LA20"] =   [0,0,0,0,0,0,0,0,0,0,148, 148, 148, 148, 148, 8, 8, 8, 8, 8, 142, 142, 142, 142, 143, 4, 4, 4, 4, 4, 15, 15, 16, 15, 15, 17, 15, 15, 15, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 124, 124, 125, 125, 126, 2, 2, 2, 1, 2, 432, 432, 432, 432, 432, 11, 11, 11, 11, 11, 0, 0, 0, 0, 0, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
FINAL_RESULTS["BEST30LA0"]=     [0,0,0,0,0,0,0,0,0,0,150, 150, 148, 148, 150, 8, 8, 8, 8, 8, 144, 144, 144, 144, 142, 4, 4, 4, 4, 4, 14, 16, 15, 16, 14, 14, 13, 13, 13, 12, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 130, 130, 129, 130, 130, 1, 1, 1, 1, 1, 424, 424, 424, 424, 424, 11, 11, 11, 11, 11, 0, 0, 0, 0, 0, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
FINAL_RESULTS["BEST30LA5"]=     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 8, 8, 8, 8, 8, 144, 144, 144, 144, 144, 4, 4, 4, 4, 4, 15, 15, 15, 15, 15, 16, 15, 16, 15, 16, 238, 238, 238, 238, 238, 189, 189, 187, 189, 189, 1, 1, 1, 1, 1, 129, 129, 130, 130, 130, 2, 2, 2, 2, 2, 427, 427, 432, 432, 427, 11, 11, 11, 11, 11, 0, 0, 0, 0, 0, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
FINAL_RESULTS["2BEST30LA5"]=    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 148, 148, 148, 148, 148, 8, 8, 8, 8, 8, 144, 144, 144, 144, 144, 4, 4, 4, 4, 4, 15, 15, 15, 16, 15, 15, 15, 15, 16, 15, 238, 238, 238, 238, 238, 189, 189, 189, 189, 189, 1, 1, 1, 1, 1, 130, 129, 129, 130, 131, 2, 2, 2, 2, 2, 421, 432, 432, 432, 427, 11, 11, 11, 11, 11, 0, 0, 0, 0, 0, 150, 150, 150, 150, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
min = sys.maxsize
minIndex = ""
minIndex2=""
for i,r in FINAL_RESULTS.items():
    base = []
    #for i2,r2 in FINAL_RESULTS.items():
    res  = []
    #if (i==i2):
    #    continue
    for j in range(0,len(r)):
        base.append(100*(INSTANCE_SAMPLES[j]-GREEDY_RESULTS[j])/INSTANCE_SAMPLES[j])
        res.append(100*(INSTANCE_SAMPLES[j]-r[j])/INSTANCE_SAMPLES[j])
    temp=wilcoxon(base,res,zero_method="wilcox", correction=True)
    wresult = temp.pvalue
    if (wresult<min):
        min = wresult
        minIndex=i
        #minIndex2=i2
    print(i,wilcoxon(base,res,zero_method="wilcox", correction=True))

print(minIndex,min)