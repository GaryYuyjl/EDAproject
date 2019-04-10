from Util import *
import numpy as np
# father class of all devices
alpha = 40
class SuperDevice:
    def __init__(self, name, connectionPoints, _type):
        self.connectionPoints = connectionPoints
        self.NPlus = self.connectionPoints[0]
        self.NMinus = self.connectionPoints[1]
        self.name = name
        self.type = _type

    def load(self):
        pass

class Diode(SuperDevice):
    def __init__(self, name, connectionPoints, _type):
        super().__init__(name, connectionPoints, _type)
        self.alpha = 40
    
    def load(self, stampMatrix, RHS, appendLine, lastValue=[]):
        if not len(lastValue):
            return stampMatrix, RHS, appendLine

        v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]

        stampMatrix[self.NPlus][self.NPlus] += self.alpha * np.exp(self.alpha * v_tMinush)
        stampMatrix[self.NMinus][self.NPlus] -= self.alpha * np.exp(self.alpha * v_tMinush)
        stampMatrix[self.NPlus][self.NMinus] -= self.alpha * np.exp(self.alpha * v_tMinush)
        stampMatrix[self.NMinus][self.NMinus] += self.alpha * np.exp(self.alpha * v_tMinush)
        RHS[self.NPlus][0] += -(np.exp(self.alpha * v_tMinush) - 1) + self.alpha * np.exp(self.alpha * v_tMinush) * v_tMinush
        RHS[self.NMinus][0] -= -(np.exp(self.alpha * v_tMinush) - 1) + self.alpha * np.exp(self.alpha * v_tMinush) * v_tMinush
        return stampMatrix, RHS, appendLine
    
    def loadBE(self, stampMatrix, RHS, appendLine, step, t = 0, lastValue=[], dcValue = None):
        v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]

        stampMatrix[self.NPlus][self.NPlus] += self.alpha * np.exp(self.alpha * v_tMinush)
        stampMatrix[self.NMinus][self.NPlus] -= self.alpha * np.exp(self.alpha * v_tMinush)
        stampMatrix[self.NPlus][self.NMinus] -= self.alpha * np.exp(self.alpha * v_tMinush)
        stampMatrix[self.NMinus][self.NMinus] += self.alpha * np.exp(self.alpha * v_tMinush)
        RHS[self.NPlus][0] += -(np.exp(self.alpha * v_tMinush) - 1) + self.alpha * np.exp(self.alpha * v_tMinush) * v_tMinush
        RHS[self.NMinus][0] -= -(np.exp(self.alpha * v_tMinush) - 1) + self.alpha * np.exp(self.alpha * v_tMinush) * v_tMinush

        return stampMatrix, RHS, appendLine

    def loadBEMatrix(self, stampMatrix, RHS, appendLine, step, lastValue):
        v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]

        stampMatrix[self.NPlus][self.NPlus] += self.alpha * np.exp(self.alpha * v_tMinush)
        stampMatrix[self.NMinus][self.NPlus] -= self.alpha * np.exp(self.alpha * v_tMinush)
        stampMatrix[self.NPlus][self.NMinus] -= self.alpha * np.exp(self.alpha * v_tMinush)
        stampMatrix[self.NMinus][self.NMinus] += self.alpha * np.exp(self.alpha * v_tMinush)
        return stampMatrix, RHS, appendLine

    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
        
        RHS[self.NPlus][0] -= np.exp(self.alpha * v_tMinush) - 1 - self.alpha * v_tMinush * np.exp(self.alpha * v_tMinush)
        RHS[self.NMinus][0] += np.exp(self.alpha * v_tMinush) - 1 - self.alpha * v_tMinush * np.exp(self.alpha * v_tMinush)
        return RHS, appendLine

    def loadFE(self, stampMatrix, RHS, appendLine, step, t = 0, lastValue=[], dcValue = None):
        return self.loadBE(stampMatrix, RHS, appendLine, step, t, lastValue, dcValue)
        
    def loadTR(self, stampMatrix, RHS, appendLine, step, t = 0, lastValue=[], dcValue = None):
        return self.loadBE(stampMatrix, RHS, appendLine, step, t, lastValue, dcValue)

    def loadFEMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.load(stampMatrix, RHS, appendLine)

    def loadFERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return RHS, appendLine
    
    def loadTRMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.load(stampMatrix, RHS, appendLine)

    def loadTRRHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return RHS, appendLine

