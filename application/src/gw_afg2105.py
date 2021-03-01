import serial
class GW_AFG2105():
    def __init__(self,port):
        self.afg = serial.Serial(port, baudrate=115200, timeout= 0.002)
        print("Connected to AFG: " + self.identify())
        

    def identify(self):
        """Print the ID of the PSU
        """
        return self.query("*IDN?")


    def query(self, message): #takes a port and a message for that port and returns the response given 
        self.afg.reset_input_buffer()
        self.write(message)
        msg =  self.afg.readline()
        #print(msg)
        return msg.decode('utf-8')



    def write(self, message):
        """Write a message to the AFG

        :param message: Message to send
        :type message: String
        """        

        message = message + '\n'
        self.afg.write(message.encode())

    def set_func(self, wave):

        self.write('SOUR1:FUNC ' + wave)

    def sin(self):
        self.set_func('SIN')

    def square(self):
        self.set_func('SQU')

    def get_func(self):
        return self.query('SOUR1:FUNC?')

    def set_frequency(self, f):
        """Set frequency in Hz

        :param f: Frequency in Hz
        :type f: float
        """        
        self.write('SOUR1:FREQ ' + ("%.1f" % f) + 'HZ')

    def get_frequency(self):
        return self.query('SOUR1:FREQ?')

    def set_amplitude(self, a):
        self.write('SOUR1:AMPL ' + ("%.1f" % a) + 'Vpp')

    def get_amplitude(self):
        return self.query('SOUR1:AMPL?')

    def am(self, state):
        msg = 'SOUR1:AM:STAT '
        if state:
            self.write(msg + 'ON')
        else:
            self.write(msg + 'OFF')

    def am_on(self):
        self.am(True)

    def am_off(self):
        self.am(False)

    def am_source(self, source):
        msg = 'SOUR1:AM:SOUR '
        if source:
            self.write(msg + 'INT')
        else:
            self.write(msg + 'EXT')

    def am_external(self):
        self.am_source(False)

    def am_internal(self):
        self.am_source(True)


def main():
    a = GW_AFG2105('COM4')
    a.square()

    print(a.get_func())
    a.set_frequency(10000)
    a.set_amplitude(7)
    print(a.get_frequency())
    a.am_on()
    a.am_external()
    

if __name__ == '__main__':
    main()