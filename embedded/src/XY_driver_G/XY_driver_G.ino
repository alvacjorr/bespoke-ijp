#include <uStepperS.h>
#include "gcode.h"
#include "constants.h"

#include <SPI.h>
#include "Adafruit_MAX31855.h"


#define UARTPORT Serial
#define DEBUGPORT Serial1

#define ANGLE_DEADZONE 0.5

uStepperS stepper;
GCode comm;

//thermocouples

Adafruit_MAX31855 thermocouple(MAXCLK, MAXCS, MAXDO); 
Adafruit_MAX31855 thermocouple2(MAXCLK, MAXCS2, MAXDO);

float target = 0.0;
bool targetReached = true;

int triggerSeq = 0;
int maxTriggerSeq = 4;

volatile bool frameLockout = false;
unsigned long nextFrame = 0;

// Used to keep track of configuration
struct
{
  float acceleration = 2000.0; // In steps/s
  float velocity = 200.0;      // In steps/s = 60 RPM
  uint8_t brake = COOLBRAKE;
  boolean closedLoop = false;
  float homeVelocity = 40.0; // In rpm
  int8_t homeThreshold = 4;
  bool homeDirection = CW; // In rpm
  uint32_t LEDPulseLengthMicros = 20;
  uint32_t LEDDelayMicros = 40;
  uint32_t LEDSecondMicros = 40;

  int LEDDelayTimerStart = 65064;  //value the timer stats at to count up to 65536.
  int LEDPulseTimerStart = 65264;  //value the timer stats at to count up to 65536. this value is abous 20us
  int LEDSecondTimerStart = 65264; // same but for the second pulse
  float cameraMaxFPS = 30;
  long cameraMinFrameTime = 33; //Camera Lockout time in milliseconds. by default this corresponds to 30 FPS

  bool secondPulseEnabled = false;

  float progAngleOffset = 0;
  float progAnglePeriod = 10;
  bool progressiveModeEnabled = false;

  float continuousFrequency = 5;
  int continuousOCR = 12500;
  bool continuousModeEnabled = false;

} conf;

//timer toggle stuff



void setup()
{

  //set up the trigger out ports as outputs, low.

  //start the serial interface

  UARTPORT.begin(115200);

  //Setup the thermocouples




  //configure the stepper motor

  stepper.setup();

  stepper.setMaxAcceleration(conf.acceleration);
  stepper.setMaxDeceleration(conf.acceleration);
  stepper.setMaxVelocity(conf.velocity);

  // wait for MAX chip to stabilize
  delay(500);
  thermocouple.begin();
  thermocouple2.begin();
  

  configureComm();
  configurePinsAndInterrupts();

}

void configureComm(){
  
  comm.setSendFunc(&uart_send);

  // Add GCode commands
  comm.addCommand(GCODE_MOVE, &uart_move);
  comm.addCommand(GCODE_MOVETO, &uart_moveto);
  comm.addCommand(GCODE_CONTINUOUS, &uart_continuous);
  comm.addCommand(GCODE_BRAKE, &uart_continuous);
  comm.addCommand(GCODE_HOME, &uart_home);

  comm.addCommand(GCODE_STOP, &uart_stop);
  comm.addCommand(GCODE_SET_SPEED, &uart_config);
  comm.addCommand(GCODE_SET_ACCEL, &uart_config);
  comm.addCommand(GCODE_SET_BRAKE_FREE, &uart_setbrake);
  comm.addCommand(GCODE_SET_BRAKE_COOL, &uart_setbrake);
  comm.addCommand(GCODE_SET_BRAKE_HARD, &uart_setbrake);
  comm.addCommand(GCODE_SET_CL_ENABLE, &uart_setClosedLoop);
  comm.addCommand(GCODE_SET_CL_DISABLE, &uart_setClosedLoop);

  comm.addCommand(GCODE_RECORD_START, &uart_record);
  comm.addCommand(GCODE_RECORD_STOP, &uart_record);
  comm.addCommand(GCODE_RECORD_ADD, &uart_record);
  comm.addCommand(GCODE_RECORD_PLAY, &uart_record);
  comm.addCommand(GCODE_RECORD_PAUSE, &uart_record);

  comm.addCommand(GCODE_REQUEST_DATA, &uart_sendData);
  comm.addCommand(GCODE_REQUEST_CONFIG, &uart_sendConfig);
  comm.addCommand(GCODE_REQUEST_TEMP, &uart_sendTemp);

  comm.addCommand(GCODE_TRIGGER, &uart_trigger);
  comm.addCommand(GCODE_TRIGGER_ALT, &uart_trigger);
  comm.addCommand(GCODE_CONFIGURE_TRIGGER_TIMING, &uart_configureTriggerTiming);
  comm.addCommand(GCODE_CONFIGURE_TRIGGER_PROGRESSIVE, &uart_configureTriggerProgressive);
  comm.addCommand(GCODE_CONFIGURE_TRIGGER_CONTINUOUS, &uart_configureTriggerContinuous);

  // Called if the packet and checksum is ok, but the command is unsupported
  comm.addCommand(NULL, uart_default);

  // Show list off all commands
  // comm.printCommands();
}

