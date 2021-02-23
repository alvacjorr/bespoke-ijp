from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from simple_pid import PID
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QPlainTextEdit, QHBoxLayout
from PySide2.QtWidgets import QGridLayout, QLineEdit, QMainWindow, QSpinBox, QLCDNumber, QGroupBox, QDoubleSpinBox
from PySide2.QtCore import Slot, Qt, QTimer,QDateTime, Signal
from constants import *

from functools import partial
class HeaterPIDController():
    def __init__(self,PSUchannel,name,PSUcontroller,sample_time,max_current):
        self.pid = PID(PID_P, PID_I, PID_D, setpoint = TEMP_SETPOINT, output_limits=(0,24),proportional_on_measurement=PID_PROPORTIONAL_ON_MEASUREMENT, sample_time=sample_time)
        self.output = PSUcontroller
        self.channel = PSUchannel
        self.output.power.set_current(max_current, self.channel)
        
        self.temperature = 0


        

        self._ui = PID_Layout(label = name)
        


        self._connectSignals()
        self._ui.graph.update_plot(0,0,0)
        self.update(0)

    def getNewSetpointFromUI(self):
        new_t = int(self._ui.setter.setpointSpin.text())
        print(new_t)
        self.set_setpoint(new_t)
        return

    def _connectSignals(self):
        self._ui.setter.setpointButton.clicked.connect(partial(self.getNewSetpointFromUI))
        return

    def update(self,t):
        """Update the PID controller with the most recent temperature reading

        :param t: Latest temperature reading
        :type t: float
        """        
        self.temperature = t
        control = self.pid(t)
        #print(self.pid.components)
        #print('T: ' + str(t) +' V: ' + str(control))
        self.set_voltage(control)

        self._ui.graph.update_plot(t, control,self.get_setpoint())
        self._ui.setter.update(t,self.get_setpoint())

    def get_setpoint(self):
        """Get the temperature setpoint

        :return: temparature setpoint in deg C
        :rtype: float
        """        
        return self.pid.setpoint

    def get_last_temperature(self):
        """Returns the most recent temperature measurement

        :return: latest temperature reading in deg C
        :rtype: float
        """        
        t = self.graph.tdata[-1]
        return t

    def set_setpoint(self, sp):
        """Set the temperature setpoint

        :param sp: setpoint in deg C
        :type sp: float
        """        
        self.pid.setpoint = sp


    def show_graphs(self):
        return
        self.graph.show()



    def set_voltage(self,v):
        """Set the output voltage

        :param v: voltage
        :type v: float
        """        
        ch = self.channel
        v = int(v)
        #v = "%0.1f" % v
        msg = "VSET" + str(ch) + ":" + str(v) + "\n"
        #print(msg)
        
        self.output.power.get_custom(msg,'NOREPLY')
        #print(self.output.power.get_custom(msg,'REPLY'))

class PID_Layout(QWidget):
    def __init__(self, label = "untitled"):
        super().__init__()
        layout = QHBoxLayout()
        #self.windowTitle = label
        self.setWindowTitle('Heater Control: ' + label)
        self.label = label
        self.setLayout(layout)

        self.graph = PIDGraphWindow(label = label)
        self.setter = PID_Setter(label = 'Controls')
        layout.addWidget(self.graph)
        layout.addWidget(self.setter)
        self.createShowButton()

        self.setMaximumHeight(0)








        #self.show()




    def createShowButton(self):
        showLabel = 'Heater Control: ' + self.label
        self.showButton = QPushButton(showLabel)
        self.showButton.clicked.connect(partial(self.show))


