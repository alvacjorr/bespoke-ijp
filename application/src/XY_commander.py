from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QPlainTextEdit, QHBoxLayout
from PySide2.QtWidgets import QGridLayout, QLineEdit, QMainWindow, QSpinBox, QLCDNumber, QGroupBox, QDoubleSpinBox
from PySide2.QtCore import Slot, Qt, QTimer,QDateTime, Signal
import sys
from functools import partial
import serial
import serial.tools.list_ports
import re
from constants import *
import time

import conversions as conv

import psu_serial

import numpy as np

import random
import datetime as dt
import matplotlib
matplotlib.use('Qt5Agg')



from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure




class MplCanvas(FigureCanvasQTAgg):
    """summary

    :param FigureCanvasQTAgg: [description]
    :type FigureCanvasQTAgg: [type]
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(1,2,1)
        self.axes2 = fig.add_subplot(1,2,2)
        super(MplCanvas, self).__init__(fig)


class GraphWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Graphs!")
        layout.addWidget(self.label)
        self.setLayout(layout)
        n_data = 50
        self.xdata = list(range(n_data))
        self.ydata = [random.randint(0, 10) for i in range(n_data)]

        n_data = 50
        self.xdata2 = list(range(n_data))
        self.ydata2 = [random.randint(0, 10) for i in range(n_data)]

        self.sc = MplCanvas(self, width=5, height=4, dpi=100)

        layout.addWidget(self.sc)

        self._plot_ref = None
        self._plot_ref_2 = None


        self.show()


    def update_plot(self, y_new):
        self.ydata = self.ydata[1:]
        self.ydata.append(y_new)
        if self._plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.sc.axes.plot(self.xdata, self.ydata, 'r')
            self._plot_ref = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref.set_ydata(self.ydata)

        # Trigger the canvas to update and redraw.
        self.sc.draw()

    def update_other_plot(self, y_new):
        self.ydata2 = self.ydata2[1:]
        self.ydata2.append(y_new)
        if self._plot_ref_2 is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.sc.axes2.plot(self.xdata2, self.ydata2, 'r')
            self._plot_ref_2 = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref_2.set_ydata(self.ydata2)

        # Trigger the canvas to update and redraw.
        self.sc.draw()






class PrinterUi(QMainWindow):
    """Main UI

    :param QMainWindow: [description]
    :type QMainWindow: [type]
    """

    keyPressed = Signal(int)
    def __init__(self):
        """Creates the UI
        """
        super().__init__()
        # Set some main window's properties
        self.setWindowTitle('Printer')
        #self.setFixedSize(300, 300)
        # Set the central widget and properties
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)


        
        self.createJoypad()
        self.goToLayout = QGridLayout()
        self.createGoToBox()
        self.createGoToAngleBox()
        self.createGoToMMBox()
        self.createPositionIndicator()
        self.createHeaterIndicator()
        self.generalLayout.addLayout(self.goToLayout)
        self.createToolBox()
        self.createScriptEditor()
        self.show_graph_window()

    def show_graph_window(self):
        self._graph = GraphWindow()
        self._graph.show()

      

        
    def keyPressEvent(self,event):
        """Handle a keypress event
        """
        super(PrinterUi, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())


    def createJoypad(self):
        """Creates a joypad to control the XY motion, with a 'DROP' button in the middle
        """
        self.joypadButtons = {}
        joypadLayout = QGridLayout()
        joypadButtons = {'^': (0,1), 'v': (2,1), '>': (1,2), '<': (1,0), 'DROP': (1,1)}
        for btnText, pos in joypadButtons.items():
            self.joypadButtons[btnText] = QPushButton(btnText)
            self.joypadButtons[btnText].setFixedSize(40, 40)
            joypadLayout.addWidget(self.joypadButtons[btnText], pos[0], pos[1])
        self.joypadDistanceSetter = QSpinBox()        
        self.joypadDistanceSetter.setMinimum(0)
        self.joypadDistanceSetter.setSingleStep(QT_JOYSTICK_STEP_INCREMENT)
        self.joypadDistanceSetter.setMaximum(QT_JOYSTICK_MAXIMUM_STEPS)
        self.joypadDistanceSetter.setValue(QT_JOYSTICK_STEP_INCREMENT)
        joypadLayout.addWidget(self.joypadDistanceSetter,2,2)
        joypadBox = QGroupBox("Joypad")
        joypadBox.setLayout(joypadLayout)
        joypadBox.setMinimumHeight(QT_JOYPAD_HEIGHT)
        joypadBox.setMinimumWidth(QT_JOYPAD_WIDTH)
        joypadBox.setMaximumHeight(QT_JOYPAD_HEIGHT)
        joypadBox.setMaximumWidth(QT_JOYPAD_WIDTH)
        self.generalLayout.addWidget(joypadBox) #check indent

    def createPositionIndicator(self):
        """Create an LCD position indicator for X and Y
        """
        PILayout = QGridLayout()
        self.PILCDScreens = {}
        self.PILCDLabels = {}
        LCDHeaderOffset = 1
        
        
        for valName,valIndex in LCDvals.items():
            for dim,dimString in dimMap.items():
                if valName == 'axis':
                    self.PILCDLabels[dim] = QLabel(dimString)
                    PILayout.addWidget(self.PILCDLabels[dim],dim+LCDHeaderOffset,0)
                else:
                    self.PILCDScreens[dim,valIndex] = QLCDNumber()
                    self.PILCDScreens[dim,valIndex].setDigitCount(6)
                    self.PILCDScreens[dim,valIndex].setFixedSize(100,40)
                    PILayout.addWidget(self.PILCDScreens[dim,valIndex],dim+LCDHeaderOffset,1+valIndex)

                
                
            PILayout.addWidget(QLabel(valName),0,1+valIndex)
            
            
        PIBox = QGroupBox("Current Position")
        PIBox.setLayout(PILayout)

        self.goToLayout.addWidget(PIBox,1,0,1,3)

    def createHeaterIndicator(self):
        HeaterLayout = QGridLayout()
        self.HeaterLCDScreens = {}
        self.HeaterLCDLabels = {}

        LCDHeaderOffset = 1
        
        
        for valName,valIndex in HeaterLCDvals.items():
            for dim,dimString in HeaterChannelNames.items():
                if valName == 'Channel':
                    self.HeaterLCDLabels[dim] = QLabel(dimString)
                    HeaterLayout.addWidget(self.HeaterLCDLabels[dim],dim+LCDHeaderOffset,0)
                else:
                    self.HeaterLCDScreens[dim,valIndex] = QLCDNumber()
                    self.HeaterLCDScreens[dim,valIndex].setDigitCount(6)
                    self.HeaterLCDScreens[dim,valIndex].setFixedSize(100,40)
                    HeaterLayout.addWidget(self.HeaterLCDScreens[dim,valIndex],dim+LCDHeaderOffset,1+valIndex)

                
                
            HeaterLayout.addWidget(QLabel(valName),0,1+valIndex)
            
            
        HeaterBox = QGroupBox("Heater Power")
        HeaterBox.setLayout(HeaterLayout)

        self.goToLayout.addWidget(HeaterBox,2,0,1,3)

    def createGoToBox(self):
        """Creates a box with a go to Steps button and two spinboxes to set X and Y in steps"""
        GTLayout = QGridLayout()
        self.GoToSpinners = {}
        self.GoToLabels = {}
        for dim,dimString in dimMap.items():
            self.GoToLabels[dim] = QLabel(dimString)
            self.GoToSpinners[dim] = QSpinBox()
            self.GoToSpinners[dim].setValue(1)
            self.GoToSpinners[dim].setMaximum(RAIL_APPROX_LENGTH_STEPS)
            GTLayout.addWidget(self.GoToLabels[dim],0,dim)
            GTLayout.addWidget(self.GoToSpinners[dim],1,dim)
        self.GoToButton = QPushButton('GO')
        GTLayout.addWidget(self.GoToButton,1,2)
        GTBox = QGroupBox("Go To Location (steps)")
        GTBox.setLayout(GTLayout)
        GTBox.setMinimumWidth(QT_XY_SETTER_WIDTH)
        GTBox.setMaximumWidth(QT_XY_SETTER_WIDTH)
        self.goToLayout.addWidget(GTBox,0,0)
            
    def createGoToAngleBox(self):
        """Creates a box with a go to Steps button and two spinboxes to set X and Y in degrees"""
        GTALayout = QGridLayout()
        self.GoToAngleSpinners = {}
        self.GoToAngleLabels = {}
        for dim,dimString in dimMap.items():
            self.GoToAngleLabels[dim] = QLabel(dimString)
            self.GoToAngleSpinners[dim] = QDoubleSpinBox()
            self.GoToAngleSpinners[dim].setValue(0)
            self.GoToAngleSpinners[dim].setMaximum(RAIL_APPROX_LENGTH_DEGREES)
            self.GoToAngleSpinners[dim].setDecimals(3)
            GTALayout.addWidget(self.GoToAngleLabels[dim],0,dim)
            GTALayout.addWidget(self.GoToAngleSpinners[dim],1,dim)
        self.GoToAngleButton = QPushButton('GO')
        GTALayout.addWidget(self.GoToAngleButton,1,2)
        GTABox = QGroupBox("Go To Angle")
        GTABox.setLayout(GTALayout)
        GTABox.setMinimumWidth(QT_XY_SETTER_WIDTH)
        GTABox.setMaximumWidth(QT_XY_SETTER_WIDTH)
        self.goToLayout.addWidget(GTABox,0,1)
        
    def createGoToMMBox(self):
        """Creates a box with a go to Steps button and two spinboxes to set X and Y in degrees"""
        Layout = QGridLayout()
        self.GoToMMSpinners = {}
        self.GoToMMLabels = {}
        for dim,dimString in dimMap.items():
            self.GoToMMLabels[dim] = QLabel(dimString)
            self.GoToMMSpinners[dim] = QDoubleSpinBox()
            self.GoToMMSpinners[dim].setValue(0)
            self.GoToMMSpinners[dim].setMaximum(RAIL_APPROX_LENGTH_MM)
            self.GoToMMSpinners[dim].setDecimals(3)
            Layout.addWidget(self.GoToMMLabels[dim],0,dim)
            Layout.addWidget(self.GoToMMSpinners[dim],1,dim)
        self.GoToMMButton = QPushButton('GO')
        Layout.addWidget(self.GoToMMButton,1,2)
        GTABox = QGroupBox("Go To MM")
        GTABox.setLayout(Layout)
        GTABox.setMinimumWidth(QT_XY_SETTER_WIDTH)
        GTABox.setMaximumWidth(QT_XY_SETTER_WIDTH)
        self.goToLayout.addWidget(GTABox,0,2)
        
    def createToolBox(self):
        """Generates a box for general tools/actions eg homing, panic etc
        """
        ToolLayout = QGridLayout()
        self.homeButton = QPushButton('home')
        self.stopButton = QPushButton('stop')
        self.stopButton.setStyleSheet("background-color: red;color: white")
        ToolLayout.addWidget(self.homeButton,0,0)
        ToolLayout.addWidget(self.stopButton,0,1)
        
        ToolBox = QGroupBox("Tools")
        ToolBox.setLayout(ToolLayout)
        self.goToLayout.addWidget(ToolBox)

    def createScriptEditor(self):
        """Creates a text entry box and execute button for scripts"""
        ScriptLayout = QGridLayout()
        self.scriptEditor = QPlainTextEdit()
        ScriptLayout.addWidget(self.scriptEditor)
        self.scriptExecuteButton = QPushButton('EXECUTE')
        self.scriptExecuteButton.setStyleSheet("background-color: green; color: white")
        ScriptLayout.addWidget(self.scriptExecuteButton)
        ScriptBox = QGroupBox("Script")
        ScriptBox.setLayout(ScriptLayout)
        self.generalLayout.addWidget(ScriptBox)

    def setExecuteStatusUI(self, status):
        if status:
            self.scriptExecuteButton.setStyleSheet(QT_STYLE_EXECUTE_RUNNING)
        else:
            self.scriptExecuteButton.setStyleSheet(QT_STYLE_EXECUTE_READY)

        

        
class PrinterController:
    #Printer controller cclass. master for basically everything.
    def __init__(self, view, xy, jetdrive, heater):
        """Create a printer controller. Acts as a bridge between UI and the various serial devices

        :param view: [description]
        :type view: [type]
        :param xy: [description]
        :type xy: [type]
        :param jetdrive: [description]
        :type jetdrive: [type]
        :param heater: [description]
        :type heater: [type]
        """
        self._view = view
        self._xy = xy
        self._script = SequenceHandler(self._xy)
        self._jetdrive = jetdrive
        self._heater = heater
        #self._bounds = bounds
        # Connect signals and slots
        self._connectSignals()
        #self.initialisePosition()
        self.createPoller()
        self.createExecutePoller()
        if QT_POLLER_ENABLED:
            time.sleep(1)
            self.startPoller()



        

    #functions for creation of a poller to check the mechanical values on the drivers        
    def createPoller(self):
        """Creates a poller that can monitor the state of the systems mechanical values (steps, angle, velocity and velocity setpoint)"""
        self.poller=QTimer()
        self.poller.timeout.connect(partial(self.updatePositionIndicator))

    def startPoller(self):
        """Start the driver poller"""
        self.poller.start(QT_POLLER_TIME_MS)

    def pausePoller(self):
        """Stop the driver poller"""
        self.poller.stop()

    def createExecutePoller(self):
        """Create a poller to track the state of the script"""
        self.executePoller=QTimer()
        self.executePoller.timeout.connect(partial(self.updateUIStatuses))
        self.executePoller.start(QT_POLLER_TIME_MS)

    def updateUIStatuses(self):
        self._view.setExecuteStatusUI(self._script.running)

    def _connectSignals(self):
        """Connects signals and slots."""
        
        for btnText, btn in self._view.joypadButtons.items():
            if btnText not in {'DROP'}:
                btn.clicked.connect(partial(self.buttonXY, btnText))

        
        self._view.joypadButtons['DROP'].clicked.connect(partial(self._jetdrive.fire))
        self._view.joypadButtons['DROP'].clicked.connect(partial(self.updatePositionIndicator))
        self._view.homeButton.clicked.connect(partial(self._xy.homeBoth))
        self._view.stopButton.clicked.connect(partial(self._xy.stopAll))
        self._view.GoToButton.clicked.connect(partial(self.goToFunc))
        self._view.GoToAngleButton.clicked.connect(partial(self.goToAngleFunc))
        self._view.GoToMMButton.clicked.connect(partial(self.goToMMFunc))
        self._view.keyPressed.connect(partial(self.keyXY))
        self._view.scriptExecuteButton.clicked.connect(partial(self.runScriptFunc))

    def goToFunc(self):
        for i in (0,1):
            target = int(self._view.GoToSpinners[i].text())
            #print(target)
            self._xy.moveStepsAbsolute(i,target)

    def goToAngleFunc(self):
        for i in (0,1):
            target = float(self._view.GoToAngleSpinners[i].text())
            #print(target)
            self._xy.moveAngleAbsolute(i,target)

    def goToMMFunc(self):
        """Go to the location, in mm, specified by the mm spinner
        """
        for i in (0,1):
            target = float(self._view.GoToMMSpinners[i].text())
            #print(target)
            target = conv.convert(target, 'mm', 'angle')
            self._xy.moveAngleAbsolute(i,target)

    def runScriptFunc(self):
        """Pass the currently edited script to the script handler and play it back
        """
        scriptString = self._view.scriptEditor.toPlainText()
        self._script.handleScript(scriptString)

    def buttonXY(self, text):
        """[Handle a joypad button press

        :param text: character label of the button - '>', '^' etc
        :type text: char
        """        
        distance = int(self._view.joypadDistanceSetter.text())

        signMap = CHEVRON_TO_SIGN_DICT

        sign = int(signMap.get(text, +1))
        distance = distance*sign


        axisMap = CHEVRON_TO_AXIS_DICT
        axis = axisMap.get(text, 0)
        self._xy.move(axis, distance)

    def keyXY(self, text):
        """Handle a single WASD keypress event

        :param text: key press character
        :type text: char
        """


        try:
            text = KEY_TO_CHEVRON_DICT[text]
        except KeyError:
            return
        
        distance = int(self._view.joypadDistanceSetter.text())
        
        signMap = CHEVRON_TO_SIGN_DICT
        sign = int(signMap.get(text, +1))
        distance = distance*sign


        axisMap = CHEVRON_TO_AXIS_DICT
        axis = axisMap.get(text, 0)
        self._xy.move(axis, distance)




    def updatePositionIndicator(self):
        """Function to request position and velocity data from each uStepper and print it on the LCDs"""
        #print("updating lcd")  

        """this bit does the voltages"""
        if QT_POLL_PSU:
            for i in range(0,2): #get power data and display it
                channel = i+1
                for  cmd, index in HeaterLCDvals.items():
                    if cmd != 'Channel':
                        self._heater.power.get(cmd,channel,'QUERY')
                        s = self._heater.power.poll_async()
                        if s != 'SANFAIL':
                            value = self._heater.power.get(cmd,channel,'REPLY')
                            if value != 'EMPTY':
                                self._view.HeaterLCDScreens[i,index].display(value)
                       
                    

        """this bit does the mechanical data"""
        if self._xy.isBlocking == 0:
            for i in range(0,2): #get positional data and display it
                data = self._xy.getData(i)
                for letter, number in data.items():
                    self._view.PILCDScreens[i,LCDvals.get(LETTER_TO_LCD.get(letter))].display(number)
                    if letter == 'S':
                        self._xy.currentPosition[i] = number
                        #print(self._xy.currentPosition)
                    if letter == 'A':
                        self._view.PILCDScreens[i,LCDvals.get('mm')].display(conv.convert(number,'angle','mm'))

            """this bit does the temp data"""
            tempData = self._xy.getTempData(TEMP_AXIS)
            #print(tempData)
            for letter, number in tempData.items():
                temp = conv.analogToTemp(number)
                if letter == 'B':                    
                    #print('Bed Temperature = ' + str(temp))
                    self._view._graph.update_plot(temp)
                if letter == 'N':
                    self._view._graph.update_other_plot(temp)
                    #print('Nozzle Temperature = ' + str(temp))

        



            
        

        
        
class XYSerialInterface:
    def __init__(self): #two serial interfaces, one with X and one with Y uStepper
        """Create the interface"""
        self.allocatePorts() #allocates its ports
        self.initialisePosition() 
        self.isBlocking = 0
        self.boundsController = EndstopBox()

        self.getBounds()
    def getBounds(self):
        if GET_BOUNDS_ON_STARTUP:
            self.homeBoth()

    def allocatePorts(self): 
        """Allocate and connect to X and Y ports.
        """


        print("connecting to steppers")
        for comport in serial.tools.list_ports.comports():
            if comport.serial_number == STAGE_X_SERIAL_NUMBER:
                self.portX = serial.Serial(comport.name, 115200, timeout=1)
            elif comport.serial_number == STAGE_Y_SERIAL_NUMBER:
                self.portY = serial.Serial(comport.name, 115200, timeout=1)

        try:
            self.portX
            self.portY
        except NameError: 
            print('error')      
   # Do something.

        #self.portX = serial.Serial(a, 115200, timeout=1)
        #self.portX.write(b'G4 V100 T2 D0\n')
        #self.portY = serial.Serial(b, 115200, timeout=1)

    def initialisePosition(self):
        self.currentPosition = {}
        self.currentPosition[0] = 0
        self.currentPosition[1] = 30

    def getCurrentPosition(self):
        return self.currentPosition
        
    def move(self, axis, steps):
        """Move a given number of steps relative to the current position

        :param axis: Axis to move
        :type axis: int
        :param steps: Number of steps to move
        :type steps: int
        """        

        self.command(axis, self.Gmove(steps))            
        #print(dimMap[axis] +" " + str(steps) + " steps")

    def moveStepsAbsolute(self, axis, steps):
        """Move to an absolute position in steps

        :param axis: Axis to move
        :type axis: int
        :param steps: Absolute step to move to
        :type steps: int
        """

        diff = int(steps - self.currentPosition[axis])
        print(diff)
        self.move(axis,diff)
        

    def moveAngleAbsolute(self, axis, angle):
        """Move to an absolute angle

        :param axis: axis to move
        :type axis: int
        :param angle: angle to move to
        :type angle: float
        """
        self.command(axis, self.GmoveAngleAbsolute(angle))


    def homeBoth(self):
        """Home both motors and reset their zero point
        """
        self.boundsController.maximumAngle[0] = self.home(0)
        self.boundsController.maximumAngle[1] = self.home(1)
        print("Rail lengths found: " + str(self.boundsController.maximumAngle))


    def home(self, axis):
        """Home a motor and return the distance it homed

        :param axis: Axis to home
        :type axis: bool
        :return: Rail length in degrees
        :rtype: float
        """
        self.command(axis, self.Ghome())
        dataDict = self.blockUntilRX(axis, 'DATA', True)
        return dataDict['A']

    def command(self, axis, data):
        """Sends a serial command to the specified axis

        :param axis: Axis to which the command is sent
        :type axis: int
        :param data: The command to be sent
        :type data: string
        """        
        self.axisToPort(axis).write(data)

    def blockUntilRX(self, axis, msg, passToParser):
        """Block until a specific message is reveived from the stepper

        :param axis: Axis to block
        :type axis: int
        :param msg: Message to wait for
        :type msg: string
        :param passToParser: If True, the message returned will be sent to the parser
        :type passToParser: bool
        :return: A dictionary containing data parsed from the message
        :rtype: dict
        """        
        self.isBlocking=1
        port = self.axisToPort(axis)
        print("blocking axis " + str(axis))

        flag = 0
        while flag == 0:
            
            msgRX = port.readline()
            msgRX = msgRX.decode('utf-8')
            #print(msgRX)
            if (msg in msgRX):
                flag = 1
                print("unblock axis " + str(axis))#
        self.isBlocking = 0
        if passToParser:
            
            dict1 = self.parseData(msgRX)
            return dict1





    def axisToPort(self, axis):
        if(axis == 0):
            return self.portX
        if(axis == 1):
            return self.portY

    def stopAll(self):
        """Stop all motors.
        """
        self.stop(1)
        self.stop(0)

    def stop(self,axis):
        """Stop motion on a given axis

        :param axis: axis to stop
        :type axis: int
        """
        self.command(axis,self.Gstop())

    def Gmove(self, steps):        
        datastring = 'G0 A' + str(steps) + '\n'
        return datastring.encode('utf-8')

    def GmoveAngleAbsolute(self, angle):
        """Generates GCode G1 to move the motor to a specified angle"""
        string = 'G1 A' +str(angle) + '\n'
        return string.encode('utf-8')

    def Ghome(self):
        """Generates GCode G4 to home the motor. at some point I should make the direction configurable"""
        datastring = 'G4 V100 T2 D1\n' #hardocded a threshold of 2 for now. seems to work fine.
        return datastring.encode('utf-8')

    def GgetData(self):
        """Generates GCode M15 to request positional data"""
        datastring = 'M15 \n'
        return datastring.encode('utf-8')

    def GgetTempData(self):
        """Generates GCode M17 to request temperature data"""
        datastring = 'M17 \n'
        return datastring.encode('utf-8')

    def Gstop(self):
        """Generates GCode M0 to stop a motor"""
        datastring = 'M0 \n'
        return datastring.encode('utf-8')

    def getData(self, axis):
        #print('getting status')
        reply = self.callResponse(self.GgetData(),self.axisToPort(axis))
        #print(reply)
        parsed = self.parseData(reply)
        #print(parsed)
        return parsed

    def getTempData(self, axis):
        reply = self.callResponse(self.GgetTempData(),self.axisToPort(axis))
        parsed = self.parseData(reply)
        return parsed

    def parseData(self, data): #parses data provided in format DATA A0.03 S0 V0.00 D0.00 from the M15 Gcode.
        seps = re.split(":? ", data)
        datadict = {}
        try:
            for s in seps:
                if ((s != 'DATA') and (s != 'TEMP')):
                    label = s[0]
                    val = re.findall(r"[-+]?\d*\.\d+|\d+", s) #weird regex. just trust it.
                    val = float(val[0])
                    datadict[label] = val
        except IndexError:
            print('Something went wrong parsing: ' + data)        
        return datadict

    def callResponse(self, message, port): #takes a port and a message for that port and returns the response given by the uStepperS
        #print(message)
        port.reset_input_buffer()
        port.write(message)
        msg =  port.readline()
        #print(msg)
        return msg.decode('utf-8')


class JetDriveSerialInterface: #serial interface with JetDrive
    def __init__(self, port):
        self.port = port

    def fire(self):
        print("drop")

#class TemperatureMonitorSerialInterface:
#    def __init__(self):

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



class EndstopBox: #class to manage the endstops of the system
    def __init__(self):
        self.maximumAngle = [10,10]
        self.minimumAngle = [0,0]

    def isInBounds(coords,units):
        #takes a two-item list coords = [x,y], with units of MM, angle or steps, and checks if it is in bounds
        flag = 0
        for i in (0,2):
            angle = conv.convert(coords[i],units,'angle')
            if angle > self.maximumAngle[i]:
                flag = 1
            if angle < self.minimumAngle[i]:
                flag = 1
        return ~flag



        
class psuController():
    def __init__(self, port):
        """class for controlling a power supply that provides power to the heater elements and the motors"""
        try:
            self.power = psu_serial.GPD_43038S(port)
            self.isConnected = True
        except:
            self.power = psu_serial.GPD_DUMMY
            self.isConnected = False
            print('PSU not found - using dummy instead.')
        self.power.turn_off()
        self.power.set_voltage(POW_HEATER_NOZZLE_INIT_VOLTAGE,POW_HEATER_NOZZLE_CHANNEL)
        self.power.set_current(POW_HEATER_NOZZLE_MAX_CURRENT,POW_HEATER_NOZZLE_CHANNEL)
        self.power.set_voltage(POW_HEATER_BED_INIT_VOLTAGE,POW_HEATER_BED_CHANNEL)
        self.power.set_current(POW_HEATER_BED_MAX_CURRENT,POW_HEATER_BED_CHANNEL)
        self.power.turn_on()
        self.toggle = False

    def change(self):
        if self.toggle:
            self.power.turn_off()
        else:
            self.power.turn_on()
        self.toggle = ~self.toggle




def main():
    """[Main function for the application]
    """
    print(WELCOME_MESSAGE)
    # Create an instance of QApplication
    printer = QApplication(sys.argv)
    # Show the printer's GUI
    view = PrinterUi()
    view.show()
    xyInterface = XYSerialInterface()
    jetdriveInterface = JetDriveSerialInterface(JETDRIVE_PORT)
    heaterPsu = psuController(HEATER_PSU_PORT)
    
    PrinterController(view=view, xy = xyInterface, jetdrive = jetdriveInterface, heater = heaterPsu)

    # Execute the printer's main loop
    sys.exit(printer.exec_())




if __name__ == '__main__':
    main()
