from PyQt5.QtWidgets import QApplication
from Parser import Parser 
from Solve import Solve
import sys
from Device import *

class Spice:
    def __init__(self):
        self.devices = []
        self.nodeDict = {}
        self.deviceList = []
        self.commandList = []
    
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
        
    # this function generate the MNA
    def solve(self):
        solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
        solve.stamping()

    def solveTran(self, method = 'BE'):
        solve = Solve(self.nodeDict, self.deviceList, self.commandList, self.devices)
        solve.stampingBE()
