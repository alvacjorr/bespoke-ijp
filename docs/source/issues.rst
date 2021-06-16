Known Issues
============

See also https://github.com/thekeeno/bespoke-ijp/issues

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

The system definitely has some backlash. The exact amount is yet to be quantified however!

Thermocouple Grounding
**********************

The MAX31855 boards are not compatible with grounded thermocouples.
If you ground the thermocouple (for example by putting it in contact with the optical table) it will return values of NAN.
This will prevent the PID loop from running, causing a loss of temperature control.
There is currently no auto-detect system for this error so do keep an eye out for it.
Watch out for messages like "TEMP N NAN B0.00"


Camera Software
***************

The more recend IC Capture 2.5 software occasionally has problems enabling the external trigger on the DFK USB camera.
To get around this, use the older version 2.4!
