from PyQt5.QtWidgets import QApplication
from Parser import Parser 
from Solve import Solve
import sys
from Device import *
import matplotlib.pyplot as plt

# the main spice class
class Spice:
    def __init__(self):
        self.devices = []
        self.nodeDict = {}
        self.deviceList = []
        self.commandList = []
    
        self.tranValueBE = []
        self.tranValueTRAP = []
        self.tranValueFE = []
    # this function parse the netlist
    def parse(self, netlist):
        self.devices = []
        self.nodeDict = {}
        self.deviceList = []
        self.commandList = []

        self.netlist = netlist.upper()
        myParser = Parser(self.netlist, self.nodeDict, self.deviceList, self.commandList)
        myParser.startParser()

        self.prepareAnalysis()

    def prepareAnalysis(self):
        self.changeConnectionPoints()
        for device in self.deviceList:
            print('device', device)
            if device['deviceType'] == 'R':
                self.devices.append(Resistor(device['name'], device['connectionPoints'], device['value'], device['deviceType']))
            elif device['deviceType'] == 'L':
                self.devices.append(Inductor(device['name'], device['connectionPoints'], device['value'], device['deviceType']))
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
        self.tranValueTRAP = []
        self.tranValueFE = []

    # this function generate the MNA
    def solve(self):
        solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
        solve.stamping()

    # solve the function in transient, has three methods
    def solveTran(self, method = 'BE', step = 0.01, stop = 200):
        solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
        if method == 'BE':
            self.tranValueBE = solve.stampingBE(step, stop)
        elif method == 'FE':
            self.tranValueFE = solve.stampingFE(step, stop)
        elif method == 'TRAP':
            self.tranValueTRAP = solve.stampingTRAP(step, stop)
    
    def plotTran(self, step = 0.01, stop = 200, mannual=[]):
        plt.figure(figsize=(10, 9))
        x = np.arange(0, stop * step, step) 
        y1 = self.tranValueFE[..., 1]
        plt.plot(x,y1[1:], label="FE")
        y2 = self.tranValueBE[..., 1]
        plt.plot(x,y2[1:], label="BE")
        y3 = self.tranValueTRAP[..., 1] 
        plt.plot(x,y3[1:], label="TRAP")
        plt.legend(loc='upper right')
        # plt.show()
        # V = 10 
        # R = 5
        # L = 4
        # C = 3
        # ym = 10 - 10 * ((np.exp(-1/30*x) * np.cos(np.sqrt(37) / (3*np.sqrt(50)) * x)) +
        #  np.exp(-1/30*x) * np.sin(np.sqrt(37) / (3*np.sqrt(50))) * np.sqrt(50) / (10*np.sqrt(37)))

        # ym = 1 + 9 * (np.exp(-11/100*x)*np.cos(3*np.sqrt(31)/100*x) + np.exp(-11/100*x)*np.sin(3*np.sqrt(31)/100*x)*11/3/np.sqrt(31))
        if len(mannual):
            plt.plot(x,mannual, label="mannual")
        plt.legend(loc='best')

        plt.title("Matplotlib demo") 
        plt.xlabel("t") 
        plt.ylabel("V") 
        plt.show()