void configurePinsAndInterrupts(){

  // initialize timer3 - based on code from http://www.letsmakerobots.com/node/28278

  noInterrupts(); // disable all interrupts
  TCCR3A = 0;
  TCCR3B = 0;
  TCNT3 = 0;
  OCR3A = conf.LEDDelayTimerStart; // preload timer 65536-16MHz*period
  TCCR3B |= (1 << CS30);           // this is a very fast toggle so we don't need a prescaler. ie presacler = 1
  TIMSK3 |= 0;                     //disable ovf interrupt
  //TIMSK3 |= (1 << TOIE3);   // enable timer overflow interrupt

  //initialise timer4 for continuous mode at 5Hz
  TCCR4A = 0;
  TCCR4B = 0;
  TCNT4 = 0;

  OCR4A = conf.continuousOCR; // compare match register 16MHz/256/5Hz
  TCCR4B |= (1 << WGM12);     // CTC mode
  TCCR4B |= (1 << CS12);      // 256 prescaler
  TIMSK4 |= (1 << OCIE1A);    // enable timer compare interrupt

  //Configure Pin Change Interrupts on Digital Pin 2
  //We don't use EXINTs or attachInterrupt because they interact weirdly with the uStepper board.
  //The pin layout here is confusing
  //On the PCB, the pin used is Pin 2.
  //In AVR-land this is PD3 (third bit on Port D).
  //In ISR land, this is PCINT19 - the 19th pin to support PCINT, living on the 2nd bank of PCINTs

  pinMode(2, INPUT_PULLUP); //Make Pin 2 an input

  PCMSK2 |= (1 << 3); //activate PCINT19 aka PD3 aka Pin 2 on the Pin Change Mask 2

  PCICR |= (1 << PCIE2); //Enable PCINT interrupts on bank 2

  //attachInterrupt(digitalPinToInterrupt(2),trigger,FALLING);

  DDR_TRIGGER_LED |= (1 << PIN_TRIGGER_LED);
  DDR_TRIGGER_DROP |= (1 << PIN_TRIGGER_DROP);
  DDR_TRIGGER_SHUTTER |= (1 << PIN_TRIGGER_SHUTTER);
  PORT_TRIGGER_DROP &= ~(1 << PIN_TRIGGER_DROP);
  PORT_TRIGGER_LED &= ~(1 << PIN_TRIGGER_LED);

  interrupts(); // enable all interrupts
}

void handleLockout()
{
  if (frameLockout)
  {
    if (millis() > nextFrame)
    {
      frameLockout = false;
    }
  }
}

//ISR routine for pin 2.
ISR(PCINT2_vect)
{
  bool edge = digitalRead(2);
  //Serial.println(edge);
  if (edge)
  { //check if it was a rising edge
    trigger();
  }                      //if it was, trigger the drop
  EIFR &= ~(1 << INTF0); //Clear interrupt flag
}

