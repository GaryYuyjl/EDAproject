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
    
    def load(self, stampMatrix, RHS, appendLine):
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
        
        RHS[self.NPlus][0] -= np.exp(self.alpha * v_tMinush) - 1 - self.alpha * np.exp(self.alpha * v_tMinush) * v_tMinush
        RHS[self.NMinus][0] += np.exp(self.alpha * v_tMinush) - 1 - self.alpha * np.exp(self.alpha * v_tMinush) * v_tMinush
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
    def load(self, stampMatrix, RHS, appendLine):
        stampMatrix[self.NPlus][self.NPlus] += 1 / self.value
        stampMatrix[self.NMinus][self.NPlus] -= 1 / self.value
        stampMatrix[self.NPlus][self.NMinus] -= 1 / self.value
        stampMatrix[self.NMinus][self.NMinus] += 1 / self.value
        return stampMatrix, RHS, appendLine
    
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
    
    def load(self, stampMatrix, RHS, appendLine):
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
        # stampMatrix[index][self.NPlus] += 1
        # stampMatrix[index][self.NMinus] -= 1
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
    def load(self, stampMatrix, RHS, appendLine):
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
    def __init__(self, name, connectionPoints, value, _type):
        super().__init__(name, connectionPoints, _type)
        self.value = value

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
    def load(self, stampMatrix, RHS, appendLine):
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
