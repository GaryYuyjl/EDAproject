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

    def clear(self):
        self.tranValueBE = np.zeros((1, self.stampMatrix.shape[1]))
        self.stampMatrix = np.zeros((self.length, self.length))
        self.RHS = np.zeros((self.length, 1))
        self.appendLine = {}


    # solve the DC
    def stamping(self, printMNA = False):
        # generate the MNA matrix by calling load function in each device
        for device in self.devices:
            self.stampMatrix, self.RHS, self.appendLine = device.load(self.stampMatrix, self.RHS, self.appendLine)
        self.iteration = np.zeros((1, self.stampMatrix.shape[1]))
        self.stampMatrix = np.zeros((self.length, self.length))
        self.RHS = np.zeros((self.length, 1))

        error = 100
        x_ = self.iteration[-1]
        count = 0
        while abs(error) > 1e-10:
            count += 1
            if count > 1000:
                print('error')
                break
            stampMatrix = copy.deepcopy(self.stampMatrix)
            tmpRHS = copy.deepcopy(self.RHS)
            appendLine = {}  

            for device in self.devices:
                stampMatrix, tmpRHS, appendLine = device.load(stampMatrix, tmpRHS, appendLine, lastValue = x_)
            # print(stampMatrix, tmpRHS)
            if printMNA:
                print('iteration', len(self.iteration), '\n', stampMatrix)
            x = np.linalg.solve(stampMatrix[1:, 1:], tmpRHS[1:])
            x = np.insert(x, 0, np.array([0]))
            error = np.sum(x - x_)
            x_ = x
            self.iteration = np.append(self.iteration, [x_.T], 0)
        # x = np.linalg.solve(self.stampMatrix, self.RHS)
        # print('stampMatrix\n', self.stampMatrix, self.RHS, self.iteration)
        print('result: \n', self.iteration[-1])        
        return self.iteration

    # to give the inital value for the iteration
    def addVoltageToInit(self, src, val, init):
        # in order to avoid singular matrix, I give the inital result a corresponding voltage
        # for k, v in enumerate(init):
        #     if v == 0:
                # init[k] = 0.1
        for device in self.devices:
            if device.name == src and device.type == 'V': # a voltage source need to be sweeped
                init[device.NPlus] = val
            elif device.type == 'V':
                init[device.NPlus] = device.value

    def stampingDC(self, src, start, stop, incr, sweep = {}):
        # print(sweep)
        if sweep.__contains__('src2'):
            src2 = sweep['src2']
            val2 = sweep['val2']
        else:
            src2 = ''
            val2 = None
        # print('src2', src2, val2)
        arr = np.arange(start, stop, incr)
        print(arr)
        for device in self.devices:
            if not (device.type == 'D' or device.type == 'M'):
                self.stampMatrix, self.RHS, self.appendLine = device.loadDC(self.stampMatrix, self.RHS, self.appendLine)
        self.DCValue = np.zeros((1, self.stampMatrix.shape[1]))
        self.stampMatrix = np.zeros((self.length, self.length))
        self.RHS = np.zeros((self.length, 1))
        result = []
        # print(self.stampMatrix, self.RHS)
        for val in arr:
            error = 100
            x_ = self.DCValue[-1]
            
            # handle nodeset
            hasNodeset = False
            for command in self.commandList:
                if command['type'] == 'NODESET':
                    hasNodeset = True
                    for key in command:
                        if self.nodeDict.__contains__(key):
                            x_[self.nodeDict[key]] = stringToNum(command[key])
            if not hasNodeset:
                self.addVoltageToInit(src, val, x_)
            # x_[0] = 0
            # x_[2] = val
            # print('x_', x_)
            count = 0
            while abs(error) > 1e-5:
                count += 1
                if count > 1000:
                    print('wrong')
                    break

                stampMatrixWithNonlinear = copy.deepcopy(self.stampMatrix)
                tmpRHS = copy.deepcopy(self.RHS)
                RHSAppendLine = {}  
                for device in self.devices:
                    if device.name == src.upper():
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadDC(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, lastValue = x_, appointValue = val)
                    elif device.name == src2.upper():
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadDC(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, lastValue = x_, appointValue = val2)
                    else:
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadDC(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, lastValue = x_, appointValue = None)
                # print(stampMatrixWithNonlinear[1:, 1:], tmpRHS[1:])
                x = np.linalg.solve(stampMatrixWithNonlinear[1:, 1:], tmpRHS[1:])
                x = np.insert(x, 0, np.array([0]))
                error = np.sum(x - x_)
                # print('sove', x)
                # print('error', error)
                x_ = x
            self.DCValue = np.append(self.DCValue, [x_.T], 0)

        print('dcvalue', self.DCValue)
        return self.DCValue, self.appendLine, arr

    #  solve TRAN with BE
    def stampingBEWithStepControl(self, step, stop, start):
        # stopTime = step * stop
        stopTime = stop
        # how to define the epsilon
        epsilon = step * 10000
        nowTime = 0
        times = [nowTime]
        # to get more points for the time step control
        fakeStep = step / 16
        fakeTranValue, fakeAppendLine, fakeTimes = self.stampingBE(fakeStep, stop * 16)

        self.clear()
        
        print(self.stampMatrix, self.RHS, self.appendLine)
        for device in self.devices:
            if not (device.type == 'D' or device.type == 'M'):
                self.stampMatrix, self.RHS, self.appendLine = device.loadBE(self.stampMatrix, self.RHS, self.appendLine, step)
        self.tranValueBE = np.zeros((1, self.stampMatrix.shape[1]))
        self.stampMatrix = np.zeros((self.length, self.length))
        self.RHS = np.zeros((self.length, 1))

        # for i in range(stop):
        # transient BE
        while nowTime < stopTime:
            error = 100
            # x_ = np.zeros((len(self.stampMatrix), 1))
            x_ = self.tranValueBE[-1]
            xnoInterate = self.tranValueBE[-1]

            # add time step control
            tmpStep = step

            # Time step control
            while True:
                needChangeStepFlag = False
                for src in self.devices:
                    if src.type == 'V':
                        self.addVoltageToInit(src.name, src.value, x_)
                count = 0
                # N-R
                while abs(error) > 1e-3:
                    count += 1
                    if count > 1000:
                        print('wrong')
                        break

                    # add the nonlinear device
                    stampMatrixWithNonlinear = copy.deepcopy(self.stampMatrix)
                    tmpRHS = copy.deepcopy(self.RHS)
                    RHSAppendLine = {}  
                    for device in self.devices:
                        if device.type == 'D' or device.type == 'M':
                            # print(3)
                            stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadBE(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, tmpStep, t = nowTime, lastValue= x_)
                        else:
                            stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadBETimeStepControl(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, tmpStep, fakeTimes, fakeTranValue, t = nowTime, lastValue= xnoInterate)
                    x = np.linalg.solve(stampMatrixWithNonlinear[1:, 1:], tmpRHS[1:])
                    x = np.insert(x, 0, np.array([0]))
                    error = np.sum(x - x_)
                    # print('sove', x)
                    # print('error',i , error)
                    x_ = x
                
                # determine this step is available or not
                tnplus1 = x_
                tn = self.tranValueBE[-1]
                for device in self.devices:
                    if device.type == 'L':
                        if device.getVoltage(tnplus1) - device.getVoltage(tn) == 0:
                            continue
                        right = 2 * device.value / abs(device.getVoltage(tnplus1) - device.getVoltage(tn)) * epsilon
                        left = tmpStep
                        if left > right:
                            needChangeStepFlag = True
                    elif device.type == 'C':
                        # print('tnplus1', tnplus1)
                        # print('tn', tn)
                        if device.getCurrent(tnplus1, self.nodeDict) - device.getCurrent(tn, self.nodeDict) == 0:
                            continue
                        right = 2 * device.value / abs(device.getCurrent(tnplus1, self.nodeDict) - device.getCurrent(tn, self.nodeDict)) * epsilon
                        left = tmpStep
                        if left > right:
                            needChangeStepFlag = True
                if not needChangeStepFlag:
                    break
                else:
                    tmpStep /= 2
                    print('need', tmpStep)
                    
            nowTime += tmpStep
            times.append(nowTime)
            self.tranValueBE = np.append(self.tranValueBE, [tnplus1.T], 0)
        return self.tranValueBE, self.appendLine, times

    #  solve TRAN with BE
    def stampingBE(self, step, stop, start):
        nowTime = start
        times = [nowTime]
        print(self.stampMatrix, self.RHS, self.appendLine)
        for device in self.devices:
            if not (device.type == 'D' or device.type == 'M'):
                self.stampMatrix, self.RHS, self.appendLine = device.loadBE(self.stampMatrix, self.RHS, self.appendLine, step)
        # print('stamp matrix', self.stampMatrix)
        self.tranValueBE = np.zeros((1, self.stampMatrix.shape[1]))
        self.stampMatrix = np.zeros((self.length, self.length))
        self.RHS = np.zeros((self.length, 1))
        while nowTime <= stop:
            error = 100
            # x_ = np.zeros((len(self.stampMatrix), 1))
            x_ = self.tranValueBE[-1]
            xnoInterate = self.tranValueBE[-1]
            for src in self.devices:
                if src.type == 'V':
                    self.addVoltageToInit(src.name, src.value, x_)
            count = 0
            while abs(error) > 1e-3:
                count += 1
                if count > 1000:
                    print('wrong')
                    break

                # add the nonlinear device
                stampMatrixWithNonlinear = copy.deepcopy(self.stampMatrix)
                tmpRHS = copy.deepcopy(self.RHS)
                RHSAppendLine = {}  
                for device in self.devices:
                    if device.type == 'D' or device.type == 'M':
                        # print(3)
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadBE(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, step, t = nowTime, lastValue= x_)
                    else:
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadBE(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, step, t = nowTime, lastValue= xnoInterate)
                x = np.linalg.solve(stampMatrixWithNonlinear[1:, 1:], tmpRHS[1:])
                x = np.insert(x, 0, np.array([0]))
                error = np.sum(x - x_)
                # print('sove', x)
                # print('error',i , error)
                x_ = x
            self.tranValueBE = np.append(self.tranValueBE, [x_.T], 0)
            nowTime += step
            times.append(nowTime)
        print(' self.tranValueBE',self.tranValueBE)
        # print('node map\n', self.nodeDict)
        # print('appendLine\n', self.appendLine)
        return self.tranValueBE, self.appendLine, times

    def stampingFEWithStepControl(self, step, stop):
        stopTime = stop
        # how to define the epsilon
        epsilon = step * 10000
        nowTime = 0
        times = [nowTime]
        # to get more points for the time step control
        fakeStep = step / 16
        fakeTranValue, fakeAppendLine, fakeTimes = self.stampingFE(fakeStep, stop * 16)

        self.clear()
        
        print(self.stampMatrix, self.RHS, self.appendLine)
        for device in self.devices:
            if not (device.type == 'D' or device.type == 'M'):
                self.stampMatrix, self.RHS, self.appendLine = device.loadFE(self.stampMatrix, self.RHS, self.appendLine, step)
        self.tranValueFE = np.zeros((1, self.stampMatrix.shape[1]))
        self.stampMatrix = np.zeros((self.length, self.length))
        self.RHS = np.zeros((self.length, 1))

        # for i in range(stop):
        # transient FE
        while nowTime < stopTime:
            error = 100
            # x_ = np.zeros((len(self.stampMatrix), 1))
            x_ = self.tranValueFE[-1]
            xnoInterate = self.tranValueFE[-1]

            # add time step control
            tmpStep = step

            # Time step control
            while True:
                needChangeStepFlag = False
                for src in self.devices:
                    if src.type == 'V':
                        self.addVoltageToInit(src.name, src.value, x_)
                count = 0
                # N-R
                while abs(error) > 1e-3:
                    count += 1
                    if count > 1000:
                        print('wrong')
                        break

                    # add the nonlinear device
                    stampMatrixWithNonlinear = copy.deepcopy(self.stampMatrix)
                    tmpRHS = copy.deepcopy(self.RHS)
                    RHSAppendLine = {}  
                    for device in self.devices:
                        if device.type == 'D' or device.type == 'M':
                            # print(3)
                            stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadFE(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, tmpStep, t = nowTime, lastValue= x_)
                        else:
                            stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadFETimeStepControl(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, tmpStep, fakeTimes, fakeTranValue, t = nowTime, lastValue= xnoInterate)
                    x = np.linalg.solve(stampMatrixWithNonlinear[1:, 1:], tmpRHS[1:])
                    x = np.insert(x, 0, np.array([0]))
                    error = np.sum(x - x_)
                    # print('sove', x)
                    # print('error',i , error)
                    x_ = x
                
                # determine this step is available or not
                tnplus1 = x_
                tn = self.tranValueFE[-1]
                for device in self.devices:
                    if device.type == 'L':
                        if device.getVoltage(tnplus1) - device.getVoltage(tn) == 0:
                            continue
                        right = 2 * device.value / abs(device.getVoltage(tnplus1) - device.getVoltage(tn)) * epsilon
                        left = tmpStep
                        if left > right:
                            needChangeStepFlag = True
                    elif device.type == 'C':
                        # print('tnplus1', tnplus1)
                        # print('tn', tn)
                        if device.getCurrent(tnplus1, self.nodeDict) - device.getCurrent(tn, self.nodeDict) == 0:
                            continue
                        right = 2 * device.value / abs(device.getCurrent(tnplus1, self.nodeDict) - device.getCurrent(tn, self.nodeDict)) * epsilon
                        left = tmpStep
                        if left > right:
                            needChangeStepFlag = True
                if not needChangeStepFlag:
                    break
                else:
                    tmpStep /= 2
                    print('need', tmpStep)
                    
            nowTime += tmpStep
            times.append(nowTime)
            self.tranValueFE = np.append(self.tranValueFE, [tnplus1.T], 0)
        return self.tranValueFE, self.appendLine, times

    #  solve TRAN with FE
    def stampingFE(self, step, stop):
        nowTime = 0
        times = [nowTime]
        for device in self.devices:
            if not (device.type == 'D' or device.type == 'M'):
                self.stampMatrix, self.RHS, self.appendLine = device.loadFE(self.stampMatrix, self.RHS, self.appendLine, step)
        # print('stamp matrix', self.stampMatrix)
        self.tranValueFE = np.zeros((1, self.stampMatrix.shape[1]))
        self.stampMatrix = np.zeros((self.length, self.length))
        self.RHS = np.zeros((self.length, 1))

        while nowTime <= stop:
            error = 100
            # x_ = np.zeros((len(self.stampMatrix), 1))
            x_ = self.tranValueFE[-1]
            xnoInterate = self.tranValueFE[-1]
            for src in self.devices:
                if src.type == 'V':
                    self.addVoltageToInit(src.name, src.value, x_)
            count = 0
            while abs(error) > 1e-3:
                count += 1
                if count > 1000:
                    print('wrong')
                    break

                # print(x_)
                # add the nonlinear device
                stampMatrixWithNonlinear = copy.deepcopy(self.stampMatrix)
                tmpRHS = copy.deepcopy(self.RHS)
                RHSAppendLine = {}  
                for device in self.devices:
                    if device.type == 'D' or device.type == 'M':
                        # print(3)
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadFE(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, step, t = nowTime, lastValue= x_)
                    else:
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadFE(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, step, t = nowTime, lastValue= xnoInterate)
                x = np.linalg.solve(stampMatrixWithNonlinear[1:, 1:], tmpRHS[1:])
                x = np.insert(x, 0, np.array([0]))
                error = np.sum(x - x_)
                # print('sove', x)
                # print('error',i , error)
                x_ = x
            self.tranValueFE = np.append(self.tranValueFE, [x_.T], 0)
            nowTime += step
            times.append(nowTime)
        print(self.tranValueFE)
        # print('node map\n', self.nodeDict)
        # print('appendLine\n', self.appendLine)
        return self.tranValueFE, self.appendLine, times

    def stampingTRWithStepControl(self, step, stop):
        stopTime = stop
        # how to define the epsilon??
        epsilon = step * 10000
        nowTime = 0
        times = [nowTime]
        # to get more points for the time step control
        fakeStep = step / 16
        fakeTranValue, fakeAppendLine, fakeTimes = self.stampingTR(fakeStep, stop * 16)

        self.clear()
        
        print(self.stampMatrix, self.RHS, self.appendLine)
        for device in self.devices:
            if not (device.type == 'D' or device.type == 'M'):
                self.stampMatrix, self.RHS, self.appendLine = device.loadTR(self.stampMatrix, self.RHS, self.appendLine, step)
        self.tranValueTR = np.zeros((1, self.stampMatrix.shape[1]))
        self.stampMatrix = np.zeros((self.length, self.length))
        self.RHS = np.zeros((self.length, 1))

        # for i in range(stop):
        # transient TR
        while nowTime < stopTime:
            error = 100
            # x_ = np.zeros((len(self.stampMatrix), 1))
            x_ = self.tranValueTR[-1]
            x__ = self.tranValueTR[-1]
            step_ = step
            xnoInterate = self.tranValueTR[-1]

            # add time step control
            tmpStep = step

            # Time step control
            while True:
                needChangeStepFlag = False
                for src in self.devices:
                    if src.type == 'V':
                        self.addVoltageToInit(src.name, src.value, x_)
                count = 0
                # N-R
                while abs(error) > 1e-3:
                    count += 1
                    if count > 1000:
                        print('wrong')
                        break

                    # add the nonlinear device
                    stampMatrixWithNonlinear = copy.deepcopy(self.stampMatrix)
                    tmpRHS = copy.deepcopy(self.RHS)
                    RHSAppendLine = {}  
                    for device in self.devices:
                        if device.type == 'D' or device.type == 'M':
                            # print(3)
                            stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadTR(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, tmpStep, t = nowTime, lastValue= x_)
                        else:
                            stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadTRTimeStepControl(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, tmpStep, fakeTimes, fakeTranValue, t = nowTime, lastValue= xnoInterate)
                    x = np.linalg.solve(stampMatrixWithNonlinear[1:, 1:], tmpRHS[1:])
                    x = np.insert(x, 0, np.array([0]))
                    error = np.sum(x - x_)
                    # print('sove', x)
                    # print('error',i , error)
                    x_ = x
                    x__ = x_
                
                # determine this step is available or not
                tnplus1 = x_
                tn = self.tranValueTR[-1]
                for device in self.devices:
                    if device.type == 'L':
                        if device.getVoltage(tnplus1) - device.getVoltage(tn) == 0:
                            continue
                        right = 2 * device.value / abs(device.getVoltage(tnplus1) - device.getVoltage(tn)) * epsilon
                        left = tmpStep
                        if left > right:
                            needChangeStepFlag = True
                    elif device.type == 'C':
                        # print('tnplus1', tnplus1)
                        # print('tn', tn)
                        # if device.getCurrent(tnplus1, self.nodeDict) - device.getCurrent(tn, self.nodeDict) == 0:
                        #     continue
                        # right = 2 * device.value / abs(device.getCurrent(tnplus1, self.nodeDict) - device.getCurrent(tn, self.nodeDict)) * epsilon
                        denom = 2 / tmpStep * (2 / tmpStep * (device.getCurrent(tn, self.nodeDict)))
                        # right = (12 * epsilon * )
                        left = tmpStep
                        if left > right:
                            needChangeStepFlag = True
                if not needChangeStepFlag:
                    break
                    step_ = tmpStep
                else:
                    tmpStep /= 2
                    print('need', tmpStep)
                    
            nowTime += tmpStep
            times.append(nowTime)
            self.tranValueTR = np.append(self.tranValueTR, [tnplus1.T], 0)
        return self.tranValueTR, self.appendLine, times

    #  solve TRAN with TR
    def stampingTR(self, step, stop):
        nowTime = 0
        times = [nowTime]
        for device in self.devices:
            if not (device.type == 'D' or device.type == 'M'):
                self.stampMatrix, self.RHS, self.appendLine = device.loadTR(self.stampMatrix, self.RHS, self.appendLine, step)
        # print('stamp matrix', self.stampMatrix)
        self.tranValueTR = np.zeros((1, self.stampMatrix.shape[1]))
        self.stampMatrix = np.zeros((self.length, self.length))
        self.RHS = np.zeros((self.length, 1))

        while nowTime <= stop:
            error = 100
            # x_ = np.zeros((len(self.stampMatrix), 1))
            x_ = self.tranValueTR[-1]
            xnoInterate = self.tranValueTR[-1]
            for src in self.devices:
                if src.type == 'V':
                    self.addVoltageToInit(src.name, src.value, x_)
            count = 0
            while abs(error) > 1e-3:
                count += 1
                if count > 1000:
                    print('wrong')
                    break

                # print(x_)
                # add the nonlinear device
                stampMatrixWithNonlinear = copy.deepcopy(self.stampMatrix)
                tmpRHS = copy.deepcopy(self.RHS)
                RHSAppendLine = {}  
                for device in self.devices:
                    if device.type == 'D' or device.type == 'M':
                        # print(3)
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadTR(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, step, t = nowTime, lastValue= x_)
                    else:
                        stampMatrixWithNonlinear, tmpRHS, RHSAppendLine = device.loadTR(stampMatrixWithNonlinear, tmpRHS, RHSAppendLine, step, t = nowTime, lastValue= xnoInterate)
                x = np.linalg.solve(stampMatrixWithNonlinear[1:, 1:], tmpRHS[1:])
                x = np.insert(x, 0, np.array([0]))
                error = np.sum(x - x_)
                # print('sove', x)
                # print('error',i , error)
                x_ = x
            self.tranValueTR = np.append(self.tranValueTR, [x_.T], 0)
            nowTime += step
            times.append(nowTime)
        print(self.tranValueTR)
        # print('node map\n', self.nodeDict)
        # print('appendLine\n', self.appendLine)
        return self.tranValueTR, self.appendLine, times
