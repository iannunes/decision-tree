import math
import datetime
import random as rd
from enum import Enum

class NodeType(Enum):
    NODE_NULL = 1
    NODE_LEAF = 2
    NODE_INTERNAL = 3

class AttributeType(Enum):
    TYPE_NUMERICAL = 1 
    TYPE_CATEGORICAL = 2

class Solution:
    def printAndExport(self, fileName):

        if fileName == "":
            raise TypeError("ERROR: fileName is empty.")

        nbMisclassifiedSamples = 0
        #print("---------------------------------------- PRINTING SOLUTION ----------------------------------------")
        serializedTree = ""
        for d in range(0, self.params.maxDepth+1):
            begin = 2**d - 1
            end = 2**(d+1) - 1
            for i in range(begin,end):

                if (self.tree[i].nodeType == NodeType.NODE_INTERNAL):
                    sinal = "="
                    if (self.params.attributeTypes[self.tree[i].splitAttribute] == AttributeType.TYPE_NUMERICAL):
                        sinal = "<="
                    serializedTree = serializedTree + "(N"+ str(i) + ",A["+ str(self.tree[i].splitAttribute) + "]"+ sinal + str(self.tree[i].splitValue)+ ")"
                else:
                    if (self.tree[i].nodeType == NodeType.NODE_LEAF):
                        misclass = self.tree[i].nbSamplesNode - self.tree[i].nbSamplesClass[self.tree[i].majorityClass]
                        nbMisclassifiedSamples += misclass
                        serializedTree = serializedTree + "(L" + str(i) + ",C" + str(self.tree[i].majorityClass) + "," + str(self.tree[i].nbSamplesClass[self.tree[i].majorityClass]) + "," + str(misclass) + ") "
            serializedTree = serializedTree + "\n"
        #print (serializedTree)
        #print(nbMisclassifiedSamples , "/" , self.params.nbSamples , " MISCLASSIFIED SAMPLES" )
        #print("---------------------------------------------------------------------------------------------------" )
        
        nodes, nodestostring = self.countNodes()

        #print("NB_SAMPLES: " ,  self.params.nbSamples )
        #print("NODES: ", nodes, " - ", nodestostring)
        #print("NB_MISCLASSIFIED: " , nbMisclassifiedSamples)
        
        # Dump result

        with open(fileName, mode='a') as fp:
            fp.write("NB_SAMPLES: " + str(self.params.nbSamples) + "\n")
            fp.write("NODES: "+ str(nodes)+" \n")
            fp.write("NB_MISCLASSIFIED: " + str(nbMisclassifiedSamples) + "\n")
            fp.write("MAX_TIME: " + str(self.params.maxTime) + "\n")
            fp.write("SEED: " + str(self.params.seed) + "\n")
            fp.write("LOOKAHEADPROPORTION: " + str(self.params.lookAheadProportion*100) + "\n")
            fp.write("NUMBER_BEST_TRIES: " + str(self.params.nbBestTries) + "\n")
            fp.write(serializedTree+" \n")

    def calculateMisclassifiedSamples(self):
        nodelist = nodelist = self.getNodeList(False,NodeType.NODE_LEAF)
        nbMisclassifiedSamples = 0

        for i in nodelist:
            misclass = self.tree[i].nbSamplesNode - self.tree[i].nbSamplesClass[self.tree[i].majorityClass]
            nbMisclassifiedSamples += misclass
        #for d in range(0, self.params.maxDepth+1):
        #    inicio = 2**d - 1
        #    fim = 2**(d+1) - 1
        #    for i in range(inicio,fim):
        #        if (self.tree[i].nodeType == NodeType.NODE_LEAF):
        #            misclass = self.tree[i].nbSamplesNode - self.tree[i].nbSamplesClass[self.tree[i].majorityClass]
        #            nbMisclassifiedSamples += misclass
        return nbMisclassifiedSamples 

    def countNodes(self):
        count = 0
        nodes = ""
        nodelist = self.getNodeList(True,NodeType.NODE_NULL)
        for i in nodelist:
            if (self.tree[i].nodeType != NodeType.NODE_NULL):
                count += 1
                if (self.tree[i].nodeType == NodeType.NODE_INTERNAL):
                    nodes += "N" + str(i) + "A"+ str(self.tree[i].splitAttribute) 
                else:
                    nodes += "L" + str(i) + "C"+ str(self.tree[i].majorityClass)
        return count, nodes

    
    def copy(self, new_id):
        return self.partialCopy(new_id,-1)

    #ignoreSubTree = subtree from this node should be set to NULL
    #copy the Solution tree except the subtree desired
    #makes the subtreeparent a LEAF
    def partialCopy(self, new_id, ignoreSubTree):
        s = Solution(self.params,new_id)
        index=0
        nodesToIgnore = [ignoreSubTree]
        if ignoreSubTree>=0:
            while index<len(nodesToIgnore):
                nodetoIgnore = nodesToIgnore[index]
                if (2*nodetoIgnore >= len(self.tree)):
                    break

                nodesToIgnore.append(2*nodetoIgnore + 1)
                nodesToIgnore.append(2*nodetoIgnore + 2)
                index+=1
            nodesToIgnore.pop(0)

        nodelist = self.getNodeList(True, NodeType.NODE_NULL)
        for node in nodelist:
            if (self.tree[node].nodeType==NodeType.NODE_NULL):
                continue
            if node in nodesToIgnore:
                continue

            if (self.tree[node].nbSamplesNode > 0):
                s.tree[node].resetNode()

            for sample in self.tree[node].samples:
                s.tree[node].addSample(sample)
            s.tree[node].nodeType = self.tree[node].nodeType
            s.tree[node].splitAttribute = self.tree[node].splitAttribute
            s.tree[node].splitValue = self.tree[node].splitValue
            s.tree[node].entropy = self.tree[node].entropy
            s.tree[node].level = self.tree[node].level
            s.tree[node].majorityClass = self.tree[node].majorityClass
            s.tree[node].bestCandidates = []
            for c in self.tree[node].bestCandidates:
                s.tree[node].bestCandidates.append(CandidateSolution(c.splitAttribute, c.splitValue, c.informationGain))

            s.tree[node].evaluate()
            if ignoreSubTree==node:
                s.tree[node].nodeType=NodeType.NODE_LEAF
        return s

    def __init__(self, params, id):
        self.params = params
        self.startTime = datetime.datetime.now()
        self.endTime = datetime.datetime.now()
        self.maxnbNodes = 2**(params.maxDepth+1)-1
        self.tree = [Node(params) for x in range(self.maxnbNodes) ]

        self.tree[0].nodeType = NodeType.NODE_LEAF
        self.tree[0].level = 0 
        for i in range(0,params.nbSamples):
            self.tree[0].addSample(i)
        self.tree[0].evaluate()
        self.id = id

    def getTime(self):
        return self.endTime - self.startTime

    def getNodeList(self,all,type):
        nodelist=[]
        for i in range(0,len(self.tree)):
            if (self.tree[i].nodeType==NodeType.NODE_NULL):
                continue
            if all==True:
                nodelist.append(i)
                continue
            if (type==self.tree[i].nodeType):
                nodelist.append(i)
                continue

        return nodelist


    #AVALIAR SE A RESET NODE E A COPY NAO ESTAO REDUNDANTES
    def ResetNode(self, node):
        return
        if (node > self.maxnbNodes):
            return
        if (self.tree[node].nodeType == NodeType.NODE_NULL):
            return

        newNode = Node(self.params)
        for i in self.tree[node].samples:
            newNode.addSample(i)
        newNode.nodeType = self.tree[node].nodeType
        newNode.level = self.tree[node].level
        newNode.entropy = self.tree[node].entropy
        newNode.majorityClass = self.tree[node].majorityClass
        newNode.splitValue = self.tree[node].splitValue
        newNode.splitAttribute = self.tree[node].splitAttribute

        self.tree[node] = newNode
        temp=2**node
        self.ResetSons(2**node+1)
        self.ResetSons(2**node+2)

    def ResetSons(self,node):
        if (node > self.maxnbNodes):
            return

        temp=2**node
        self.ResetSons(2**node+1)
        self.ResetSons(2**node+2)
        self.tree[node] = Node(self.params)

