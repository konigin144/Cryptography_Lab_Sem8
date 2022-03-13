import operator, os, re

repoPath = os.path.dirname(os.path.abspath(__file__))+'\\'

# print 2-dimensional array in prettier way
def prettyArrayPrint(arr):
    print('\n'.join(' '.join(str(x) for x in row) for row in arr))

# get SBOXes from file
def readSboxFile(filePath):
    sboxes = []
    with open(repoPath+filePath, 'r') as readFile:
       file = readFile.readlines()

    sboxesNum = int(len(file)/6)
    for i in range(sboxesNum+1):
        sbox = []
        for j in range(1, 5):
            line = file[i*6+j]
            numbers = [int(s) for s in re.findall(r'\b\d+\b', line)]
            sbox.append(numbers)
        sboxes.append(sbox)
    return sboxes

# generate TDR and TZP tables for SBOX
def generateTDR_TZP(sbox):
    tdrTable = []
    tzpTable = []
    for i in range(64):
        row1 = []
        row2 = []
        for j in range(16):
            row1.append(0)
            row2.append([])
        tdrTable.append(row1)
        tzpTable.append(row2)

    for x1 in range(64):
        for x2 in range(64):
            so = x1 ^ x2
            sbox1 = getValueFromSbox(x1, sbox)
            sbox2 = getValueFromSbox(x2, sbox)
            si = sbox1 ^ sbox2
            tdrTable[so][si] += 1
            tzpTable[so][si].append((x1, x2))

    return tdrTable, tzpTable

# get So for given Si and SBOX
def getValueFromSbox(val, sbox):
    binary = format(val, "06b")
    row = ""+str(binary[0])+str(binary[5])
    col = ""+str(binary[1])+str(binary[2])+str(binary[3])+str(binary[4])
    rowDec = int(row, 2)
    colDec = int(col, 2)
    return sbox[rowDec][colDec]

# get n pair indexes with highest value
def getHighestPairsIndexes(tdrTable, n):
    highestValues = [0] * n
    highestIndexes = [(0,0)] * n

    for k in range(n):
        for i in range(len(tdrTable)):
            row = tdrTable[i]
            highestInRow = max(row)
            if highestInRow != 64:
                for j in range(n):
                    if highestValues[j] < highestInRow and (i, row.index(highestInRow)) not in highestIndexes:
                        highestIndexes[j] = (i, row.index(highestInRow))
                        highestValues[j] = highestInRow
                        break

    return highestIndexes

# get (x1, x2) pairs from TZP
def getPairsFromByIndexes(tzpTable, rowCols):
    result = []

    for rowCol in rowCols:
        result.append(tzpTable[rowCol[0]][rowCol[1]])

    return result

# get pair (x1, x2) that matches x1 xor x2 = result
def getPairByModuloResult(result):
    x1 = 1
    x2 = 0
    while True:
        if x1 ^ x2 == result:
            return x1, x2
        x2 += 1

# generate keys from pairs
def getKeys(si, rowCols):


    keys = []
    for rowPairs, rowCol in zip(si, rowCols):
        for pair in rowPairs:
            xe1, xe2 = getPairByModuloResult(rowCol[0])
            keys.append(pair[0] ^ xe1)

    keysResult = dict()
    for key in keys:
        if key in keysResult:
            keysResult[key] += 1
        else:
            keysResult[key] = 1

    sorted_d = dict(sorted(keysResult.items(), key=operator.itemgetter(1),reverse=True))

    return sorted_d

# generate n best keys from given keys dictionary
def getNBestKeysHex(keys, n):
    result = dict()
    i = 0
    for key in keys.items():
        if i < n:
            result[hex(key[0])] = key[1]
            i += 1

    return result

### ------------------------------------------------------------ ###

sboxes = readSboxFile("S-boxes.txt")
sboxNum = 1
for sbox in sboxes:
    tdrTable, tzpTable = generateTDR_TZP(sbox)

    rowCols = getHighestPairsIndexes(tdrTable, 5)
    pairs = getPairsFromByIndexes(tzpTable, rowCols)
    keys = getKeys(pairs, rowCols)
    bestKeys = getNBestKeysHex(keys, 5)

    print("Keys for SBOX"+str(sboxNum)+": ")
    print(bestKeys)
    sboxNum += 1