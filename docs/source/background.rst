Background and Motivation
==========

This section explains the main motivations for the development of the bespoke-ijp system, as well as a description of some of the work that precedes it.
Much of this section is copied verbatim from Andrew Orr's transfer report.

Old system
********************

The predecessor to this system, which ran using smaller stepper motors on belts, over a LabVIEW controller, currently still lives in the Fluids Lab.
It is thoroughly documented in Ellis Parry's DPhil thesis, soon to be available on ORA.
However, it has some limitations, including problems with driver compatibility, stepper repeatability, and mechanical robustness.
The new bespoke-ijp system was therefore conceived to remedy these issues. The major improvements are set to include:

- Use of closed-loop position control for maximum repeatability
- Dedicated stepper driver chips
- All built on open-source platforms (Arduino, Python)
- Cross-platform compatability (Windows, Linux in the works)
- Optional closed-loop heating control
- Support for synchronised motion and piezo pulses
- Basic scripting language, built on GCode, to allow for printing of patterns and similar routines


Inkjet Printing
***************

Inkjet printing is a digital, non-contact manufacturing method which, broadly speaking, consists of launching droplets of fluid from a nozzle onto a substrate.
Inkjet printing is a large market, with an estimated size of \$34 billion in 2019(Mordor Intelligence). 
The most familiar usage of inkjet printing is in reprographics, which makes up around 90\% of the market, and includes commodity devices like desktop inkjet printers.

In the case of this system, Drop-On-Demand (DOD) is used.