from constants import *



def convert(inValue, inUnits, outUnits): #converts a generic input from mm, angle or steps to mm, angle or steps.
    angle = inValue * TO_ANGLE_DICT[inUnits]
    return angle/TO_ANGLE_DICT[outUnits]

def analogToTemp(analog):
    v = analog*ARDUINO_ANALOG_REFERENCE/ARDUINO_MAX_RAW_ANALOG
    t = (v + AD8495_OFFSET)/AD8495_DIVISOR
    return t