class Params(object):
    def __init__(self, pathToInstance, pathToSolution, seedRNG, maxDepth, maxTime, lookAheadProportion, nbBestTries, debug):
        rd.seed(seedRNG)
        if debug:
            print("INITIALIZING RNG WITH SEED: ",seedRNG)
        f=open(pathToInstance, "r")
        self.maxDepth = maxDepth-1
        self.maxTime = maxTime
        self.seed = seedRNG
        self.lookAheadProportion = lookAheadProportion
        self.nbBestTries = nbBestTries

        attributeTypes = []
        
        line = f.readline()        
        self.datasetName = line.replace("\n","").split(" ")[1]
        line = f.readline()
        self.nbSamples = int(line.split(" ")[1])
        line = f.readline()
        self.nbAttributes = int(line.split(" ")[1])
        line = f.readline()
        self.attType = line.replace("\n","").split(" ")

        line = f.readline()
        self.nbClasses = int(line.split(" ")[1])
        self.attributeTypes = []
        for i in range(1,len(self.attType)):
            if(self.attType[i] == "C"):
                self.attributeTypes.append(AttributeType.TYPE_CATEGORICAL)
            else:
                if (self.attType[i] == "N"):
                    self.attributeTypes.append(AttributeType.TYPE_NUMERICAL)
                else:
                    print("ERROR: non recognized attribute type", self.attType)
        self.dataAttributes = [[0 for x in range(int(self.nbAttributes))] for y in range(int(self.nbSamples))]
        self.dataClasses = [0 for y in range(int(self.nbSamples))]
        self.nbLevels =  [0 for y in range(int(self.nbAttributes))]
        
        for s in range(0,self.nbSamples):
            line = f.readline()
            self.attributes = [float(y) for y in line.split(" ")]
            for i in range(0,self.nbAttributes):
                self.dataAttributes[s][i] = self.attributes[i]
                if ((self.attributeTypes[i] == AttributeType.TYPE_CATEGORICAL) 
                    and (self.dataAttributes[s][i]+1 > self.nbLevels[i])):
                    self.nbLevels[i] = self.dataAttributes[s][i]+1
            self.dataClasses[s]=self.attributes[self.nbAttributes]
        f.close()

        self.startTime = datetime.datetime.now()
        #if debug:
        #    print("----- DATASET [",self.datasetName,"]") # LOADED IN " << clock()/ (double)CLOCKS_PER_SEC << "(s)" << std::endl;
        #    print("----- NUMBER OF SAMPLES: ", self.nbSamples) 
        #    print("----- NUMBER OF ATTRIBUTES: ",self.nbAttributes)
        #    print("----- NUMBER OF CLASSES: ",self.nbClasses)

class Node:
    
    def __init__(self, params):
        self.params = params                   # Access to the problem and dataset parameters
        self.resetNode()
        self.bestCandidates = []

    def orderSamples(self):
        self.isOrderedSamples = True

        for att in range(0, self.params.nbAttributes):
            if (self.params.attributeTypes[att] == AttributeType.TYPE_NUMERICAL):
#                 CASE 1) -- FIND SPLIT WITH BEST INFORMATION GAIN FOR NUMERICAL ATTRIBUTE c */

