from Util import *
# father class of all devices
class SuperDevice:
    def __init__(self, name, connectionPoints, _type):
        self.connectionPoints = connectionPoints
        self.NPlus = self.connectionPoints[0]
        self.NMinus = self.connectionPoints[1]
        self.name = name
        self.type = _type

    def load(self):
        pass

class Resistor(SuperDevice):
    def __init__(self, name, connectionPoints, value, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
    
    # load function will add this device to MNA matrix
    def load(self, stampMatrix, RHS, appendLine):
        stampMatrix[self.NPlus][self.NPlus] += 1 / self.value
        stampMatrix[self.NMinus][self.NPlus] -= 1 / self.value
        stampMatrix[self.NPlus][self.NMinus] -= 1 / self.value
        stampMatrix[self.NMinus][self.NMinus] += 1 / self.value
        return stampMatrix, RHS, appendLine
    
    def loadBEMatrix(self, stampMatrix, RHS, appendLine, step):
        stampMatrix[self.NPlus][self.NPlus] += 1 / self.value
        stampMatrix[self.NMinus][self.NPlus] -= 1 / self.value
        stampMatrix[self.NPlus][self.NMinus] -= 1 / self.value
        stampMatrix[self.NMinus][self.NMinus] += 1 / self.value
        return stampMatrix, RHS, appendLine
    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return RHS

class Capacitor(SuperDevice):
    def __init__(self, name, connectionPoints, value, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
    
    def load(self, stampMatrix, RHS, appendLine):
        stampMatrix[self.NPlus][self.NPlus] += self.value * 1j
        stampMatrix[self.NPlus][self.NMinus] -= self.value * 1j
        stampMatrix[self.NMinus][self.NPlus] -= self.value * 1j
        stampMatrix[self.NMinus][self.NMinus] += self.value * 1j
        return stampMatrix, RHS, appendLine

    def loadBEMatrix(self, stampMatrix, RHS, appendLine, h):
        # print('capacitor', self.value, h, stampMatrix)
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += self.value / h
        stampMatrix[index][self.NMinus] -= self.value / h
        stampMatrix[index][index] -= 1

        # # need to update
        # v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
        # RHS = np.vstack((RHS, np.array([self.value / h * v_tMinush]))) # add vc

        appendLine[self.name] = index
        return stampMatrix, RHS, appendLine

    def loadBERHS(self, stampMatrix, RHS, appendLine, h, lastValue):
        # index = len(RHS)
        # stampMatrix = expandMatrix(stampMatrix, 1)

        # stampMatrix[self.NPlus][index] += 1
        # stampMatrix[self.NMinus][index] -= 1
        # stampMatrix[index][self.NPlus] += self.value / h
        # stampMatrix[index][self.NMinus] -= self.value / h
        # stampMatrix[index][index] -= 1

        # print(RHS)
        # need to update
        v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
        add = np.array([[self.value / h * v_tMinush]])
        RHS = np.vstack((RHS, add)) # add vc

        return RHS

class Inductor(SuperDevice):
    def __init__(self, name, connectionPoints, value, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
    
    def load(self, stampMatrix, RHS, appendLine):
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += 1
        stampMatrix[index][self.NMinus] -= 1
        stampMatrix[index][index] -= self.value * 1j
        RHS = np.vstack((RHS, np.array([0]))) # add vc

        appendLine[self.name] = index
        return stampMatrix, RHS, appendLine

    def loadBEMatrix(self, stampMatrix, RHS, appendLine, h):
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += 1
        stampMatrix[index][self.NMinus] -= 1
        stampMatrix[index][index] -= self.value / h

        # # need to update
        # v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
        # RHS = np.vstack((RHS, np.array([self.value / h * v_tMinush]))) # add vc

        appendLine[self.name] = index
        return stampMatrix, RHS, appendLine

    def loadBERHS(self, stampMatrix, RHS, appendLine, h, lastValue):
        index = len(RHS)

        # index = stampMatrix.shape[0]
        # stampMatrix = expandMatrix(stampMatrix, 1)

        # stampMatrix[self.NPlus][index] += 1
        # stampMatrix[self.NMinus][index] -= 1
        # stampMatrix[index][self.NPlus] += 1
        # stampMatrix[index][self.NMinus] -= 1
        # stampMatrix[index][index] -= self.value / h

        # need to update
        # lastValue = 0
        i_tMinush = lastValue[index]
        RHS = np.vstack((RHS, np.array([[-self.value / h * i_tMinush]]))) # add vc

        return RHS

class ISource(SuperDevice):
    def __init__(self, name, connectionPoints, value, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
    
    def load(self, stampMatrix, RHS, appendLine):
        RHS[self.NPlus][0] -= self.value
        RHS[self.NMinus][0] += self.value
        return stampMatrix, RHS, appendLine
    
    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.load(stampMatrix, RHS, appendLine)

class VSource(SuperDevice):
    def __init__(self, name, connectionPoints, value, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
    
    def load(self, stampMatrix, RHS, appendLine):
        if not appendLine.__contains__(self.name):
            index = stampMatrix.shape[0]
            # print(stampMatrix.shape)
            stampMatrix = expandMatrix(stampMatrix, 1)
            # print(stampMatrix.shape, self.NPlus, index)
            stampMatrix[self.NPlus][index] += 1
            stampMatrix[self.NMinus][index] -= 1
            stampMatrix[index][self.NPlus] += 1
            stampMatrix[index][self.NMinus] -= 1

            RHS = np.vstack((RHS, np.array([self.value])))
            
            appendLine[self.name] = index

        return stampMatrix, RHS, appendLine

    def loadBEMatrix(self, stampMatrix, RHS, appendLine, h):
        if not appendLine.__contains__(self.name):
            index = stampMatrix.shape[0]
            # print(stampMatrix.shape)
            stampMatrix = expandMatrix(stampMatrix, 1)
            # print(stampMatrix.shape, self.NPlus, index)
            stampMatrix[self.NPlus][index] += 1
            stampMatrix[self.NMinus][index] -= 1
            stampMatrix[index][self.NPlus] += 1
            stampMatrix[index][self.NMinus] -= 1
            appendLine[self.name] = index

        return stampMatrix, RHS, appendLine
    
    def loadBERHS(self, stampMatrix, RHS, appendLine, h, lastValue):
        RHS = np.vstack((RHS, np.array([[self.value]])))
        return RHS

class VCCS(SuperDevice):
    def __init__(self, name, connectionPoints, value, controlConnectionPoints, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
        self.controlPoints = controlConnectionPoints
        self.NCPlus = self.controlPoints[0]
        self.NCMinus = self.controlPoints[1]
    
    def load(self, stampMatrix, RHS, appendLine):
        stampMatrix[self.NPlus][self.NCPlus] += self.value
        stampMatrix[self.NPlus][self.NCMinus] -= self.value
        stampMatrix[self.NMinus][self.NCPlus] -= self.value
        stampMatrix[self.NMinus][self.NCMinus] += self.value
        return stampMatrix, RHS, appendLine
        
    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.load(stampMatrix, RHS, appendLine)

class VCVS(SuperDevice):
    def __init__(self, name, connectionPoints, value, controlConnectionPoints, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
        self.controlPoints = controlConnectionPoints
        self.NCPlus = self.controlPoints[0]
        self.NCMinus = self.controlPoints[1]

    def load(self, stampMatrix, RHS, appendLine):
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)
        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += 1
        stampMatrix[index][self.NMinus] -= 1
        stampMatrix[index][self.NCPlus] -= self.value
        stampMatrix[index][self.NCMinus] += self.value

        RHS = np.vstack((RHS, np.array([0])))
        appendLine[self.name] = index
        return stampMatrix, RHS, appendLine
        
    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.load(stampMatrix, RHS, appendLine)

class CCCS(SuperDevice):
    def __init__(self, name, connectionPoints, value, controlConnectionPoints, control, controlValue, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
        self.controlPoints = controlConnectionPoints
        self.NCPlus = self.controlPoints[0]
        self.NCMinus = self.controlPoints[1]
        self.control = control
        self.controlValue = controlValue

    def load(self, stampMatrix, RHS, appendLine):
        if not appendLine.__contains__(self.control):
            index = stampMatrix.shape[0]
            stampMatrix = expandMatrix(stampMatrix, 1)
            stampMatrix[self.NPlus][index] += self.value
            stampMatrix[self.NMinus][index] -= self.value
            stampMatrix[self.NCPlus][index] += 1
            stampMatrix[self.NCMinus][index] -= 1
            stampMatrix[index][self.NCPlus] += 1
            stampMatrix[index][self.NCMinus] -= -1
            
            RHS = np.vstack((RHS, np.array([self.controlValue]))) # add vc

            appendLine[self.control] = index
        else:
            index = appendLine[self.control]
            stampMatrix[self.NPlus][index] += self.value
            stampMatrix[self.NMinus][index] -= self.value
            
        return stampMatrix, RHS, appendLine

    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.load(stampMatrix, RHS, appendLine)


class CCVS(SuperDevice):
    def __init__(self, name, connectionPoints, value, controlConnectionPoints, control, controlValue, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
        self.controlPoints = controlConnectionPoints
        self.NCPlus = self.controlPoints[0]
        self.NCMinus = self.controlPoints[1]
        self.control = control
        self.controlValue = controlValue

    def load(self, stampMatrix, RHS, appendLine):
        if not appendLine.__contains__(self.control):
            indexK = stampMatrix.shape[0]
            stampMatrix = expandMatrix(stampMatrix, 1)
            indexC = stampMatrix.shape[0]
            stampMatrix = expandMatrix(stampMatrix, 1)

            stampMatrix[self.NPlus][indexK] += 1
            stampMatrix[self.NMinus][indexK] -= 1
            stampMatrix[indexK][self.NPlus] += 1
            stampMatrix[indexK][self.NMinus] -= 1
            stampMatrix[indexC][self.NCPlus] += 1
            stampMatrix[indexC][self.NCMinus] -= 1
            stampMatrix[self.NCPlus][indexC] -= 1
            stampMatrix[self.NCMinus][indexC] -= 1
            stampMatrix[indexK][indexC] -= self.controlValue
            RHS = np.vstack((RHS, np.array([0]))) # add vc

            appendLine[self.control] = indexC
            appendLine[self.name] = indexK
        else:
            indexC = appendLine[self.control]
            indexK = stampMatrix.shape[0]
            stampMatrix = expandMatrix(stampMatrix, 1)

            stampMatrix[self.NPlus][indexK] += 1
            stampMatrix[self.NMinus][indexK] -= 1
            stampMatrix[indexK][self.NPlus] += 1
            stampMatrix[indexK][self.NMinus] -= 1
            stampMatrix[indexK][indexC] -= self.controlValue
            RHS = np.vstack((RHS, np.array([0]))) # add vc
            appendLine[self.name] = indexK
            
        return stampMatrix, RHS, appendLine

    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.load(stampMatrix, RHS, appendLine)
