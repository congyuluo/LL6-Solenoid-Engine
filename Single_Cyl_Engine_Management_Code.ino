// Define port numbers
const int hallSensor = 10;
const int solenoidMosfet = 7;
const int voltageSensor = A0;

// Define Communication Variables
int messageInterval = 200;

// Program variables
int val;

float vOUT = 0.0;
float vIN = 0.0;
float R1 = 30000.0;
float R2 = 7500.0;
int rpm;
int volt_val = 0;
float total_time;
float last_toggle_time;
int num_strokes;
// For indicating currently in stroke
bool in_stroke;
// For reporting rpm
float last_report_time;

// Test Variable
int a;

//void print_message(int rpm, float voltage) {
//
//  // Send RPM Information
//  Serial.print("{'RPM': ");
//  Serial.print(rpm);
//  Serial.print(", ");
//
//  // Send Voltage Information
//  Serial.print("'Voltage': ");
//  Serial.print(voltage);
//  Serial.println("}");
//}

void print_message(int rpm, float voltage) {

  // Send RPM Information
  Serial.print(rpm);
  Serial.print(",");

  // Send Voltage Information
  Serial.print(voltage);
  Serial.print(",");

  // Send temperature Information
  Serial.print(0);
  Serial.print(",");
  Serial.print(0);
  Serial.print(",");
  Serial.print(0);
  Serial.print(",");
  Serial.print(0);
  Serial.print(",");
  Serial.print(0);
  Serial.print(",");
  Serial.println(0);
}

void setup() {
  // put your setup code here, to run once:
  //Setup Communication
  Serial.begin(1000000);

  // Setup pinMode
  pinMode(solenoidMosfet, OUTPUT);
  pinMode(hallSensor, INPUT);
  pinMode(voltageSensor, INPUT);

  // Setup Variables
  in_stroke = false;
  num_strokes = 0;
  last_toggle_time = 0.0;
  total_time = 0.0;
  last_report_time = millis();
}

void loop() {
  // Get sensor reading
  val = digitalRead(hallSensor);
  // If magnet is detected
  if (val == LOW) {
    // End Stroke
    if (in_stroke) {
      
      digitalWrite(solenoidMosfet, LOW);
      // Initial start
      if (last_toggle_time == 0.0) {
        last_toggle_time = millis();
        // Collect time delta
      } else {
        num_strokes += 1;
        total_time += millis() - last_toggle_time;
        last_toggle_time = millis();
      }

      // Report Information
      if ((millis() - last_report_time) >= messageInterval) {
        volt_val = analogRead(voltageSensor);

        // Get voltage information
        vOUT = (volt_val * 5.0) / 1024.0;
        vIN = vOUT / (R2 / (R1 + R2));

        if (num_strokes == 0) {
          rpm = 0;
        } else {
          rpm = 60000 / (total_time / num_strokes);
        }

        print_message(rpm, vIN);
        // Reset Variables
        num_strokes = 0;
        total_time = 0.0;
        last_report_time = millis();
      }

      // Start Stroke
    } else {
      digitalWrite(solenoidMosfet, HIGH);
    }
    in_stroke = !in_stroke;

    while (val == LOW) {
      val = digitalRead(hallSensor);
    }
  }
}