#                 Define some data structures
                orderedSamplesInternal = []        #Order of the samples according to attribute c
                attributeLevelsInternal = []       #Store the possible levels of this attribute among the samples (will allow to "skip" samples with equal attribute value)

                for s in self.samples:
                    orderedSamplesInternal.append((self.params.dataAttributes[s][att], int(self.params.dataClasses[s])))
                    attributeLevelsInternal.append(self.params.dataAttributes[s][att])
                attributeLevelsInternal.sort()
                orderedSamplesInternal.sort()

                self.attributeLevels[att] = attributeLevelsInternal
                self.orderedSamples[att] = orderedSamplesInternal
            else:
                nbSamplesLevelInternal = [0 for y in range(int(self.params.nbLevels[att]))]
                nbSamplesClassInternal = [0 for y in range(self.params.nbClasses)]
                nbSamplesLevelClassInternal = {}
        
                for k in range(int(self.params.nbLevels[att])):
                    nbSamplesLevelClassInternal[k] = [0 for i in range(self.params.nbClasses)]
                for s in self.samples:
                    nbSamplesLevelInternal[int(self.params.dataAttributes[s][att])]+=1
                    nbSamplesClassInternal[int(self.params.dataClasses[s])]+=1
                    nbSamplesLevelClassInternal[int(self.params.dataAttributes[s][att])][int(self.params.dataClasses[s])] = int(nbSamplesLevelClassInternal[int(self.params.dataAttributes[s][att])][int(self.params.dataClasses[s])])+1

                self.nbSamplesLevel[att] = nbSamplesLevelInternal
                self.nbSamplesLevelClass[att] = nbSamplesLevelClassInternal

    def getnbSamplesLevel(self):
        if (self.isOrderedSamples == False):
            self.orderSamples()

        return self.nbSamplesLevel

    def getnbSamplesLevelClass(self):
        if (self.isOrderedSamples == False):
            self.nbSamplesClass()

        return self.nbSamplesLevelClass

    def getOrderedSamples(self):
        if (self.isOrderedSamples == False):
            self.orderSamples()

        return self.orderedSamples

    def getAttributeLevels(self):
        if (self.isOrderedSamples == False):
            self.orderSamples()

        return self.attributeLevels

    def getSamples(self):
        if (self.isOrderedSamples == False):
            self.orderSamples()

        return self.samples
    def evaluate(self):
        self.entropy = 0
        for c in range(0,self.params.nbClasses):
            if (self.nbSamplesClass[c]>0):
                frac = self.nbSamplesClass[c]/self.nbSamplesNode
                self.entropy -= frac * math.log(frac)
                if (self.nbSamplesClass[c] > self.maxSameClass):
                    self.maxSameClass = self.nbSamplesClass[c]
                    self.majorityClass = c

    
    def addSample(self, i):
        self.samples.append(i)
        self.nbSamplesClass[int(self.params.dataClasses[i])] += 1;
        self.nbSamplesNode += 1
        self.isOrderedSamples  = False

    def resetNode(self):
        self.nodeType = NodeType.NODE_NULL     # Node type
        self.splitAttribute = -1               # Attribute to which the split is applied (filled through the greedy algorithm)
        self.splitValue = -1.e30               # Threshold value for the split (for numerical attributes the left branch will be <= splitValue, for categorical will be == splitValue)					
        self.samples = []                      # Samples from the training set at this node
        self.orderedSamples = {}
        self.attributeLevels = {}
        self.nbSamplesClass = [0 for x in range(self.params.nbClasses+1)] # Number of samples of each class at this node (for each class)
        self.nbSamplesNode = 0                 # Total number of samples in this node
        self.majorityClass = -1                # Majority class in this node
        self.maxSameClass = 0                  # Maximum number of elements of the same class in this node
        self.entropy = -1.e30                  # Entropy in this node
        self.isOrderedSamples = False
        self.nbSamplesLevel = {}
        self.nbSamplesLevelClass  = {}
        self.bestCandidates = []
        self.level = -1

class CandidateSolution:
    def __init__(self, splitAttribute, splitValue, informationGain):
        self.splitAttribute = splitAttribute
        self.splitValue = splitValue
        self.informationGain = informationGain
        self.solution = ""
        self.nodes = -1
        self.nodestostring = ""
        self.misclassified=200000000

class Greedy:
    def __init__(self, params):
        self.params = params
        self.solution = ""
        self.bestSolution = None
        self.MY_EPSILON = 0.00001

        #if (autoexecute==True):
        #    self.recursiveConstruction(0,0,"",2, solution)
    
    def recursiveConstruction(self, node, level, forcedAttribute, nbSearchChildren, solution, allsolutions, nbCandidateSolutions):
        if (self.solution == ""):
            self.solution = solution

        nodeObj = solution.tree[node]
        # BASE CASES -- MAXIMUM LEVEL HAS BEEN ATTAINED OR ALL SAMPLES BELONG TO THE SAME CLASS
        if (( level >= self.params.maxDepth ) or ( nodeObj.maxSameClass == nodeObj.nbSamplesNode )):
            return solution

        if (datetime.datetime.now()-self.params.startTime).seconds>self.params.maxTime:
            nbSearchChildren=1

        candidateSolutions = []
        
#         LOOK FOR A BEST SPLIT        
        allIdentical = True
        nbSamplesNode = nodeObj.nbSamplesNode
        originalEntropy = nodeObj.entropy
        bestInformationGain = -1.e30
        bestSplitAttribute = -1
        bestSplitThrehold = -1.e30
        
        for att in range(0, self.params.nbAttributes):
            if (forcedAttribute != ""):
                if (forcedAttribute != att):
                    continue
            
            #nodeObj = self.solution.tree[node]

            if (self.params.attributeTypes[att] == AttributeType.TYPE_NUMERICAL):
