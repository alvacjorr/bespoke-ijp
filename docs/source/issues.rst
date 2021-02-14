Known Issues
============

Mechanical Vibrations
*********************

The motors will occasionally vibrate very loudly. This will likely be fixed in future builds with a 3D printed bracket to better secure and align the motors with their axes.

Rate of PSU Polling
*******************

The GW INSTEK power suplpy sued may take upwards of 50ms to reply to requests for data.
This sets a hard limit on the rate at which currents and voltages may be retrieved for the PID control.
It can also slow down the program's UI from time to time.
