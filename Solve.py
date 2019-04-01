import numpy as np
from Device import *
import copy
# generate the MNA stamps and solve the matrix
class Solve:
    def __init__(self, nodeDict, deviceList, commandList, devices):
        self.nodeDict = nodeDict
        self.deviceList = deviceList
        self.commandList = commandList
        self.devices = devices

        self.length = len(self.nodeDict)
        self.stampMatrix = np.zeros((self.length, self.length))
        self.RHS = np.zeros((self.length, 1))
        self.LHS = np.zeros((self.length, 1))

        self.appendLine = {}

    def stamping(self):
        # generate the MNA matrix by calling load function in each device
        for device in self.devices:
            self.stampMatrix, self.RHS, self.appendLine = device.load(self.stampMatrix, self.RHS, self.appendLine)
        # print and solve   
        print('stampMatrix\n', self.stampMatrix[1:, 1:])
        print('RHS\n', self.RHS[1:])
        x = np.linalg.solve(self.stampMatrix[1:, 1:], self.RHS[1:])
        # x = np.linalg.solve(self.stampMatrix, self.RHS)
        # print('stampMatrix\n', self.stampMatrix, self.RHS)
        revNodeDict = dict((v, k) for  k,v in self.nodeDict.items())
        revAppendLine = dict((v, k) for  k,v in self.appendLine.items())
        print('node map\n', self.nodeDict)
        print('appendLine\n', self.appendLine)
        print('result\n', x)
        
        for k, v in revNodeDict.items():
            if k == 0:
                continue
            print('node', v, ' = ', x[k - 1][0])
        for k , v in revAppendLine.items():
            print('I%s  = %lf' % (v, x[k - 1][0] ))
    
    def stampingBE(self):
        # generate the unchangeable MNA matrix
        step = 0.1
        for device in self.devices:
            # if device.type == 'C' or device.type == 'L':
            self.stampMatrix, self.RHS, self.appendLine = device.loadBEMatrix(self.stampMatrix, self.RHS, self.appendLine, step)
        #初始状态都为0？
        print('stamp matrix', self.stampMatrix)
        self.tranValue = np.zeros((1, self.stampMatrix.shape[1] - 1))

        for i in range(10):
            tmpRHS = copy.deepcopy(self.RHS)
            for device in self.devices:
                tmpRHS = device.loadBERHS(self.stampMatrix, tmpRHS, self.appendLine, step, self.tranValue[-1])

            # print(self.stampMatrix)
            x = np.linalg.solve(self.stampMatrix[1:, 1:], tmpRHS[1:])
            # print(x.shape, self.tranValue.reshape((1,)).shape.)
            self.tranValue = np.append(self.tranValue, x.T, 0)

        print(self.tranValue)
        print('node map\n', self.nodeDict)