#               CASE 1) -- FIND SPLIT WITH BEST INFORMATION GAIN FOR NUMERICAL ATTRIBUTE c */
#               Define some data structures

                tempOrderedSampes = nodeObj.getOrderedSamples()
                orderedSamples = tempOrderedSampes[att]         # Order of the samples according to attribute c
                tempAttributeLevels = nodeObj.getAttributeLevels()
                attributeLevels = list(set(tempAttributeLevels[att]))       # Store the possible levels of this attribute among the samples (will allow to "skip" samples with equal attribute value)
                attributeLevels.sort()

                if (len(attributeLevels)<=1):
                    continue
                else:
                    allIdentical = False
                
                #Initially all samples are on the right
                nbSamplesClassLeft = [0 for y in range(self.params.nbClasses+1)]
                nbSamplesClassRight = [nodeObj.nbSamplesClass[y] for y in range(self.params.nbClasses+1)]
                indexSample = 0

                # Go through all possible attribute values in increasing order
                # Iterate on all samples with this attributeValue and switch them to the left
                for attributeValue in attributeLevels:                     

                    while (indexSample < nodeObj.nbSamplesNode and orderedSamples[indexSample][0] < float(attributeValue + self.MY_EPSILON)):                     
                        nbSamplesClassLeft[orderedSamples[indexSample][1]]  += 1
                        nbSamplesClassRight[orderedSamples[indexSample][1]] -= 1
                        indexSample += 1

                    if (indexSample != nbSamplesNode):
                        #Evaluate entropy of the two resulting sample sets
                        entropyLeft = 0
                        entropyRight = 0
                        
                        for c in range(0, self.params.nbClasses):
                            #Remark that indexSample contains at this stage the number of samples in the left
                            if (nbSamplesClassLeft[c]>0):
                                fracLeft = nbSamplesClassLeft[c] / indexSample
                                entropyLeft -= fracLeft * math.log(fracLeft)
                            if (nbSamplesClassRight[c]>0):
                                fracRight = nbSamplesClassRight[c] / (nodeObj.nbSamplesNode - indexSample)
                                entropyRight -= fracRight * math.log(fracRight)
                            
                            #Evaluate the information gain and store if this is the best option found until now
                        informationGain = originalEntropy - (indexSample*entropyLeft + (nbSamplesNode - indexSample)*entropyRight) / nbSamplesNode

                        candidateSolutions.append((informationGain, CandidateSolution(att, attributeValue, informationGain)))
                        if (informationGain > bestInformationGain):
                            bestInformationGain = informationGain
                            bestSplitAttribute = att
                            bestSplitThrehold = attributeValue
                                           
                #candidateSolutions.append((bestInformationGain, CandidateSolution(bestSplitAttribute, bestSplitThrehold, bestInformationGain)))
            else:
                ##CASE 2) -- FIND BEST SPLIT FOR CATEGORICAL ATTRIBUTE c 
                ##Count for each level of attribute c and each class the number of samples

                nbSamplesLevel = nodeObj.getnbSamplesLevel()[att]
                nbSamplesClass = nodeObj.nbSamplesClass
                nbSamplesLevelClass = nodeObj.getnbSamplesLevelClass()[att]

                #Calculate information gain for a split at each possible level of attribute c
                for l in range(0,int(self.params.nbLevels[att])):
                    if (nbSamplesLevel[l] > 0 and nbSamplesLevel[l] <= nbSamplesNode):
                        #Evaluate entropy of the two resulting sample sets
                        allIdentical = False
                        entropyLevel = 0
                        entropyOthers = 0
                        for c in range(0,self.params.nbClasses):
                            if (nbSamplesLevelClass[l][c] > 0):
                                fracLevel = nbSamplesLevelClass[l][c] / nbSamplesLevel[l]
                                entropyLevel -= fracLevel * math.log(fracLevel)
                            if (nbSamplesClass[c] - nbSamplesLevelClass[l][c] > 0):
                                fracOthers = (nbSamplesClass[c] - nbSamplesLevelClass[l][c]) / (nbSamplesNode - nbSamplesLevel[l])
                                entropyOthers -= fracOthers * math.log(fracOthers)
                        # Evaluate the information gain and store if this is the best option found until now
                        informationGain = originalEntropy - (nbSamplesLevel[l] *entropyLevel + (nbSamplesNode - nbSamplesLevel[l])*entropyOthers) / nbSamplesNode 

                        candidateSolutions.append((informationGain, CandidateSolution(att, l, informationGain)))
                        if (informationGain > bestInformationGain):
                            bestInformationGain = informationGain
                            bestSplitAttribute = att
                            bestSplitThrehold = l

                #candidateSolutions.append((bestInformationGain, CandidateSolution(bestSplitAttribute, bestSplitThrehold, bestInformationGain)))

        
        # SPECIAL CASE TO HANDLE POSSIBLE CONTADICTIONS IN THE DATA 
        # (Situations where the same samples have different classes -- In this case no improving split can be found)

        if (allIdentical): 
            # APPLY THE SPLIT AND RECURSIVE CALL */
            nodeObj.splitAttribute = bestSplitAttribute
            nodeObj.splitValue = bestSplitThrehold
            return solution

        # APPLY THE SPLIT AND RECURSIVE CALL */

        candidatesExecuted = []
        nodeObj.bestCandidates=[]

        for j in range(0,nbCandidateSolutions):
            if (len(candidateSolutions)<=0):
                break
            nodeObj.bestCandidates.append(self.getNextBestCandidateSolution(candidateSolutions)[1])

        for j in range(0,nbSearchChildren):
            if (len(nodeObj.bestCandidates) <= j):
                break
            candidateSolution = nodeObj.bestCandidates[j]
            nodeObj.bestCandidates.append(candidateSolution)
            newid=rd.randint(1100000000,2000000000)
            candidateSolution.solution = solution.partialCopy(newid,node)
            candidatesExecuted.append(candidateSolution)
            candidateSolution.solution = self.recursiveContructionAux(node, level, candidateSolution.solution, candidateSolution.splitAttribute, candidateSolution.splitValue, candidateSolution.informationGain, nbSearchChildren, allsolutions, False, nbCandidateSolutions)
            candidateSolution.nodes, candidateSolution.nodestostring = candidateSolution.solution.countNodes()
            candidateSolution.misclassified = candidateSolution.solution.calculateMisclassifiedSamples()

        bestSolution = self.bestSolution
        bestMisclassified = 200000000
        bestNodes = 200000000
        if (self.bestSolution != None):
            bestMisclassified = self.bestSolution.calculateMisclassifiedSamples()

        for i in range(0,len(candidatesExecuted)):
            allsolutions[candidatesExecuted[i].nodestostring] = candidatesExecuted[i].solution
            if (candidatesExecuted[i].misclassified<=bestMisclassified):
                if (candidatesExecuted[i].misclassified==bestMisclassified):
                    if (candidatesExecuted[i].nodes<bestNodes):
                        bestNodes = candidatesExecuted[i].nodes
                        bestSolution = candidatesExecuted[i].solution
                        bestMisclassified = candidatesExecuted[i].misclassified
                else:
                    bestNodes = candidatesExecuted[i].nodes
                    bestSolution = candidatesExecuted[i].solution
                    bestMisclassified = candidatesExecuted[i].misclassified

        self.bestSolution = bestSolution
        
        self.bestSolution.endTime = datetime.datetime.now()
        return self.bestSolution

    def localsearch(self, node, solution, nbCandidateSolutions):
        if (self.solution == ""):
            self.solution = solution

        allsolutions = {}
        level = solution.tree[node].level
        nodeObj = solution.tree[node]

        candidatesExecuted=[]
        for candidateSolution in nodeObj.bestCandidates:
            newid=rd.randint(1100000000,2000000000)
            candidateSolution.solution = solution.partialCopy(newid,node)
            candidateSolution.solution = self.recursiveContructionAux(node, level, candidateSolution.solution, candidateSolution.splitAttribute, candidateSolution.splitValue, candidateSolution.informationGain, 1, allsolutions, False, nbCandidateSolutions)
            candidateSolution.nodes, candidateSolution.nodestostring = candidateSolution.solution.countNodes()
            candidateSolution.misclassified = candidateSolution.solution.calculateMisclassifiedSamples()
            candidatesExecuted.append(candidateSolution)

        bestSolution = self.bestSolution
        if (self.bestSolution == None):
            self.bestSolution = solution
            bestSolution = self.bestSolution
        bestMisclassified = self.bestSolution.calculateMisclassifiedSamples()
        bestNodes, nodestostring = self.bestSolution.countNodes()

        for i in range(0,len(candidatesExecuted)):
            if (candidatesExecuted[i].misclassified<=bestMisclassified):
                if (candidatesExecuted[i].misclassified==bestMisclassified):
                    if (candidatesExecuted[i].nodes<bestNodes):
                        bestNodes = candidatesExecuted[i].nodes
                        bestSolution = candidatesExecuted[i].solution
                        bestMisclassified = candidatesExecuted[i].misclassified
                else:
                    bestNodes = candidatesExecuted[i].nodes
                    bestSolution = candidatesExecuted[i].solution
                    bestMisclassified = candidatesExecuted[i].misclassified

        self.bestSolution = bestSolution
        
        self.bestSolution.endTime = datetime.datetime.now()
        return self.bestSolution
        

    def recursiveConstructionBestNatNode(self, node, level, forcedAttribute, nbSearchChildren, solution, allsolutions):
        if (self.solution == ""):
            self.solution = solution

        nodeObj = solution.tree[node]
        # BASE CASES -- MAXIMUM LEVEL HAS BEEN ATTAINED OR ALL SAMPLES BELONG TO THE SAME CLASS
        if (( level >= self.params.maxDepth ) or ( nodeObj.maxSameClass == nodeObj.nbSamplesNode )):
            return solution

        if (datetime.datetime.now()-self.params.startTime).seconds>self.params.maxTime:
            nbSearchChildren=1

        candidateSolutions = []
        
