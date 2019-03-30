import re
import math
import numpy as np
exampleNetlist = """*netlist example 1
R1 1 0 5
G2 1 0 1 2 2
R3 1 2 6
R4 2 0 8
Is5 0 2 10
Vs6 3 2 5
R8 3 4 10
E7 4 0 1 2 3
"""
expoDic = {
    'F': 1e-15,
    'P': 1e-12,
    'N': 1e-9,
    'U': 1e-6,
    'M': 1e-3,
    'K': 1e3,
    'MEG': 1e6,
    'G': 1e9,
    'T': 1e12
}

parseType = {
    'R': 0,'L': 0,'C': 0, #RLC
    'E': 1,'F': 1,'G': 1,'H': 1, # Control Source
    'D': 2, # Diode
    'V': 3, 'I': 3, # source
    'M': 4
}

# give all devices a initial status
def initDeviceParams(deviceType, deviceName = None, connectionPoints = None):
    # print(deviceType)
    if parseType[deviceType] == 0:
        pass
    elif parseType[deviceType] == 1:
        return {
            'deviceType': deviceType,
            'name': deviceName,
            'connectionPoints': connectionPoints,
        }
    elif parseType[deviceType] == 2:
        pass
    elif parseType[deviceType] == 3:
        return {
            'deviceType': deviceType,
            'name': deviceName,
            'connectionPoints': connectionPoints,
            # 'timeFunctionType': None,
            # 'timeFunctionTypeParam': None,
            # 'ACParams': None,
            # 'DCParams': None
        }
    elif parseType[deviceType] == 4:
        return{
            'deviceType': deviceType,
            'name': deviceName,
            'connectionPoints': connectionPoints, # d g s b
            # 'MNAME': None,
            # 'L': None,
            # 'W': None,
            # 'AD': None,
            # 'AS': None,
            # 'PD': None,
            # 'PS': None,
            # 'NRD': None,
            # 'NRS': None
        }

# parse the numbers written in spice's style (like 1k, 1m ... )
def stringToNum(string):
    matchResult = re.match(r'(-?[0-9]+\.?[0-9]*)([FPNUMKGT])?(MEG)?(DB)?([A-Z]*)', string)
    # print(string)
    if matchResult:
        stringParsedTuple = matchResult.groups()
        num = float(stringParsedTuple[0])
        if stringParsedTuple[1]:
            num = num * expoDic[stringParsedTuple[1]]
        elif stringParsedTuple[2]:
            num = num * expoDic[stringParsedTuple[2]]
        elif stringParsedTuple[3]:
            num = 20 * math.log(num, 10)
        # print('matchResult', stringParsedTuple, num)
        return num
    return string

def repl (matched):
    return matched.group(1) + matched.group(3)

def stripSpaceInParentheseWithComma (s):
    matchResult = re.sub(r'([(][0-9A-Z]*,)(\s*)([0-9A-Z]*[)])', repl, s)
    return matchResult

def stripSpaceAroundEqualSign (s):
    matchResult = re.sub(r'\s*=\s*', lambda x: '=', s)
    # print(matchResult)
    return matchResult

def deleteCharsInString (chars, _string):
    for char in chars:
        _string = _string.replace(char, ' ')
    return _string

# expand n * n matrix to n+1 * n+1 
def expandMatrix(matrix, num):
    (height, width) = matrix.shape
    matrix = np.hstack((matrix, np.zeros((height, num))))
    matrix = np.vstack((matrix, np.zeros((num, width + num))))
    return matrix