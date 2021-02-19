from PySide2.QtCore import QTimer
from functools import partial

class SequenceHandler:
    def __init__(self, xyint):
        self.text = ""
        self.lineIndex = 0
        self.numberOfLines = 0
        self.xyint = xyint
        self.createPauseTimer()
        self.connectPauseTimer()
        self.running = 0

        

    def createPauseTimer(self): 
        """Creates a single-shot timer to time pauses in scripts in a non-blocking way"""
        self.pauseTimer = QTimer()
        self.pauseTimer.setSingleShot(True)

    def printTextBuffer(self):
        print(self.text)

    def connectPauseTimer(self):
        """Connects up the pause timer to the script restart function"""
        self.pauseTimer.timeout.connect(partial(self.continueHandleScript))


    def startPauseTimer(self, time):
        """starts the pause timer"""
        self.pauseTimer.setInterval(time)
        self.pauseTimer.start()



    def handleScript(self, scriptString):
        print('handling script')
        self.running = 1
        self.text = scriptString
        self.splits = self.text.splitlines()
        self.numberOfLines = len(self.splits)
        self.lineIndex = 0
        while self.lineIndex < self.numberOfLines:
            self.handleSingleLine()
            if self.pauseTimer.isActive():
                return
        self.running = 0


    def continueHandleScript(self): #picks up where you left off
        while self.lineIndex < self.numberOfLines:
            self.handleSingleLine()
            if self.pauseTimer.isActive():
                return

        self.running = 0
        

    def incrementLineIndex(self):
        self.lineIndex += 1

    def handleSingleLine(self):
        self.parseCurrentLine()
        self.incrementLineIndex()
        
    def parseCurrentLine(self):
        self.parseLine(self.lineIndex)
    

    def parseLine(self, line):
        
        thisLine = self.splits[line]
        pointerChar = thisLine[0]
        restOfLine = thisLine[1:]

        if pointerChar == 'X': #directly send the rest of the line to the X uStepper as GCode
            print('x')
            
            restOfLine += ' '
            restOfLine = restOfLine.encode('utf-8')
            self.xyint.command(0, restOfLine)
            

        elif pointerChar == 'Y': #directly send the rest of the line to the Y uStepper as GCode
            restOfLine += ' '
            restOfLine = restOfLine.encode('utf-8')
            print('y')
            self.xyint.command(1, restOfLine)

        elif pointerChar == 'T': #delay for a set amount of time in ms. has the side effect of freezing the window.
            delayTime = int(restOfLine)
            print('delay ' + str(delayTime) + ' ms')
            
            self.startPauseTimer(delayTime)
            

        elif pointerChar == 'D':
            print('droplet not implemented yet')

        elif pointerChar == 'B':
            print('RX blocking not implemented yet')

        else:
            print('unrecognised line, skipping')
