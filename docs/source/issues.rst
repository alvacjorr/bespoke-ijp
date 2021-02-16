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

Initialisation of uSteppers
***************************

Sometimes the uSteppers will not initialise their serial comms correctly when powered on.
Usually this corresponds to an error message in the GUI saying 'parsing failed' or similar.
To get around this, try power cycling the uSteppers (unlplug from USB and switch off the 24V rail).

Backlash
********


