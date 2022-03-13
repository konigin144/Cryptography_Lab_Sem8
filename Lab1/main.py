from bitarray import bitarray
from bitarray.util import int2ba
import itertools, os

repoPath = os.path.dirname(os.path.abspath(__file__))+'\\'

# read file in binary mode
def readFile(filePath):
    inputBitarray = bitarray()
    with open(repoPath+filePath, 'rb') as readFile:
       inputBitarray.fromfile(readFile)
    
    global FUNC_SIZE
    FUNC_SIZE = int(len(inputBitarray) / 16)
    return inputBitarray

# delete bytes equal to 0
def deleteZeroBytes(bitArray):
    for i in range(FUNC_SIZE):
        for j in range(8):
            bitArray.pop(8*(i+1))
    return bitArray

# generate functions from file
def buildInputFunc(bitArray):
    inputFuncArray = []
    for i in range(8):
        inputFunc = bitarray()
        for j in range(FUNC_SIZE):
            inputFunc.append(bitArray[j*8+i])
        inputFuncArray.append(inputFunc)
    return inputFuncArray

# check if function is balanced - number of 0s is equal to number of 1s
def isFuncBalaced(func):
    zeros = func.count(0)
    ones = func.count(1)
    return zeros == ones    

# get all combinations from array (0, 2^size)
def getIndexCombinations(size):
    result = []
    indexArray = list(range(0,size))
    for i in range(1, size+1):
        result += list(itertools.combinations(indexArray, i))
    return result

# generate linear functions
def buildLinearFuncs():
    # generate 0-255 in binary
    array = []
    for i in range(FUNC_SIZE):
        newArray = bitarray('00000000')
        num = int2ba(i)
        for j in range(len(str(num.to01()))):
            newArray.pop()
        newArray.extend(int2ba(i))
        array.append(newArray)

    combs = getIndexCombinations(8)

    resultArray = []
    for comb in combs: # for every index combination
        partArray = bitarray()
        for bits in array: # 0-255
            xs = []
            for index in comb: # get xs
                xs.append(int(bits[7-index]))
            partResult = xs[0]
            for i in range(1, len(xs), 1): # xor xs
                partResult ^= xs[i]
            partArray.append(partResult)
        resultArray.append(partArray)

    # add function with 0s
    zeros256 = "0" * FUNC_SIZE
    resultArray.append(bitarray(zeros256))
    return resultArray

# determine nonlinearity of functions
def nonlinearity(fileFuncs, linearFuncs): 
    result = []
    for fileFunc in fileFuncs: # for every file function
        fileFuncResults = []
        for linearFunc in linearFuncs: # for every linear function
            xorResult = []
            for i in range(FUNC_SIZE):
                xorResult.append(int(fileFunc[i] ^ linearFunc[i]))
            xorSum = sum(xorResult)
            fileFuncResults.append(xorSum)
        result.append(min(fileFuncResults))
    return result

# verify SAC   
def sac(fileFuncs):
    results = []
    for fileFunc in fileFuncs: # for every file function
        fileFuncResults = []
        for i in range(8): # for every bit in polynomial
            newFunc = []
            power2 = 2**i
            swapPairsNum = int(FUNC_SIZE/(power2*2))
            lastIndex = 0
            for j in range(swapPairsNum): # for every swap pair
                top = []
                bot = []         
                for k in range(lastIndex, lastIndex+power2):
                    top.append(int(fileFunc[k]))
                    lastIndex += 1
                for k in range(lastIndex, lastIndex+power2):
                    bot.append(int(fileFunc[k]))
                    lastIndex += 1
                newFunc += bot
                newFunc += top
            fileFuncResults.append(newFunc)
        results.append(fileFuncResults)

    sacs = []
    for fileFunc, funcResult in zip(fileFuncs, results):
        functionSacs = []
        for result in funcResult:
            xorFunction = []
            for i in range(FUNC_SIZE):
                xorFunction.append(fileFunc[i] ^ result[i])
            functionSacs.append(sum(xorFunction))
        average = avg(functionSacs)
        percentage = average / FUNC_SIZE
        sacs.append(percentage)
    
    totalSac = avg(sacs)

    print("=== SAC for functions ===")
    print('\n'.join(str(el) for el in sacs))
    print("=== AVG ===")
    print(totalSac)

def avg(array):
    return sum(array)/len(array)

### ------------------------------------------------------------ ###
    
# read functions from file
file = readFile("sbox_08x08_20130110_011319_02.SBX")
newFile = deleteZeroBytes(file)
fileFuncs = buildInputFunc(newFile)

# check if functions from file are balanced
for i in range(8):
    if isFuncBalaced(fileFuncs[i]) is False:
        print(str(i) + " is bot balanced!")

# build linear functions
linearFuncs = buildLinearFuncs()

# determine nonlinearity
result = nonlinearity(fileFuncs, linearFuncs)

# verify SAC
sac(fileFuncs)