class Mosfet(SuperDevice):
    def __init__(self, name, connectionPoints, _type, mname, W = None, L = None):
        super().__init__(name, connectionPoints, _type)
        self.mname = mname
        self.D = connectionPoints[0]
        self.G = connectionPoints[1]
        self.S = connectionPoints[2]
        self.B = connectionPoints[3]
        if mname[0] == 'N':
            self.k = 115e-6
            self.W = 2e-6
            self.L = 1e-6
            self.vt = 0.43
            self.lamda = 0.06
        elif mname[0] == 'P':
            self.k = -30e-6
            self.W = 4e-6
            self.L = 1e-6
            self.vt = -0.4
            self.lamda = -0.1
        if not W == None:
            self.W = stringToNum(W)
        if not L == None:
            self.L = stringToNum(L)
        

    def load(self, stampMatrix, RHS, appendLine, lastValue=[]):
        return stampMatrix, RHS, appendLine

    def loadDC(self, stampMatrix, RHS, appendLine, lastValue=None, dcValue = None):
        if len(lastValue) == 0:
            return stampMatrix, RHS, appendLine
        vgs = lastValue[self.G] - lastValue[self.S]
        vds = lastValue[self.D] - lastValue[self.S]
        # if self.mname[0] == 'N':
        #     gds = self.k * self.W / self.L * (vgs - self.vt) ** 2 * self.lamda
        #     gm = self.k * self.W / self.L * 2 * vds
        # elif self.mname[0] == 'P':
        #     gds = self.k * self.W / self.L * (-vgs + self.vt) ** 2 * self.lamda
        #     gm = -self.k * self.W / self.L * 2 * vds
        # print('gds', gds)
        # print('gm', gm)
        # print(self.mname[0], vgs, vds)
        if self.mname[0] == 'N':
            if vgs <= self.vt:
                print(1, self.name, vds, vgs, self.vt, lastValue)
                gm = 0
                gds = 0
                ids = 0
            elif vds <= vgs - self.vt:
                print(2, self.name, vds, vgs, self.vt, lastValue)
                gm = self.k * self.W / self.L * 2 * vds * (1 + self.lamda * vds)
                gds = self.k * self.W / self.L * (2 * (vgs - self.vt) + (4 * self.lamda * (vgs - self.vt) - 2) * vds - 3 * self.lamda * vds ** 2)
                ids = self.k * self.W / self.L * (2 * (vgs - self.vt) * vds - vds ** 2) * (1 + self.lamda * vds)
                if vds <= 0:
                    gm = self.k * self.W / self.L * 2 * vds
                    gds = self.k * self.W / self.L * (2 * (vgs - self.vt) - 2 * vds)
                    ids = self.k * self.W / self.L * (2 * (vgs - self.vt) * vds - vds ** 2)
            elif vds > vgs - self.vt:
                print(3, self.name, vds, vgs, self.vt, lastValue)
                gm = self.k * self.W / self.L * 2 * (vgs - self.vt) * (1 + self.lamda * vds)
                gds = self.k * self.W / self.L * (vgs - self.vt) ** 2 * self.lamda
                ids = self.k * self.W / self.L * (vgs - self.vt) ** 2 * (1 + self.lamda * vds)
        elif self.mname[0] == 'P':
            if vgs >= self.vt:
                print(4, self.name, vds, vgs, self.vt, lastValue)
                ids = 0
                gm = 0
                gds = 0
            elif vds >= vgs - self.vt:
                print(5, self.name, vds, vgs, self.vt, lastValue)
                gm = self.k * self.W / self.L * 2 * vds * (1 - self.lamda * vds)
                ### 重新算一下
                gds = self.k * self.W / self.L * (2 * (vgs - self.vt) + (-4 * self.lamda * (vgs - self.vt) - 2) * vds + 3 * self.lamda * vds ** 2)
                ids = self.k * self.W / self.L * (2 * (vgs - self.vt) * vds - vds ** 2) * (1 - self.lamda * vds)
                if vds >= 0:
                    gm = self.k * self.W / self.L * 2 * vds
                    gds = self.k * self.W / self.L * (2 * (vgs - self.vt) - 2 * vds)
                    ids = self.k * self.W / self.L * (2 * (vgs - self.vt) * vds - vds ** 2)
            elif vds < vgs - self.vt:
                print(6, self.name, vds, vgs, self.vt, lastValue)
                gm = self.k * self.W / self.L * 2 * (-vgs + self.vt) * (1 - self.lamda * vds)
                gds = self.k * self.W / self.L * (vgs - self.vt) ** 2 * self.lamda
                ids = self.k * self.W / self.L * (-vgs + self.vt) ** 2 * (1 - self.lamda * vds)
        stampMatrix[self.D][self.D] += gds
        stampMatrix[self.S][self.D] -= gds
        stampMatrix[self.D][self.S] -= gds + gm
        stampMatrix[self.S][self.S] += gds + gm
        stampMatrix[self.D][self.G] += gm
        stampMatrix[self.S][self.G] -= gm
        # print('vds', vds, gds, gm)
        jds = ids - gm * vgs - gds * vds
        RHS[self.D][0] -= jds
        RHS[self.S][0] += jds
        return stampMatrix, RHS, appendLine

    def loadDCMatrix(self, stampMatrix, RHS, appendLine, lastValue):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, 0, lastValue)

    def loadDCRHS(self, stampMatrix, RHS, appendLine, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, 0, lastValue)

    def loadBE(self, stampMatrix, RHS, appendLine,  step, t = 0, lastValue=[], dcValue = None):
        return self.loadDC(stampMatrix, RHS, appendLine, lastValue, dcValue)

    def loadFE(self, stampMatrix, RHS, appendLine,  step, t = 0, lastValue=[], dcValue = None):
        return self.loadDC(stampMatrix, RHS, appendLine, lastValue, dcValue)

    def loadTR(self, stampMatrix, RHS, appendLine,  step, t = 0, lastValue=[], dcValue = None):
        return self.loadDC(stampMatrix, RHS, appendLine, lastValue, dcValue)

    def loadBEMatrix(self, stampMatrix, RHS, appendLine, step, lastValue):
        vgs = lastValue[self.G] - lastValue[self.S]
        vds = lastValue[self.D] - lastValue[self.S]
        gds = self.k * self.W / self.L * (vgs - self.vt) ** 2 * self.lamda
        gm = self.k * self.W / self.L * 2 * vds

        stampMatrix[self.D][self.D] += gds
        stampMatrix[self.S][self.D] -= gds
        stampMatrix[self.D][self.S] -= gds + gm
        stampMatrix[self.S][self.S] += gds + gm
        stampMatrix[self.D][self.G] += gm
        stampMatrix[self.S][self.G] -= gm
        return stampMatrix, RHS, appendLine

    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        vgs = lastValue[self.G] - lastValue[self.S]
        vds = lastValue[self.D] - lastValue[self.S]
        gds = self.k * self.W / self.L * (vgs - self.vt) ** 2 * self.lamda
        gm = self.k * self.W / self.L * 2 * vds

        if vds < vgs - self.vt:
            ids = self.k * self.W / self.L * (2 * (vgs - self.vt) * vds - vds ** 2) * (1 + self.lamda * vds)
        elif vds > vgs - self.vt:
            ids = self.k * self.W / self.L * (vgs - self.vt) ** 2 * (1 + self.lamda * vds)
        jds = ids - gm * vgs - gds * vds
        RHS[self.D][0] -= jds
        RHS[self.S][0] += jds
        return RHS, appendLine
    
    def loadFEMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.load(stampMatrix, RHS, appendLine)

    def loadFERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return RHS, appendLine
    
    def loadTRMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.load(stampMatrix, RHS, appendLine)

    def loadTRRHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return RHS, appendLine

