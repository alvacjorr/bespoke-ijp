#include <uStepperS.h>
#include "gcode.h"
#include "constants.h"

#define UARTPORT Serial
#define DEBUGPORT Serial1

#define ANGLE_DEADZONE 0.5

uStepperS stepper;
GCode comm;

float target = 0.0;
bool targetReached = true;

// Used to keep track of configuration
struct{
  float acceleration = 2000.0;  // In steps/s
  float velocity = 200.0;     // In steps/s = 60 RPM
  uint8_t brake = COOLBRAKE;
  boolean closedLoop = false;
  float homeVelocity = 40.0; // In rpm
  int8_t homeThreshold = 4;
  bool homeDirection = CW; // In rpm
  uint32_t APulseLengthMicros = 20;
  uint32_t BPulseLengthMicros = 5;
  uint32_t ABDelayMicros = 10000;
} conf;

void setup() {



  UARTPORT.begin(115200);
  // DEBUGPORT.begin(115200);


   
  stepper.setup(CLOSEDLOOP,200);
  stepper.disableClosedLoop();

  stepper.setMaxAcceleration( conf.acceleration );
  stepper.setMaxDeceleration( conf.acceleration );
  stepper.setMaxVelocity( conf.velocity  );

  comm.setSendFunc(&uart_send);
  
  // Add GCode commands
  comm.addCommand( GCODE_MOVE,            &uart_move ); 
  comm.addCommand( GCODE_MOVETO,          &uart_moveto ); 
  comm.addCommand( GCODE_CONTINUOUS,      &uart_continuous ); 
  comm.addCommand( GCODE_BRAKE,           &uart_continuous ); 
  comm.addCommand( GCODE_HOME,            &uart_home );

  comm.addCommand( GCODE_STOP,            &uart_stop );
  comm.addCommand( GCODE_SET_SPEED,       &uart_config );
  comm.addCommand( GCODE_SET_ACCEL,       &uart_config );
  comm.addCommand( GCODE_SET_BRAKE_FREE,  &uart_setbrake );
  comm.addCommand( GCODE_SET_BRAKE_COOL,  &uart_setbrake );
  comm.addCommand( GCODE_SET_BRAKE_HARD,  &uart_setbrake );
  comm.addCommand( GCODE_SET_CL_ENABLE,   &uart_setClosedLoop );
  comm.addCommand( GCODE_SET_CL_DISABLE,  &uart_setClosedLoop );
  
  comm.addCommand( GCODE_RECORD_START,  &uart_record );
  comm.addCommand( GCODE_RECORD_STOP,   &uart_record );
  comm.addCommand( GCODE_RECORD_ADD,    &uart_record );
  comm.addCommand( GCODE_RECORD_PLAY,   &uart_record );
  comm.addCommand( GCODE_RECORD_PAUSE,  &uart_record );
  
  comm.addCommand( GCODE_REQUEST_DATA,    &uart_sendData );
  comm.addCommand( GCODE_REQUEST_CONFIG,  &uart_sendConfig );
  comm.addCommand( GCODE_REQUEST_TEMP,  &uart_sendTemp);

  comm.addCommand( GCODE_TRIGGER_A, &uart_trigger);
  comm.addCommand( GCODE_TRIGGER_B, &uart_trigger);
  comm.addCommand( GCODE_SET_TRIGGER_AB_DELAY, &uart_configureTrigger);
  
  
  // Called if the packet and checksum is ok, but the command is unsupported
  comm.addCommand( NULL, uart_default );

  // Show list off all commands
  // comm.printCommands();

  pinMode(PIN_TRIGGER_A,OUTPUT);

  pinMode(PIN_TRIGGER_B,OUTPUT);
}

