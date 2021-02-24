import serial
class GW_AFG2105():
    def __init__(self,port):
        self.afg = serial.Serial(port, baudrate=115200, timeout= 0.002)
        print("Connected to power supply.")
        self.identify()

    def identify(self):
        """Print the ID of the PSU
        """
        print(self.query("*IDN?\n"))


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
        self.afg.write(message.encode())



def main():
    a = GW_AFG2105('COM4')
    

if __name__ == '__main__':
    main()