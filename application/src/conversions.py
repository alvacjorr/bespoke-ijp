from constants import *



def convert(inValue, inUnits, outUnits):
    """Generic conversion function to convert to and from any of angle, distance in mm and steps.

    :param inValue: Value to be converted
    :type inValue: float
    :param inUnits: units of the input variable - 'mm', 'angle', or 'steps'
    :type inUnits: string
    :param outUnits: units to convert to - 'mm', 'angle', or 'steps'
    :type outUnits: string
    :return: The converted value
    :rtype: float
    """    
    angle = inValue * TO_ANGLE_DICT[inUnits]
    return angle/TO_ANGLE_DICT[outUnits]

def analogToTemp(analog):
    """Converts a raw AD8495 reading to a temperature in Celsius

    :param analog: The raw analog value returned by the uStepper/Arduino (0-1023)
    :type analog: int
    :return: The temperature in Celsius
    :rtype: float
    """    
    return voltageToTemp(analogToVoltage(analog))

def analogToVoltage(analog):
    """Convert and Arduino ADC reading to a voltage

    :param analog: Raw ADC reading (0-1023)
    :type analog: int
    :return: Voltage
    :rtype: float
    """    

    v = analog*ARDUINO_ANALOG_REFERENCE/ARDUINO_MAX_RAW_ANALOG
    return v

def voltageToTemp(v):
    """Convert an AD8495 voltage to a temperature

    :param v: Voltage
    :type v: float
    :return: Temperature
    :rtype: float
    """    
    t = (v + AD8495_OFFSET)/AD8495_DIVISOR
    return t


