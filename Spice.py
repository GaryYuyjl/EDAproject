from Parser import Parser 
from Solve import Solve
from Device import *
import matplotlib.pyplot as plt
from Util import TranError, stringToNum
# the main spice class
class Spice:
    def __init__(self):
        self.devices = []
        self.nodeDict = {}
        self.deviceList = []
        self.commandList = []
        self.appendLine = {}
        self.revAppendLine = {}
        self.revNodeDict = {}
        self.tranValueBE = []
        self.tranValueTR = []
        self.tranValueFE = []
        self.DCValue = []
        self.ACValue = []    
    # this function parse the netlist
    def parse(self, netlist):
        self.devices = []
        self.nodeDict = {}
        self.deviceList = []
        self.commandList = []

        self.netlist = netlist.upper()
        myParser = Parser(self.netlist, self.nodeDict, self.deviceList, self.commandList)
        self.nodeDict, self.deviceList, self.commandList = myParser.startParser()
        self.prepareAnalysis()
        self.revNodeDict = {v : k for k, v in self.nodeDict.items()}
        print(self.nodeDict, self.deviceList)
        for command in self.commandList:
            print(command)
            if command['type'] == 'TRAN':
                # TRAN
                stop = command['tstop']
                step = command['tstep']
                if command.__contains__('tstart'):
                    start = command['tstart']
                else:
                    start = 0
                # self.solveTran('FE', step, stop, start)
                self.solveTran('BE', step, stop, start)
                # self.solveTran('TR', step, stop, start)
            elif command['type'] == 'DC':
                src1 = command['src1']
                start1 = command['start1']
                stop1 = command['stop1']
                incr1 = command['incr1']
                if command.__contains__('src2'):
                    src2 = command['src2']
                    start2 = command['start2']
                    stop2 = command['stop2']
                    incr2 = command['incr2']
                else:
                    src2 = None
                    start2 = None
                    stop2 = None
                    incr2 = None
                self.solveDC(src1, start1, stop1, incr1, src2, start2, stop2, incr2)
            elif command['type'] == 'AC':
                variation = command['variation']
                pointsSelect = command['pointsSelect']
                fstart = command['fstart']
                fstop = command['fstop']
                self.solveAC(variation, pointsSelect, fstart, fstop)
            elif command['type'] == 'OP': 
                # DC
                self.solve()
            elif command['type'] == 'PLOT' or command['type'] == 'PRINT':
                # print and plot need to be finished after all the commands
                pass
        
    def prepareAnalysis(self):
        self.changeConnectionPoints()
        for device in self.deviceList:
            # print('device', device)
            if device['deviceType'] == 'R':
                self.devices.append(Resistor(device['name'], device['connectionPoints'], device['value'], device['deviceType']))
            elif device['deviceType'] == 'L':
                if device.__contains__('IC'):
                    ic = device['IC']
                else:
                    ic = 0
                self.devices.append(Inductor(device['name'], device['connectionPoints'], device['value'], device['deviceType'], ic))
            elif device['deviceType'] == 'D':
                self.devices.append(Diode(device['name'], device['connectionPoints'], device['deviceType']))
            elif device['deviceType'] == 'Z':
                if device.__contains__('RON'):
                    ron = stringToNum(device['RON'])
                else:
                    ron = 100
                if device.__contains__('ROFF'):
                    roff = stringToNum(device['ROFF'])
                else:
                    roff = 100000
                if device.__contains__('RINIT'):
                    rinit = stringToNum(device['RINIT'])
                else:
                    rinit = 95000
                self.devices.append(Memresistor(device['name'], device['connectionPoints'], device['deviceType'], ron=ron, roff=roff, rinit=rinit))
            elif device['deviceType'] == 'M':
                if device.__contains__('W'):
                    W = device['W']
                else:
                    W = None
                if device.__contains__('L'):
                    L = device['L']
                else:
                    L = None
                self.devices.append(Mosfet(device['name'], device['connectionPoints'], device['deviceType'], device['MNAME'], W = W, L = L))
            elif device['deviceType'] == 'C':
                if device.__contains__('IC'):
                    ic = device['IC']
                else:
                    ic = 0
                self.devices.append(Capacitor(device['name'], device['connectionPoints'], device['value'], device['deviceType'], ic))
            elif device['deviceType'] == 'I':
                self.devices.append(ISource(device['name'], device['connectionPoints'], device['DC'], device['deviceType']))
            elif device['deviceType'] == 'V':
                sin = ()
                pulse = ()
                const = ()
                if device.__contains__('SIN'):
                    sin = device['SIN']
                if device.__contains__('PULSE'):
                    pulse = device['PULSE']
                if device.__contains__('CONST'):
                    const = device['CONST']
                self.devices.append(VSource(device['name'], device['connectionPoints'], device['DC'], device['deviceType'], sin, pulse, const))
            elif device['deviceType'] == 'E':
                self.devices.append(VCVS(device['name'], device['connectionPoints'], device['value'], device['control'], device['deviceType']))
            elif device['deviceType'] == 'F':
                for d in self.deviceList:
                    if d['name'] == device['control']:
                        controlDevice = d
                        break
                self.devices.append(CCCS(device['name'], device['connectionPoints'], device['value'], controlDevice['connectionPoints'], device['control'], device['value'], device['deviceType']))
            elif device['deviceType'] == 'G':
                self.devices.append(VCCS(device['name'], device['connectionPoints'], device['value'], device['control'], device['deviceType']))
            elif device['deviceType'] == 'H':
                for d in self.deviceList:
                    if d['name'] == device['control']:
                        controlDevice = d
                        break
                self.devices.append(CCVS(device['name'], device['connectionPoints'], device['value'], controlDevice['connectionPoints'], device['control'], device['value'], device['deviceType']))

    # this function map the node to consecutive number
    def changeConnectionPoints(self):
        for device in self.deviceList:
            tmp = list(device['connectionPoints'])
            for index, cp in enumerate(tmp):
                tmp[index] = self.nodeDict[cp]
            device['connectionPoints'] = tuple(tmp)

            if device['deviceType'] == 'E' or device['deviceType'] == 'G':
                tmp = list(device['control'])
                for index, cp in enumerate(tmp):
                    tmp[index] = self.nodeDict[cp]
                device['control'] = tuple(tmp)
        # print('change', self.deviceList)
        
    def clean(self):
        self.devices = []
        self.nodeDict = {}
        self.deviceList = []
        self.commandList = []
    
        self.tranValueBE = []
        self.tranValueTR = []
        self.tranValueFE = []
        self.DCValue = []
        self.ACValue = []

    # this function generate the MNA
    def solve(self):
        try:
            solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
            self.iteration = solve.stamping()
            print(self.iteration)
        except:
            print('Solve OP Error!')
            
    def showIteration(self):
        # plt.figure(figsize=(10, 6))
        x = np.arange(len(self.iteration) - 1)
        plt.plot(x, self.iteration[..., 2][1:] - self.iteration[..., 2][1:][-1], label='interation')
        plt.legend(loc='best')
        plt.title("NR iteration") 
        plt.xlabel("iteration") 
        plt.ylabel("V") 
        plt.show()

    def solveAC(self, variation, pointsSelect, fstart, fstop):
        try:
            self.ACValue = []    
            solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
            ACValue, self.appendLine, self.times = solve.stampingAC(variation, pointsSelect, fstart, fstop)
            self.revAppendLine = {v : k for k, v in self.appendLine.items()}
            self.ACValue.append(ACValue)
        except:
            print('Solve AC error')
        # print(self.ACValue)

    def solveDC(self, src, start, stop, incr, src2, start2, stop2, incr2):
        try:
            self.DCValue = []
            if not src2 == None:
                arr = np.arange(start2, stop2, incr2)
                for val in arr:
                    solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
                    DCValue, self.appendLine, self.times = solve.stampingDC(src, start, stop, incr, {
                        'src2': src2, 
                        'val2': val}
                        )
                    self.DCValue.append(DCValue)
                    self.revAppendLine = {v : k for k, v in self.appendLine.items()}

            else:
                print('solveDc without src2')
                solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
                DCValue, self.appendLine, self.times = solve.stampingDC(src, start, stop, incr)
                self.DCValue.append(DCValue)
                self.revAppendLine = {v : k for k, v in self.appendLine.items()}
        except:
            print('Solve DC error')

    def plotDCWithMatplotlib(self, abscissa = None, mannual=[]):
        try:
            if not abscissa == None:
                abscissa = self.nodeDict[abscissa]
            for command in self.commandList:
                print(command)
                if command['type'] == 'PRINT' or command['type'] == 'PLOT':
                    width = 1
                    height = len(command['ovs'])

                    for k, ov in enumerate(command['ovs']):
                        if ov['ovtype'] == 'V':
                            node1 = self.nodeDict[ov['ovnodes'][0]]
                            node2 = self.nodeDict[ov['ovnodes'][1]]
                            self.plotDC(self.times, abscissa, {
                                'mode': 'V',
                                'nodes': (node1, node2)})
                        elif ov['ovtype'] == 'I':
                            # node1 = self.nodeDict['I' + ov['ovnodes'][0]]
                            node1 = self.appendLine[ov['ovnodes'][0]]
                            self.plotDC(self.times, abscissa, {
                                'mode': 'I',
                                'nodes': node1})
        
                plt.show()
        except:
            print('Plot DC error')

    def plotACWithMatplotlib(self, abscissa = None):
        try:
            if not abscissa == None:
                abscissa = self.nodeDict[abscissa]
            for command in self.commandList:
                if command['type'] == 'PRINT' or command['type'] == 'PLOT':
                    width = 1
                    height = len(command['ovs'])
                    for k, ov in enumerate(command['ovs']):
                        if len(ov['ovtype']) == 1:
                            subMode = 'M'
                        else:
                            subMode = ov['ovtype'][1:]
                        print('mode', subMode)
                        if ov['ovtype'][0] == 'V':
                            node1 = self.nodeDict[ov['ovnodes'][0]]
                            node2 = self.nodeDict[ov['ovnodes'][1]]
                            self.plotAC(self.times, abscissa, {
                                'mode': 'V',
                                'subMode': subMode,
                                'nodes': (node1, node2)})
                        elif ov['ovtype'][0] == 'I':
                            # node1 = self.nodeDict['I' + ov['ovnodes'][0]]
                            node1 = self.appendLine[ov['ovnodes'][0]]
                            self.plotAC(self.times, abscissa, {
                                'mode': 'I',
                                'subMode': subMode,
                                'nodes': node1})
            plt.show()
        except:
            print('Plot AC error')


    def plotAC(self, times, abscissaNode=None, params = {}):
        # print(self.DCValue)
        print('plotdc', params)
        if params=={}:
            return
        subMode = params['subMode']
        # plt.figure(figsize=(10, 6))
        # arr = np.arange(start, stop, incr)
        arr = times
        ACValue = self.ACValue[0]
        if params['mode'] == 'V':
            node1 = params['nodes'][0]
            node2 = params['nodes'][1]
            print(node1, node2, self.tranValueFE)
            if subMode == 'M':
                y1 = np.abs(ACValue[..., node1] - ACValue[..., node2])
            elif subMode == 'I':
                y1 = np.imag(ACValue[..., node1] - ACValue[..., node2])
            elif subMode == 'R':
                y1 = np.real(ACValue[..., node1] - ACValue[..., node2])
            elif subMode == 'P':
                y1 = np.angle(ACValue[..., node1] - ACValue[..., node2])
            elif subMode == 'DB':
                y1 = 20 * np.log10(np.abs(ACValue[..., node1] - ACValue[..., node2]))
            # for val in arr:
            if not abscissaNode == None:
                x1 = ACValue[..., abscissaNode][1:]
            else:
                x1 = arr
            print('node', node1, node2, int(node2))
            print('Vnode%snode%s' % (self.revNodeDict[node1], self.revNodeDict[node2]))
            plt.plot(x1, y1[1:], label='Vnode%snode%s' % (self.revNodeDict[node1], self.revNodeDict[node2]))
            plt.legend(loc='best')
            plt.title('Vnode%snode%s' % (self.revNodeDict[node1], self.revNodeDict[node2])) 
            plt.xlabel("V") 
            plt.ylabel("V") 
        elif params['mode'] == 'I':
            node1 = params['nodes']
            y1 = ACValue[..., node1]
            if not abscissaNode == None:
                x1 = ACValue[..., abscissaNode][1:]
            else:
                x1 = arr
            plt.plot(x1,y1[1:], label='I%s' % self.revAppendLine[params['nodes']])
            plt.legend(loc='best')
            plt.title('I%s' % self.revAppendLine[params['nodes']]) 
            plt.xlabel("V") 
            plt.ylabel("I") 

    def plotDC(self, times, abscissaNode=None, params = {}):
        if params=={}:
            return
        arr = times
        if len(self.DCValue) == 1:
            DCValue = self.DCValue[0]
            if params['mode'] == 'V':
                node1 = params['nodes'][0]
                node2 = params['nodes'][1]
                y1 = DCValue[..., node1] - DCValue[..., node2]

                # for val in arr:
                if not abscissaNode == None:
                    x1 = DCValue[..., abscissaNode][1:]
                else:
                    x1 = arr
                plt.plot(x1, y1[1:], label='Vnode%snode%s' % (self.revNodeDict[node1], self.revNodeDict[node2]))
            
                plt.legend(loc='best')
                plt.title('Vnode%snode%s' % (self.revNodeDict[node1], self.revNodeDict[node2])) 
                plt.xlabel("V") 
                plt.ylabel("V") 
            elif params['mode'] == 'I':
                node1 = params['nodes']
                y1 = DCValue[..., node1]
                if not abscissaNode == None:
                    x1 = DCValue[..., abscissaNode][1:]
                else:
                    x1 = arr
                plt.plot(x1,y1[1:], label='I%s' % self.revAppendLine[params['nodes']])
                plt.legend(loc='best')
                plt.title(label='I%s' % self.revAppendLine[params['nodes']])
                plt.xlabel("V") 
                plt.ylabel("I") 
        else:
            for k,DCValue in enumerate(self.DCValue):
                if params['mode'] == 'V':
                    isV = True
                    node1 = params['nodes'][0]
                    node2 = params['nodes'][1]
                    y1 = DCValue[..., node1] - DCValue[..., node2]

                    # for val in arr:
                    # vinverter
                    if not abscissaNode == None:
                        x1 = DCValue[..., abscissaNode][1:]
                    else:
                        x1 = arr

                    plt.plot(x1, y1[1:], label='V%dnode%snode%s' % (k, self.revNodeDict[node1], self.revNodeDict[node2]))
                    # plt.show()
                elif params['mode'] == 'I':
                    isV = False
                    node1 = params['nodes']
                    y1 = DCValue[..., node1]
                    if not abscissaNode == None:
                        x1 = DCValue[..., abscissaNode][1:]
                    else:
                        x1 = arr

                    plt.plot(x1,y1[1:], label='I%dnode%s' % (k, self.revAppendLine[params['nodes']]))
                    plt.legend(loc='best')
                    plt.xlabel("V") 
                    plt.ylabel("I") 
            if isV:
                plt.title('V' + self.revNodeDict[params['nodes'][0]] + self.revNodeDict[params['nodes'][1]])
            else:
                plt.title('I%s' % self.revAppendLine[params['nodes']])
        plt.show()


    # solve the function in transient, has three methods
    def solveTran(self, method = 'BE', step = 0.1, stop = 1500, start = 0, timeStepControl = False):
        try:
            solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
            if method == 'BE':
                if timeStepControl:
                    self.tranValueBE, self.appendLine, self.times = solve.stampingBEWithStepControl(step, stop, start)
                else:
                    self.tranValueBE, self.appendLine, self.times = solve.stampingBE(step, stop, start)
                    print(self.tranValueBE)
                print('step stop start in spice', step, stop, start)
            elif method == 'FE':
                print('FE')
                self.tranValueFE, self.appendLine, self.times = solve.stampingFE(step, stop, start)
            elif method == 'TR':
                print(' TR')
                self.tranValueTR, self.appendLine, self.times = solve.stampingTR(step, stop, start)
            self.revAppendLine = {v : k for k, v in self.appendLine.items()}
        except Exception as e:
            print('Tran ERROR!', e)
    
    def plotTranWithMatplotlib(self, mannual=[]):
        try:
            for command in self.commandList:
                if command['type'] == 'PRINT' or command['type'] == 'PLOT':
                    # plt.figure(figsize=(10, 6))
                    width = 1
                    height = len(command['ovs'])
                    if command['prtype'] == 'TRAN':
                        fig = plt.figure()
                        ax1 = fig.add_subplot(111)
                        for k, ov in enumerate(command['ovs']):
                            if ov['ovtype'][0] == 'V':
                                node1 = self.nodeDict[ov['ovnodes'][0]]
                                node2 = self.nodeDict[ov['ovnodes'][1]]
                                self.plotTran(mannual, {
                                    'mode': 'V',
                                    'nodes': (node1, node2)})
                            elif ov['ovtype'][0] == 'I':
                                # node1 = self.nodeDict['I' + ov['ovnodes'][0]]
                                node1 = self.appendLine[ov['ovnodes'][0]]
                                self.plotTran(mannual, {
                                    'mode': 'I',
                                    'nodes': node1})
                plt.show()
        except:
            prnt('plot tran error')



    # the main function of plotting transient value, will call plotTran()
    def plotTranWithMatplotlibTwin(self, mannual=[]):
        for command in self.commandList:
            if command['type'] == 'PRINT' or command['type'] == 'PLOT':
                # plt.figure(figsize=(10, 6))
                width = 1
                height = len(command['ovs'])
                if command['prtype'] == 'TRAN':
                    fig = plt.figure()
                    ax1 = fig.add_subplot(111)
                    for k, ov in enumerate(command['ovs']):
                        if k == 0:
                            node1 = self.nodeDict[ov['ovnodes'][0]]
                            node2 = self.nodeDict[ov['ovnodes'][1]]
                            self.plotTran(mannual, {
                                'mode': 'V',
                                'nodes': (node1, node2)}, ax1)
                        elif k == 1:
                            ax2 = ax1.twinx()
                            # node1 = self.nodeDict['I' + ov['ovnodes'][0]]
                            node1 = self.appendLine[ov['ovnodes'][0]]
                            self.plotTran(mannual, {
                                'mode': 'I',
                                'nodes': node1}, ax2)
            plt.show()

    # plot each part
    def plotTran(self, mannual=[], params = {}, ax=plt):
        if params=={}:
            return
        x = np.array(self.times)[1:]
        if params['mode'] == 'V':
            node1 = params['nodes'][0]
            node2 = params['nodes'][1]
            if len(self.tranValueFE):
                y1 = self.tranValueFE[..., node1] - self.tranValueFE[..., node2]
                ax.plot(x,y1[1:], label='Vnode%snode%s' % (self.revNodeDict[node1], self.revNodeDict[node2]))
                # ax.scatter(x,y1[1:], s=1, label="FE")
            if len(self.tranValueBE):
                y2 = self.tranValueBE[..., node1] - self.tranValueBE[..., node2]
                print(x.size, y2.size)
                ax.plot(x,y2[1:], label='Vnode%snode%s' % (self.revNodeDict[node1], self.revNodeDict[node2]))
                # ax.scatter(x,y2[1:], s=1, label="BE")
            if len(self.tranValueTR):
                y3 = self.tranValueTR[..., node1] - self.tranValueTR[..., node2] 
                ax.plot(x,y3[1:], label='Vnode%snode%s' % (self.revNodeDict[node1], self.revNodeDict[node2]))
                # ax.scatter(x,y3[1:], s=1, label="TR")
            if len(mannual):
                ax.plot(x,mannual, label="mannual")
                # ax.scatter(x,mannual, label="mannual")
            ax.legend(loc='best')
        elif params['mode'] == 'I':
            node1 = params['nodes']
            # plt.figure('I%s' % params['nodes']
            if len(self.tranValueFE):
                y1 = self.tranValueFE[..., node1]
                ax.plot(x,y1[1:], 'r', label='I%s' % self.revAppendLine[params['nodes']])
                # ax.scatter(x,y1[1:], 'r', s=1, label="FE")
            if len(self.tranValueBE):
                y2 = self.tranValueBE[..., node1]
                ax.plot(x,y2[1:], 'r', label='I%s' % self.revAppendLine[params['nodes']])
                # ax.scatter(x,y2[1:], 'r', s=1, label="BE")
            if len(self.tranValueTR):
                y3 = self.tranValueTR[..., node1]
                ax.plot(x,y3[1:], 'r', label='I%s' % self.revAppendLine[params['nodes']])
                # ax.scatter(x,y3[1:], 'r', s=1, label="TR")
            if len(mannual):
                ax.plot(x,mannual, label="mannual")
                # ax.scatter(x,mannual, label="mannual")
            ax.legend(loc='best')

    def printMNAwithDiode(self, netlist):
        solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
        self.iteration = solve.stamping(printMNA = True)

    def showNewtonRaphson(self):
        # plt.figure(figsize=(10, 6))
        step = 0.00001
        x = np.arange(0, 0.02, step)
        y = 2 / 3 * x - 5 / 3 + np.exp(40 * x)

        for k, ite in enumerate(self.iteration):
            x1 = ite[2]
            y1 = 2 / 3 * x1 - 5 / 3 + np.exp(40 * x1)
            line = [(x1, 0), (x1, y1)]
            (xpoints, ypoints) = zip(*line)
            plt.plot(xpoints, ypoints, color='black')
            if k >= 1:
                lastx1 = self.iteration[k - 1][2]
                lasty1 = 2 / 3 * lastx1 - 5 / 3 + np.exp(40 * lastx1)
                line = [(lastx1, lasty1), (x1, 0)]
                (xpoints, ypoints) = zip(*line)
                plt.plot(xpoints, ypoints, color='black')

        zero = np.zeros((len(x)))
        # print(y)
        # print('iteration', self.iteration)
        plt.plot(x, zero, label="mannual")
        plt.plot(x, y, label="mannual")
        plt.title("Newton Raphson") 
        plt.xlabel("V") 
        plt.ylabel("I") 
        plt.show()
