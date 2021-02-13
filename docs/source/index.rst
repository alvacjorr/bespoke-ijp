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

This manual is for the Bespoke IEB Inkjet Printing (IJP) rig.
Currently the person responsible for this rig is Andrew Orr.
It builds on work done by Ellis Parry.
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
***

Before beginning any experiment, ensure that the following connections are made:

- USB cables from both uSteppers to the PC
- Power from the motor PSU to the two motors controllers
- USB cable from the heater power supply to the PC
- Nozzle and bed heating elements are conected to the heater PSU




Turning on the system
***

In order:

#. Power on the controlling computer
#. Power on the heater power supply (GW INSTEK GPD-X303S)

  * The power supply should say USB YES on its front panel.

#. Power on the motor power supply and ensure it is set to 3A, 24V
#. Start the software by opening the python file.







Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
