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
#define GCODE_TRIGGER_A "M19"
#define GCODE_TRIGGER_B "M20" //deprecated
#define GCODE_CONFIGURE_TRIGGER_PROGRESSIVE "M21"
#define GCODE_CONFIGURE_TRIGGER_CONTINUOUS "M22"

//Port registers for the various output pins.
//Consult uStepper datasheet and circuit diagram before changing these
//Trigger pin is logical E0, physical D8
#define PIN_TRIGGER_DROP 0 
#define PORT_TRIGGER_DROP PORTE
#define DDR_TRIGGER_DROP DDRE
#define PIN_TRIGGER_LED 1 // E1 (D7)
#define PORT_TRIGGER_LED PORTE
#define DDR_TRIGGER_LED DDRE
#define PIN_TRIGGER_SHUTTER 5 //B5 (D6)
#define PORT_TRIGGER_SHUTTER PORTB
#define DDR_TRIGGER_SHUTTER DDRB

//Analogue pins for temperature sensing (to be deprecated once we have digital temperature sensing)
#define PIN_TEMP_BED A0
#define PIN_TEMP_NOZZLE A1

#define TIMER_DELAY_COMPENSATION 2.4 //fudge factor because Arduino is slow!!!


