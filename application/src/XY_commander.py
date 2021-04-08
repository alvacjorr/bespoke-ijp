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

import numpy as np

import random
import datetime as dt
import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


from SequenceHandler import *
import psu_serial
from XYSerialInterface import *
from HeaterPIDController import *





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
        self.ydata = [random.randint(0, 80) for i in range(n_data)]

        n_data = 50
        self.xdata2 = list(range(n_data))
        self.ydata2 = [random.randint(0, 80) for i in range(n_data)]

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
            plot_refs = self.sc.axes.plot(self.xdata, self.ydata, 'r', label = 'bed')
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
            plot_refs = self.sc.axes.plot(self.xdata2, self.ydata2, 'r', label = 'bed2')
            self._plot_ref_2 = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref_2.set_ydata(self.ydata2)

        # Trigger the canvas to update and redraw.
        self.sc.draw()





class TriggerWindow(QWidget):
    def __init__(self, label = "untitled"):
        super().__init__()
        layout = QVBoxLayout()
        #self.windowTitle = label
        self.setWindowTitle('Trig. Config')
        self.label = label

        layout.addWidget(QLabel('LED Delay/us'))

        
        self.LEDDelaySpin = QSpinBox(minimum = TRIGGER_MIN_TIME, maximum = TRIGGER_MAX_TIME)
        layout.addWidget(self.LEDDelaySpin)
        
        layout.addWidget(QLabel('LED Exposure/us'))

        self.LEDExposureSpin = QSpinBox(minimum = TRIGGER_MIN_TIME, maximum = TRIGGER_MAX_TIME)
        layout.addWidget(self.LEDExposureSpin)

        layout.addWidget(QLabel('Second Strobe Delay/us'))

        self.LEDSecondSpin = QSpinBox(minimum = TRIGGER_MIN_TIME+10, maximum = TRIGGER_MAX_TIME)
        layout.addWidget(self.LEDSecondSpin)
        self.setButton = QPushButton('SET')
        #layout.addWidget(self.setButton)


        self.setLayout(layout)
        self.setWindowFlags(Qt.Tool)
        self.createShowButton()
        #self.core = TriggerWindow(label = label)


    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()


    def createShowButton(self):
        showLabel = 'Trig. Config'
        self.showButton = QPushButton(showLabel)
        self.showButton.clicked.connect(partial(self.toggle))




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

        self.inputLayout = QGridLayout()
        self.monitorLayout = QGridLayout()
        self.miLayout = QGridLayout()
        self.miLayout.addLayout(self.inputLayout,0,0)
        self.miLayout.addLayout(self.monitorLayout,0,1)
        self.createJoypad(self.inputLayout)
        self.goToLayout = QGridLayout()
        self.createGoToBox(self.inputLayout)
        self.createGoToAngleBox(self.inputLayout)
        self.createGoToMMBox(self.inputLayout)
        self.createPositionIndicator(self.monitorLayout)
        self.createHeaterIndicator(self.monitorLayout)

        self.createTriggerWindow()
        
        self.createToolBox(self.goToLayout)
        self.createScriptEditor(self.goToLayout)





        self.generalLayout.addLayout(self.miLayout)
        self.generalLayout.addLayout(self.goToLayout)

    def createTriggerWindow(self):
        self.triggerWindow = TriggerWindow()


        
    def keyPressEvent(self,event):
        """Handle a keypress event
        """
        super(PrinterUi, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())

    def createJoypad(self,l):
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
        l.addWidget(joypadBox,0,0,3,1) 

    def createPositionIndicator(self,l):
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

        l.addWidget(PIBox,1,0,1,3)

    def createHeaterIndicator(self,l):
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
            
            
        HeaterBox = QGroupBox("Heater Power (TESTING ONLY!!)")
        HeaterBox.setLayout(HeaterLayout)

        l.addWidget(HeaterBox,2,0,1,3)

    def createGoToBox(self,l):
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
        l.addWidget(GTBox,0,1)
            
    def createGoToAngleBox(self,l):
        """Creates a box with a go to Steps button and two spinboxes to set X and Y in degrees"""
        GTALayout = QGridLayout()
        self.GoToAngleSpinners = {}
        self.GoToAngleLabels = {}
        for dim,dimString in dimMap.items():
            self.GoToAngleLabels[dim] = QLabel(dimString)
            self.GoToAngleSpinners[dim] = QDoubleSpinBox()
            self.GoToAngleSpinners[dim].setValue(0)
            self.GoToAngleSpinners[dim].setMaximum(RAIL_APPROX_LENGTH_DEGREES)
            self.GoToAngleSpinners[dim].setMinimum(-RAIL_APPROX_LENGTH_DEGREES)
            self.GoToAngleSpinners[dim].setDecimals(3)
            GTALayout.addWidget(self.GoToAngleLabels[dim],0,dim)
            GTALayout.addWidget(self.GoToAngleSpinners[dim],1,dim)
        self.GoToAngleButton = QPushButton('GO')
        GTALayout.addWidget(self.GoToAngleButton,1,2)
        GTABox = QGroupBox("Go To Angle")
        GTABox.setLayout(GTALayout)
        GTABox.setMinimumWidth(QT_XY_SETTER_WIDTH)
        GTABox.setMaximumWidth(QT_XY_SETTER_WIDTH)
        l.addWidget(GTABox,1,1)
        
    def createGoToMMBox(self,l):
        """Creates a box with a go to Steps button and two spinboxes to set X and Y in degrees"""
        Layout = QGridLayout()
        self.GoToMMSpinners = {}
        self.GoToMMLabels = {}
        for dim,dimString in dimMap.items():
            self.GoToMMLabels[dim] = QLabel(dimString)
            self.GoToMMSpinners[dim] = QDoubleSpinBox()
            self.GoToMMSpinners[dim].setValue(0)
            self.GoToMMSpinners[dim].setMaximum(RAIL_APPROX_LENGTH_MM)
            self.GoToMMSpinners[dim].setMinimum(-RAIL_APPROX_LENGTH_MM)
            self.GoToMMSpinners[dim].setDecimals(3)
            Layout.addWidget(self.GoToMMLabels[dim],0,dim)
            Layout.addWidget(self.GoToMMSpinners[dim],1,dim)
        self.GoToMMButton = QPushButton('GO')
        Layout.addWidget(self.GoToMMButton,1,2)
        GTABox = QGroupBox("Go To MM")
        GTABox.setLayout(Layout)
        GTABox.setMinimumWidth(QT_XY_SETTER_WIDTH)
        GTABox.setMaximumWidth(QT_XY_SETTER_WIDTH)
        l.addWidget(GTABox,2,1)
        
    def createToolBox(self,l):
        """Generates a box for general tools/actions eg homing, panic etc
        """
        ToolLayout = QGridLayout()
        self.homeButton = QPushButton('home')
        self.stopButton = QPushButton('stop')
        self.stopButton.setStyleSheet("background-color: red;color: white")
        self.psuOnButton = QPushButton('heater on')
        self.psuOffButton = QPushButton('heater off')
        ToolLayout.addWidget(self.homeButton,0,0)
        ToolLayout.addWidget(self.stopButton,0,1)
        ToolLayout.addWidget(self.psuOnButton,0,2)
        ToolLayout.addWidget(self.psuOffButton,0,3)
        ToolLayout.addWidget(self.triggerWindow.showButton,0,4)
        
        

        ToolBox = QGroupBox("Tools")
        ToolBox.setLayout(ToolLayout)
        l.addWidget(ToolBox)

    def createScriptEditor(self,l):
        """Creates a text entry box and execute button for scripts"""
        ScriptLayout = QGridLayout()
        self.scriptEditor = QPlainTextEdit()
        ScriptLayout.addWidget(self.scriptEditor)
        self.scriptExecuteButton = QPushButton('EXECUTE')
        self.scriptExecuteButton.setStyleSheet("background-color: green; color: white")
        ScriptLayout.addWidget(self.scriptExecuteButton)
        ScriptBox = QGroupBox("Script")
        ScriptBox.setLayout(ScriptLayout)
        l.addWidget(ScriptBox)

    def setExecuteStatusUI(self, status):
        if status:
            self.scriptExecuteButton.setStyleSheet(QT_STYLE_EXECUTE_RUNNING)
        else:
            self.scriptExecuteButton.setStyleSheet(QT_STYLE_EXECUTE_READY)

        

        
