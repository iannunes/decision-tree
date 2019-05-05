import math
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
        nbMisclassifiedSamples = 0
        print("---------------------------------------- PRINTING SOLUTION ----------------------------------------")
        serialized = ""
        for d in range(0, self.params.maxDepth+1):
            inicio = 2**d - 1
            fim = 2**(d+1) - 1
            for i in range(inicio,fim):
                if (self.tree[i].nodeType == NodeType.NODE_INTERNAL):
                    sinal = "="
                    if (self.params.attributeTypes[self.tree[i].splitAttribute] == AttributeType.TYPE_NUMERICAL):
                        sinal = "<="
                    serialized = serialized + "(N"+ str(i) + ",A["+ str(self.tree[i].splitAttribute) + "]"+ sinal + str(self.tree[i].splitValue)+ ")"
                else:
                    if (self.tree[i].nodeType == NodeType.NODE_LEAF):
                        misclass = self.tree[i].nbSamplesNode - self.tree[i].nbSamplesClass[self.tree[i].majorityClass]
                        nbMisclassifiedSamples += misclass
                        serialized = serialized + "(L" + str(i) + ",C" + str(self.tree[i].majorityClass) + "," + str(self.tree[i].nbSamplesClass[self.tree[i].majorityClass]) + "," + str(misclass) + ") "
            serialized = serialized + "\n"
        print (serialized)
        print(nbMisclassifiedSamples , "/" , self.params.nbSamples , " MISCLASSIFIED SAMPLES" )
        print("---------------------------------------------------------------------------------------------------" )
        
        print("TIME(s): ", (self.params.endTime - self.params.startTime))
        print("NB_SAMPLES: " ,  self.params.nbSamples )
        print("NB_MISCLASSIFIED: " , nbMisclassifiedSamples)

    def __init__(self, params):
        self.params = params
        self.tree = [Node(params) for x in range(2**(params.maxDepth+1)-1) ]
        for i in range(0,len(self.tree)):
            self.tree[i] = Node(params)
        
        self.tree[0].nodeType = NodeType.NODE_LEAF
        for i in range(0,params.nbSamples):
            self.tree[0].addSample(i)
        self.tree[0].evaluate()

class Params(object):
    def __init__(self, pathToInstance, pathToSolution, seedRNG, maxDepth, maxTime):
        rd.seed(seedRNG)
        print("INITIALIZING RNG WITH SEED: ",seedRNG)
        f=open(pathToInstance, "r")
        self.maxDepth = maxDepth-1

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
        
        print("----- DATASET [",self.datasetName,"]") # LOADED IN " << clock()/ (double)CLOCKS_PER_SEC << "(s)" << std::endl;
        print("----- NUMBER OF SAMPLES: ", self.nbSamples) 
        print("----- NUMBER OF ATTRIBUTES: ",self.nbAttributes)
        print("----- NUMBER OF CLASSES: ",self.nbClasses)

class Node:
    
    def __init__(self, params):
        self.params = params
        self.nodeType = NodeType.NODE_NULL     # Node type
        self.params = params                   # Access to the problem and dataset parameters
        self.splitAttribute = -1               # Attribute to which the split is applied (filled through the greedy algorithm)
        self.splitValue = -1.e30               # Threshold value for the split (for numerical attributes the left branch will be <= splitValue, for categorical will be == splitValue)					
        self.samples = []                      # Samples from the training set at this node
        self.nbSamplesClass = [0 for x in range(self.params.nbClasses+1)] # Number of samples of each class at this node (for each class)
        self.nbSamplesNode = 0                 # Total number of samples in this node
        self.majorityClass = -1                # Majority class in this node
        self.maxSameClass = 0                  # Maximum number of elements of the same class in this node
        self.entropy = -1.e30                  # Entropy in this node
        
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

class Greedy:
    def __init__(self, params, solution):
        self.params = params
        self.solution = solution
        self.recursiveConstruction(0,0)
    
    def recursiveConstruction(self, node, level):
        nodeObj = self.solution.tree[node]
        # BASE CASES -- MAXIMUM LEVEL HAS BEEN ATTAINED OR ALL SAMPLES BELONG TO THE SAME CLASS
        if (( level >= self.params.maxDepth ) or ( nodeObj.maxSameClass == nodeObj.nbSamplesNode )):
            return
        
#         LOOK FOR A BEST SPLIT        
        allIdentical = True
        nbSamplesNode = nodeObj.nbSamplesNode
        originalEntropy = nodeObj.entropy
        bestInformationGain = -1.e30
        bestSplitAttibute = -1
        bestSplitThrehold = -1.e30
        MY_EPSILON=0.00001
        
        for att in range(0, self.params.nbAttributes):
            if (self.params.attributeTypes[att] == AttributeType.TYPE_NUMERICAL):
