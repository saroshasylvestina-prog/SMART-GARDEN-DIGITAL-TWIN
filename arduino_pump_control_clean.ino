/*
 * Arduino Pump Control via Serial Communication - CLEAN VERSION
 * NO DELAYS - Pump only responds to Python commands
 * 
 * This code listens for serial commands from Python to control a relay on pin 8
 * 
 * Commands:
 * - "ON" or "1" -> Turn pump ON (set pin 8 to LOW for active-low relay)
 * - "OFF" or "0" -> Turn pump OFF (set pin 8 to HIGH for active-low relay)
 * - "STATUS" -> Return current pump status
 * 
 * Wiring:
 * - Relay IN/IN1 -> Digital Pin 8
 * - Relay VCC -> 5V
 * - Relay GND -> GND
 * - Pump -> Relay NO/COM terminals
 * 
 * IMPORTANT: This code has NO automatic delays or loops.
 * Pump ONLY turns ON when Python sends "ON" command.
 * Pump ONLY turns OFF when Python sends "OFF" command.
 */

// Relay connected to digital pin 8
const int relayPin = 8;
bool pumpState = false;  // false = OFF, true = ON
bool activeLow = true;   // Set to false if your relay is active-high

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect (needed for some boards)
  }
  
  // Initialize relay pin
  pinMode(relayPin, OUTPUT);
  
  // Set initial state to OFF immediately
  // For active-low: HIGH = OFF
  // For active-high: LOW = OFF
  if (activeLow) {
    digitalWrite(relayPin, HIGH);  // HIGH = OFF for active-low relay
  } else {
    digitalWrite(relayPin, LOW);   // LOW = OFF for active-high relay
  }
  
  pumpState = false;
  
  // Wait a moment for serial to stabilize
  delay(100);
  
  Serial.println("Arduino Pump Control Ready - NO AUTO DELAYS");
  Serial.println("Commands: ON, OFF, STATUS");
  Serial.print("Initial state: OFF (Pin 8 = ");
  Serial.print(activeLow ? "HIGH" : "LOW");
  Serial.println(")");
  Serial.println("Pump will ONLY respond to serial commands - no automatic behavior");
}

void loop() {
  // Check for incoming serial commands ONLY
  // NO automatic delays, NO automatic pump control
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove whitespace
    command.toUpperCase();  // Convert to uppercase
    
    if (command == "ON" || command == "1") {
      // Turn pump ON - ONLY when Python sends this command
      if (activeLow) {
        digitalWrite(relayPin, LOW);  // LOW = ON for active-low
      } else {
        digitalWrite(relayPin, HIGH); // HIGH = ON for active-high
      }
      pumpState = true;
      Serial.println("PUMP:ON");
      Serial.print("Pin 8 set to: ");
      Serial.println(activeLow ? "LOW" : "HIGH");
      Serial.println("Pump is ON - waiting for OFF command from Python");
      
    } else if (command == "OFF" || command == "0") {
      // Turn pump OFF - ONLY when Python sends this command
      if (activeLow) {
        digitalWrite(relayPin, HIGH); // HIGH = OFF for active-low
      } else {
        digitalWrite(relayPin, LOW);  // LOW = OFF for active-high
      }
      pumpState = false;
      Serial.println("PUMP:OFF");
      Serial.print("Pin 8 set to: ");
      Serial.println(activeLow ? "HIGH" : "LOW");
      Serial.println("Pump is OFF");
      
    } else if (command == "STATUS") {
      // Return current status
      Serial.print("STATUS:");
      Serial.println(pumpState ? "ON" : "OFF");
      Serial.print("Pin 8 state: ");
      Serial.println(digitalRead(relayPin) == (activeLow ? LOW : HIGH) ? "ON" : "OFF");
      
    } else {
      // Unknown command
      Serial.print("ERROR:Unknown command: ");
      Serial.println(command);
    }
  }
  
  // Small delay to prevent overwhelming the serial buffer
  // This is ONLY for serial communication, NOT for pump control
  delay(10);
}

// IMPORTANT NOTES:
// - This code has NO delay(2000) or any long delays
// - Pump does NOT turn on automatically on reset
// - Pump does NOT turn on in a loop
// - Pump ONLY responds to "ON" and "OFF" commands from Python
// - Duration is controlled by Python, NOT by Arduino

