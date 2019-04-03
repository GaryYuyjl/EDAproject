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
        # print and solve   
        # print('stampMatrix\n', self.stampMatrix[1:, 1:])
        # print('RHS\n', self.RHS[1:])
        x = np.linalg.solve(self.stampMatrix[1:, 1:], self.RHS[1:])
        # x = np.linalg.solve(self.stampMatrix, self.RHS)
        # print('stampMatrix\n', self.stampMatrix, self.RHS)
        revNodeDict = dict((v, k) for  k,v in self.nodeDict.items())
        revAppendLine = dict((v, k) for  k,v in self.appendLine.items())
        # print('node map\n', self.nodeDict)
        # print('appendLine\n', self.appendLine)
        # print('result\n', x)
        
        for k, v in revNodeDict.items():
            if k == 0:
                continue
            print('node', v, ' = ', x[k - 1][0])
        for k , v in revAppendLine.items():
            print('I%s  = %lf' % (v, x[k - 1][0] ))
    
    #  solve TRAN with BE
    def stampingBE(self, step, stop):
        RHSAppendLine = {}
        # generate the unchangeable MNA matrix
        for device in self.devices:
            self.stampMatrix, self.RHS, self.appendLine = device.loadBEMatrix(self.stampMatrix, self.RHS, self.appendLine, step)
        # print('stamp matrix', self.stampMatrix)
        self.tranValueBE = np.zeros((1, self.stampMatrix.shape[1] - 1))

        for i in range(stop):
            tmpRHS = copy.deepcopy(self.RHS)
            for device in self.devices:
                tmpRHS, RHSAppendLine = device.loadBERHS(self.stampMatrix, tmpRHS, RHSAppendLine, step, np.insert(self.tranValueBE[-1], 0, np.array([0])))

            # print(self.stampMatrix)
            x = np.linalg.solve(self.stampMatrix[1:, 1:], tmpRHS[1:])
            # print(x.shape, self.tranValueBE.reshape((1,)).shape.)
            self.tranValueBE = np.append(self.tranValueBE, x.T, 0)

        # print(self.tranValueBE)
        # print('node map\n', self.nodeDict)
        # print('appendLine\n', self.appendLine)
        x = np.arange(0, stop * step, step) 
        return self.tranValueBE

    # solve TRAN with FE
    def stampingFE(self, step, stop):
        RHSAppendLine = {}
        # generate the unchangeable MNA matrix
        for device in self.devices:
            self.stampMatrix, self.RHS, self.appendLine = device.loadFEMatrix(self.stampMatrix, self.RHS, self.appendLine, step)
        # print('stamp matrix', self.stampMatrix)
        self.tranValueFE = np.zeros((1, self.stampMatrix.shape[1] - 1))

        for i in range(stop):
            tmpRHS = copy.deepcopy(self.RHS)
            for device in self.devices:
                tmpRHS, RHSAppendLine = device.loadFERHS(self.stampMatrix, tmpRHS, RHSAppendLine, step, np.insert(self.tranValueFE[-1], 0, np.array([0])))

            # print(self.stampMatrix)
            x = np.linalg.solve(self.stampMatrix[1:, 1:], tmpRHS[1:])
            # print(x.shape, self.tranValueFE.reshape((1,)).shape.)
            self.tranValueFE = np.append(self.tranValueFE, x.T, 0)

        # print(self.tranValueFE)
        # print('node map\n', self.nodeDict)
        # print('appendLine\n', self.appendLine)
        x = np.arange(0, stop * step, step) 
        return self.tranValueFE
    
    # solve TRAN with TRAP
    def stampingTRAP(self, step, stop):
        RHSAppendLine = {}
        # generate the unchangeable MNA matrix
        for device in self.devices:
            self.stampMatrix, self.RHS, self.appendLine = device.loadTRAPMatrix(self.stampMatrix, self.RHS, self.appendLine, step)
        # print('stamp matrix', self.stampMatrix)
        self.tranValueTRAP = np.zeros((1, self.stampMatrix.shape[1] - 1))

        for i in range(stop):
            tmpRHS = copy.deepcopy(self.RHS)
            for device in self.devices:
                tmpRHS, RHSAppendLine = device.loadTRAPRHS(self.stampMatrix, tmpRHS, RHSAppendLine, step, np.insert(self.tranValueTRAP[-1], 0, np.array([0])))

            # print(self.stampMatrix)
            x = np.linalg.solve(self.stampMatrix[1:, 1:], tmpRHS[1:])
            # print(x.shape, self.tranValueTRAP.reshape((1,)).shape.)
            self.tranValueTRAP = np.append(self.tranValueTRAP, x.T, 0)
        # print('node map\n', self.nodeDict)
        # print('appendLine\n', self.appendLine)
        x = np.arange(0, stop * step, step) 
        return self.tranValueTRAP
