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
            print('I%s = %lf' % (v, x[k - 1][0] ))
    
    def addVoltageToInit(self, src, val, init):
        # in order to avoid singular matrix, I give the inital result a corresponding voltage
        for device in self.devices:
            if device.name == src: # a voltage source need to be sweeped
                init[device.NPlus] = val
            elif device.type == 'V':
                init[device.NPlus] = device.value

    def stampingDC(self, src, start, stop, incr, sweep = {}):
        print(sweep)
        if sweep.__contains__('src2'):
            src2 = sweep['src2']
            val2 = sweep['val2']
        else:
            src2 = ''
            val2 = None
        print('src2', src2, val2)
        arr = np.arange(start, stop, incr)
        for device in self.devices:
            if not (device.type == 'D' or device.type == 'M'):
                self.stampMatrix, self.RHS, self.appendLine = device.loadDC(self.stampMatrix, self.RHS, self.appendLine)
        self.DCValue = np.zeros((1, self.stampMatrix.shape[1]))


        self.stampMatrix = np.zeros((self.length, self.length))
        self.RHS = np.zeros((self.length, 1))
        # self.appendLine = {}

        # for device in self.devices:
        #     # if device.name == src.upper():
        #     #     self.stampMatrix, self.RHS, self.appendLine = device.loadDCMatrix(self.stampMatrix, self.RHS, self.appendLine, val)
        #     if not ((device.type == 'D' or device.type == 'M') or device.name == src.upper()):
        #         print(device.name)
        #         self.stampMatrix, self.RHS, self.appendLine = device.load(self.stampMatrix, self.RHS, self.appendLine)
        #         # self.RHS, self.appendLine = device.loadDCRHS(self.stampMatrix, self.RHS, self.appendLine)
        result = []
        # print(self.stampMatrix, self.RHS)
        for val in arr:
            error = 100
            x_ = self.DCValue[-1]
            self.addVoltageToInit(src, val, x_)
            # x_[1] = 2
            # x_[2] = val
            # print('x_', x_)
            while abs(error) > 1e-5:
                stampMatrixWithNonlinear = copy.deepcopy(self.stampMatrix)
                tmpRHS = copy.deepcopy(self.RHS)
                RHSAppendLine = {}  
                for device in self.devices:
                    if device.name == src.upper():
                        # print(device.name, val)
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadDC(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, lastValue = x_, dcValue = val)
                    elif device.name == src2.upper():
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadDC(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, lastValue = x_, dcValue = val2)
                    else:
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadDC(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, lastValue = x_, dcValue = None)
                # for device in self.devices:
                #     if device.name == src.upper():
                #         # self.stampMatrix, self.RHS, self.appendLine = device.load(self.stampMatrix, self.RHS, self.appendLine, val)
                #         stampMatrixWithNonlinear, tmpRHS, self.appendLine = device.loadDCMatrix(stampMatrixWithNonlinear, tmpRHS, self.appendLine, lastValue = xnoInterate, dcValue = val)
                #     elif device.type == 'D' or device.type == 'M':
                #         stampMatrixWithNonlinear, tmpRHS, self.appendLine = device.loadDCMatrix(stampMatrixWithNonlinear, tmpRHS, self.appendLine, lastValue = x_)
                # for device in self.devices:
                #     if device.name == src.upper():
                #         # self.stampMatrix, self.RHS, self.appendLine = device.load(self.stampMatrix, self.RHS, self.appendLine, val)
                #         tmpRHS, RHSAppendLine = device.loadDCRHS(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, dcValue = val)
                #     elif device.type == 'D' or device.type == 'M':
                #         tmpRHS, RHSAppendLine = device.loadDCRHS(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, x_)
                #     else:
                #         tmpRHS, RHSAppendLine = device.loadDCRHS(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, xnoInterate)
                # print('stampMatrixWithNonlinear', stampMatrixWithNonlinear[1:, 1:])
                # print(tmpRHS[1:])
                x = np.linalg.solve(stampMatrixWithNonlinear[1:, 1:], tmpRHS[1:])
                x = np.insert(x, 0, np.array([0]))
                error = np.sum(x - x_)
                # print('sove', x)
                # print('error', error)
                x_ = x
            self.DCValue = np.append(self.DCValue, [x_.T], 0)
        # print('dcvalue', self.DCValue)
        return self.DCValue, self.appendLine


    #  solve TRAN with BE
    def stampingBE(self, step, stop):
        print(self.deviceList)
        # generate the unchangeable MNA matrix without nonlinear device
        for device in self.devices:
            if not (device.type == 'D' or device.type == 'M'):
                self.stampMatrix, self.RHS, self.appendLine = device.loadBEMatrix(self.stampMatrix, self.RHS, self.appendLine, step)
        # print('stamp matrix', self.stampMatrix)
        self.tranValueBE = np.zeros((1, self.stampMatrix.shape[1]))

        for i in range(stop):
            error = 100
            # x_ = np.zeros((len(self.stampMatrix), 1))
            x_ = self.tranValueBE[-1]
            xnoInterate = self.tranValueBE[-1]
            while abs(error) > 1e-5:
                # print(x_)
                # add the nonlinear device
                stampMatrixWithNonlinear = copy.deepcopy(self.stampMatrix)
                tmpRHS = copy.deepcopy(self.RHS)
                RHSAppendLine = {}  
                for device in self.devices:
                    if device.type == 'D' or device.type == 'M':
                        # print(2)
                        stampMatrixWithNonlinear, tmpRHS, self.appendLine = device.loadBEMatrix(stampMatrixWithNonlinear, tmpRHS, self.appendLine, step, x_)
                for device in self.devices:
                    if device.type == 'D' or device.type == 'M':
                        # print(3)
                        tmpRHS, RHSAppendLine = device.loadBERHS(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, step, x_)
                    else:
                        tmpRHS, RHSAppendLine = device.loadBERHS(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, step, xnoInterate)
                # print(stampMatrixWithNonlinear, '\n', self.stampMatrix, '\n' ,tmpRHS)
                x = np.linalg.solve(stampMatrixWithNonlinear[1:, 1:], tmpRHS[1:])
                x = np.insert(x, 0, np.array([0]))
                error = np.sum(x - x_)
                # print('sove', x)
                # print('error',i , error)
                x_ = x
            self.tranValueBE = np.append(self.tranValueBE, [x_.T], 0)

        print(self.tranValueBE)
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
