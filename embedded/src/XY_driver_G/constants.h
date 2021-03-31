#define GCODE_MOVE 				"G0"
#define GCODE_MOVETO            "G1"
#define GCODE_CONTINUOUS 		"G2"
#define GCODE_BRAKE 			"G3"
#define GCODE_HOME 				"G4"

// Miscellaneous commands
#define GCODE_STOP 				"M0" // Stop everything
#define GCODE_SET_SPEED 		"M1"
#define GCODE_SET_ACCEL 		"M2"
#define GCODE_SET_BRAKE_FREE	"M3"
#define GCODE_SET_BRAKE_COOL 	"M4"
#define GCODE_SET_BRAKE_HARD 	"M5"
#define GCODE_SET_CL_ENABLE 	"M6" // Enable closed loop 
#define GCODE_SET_CL_DISABLE 	"M7" // Disable closed loop

#define GCODE_RECORD_START 		"M10"
#define GCODE_RECORD_STOP 		"M11"
#define GCODE_RECORD_ADD 		"M12"
#define GCODE_RECORD_PLAY 		"M13"
#define GCODE_RECORD_PAUSE 		"M14"
#define GCODE_REQUEST_DATA 		"M15"
#define GCODE_REQUEST_CONFIG    "M16"

#define BAUD_RATE 115200

//IJP-specific codes
#define GCODE_REQUEST_TEMP    "M17"
#define GCODE_SET_TRIGGER_AB_DELAY "M18"
#define GCODE_TRIGGER_A "M19"
#define GCODE_TRIGGER_B "M20"


#define PIN_TRIGGER_DROP 0 //note this is strongly tied to port registers!! BEWARE IF YOU CHANGE THIS
#define PIN_TRIGGER_LED 1 //also they swap for some reason. port registers are weird.

//so the microfab is attached to D3?
//and the LED to D2..
//whyyyyyyyyyyyyyyyyy

#define PIN_TEMP_BED A0
#define PIN_TEMP_NOZZLE A1

#define TIMER_DELAY_COMPENSATION 2.4 //fudge factor because Arduino is slow!!!