class PID_Setter(QGroupBox):
    def __init__(self,label = "untitled"):
        super().__init__()

        self.setTitle(label)

        layout = QGridLayout()
        self.setlabel = QLabel('Setpoint')
        self.templabel = QLabel('Temperature')
        
        self.setLayout(layout)

        self.setpointLCD = QLCDNumber()
        self.setpointLCD.setDigitCount(6)
        self.setpointLCD.setFixedSize(100,40)
        self.temperatureLCD = QLCDNumber()
        self.temperatureLCD.setDigitCount(6)
        self.temperatureLCD.setFixedSize(100,40)
        self.setpointSpin = QSpinBox()
        self.setpointSpin.setValue(0)
        self.setpointSpin.setMaximum(120)
        self.setpointButton = QPushButton('SET')
        layout.addWidget(self.templabel)
        layout.addWidget(self.temperatureLCD)
        layout.addWidget(self.setlabel)        
        layout.addWidget(self.setpointLCD)
        layout.addWidget(self.setpointSpin)
        layout.addWidget(self.setpointButton)
        self.setMinimumHeight(0)
        self.setMinimumWidth(0)
        #self.show()
        #self.update(40, 50)

    def update(self, t, sp):
        self.setpointLCD.display(sp)
        self.temperatureLCD.display(t)



class PIDCanvas(FigureCanvasQTAgg):
    """Canvas for PID data

    :param FigureCanvasQTAgg: [description]
    :type FigureCanvasQTAgg: [type]
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(1,1,1)
        self.axes.set_ylim([0, 100])
        self.axes2 = self.axes.twinx()
        self.axes2.set_ylim([0,25])
        fig.tight_layout()
        super(PIDCanvas, self).__init__(fig)



class PIDGraphWindow(QWidget):

    """This "window" is a QWidget. If it has no parent, it will appear as a free-floating window."""

    def __init__(self, label = "untitled"):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel(label)
        #layout.addWidget(self.label)
        self.setLayout(layout)
        n_data = GRAPH_TEMP_WIDTH
        self.xdata = list(range(n_data))
        self.tdata = [10 for i in range(n_data)]
        self.vdata = [10 for i in range(n_data)]

        sp = TEMP_SETPOINT 

        self.sdata = [sp for i in range(n_data)]

        self.sc = PIDCanvas(self, width=5, height=4, dpi=100)

        layout.addWidget(self.sc)

        self.t_plot_ref = None
        self.v_plot_ref = None
        self.s_plot_ref = None

        #self.sc.axes.set_xlabel('time')
        #self.sc.axes.set_ylabel('temperature')
        #self.sc.axes2.set_ylabel('voltage')

        self.show()


    def update_plot(self, t_new, v_new, s_new):
        self.tdata = self.tdata[1:]
        self.tdata.append(t_new)
        self.vdata = self.vdata[1:]
        self.vdata.append(v_new)
        self.sdata = self.sdata[1:]
        self.sdata.append(s_new)

        if self.t_plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.sc.axes.plot(self.xdata, self.tdata, 'r', label = 'temperature')
            self.t_plot_ref = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self.t_plot_ref.set_ydata(self.tdata)

        if self.v_plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.sc.axes2.plot(self.xdata, self.vdata, 'b', label = 'voltage')
            self.v_plot_ref = plot_refs[0]
            #self.sc.axes.legend()
            #self.sc.axes2.legend()
        else:
            # We have a reference, we can use it to update the data for that line.
            self.v_plot_ref.set_ydata(self.vdata)

        # Trigger the canvas to update and redraw.
        self.setpoint_graph()
        self.sc.draw()

    def setpoint_graph(self):
        if self.s_plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.sc.axes.plot(self.xdata, self.sdata, 'k--', label = 'setpoint')
            self.s_plot_ref = plot_refs[0]
            #self.sc.axes.legend()
            lns = [self.t_plot_ref, self.v_plot_ref ,self.s_plot_ref]
            labs = [l.get_label() for l in lns]
            self.sc.axes.legend(lns, labs, loc='upper left')
        else:
            # We have a reference, we can use it to update the data for that line.
            self.s_plot_ref.set_ydata(self.sdata)

        # Trigger the canvas to update and redraw.
        self.sc.draw()


