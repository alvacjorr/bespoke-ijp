from psu_serial import GPD_43038

import time

gw = GPD_43038('COM5')



for v in range(1):


    gw.get("IOUT",1,"QUERY")

    time.sleep(1)

    
    gw.poll_async()
    print(gw.get("IOUT",1,"REPLY"))





time.sleep(1)

gw.turn_on()

time.sleep(1)

gw.turn_off()