class Resistor(SuperDevice):
    def __init__(self, name, connectionPoints, value, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
    
    # load function will add this device to MNA matrix
    '''DC
        +    -     |  RHS
                   |   
    +  1/R  -1/R   |   0
                   |
    - -1/R  1/R    |   0
                   |
    '''
    def load(self, stampMatrix, RHS, appendLine, lastValue=[]):
        stampMatrix[self.NPlus][self.NPlus] += 1 / self.value
        stampMatrix[self.NMinus][self.NPlus] -= 1 / self.value
        stampMatrix[self.NPlus][self.NMinus] -= 1 / self.value
        stampMatrix[self.NMinus][self.NMinus] += 1 / self.value
        return stampMatrix, RHS, appendLine

    def loadDC(self, stampMatrix, RHS, appendLine, lastValue=None, dcValue = None):
        if dcValue == None:
            dcValue = self.value
        stampMatrix[self.NPlus][self.NPlus] += 1 / self.value
        stampMatrix[self.NPlus][self.NMinus] -= 1 / self.value
        stampMatrix[self.NMinus][self.NPlus] -= 1 / self.value
        stampMatrix[self.NMinus][self.NMinus] += 1 / self.value
        return stampMatrix, RHS, appendLine
    
    # def loadBE(self, stampMatrix, RHS, appendLine, step, t = 0, lastValue=[], dcValue = None):
    #     if dcValue == None:
    #         dcValue = self.value
    #     stampMatrix[self.NPlus][self.NPlus] += 1 / self.value
    #     stampMatrix[self.NPlus][self.NMinus] -= 1 / self.value
    #     stampMatrix[self.NMinus][self.NPlus] -= 1 / self.value
    #     stampMatrix[self.NMinus][self.NMinus] += 1 / self.value
    #     return stampMatrix, RHS, appendLine
    
    def loadBE(self, stampMatrix, RHS, appendLine,  step, t = 0, lastValue=[], dcValue = None):
        return self.loadDC(stampMatrix, RHS, appendLine, lastValue, dcValue)

    def loadFE(self, stampMatrix, RHS, appendLine,  step, t = 0, lastValue=[], dcValue = None):
        return self.loadDC(stampMatrix, RHS, appendLine, lastValue, dcValue)

    def loadTR(self, stampMatrix, RHS, appendLine,  step, t = 0, lastValue=[], dcValue = None):
        return self.loadDC(stampMatrix, RHS, appendLine, lastValue, dcValue)
    
    def loadBEMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.load(stampMatrix, RHS, appendLine)

    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return RHS, appendLine
    
    def loadFEMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.load(stampMatrix, RHS, appendLine)

    def loadFERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return RHS, appendLine
    
    def loadTRMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.load(stampMatrix, RHS, appendLine)

    def loadTRRHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return RHS, appendLine
    
class Capacitor(SuperDevice):
    def __init__(self, name, connectionPoints, value, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
    
    def load(self, stampMatrix, RHS, appendLine, lastValue=[]):
        stampMatrix[self.NPlus][self.NPlus] += self.value * 1j
        stampMatrix[self.NPlus][self.NMinus] -= self.value * 1j
        stampMatrix[self.NMinus][self.NPlus] -= self.value * 1j
        stampMatrix[self.NMinus][self.NMinus] += self.value * 1j
        return stampMatrix, RHS, appendLine

    def loadDC(self, stampMatrix, RHS, appendLine, lastValue=None, dcValue = None):
        if dcValue == None:
            dcValue = self.value
        stampMatrix[self.NPlus][self.NPlus] += self.value * 1j
        stampMatrix[self.NPlus][self.NMinus] -= self.value * 1j
        stampMatrix[self.NMinus][self.NPlus] -= self.value * 1j
        stampMatrix[self.NMinus][self.NMinus] += self.value * 1j
        return stampMatrix, RHS, appendLine

    '''TRAN BE
        +    -    i   |  RHS
                      |   
    +   0    0    1   |   0
                      |
    -   0    0    -1  |   0
                      |
    br C/h  -C/h  -1  |  C/h*v(t-h)
                      |
    '''

    def loadBE(self, stampMatrix, RHS, appendLine, h, t = 0, lastValue=[], dcValue = None):
        if dcValue == None:
            dcValue = self.value
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += self.value / h
        stampMatrix[index][self.NMinus] -= self.value / h
        stampMatrix[index][index] -= 1
        if len(lastValue):
            v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
            add = np.array([self.value / h * v_tMinush])
            RHS = np.vstack((RHS, add)) # add vc
        appendLine[self.name] = index

        return stampMatrix, RHS, appendLine

    def loadFE(self, stampMatrix, RHS, appendLine, step, t = 0, lastValue=[], dcValue = None):
        if dcValue == None:
            dcValue = self.value
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += self.value / step
        stampMatrix[index][self.NMinus] -= self.value / step
        if len(lastValue):
            v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
            i_tMinush = lastValue[index]
            add = np.array([self.value / step * v_tMinush + i_tMinush])
            RHS = np.vstack((RHS, add)) # add vc
            appendLine[self.name] = index

        return stampMatrix, RHS, appendLine

    def loadTR(self, stampMatrix, RHS, appendLine, step, t = 0, lastValue=[], dcValue = None):
        if dcValue == None:
            dcValue = self.value
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += 2 * self.value / step
        stampMatrix[index][self.NMinus] -= 2 * self.value / step
        stampMatrix[index][index] -= 1
        if len(lastValue):
            v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
            i_tMinush = lastValue[index]
            add = np.array([i_tMinush + 2 * self.value / step * v_tMinush])
            RHS = np.vstack((RHS, add)) # add vc
        appendLine[self.name] = index
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

        appendLine[self.name] = index
        return stampMatrix, RHS, appendLine

    def loadBERHS(self, stampMatrix, RHS, appendLine, h, lastValue):
        index = len(RHS)
        v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
        add = np.array([self.value / h * v_tMinush])
        RHS = np.vstack((RHS, add)) # add vc
        appendLine[self.name] = index

        return RHS, appendLine

    '''TRAN FE
        +    -    i   |  RHS
                      |   
    +   0    0    1   |   0
                      |
    -   0    0    -1  |   0
                      |
    br C/h -C/h   0   |  i(t-h)+C/h*v(t-h)
                      |
    '''
    def loadFEMatrix(self, stampMatrix, RHS, appendLine, step):
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += self.value / step
        stampMatrix[index][self.NMinus] -= self.value / step

        appendLine[self.name] = index
        return stampMatrix, RHS, appendLine

    def loadFERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        index = len(RHS)
        v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
        i_tMinush = lastValue[index]
        appendLine[self.name] = index

        add = np.array([self.value / step * v_tMinush + i_tMinush])
        RHS = np.vstack((RHS, add)) # add vc

        return RHS, appendLine
    
    '''TRAN TR
        +    -    i   |  RHS
                      |   
    +   0    0    1   |   0
                      |
    -   0    0    -1  |   0
                      |
    br 2C/h -2C/h -1  |  i(t-h)+2C/h*v(t-h)
                      |
    '''
    def loadTRMatrix(self, stampMatrix, RHS, appendLine, step):
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += 2 * self.value / step
        stampMatrix[index][self.NMinus] -= 2 * self.value / step
        stampMatrix[index][index] -= 1

        appendLine[self.name] = index
        return stampMatrix, RHS, appendLine

    def loadTRRHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        index = len(RHS)
        v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
        i_tMinush = lastValue[index]
        appendLine[self.name] = index

        add = np.array([i_tMinush + 2 * self.value / step * v_tMinush])
        RHS = np.vstack((RHS, add)) # add vc

        return RHS, appendLine

class Inductor(SuperDevice):
    def __init__(self, name, connectionPoints, value, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
    
    def load(self, stampMatrix, RHS, appendLine, lastValue=[]):
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

    '''TRAN BE
        +    -    i   |  RHS
                      |   
    +   0    0    1   |   0
                      |
    -   0    0    -1  |   0
                      |
    br  1   -1   -L/h |  -L/h*i(t-h)
                      |
    '''

    def loadBE(self, stampMatrix, RHS, appendLine, h, t = 0, lastValue=[], dcValue = None):
        if dcValue == None:
            dcValue = self.value
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += 1
        stampMatrix[index][self.NMinus] -= 1
        stampMatrix[index][index] -= self.value / h
        appendLine[self.name] = index
        if len(lastValue):
            i_tMinush = lastValue[index] 
            RHS = np.vstack((RHS, np.array([-self.value / h * i_tMinush]))) # add vc
        return stampMatrix, RHS, appendLine

    def loadFE(self, stampMatrix, RHS, appendLine, step, t = 0, lastValue=[], dcValue = None):
        if dcValue == None:
            dcValue = self.value
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][index] += 1
        appendLine[self.name] = index
        if len(lastValue):
            v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
            i_tMinush = lastValue[index] 
            RHS = np.vstack((RHS, np.array([step * v_tMinush / self.value + i_tMinush]))) # add vc
        return stampMatrix, RHS, appendLine

    def loadTR(self, stampMatrix, RHS, appendLine, step, t = 0, lastValue=[], dcValue = None):
        if dcValue == None:
            dcValue = self.value
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] -= 1
        stampMatrix[index][self.NMinus] += 1
        stampMatrix[index][index] += 2 * self.value / step

        appendLine[self.name] = index
        if len(lastValue):
            v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
            i_tMinush = lastValue[index]
            appendLine[self.name] = index

            add = np.array([i_tMinush * 2 * self.value / step + v_tMinush])
            RHS = np.vstack((RHS, add)) # add vc
        return stampMatrix, RHS, appendLine

    def loadBEMatrix(self, stampMatrix, RHS, appendLine, h):
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += 1
        stampMatrix[index][self.NMinus] -= 1
        stampMatrix[index][index] -= self.value / h
        appendLine[self.name] = index
        return stampMatrix, RHS, appendLine

    def loadBERHS(self, stampMatrix, RHS, appendLine, h, lastValue):
        index = len(RHS)
        i_tMinush = lastValue[index] 
        RHS = np.vstack((RHS, np.array([-self.value / h * i_tMinush]))) # add vc
        appendLine[self.name] = index

        return RHS, appendLine
    
    '''TRAN FE
        +    -    i   |  RHS
                      |   
    +   0    0    1   |   0
                      |
    -   0    0    -1  |   0
                      |
    br  0    0    1   |  i(t-h)+h/L*v(t-h)
                      |
    '''
    def loadFEMatrix(self, stampMatrix, RHS, appendLine, step):
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][index] += 1
        appendLine[self.name] = index
        return stampMatrix, RHS, appendLine

    def loadFERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        index = len(RHS)
        v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
        i_tMinush = lastValue[index] 
        RHS = np.vstack((RHS, np.array([step * v_tMinush / self.value + i_tMinush]))) # add vc
        appendLine[self.name] = index

        return RHS, appendLine
    
    '''TRAN TR
        +    -    i   |  RHS
                      |   
    +   0    0    1   |   0
                      |
    -   0    0   -1   |   0
                      |
    br  -1   1   2L/h |  2L/h*i(t-h)+i(t-h)
                      |
    '''
    def loadTRMatrix(self, stampMatrix, RHS, appendLine, step):
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)

        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] -= 1
        stampMatrix[index][self.NMinus] += 1
        stampMatrix[index][index] += 2 * self.value / step

        appendLine[self.name] = index
        return stampMatrix, RHS, appendLine

    def loadTRRHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        index = len(RHS)
        v_tMinush = lastValue[self.NPlus] - lastValue[self.NMinus]
        i_tMinush = lastValue[index]
        appendLine[self.name] = index

        add = np.array([i_tMinush * 2 * self.value / step + v_tMinush])
        RHS = np.vstack((RHS, add)) # add vc

        return RHS, appendLine


