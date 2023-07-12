#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <AD9833.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64 
#define OLED_RESET     -1 
#define SCREEN_ADDRESS 0x3C 
#define CLK 7
#define DT 8
#define SW 9
#define FSYNC 10
#define relay 6

unsigned long data, freq, count = 10000, hz = 1000;
float freqz, mhz = 1000000.00;
int counter = 0;
int currentStateCLK;
int lastStateCLK, btnState;
unsigned long lastButtonPress = 0;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
AD9833 ad (FSYNC);

void setup(){
  pinMode(CLK,INPUT_PULLUP);
  pinMode(DT,INPUT_PULLUP);
  pinMode(SW, INPUT_PULLUP);
  pinMode(relay, OUTPUT);
  Serial.begin(115200);
  ad.Begin();
  ad.EnableOutput(true);
   if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  lastStateCLK = digitalRead(CLK);
  display.setTextColor(SSD1306_WHITE);
  display.display();
  delay(2000); 
  display.clearDisplay();
  display.display();
  display_update();
}

void loop(){
  encoder();
  button();  
  delay(1);
}

void encoder(){
  currentStateCLK = digitalRead(CLK);
  btnState = digitalRead(SW);
  if (currentStateCLK != lastStateCLK  && currentStateCLK == 1){
    if (digitalRead(DT) != currentStateCLK){
      counter ++;
      if(counter>=500)
        counter=500;
    } 
    else {
      counter --;
      if(counter<=0)
        counter=0;
    }
    data = count * counter;
    display_update();
  }  
  lastStateCLK = currentStateCLK;
}

void button(){
  if (btnState == LOW){
    if (millis() - lastButtonPress > 50){ 
    Serial.println("Button pressed!");
    transducer();
    }
    lastButtonPress = millis();
  }
}

void display_update(){
  freq = data / hz;
  freqz = data / mhz;
  Serial.print("Frekuensi: ");
  Serial.println(data);
  display.clearDisplay();
  display.setTextSize(2); 
  display.setCursor(10.5, 0);
  display.print("Frequency");
  if (data < mhz){
    display.setTextSize(3);
    if (freq < 10){ 
      display.setCursor(23, 35);
      display.print(freq);
      display.setCursor(52, 35);
      display.print("KHz");
    }
    else if (freq < 100){ 
      display.setCursor(15, 35);
      display.print(freq);
      display.setCursor(59, 35);
      display.print("KHz");
    }
    else { 
      display.setCursor(5, 35);
      display.print(freq);
      display.setCursor(69, 35);
      display.print("KHz");
    }
    display.display();
  }
  else {
    display.setTextSize(3); 
    display.setCursor(0, 35);
    display.print(freqz);
    display.setCursor(74, 35);
    display.print("MHz");
    display.display();
  }
  ad.ApplySignal(SQUARE_WAVE, REG0, data);
}

void transducer(){
  digitalWrite (relay, HIGH);
  delay(1000);
  digitalWrite (relay, LOW);
}