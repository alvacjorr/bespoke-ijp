from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit,
    QTextEdit,
    QCheckBox,
    QHBoxLayout,
)
from PySide2.QtWidgets import (
    QGridLayout,
    QLineEdit,
    QMainWindow,
    QSpinBox,
    QLCDNumber,
    QGroupBox,
    QDoubleSpinBox,
)
from PySide2.QtCore import Slot, Qt, QTimer, QDateTime, Signal, QObject, Signal
from PySide2.QtGui import QTextCursor
import sys
from functools import partial
import serial
import serial.tools.list_ports
import re
import photofluor
from constants import *


import time


import conversions as conv

import numpy as np

import random
import datetime as dt
import matplotlib

matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


from SequenceHandler import *
import psu_serial
from XYSerialInterface import *
from HeaterPIDController import *



class EmittingStream(QObject):

    textWritten = Signal(str)

    def write(self, text):
        self.textWritten.emit(str(text))



class MplCanvas(FigureCanvasQTAgg):
    """summary

    :param FigureCanvasQTAgg: [description]
    :type FigureCanvasQTAgg: [type]
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(1, 2, 1)
        self.axes2 = fig.add_subplot(1, 2, 2)
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
            plot_refs = self.sc.axes.plot(self.xdata, self.ydata, "r", label="bed")
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
            plot_refs = self.sc.axes.plot(self.xdata2, self.ydata2, "r", label="bed2")
            self._plot_ref_2 = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref_2.set_ydata(self.ydata2)

        # Trigger the canvas to update and redraw.
        self.sc.draw()


class TriggerWindow(QWidget):
    def __init__(self, label="untitled"):
        super().__init__()
        layout = QHBoxLayout()

        self.setWindowTitle("Trig. Config")

        self.label = label

        layout.addWidget(self.createTimingBox())
        layout.addWidget(self.createProgressiveBox())
        layout.addWidget(self.createContinuousBox())

        self.setLayout(layout)
        self.setWindowFlags(Qt.Tool)
        self.createShowButton()
        # self.core = TriggerWindow(label = label)

    def createProgressiveBox(self):
        progressiveLayout = QVBoxLayout()
        progressiveBox = QGroupBox("Progressive")

        self.progressiveModeCheckBox = QCheckBox("Enable")
        progressiveLayout.addWidget(self.progressiveModeCheckBox)
        progressiveLayout.addWidget(QLabel("Distance/mm"))
        self.progressiveMMPeriodSpin = QDoubleSpinBox(minimum=0.01, maximum=100, suffix = " mm", singleStep = 0.01)
        progressiveLayout.addWidget(self.progressiveMMPeriodSpin)

        progressiveBox.setLayout(progressiveLayout)
        return progressiveBox

    def createContinuousBox(self):
        layout = QVBoxLayout()
        box = QGroupBox("Continuous")

        self.continuousModeCheckBox = QCheckBox("Enable")
        layout.addWidget(self.continuousModeCheckBox)
        layout.addWidget(QLabel("Frequency"))
        self.continuousFrequencySpin = QSpinBox(minimum=1, maximum=1000, suffix = " Hz", singleStep = 1)
        layout.addWidget(self.continuousFrequencySpin)

        box.setLayout(layout)


        return box

    def createTimingBox(self):
        timingLayout = QVBoxLayout()
        timingBox = QGroupBox("Timing")

        timingLayout.addWidget(QLabel("Camera Max FPS"))
        self.CameraFPSSpin = QSpinBox(minimum = 1, maximum = 120)
        self.CameraFPSSpin.setValue(20)
        timingLayout.addWidget(self.CameraFPSSpin)

        timingLayout.addWidget(QLabel("LED Delay/us"))

        self.LEDDelaySpin = QSpinBox(minimum=TRIGGER_MIN_TIME, maximum=TRIGGER_MAX_TIME)
        timingLayout.addWidget(self.LEDDelaySpin)

        timingLayout.addWidget(QLabel("LED Exposure/us"))

        self.LEDExposureSpin = QSpinBox(
            minimum=TRIGGER_MIN_TIME, maximum=TRIGGER_MAX_TIME
        )
        timingLayout.addWidget(self.LEDExposureSpin)

        timingLayout.addWidget(QLabel("Second Strobe Delay/us"))

        self.LEDSecondSpin = QSpinBox(
            minimum=TRIGGER_MIN_TIME + 10, maximum=TRIGGER_MAX_TIME
        )
        timingLayout.addWidget(self.LEDSecondSpin)
        self.setButton = QPushButton("SET")
        # layout.addWidget(self.setButton)

        self.secondPulseEnable = QCheckBox("Double Pulse")
        timingLayout.addWidget(self.secondPulseEnable)

        timingBox.setLayout(timingLayout)

        return timingBox

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def createShowButton(self):
        showLabel = "Trig. Config"
        self.showButton = QPushButton(showLabel)
        self.showButton.clicked.connect(partial(self.toggle))


class PhotoFluorWindow(QWidget):
    def __init__(self, label="untitled"):
        super().__init__()

        self.pf = photofluor.PhotoFluor_II('COM4')

        layout = QVBoxLayout()

        self.setWindowTitle("PhotoFluor")

        self.setLayout(layout)
        self.setWindowFlags(Qt.Tool)
        self.createShowButton()
        # self.core = TriggerWindow(label = label)

        self.shutterOpenButton  = QPushButton("Shutter Open")
        self.shutterCloseButton = QPushButton("Shutter Close")
        layout.addWidget(self.shutterOpenButton)
        layout.addWidget(self.shutterCloseButton)

        self.shutterOpenButton.clicked.connect(partial(self.pf.shutter_open))
        self.shutterCloseButton.clicked.connect(partial(self.pf.shutter_close))


    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def createShowButton(self):
        showLabel = "PhotoFluor"
        self.showButton = QPushButton(showLabel)
        self.showButton.clicked.connect(partial(self.toggle))

class GridMacroWindow(QWidget):
    def __init__(self, label="Grid Stuff"):
        super().__init__()


        self.label = label
        layout = QVBoxLayout()

        self.setWindowTitle(label)

        self.setLayout(layout)
        self.setWindowFlags(Qt.Tool)
        self.createShowButton()
        # self.core = TriggerWindow(label = label)

        self.beginButton  = QPushButton("Begin")

        self.gridXSetter = QSpinBox(minimum = 1, maximum = GRID_MAX_DROPS)
        self.gridYSetter = QSpinBox(minimum = 1, maximum = GRID_MAX_DROPS)

        self.gridXSepSetter = QSpinBox(minimum = 1, maximum = 20000)
        self.gridYSepSetter = QSpinBox(minimum = 1, maximum = 20000)

        layout.addWidget(QLabel("x"))
        layout.addWidget(self.gridXSetter)
        layout.addWidget(QLabel("y"))
        layout.addWidget(self.gridYSetter)
        layout.addWidget(QLabel("dx/steps"))
        layout.addWidget(self.gridXSepSetter)
        layout.addWidget(QLabel("dy/steps"))
        layout.addWidget(self.gridYSepSetter)
        layout.addWidget(self.beginButton)


    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def createShowButton(self):
        showLabel = self.label
        self.showButton = QPushButton(showLabel)
        self.showButton.clicked.connect(partial(self.toggle))


class PrinterUi(QMainWindow):
    """Main UI

    :param QMainWindow: [description]
    :type QMainWindow: [type]
    """
    
    def closeEvent(self,event):
        self.close_signal.emit()


    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.consoleOut.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.consoleOut.setTextCursor(cursor)
        self.consoleOut.ensureCursorVisible()
    keyPressed = Signal(int)

    close_signal = Signal()

    def __init__(self):
        """Creates the UI"""

        super().__init__()

        

        self.consoleOut = QTextEdit()
        self.consoleOut.setStyleSheet("background-color: black;color: white")
        self.consoleOut.setReadOnly(True)
        # Install the custom output stream
        if QT_REDIRECT_STDERR:

            #sys.stdout = EmittingStream()
            sys.stderr = EmittingStream()
            #sys.stdout.textWritten.connect(self.normalOutputWritten)
            sys.stderr.textWritten.connect(self.normalOutputWritten)

        if QT_REDIRECT_STDOUT:

            sys.stdout = EmittingStream()
            #sys.stderr = EmittingStream()
            sys.stdout.textWritten.connect(self.normalOutputWritten)
            #sys.stderr.textWritten.connect(self.normalOutputWritten)
        
        print(WELCOME_MESSAGE)
        # Set some main window's properties
        self.setWindowTitle(QT_MAIN_WINDOW_TITLE)
        # self.setFixedSize(300, 300)
        # Set the central widget and properties
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self.inputLayout = QGridLayout()
        self.monitorLayout = QGridLayout()
        self.miLayout = QGridLayout()
        self.miLayout.addLayout(self.inputLayout, 0, 0)
        self.miLayout.addLayout(self.monitorLayout, 0, 1)
        self.createJoypad(self.inputLayout)
        self.goToLayout = QGridLayout()
        self.createGoToBox(self.inputLayout)
        self.createGoToAngleBox(self.inputLayout)
        self.createGoToMMBox(self.inputLayout)
        self.createPositionIndicator(self.monitorLayout)
        self.createHeaterIndicator(self.monitorLayout)

        self.createTriggerWindow()
        self.createPhotoFluorWindow()
        self.createGridMacroWindow()
        self.createToolBox(self.goToLayout)
        self.createScriptEditor(self.goToLayout)

        self.goToLayout.addWidget(self.consoleOut)

        self.generalLayout.addLayout(self.miLayout)
        self.generalLayout.addLayout(self.goToLayout)

    def createTriggerWindow(self):
        self.triggerWindow = TriggerWindow()

    def createPhotoFluorWindow(self):
        self.photoFluorWindow = PhotoFluorWindow()

    def createGridMacroWindow(self):
        self.gridMacroWindow = GridMacroWindow()

    def keyPressEvent(self, event):
        """Handle a keypress event"""
        super(PrinterUi, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())

    def createJoypad(self, l):
        """Creates a joypad to control the XY motion, with a 'DROP' button in the middle"""
        self.joypadButtons = {}
        joypadLayout = QGridLayout()
        joypadButtons = {
            "^": (0, 1),
            "v": (2, 1),
            ">": (1, 2),
            "<": (1, 0),
            "DROP": (1, 1),
            "BURST": (0,0),
        }
        for btnText, pos in joypadButtons.items():
            self.joypadButtons[btnText] = QPushButton(btnText)
            self.joypadButtons[btnText].setFixedSize(40, 40)
            joypadLayout.addWidget(self.joypadButtons[btnText], pos[0], pos[1])


        self.joypadBurstSetter = QSpinBox()
        self.joypadBurstSetter.setMinimum(1)
        self.joypadBurstSetter.setSingleStep(1)
        self.joypadBurstSetter.setMaximum(100)
        self.joypadBurstSetter.setValue(1)
        joypadLayout.addWidget(self.joypadBurstSetter, 0, 2)    

        self.joypadDistanceSetter = QSpinBox()
        self.joypadDistanceSetter.setMinimum(0)
        self.joypadDistanceSetter.setSingleStep(QT_JOYSTICK_STEP_INCREMENT)
        self.joypadDistanceSetter.setMaximum(QT_JOYSTICK_MAXIMUM_STEPS)
        self.joypadDistanceSetter.setValue(QT_JOYSTICK_STEP_INCREMENT)
        joypadLayout.addWidget(self.joypadDistanceSetter, 2, 2)



        joypadBox = QGroupBox("Joypad")
        joypadBox.setLayout(joypadLayout)
        joypadBox.setMinimumHeight(QT_JOYPAD_HEIGHT)
        joypadBox.setMinimumWidth(QT_JOYPAD_WIDTH)
        joypadBox.setMaximumHeight(QT_JOYPAD_HEIGHT)
        joypadBox.setMaximumWidth(QT_JOYPAD_WIDTH)
        l.addWidget(joypadBox, 0, 0, 3, 1)

    def createPositionIndicator(self, l):
        """Create an LCD position indicator for X and Y"""
        PILayout = QGridLayout()
        self.PILCDScreens = {}
        self.PILCDLabels = {}
        LCDHeaderOffset = 1

        for valName, valIndex in LCDvals.items():
            for dim, dimString in dimMap.items():
                if valName == "axis":
                    self.PILCDLabels[dim] = QLabel(dimString)
                    PILayout.addWidget(self.PILCDLabels[dim], dim + LCDHeaderOffset, 0)
                else:
                    self.PILCDScreens[dim, valIndex] = QLCDNumber()
                    self.PILCDScreens[dim, valIndex].setDigitCount(6)
                    self.PILCDScreens[dim, valIndex].setFixedSize(100, 40)
                    PILayout.addWidget(
                        self.PILCDScreens[dim, valIndex],
                        dim + LCDHeaderOffset,
                        1 + valIndex,
                    )

            PILayout.addWidget(QLabel(valName), 0, 1 + valIndex)

        PIBox = QGroupBox("Current Position")
        PIBox.setLayout(PILayout)

        l.addWidget(PIBox, 1, 0, 1, 3)

    def createHeaterIndicator(self, l):
        HeaterLayout = QGridLayout()
        self.HeaterLCDScreens = {}
        self.HeaterLCDLabels = {}

        LCDHeaderOffset = 1

        for valName, valIndex in HeaterLCDvals.items():
            for dim, dimString in HeaterChannelNames.items():
                if valName == "Channel":
                    self.HeaterLCDLabels[dim] = QLabel(dimString)
                    HeaterLayout.addWidget(
                        self.HeaterLCDLabels[dim], dim + LCDHeaderOffset, 0
                    )
                else:
                    self.HeaterLCDScreens[dim, valIndex] = QLCDNumber()
                    self.HeaterLCDScreens[dim, valIndex].setDigitCount(6)
                    self.HeaterLCDScreens[dim, valIndex].setFixedSize(100, 40)
                    HeaterLayout.addWidget(
                        self.HeaterLCDScreens[dim, valIndex],
                        dim + LCDHeaderOffset,
                        1 + valIndex,
                    )

            HeaterLayout.addWidget(QLabel(valName), 0, 1 + valIndex)

        HeaterBox = QGroupBox("Heater Power (TESTING ONLY!!)")
        HeaterBox.setLayout(HeaterLayout)

        l.addWidget(HeaterBox, 2, 0, 1, 3)

    def createGoToBox(self, l):
        """Creates a box with a go to Steps button and two spinboxes to set X and Y in steps"""
        GTLayout = QGridLayout()
        self.GoToSpinners = {}
        self.GoToLabels = {}
        for dim, dimString in dimMap.items():
            self.GoToLabels[dim] = QLabel(dimString)
            self.GoToSpinners[dim] = QSpinBox()
            self.GoToSpinners[dim].setValue(1)
            self.GoToSpinners[dim].setMaximum(RAIL_APPROX_LENGTH_STEPS)
            GTLayout.addWidget(self.GoToLabels[dim], 0, dim)
            GTLayout.addWidget(self.GoToSpinners[dim], 1, dim)
        self.GoToButton = QPushButton("GO")
        GTLayout.addWidget(self.GoToButton, 1, 2)
        GTBox = QGroupBox("Go To Location (steps)")
        GTBox.setLayout(GTLayout)
        GTBox.setMinimumWidth(QT_XY_SETTER_WIDTH)
        GTBox.setMaximumWidth(QT_XY_SETTER_WIDTH)
        l.addWidget(GTBox, 0, 1)

    def createGoToAngleBox(self, l):
        """Creates a box with a go to Steps button and two spinboxes to set X and Y in degrees"""
        GTALayout = QGridLayout()
        self.GoToAngleSpinners = {}
        self.GoToAngleLabels = {}
        for dim, dimString in dimMap.items():
            self.GoToAngleLabels[dim] = QLabel(dimString)
            self.GoToAngleSpinners[dim] = QDoubleSpinBox()
            self.GoToAngleSpinners[dim].setValue(0)
            self.GoToAngleSpinners[dim].setMaximum(RAIL_APPROX_LENGTH_DEGREES)
            self.GoToAngleSpinners[dim].setMinimum(-RAIL_APPROX_LENGTH_DEGREES)
            self.GoToAngleSpinners[dim].setDecimals(3)
            GTALayout.addWidget(self.GoToAngleLabels[dim], 0, dim)
            GTALayout.addWidget(self.GoToAngleSpinners[dim], 1, dim)
        self.GoToAngleButton = QPushButton("GO")
        GTALayout.addWidget(self.GoToAngleButton, 1, 2)
        GTABox = QGroupBox("Go To Angle")
        GTABox.setLayout(GTALayout)
        GTABox.setMinimumWidth(QT_XY_SETTER_WIDTH)
        GTABox.setMaximumWidth(QT_XY_SETTER_WIDTH)
        l.addWidget(GTABox, 1, 1)

    def createGoToMMBox(self, l):
        """Creates a box with a go to Steps button and two spinboxes to set X and Y in degrees"""
        Layout = QGridLayout()
        self.GoToMMSpinners = {}
        self.GoToMMLabels = {}
        for dim, dimString in dimMap.items():
            self.GoToMMLabels[dim] = QLabel(dimString)
            self.GoToMMSpinners[dim] = QDoubleSpinBox()
            self.GoToMMSpinners[dim].setValue(0)
            self.GoToMMSpinners[dim].setMaximum(RAIL_APPROX_LENGTH_MM)
            self.GoToMMSpinners[dim].setMinimum(-RAIL_APPROX_LENGTH_MM)
            self.GoToMMSpinners[dim].setDecimals(3)
            Layout.addWidget(self.GoToMMLabels[dim], 0, dim)
            Layout.addWidget(self.GoToMMSpinners[dim], 1, dim)
        self.GoToMMButton = QPushButton("GO")
        Layout.addWidget(self.GoToMMButton, 1, 2)
        GTABox = QGroupBox("Go To MM")
        GTABox.setLayout(Layout)
        GTABox.setMinimumWidth(QT_XY_SETTER_WIDTH)
        GTABox.setMaximumWidth(QT_XY_SETTER_WIDTH)
        l.addWidget(GTABox, 2, 1)

    def createToolBox(self, l):
        """Generates a box for general tools/actions eg homing, panic etc"""
        ToolLayout = QGridLayout()
        self.homeButton = QPushButton("home")
        self.stopButton = QPushButton("stop")
        self.stopButton.setStyleSheet("background-color: red;color: white")
        self.psuOnButton = QPushButton("heater on")
        self.psuOffButton = QPushButton("heater off")
        ToolLayout.addWidget(self.homeButton, 0, 0)
        ToolLayout.addWidget(self.stopButton, 0, 1)
        ToolLayout.addWidget(self.psuOnButton, 0, 2)
        ToolLayout.addWidget(self.psuOffButton, 0, 3)
        ToolLayout.addWidget(self.triggerWindow.showButton, 0, 4)
        ToolLayout.addWidget(self.photoFluorWindow.showButton, 0, 5)
        ToolLayout.addWidget(self.gridMacroWindow.showButton,0, 6)

        ToolBox = QGroupBox("Tools")
        ToolBox.setLayout(ToolLayout)
        l.addWidget(ToolBox)

    def createScriptEditor(self, l):
        """Creates a text entry box and execute button for scripts"""
        ScriptLayout = QGridLayout()
        self.scriptEditor = QPlainTextEdit()
        ScriptLayout.addWidget(self.scriptEditor)
        self.scriptExecuteButton = QPushButton("EXECUTE")
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

class GridController:
    """Class to control async grid printing
    """
    def __init__(self,xy,view):
        self._xy = xy
        self._view = view
        self.createPoller()
        self.pollTime = GRID_POLL_MS
        self.x = 0
        self.nx = 0
        self.y = 0
        self.ny = 0
        self.dx = 0
        self.dy = 0
        self.x0 = 0
        self.y0 = 0

    def createPoller(self):
        self.poller = QTimer()
        self.poller.timeout.connect(partial(self.handle))

    def startPoller(self):
        self.poller.start(self.pollTime)

    def stopPoller(self):
        self.poller.stop()

    def trigger(self):
        self._xy.trigger(TRIGGER_AXIS, "A")

    def handle(self):

    def gridAsyncStartDefault():
        """Starts grid printing with standard values taken from the GUI
        """
        gridAsyncStart(self._view.gridMacroWindow.gridXSetter.value(),self._view.gridMacroWindow.gridYSetter.value(),self._view.gridMacroWindow.gridXSepSetter.value(),self._view.gridMacroWindow.gridYSepSetter.value(),self._xy.currentPosition[0],self._xy.currentPosition[1])


    def gridAsyncStart(nx, ny, dx, dy, x0, y0):
        """Function to initiate grid printing with chosen paramaters.
        """

        print("Printing grid started.")
        self.x = 0
        self.y = 0
        self.nx = nx
        self.ny = ny
        self.dx = dx
        self.dy = dy
        self.x0 = x0
        self.y0 = y0





        self.xTotalWidth = (nx-1)*dx
        self.yTotalWidth = (ny-1)*dy
        print("Printing Grid")
        

        for x in range(0, nx):            

            for y in range(0, ny):
                self._xy.trigger(TRIGGER_AXIS, "A")
                print("print at " + str(x) + ", " + str(y))
                time.sleep(GRID_TIME_DELAY_MS/1000)
                if (y!=(ny-1)):
                    self._xy.move(1, dy)
                    time.sleep(GRID_TIME_DELAY_MS/1000)

            self._xy.move(1, -yTotalWidth)
            time.sleep(ny*GRID_TIME_DELAY_MS/1000)
            if (GRID_BACKLASH_COMPENSATION_ENABLED):
                self._xy.move(1, -GRID_BACKLASH_COMPENSATION_STEPS)
                time.sleep(GRID_TIME_DELAY_MS/1000)
                self._xy.move(1, GRID_BACKLASH_COMPENSATION_STEPS)
                time.sleep(GRID_TIME_DELAY_MS/1000)
            if (x!= (nx-1)):
                self._xy.move(0, dx)
                time.sleep(GRID_TIME_DELAY_MS/1000)
        self._xy.move(0, -xTotalWidth)
        time.sleep(nx*GRID_TIME_DELAY_MS/1000)


        self.poller.start()





class PrinterController:
    """Printer controller cclass. master for basically everything."""

    def __init__(self, view, xy, jetdrive, heater):
        """Create a printer controller. Acts as a bridge between UI and the various serial devices"""
        self._view = view
        self._xy = xy
        self._script = SequenceHandler(self._xy)
        self._jetdrive = jetdrive
        self._heater = heater
        # self._bounds = bounds
        # Connect signals and slots
        self._connectSignals()
        # self.initialisePosition()
        self.createPoller()
        self.createExecutePoller()

        self.gridController = GridController(self._xy, self._view)
        
        if QT_POLLER_ENABLED:
            time.sleep(1)
            self.startPoller()

        self.bed_controller = HeaterPIDController(
            POW_HEATER_BED_CHANNEL, "Bed", self._heater, QT_POLLER_TIME_MS / 1000,POW_HEATER_BED_MAX_CURRENT , POW_HEATER_BED_MAX_VOLTAGE
        )
        # self.bed_controller.show_graphs()
        self._view.generalLayout.addWidget(self.bed_controller._ui.showButton)

        self.nozzle_controller = HeaterPIDController(
            POW_HEATER_NOZZLE_CHANNEL, "Nozzle", self._heater, QT_POLLER_TIME_MS / 1000, POW_HEATER_NOZZLE_MAX_CURRENT, POW_HEATER_NOZZLE_MAX_VOLTAGE
        )
        # self.bed_controller.show_graphs()
        self._view.generalLayout.addWidget(self.nozzle_controller._ui.showButton)

    # functions for creation of a poller to check the mechanical values on the drivers
    def createPoller(self):
        """Creates a poller that can monitor the state of the systems mechanical values (steps, angle, velocity and velocity setpoint)"""
        self.poller = QTimer()
        self.poller.timeout.connect(partial(self.updatePositionIndicator))


    def startPoller(self):
        """Start the driver poller"""
        self.poller.start(QT_POLLER_TIME_MS)

    def pausePoller(self):
        """Stop the driver poller"""
        self.poller.stop()

    def createExecutePoller(self):
        """Create a poller to track the state of the script"""
        self.executePoller = QTimer()
        self.executePoller.timeout.connect(partial(self.updateUIStatuses))
        self.executePoller.start(QT_POLLER_TIME_MS)

    def updateUIStatuses(self):
        self._view.setExecuteStatusUI(self._script.running)

    def closeFunc(self):
        self._heater.power.turn_off()
        print("Power Supply turned off.")
        print("Exiting...")

    def _connectSignals(self):
        """Connects signals and slots."""

        for btnText, btn in self._view.joypadButtons.items():
            if btnText not in {"DROP", "BURST"}:
                btn.clicked.connect(partial(self.buttonXY, btnText))

        self._view.joypadButtons["DROP"].clicked.connect(
            partial(self._xy.trigger, TRIGGER_AXIS, "A")
        )
        self._view.joypadButtons["BURST"].clicked.connect(
            partial(self.burstFunc)
        )
        # self._view.joypadButtons['DROP'].clicked.connect(partial(self.updatePositionIndicator))
        self._view.homeButton.clicked.connect(partial(self._xy.homeBoth))
        self._view.stopButton.clicked.connect(partial(self._xy.stopAll))
        self._view.psuOnButton.clicked.connect(self._heater.power.turn_on)
        self._view.psuOffButton.clicked.connect(self._heater.power.turn_off)
        self._view.GoToButton.clicked.connect(partial(self.goToFunc))
        self._view.GoToAngleButton.clicked.connect(partial(self.goToAngleFunc))
        self._view.GoToMMButton.clicked.connect(partial(self.goToMMFunc))
        self._view.keyPressed.connect(partial(self.keyXY))
        self._view.scriptExecuteButton.clicked.connect(partial(self.runScriptFunc))

        # Trigger Timing Config
        self._view.triggerWindow.setButton.clicked.connect(partial(self.setTriggerFunc))
        self._view.triggerWindow.LEDDelaySpin.valueChanged.connect(
            partial(self.setTriggerFunc)
        )
        self._view.triggerWindow.LEDExposureSpin.valueChanged.connect(
            partial(self.setTriggerFunc)
        )
        self._view.triggerWindow.LEDSecondSpin.valueChanged.connect(
            partial(self.setTriggerFunc)
        )
        self._view.triggerWindow.secondPulseEnable.stateChanged.connect(
            partial(self.setTriggerFunc)
        )
        self._view.triggerWindow.CameraFPSSpin.valueChanged.connect(
            partial(self.setTriggerFunc)
        )

        self._view.triggerWindow.progressiveMMPeriodSpin.valueChanged.connect(
            partial(self.configureTriggerProgressiveFunc)
        )
        self._view.triggerWindow.progressiveModeCheckBox.stateChanged.connect(
            partial(self.configureTriggerProgressiveFunc)
        )

        self._view.triggerWindow.continuousFrequencySpin.valueChanged.connect(
            partial(self.configureTriggerContinuousFunc)
        )
        self._view.triggerWindow.continuousModeCheckBox.stateChanged.connect(
            partial(self.configureTriggerContinuousFunc)
        )
        self._view.gridMacroWindow.beginButton.clicked.connect(partial(self.gridFunc))

        self._view.close_signal.connect(partial(self.closeFunc))



    def setTriggerFunc(self, value=0):
        """Function call to configure the triggers/timing, based upon the SpinBoxes in triggerWindow"""
        delay = self._view.triggerWindow.LEDDelaySpin.value()
        exposure = self._view.triggerWindow.LEDExposureSpin.value()
        second = self._view.triggerWindow.LEDSecondSpin.value()

        tog = self._view.triggerWindow.secondPulseEnable.isChecked()
        fps = self._view.triggerWindow.CameraFPSSpin.value()

        self._view.triggerWindow.LEDSecondSpin.setMinimum(exposure + 10)
        self._xy.setDurations(TRIGGER_AXIS, delay, exposure, second, tog, fps)

    def configureTriggerProgressiveFunc(self, value=0):
        tog = self._view.triggerWindow.progressiveModeCheckBox.isChecked()
        distance = self._view.triggerWindow.progressiveMMPeriodSpin.value()
        angle = conv.convert(distance,"mm","angle")
        self._xy.configureTriggerProgressive(TRIGGER_AXIS, tog, angle)

    def configureTriggerContinuousFunc(self, value = 0):
        tog = self._view.triggerWindow.continuousModeCheckBox.isChecked()
        freq = self._view.triggerWindow.continuousFrequencySpin.value()
        self._xy.configureTriggerContinuous(TRIGGER_AXIS, freq, tog)

    def goToFunc(self):
        for i in (0, 1):
            target = int(self._view.GoToSpinners[i].text())
            # print(target)
            self._xy.moveStepsAbsolute(i, target)

   

    def goToAngleFunc(self):
        for i in (0, 1):
            target = float(self._view.GoToAngleSpinners[i].text())
            # print(target)
            self._xy.moveAngleAbsolute(i, target)

    def goToMMFunc(self):
        """Go to the location, in mm, specified by the mm spinner"""
        for i in (0, 1):
            target = float(self._view.GoToMMSpinners[i].text())
            # print(target)
            target = conv.convert(target, "mm", "angle")
            self._xy.moveAngleAbsolute(i, target)



    def gridFunc(self):
        """Function to print grids. Note that this function blocks the main thread and may affect the PID loop...
        """
        print("Printing grid. Blocking all other functions (!)")
        nx = self._view.gridMacroWindow.gridXSetter.value()
        ny = self._view.gridMacroWindow.gridYSetter.value()
        dx = self._view.gridMacroWindow.gridXSepSetter.value()
        dy = self._view.gridMacroWindow.gridYSepSetter.value()

        x0 = self._xy.currentPosition[0]
        y0 = self._xy.currentPosition[1]

        xTotalWidth = (nx-1)*dx
        yTotalWidth = (ny-1)*dy
        print("Printing Grid")
        

        for x in range(0, nx):            

            for y in range(0, ny):
                self._xy.trigger(TRIGGER_AXIS, "A")
                print("print at " + str(x) + ", " + str(y))
                time.sleep(GRID_TIME_DELAY_MS/1000)
                if (y!=(ny-1)):
                    self._xy.move(1, dy)
                    time.sleep(GRID_TIME_DELAY_MS/1000)

            self._xy.move(1, -yTotalWidth)
            time.sleep(ny*GRID_TIME_DELAY_MS/1000)
            if (GRID_BACKLASH_COMPENSATION_ENABLED):
                self._xy.move(1, -GRID_BACKLASH_COMPENSATION_STEPS)
                time.sleep(GRID_TIME_DELAY_MS/1000)
                self._xy.move(1, GRID_BACKLASH_COMPENSATION_STEPS)
                time.sleep(GRID_TIME_DELAY_MS/1000)
            if (x!= (nx-1)):
                self._xy.move(0, dx)
                time.sleep(GRID_TIME_DELAY_MS/1000)
        self._xy.move(0, -xTotalWidth)
        time.sleep(nx*GRID_TIME_DELAY_MS/1000)

    def burstFunc(self):
        """Function to print bursts. Note that this function blocks the main thread and may affect the PID loop...
        """
        n = int(self._view.joypadBurstSetter.text())

        print("Printing burst of " + str(n) + " droplets. Blocking all other functions (!)")

        for i in range(0, n):
            self._xy.trigger(TRIGGER_AXIS, "A")
            print(str(i+1), end='\r')
            if not(i == n-1):
                time.sleep(BURST_TIME_DELAY_MS/1000)
        
        print("Burst complete.")
   
                


    def runScriptFunc(self):
        """Pass the currently edited script to the script handler and play it back"""
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
        distance = distance * sign

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
        distance = distance * sign

        axisMap = CHEVRON_TO_AXIS_DICT
        axis = axisMap.get(text, 0)
        self._xy.move(axis, distance)

    def updatePositionIndicator(self):
        """Update LCDs with mechanical data from uSteps"""
        # print("updating lcd")

        # self.updatePowerSupplyIndicator()

        self.updateTemperatureIndicator()


        """this bit does the mechanical data"""
        
        if self._xy.isBlocking == 0:
            for i in range(0, 2):  # get positional data and display it
                
                data = self._xy.getData(i)
                
                for letter, number in data.items():
                    self._view.PILCDScreens[
                        i, LCDvals.get(LETTER_TO_LCD.get(letter))
                    ].display(number)
                    if letter == "S":
                        self._xy.currentPosition[i] = number
                        # print(self._xy.currentPosition)
                    if letter == "A":
                        self._view.PILCDScreens[i, LCDvals.get("mm")].display(
                            conv.convert(number, "angle", "mm")
                        )
                
        

    def updateTemperatureIndicator(self):
        """Update GUI temperature data and PID loops"""
        try:
            tempData = self._xy.getTempData(TEMP_AXIS)
            # print(tempData)
            for letter, number in tempData.items():
                temp = number
                if letter == "B":
                    # print('Bed Temperature = ' + str(temp))
                    self.bed_controller.update(temp)
                if letter == "N":
                    # print('Nozzle Temperature = ' + str(temp))
                    self.nozzle_controller.update(temp)
        except Exception as e:
            print("Something went wrong running the temperature control loop. The full error is:")
            print(repr(e))


    def updatePowerSupplyIndicator(self):
        """Update GUI components with PSU data"""
        if QT_POLL_PSU:
            for i in range(0, 2):  # get power data and display it
                channel = i + 1
                for cmd, index in HeaterLCDvals.items():
                    if cmd != "Channel":
                        self._heater.power.get(cmd, channel, "QUERY")
                        s = self._heater.power.poll_async()
                        if s != "SANFAIL":
                            value = self._heater.power.get(cmd, channel, "REPLY")
                            if value != "EMPTY":
                                self._view.HeaterLCDScreens[i, index].display(value)


class JetDriveSerialInterface:  # serial interface with JetDrive
    def __init__(self, port):
        self.port = port

    def fire(self):
        print("drop")


# class TemperatureMonitorSerialInterface:
#    def __init__(self):


class psuController:
    def __init__(self, port):
        """class for controlling a power supply that provides power to the heater elements and the motors"""
        try:
            self.power = psu_serial.GPD_4303S(port)
            self.isConnected = True
        except:
            self.power = psu_serial.PSU_DUMMY(port)
            self.isConnected = False
            print("PSU not found - using dummy instead.")
        


def main():
    """Main function for the application"""
    
    # Create an instance of QApplication
    printer = QApplication(sys.argv)
    # Show the printer's GUI
    view = PrinterUi()
    view.show()
    xyInterface = XYSerialInterface()
    jetdriveInterface = JetDriveSerialInterface(JETDRIVE_PORT)
    heaterPsu = psuController(HEATER_PSU_PORT)

    PrinterController(
        view=view, xy=xyInterface, jetdrive=jetdriveInterface, heater=heaterPsu
    )

    # Execute the printer's main loop
    sys.exit(printer.exec_())


if __name__ == "__main__":
    main()