class PrinterController:
    """Printer controller cclass. master for basically everything."""
    def __init__(self, view, xy, jetdrive, heater):
        """Create a printer controller. Acts as a bridge between UI and the various serial devices

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
        
        self.bed_controller = HeaterPIDController(1,'Bed',self._heater,QT_POLLER_TIME_MS/1000, 2.5)
        #self.bed_controller.show_graphs()
        self._view.generalLayout.addWidget(self.bed_controller._ui.showButton)

        self.nozzle_controller = HeaterPIDController(2,'Nozzle',self._heater,QT_POLLER_TIME_MS/1000, 2.5)
        #self.bed_controller.show_graphs()
        self._view.generalLayout.addWidget(self.nozzle_controller._ui.showButton)

        



        

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

        
        self._view.joypadButtons['DROP'].clicked.connect(partial(self._xy.trigger,TRIGGER_AXIS,'A'))
        #self._view.joypadButtons['DROP'].clicked.connect(partial(self.updatePositionIndicator))
        self._view.homeButton.clicked.connect(partial(self._xy.homeBoth))
        self._view.stopButton.clicked.connect(partial(self._xy.stopAll))
        self._view.psuOnButton.clicked.connect(self._heater.power.turn_on)
        self._view.psuOffButton.clicked.connect(self._heater.power.turn_off)
        self._view.GoToButton.clicked.connect(partial(self.goToFunc))
        self._view.GoToAngleButton.clicked.connect(partial(self.goToAngleFunc))
        self._view.GoToMMButton.clicked.connect(partial(self.goToMMFunc))
        self._view.keyPressed.connect(partial(self.keyXY))
        self._view.scriptExecuteButton.clicked.connect(partial(self.runScriptFunc))
        self._view.triggerWindow.setButton.clicked.connect(partial(self.setTriggerFunc))
        self._view.triggerWindow.LEDDelaySpin.valueChanged.connect(partial(self.setTriggerFunc))
        self._view.triggerWindow.LEDExposureSpin.valueChanged.connect(partial(self.setTriggerFunc))
        self._view.triggerWindow.LEDSecondSpin.valueChanged.connect(partial(self.setTriggerFunc))


    def setTriggerFunc(self, value = 0):
        """Function call to configure the triggers/timing, based upon the SpinBoxes in triggerWindow
        """        
        delay = self._view.triggerWindow.LEDDelaySpin.value()
        exposure = self._view.triggerWindow.LEDExposureSpin.value()
        second = self._view.triggerWindow.LEDSecondSpin.value()

        self._view.triggerWindow.LEDSecondSpin.setMinimum(exposure+10)
        self._xy.setDurations(TRIGGER_AXIS, delay, exposure,second)

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
        """Update LCDs with mechanical data from uSteps"""
        #print("updating lcd")  

        
        #self.updatePowerSupplyIndicator()
        self.updateTemperatureIndicator()
                       
                    

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



    def updateTemperatureIndicator(self):
        """Update GUI temperature data
        """            
        tempData = self._xy.getTempData(TEMP_AXIS)
        #print(tempData)
        for letter, number in tempData.items():
            temp = conv.analogToTemp(number)
            if letter == 'B':                    
                #print('Bed Temperature = ' + str(temp))
                self.bed_controller.update(temp)
            if letter == 'N':
                #print('Nozzle Temperature = ' + str(temp))
                self.nozzle_controller.update(temp)

            


    def updatePowerSupplyIndicator(self):
        """Update GUI components with PSU data
        """        
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
        

        



            
        

        
        


class JetDriveSerialInterface: #serial interface with JetDrive
    def __init__(self, port):
        self.port = port

    def fire(self):
        print("drop")

#class TemperatureMonitorSerialInterface:
#    def __init__(self):








        
class psuController():
    def __init__(self, port):
        """class for controlling a power supply that provides power to the heater elements and the motors"""
        try:
            self.power = psu_serial.GPD_4303S(port)
            self.isConnected = True
        except:
            self.power = psu_serial.GPD_DUMMY
            self.isConnected = False
            print('PSU not found - using dummy instead.')
        self.power.turn_on()





def main():
    """Main function for the application
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