ISR(TIMER4_COMPA_vect) // timer compare interrupt service routine

{
  if (conf.continuousModeEnabled)
  {
    trigger();
  }
}

//ISR for the trigger

ISR(TIMER3_OVF_vect)
{
  switch (triggerSeq)
  {
  case 0:
    TCNT3 = conf.LEDDelayTimerStart;
    //digitalWrite(PIN_TRIGGER_DROP, HIGH); //go high
    PORT_TRIGGER_DROP |= (1 << PIN_TRIGGER_DROP);

    break;

  case 1:
    TCNT3 = conf.LEDPulseTimerStart;
    //digitalWrite(PIN_TRIGGER_B, HIGH); //go high
    PORT_TRIGGER_LED |= (1 << PIN_TRIGGER_LED);
    PORT_TRIGGER_DROP &= ~(1 << PIN_TRIGGER_DROP);
    PORT_TRIGGER_SHUTTER |= (1 << PIN_TRIGGER_SHUTTER);

    break;

  case 2:

    TCNT3 = conf.LEDSecondTimerStart;

    PORT_TRIGGER_LED &= ~(1 << PIN_TRIGGER_LED);

    break;

  case 3:
    TCNT3 = conf.LEDPulseTimerStart;
    if (conf.secondPulseEnabled)
    {
      PORT_TRIGGER_LED |= (1 << PIN_TRIGGER_LED);
    }

    break;

  case 4:

    TCNT3 = conf.LEDDelayTimerStart;

    PORT_TRIGGER_LED &= ~(1 << PIN_TRIGGER_LED);
    PORT_TRIGGER_SHUTTER &= ~(1 << PIN_TRIGGER_SHUTTER);
    TIMSK3 = 0; //disable the interrupts so that this pulse is only seen once.
    nextFrame = millis() + conf.cameraMinFrameTime;
    frameLockout = true;

    break;

  case 5: //I think this does not ever run. but need to check.
    TIMSK3 = 0;
    TCNT3 = conf.LEDDelayTimerStart;
    PORT_TRIGGER_DROP &= ~(1 << PIN_TRIGGER_DROP);
    break;
  }

  if (triggerSeq >= maxTriggerSeq)
  {
    triggerSeq = 0;
  }
  else
  {
    triggerSeq++;
  }

  if ((triggerSeq == 1) && frameLockout) //special case - if we are locked out by the frame rate limit, then skip the LED pulse and camera trigger.
  {
    triggerSeq = 5;
  }
}




void loop()
{
  // Process serial data, and call functions if any commands if received.
  comm.run();

  // Feed the gcode handler serial data
  if (UARTPORT.available() > 0)
    comm.insert(UARTPORT.read());

  if (!stepper.getMotorState(POSITION_REACHED))
  {

    if (!targetReached)
    {
      comm.send("REACHED");
      targetReached = true;
    }
  }

  if (stepper.driver.getVelocity() == 0)
    stepper.moveSteps(0); // Enter positioning mode again

  handleProgressiveTrigger();
  handleLockout();
}

void handleProgressiveTrigger()
{
  if (conf.progressiveModeEnabled)
  {
    float theta = stepper.angleMoved();

    if (theta > conf.progAngleOffset + conf.progAnglePeriod)
    {
      trigger();
      conf.progAngleOffset += conf.progAnglePeriod;
    }

    if (theta < conf.progAngleOffset - conf.progAnglePeriod)
    {
      trigger();
      conf.progAngleOffset -= conf.progAnglePeriod;
    }
  }
}

/* 
 * --- GCode functions ---
 * Used by the GCode class to handle the different commands and send data
 */

void uart_send(char *data)
{
  UARTPORT.print(data);
}

void uart_default(char *cmd, char *data)
{
  comm.send("Unknown");
}

