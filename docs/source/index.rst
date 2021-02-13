IEB Bespoke Inkjet Printing
=======================================



.. toctree::
   :maxdepth: 4

   XY_commander
   constants
   conversions
   plotter
   port_finder
   psu_serial
   testpsu

Welcome
=========

This manual is for the Bespoke IEB Inkjet Printing (IJP) rig, a collaborative project between the Fluids Lab and Soft Matter Photonics groups in the Oxford University Department of Engineering Science.
Currently the person responsible for this rig is Andrew Orr. It builds on work done by Ellis Parry.


This documentation will (eventually) include, amongst other things:

- Instructions on how to build this system from scratch
- Instructions on how to upload the firmware to the microcontrollers
- A User's Guide
- A Programmer's documentation for the Python GUI

User's Guide
============

Hardware Overview
*****************

The system consists of:

- Motor Power Supply
- Heater Power Supply (GW INSTEK GPD-X303S)
- Control PC
- XY Translation Stage
- Heating elements (nozzle and bed)
- MicroFab JetDrive III

Installing the software
***********************

Ensure you have git installed, as well as Python 3. Then run:
::

    git clone https://github.com/thekeeno/bespoke-ijp

This should copy all the necessary files to your system.

Connections
***********

Before beginning any experiment, ensure that the following connections are made:

- USB cables from both uSteppers to the PC
- Power from the motor PSU to the two motors controllers
- USB cable from the heater power supply to the PC
- Nozzle and bed heating elements are conected to the heater PSU




Turning on the system
********************

In order:

#. Power on the controlling computer
#. Power on the heater power supply (GW INSTEK GPD-X303S)

  * The power supply should say USB YES on its front panel.

#. Power on the motor power supply and ensure it is set to 3A, 24V
#. Start the software by opening the python file.

Using the GUI
*************

GUI is in progress - this section is very subject to change!


Programmer's Documentation
==========================

Something something docstrings... 

Assembling a new bespoke-ijp system
===================================

The following instructions are advice only, and are followed at the rearer's risk.
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

OpenBuilds have an instruction set for this. Pictures also on their way!


Downloading the software
************************

As in previous sections!


Registering the X and Y axes
****************************

To distinguish between the X and Y rails, simply specifying a COM or tty port can result in guesswork.
To simplify this process, I made a python script for this.






Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
