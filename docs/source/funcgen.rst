Function Generator Setup
========================

Aim 
******

We want to generate 10kHz square waves, that ramp up and down to various amplitudes ~175V.
The ramp up should be configurable to either be linear at varying rates, or in steps.

How

****

Unfortunately, the Tektronics AFG-2021 has some weird behavior with arbitrary waveforms and AM.
So we use the AFG-2021 as the modulator, and have a different (GWINSTEK?) AFG generate the 10kHz carrier.

Configuration of the AFG-2021
*****************************

1-Shot mode. around 100mHz. Lower voltage 0V. Higher voltage 5V.

Equation comes from PC. 


Configuration of the other function Generator
**********************************************

Set up so that at 0V Mod, the waveform is 0V p-p, and at 5V Mod, the output is XV p-p.
