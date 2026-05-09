#define BUZZER 5 // For buzzing
#define RED_LED 19 // Onboard LED for Distracted
#define GREEN_LED 21 // Onboard LED for Focused
#define LED_BUILTIN 2 // Onboard LED for status

int distraction_score = 0;
int max_threshold = 16; // 8 cycles of 2 seconds
unsigned long last_tick = 0;
bool systemActive = false;
bool alertTriggered = false;
char current_state = 'F';

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH); 
}

void loop() {
  if (Serial.available() > 0) {
    char signal = Serial.read();
    
    if (signal == 'S') { 
      systemActive = true; 
      distraction_score = 0; 
      digitalWrite(LED_BUILTIN, LOW); // Turn OFF when monitoring starts
    }
    else if (signal == 'X') { 
      systemActive = false; 
      digitalWrite(LED_BUILTIN, HIGH); // Turn back ON when session ends
      digitalWrite(RED_LED, LOW);
      digitalWrite(GREEN_LED, LOW);
      digitalWrite(BUZZER, LOW);
    }
    else if (signal == 'C') { 
      distraction_score = 0; 
      digitalWrite(BUZZER, LOW); 
      alertTriggered = false; 
    }
    else { 
      current_state = signal; 
    }
  }

  // 2-Second Power Sync Logic
  if (systemActive && (millis() - last_tick >= 2000)) { 
    if (current_state == 'D') {
      distraction_score += 2;
      digitalWrite(RED_LED, HIGH);
      digitalWrite(GREEN_LED, LOW);
    } else {
      distraction_score = 0;
      digitalWrite(RED_LED, LOW);
      digitalWrite(GREEN_LED, HIGH);
      digitalWrite(BUZZER, LOW);
    }

    if (distraction_score >= max_threshold && !alertTriggered) {
      digitalWrite(BUZZER, HIGH);
      Serial.println("T"); 
      alertTriggered = true;
    }
    last_tick = millis();
  }
}