import serial
class PhotoFluor_II():
    def __init__(self,port):
        self.serial = serial.Serial(port, baudrate=19200)
        print("Connected to PhotoFluor II on " + port)

    def shutter_open(self):
        self.serial.write(b'+')

    def shutter_close(self):
        self.serial.write(b'-')

    def NDF(self, filter_position):
        f = int(filter_position)
        f = max(0, min(f, 5))
        f = str(f)
        
        self.serial.write(f.encode('utf-8'))

    def lamp_off(self):
        self.serial.write(b'o')

def main():
    pf = PhotoFluor_II('COM4')
    #pf.lamp_off()
    pf.shutter_close()
    pf.shutter_open()
    pf.shutter_close()


if __name__ == "__main__":
    main()
