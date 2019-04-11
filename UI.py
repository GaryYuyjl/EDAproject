import sys
from PyQt5.QtWidgets import QWidget, QGridLayout, QMainWindow, QTextEdit, QAction, QApplication, QFileDialog, QScrollArea
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtCore import QObject, pyqtSignal
from Parser import Parser 
from Solve import Solve
from Spice import Spice 
from Util import exampleNetlist

# redirect the console
class Stream(QObject):
    newText = pyqtSignal(str)
    def write(self, text):
        self.newText.emit(str(text))

# this class handle the user interface
class GUI(QMainWindow):
    def __init__(self, ):
        super().__init__()
        self.initUI()
        self.devices = []
        self.nodeDict = {}
        self.nodeCount = 0
        self.deviceList = []
        self.commandList = []

        self.mySpice = Spice()

    def saveFile(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')
        if name[0]:
            with open(name[0], 'w') as file:
                text = self.textEdit.toPlainText()
                file.write(text)

    def openFile(self):
        name = QFileDialog.getOpenFileName(self,'save file')
        if name[0]:
            with open(name[0], 'r') as file:
                self.textEdit.setText(file.read())
                

    def initUI(self):              

        grid = QGridLayout()
        grid.setSpacing(10)
        widget = QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

        self.textEdit = QTextEdit(self)
        # self.setCentralWidget(self.textEdit)
        # self.textEdit.setGeometry(0, 75, 1200, 500)
        self.textEdit.setPlainText(exampleNetlist)
        self.consoleText = QTextEdit(self)
        # self.consoleText = QScrollArea()
        # self.consoleText.setObjectName
        
        # self.consoleText.setGeometry(0, 500, 1200, 300)
        self.consoleText.setReadOnly(True)
        self.consoleText.setPlainText('CONSOLE. \n')
        
        grid.addWidget(self.textEdit, 1, 0)
        grid.addWidget(self.consoleText, 1, 1)


        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        saveFile = QAction('Save File', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save File')
        saveFile.triggered.connect(self.saveFile)

        openFile = QAction('Open File', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(self.openFile)

        parse = QAction('Parse', self)
        parse.setShortcut('Ctrl+P')
        parse.setStatusTip('Parse')
        parse.triggered.connect(self.parse)

        solveDC = QAction('SolveDC', self)
        solveDC.setShortcut('Ctrl+D')
        solveDC.setStatusTip('SolveDC')
        solveDC.triggered.connect(self.solveDC)

        solveTRAN = QAction('SolveTRAN', self)
        solveTRAN.setShortcut('Ctrl+T')
        solveTRAN.setStatusTip('SolveTRAN')
        solveTRAN.triggered.connect(self.solveTRAN)
        
        self.statusBar()
 
        # init tool bar and shorcuts
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAction)
        toolbar.addAction(saveFile)
        toolbar.addAction(openFile)
        toolbar.addAction(parse)
        toolbar.addAction(solveDC)
        toolbar.addAction(solveTRAN)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        simulationMenu = menubar.addMenu('Simulation')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(saveFile)
        fileMenu.addAction(openFile)
        simulationMenu.addAction(parse)
        simulationMenu.addAction(solveDC)
        simulationMenu.addAction(solveTRAN)
        # toolbar = self.addToolBar('Exit')
        # toolbar.addAction(exitAction)
         
        self.setGeometry(300, 100, 1200, 800)
        self.setWindowTitle('Python Spice')   
        self.show()
         
        sys.stdout = Stream(newText = self.outputWritten)  
        sys.stderr = Stream(newText = self.outputWritten)  

    def outputWritten(self, text):  
        cursor = self.consoleText.textCursor()  
        cursor.movePosition(QTextCursor.End)  
        cursor.insertText(text)  
        self.consoleText.setTextCursor(cursor)  
        self.consoleText.ensureCursorVisible()   

    def parse(self):
        text = self.textEdit.toPlainText()
        # myParser = Parser(text, self.nodeDict, self.deviceList, self.commandList)
        # myParser.startParser()
        self.mySpice.parse(text)
        self.consoleText.insertPlainText('finish parse\n')

    def solveDC(self):
        self.mySpice.solve()

    def solveTRAN(self):
        self.mySpice.solveTran(method='BE')
        self.mySpice.solveTran(method='FE')
        self.mySpice.solveTran(method='TR')
        self.mySpice.plotTranWithMatplotlib()

if __name__ == '__main__':
     
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec_())