class ISource(SuperDevice):
    def __init__(self, name, connectionPoints, value, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
    
    '''DC
        +    -     |  RHS
                   |   
    +   0    0     |   -i
                   |
    -   0    0     |   i
                   |
    '''
    def load(self, stampMatrix, RHS, appendLine, lastValue=[]):
        RHS[self.NPlus][0] -= self.value
        RHS[self.NMinus][0] += self.value
        return stampMatrix, RHS, appendLine

    def loadDC(self, stampMatrix, RHS, appendLine, lastValue=None, dcValue = None):
        # print(dcValue, self.name, self.connectionPoints)
        if dcValue == None:
            dcValue = self.value
        if not appendLine.__contains__(self.name):
            RHS[self.NPlus][0] -= dcValue
            RHS[self.NMinus][0] += dcValue
        return stampMatrix, RHS, appendLine

    def loadBE(self, stampMatrix, RHS, appendLine, step, t = 0, lastValue=[], dcValue = None):
        if dcValue == None:
            dcValue = self.value
        RHS[self.NPlus][0] -= self.value
        RHS[self.NMinus][0] += self.value
        return stampMatrix, RHS, appendLine

    def loadBEMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.load(stampMatrix, RHS, appendLine)

    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        RHS[self.NPlus][0] -= self.value
        RHS[self.NMinus][0] += self.value
        return RHS, appendLine

    def loadFEMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)
    
    def loadFERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)
        
    def loadTRMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)
    
    def loadTRRHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)