void uart_move(char *cmd, char *data)
{
  int32_t steps = 0;
  comm.value("A", &steps);

  stepper.setMaxVelocity(conf.velocity);
  stepper.moveSteps(steps);

  comm.send("OK");
}

void uart_moveto(char *cmd, char *data)
{
  float angle = 0.0;
  comm.value("A", &angle);

  stepper.setMaxVelocity(conf.velocity);
  stepper.moveToAngle(angle);
  target = angle;
  targetReached = false;

  comm.send("OK");
}

void uart_continuous(char *cmd, char *data)
{
  float velocity = 0.0;
  comm.value("A", &velocity);

  if (!strcmp(cmd, GCODE_CONTINUOUS))
    stepper.setRPM(velocity);
  else
  {
    stepper.setRPM(0);
  }

  comm.send("OK");
}

void uart_home(char *cmd, char *data)
{
  char buf[50] = {'\0'};
  char strAngle[12] = {'\0'};
  float railLengthAngle;

  float velocity = conf.homeVelocity;
  int32_t threshold = conf.homeThreshold;
  int32_t dir = conf.homeDirection;

  comm.value("V", &velocity);
  comm.value("T", &threshold);
  comm.value("D", &dir);

  conf.homeVelocity = velocity;
  conf.homeThreshold = (int8_t)threshold;
  conf.homeDirection = (bool)dir;

  stepper.moveToEnd(conf.homeDirection, conf.homeVelocity, conf.homeThreshold);                    //move to one end
  railLengthAngle = stepper.moveToEnd(!conf.homeDirection, conf.homeVelocity, conf.homeThreshold); //then move all the way back to the other end and measure how far it was
  stepper.encoder.setHome();                                                                       // Reset home position

  dtostrf(railLengthAngle, 6, 2, strAngle);

  strcat(buf, "DATA ");
  sprintf(buf + strlen(buf), "A%s", strAngle);
  comm.send(buf); // Tell GUI homing is done
}

void uart_stop(char *cmd, char *data)
{
  stepper.stop();
  comm.send("OK");
}

void uart_setbrake(char *cmd, char *data)
{
  if (!strcmp(cmd, GCODE_SET_BRAKE_FREE))
  {
    stepper.setBrakeMode(FREEWHEELBRAKE);
    conf.brake = FREEWHEELBRAKE;
  }
  else if (!strcmp(cmd, GCODE_SET_BRAKE_COOL))
  {
    stepper.setBrakeMode(COOLBRAKE);
    conf.brake = COOLBRAKE;
  }
  else if (!strcmp(cmd, GCODE_SET_BRAKE_HARD))
  {
    stepper.setBrakeMode(HARDBRAKE);
    conf.brake = HARDBRAKE;
  }
  comm.send("OK");
}

void uart_config(char *cmd, char *data)
{
  float value = 0.0;

  // If no value can be extracted dont change config
  if (comm.value("A", &value))
  {
    if (!strcmp(cmd, GCODE_SET_SPEED))
    {
      conf.velocity = value;
    }
    else if (!strcmp(cmd, GCODE_SET_ACCEL))
    {
      stepper.setMaxAcceleration(value);
      stepper.setMaxDeceleration(value);
      conf.acceleration = value;
    }
  }
}

void uart_setClosedLoop(char *cmd, char *data)
{
  if (!strcmp(cmd, GCODE_SET_CL_ENABLE))
  {
    stepper.moveSteps(0); // Set target position
    stepper.enableClosedLoop();
    conf.closedLoop = true;
  }
  else if (!strcmp(cmd, GCODE_SET_CL_DISABLE))
  {
    stepper.disableClosedLoop();
    conf.closedLoop = false;
  }
}