void loop() {
  // Process serial data, and call functions if any commands if received.
  comm.run();

  // Feed the gcode handler serial data
  if( UARTPORT.available() > 0 )
    comm.insert( UARTPORT.read() );

    
  if( ! stepper.getMotorState(POSITION_REACHED) ){

    if( !targetReached ){
      comm.send("REACHED");  
      targetReached = true;
    }
  }

  if( stepper.driver.getVelocity() == 0)
    stepper.moveSteps(0); // Enter positioning mode again
}


/* 
 * --- GCode functions ---
 * Used by the GCode class to handle the different commands and send data
 */
 
void uart_send( char * data ){
  UARTPORT.print(data);  
}

void uart_default(char * cmd, char *data){
  comm.send("Unknown");  
}

void uart_move(char *cmd, char *data){
  int32_t steps = 0;
  comm.value("A", &steps);

  stepper.setMaxVelocity( conf.velocity );
  stepper.moveSteps(steps); 

  comm.send("OK");
}

void uart_moveto(char *cmd, char *data){
  float angle = 0.0;
  comm.value("A", &angle);

  stepper.setMaxVelocity( conf.velocity );
  stepper.moveToAngle(angle); 
  target = angle;
  targetReached = false; 

  comm.send("OK");
}

void uart_continuous(char *cmd, char *data){
  float velocity = 0.0;
  comm.value("A", &velocity);

  if( !strcmp(cmd, GCODE_CONTINUOUS ))
    stepper.setRPM(velocity);
  else{
    stepper.setRPM(0);
  }
  
  comm.send("OK");
}

void uart_home(char *cmd, char *data){ 
  char buf[50] = {'\0'};
  char strAngle[12] = {'\0'};
  float railLengthAngle;

  float velocity    = conf.homeVelocity;
  int32_t threshold = conf.homeThreshold;
  int32_t dir       = conf.homeDirection;

  comm.value("V", &velocity);
  comm.value("T", &threshold);
  comm.value("D", &dir);

  conf.homeVelocity   = velocity;
  conf.homeThreshold  = (int8_t)threshold;
  conf.homeDirection  = (bool)dir;
  
  stepper.moveToEnd( conf.homeDirection, conf.homeVelocity, conf.homeThreshold ); //move to one end
  railLengthAngle = stepper.moveToEnd( !conf.homeDirection, conf.homeVelocity, conf.homeThreshold ); //then move all the way back to the other end and measure how far it was
  stepper.encoder.setHome(); // Reset home position

  dtostrf(railLengthAngle, 6, 2, strAngle);
  
  strcat(buf, "DATA ");
  sprintf(buf + strlen(buf), "A%s", strAngle);  
  comm.send(buf); // Tell GUI homing is done
}


void uart_stop(char *cmd, char *data){
  stepper.stop();
  comm.send("OK");
}

void uart_setbrake(char *cmd, char *data){
  if( !strcmp(cmd, GCODE_SET_BRAKE_FREE )){
    stepper.setBrakeMode(FREEWHEELBRAKE);
    conf.brake = FREEWHEELBRAKE;
  }else if( !strcmp(cmd, GCODE_SET_BRAKE_COOL )){
    stepper.setBrakeMode(COOLBRAKE);
    conf.brake = COOLBRAKE;
  }else if( !strcmp(cmd, GCODE_SET_BRAKE_HARD )){
    stepper.setBrakeMode(HARDBRAKE);
    conf.brake = HARDBRAKE;
  }
  comm.send("OK");
}

void uart_config(char *cmd, char *data){
  float value = 0.0;

  // If no value can be extracted dont change config
  if( comm.value("A", &value) ){
    if( !strcmp(cmd, GCODE_SET_SPEED)){
      conf.velocity = value;
    }else if( !strcmp(cmd, GCODE_SET_ACCEL)){
      stepper.setMaxAcceleration( value );
      stepper.setMaxDeceleration( value );
      conf.acceleration = value;
    }
  }
}

