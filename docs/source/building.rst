Assembling a new bespoke-ijp system
===================================

The following instructions are advice only, and are followed at the reader's risk.
The writer(s) accept no responsibility for any inaccuracies.

Parts List
**********

This system is almost entirely made of off-the-shelf or 3D-printed parts.

Note: this is not exhaustive!

- An optical table
- A comedically large quantity of 
- 2x `OpenBuilds C-Beam Linear Actuator <https://ooznest.co.uk/product/c-beam-linear-actuator>`_

  - Actuator Length 250mm
  - NEMA23 Stepper Motor
  - XL Gantry Plate
  - No C-Beam Motor Standoff
  - uStepper S Controller Board

- A power supply (3A, 24V) for the motors
- Probably a 3D printer! To make extra bits with...
- A Windows computer to install the software on (Linux compatability is in the works)
- A programmable power supply for the heater beds
- An inkjet nozzle system (MicroFab or equivalent)
- An optical observation system (highspeed camera, polarised filters, microscope lens or similar)


Assembling the rails
*******************

OpenBuilds have instructions on their `website <https://openbuilds.com/builds/c-beam%E2%84%A2-linear-actuator.1955/>`_ to help you assemble the rails. Pictures also on their way!


Software Prerequisites
**********************



Installing the software
***********************

Prerequisites
-------------

You will need the following software installed:

- Python 3.7 with pip
- Arduino IDE 
- Git (and Git Bash if on windows)
- Arduino libraries and board profiles from the `uStepperS readme <https://github.com/uStepper/uStepperS>`_

Downloading the project
-----------------------

Open bash (linux/macOS) or Git Bash (Windows). Navigate to the folder you want to install the software in and enter the following:
::

    git clone https://github.com/thekeeno/bespoke-ijp

This will download the main repository to your system and put it in a folder called bespoke-ijp. 

Installing Python libraries
-----------------------------

Next, move into the project's root folder::

    cd bespoke-ijp

If you have a python venv, now is the time to activate it. If not, don't worry about it. To download the python libraries needed for this project, run::

    pip install -r requirements.txt

This may take a while. 

Uploading the firmware to the uSteppers
----------------------------------------

This can be done via Arduino IDE, arduino-cli and Visual Studio Code. In this section we will use the Arduino IDE.
The core firmware is located in embedded/src/XY_commander/XY_commander.ino.
Open this in Arduino IDE.
To verify you have the correct library configuration, click the tick button on the top bar.
This will compile the firmware but not upload it.
If this fails, check that you have selected uStepepr S as the board, and have downloaded the requisite Arduino libraries.

Once you know you can compile the firmware, it's time to upload it.
Ensure the uSteppers are powered externally and connected by USB.
Select the COM or tty port associated with your uStepper and click Upload.
Repeat for the second board.




Registering the X and Y axes with the GUI
------------------------------

To distinguish between the X and Y rails, simply specifying a COM or tty port can result in guesswork.
To simplify this process, I made a python script that prints the unique serial numbers from the uSteppers, allowing the X and Y stages to be directly identified, from system to system.


