from Parser import Parser 
from Solve import Solve
from Device import *
import matplotlib.pyplot as plt
from Util import TranError
# the main spice class
class Spice:
    def __init__(self):
        self.devices = []
        self.nodeDict = {}
        self.deviceList = []
        self.commandList = []
        self.appendLine = {}
        self.tranValueBE = []
        self.tranValueTR = []
        self.tranValueFE = []
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

        for command in self.commandList:
            print(command)
            if command['type'] == 'TRAN':
                # TRAN
                stop = command['tstop']
                step = command['tstep']
                num = np.floor(stop / step)
                self.solveTran('FE', step, num)
                self.solveTran('BE', step, num)
                self.solveTran('TR', step, num)
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
                self.devices.append(Inductor(device['name'], device['connectionPoints'], device['value'], device['deviceType']))
            elif device['deviceType'] == 'D':
                self.devices.append(Diode(device['name'], device['connectionPoints'], device['deviceType']))
            elif device['deviceType'] == 'M':
                self.devices.append(Mosfet(device['name'], device['connectionPoints'], device['deviceType'], device['MNAME']))
            elif device['deviceType'] == 'C':
                self.devices.append(Capacitor(device['name'], device['connectionPoints'], device['value'], device['deviceType']))
            elif device['deviceType'] == 'I':
                self.devices.append(ISource(device['name'], device['connectionPoints'], device['DC'], device['deviceType']))
            elif device['deviceType'] == 'V':
                self.devices.append(VSource(device['name'], device['connectionPoints'], device['DC'], device['deviceType']))
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
        # print(self.devices, '\n', self.nodeDict)

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

    # this function generate the MNA
    def solve(self):
        try:
            solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
            solve.stamping()
        except:
            print('Solve DC Error!')
            
    def solveDC(self, src, start, stop, incr, src2, start2, stop2, incr2):
        self.DCValue = []
        if not src2 == None:
            arr = np.arange(start2, stop2, incr2)
            for val in arr:
                solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
                DCValue, self.appendLine = solve.stampingDC(src, start, stop, incr, {
                    'src2': src2, 
                    'val2': val}
                    )
                self.DCValue.append(DCValue)
        else:
            solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
            DCValue, self.appendLine = solve.stampingDC(src, start, stop, incr)
            self.DCValue.append(DCValue)

    def plotDCWithMatplotlib(self, start, stop, incr, abscissa = None, mannual=[]):
        print(self.appendLine)
        print(self.nodeDict)
        if not abscissa == None:
            abscissa = self.nodeDict[abscissa]
        for command in self.commandList:
            # print(command)
            if command['type'] == 'PRINT' or command['type'] == 'PLOT':
                if command['prtype'] == 'DC':
                    for ov in command['ovs']:
                        if ov['ovtype'] == 'V':
                            node1 = self.nodeDict[ov['ovnodes'][0]]
                            node2 = self.nodeDict[ov['ovnodes'][1]]
                            self.plotDC(start, incr, stop, abscissa, {
                                'mode': 'V',
                                'nodes': (node1, node2)})
                        elif ov['ovtype'] == 'I':
                            # node1 = self.nodeDict['I' + ov['ovnodes'][0]]
                            node1 = self.appendLine[ov['ovnodes'][0]]
                            self.plotDC(start, incr, stop, abscissa, {
                                'mode': 'I',
                                'nodes': node1})

    def plotDC(self, start = 0, incr = 0.1, stop = 1.5, abscissaNode=None, params = {}):
        print(self.DCValue)
        print('plotdc', params)
        if params=={}:
            return
        plt.figure(figsize=(10, 9))
        arr = np.arange(start, stop, incr)
        if len(self.DCValue) == 1:
            DCValue = self.DCValue[0]
            if params['mode'] == 'V':
                node1 = params['nodes'][0]
                node2 = params['nodes'][1]
                # print(node1, node2, self.tranValueFE)
                y1 = DCValue[..., node1] - DCValue[..., node2]

                # for val in arr:
                print(DCValue, self.nodeDict)
                # vinverter
                if not abscissaNode == None:
                    # x1 = DCValue[..., 2]
                    x1 = DCValue[..., abscissaNode][1:]
                else:
                    x1 = np.arange(start, stop, incr)
                # y1 = DCValue[..., 3]
                plt.plot(x1, y1[1:], label="DC")

                plt.legend(loc='best')
                plt.title("demo") 
                plt.xlabel("t") 
                plt.ylabel("V") 
            elif params['mode'] == 'I':
                node1 = params['nodes']
                y1 = DCValue[..., node1]
                if not abscissaNode == None:
                    # x1 = DCValue[..., 2]
                    x1 = DCValue[..., abscissaNode][1:]
                else:
                    x1 = np.arange(start, stop, incr)

                # nmos
                # x1 = self.DCValue[..., 1] - self.DCValue[..., 0]
                # pmos
                # x1 = self.DCValue[..., 2] - self.DCValue[..., 0]

                plt.plot(x1,y1[1:], label="DC")
                plt.legend(loc='best')
                plt.title("demo") 
                plt.xlabel("t") 
                plt.ylabel("I") 
        else:
            for k,DCValue in enumerate(self.DCValue):
                if params['mode'] == 'V':
                    node1 = params['nodes'][0]
                    node2 = params['nodes'][1]
                    # print(node1, node2, self.tranValueFE)
                    y1 = DCValue[..., node1] - DCValue[..., node2]

                    # for val in arr:
                    print(DCValue, self.nodeDict)
                    # vinverter
                    if not abscissaNode == None:
                        # x1 = DCValue[..., 2]
                        x1 = DCValue[..., abscissaNode][1:]
                    else:
                        x1 = np.arange(start, stop, incr)
                    # y1 = DCValue[..., 3]
                    plt.plot(x1, y1[1:], label=("DC" + str(k)))

                    # plt.legend(loc='best')
                    # plt.title("demo") 
                    # plt.xlabel("t") 
                    # plt.ylabel("V") 
                    plt.show()
                elif params['mode'] == 'I':
                    node1 = params['nodes']
                    y1 = DCValue[..., node1]
                    if not abscissaNode == None:
                        # x1 = DCValue[..., 2]
                        x1 = DCValue[..., abscissaNode][1:]
                    else:
                        x1 = np.arange(start, stop, incr)
                    # nmos
                    # x1 = DCValue[..., 1] - DCValue[..., 0]
                    # pmos
                    # x1 = DCValue[..., 2] - DCValue[..., 0]
                    plt.plot(x1,y1[1:], label=("DC" + str(k)))
                    plt.legend(loc='best')
                    plt.title("demo") 
                    plt.xlabel("t") 
                    plt.ylabel("I") 
        plt.show()


    # solve the function in transient, has three methods
    def solveTran(self, method = 'BE', step = 0.1, stop = 1500):
        # try:
            solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
            if method == 'BE':
                self.tranValueBE, self.appendLine = solve.stampingBE(step, stop)
            elif method == 'FE':
                self.tranValueFE, self.appendLine = solve.stampingFE(step, stop)
            elif method == 'TR':
                self.tranValueTR, self.appendLine = solve.stampingTR(step, stop)
        # except Exception as e:
        #     print('Tran ERROR!', e)
    
    # the main function of plotting transient value, will call plotTran()
    def plotTranWithMatplotlib(self, step = 0.1, stop = 1500, mannual=[]):
        for command in self.commandList:
            # print(command)
            if command['type'] == 'PRINT' or command['type'] == 'PLOT':
                if command['prtype'] == 'TRAN':
                    for ov in command['ovs']:
                        if ov['ovtype'] == 'V':
                            node1 = self.nodeDict[ov['ovnodes'][0]]
                            node2 = self.nodeDict[ov['ovnodes'][1]]
                            self.plotTran(step, stop, mannual, {
                                'mode': 'V',
                                'nodes': (node1, node2)})
                        elif ov['ovtype'] == 'I':
                            # node1 = self.nodeDict['I' + ov['ovnodes'][0]]
                            node1 = self.appendLine[ov['ovnodes'][0]]
                            self.plotTran(step, stop, mannual, {
                                'mode': 'I',
                                'nodes': node1})

    # plot each part
    def plotTran(self, step = 0.1, stop = 1500, mannual=[], params = {}):
        # print(self.tranValueBE, self.tranValueFE, self.tranValueTR)
        if params=={}:
            return
        plt.figure(figsize=(10, 9))
        x = np.arange(0, stop * step, step)
        if params['mode'] == 'V':
            node1 = params['nodes'][0]
            node2 = params['nodes'][1]
            # print(node1, node2, self.tranValueFE)
            if len(self.tranValueFE):
                y1 = self.tranValueFE[..., node1] - self.tranValueFE[..., node2]
                plt.plot(x,y1[1:], label="FE")
            if len(self.tranValueBE):
                y2 = self.tranValueBE[..., node1] - self.tranValueBE[..., node2]
                plt.plot(x,y2[1:], label="BE")
            if len(self.tranValueTR):
                y3 = self.tranValueTR[..., node1] - self.tranValueTR[..., node2] 
                plt.plot(x,y3[1:], label="TR")
            if len(mannual):
                plt.plot(x,mannual, label="mannual")
            plt.legend(loc='best')
            plt.title("demo") 
            plt.xlabel("t") 
            plt.ylabel("V") 
            plt.show()
        elif params['mode'] == 'I':
            node1 = params['nodes']
            if len(self.tranValueFE):
                y1 = self.tranValueFE[..., node1]
                plt.plot(x,y1[1:], label="FE")
            if len(self.tranValueBE):
                y2 = self.tranValueBE[..., node1]
                plt.plot(x,y2[1:], label="BE")
            if len(self.tranValueTR):
                y3 = self.tranValueTR[..., node1]
                plt.plot(x,y3[1:], label="TR")
            if len(mannual):
                plt.plot(x,mannual, label="mannual")
            plt.legend(loc='best')
            plt.title("demo") 
            plt.xlabel("t") 
            plt.ylabel("I") 
            plt.show()
