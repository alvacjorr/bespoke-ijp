from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from simple_pid import PID
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QPlainTextEdit, QHBoxLayout
from PySide2.QtWidgets import QGridLayout, QLineEdit, QMainWindow, QSpinBox, QLCDNumber, QGroupBox, QDoubleSpinBox
from PySide2.QtCore import Slot, Qt, QTimer,QDateTime, Signal
from constants import *
class HeaterPIDController():
    def __init__(self,PSUchannel,name,PSUcontroller,sample_time,max_current):
        self.pid = PID(1, 0.1,0.05, setpoint = 40, output_limits=(0,24),proportional_on_measurement=False, sample_time=sample_time)
        self.output = PSUcontroller
        self.channel = PSUchannel
        self.output.power.set_current(max_current, self.channel)
        
        self.temperature = 0

        self.graph = PIDGraphWindow(label = name)

        self.graph.update_plot(0,0)
        self.update(0)

    def update(self,t):
        """Update the PID controller with the most recent temperature reading

        :param t: Latest temperature reading
        :type t: float
        """        
        self.temperature = t
        control = self.pid(t)
        print('T: ' + str(t) +' V: ' + str(control))
        self.set_voltage(control)

        self.graph.update_plot(t, control)


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
        print(msg)
        #msg = "VSET1:1\n"
        self.output.power.get_custom(msg,'NOREPLY')
        #print(self.output.power.get_custom(msg,'REPLY'))

class PIDCanvas(FigureCanvasQTAgg):
    """Canvas for PID data

    :param FigureCanvasQTAgg: [description]
    :type FigureCanvasQTAgg: [type]
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(1,1,1)
        self.axes.set_ylim([0, 100])
        super(PIDCanvas, self).__init__(fig)



class PIDGraphWindow(QWidget):

    """This "window" is a QWidget. If it has no parent, it will appear as a free-floating window."""

    def __init__(self, label = "untitled"):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel(label)
        layout.addWidget(self.label)
        self.setLayout(layout)
        n_data = GRAPH_TEMP_WIDTH
        self.xdata = list(range(n_data))
        self.tdata = [10 for i in range(n_data)]
        self.vdata = [10 for i in range(n_data)]



        self.sc = PIDCanvas(self, width=5, height=4, dpi=100)

        layout.addWidget(self.sc)

        self.t_plot_ref = None
        self.v_plot_ref = None

        self.show()


    def update_plot(self, t_new, v_new):
        self.tdata = self.tdata[1:]
        self.tdata.append(t_new)
        self.vdata = self.vdata[1:]
        self.vdata.append(v_new)
        if self.t_plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.sc.axes.plot(self.xdata, self.tdata, 'r', label = 'bed')
            self.t_plot_ref = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self.t_plot_ref.set_ydata(self.tdata)

        if self.v_plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.sc.axes.plot(self.xdata, self.vdata, 'b')
            self.v_plot_ref = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self.v_plot_ref.set_ydata(self.vdata)

        # Trigger the canvas to update and redraw.
        self.sc.draw()