void uart_sendData(char *cmd, char *data)
{
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

void uart_sendConfig(char *cmd, char *data)
{
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

void uart_sendTemp(char *cmd, char *data)
{
  char buf[50] = {'\0'};
  char strNozzle[10] = {'\0'};
  char strBed[10] = {'\0'};


  double c1 = thermocouple.readCelsius();
  double c2 = thermocouple2.readCelsius();

  dtostrf(c1, 4, 2, strNozzle);
  dtostrf(c2, 4, 2, strBed);

  strcat(buf, "TEMP ");
  sprintf(buf + strlen(buf), "N%s B%s", strNozzle, strBed);

  comm.send(buf);
}

void trigger()
{
  noInterrupts();
  TIMSK3 |= (1 << TOIE3);

  interrupts();
}

void uart_trigger(char *cmd, char *data)
{
  trigger();

  comm.send("OK");
}

void uart_configureTriggerTiming(char *cmd, char *data)
{

  int32_t LEDPulseLengthMicros = conf.LEDPulseLengthMicros;
  int32_t LEDDelayMicros = conf.LEDDelayMicros;
  int32_t LEDSecondMicros = conf.LEDSecondMicros;
  int32_t LEDPulseTimerStart = conf.LEDPulseTimerStart;
  int32_t LEDDelayTimerStart = conf.LEDDelayTimerStart;
  int32_t cameraMaxFPS = conf.cameraMaxFPS;
  int32_t LEDSecondTimerStart = conf.LEDSecondTimerStart;
  int32_t secondPulseEnabled = conf.secondPulseEnabled;

  comm.value("L", &LEDPulseLengthMicros);
  comm.value("D", &LEDDelayMicros);
  comm.value("S", &LEDSecondMicros);
  comm.value("T", &secondPulseEnabled);
  comm.value("F", &cameraMaxFPS);

  conf.LEDPulseLengthMicros = LEDPulseLengthMicros;
  conf.LEDDelayMicros = LEDDelayMicros;
  conf.secondPulseEnabled = secondPulseEnabled;

  conf.cameraMaxFPS = cameraMaxFPS;
  conf.cameraMinFrameTime = 1000 / cameraMaxFPS;

  conf.LEDPulseTimerStart = 65536 - (16 * (LEDPulseLengthMicros - TIMER_DELAY_COMPENSATION)); //derive value of OCR3A from the A Pulse Length. NB the -3 is just a fudge. minimum value of 12us currently!! max is about 4ms.
  conf.LEDDelayTimerStart = 65536 - (16 * (LEDDelayMicros - TIMER_DELAY_COMPENSATION));
  conf.LEDSecondTimerStart = 65536 - (16 * ((LEDSecondMicros - LEDPulseLengthMicros) - TIMER_DELAY_COMPENSATION));

  comm.send("OK");
}

void uart_configureTriggerProgressive(char *cmd, char *data)
{

  float progAngleOffset = conf.progAngleOffset;
  float progAnglePeriod = conf.progAnglePeriod;
  int32_t progressiveModeEnabled = conf.progressiveModeEnabled;

  comm.value("B", &progAngleOffset);
  comm.value("P", &progAnglePeriod);
  comm.value("T", &progressiveModeEnabled);

  progAngleOffset = stepper.angleMoved();

  conf.progAngleOffset = progAngleOffset;
  conf.progAnglePeriod = progAnglePeriod;
  conf.progressiveModeEnabled = progressiveModeEnabled;

  comm.send("Progressive Mode Configured OK");
}

void uart_configureTriggerContinuous(char *cmd, char *data)
{

  //store the old config values
  float continuousFrequency = conf.continuousFrequency;
  int32_t continuousOCR = conf.continuousOCR;
  int32_t continuousModeEnabled = conf.continuousModeEnabled;

  //if new ones are available, overwrite them
  comm.value("F", &continuousFrequency);
  comm.value("T", &continuousModeEnabled);

  //and apply them
  conf.continuousFrequency = continuousFrequency;
  conf.continuousModeEnabled = continuousModeEnabled;


  //calculate the value of OCR4A needed and apply it
  conf.continuousOCR = (F_CPU/256)/continuousFrequency;
  OCR4A = conf.continuousOCR;
}

/** Implemented on the WiFi shield */
void uart_record(char *cmd, char *data) {}
