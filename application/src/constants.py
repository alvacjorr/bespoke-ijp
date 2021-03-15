#Constants file for the bespoke IJP rig. lots of useful parameters here if you ever feel the need to tweak how it works...


#COM ports. eventually these won't need to be hardcoded...



STAGE_X_SERIAL_NUMBER = '304D1F32CBA3E811939993603B0549EC'
STAGE_Y_SERIAL_NUMBER = '7A6AA05F5414E81185539C3A3B0549EC'
JETDRIVE_PORT = 'COM1'
HEATER_PSU_PORT = 'COM5'

GET_BOUNDS_ON_STARTUP = False


dimMap = {0:'x',1:'y'}

LCDvals = {'axis':0,'angle':1,'steps':2,'V_measured':5,'V_target':4,'mm':3}

LETTER_TO_LCD = {'A':'angle','S':'steps','V':'V_measured','D':'V_target'}


#Heater LCD stuff

HeaterLCDvals = {'Channel':0,'VSET':1,'ISET':3,'VOUT':2,'IOUT':4}

HeaterChannelNames = {0:'nozzle',1:'bed'}

#motor settings

MICROSTEPPING = 256

WHOLE_STEPS_PER_REV = 200

STEPS_PER_REV = MICROSTEPPING*WHOLE_STEPS_PER_REV

#Physical parameters of the rail

RAIL_APPROX_LENGTH_STEPS = 700000

RAIL_APPROX_LENGTH_DEGREES = 5000

RAIL_DEGREES_TO_MM = 8/360

RAIL_MM_TO_DEGREES = 1/RAIL_DEGREES_TO_MM

RAIL_APPROX_LENGTH_MM = RAIL_APPROX_LENGTH_DEGREES*RAIL_DEGREES_TO_MM

TO_ANGLE_DICT = {'mm':RAIL_MM_TO_DEGREES,'angle':1,'steps':360/STEPS_PER_REV}

#temperature conversion

ARDUINO_MAX_RAW_ANALOG = 1023

ARDUINO_ANALOG_REFERENCE = 5.0

AD8495_OFFSET = -1.25

AD8495_DIVISOR = 0.005

#up, down, left and right

#WASD mappings

KEY_PRINTER_UP = 87
KEY_PRINTER_DOWN = 83
KEY_PRINTER_RIGHT = 68
KEY_PRINTER_LEFT = 65

KEY_TO_CHEVRON_DICT = {
    KEY_PRINTER_UP:'^',
    KEY_PRINTER_DOWN:'v',
    KEY_PRINTER_LEFT:'<',
    KEY_PRINTER_RIGHT:'>'
}

CHEVRON_TO_AXIS_DICT = {
            '^': 1,
            'v': 1,
            '>': 0,
            '<': 0,
            }

CHEVRON_TO_SIGN_DICT = {
            '^': 1,
            'v': -1,
            '>': 1,
            '<': -1,
            }


#Application GUI Settings

QT_JOYPAD_WIDTH = 200
QT_JOYPAD_HEIGHT = 200

QT_XY_SETTER_WIDTH = 300

QT_JOYSTICK_MAXIMUM_STEPS = 1000000

QT_JOYSTICK_STEP_INCREMENT = 10000

QT_POLLER_ENABLED = 1

QT_POLLER_TIME_MS = 2000

QT_POLL_PSU = False

QT_STYLE_EXECUTE_READY = "background-color: green; color: white"

QT_STYLE_EXECUTE_RUNNING = "background-color: yellow; color: black"


WELCOME_MESSAGE = "Welcome to IEB Printing."

#Power Supply Settings


POW_HEATER_NOZZLE_CHANNEL = 1
POW_HEATER_NOZZLE_INIT_VOLTAGE = 12
POW_HEATER_NOZZLE_MAX_CURRENT = 2

POW_HEATER_BED_CHANNEL = 2
POW_HEATER_BED_INIT_VOLTAGE = 12
POW_HEATER_BED_MAX_CURRENT = 2

POW_SERIAL_TIMEOUT = 0.01

#Control Loop stuff

PID_PROPORTIONAL_ON_MEASUREMENT = False

# Proportional Integral and Derivative terms

PID_P = 1
PID_I = 0.05
PID_D =  0.05

#uStepper Axis responsible for trigger control

TRIGGER_AXIS = 0

#uStepper Axis responsible for temperature readouts
TEMP_AXIS = 0

TEMP_SETPOINT = 20 #default temperature setpoint

GRAPH_TEMP_WIDTH = 50 #number of successive points to plot on graph


#AFG2021 settings

AFG2021_VISA_PORT = 'USB::0x0699::0x0349::C013148::INSTR'

#AFG-2105 settings