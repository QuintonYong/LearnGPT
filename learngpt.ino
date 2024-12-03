#include <LiquidCrystal.h>

#define button0 A5
#define button1 A4
#define button2 A3

int contrast = 85;

// initialize the library by associating any needed LCD interface pin
// with the arduino pin number it is connected to
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// button globals
int previousBtnState = LOW;
long startTime;
int debounceTime = 300;

void setup() {
  Serial.begin(9600);
  analogWrite(6, contrast);
  pinMode(button0, INPUT);
  pinMode(button1, INPUT);
  pinMode(button2, INPUT);
  startTime = millis();
  
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  // Print a message to the LCD.
  lcd.setCursor(3, 0);
  lcd.print("Welcome to");
  lcd.setCursor(4, 1);
  lcd.print("LearnGPT!");

  delay(2000);

  lcd.begin(16, 2);
  lcd.print("Look at camera");
  lcd.setCursor(0, 1);
  lcd.print("to log in...");

  // login
  while(true) {
    String login = Serial.readStringUntil('\n');
    if (login == "LOGIN") {
      break;
    }
  }

  lcd.begin(16, 2);
  lcd.setCursor(2, 0);
  lcd.print("Welcome back");
  lcd.setCursor(4, 1);
  lcd.print("Quinton!");

  delay(3000);
  lcd.begin(16, 2);
  lcd.setCursor(1, 0);
  lcd.print("Please select");
  lcd.setCursor(3, 1);
  lcd.print("a mode...");

}

void checkPush(int pinNumber) {
  long currentTime = millis();
  int buttonPushed = digitalRead(pinNumber);
  bool stateChange = buttonPushed == HIGH && previousBtnState != HIGH; 
  bool debounceCheck = currentTime - startTime > debounceTime;

  if (stateChange && debounceCheck) {
    if (pinNumber == button0) { // learn button
      lcd.begin(16, 2);
      lcd.print("Learning Mode");
      Serial.println("L");
    } else if (pinNumber == button1) { // test button
      lcd.begin(16, 2);
      lcd.print("Testing Mode");
      Serial.println("T");
    } else if (pinNumber == button2) { // history button
      lcd.begin(16, 2);
      lcd.print("History Mode");
      Serial.println("H");
    }
    startTime = millis();
  }
  previousBtnState = buttonPushed;
}

void loop() {

  checkPush(button0);
  checkPush(button1);
  checkPush(button2);
  
}
