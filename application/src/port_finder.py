import serial.tools.list_ports




def main():
    instructions = "Welcome to the serial port finder for bespoke-ijp."
    print(instructions)
    for comport in serial.tools.list_ports.comports():
        if comport.serial_number is None:
            print('No ports found. Exiting...')
        else:
            print ('Port: ' + comport.name + ', Serial Number: ' + comport.serial_number)







if __name__ == '__main__':
    main()