#                 CASE 1) -- FIND SPLIT WITH BEST INFORMATION GAIN FOR NUMERICAL ATTRIBUTE c */

#                 Define some data structures
                orderedSamples = []        #Order of the samples according to attribute c
                attributeLevels = []       #Store the possible levels of this attribute among the samples (will allow to "skip" samples with equal attribute value)
                for s in nodeObj.samples:
                    orderedSamples.append((self.params.dataAttributes[s][att],int(self.params.dataClasses[s])))
                    attributeLevels.append(self.params.dataAttributes[s][att])
                attributeLevels.sort()
                orderedSamples.sort()
                if (len(attributeLevels)<=1):
                    continue
                else:
                    allIdentical = False
                
                #Initially all samples are on the right
                
                nbSamplesClassLeft = [0 for y in range(self.params.nbClasses+1)]
                nbSamplesClassRight = [nodeObj.nbSamplesClass[y] for y in range(self.params.nbClasses+1)]
                indexSample = 0
                #filteredOrderedSamples = sorted({k : v for k,v in filter(lambda t: t[0] in [1, 3], orderedSamples.iteritems())})
                # Go through all possible attribute values in increasing order
                # Iterate on all samples with this attributeValue and switch them to the left
                for attributeValue in attributeLevels:                     

                    while (indexSample < nodeObj.nbSamplesNode and orderedSamples[indexSample][0] < float(attributeValue + MY_EPSILON)):                     
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
                            
                        if (informationGain > bestInformationGain):
                            bestInformationGain = informationGain
                            bestSplitAttribute = att
                            bestSplitThrehold = attributeValue
            else:
                #CASE 2) -- FIND BEST SPLIT FOR CATEGORICAL ATTRIBUTE c 
                #Count for each level of attribute c and each class the number of samples
                nbSamplesLevel = [0 for y in range(int(self.params.nbLevels[att]))]
                nbSamplesClass = [0 for y in range(self.params.nbClasses)]
                nbSamplesLevelClass = {}
                
                for k in range(int(self.params.nbLevels[att])):
                    nbSamplesLevelClass[k] = [0 for i in range(self.params.nbClasses)]
                
                for s in nodeObj.samples:
                    s = int(s)
                    att = int(att)

                    nbSamplesLevel[int(self.params.dataAttributes[s][att])]+=1
                    nbSamplesClass[int(self.params.dataClasses[s])]+=1
                    
                    #print(int(self.params.dataAttributes[s][att]))
                    #print(self.params.dataClasses[s])
                    #print(nbSamplesLevelClass)
                    
                    nbSamplesLevelClass[int(self.params.dataAttributes[s][att])][int(self.params.dataClasses[s])] = int(nbSamplesLevelClass[int(self.params.dataAttributes[s][att])][int(self.params.dataClasses[s])])+1
                #print(self.params.nbLevels[att])                                                
                #Calculate information gain for a split at each possible level of attribute c
                for l in range(0,int(self.params.nbLevels[att])):
                    if (nbSamplesLevel[l] > 0 and nbSamplesLevel[l] < nbSamplesNode):
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
                        if (informationGain > bestInformationGain):
                            bestInformationGain = informationGain
                            bestSplitAttribute = att
                            bestSplitThrehold = l
        # SPECIAL CASE TO HANDLE POSSIBLE CONTADICTIONS IN THE DATA 
        # (Situations where the same samples have different classes -- In this case no improving split can be found)

        if (allIdentical): 
            return

        # APPLY THE SPLIT AND RECURSIVE CALL */
        nodeObj.splitAttribute = bestSplitAttribute
        nodeObj.splitValue = bestSplitThrehold
        nodeObj.nodeType = NodeType.NODE_INTERNAL
        self.solution.tree[2*node+1].nodeType = NodeType.NODE_LEAF
        self.solution.tree[2*node+2].nodeType = NodeType.NODE_LEAF
        for s in nodeObj.samples:
            if ((self.params.attributeTypes[bestSplitAttribute] == AttributeType.TYPE_NUMERICAL and 
                 self.params.dataAttributes[s][bestSplitAttribute] < bestSplitThrehold + MY_EPSILON) or 
                (self.params.attributeTypes[bestSplitAttribute] == AttributeType.TYPE_CATEGORICAL and
                 self.params.dataAttributes[s][bestSplitAttribute] < bestSplitThrehold + MY_EPSILON and
                 self.params.dataAttributes[s][bestSplitAttribute] > bestSplitThrehold - MY_EPSILON)):
                self.solution.tree[2*node+1].addSample(s)
            else:
                self.solution.tree[2*node+2].addSample(s)
        self.solution.tree[2*node+1].evaluate() # Setting all other data structures
        self.solution.tree[2*node+2].evaluate() # Setting all other data structures
        self.recursiveConstruction(2*node+1,level+1) # Recursive call
        self.recursiveConstruction(2*node+2,level+1) # Recursive call