class VSource(SuperDevice):
    def __init__(self, name, connectionPoints, value, _type, sin, pulse):
        super().__init__(name, connectionPoints, _type)
        self.value = value
        self.sin = False
        self.pulse = False
        if len(sin):
            self.sin = True
            self.sin_v0 = stringToNum(sin[0])
            self.sin_va = stringToNum(sin[1])
            self.sin_freq = stringToNum(sin[2])
            self.sin_td = stringToNum(sin[3])
            self.sin_theta = stringToNum(sin[4])
        if len(pulse):
            self.pulse = True
            self.pulse_v1 = stringToNum(pulse[0])
            self.pulse_v2 = stringToNum(pulse[1])
            self.pulse_td = stringToNum(pulse[2])
            self.pulse_tr = stringToNum(pulse[3])
            self.pulse_tf = stringToNum(pulse[4])
            self.pulse_pw = stringToNum(pulse[5])
            self.pulse_per = stringToNum(pulse[6])

    '''DC
        +    -    i   |  RHS
                      |   
    +   0    0    1   |   0
                      |
    -   0    0   -1   |   0
                      |
    br  -1   1    0   |   v
                      |
    '''
    def load(self, stampMatrix, RHS, appendLine, lastValue=[], dcValue = None):
        if dcValue == None:
            dcValue = self.value
        if not appendLine.__contains__(self.name):
            index = stampMatrix.shape[0]
            # print(stampMatrix.shape)
            stampMatrix = expandMatrix(stampMatrix, 1)
            # print(stampMatrix.shape, self.NPlus, index)
            stampMatrix[self.NPlus][index] += 1
            stampMatrix[self.NMinus][index] -= 1
            stampMatrix[index][self.NPlus] += 1
            stampMatrix[index][self.NMinus] -= 1

            RHS = np.vstack((RHS, np.array([dcValue])))
            
            appendLine[self.name] = index

        return stampMatrix, RHS, appendLine

    def loadDC(self, stampMatrix, RHS, appendLine, lastValue=None, dcValue = None):
        # print(dcValue, self.name, self.connectionPoints)
        if dcValue == None:
            dcValue = self.value
        if not appendLine.__contains__(self.name):
            index = stampMatrix.shape[0]
            # print(stampMatrix.shape)
            stampMatrix = expandMatrix(stampMatrix, 1)
            # print(stampMatrix.shape, self.NPlus, index)
            stampMatrix[self.NPlus][index] += 1
            stampMatrix[self.NMinus][index] -= 1
            stampMatrix[index][self.NPlus] += 1
            stampMatrix[index][self.NMinus] -= 1

            RHS = np.vstack((RHS, np.array([dcValue])))
            
            appendLine[self.name] = index
        return stampMatrix, RHS, appendLine

    def loadBE(self, stampMatrix, RHS, appendLine, step, t = 0, lastValue=[], dcValue = None):
        if dcValue == None:
            if self.sin == True:
                if t <= self.sin_td:
                    dcValue = self.sin_v0
                else:
                    dcValue = self.sin_v0 + self.sin_va * np.exp(-(t - self.sin_td) * self.sin_theta) * np.sin(2 * np.pi * self.sin_freq * (t - self.sin_td))
            elif self.pulse:
                if t >self.pulse_td and t < self.pulse_td+self.pulse_pw:
                    dcValue = self.pulse_v2
                else:
                    dcValue = self.pulse_v1
                print('dcvalue', dcValue, t, self.pulse_td, self.pulse_td+self.pulse_pw)
            else:
                dcValue = self.value
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
            RHS = np.vstack((RHS, np.array([dcValue])))
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
        if not appendLine.__contains__(self.name):
            index = len(RHS)        
            appendLine[self.name] = index
            RHS = np.vstack((RHS, np.array([self.value])))
        return RHS, appendLine
        
    def loadFEMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)
    
    def loadFERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)
        
    def loadTRMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)
    
    def loadTRRHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)
        
