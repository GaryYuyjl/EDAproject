# 行首能为空格？
# 字符串转数字
import re
from Util import *
class Parser:
    def __init__(self, netlist, nodeDict, deviceList, commandList):
        # self.netlist = netlist.upper()
        self.netlist = netlist
        self.nodeDict = nodeDict
        self.nodeCount = 1
        self.deviceList = deviceList
        self.commandList = commandList
        self.hasGround = False

    def updateNodeDict (self, *nodes):
        for node in nodes:
            if node == '0' or node == 0:
                self.nodeDict[node] = 0
                self.hasGround = True
                break
        for node in nodes:
            if not self.nodeDict.__contains__(node):
                self.nodeDict[node] = self.nodeCount
                self.nodeCount += 1
                
    def startParser(self):
        # print('Start parser now. \n')
        try:
            netlistList = self.netlist.splitlines()
            # handle the + continue line
            # print('Read netlist. \n')
            # print(netlistList)
            netlistList.reverse()
            handleContinueLineList = []
            tempLine = ''
            for line in netlistList:
                if len(line) == 0:
                    continue
                tempLine = line + tempLine 
                if not line[0] == '+':
                    handleContinueLineList.append(deleteCharsInString('+', tempLine))
                    tempLine = ''
            if len(tempLine):
                handleContinueLineList.append(tempLine)
            # print(handleContinueLineList)
            handleContinueLineList.reverse()
            netlistList = handleContinueLineList
            if not netlistList[-1] == '.END':
                raise NoEnddError('No .end command!')
            # print(netlistList)
            for index, line in enumerate(netlistList):
                # print(line, index)
                if not index == 0 and not line[0] == '*': # skip the fist line and the comment line
                    if line[0] == '.': # handle command line
                        self.handleCommand(line)
                    elif line[0].isalpha(): # handle device
                        self.handleDevice(line)
                    else:
                        print('line %d input is wrong' % index)
            # self.printInformation()
            if not self.hasGround:
                raise NoGroundError('No ground!')
            return self.nodeDict, self.deviceList, self.commandList
        except NoGroundError as ng:
            self.clean()
            print('ERROR NoGroundError', ng)
            return self.nodeDict, self.deviceList, self.commandList
        except NoEnddError as ne:
            self.clean()
            print('ERROR NoEnddError', ne)
            return self.nodeDict, self.deviceList, self.commandList
        except Exception as e:
            self.clean()
            print('ERROR', e)
            return self.nodeDict, self.deviceList, self.commandList

    def clean(self):
        self.nodeDict = {}
        self.deviceList = []
        self.commandList = []

    def printInformation(self):
        print(self.nodeDict)
        print('Devices:')
        for index, device in enumerate(self.deviceList):
            print('Device%d' % index)
            for k, v in device.items():
                if type(v) == tuple:
                    print('\t', k, ':', end = ' ')
                    list(map(lambda x: print(x, end = ' '), v))
                    print()
                else: 
                    print('\t', k, ':', v)
        print('Commands:')
        for index, command in enumerate(self.commandList):
            print('Command%d' % index)
            for k, v in command.items():
                if type(v) == tuple:
                    print('\t', k, ':', end = ' ')
                    list(map(lambda x: print(x, end = ' '), v))
                    print()
                else:
                    print('\t', k, ':', v)

    def handleDevice(self, line):
        # split_line = line.split()
        # print(split_line)
        line.strip()
        deviceParseType = parseType[line[0]]
        if deviceParseType == 0:
            self.parseRLC(line.strip().split())
        elif deviceParseType == 1:
            self.parseEFGH(line.strip().split())
        elif deviceParseType == 2:
            self.parseD(line)
        elif deviceParseType == 3:
            self.parseVI(line)
        elif deviceParseType == 4:
            self.parseM(line)
        

    def handleCommand(self, _line):
        line = stripSpaceInParentheseWithComma(_line)
        line = stripSpaceAroundEqualSign(line)
        commandList = line.strip().split()
        commandParams = {
            'type': commandList[0][1:]
        }
        # print(commandList, commandParams['type'])
        if commandParams['type'] == 'AC':
            # DEC stands for stands for stands for decade variation decade variation decade variation decade variation decade variation decade variation, and , and ND = # points = # points = # points = # points per decade per decade .
            # OCT stands for stands for stands for octave variation octave variation octave variationoctave variation octave variation octave variation, and , and NO = # points = # points = # points = # points per octave per octaveper octave.
            # LIN stands for stands for stands for linear variation linear variation linear variation linear variation linear variation linear variation, and , and , and NP = # points. = # points. = # points. =
            commandParams['variation'] = commandList[1]
            commandParams['pointsSelect'] = commandList[2]
            commandParams['fstart'] = stringToNum(commandList[3])
            commandParams['fstop'] = stringToNum(commandList[4])
        elif commandParams['type'] == 'TRAN':
            commandParams['tstep'] = stringToNum(commandList[1])
            commandParams['tstop'] = stringToNum(commandList[2])
        elif commandParams['type'] == 'DC':
            commandParams['src1'] = commandList[1]
            commandParams['start1'] = stringToNum(commandList[2])
            commandParams['stop1'] = stringToNum(commandList[3])
            commandParams['incr1'] = stringToNum(commandList[4])
            if len(commandParams) > 5:
                commandParams['src2'] = commandList[5]
                commandParams['start2'] = stringToNum(commandList[6])
                commandParams['stop2'] = stringToNum(commandList[7])
                commandParams['incr2'] = stringToNum(commandList[8])
        elif commandParams['type'] == 'PRINT' or commandParams['type'] == 'PLOT':
            commandParams['prtype'] = commandList[1]
            ovs = []
            for ov in commandList[2:]:
                ovParams = re.split('[(,)]', ov)
                ovParams.remove('')
                # print('ovparams', ovParams)
                if len(ovParams) == 2:
                    ovNodes = (ovParams[1], '0')
                elif len(ovParams) == 3:
                    ovNodes = (ovParams[1], ovParams[2])
                else:
                    ovNodes = None
                ovs.append({
                    'ovtype': ovParams[0],
                    'ovnodes': ovNodes
                })
            commandParams['ovs'] = ovs
        elif commandParams['type'] == 'MODEL':
            line = deleteCharsInString(('(', ')'), _line)
            commandList = line.split()
            commandParams['MNAME'] = commandList[1]
            commandParams['MTYPE'] = commandList[2]
            for param in commandList[3:]:
                paramPair = param.split('=')
                commandParams[paramPair[0].strip()] = paramPair[1].strip()
        elif commandParams['type'] == 'NODESET':
            for param in commandList[1:]:
                param = deleteCharsInString(('=', '(', ')'), param)
                paramPair = param.split()
                commandParams[paramPair[1].strip()] = paramPair[2].strip()
        elif commandParams['type'] == 'IC':
            for param in commandList[1:]:
                param = deleteCharsInString(('=', '(', ')'), param)
                paramPair = param.split()
                commandParams[paramPair[1].strip()] = paramPair[2].strip()
        elif commandParams['type'] == 'NOISE':
            VParams = re.split('[(),]', commandList[1])
            commandParams['noiseVoltage'] = tuple(VParams[1:])
            commandParams['SRC'] = commandList[2]
            commandParams['DECLINOCT'] = commandList[3]
            commandParams['PTS'] = commandList[4]
            commandParams['FSTART'] = commandList[5]
            commandParams['FSTOP'] = commandList[6]
            if len(commandList) > 7:
                commandParams['PTSPERSUMMARY'] = commandParams[7]
        elif commandParams['type'] == 'DISTO':
            commandParams['FSTART'] = commandList[3] 
            commandParams['FSTOP'] = commandList[4] 
            if commandList[1] == 'DEC':
                commandParams['DECLINOCT'] = 'DEC' 
                commandParams['ND'] = commandList[2]
            elif commandList[1] == 'OCT':
                commandParams['DECLINOCT'] = 'OCT' 
                commandParams['NO'] = commandList[2]
            elif commandList[1] == 'LIN':
                commandParams['DECLINOCT'] = 'LIN' 
                commandParams['NP'] = commandList[2]
            if len(commandList) > 5:
                commandParams['F2OVERF1'] = commandList[5]
        elif commandParams['type'] == 'PZ':
            commandParams['output'] = commandList[1] 
            commandParams['input'] = commandList[2] 
        else:
            bools = []
            for param in commandList[1:]:
                paramPair = param.split('=')
                if len(paramPair) > 1:
                    commandParams[paramPair[0].strip()] = paramPair[1].strip()
                else:
                    bools.append(paramPair[0])
            if len(bools):
                commandParams['bools'] = bools
        # print('command', commandList)
        self.commandList.append(commandParams)
    
    def parseRLC(self, device):
        deviceType = device[0][0]
        name = device[0]
        connectionPoints = (device[1], device[2])
        self.updateNodeDict(device[1], device[2])
        value = stringToNum(device[3])
        # print(device)
        self.deviceList.append({
            'deviceType': deviceType,
            'name': name,
            'connectionPoints': connectionPoints,
            'value': value
        })

    def parseD(self, device):
        deviceType = device[0][0]
        name = device[0]
        connectionPoints = (device[1], device[2])
        self.updateNodeDict(device[1], device[2])
        # value = stringToNum(device[3])
        # print(device)
        self.deviceList.append({
            'deviceType': deviceType,
            'name': name,
            'connectionPoints': connectionPoints
            # 'value': value
        })

    def parseM(self, _device):
        device = _device.strip()
        device = stripSpaceAroundEqualSign(device)
        device = device.split()
        deviceParams = initDeviceParams(device[0][0], device[0], (device[1], device[2], device[3], device[4]))
        self.updateNodeDict(device[1], device[2], device[3], device[4])
        deviceParams['name'] = device[0]
        deviceParams['MNAME'] = device[5]
        for param in device[6:]:
            paramPair = param.split('=')
            deviceParams[paramPair[0].strip()] = paramPair[1].strip()
        self.deviceList.append(deviceParams)

    def parseVI(self, device):
        params = deleteCharsInString(('(', ')'), device).split()
        # print(params)
        deviceParams = initDeviceParams(params[0][0], params[0], (params[1], params[2]))
        self.updateNodeDict(params[1], params[2])
        function = 'DC'
        functionParams = []
        for index, param in enumerate(params[3: ]):
            if param.isalpha():
                if len(functionParams):
                    deviceParams[function] = tuple(functionParams)
                function = param
                functionParams = []
            else:
                functionParams.append(param)
        if len(functionParams):
            deviceParams[function] = tuple(functionParams)
        deviceParams['DC'] = stringToNum(deviceParams['DC'][0])
        self.deviceList.append(deviceParams)

    def parseEFGH(self, device):
        # deviceType = device[0][0]
        deviceParams = initDeviceParams(device[0][0], device[0], (device[1], device[2]))
        self.updateNodeDict(device[1], device[2])
        # name = device[0]
        # connectionPoints = (device[1], device[2])
        deviceParams['value'] = stringToNum(device[-1])
        if device[0][0] == 'E' or device[0][0] == 'G':
            deviceParams['control'] = (device[3], device[4])
        else:
            deviceParams['control'] = device[3]
        self.deviceList.append(deviceParams)