#         LOOK FOR A BEST SPLIT        
        allIdentical = True
        nbSamplesNode = nodeObj.nbSamplesNode
        originalEntropy = nodeObj.entropy
        bestInformationGain = -1.e30
        bestSplitAttribute = -1
        bestSplitThrehold = -1.e30
        
        for att in range(0, self.params.nbAttributes):
            if (forcedAttribute != ""):
                if (forcedAttribute != att):
                    continue
            
            #nodeObj = self.solution.tree[node]

            if (self.params.attributeTypes[att] == AttributeType.TYPE_NUMERICAL):
#               CASE 1) -- FIND SPLIT WITH BEST INFORMATION GAIN FOR NUMERICAL ATTRIBUTE c */
#               Define some data structures

                orderedSamples = nodeObj.getOrderedSamples()[att]         # Order of the samples according to attribute c
                attributeLevels = list(set(nodeObj.getAttributeLevels()[att]))       # Store the possible levels of this attribute among the samples (will allow to "skip" samples with equal attribute value)
                attributeLevels.sort()

                if (len(attributeLevels)<=1):
                    continue
                else:
                    allIdentical = False
                
                #Initially all samples are on the right
                nbSamplesClassLeft = [0 for y in range(self.params.nbClasses+1)]
                nbSamplesClassRight = [nodeObj.nbSamplesClass[y] for y in range(self.params.nbClasses+1)]
                indexSample = 0

                # Go through all possible attribute values in increasing order
                # Iterate on all samples with this attributeValue and switch them to the left
                for attributeValue in attributeLevels:                     

                    while (indexSample < nodeObj.nbSamplesNode and orderedSamples[indexSample][0] < float(attributeValue + self.MY_EPSILON)):                     
                        nbSamplesClassLeft[orderedSamples[indexSample][1]]  += 1
                        nbSamplesClassRight[orderedSamples[indexSample][1]] -= 1
                        indexSample += 1

                    if (indexSample != nbSamplesNode):
                        #Evaluate entropy of the two resulting sample sets
                        entropyLeft = 0
                        entropyRight = 0
                        
                        for c in range(0, self.params.nbClasses):
                            #Remark that indexSample contains at this stage the number of samples in the left
                            if (nbSamplesClassLeft[c]>0):
                                fracLeft = nbSamplesClassLeft[c] / indexSample
                                entropyLeft -= fracLeft * math.log(fracLeft)
                            if (nbSamplesClassRight[c]>0):
                                fracRight = nbSamplesClassRight[c] / (nodeObj.nbSamplesNode - indexSample)
                                entropyRight -= fracRight * math.log(fracRight)
                            
                            #Evaluate the information gain and store if this is the best option found until now
                        informationGain = originalEntropy - (indexSample*entropyLeft + (nbSamplesNode - indexSample)*entropyRight) / nbSamplesNode

                        candidateSolutions.append((informationGain, CandidateSolution(att, attributeValue, informationGain)))
                        if (informationGain > bestInformationGain):
                            bestInformationGain = informationGain
                            bestSplitAttribute = att
                            bestSplitThrehold = attributeValue
                                           
                candidateSolutions.append((bestInformationGain, CandidateSolution(bestSplitAttribute, bestSplitThrehold, bestInformationGain)))
            else:
                ##CASE 2) -- FIND BEST SPLIT FOR CATEGORICAL ATTRIBUTE c 
                ##Count for each level of attribute c and each class the number of samples

                nbSamplesLevel = nodeObj.getnbSamplesLevel()[att]
                nbSamplesClass = nodeObj.nbSamplesClass
                nbSamplesLevelClass = nodeObj.getnbSamplesLevelClass()[att]

                #Calculate information gain for a split at each possible level of attribute c
                for l in range(0,int(self.params.nbLevels[att])):
                    if (nbSamplesLevel[l] > 0 and nbSamplesLevel[l] <= nbSamplesNode):
                        #Evaluate entropy of the two resulting sample sets
                        allIdentical = False
                        entropyLevel = 0
                        entropyOthers = 0
                        for c in range(0,self.params.nbClasses):
                            if (nbSamplesLevelClass[l][c] > 0):
                                fracLevel = nbSamplesLevelClass[l][c] / nbSamplesLevel[l]
                                entropyLevel -= fracLevel * math.log(fracLevel)
                            if (nbSamplesClass[c] - nbSamplesLevelClass[l][c] > 0):
                                fracOthers = (nbSamplesClass[c] - nbSamplesLevelClass[l][c]) / (nbSamplesNode - nbSamplesLevel[l])
                                entropyOthers -= fracOthers * math.log(fracOthers)
                        # Evaluate the information gain and store if this is the best option found until now
                        informationGain = originalEntropy - (nbSamplesLevel[l] *entropyLevel + (nbSamplesNode - nbSamplesLevel[l])*entropyOthers) / nbSamplesNode 

                        candidateSolutions.append((informationGain, CandidateSolution(att, l, informationGain)))
                        if (informationGain > bestInformationGain):
                            bestInformationGain = informationGain
                            bestSplitAttribute = att
                            bestSplitThrehold = l

                candidateSolutions.append((bestInformationGain, CandidateSolution(bestSplitAttribute, bestSplitThrehold, bestInformationGain)))

        
        # SPECIAL CASE TO HANDLE POSSIBLE CONTADICTIONS IN THE DATA 
        # (Situations where the same samples have different classes -- In this case no improving split can be found)

        if (allIdentical): 
            # APPLY THE SPLIT AND RECURSIVE CALL */
            nodeObj.splitAttribute = bestSplitAttribute
            nodeObj.splitValue = bestSplitThrehold
            return solution

        # APPLY THE SPLIT AND RECURSIVE CALL */

        candidatesExecuted = []

        for j in range(0,nbSearchChildren):
            if (len(candidateSolutions) <= 0):
                break
            if (datetime.datetime.now()-self.params.startTime).seconds>self.params.maxTime:
                break
            candidateSolution = self.getNextBestCandidateSolution(candidateSolutions)[1]
            newid=rd.randint(1100000000,2000000000)
            candidateSolution.solution = solution.partialCopy(newid,node)
            candidatesExecuted.append(candidateSolution)
            candidateSolution.solution = self.recursiveContructionAux(node, level, candidateSolution.solution, candidateSolution.splitAttribute, candidateSolution.splitValue, candidateSolution.informationGain, 1, allsolutions, False, nbSearchChildren)
            candidateSolution.nodes, candidateSolution.nodestostring = candidateSolution.solution.countNodes()
            candidateSolution.misclassified = candidateSolution.solution.calculateMisclassifiedSamples()

        bestSolution = self.bestSolution
        bestMisclassified = 200000000
        bestNodes = 200000000
        if (self.bestSolution != None):
            bestMisclassified = self.bestSolution.calculateMisclassifiedSamples()

        for i in range(0,len(candidatesExecuted)):
            allsolutions[candidatesExecuted[i].nodestostring] = candidatesExecuted[i].solution
            if (candidatesExecuted[i].misclassified<=bestMisclassified):
                if (candidatesExecuted[i].misclassified==bestMisclassified):
                    if (candidatesExecuted[i].nodes<bestNodes):
                        bestNodes = candidatesExecuted[i].nodes
                        bestSolution = candidatesExecuted[i].solution
                        bestMisclassified = candidatesExecuted[i].misclassified
                else:
                    bestNodes = candidatesExecuted[i].nodes
                    bestSolution = candidatesExecuted[i].solution
                    bestMisclassified = candidatesExecuted[i].misclassified

        self.bestSolution = bestSolution
        
        self.bestSolution.endTime = datetime.datetime.now()
        return self.bestSolution