class VCCS(SuperDevice):
    def __init__(self, name, connectionPoints, value, controlConnectionPoints, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
        self.controlPoints = controlConnectionPoints
        self.NCPlus = self.controlPoints[0]
        self.NCMinus = self.controlPoints[1]
    
    '''DC
        +    -     |  RHS
                   |   
    +   G   -G     |   0
                   |
    -  -G    G     |   0
                   |
    '''
    def load(self, stampMatrix, RHS, appendLine, lastValue=[]):
        stampMatrix[self.NPlus][self.NCPlus] += self.value
        stampMatrix[self.NPlus][self.NCMinus] -= self.value
        stampMatrix[self.NMinus][self.NCPlus] -= self.value
        stampMatrix[self.NMinus][self.NCMinus] += self.value
        return stampMatrix, RHS, appendLine
    
    def loadBEMatrix(self, stampMatrix, RHS, appendLine, h):
        stampMatrix[self.NPlus][self.NCPlus] += self.value
        stampMatrix[self.NPlus][self.NCMinus] -= self.value
        stampMatrix[self.NMinus][self.NCPlus] -= self.value
        stampMatrix[self.NMinus][self.NCMinus] += self.value
        return stampMatrix, RHS, appendLine
        
    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return RHS, appendLine

    def loadFEMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)
    
    def loadFERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)
        
    def loadTRMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)
    
    def loadTRRHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)

