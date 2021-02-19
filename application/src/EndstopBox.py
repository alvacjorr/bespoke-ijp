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