from constants import *



def convert(inValue, inUnits, outUnits): #converts a generic input from mm, angle or steps to mm, angle or steps.
    angle = inValue * TO_ANGLE_DICT[inUnits]
    return angle/TO_ANGLE_DICT[outUnits]