#    def recursiveConstructionrandom(self, node, level, forcedAttribute, nbSearchChildren, solution, allsolutions):
#        if (self.solution == ""):
#            self.solution = solution

#        nodeObj = solution.tree[node]
#        # BASE CASES -- MAXIMUM LEVEL HAS BEEN ATTAINED OR ALL SAMPLES BELONG TO THE SAME CLASS
#        if (( level >= self.params.maxDepth ) or ( nodeObj.maxSameClass == nodeObj.nbSamplesNode )):
#            return solution

#        candidateSolutions = []
        
##         LOOK FOR A BEST SPLIT        
#        allIdentical = True
#        nbSamplesNode = nodeObj.nbSamplesNode
#        originalEntropy = nodeObj.entropy
#        bestInformationGain = -1.e30
#        bestSplitAttribute = -1
#        bestSplitThrehold = -1.e30
        
#        for att in range(0, self.params.nbAttributes):
#            if (forcedAttribute != ""):
#                if (forcedAttribute != att):
#                    continue
            
#            #nodeObj = self.solution.tree[node]

#            if (self.params.attributeTypes[att] == AttributeType.TYPE_NUMERICAL):
##               CASE 1) -- FIND SPLIT WITH BEST INFORMATION GAIN FOR NUMERICAL ATTRIBUTE c */
##               Define some data structures

