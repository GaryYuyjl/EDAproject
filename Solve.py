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

    # solve the DC
    def stamping(self):
        # generate the MNA matrix by calling load function in each device
        for device in self.devices:
            self.stampMatrix, self.RHS, self.appendLine = device.load(self.stampMatrix, self.RHS, self.appendLine)
        x = np.linalg.solve(self.stampMatrix[1:, 1:], self.RHS[1:])
        # x = np.linalg.solve(self.stampMatrix, self.RHS)
        # print('stampMatrix\n', self.stampMatrix, self.RHS)
        revNodeDict = dict((v, k) for  k,v in self.nodeDict.items())
        revAppendLine = dict((v, k) for  k,v in self.appendLine.items())
        
        for k, v in revNodeDict.items():
            if k == 0:
                continue
            print('node', v, ' = ', x[k - 1][0])
        for k , v in revAppendLine.items():
            print('I%s  = %lf' % (v, x[k - 1][0] ))
    
    #  solve TRAN with BE
    def stampingBE(self, step, stop):
        # generate the unchangeable MNA matrix
        for device in self.devices:
            self.stampMatrix, self.RHS, self.appendLine = device.loadBEMatrix(self.stampMatrix, self.RHS, self.appendLine, step)
        # print('stamp matrix', self.stampMatrix)
        self.tranValueBE = np.zeros((1, self.stampMatrix.shape[1]))

        for i in range(stop):
            RHSAppendLine = {}
            tmpRHS = copy.deepcopy(self.RHS)
            for device in self.devices:
                tmpRHS, RHSAppendLine = device.loadBERHS(self.stampMatrix, tmpRHS, RHSAppendLine, step, self.tranValueBE[-1])

            x = np.linalg.solve(self.stampMatrix[1:, 1:], tmpRHS[1:])
            x = np.insert(x, 0, np.array([0]))
            self.tranValueBE = np.append(self.tranValueBE, [x.T], 0)

        # print(self.tranValueBE)
        # print('node map\n', self.nodeDict)
        # print('appendLine\n', self.appendLine)
        return self.tranValueBE, self.appendLine

    # solve TRAN with FE
    def stampingFE(self, step, stop):
        # generate the unchangeable MNA matrix
        for device in self.devices:
            self.stampMatrix, self.RHS, self.appendLine = device.loadFEMatrix(self.stampMatrix, self.RHS, self.appendLine, step)
        # print('stamp matrix', self.stampMatrix)
        self.tranValueFE = np.zeros((1, self.stampMatrix.shape[1]))

        for i in range(stop):
            RHSAppendLine = {}
            tmpRHS = copy.deepcopy(self.RHS)
            for device in self.devices:
                tmpRHS, RHSAppendLine = device.loadFERHS(self.stampMatrix, tmpRHS, RHSAppendLine, step, self.tranValueFE[-1])

            # print(self.stampMatrix)
            x = np.linalg.solve(self.stampMatrix[1:, 1:], tmpRHS[1:])
            x = np.insert(x, 0, np.array([0]))
            self.tranValueFE = np.append(self.tranValueFE, [x.T], 0)

        # print(self.tranValueFE)
        # print('node map\n', self.nodeDict)
        # print('appendLine\n', self.appendLine)
        return self.tranValueFE, self.appendLine
    
    # solve TRAN with TR
    def stampingTR(self, step, stop):
        # generate the unchangeable MNA matrix
        for device in self.devices:
            self.stampMatrix, self.RHS, self.appendLine = device.loadTRMatrix(self.stampMatrix, self.RHS, self.appendLine, step)
        # print('stamp matrix', self.stampMatrix)
        self.tranValueTR = np.zeros((1, self.stampMatrix.shape[1]))

        for i in range(stop):
            RHSAppendLine = {}
            tmpRHS = copy.deepcopy(self.RHS)
            for device in self.devices:
                tmpRHS, RHSAppendLine = device.loadTRRHS(self.stampMatrix, tmpRHS, RHSAppendLine, step, self.tranValueTR[-1])

            # print(self.stampMatrix)
            x = np.linalg.solve(self.stampMatrix[1:, 1:], tmpRHS[1:])
            x = np.insert(x, 0, np.array([0]))
            self.tranValueTR = np.append(self.tranValueTR, [x.T], 0)
        # print('node map\n', self.nodeDict)
        # print('appendLine\n', self.appendLine)
        return self.tranValueTR, self.appendLine
