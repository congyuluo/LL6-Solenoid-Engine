const int hall_set_1 = 12;
const int hall_set_2 = 11;
const int hall_set_3 = 10;

const int mosfet_group_1 = 9;
const int mosfet_group_2 = 8;
const int mosfet_group_3 = 7;

const int voltage_sensor = A0;

const int temp_1 = A1;
const int temp_2 = A2;
const int temp_3 = A3;
const int temp_4 = A4;
const int temp_5 = A5;
const int temp_6 = A6;


// Declare Program Variables
int hall_sensor_value_1 = LOW;
int hall_sensor_value_2 = LOW;
int hall_sensor_value_3 = LOW;

// Tachometer Vars
float last_report_time = millis();
int num_strokes = 0;
float total_time = 0.0;
float last_toggle_time = millis();

// Voltage Meter Vars
float vOUT = 0.0;
float vIN = 0.0;
float R1 = 30000.0;
float R2 = 7500.0;

// Thermometer Vars
float t1_reading = 0.0;
float t2_reading = 0.0;
float t3_reading = 0.0;
float t4_reading = 0.0;
float t5_reading = 0.0;
float t6_reading = 0.0;


int rpm;

// Define Communication Variables
int messageInterval = 200;

// Test variable
float a;

void print_message(int rpm, float voltage) {

  // Send RPM Information
  Serial.print(rpm);
  Serial.print(",");

  // Send Voltage Information
  Serial.print(voltage);
  Serial.print(",");

  // Send temperature Information
  Serial.print(t1_reading);
  Serial.print(",");
  Serial.print(t2_reading);
  Serial.print(",");
  Serial.print(t3_reading);
  Serial.print(",");
  Serial.print(t4_reading);
  Serial.print(",");
  Serial.print(t5_reading);
  Serial.print(",");
  Serial.println(t6_reading);
}

void read_sensor_data() {
  hall_sensor_value_1 = !digitalRead(hall_set_1);
  hall_sensor_value_2 = !digitalRead(hall_set_2);
  hall_sensor_value_3 = !digitalRead(hall_set_3);
}

void read_voltage_data() {
  // Get voltage information
  vOUT = (analogRead(voltage_sensor) * 5.0) / 1024.0;
  vIN = vOUT / (R2 / (R1 + R2));
}

float read_single_temperature_data(int thermometer_port){
  return 0.4882813 * (analogRead(thermometer_port) - 102.4);
}

void read_temperature_data(){
  t1_reading = read_single_temperature_data(temp_1);
  t2_reading = read_single_temperature_data(temp_2);
  t3_reading = read_single_temperature_data(temp_3);
  t4_reading = read_single_temperature_data(temp_4);
  t5_reading = read_single_temperature_data(temp_5);
  t6_reading = read_single_temperature_data(temp_6);
}

void tick_tachometer() {
  // Tick tachometer counts
  num_strokes += 1;
  total_time += millis() - last_toggle_time;
  last_toggle_time = millis();
}

void setup() {
  // Setup communication
  Serial.begin(1000000);

  // Setup pinmode
  pinMode(hall_set_1, INPUT);
  pinMode(hall_set_2, INPUT);
  pinMode(hall_set_3, INPUT);

  pinMode(mosfet_group_1, OUTPUT);
  pinMode(mosfet_group_2, OUTPUT);
  pinMode(mosfet_group_3, OUTPUT);

  // Initialize data
  read_voltage_data();
  read_temperature_data();
}

void loop() {
  // Read Sensor Data
  read_sensor_data();

  if (hall_sensor_value_1 && hall_sensor_value_2) {
    // Turn off others
    digitalWrite(mosfet_group_1, LOW);
    digitalWrite(mosfet_group_3, LOW);
    // Turn on current
    digitalWrite(mosfet_group_2, HIGH);
    
    tick_tachometer();
    
    while (hall_sensor_value_1 && hall_sensor_value_2) {
      read_sensor_data();
      read_voltage_data();
    }
  }
  else if (hall_sensor_value_2 && hall_sensor_value_3) {
    // Turn off others
    digitalWrite(mosfet_group_1, LOW);
    digitalWrite(mosfet_group_2, LOW);
    // Turn on current
    digitalWrite(mosfet_group_3, HIGH);

    // Report Information
    if ((millis() - last_report_time) >= messageInterval) {
      
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

    while (hall_sensor_value_2 && hall_sensor_value_3) {
      read_sensor_data();
    }
  }
  else if (hall_sensor_value_3 && hall_sensor_value_1) {
    // Turn off others
    digitalWrite(mosfet_group_2, LOW);
    digitalWrite(mosfet_group_3, LOW);
    // Turn on current
    digitalWrite(mosfet_group_1, HIGH);

    // Collect Temperature Data
    read_temperature_data();

    while (hall_sensor_value_3 && hall_sensor_value_1) {
      read_sensor_data();
    }
  }

}