#                orderedSamples = nodeObj.getOrderedSamples()[att][1]         # Order of the samples according to attribute c
#                attributeLevels = list(set(nodeObj.getAttributeLevels()[att][1]))       # Store the possible levels of this attribute among the samples (will allow to "skip" samples with equal attribute value)
#                attributeLevels.sort()

#                if (len(attributeLevels)<=1):
#                    continue
#                else:
#                    allIdentical = False
                
#                #Initially all samples are on the right
#                nbSamplesClassLeft = [0 for y in range(self.params.nbClasses+1)]
#                nbSamplesClassRight = [nodeObj.nbSamplesClass[y] for y in range(self.params.nbClasses+1)]
#                indexSample = 0

#                # Go through all possible attribute values in increasing order
#                # Iterate on all samples with this attributeValue and switch them to the left
#                for attributeValue in attributeLevels:                     

#                    while (indexSample < nodeObj.nbSamplesNode and orderedSamples[indexSample][0] < float(attributeValue + self.MY_EPSILON)):                     
#                        nbSamplesClassLeft[orderedSamples[indexSample][1]]  += 1
#                        nbSamplesClassRight[orderedSamples[indexSample][1]] -= 1
#                        indexSample += 1

#                    if (indexSample != nbSamplesNode):
#                        #Evaluate entropy of the two resulting sample sets
#                        entropyLeft = 0
#                        entropyRight = 0
                        
#                        for c in range(0, self.params.nbClasses):
#                            #Remark that indexSample contains at this stage the number of samples in the left
#                            if (nbSamplesClassLeft[c]>0):
#                                fracLeft = nbSamplesClassLeft[c] / indexSample
#                                entropyLeft -= fracLeft * math.log(fracLeft)
#                            if (nbSamplesClassRight[c]>0):
#                                fracRight = nbSamplesClassRight[c] / (nodeObj.nbSamplesNode - indexSample)
#                                entropyRight -= fracRight * math.log(fracRight)
                            
#                            #Evaluate the information gain and store if this is the best option found until now
#                        informationGain = originalEntropy - (indexSample*entropyLeft + (nbSamplesNode - indexSample)*entropyRight) / nbSamplesNode

#                        candidateSolutions.append((informationGain, CandidateSolution(att, attributeValue, informationGain)))
#                        if (informationGain > bestInformationGain):
#                            bestInformationGain = informationGain
#                            bestSplitAttribute = att
#                            bestSplitThrehold = attributeValue
                                           
#                candidateSolutions.append((bestInformationGain, CandidateSolution(bestSplitAttribute, bestSplitThrehold, bestInformationGain)))
#            else:
#                ##CASE 2) -- FIND BEST SPLIT FOR CATEGORICAL ATTRIBUTE c 
#                ##Count for each level of attribute c and each class the number of samples

#                nbSamplesLevel = nodeObj.getnbSamplesLevel()[att]
#                nbSamplesClass = nodeObj.nbSamplesClass
#                nbSamplesLevelClass = nodeObj.getnbSamplesLevelClass()[att]

#                #Calculate information gain for a split at each possible level of attribute c
#                for l in range(0,int(self.params.nbLevels[att])):
#                    if (nbSamplesLevel[l] > 0 and nbSamplesLevel[l] <= nbSamplesNode):
#                        #Evaluate entropy of the two resulting sample sets
#                        allIdentical = False
#                        entropyLevel = 0
#                        entropyOthers = 0
#                        for c in range(0,self.params.nbClasses):
#                            if (nbSamplesLevelClass[l][c] > 0):
#                                fracLevel = nbSamplesLevelClass[l][c] / nbSamplesLevel[l]
#                                entropyLevel -= fracLevel * math.log(fracLevel)
#                            if (nbSamplesClass[c] - nbSamplesLevelClass[l][c] > 0):
#                                fracOthers = (nbSamplesClass[c] - nbSamplesLevelClass[l][c]) / (nbSamplesNode - nbSamplesLevel[l])
#                                entropyOthers -= fracOthers * math.log(fracOthers)
#                        # Evaluate the information gain and store if this is the best option found until now
#                        informationGain = originalEntropy - (nbSamplesLevel[l] *entropyLevel + (nbSamplesNode - nbSamplesLevel[l])*entropyOthers) / nbSamplesNode 

