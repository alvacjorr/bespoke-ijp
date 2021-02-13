Background and Motivation
==========

This section explains the main motivations for the development of the bespoke-ijp system, as well as a description of some of the work that precedes it.

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