void uart_setClosedLoop(char *cmd, char *data){
  if( !strcmp(cmd, GCODE_SET_CL_ENABLE)){
    stepper.moveSteps(0); // Set target position
    stepper.enableClosedLoop();
    conf.closedLoop = true;
  }else if( !strcmp(cmd, GCODE_SET_CL_DISABLE)){
    stepper.disableClosedLoop();
    conf.closedLoop = false;  
  }
}

void uart_sendData(char *cmd, char *data){
  char buf[50] = {'\0'};
  char strAngle[10] = {'\0'};
  char strRPM[10] = {'\0'};
  char strDriverRPM[10] = {'\0'};

  int32_t steps = stepper.driver.getPosition();
  float angle = stepper.angleMoved();
  float RPM = stepper.encoder.getRPM();
  float driverRPM = stepper.getDriverRPM();
  
  dtostrf(angle, 4, 2, strAngle);
  dtostrf(RPM, 4, 2, strRPM);
  dtostrf(driverRPM, 4, 2, strDriverRPM);
  
  strcat(buf, "DATA ");
  sprintf(buf + strlen(buf), "A%s S%ld V%s D%s", strAngle, steps, strRPM, strDriverRPM);

  comm.send(buf);
}

void uart_sendConfig(char *cmd, char *data){
  char buf[50] = {'\0'};
  char strVel[10] = {'\0'};
  char strAccel[10] = {'\0'};
  char strHomeVel[10] = {'\0'};
  
  dtostrf(conf.velocity, 4, 2, strVel);
  dtostrf(conf.acceleration, 4, 2, strAccel);
  dtostrf(conf.homeVelocity, 4, 2, strHomeVel);
  
  strcat(buf, "CONF ");
  sprintf(buf + strlen(buf), "V%s A%s B%d C%d D%s E%d F%d", strVel, strAccel, conf.brake, conf.closedLoop, strHomeVel, conf.homeThreshold, conf.homeDirection);

  comm.send(buf);
}

void uart_sendTemp(char *cmd, char *data){
  char buf[50] = {'\0'};
  char strNozzle[10] = {'\0'};
  char strBed[10] = {'\0'};
  
  dtostrf(analogRead(PIN_TEMP_NOZZLE), 4, 2, strNozzle);
  dtostrf(analogRead(PIN_TEMP_BED), 4, 2, strBed);
  
  strcat(buf, "TEMP ");
  sprintf(buf + strlen(buf), "N%s B%s", strNozzle, strBed);

  comm.send(buf);
}

void uart_trigger(char *cmd, char *data){

  if( !strcmp(cmd, GCODE_TRIGGER_A )){
    digitalWrite(PIN_TRIGGER_A,HIGH);
    delayMicroseconds(conf.APulseLengthMicros);
    digitalWrite(PIN_TRIGGER_A,LOW);
    delayMicroseconds(conf.ABDelayMicros);
    digitalWrite(PIN_TRIGGER_B,HIGH);
    delayMicroseconds(conf.BPulseLengthMicros);
    digitalWrite(PIN_TRIGGER_B,LOW) ;
    }
  else if ( !strcmp(cmd, GCODE_TRIGGER_B )){
    digitalWrite(PIN_TRIGGER_B,HIGH);
    delayMicroseconds(conf.BPulseLengthMicros);
    digitalWrite(PIN_TRIGGER_B,LOW) ;
    }
  comm.send("OK");

}

void uart_configureTrigger(char *cmd, char *data){ 


  int32_t ALength    = conf.APulseLengthMicros;
  int32_t BLength = conf.BPulseLengthMicros;
  int32_t ABDelay       = conf.ABDelayMicros;

  comm.value("A", &ALength);
  comm.value("B", &BLength);
  comm.value("D", &ABDelay);

  conf.APulseLengthMicros   = ALength;
  conf.BPulseLengthMicros  = BLength;
  conf.ABDelayMicros  = ABDelay;
 
  comm.send("OK"); // Tell GUI homing is done
}

/** Implemented on the WiFi shield */
void uart_record(char *cmd, char *data){}