class VCVS(SuperDevice):
    def __init__(self, name, connectionPoints, value, controlConnectionPoints, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
        self.controlPoints = controlConnectionPoints
        self.NCPlus = self.controlPoints[0]
        self.NCMinus = self.controlPoints[1]
    
    '''DC
        +    -    C+    C-    i   |  RHS
                                  |   
    +   0    0    0     0     1   |   0
                                  |
    -   0    0    0     0    -1   |   0
                                  |
    C+  0    0    0     0     0   |   0
                                  |
    C-  0    0    0     0     0   |   0
                                  |
    br  1   -1   -E     E     0   |   0
                                  |
    '''
    def load(self, stampMatrix, RHS, appendLine, lastValue=[]):
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
    
    def loadBEMatrix(self, stampMatrix, RHS, appendLine, h):
        index = stampMatrix.shape[0]
        stampMatrix = expandMatrix(stampMatrix, 1)
        stampMatrix[self.NPlus][index] += 1
        stampMatrix[self.NMinus][index] -= 1
        stampMatrix[index][self.NPlus] += 1
        stampMatrix[index][self.NMinus] -= 1
        stampMatrix[index][self.NCPlus] -= self.value
        stampMatrix[index][self.NCMinus] += self.value

        appendLine[self.name] = index
        return stampMatrix, RHS, appendLine

    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        index = len(RHS)        
        appendLine[self.name] = index
        RHS = np.vstack((RHS, np.array([0])))

        return RHS, appendLine

    def loadFEMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)
    
    def loadFERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)
        
    def loadTRMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)
    
    def loadTRRHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)