#                        candidateSolutions.append((informationGain, CandidateSolution(att, l, informationGain)))
#                        if (informationGain > bestInformationGain):
#                            bestInformationGain = informationGain
#                            bestSplitAttribute = att
#                            bestSplitThrehold = l

#                candidateSolutions.append((bestInformationGain, CandidateSolution(bestSplitAttribute, bestSplitThrehold, bestInformationGain)))

        
#        # SPECIAL CASE TO HANDLE POSSIBLE CONTADICTIONS IN THE DATA 
#        # (Situations where the same samples have different classes -- In this case no improving split can be found)

#        if (allIdentical): 
#            # APPLY THE SPLIT AND RECURSIVE CALL */
#            nodeObj.splitAttribute = bestSplitAttribute
#            nodeObj.splitValue = bestSplitThrehold
#            return solution

#        # APPLY THE SPLIT AND RECURSIVE CALL */

#        candidatesExecuted = []
#        candidatestoExecution = []

#        for j in range(0,nbSearchChildren):
#            if (len(candidateSolutions) <= 0):
#                break
#            candidateSolution = self.getNextBestCandidateSolution(candidateSolutions)[1]
#            candidateSolution.solution = solution.partialCopy(rd.randint(10000000,200000000),node)
#            candidatestoExecution.append(candidateSolution)

#        indextoExecute = rd.randint(0,len(candidatestoExecution)-1)
#        candidateSolution = candidatestoExecution[indextoExecute]
#        candidatesExecuted.append(candidateSolution)
#        candidateSolution.solution = self.recursiveContructionAux(node, level, candidateSolution.solution, candidateSolution.splitAttribute, candidateSolution.splitValue, candidateSolution.informationGain, 1, allsolutions, False)
#        candidateSolution.nodes, candidateSolution.nodestostring = candidateSolution.solution.countNodes()
#        candidateSolution.misclassified = candidateSolution.solution.calculateMisclassifiedSamples()

#        bestSolution = self.bestSolution
#        bestMisclassified = 200000000
#        bestNodes = 200000000
#        if (self.bestSolution != None):
#            bestMisclassified = self.bestSolution.calculateMisclassifiedSamples()

#        for i in range(0,len(candidatesExecuted)):
#            allsolutions[candidatesExecuted[i].nodestostring] = candidatesExecuted[i].solution
#            if (candidatesExecuted[i].misclassified<=bestMisclassified):
#                if (candidatesExecuted[i].misclassified==bestMisclassified):
#                    if (candidatesExecuted[i].nodes<bestNodes):
#                        bestNodes = candidatesExecuted[i].nodes
#                        bestSolution = candidatesExecuted[i].solution
#                        bestMisclassified = candidatesExecuted[i].misclassified
#                else:
#                    bestNodes = candidatesExecuted[i].nodes
#                    bestSolution = candidatesExecuted[i].solution
#                    bestMisclassified = candidatesExecuted[i].misclassified

#        self.bestSolution = bestSolution
        
#        self.bestSolution.endTime = datetime.datetime.now()
#        return self.bestSolution


    def getNextBestCandidateSolution(self,candidates):
        bestIndex = -1
        bestIG = -1

        for i in range(0,len(candidates)):
            if (candidates[i][0]>=bestIG):
                bestIndex = i
                bestIG = candidates[i][0]

        return candidates.pop(bestIndex)

    def recursiveContructionAux(self, node, level, solution, splitAttribute, splitValue, informationGain, nbSearchChildren, allsolutions, random, nbCandidateSolutions ):
        nodeObj = solution.tree[node]

        nodeObj.splitAttribute = splitAttribute
        nodeObj.splitValue = splitValue
        nodeObj.nodeType = NodeType.NODE_INTERNAL

        solution.tree[2*node+1].nodeType = NodeType.NODE_LEAF
        solution.tree[2*node+2].nodeType = NodeType.NODE_LEAF
        solution.tree[2*node+1].level = level + 1 
        solution.tree[2*node+2].level = level + 1 
        for s in nodeObj.samples:
            if ((self.params.attributeTypes[splitAttribute] == AttributeType.TYPE_NUMERICAL and 
                    self.params.dataAttributes[s][splitAttribute] < splitValue + self.MY_EPSILON) or 
                (self.params.attributeTypes[splitAttribute] == AttributeType.TYPE_CATEGORICAL and
                    self.params.dataAttributes[s][splitAttribute] < splitValue + self.MY_EPSILON and
                    self.params.dataAttributes[s][splitAttribute] > splitValue - self.MY_EPSILON)):
                solution.tree[2*node+1].addSample(s)
            else:
                solution.tree[2*node+2].addSample(s)

        solution.tree[2*node+1].evaluate() # Setting all other data structures
        solution.tree[2*node+2].evaluate() # Setting all other data structures

        if random:
            solution = self.recursiveConstructionrandom(2*node+1,level+1,"", nbSearchChildren, solution, allsolutions) # Recursive call
            solution = self.recursiveConstructionrandom(2*node+2,level+1,"", nbSearchChildren, solution, allsolutions) # Recursive call
        else:
            solution = self.recursiveConstruction(2*node+1,level+1,"", nbSearchChildren, solution, allsolutions, nbCandidateSolutions) # Recursive call
            solution = self.recursiveConstruction(2*node+2,level+1,"", nbSearchChildren, solution, allsolutions, nbCandidateSolutions) # Recursive call
        return solution
