#define BAUD_RATE 115200

// Standard Gcode
#define GCODE_MOVE "G0"
#define GCODE_MOVETO "G1"
#define GCODE_CONTINUOUS "G2"
#define GCODE_BRAKE "G3"
#define GCODE_HOME "G4"

// Miscellaneous commands
#define GCODE_STOP "M0" // Stop everything
#define GCODE_SET_SPEED "M1"
#define GCODE_SET_ACCEL "M2"
#define GCODE_SET_BRAKE_FREE "M3"
#define GCODE_SET_BRAKE_COOL "M4"
#define GCODE_SET_BRAKE_HARD "M5"
#define GCODE_SET_CL_ENABLE "M6"  // Enable closed loop
#define GCODE_SET_CL_DISABLE "M7" // Disable closed loop

#define GCODE_RECORD_START "M10"
#define GCODE_RECORD_STOP "M11"
#define GCODE_RECORD_ADD "M12"
#define GCODE_RECORD_PLAY "M13"
#define GCODE_RECORD_PAUSE "M14"
#define GCODE_REQUEST_DATA "M15"
#define GCODE_REQUEST_CONFIG "M16"

//IJP-specific codes
#define GCODE_REQUEST_TEMP "M17" //get temperature data
#define GCODE_CONFIGURE_TRIGGER_TIMING "M18"

#define GCODE_TRIGGER "M19"
#define GCODE_TRIGGER_ALT "M20" //deprecated
#define GCODE_CONFIGURE_TRIGGER_PROGRESSIVE "M21"
#define GCODE_CONFIGURE_TRIGGER_CONTINUOUS "M22"

//Port registers for the various output pins.
//Consult uStepper datasheet and circuit diagram before changing these

//Droplet Trigger is on D3 (PD2)

#define PIN_TRIGGER_DROP 2
#define PORT_TRIGGER_DROP PORTD
#define DDR_TRIGGER_DROP DDRD

//LED Strobe is on  D4 (PB3)

#define PIN_TRIGGER_LED 3 
#define PORT_TRIGGER_LED PORTB
#define DDR_TRIGGER_LED DDRB

//Camera Shutter is on A0 (PC5)

#define PIN_TRIGGER_SHUTTER 5 
#define PORT_TRIGGER_SHUTTER PORTC
#define DDR_TRIGGER_SHUTTER DDRC

//Analogue pins for temperature sensing (to be deprecated once we have digital temperature sensing)
#define PIN_TEMP_BED A0
#define PIN_TEMP_NOZZLE A1

#define TIMER_DELAY_COMPENSATION 2.4 //fudge factor because Arduino is slow!!!
