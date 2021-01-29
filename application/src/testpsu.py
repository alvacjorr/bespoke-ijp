from psu_serial import GPD_43038

import time

gw = GPD_43038('COM5')


for v in range(6):
    gw.set_voltage(v,1)

    time.sleep(1)



time.sleep(1)

gw.turn_on()

time.sleep(1)

gw.turn_off()