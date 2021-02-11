import serial.tools.list_ports

instructions = "Welcome to the serial port finder for bespoke-ijp."
print(instructions)
for comport in serial.tools.list_ports.comports():
    print ('Port: ' + comport.name + ', Serial Number: ' + comport.serial_number)