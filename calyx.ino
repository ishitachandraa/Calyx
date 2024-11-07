#include <Servo.h>

Servo flowerServo;                  // Create a Servo object for the flower
int bloomStage = 0;                 // Bloom stage, starts at 3 (unbloomed, 120 degrees)
int bloomAngles[5] = {120, 120, 80, 40, 0};  // Degrees for each bloom stage (decreasing from unbloomed to fully bloomed)

void setup() {
    Serial.begin(9600);                 // Start serial communication
    flowerServo.attach(9);              // Attach servo to pin 9
    flowerServo.write(bloomAngles[bloomStage]);  // Set initial position to unbloomed (120 degrees)
    
  // Set each LED pin as output and turn them off initially

    pinMode(6, OUTPUT);
    digitalWrite(6, LOW);
    
  }

void loop() {
    if (Serial.available() > 0) {
        char signal = Serial.read();
        
        if (signal == '1') {  // Outgoing message signal
            if (bloomStage < 4) {    // 
                bloomStage++;        // Increment bloom stage
                flowerServo.write(bloomAngles[bloomStage]);  // Move to new angle
            }
        }
        else if (signal == '3') {  // Incoming message signal
            Alert();  // Call the alert function
        }
        else if (signal == '4') {  // Online signal
            // Turn all LEDs on
                digitalWrite(6, HIGH);
            
        }
        else if (signal == '5') {  // Offline signal
            // Turn all LEDs off
                digitalWrite(6, LOW);
        }
    }
}
void Alert() {
    int currentAngle = bloomAngles[bloomStage];  // Save the current angle
    int vibrationRange = 10;                      // Number of degrees to move up/down for vibration
    int numVibrations = 5;                       // Number of vibrations

    for (int i = 0; i < numVibrations; i++) {
        flowerServo.write(currentAngle + vibrationRange); 
        digitalWrite(6, LOW);
 // Move up a bit
        delay(50);                                        // Short delay
        flowerServo.write(currentAngle - vibrationRange); 
        digitalWrite(6, HIGH);
 // Move down a bit
        delay(50);                                        // Short delay
    }

    flowerServo.write(currentAngle);  // Return to original position
}