class CCCS(SuperDevice):
    def __init__(self, name, connectionPoints, value, controlConnectionPoints, control, controlValue, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
        self.controlPoints = controlConnectionPoints
        self.NCPlus = self.controlPoints[0]
        self.NCMinus = self.controlPoints[1]
        self.control = control
        self.controlValue = controlValue\

    '''DC
        +    -    C+    C-    i   |  RHS
                                  |   
    +   0    0    0     0     F   |   0
                                  |
    -   0    0    0     0    -F   |   0
                                  |
    C+  0    0    0     0     1   |   0
                                  |
    C-  0    0    0     0    -1   |   0
                                  |
    br  0    0    1    -1     0   |   Vc
                                  |
    '''
    def load(self, stampMatrix, RHS, appendLine, lastValue=[]):
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

    def loadBEMatrix(self, stampMatrix, RHS, appendLine, h):
        if not appendLine.__contains__(self.control):
            index = stampMatrix.shape[0]
            stampMatrix = expandMatrix(stampMatrix, 1)
            stampMatrix[self.NPlus][index] += self.value
            stampMatrix[self.NMinus][index] -= self.value
            stampMatrix[self.NCPlus][index] += 1
            stampMatrix[self.NCMinus][index] -= 1
            stampMatrix[index][self.NCPlus] += 1
            stampMatrix[index][self.NCMinus] -= -1
            
            appendLine[self.control] = index
        else:
            index = appendLine[self.control]
            stampMatrix[self.NPlus][index] += self.value
            stampMatrix[self.NMinus][index] -= self.value

    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        if not appendLine.__contains__(self.control):
            index = len(RHS)
            appendLine[self.control] = index
            
            RHS = np.vstack((RHS, np.array([self.controlValue]))) # add vc
        # else:
            # index = appendLine[self.control]
            # stampMatrix[self.NPlus][index] += self.value
            # stampMatrix[self.NMinus][index] -= self.value

        return RHS, appendLine

    def loadFEMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)
    
    def loadFERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)
        
    def loadTRMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)
    
    def loadTRRHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)

class CCVS(SuperDevice):
    def __init__(self, name, connectionPoints, value, controlConnectionPoints, control, controlValue, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value
        self.controlPoints = controlConnectionPoints
        self.NCPlus = self.controlPoints[0]
        self.NCMinus = self.controlPoints[1]
        self.control = control
        self.controlValue = controlValue

    '''DC
        +    -    C+    C-    ik    ic   |  RHS
                                         |   
    +   0    0    0     0     1     0    |   0
                                         |
    -   0    0    0     0    -1     0    |   0
                                         |
    C+  0    0    0     0     0     1    |   0
                                         |
    C-  0    0    0     0     0    -1    |   0
                                         |
    vs  1   -1    0     0     0    -H    |   Vc
                                         |
    cc  0    0    1    -1     0    0     |   Vc
                                         |
    '''
    def load(self, stampMatrix, RHS, appendLine, lastValue=[]):
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
            stampMatrix[indexK][indexC] -= self.value
            RHS = np.vstack((RHS, np.array([0]))) # add vc
            RHS = np.vstack((RHS, np.array([self.controlValue]))) # add vc
            
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
            stampMatrix[indexK][indexC] -= self.value
            RHS = np.vstack((RHS, np.array([0]))) # add vc
            appendLine[self.name] = indexK
        return stampMatrix, RHS, appendLine

    def loadBEMatrix(self, stampMatrix, RHS, appendLine, h):
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
            stampMatrix[indexK][indexC] -= self.value
            
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
            stampMatrix[indexK][indexC] -= self.value
            appendLine[self.name] = indexK
            
        return stampMatrix, RHS, appendLine

    def loadBERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        if not appendLine.__contains__(self.control):
            indexK = len(RHS)
            RHS = np.vstack((RHS, np.array([0]))) # add vc
            indexC = len(RHS)
            RHS = np.vstack((RHS, np.array([self.controlValue]))) # add vc

            appendLine[self.control] = indexC
            appendLine[self.name] = indexK
        else:
            indexC = appendLine[self.control]
            indexK = stampMatrix.shape[0]
            RHS = np.vstack((RHS, np.array([0]))) # add vc
            appendLine[self.name] = indexK
            
        return RHS, appendLine

    def loadFEMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)
    
    def loadFERHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)
        
    def loadTRMatrix(self, stampMatrix, RHS, appendLine, step):
        return self.loadBEMatrix(stampMatrix, RHS, appendLine, step)

    def loadTRRHS(self, stampMatrix, RHS, appendLine, step, lastValue):
        return self.loadBERHS(stampMatrix, RHS, appendLine, step, lastValue)
