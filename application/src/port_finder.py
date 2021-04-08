import serial.tools.list_ports

import os.path

filename = './application/src/ports_serial.py'

def main():
    instructions = "Welcome to the serial port finder for bespoke-ijp."
    print(instructions)
    comlist = serial.tools.list_ports.comports()
    for comport in comlist:
        if comport.serial_number is None:
            print('No ports found. Exiting...')
        else:
            print ('Port: ' + comport.name + ', Serial Number: ' + comport.serial_number)

    configure_and_commit()

def configure():
    input('Please unplug the X and Y axes. Then press Enter to continue')
    comlist = serial.tools.list_ports.comports()
    input('Please plug in the X axis. Then press Enter to continue')
    comlist_x = serial.tools.list_ports.comports()
    x_serial = compare(comlist,comlist_x)
    print('x: ' + x_serial)
    input('Please plug in the Y axis. Then press Enter to continue')
    comlist_y = serial.tools.list_ports.comports()
    y_serial = compare(comlist_x,comlist_y)
    print('y: ' + y_serial)
    return[x_serial,y_serial]

def configure_and_commit():
    cfg = configure()
    commit(cfg)


def commit(c):
    if os.path.isfile(filename):
        i = input('Found an existing configuration. Clear it? y/n')
        if i == 'y':
            f = open(filename, "w")
        else:
            print('exiting...')
    else:
        print('No config found. Making one.')
        f = open(filename, "w")

    content = """
STAGE_X_SERIAL_NUMBER = '""" + c[0] + """'
STAGE_Y_SERIAL_NUMBER = '""" + c[1]+ "'"

    print(content)

    f.write(content)
    f.close()




def compare(l1,l3):
    res = [x for x in l1 + l3 if x not in l1 or x not in l3]
    return res[0].serial_number
        








if __name__ == '__main__':
    main()