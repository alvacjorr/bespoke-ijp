import pyvisa

from constants import *


class TEK_AFG2021():
    def __init__(self,port):
        rm = pyvisa.ResourceManager()
        self.afg = rm.open_resource(port)
        print("Connected to AFG2021 - " + self.identify())
        #self.trigger()


    def identify(self):
        """Query and return the ID of the device

        :return: The Device ID
        :rtype: String
        """        
        m = self.afg.query('*IDN?')
        #print(m)
        return m

    def trigger(self):
        """Activate the AFG's internal trigger, once.
        """        
        self.afg.write('*TRG')

    def output(self,status):
        """Turn the AFG's output on or off.

        :param status: True for ON, False for OFF
        :type status: bool
        """        
        if status:
            self.afg.write('OUTP1:STATE ON')
        else:
            self.afg.write('OUTP1:STATE OFF')

    def output_on(self):
        """Turn on the AFG output.
        """        
        self.output(True)

    def output_off(self):
        """Turn off the AFG output
        """        
        self.output(False)

    def output_query(self):
        """Return the status of the output.

        :return: Output Status
        :rtype: String
        """        
        return self.afg.query('OUTP1:STATE?')

def main():
    a = TEK_AFG2021(AFG2021_VISA_PORT)
    print(a.output_query())
    a.output_off()
    print(a.output_query())

    


if __name__ == '__main__':
    main()

