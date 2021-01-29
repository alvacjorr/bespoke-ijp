import serial
class GPD_43038:
    def __init__(self,port):
        """class to control a GWINSTEK GPD-43038"""

        
        self.instrument = serial.Serial(port)
        print("Connected to power supply:")
        self.identify()


    def query(self, message): #takes a port and a message for that port and returns the response given 
        self.instrument.reset_input_buffer()
        self.write(message)
        msg =  self.instrument.readline()
        #print(msg)
        return msg.decode('utf-8')

    def write(self, message):
        self.instrument.write(message.encode())
        
        

    def identify(self):
        print(self.query("*IDN?\n"))

    def turn_on(self):
        self.write("OUT1\n")

    def turn_off(self):
        self.write("OUT0\n")

    def set_voltage(self, v, ch):
        self.write("VSET" + str(ch) + ":" + str(v) + "\n")

    def set_current(self, i, ch):
        self.write("ISET" + str(ch) + ":" + str(i) + "\n")


class PSU_DUMMY:
    def __init__(self,port):
        """dummy GPD-43038"""

        
        print("Connected to dummy power supply.")



    def query(self, message): #takes a port and a message for that port and returns the response given 

        self.write(message)
        msg =  self.instrument.readline()
        #print(msg)
        return msg.decode('utf-8')

    def write(self, message):
        print(message)
        
        

    def identify(self):
        print(self.query("*IDN?\n"))

    def turn_on(self):
        self.write("OUT1\n")

    def turn_off(self):
        self.write("OUT0\n")

    def set_voltage(self, v, ch):
        self.write("VSET" + str(ch) + ":" + str(v) + "\n")

    def set_current(self, i, ch):
        self.write("ISET" + str(ch) + ":" + str(i) + "\n")
