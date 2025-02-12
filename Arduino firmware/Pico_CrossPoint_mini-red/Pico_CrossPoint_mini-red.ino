//Pico_CrossPoint controller using mini red solderless breadboards with MCP4822 DAC
// 1/10/2025
#include "pico/stdlib.h"
#include "hardware/adc.h"
#include "hardware/pwm.h"
#include <hardware/timer.h>
#include <hardware/irq.h>
#include <SPI.h>
#include "pico/multicore.h"

#define ALARM_NUM 1
#define ALARM_IRQ TIMER_IRQ_1

uint8_t scopea[16384]; // 14336/8 ~ 1700 max samples
//  uint8_t digin[4096];
uint16_t awgouta[4096];
uint16_t awgoutb[4096];

short led = 25;
short awgona;
short awgonb;
short awgtpa;
short awgtpb;
short addr;
short data;
short awgdata;
short awgres;
short n;
short m;
short xadr = 0;
short yadr = 0;
short cadr = 1;
short dadr = 7;
short swon = 0;
uint32_t tg;
short sync = 0;
short point = 0;
float Step;
unsigned int at, at2, st, st2, stReal;
short bmax=4096;
short amax=4096;
short bs=1024;
uint16_t tbs=2048;
uint16_t rbs=3072;
uint16_t fbs=4096;
uint16_t vbs=5120;
uint16_t sbs=6144;
uint16_t ebs=7168;
uint16_t gbs=8192;
short dy=1;
uint16_t ns=1024;
uint16_t ms=1024;
int pwmf = 500;
int pwid = 500;

static void alarm_irq(void) {
  hw_clear_bits(&timer_hw->intr, 1u << ALARM_NUM);
  alarm_in_us_arm(at);
  if (awgona == 1){ // send data to DAC A
    if (n >= ns) n = 0;
    SPI.transfer16(awgouta[n]);
    n++;
  } else {
    n = 0;
  }
  if (awgonb == 1) { // send data to DAC B
    if (m >= ms) m = 0;
    SPI.transfer16(awgoutb[m]);
    m++;
  }
  else {
    m = 0;
  }
}

static void alarm_in_us_arm(uint32_t delay_us) {
  uint64_t target = timer_hw->timerawl + delay_us;
  timer_hw->alarm[ALARM_NUM] = (uint32_t) target;
}

static void alarm_in_us(uint32_t delay_us) {
  hw_set_bits(&timer_hw->inte, 1u << ALARM_NUM);
  irq_set_exclusive_handler(ALARM_IRQ, alarm_irq);
  irq_set_enabled(ALARM_IRQ, true);
  alarm_in_us_arm(at);
}

void setup1() {
  at=20;
  awgona = 0; // default AWG A off
  awgonb = 0; // default AWG B off
  alarm_in_us(at);
}

void loop1() {
  
}
  
void setup() {
  
  Serial.begin(2000000);
  pinMode(led, OUTPUT);
  pinMode(0, OUTPUT); // common Clock input 
  pinMode(1, OUTPUT); // common Data input
  pinMode(2, OUTPUT); // common Reset input
  pinMode(3, OUTPUT); // CSD strobe for switch chip D 
  pinMode(4, OUTPUT); // CSE strobe for switch chip E 
  pinMode(5, OUTPUT); // CSC strobe for switch chip C
  pinMode(6, OUTPUT); // CSB strobe for switch chip B 
  pinMode(7, OUTPUT); // CSA strobe for switch chip A
  pinMode(8, OUTPUT); 
  pinMode(9, OUTPUT); 
  pinMode(10, OUTPUT); 
  pinMode(11, OUTPUT); 
  pinMode(12, OUTPUT); 
  pinMode(13, OUTPUT); 
  pinMode(14, OUTPUT); 
  pinMode(15, OUTPUT); 
  // preset cross point control lines
  digitalWrite(0, HIGH); // CLK input idles High
  delayMicroseconds(6); // Wait
  digitalWrite(2, HIGH); // Toggel Reset pin High
  delayMicroseconds(6); // Wait
  digitalWrite(2, LOW); // Reset input defaults Low
  digitalWrite(1, LOW); // Data input defaults Low
  digitalWrite(7, LOW); // Chip A Strobe input defaults Low
  digitalWrite(6, LOW); // Chip B Strobe input defaults Low
  digitalWrite(5, LOW); // Chip C Strobe input defaults Low
  digitalWrite(3, LOW); // Chip D Strobe input defaults Low
  digitalWrite(4, LOW); // Chip E Strobe input defaults Low

  analogWriteFreq(pwmf);
  analogWriteRange(1000);
  adc_init();
  adc_gpio_init(26); // ADC0
  adc_gpio_init(27); // ADC1
  adc_gpio_init(28); // ADC2
  adc_gpio_init(29); // ADC3
  adc_select_input(0);
  SPI.begin(true); // Start up SPI for DAC
  SPI.beginTransaction(SPISettings(25000000, MSBFIRST, SPI_MODE0));  
  //alarm_in_us(at);
} 

void loop() {
  
  int measa;
  int measb;
  int measc;
  int digmeas;
  int VDD;
  char c, c2;
  uint32_t ta, TotalReal, StartReal;
  st=11;
  awgres = 4095;
  at=20;
  short Ain1;
  Ain1 = 0; // 26; // pin number for A1
  short Ain2;
  Ain2 = 1; // 27; // pin number for A2
  short Ain3;
  Ain3 = 2; // 28; // pin number for A3
  short Ain4;
  Ain4 = 3; // 29; // pin number for A4

  while (true) { 
    if (Serial.available()){
      c=Serial.read();
      switch (c){
        case 'I': // read back FW Rev
          Serial.println ("Pi Pico Cross Point Mini Red");
          break;
        case 'T': // change the AWG value of at in uSec both channels must be same rate
          at2 = Serial.parseInt();
          if(at2>0){
            at=at2;
          }
          break;
        case 'N': // change number of AWG A samples 
          ns = Serial.parseInt();
          if(ns>bmax){
            ns=bmax;
          }
          break;
        case 'M': // change number of AWG B samples 
          ms = Serial.parseInt();
          if(ms>bmax){
            ms=bmax;
          }
          break;
        case 'L': // load AWG A Buffer data
          addr = Serial.parseInt();
          if(addr > 2047){
              addr=2047;
            }
            if(addr < 0){
              addr=0;
            }
          c2 = Serial.read();
          if(c2=='D'){
            data = Serial.parseInt();
            if(data > awgres){
              data=awgres;
            }
            if(data < 0){
              data=0;
            }
          } else {
            data = 0;
          }
          awgouta[addr] = data | 0b0001000000000000; // address DACA 2X REF MCP4822
          break;
        case 'l': // load AWG B Buffer data
          addr = Serial.parseInt();
          if(addr > 2047){
              addr=2047;
            }
            if(addr < 0){
              addr=0;
            }
          c2 = Serial.read();
          if(c2=='D'){
            data = Serial.parseInt();
            if(data > awgres){
              data=awgres;
            }
            if(data < 0){
              data=0;
            }
          } else {
            data = 0;
          }
          awgoutb[addr] = data | 0b1001000000000000; // address DACB 2X REF MCP4822
          break;
        case 't': // change the Scope value of dt in uSec
          st2 = Serial.parseInt();
          if(st2>0){
            st=st2;
          }
          break;
        case 'b': // change number of samples to capture
          bs = Serial.parseInt();
          if(bs>bmax){
            bs=bmax;
          }
          tbs = bs * 2;
          rbs = bs * 3;
          fbs = bs * 4;
          vbs = bs * 5;
          sbs = bs * 6;
          ebs = bs * 7;
          gbs = bs * 8;
          break;
        case 'G': // enable - disable AWG A output
          c2 = Serial.read();
          if(c2=='o'){
            awgona = 1;
          }else{
            awgona = 0;
          }
          break;
        case 'g': // enable - disable AWG A output
          c2 = Serial.read();
          if(c2=='o'){
            awgonb = 1;
          }else{
            awgonb = 0;
          }
          break;
        case 'R': // Reset AWG start point at start of aquire
          sync = Serial.parseInt();
          break;
        case 'r': // Set AWG start address when case R > 0
          point = Serial.parseInt();
          break;
        case 's': // enable - disable PWM output
          c2 = Serial.read();
          if(c2=='o'){
            analogWrite (22, pwid); 
          }else{
            analogWrite (22, 0); 
          }
          break;
        case 'p': // change analog write pwm frequency value
          pwmf = Serial.parseInt();
          analogWriteFreq( pwmf );
          break;
        case 'm': // change pwm duty cycle % 
          pwid = Serial.parseInt(); // range from 0 (0%) to 1000 (100%)
          break;
        case 'V': // Read back the 3.3 V supply voltage divider 1/3
          adc_select_input(3);
          sleep_ms(1);
          VDD=adc_read();
          Serial.print ("V=");
          Serial.println ((int) VDD);
          break;
        case 'A': // set input pin value for scope channel Ain1
          Ain1 = Serial.parseInt();
          break;
        case 'B': // set input pin value for scope channel Ain2
          Ain2 = Serial.parseInt();
          break;
        case 'C': // set input pin value for scope channel Ain3
          Ain3 = Serial.parseInt();
          break;
        case 'D': // set input pin value for scope channel Ain4
          Ain4 = Serial.parseInt();
          break;
        case '1': // do scope ch a single capture
        // if sync is on reset start of awg buffer pointer
          if (sync > 0 ) {
            if (awgona == 1 || awgonb == 1){
              awgtpa = awgona;
              awgtpb = awgonb;
              awgona = 0;
              awgonb = 0;
              while ( n != point || m != point ) {
                n = point;
                m = point;
              }
              delayMicroseconds(6);
              awgona = awgtpa;
              awgonb = awgtpb;
              delayMicroseconds(sync);
            }
          }
          ta = time_us_32();
          adc_select_input(Ain1);
          StartReal = ta;
          for (int i = 0; i < bs; i++){ // Fill Buffer
            measa = adc_read(); // analogRead(A1);
            scopea[i] = (measa & 0xFF00) >> 8;
            scopea[i+bs] = measa & 0xFF;
            ta+=st;
            while (ta>time_us_32());
          }
          TotalReal=time_us_32()-StartReal;
          //stReal=TotalReal/bs; // calculate the average time for each reading
          digitalWrite(led, HIGH); // Toggel LED High while sending data
          Serial.print("stReal= ");
          Serial.println(TotalReal); // report total time for bs samples
          // dump buffer over serial
          Serial.write(scopea, tbs);
          Serial.println("");
          //
          digitalWrite(led, LOW);
          break;
          //
        case '2': // do scope ch a and b single capture
        // if sync is on reset start of awg buffer pointer
          if (sync > 0 ) {
            if (awgona == 1 || awgonb == 1){
              awgtpa = awgona;
              awgtpb = awgonb;
              awgona = 0;
              awgonb = 0;
              while ( n != point || m != point ) {
                n = point;
                m = point;
              }
              delayMicroseconds(6);
              awgona = awgtpa;
              awgonb = awgtpb;
              delayMicroseconds(sync);
            }
          }
          ta = time_us_32();
          StartReal = ta;
          for (int i = 0; i < bs; i++){ // Fill Buffer
            adc_select_input(Ain1);
            measa = adc_read();
            adc_select_input(Ain2);
            measb = adc_read();
            scopea[i] = (measa & 0xFF00) >> 8;
            scopea[i+bs] = measa & 0xFF;
            scopea[i+tbs] = (measb & 0xFF00) >> 8;
            scopea[i+rbs] = measb & 0xFF;
            ta+=st;
            while (ta>time_us_32());
          }
          TotalReal=time_us_32()-StartReal;
          //stReal=TotalReal/bs; // calculate the average time for each reading
          digitalWrite(led, HIGH); // Toggel LED High while sending data
          Serial.print("stReal= ");
          Serial.println(TotalReal);
          // Dump Buffer over serial
          Serial.write(scopea, fbs);
          Serial.println("");
          //
          digitalWrite(led, LOW);  // turn the LED off (HIGH is the voltage level)
          break;
          //
        case '3': // do scope ch a b and c single capture
        // if sync is on reset start of awg buffer pointer
          if (sync > 0 ) {
            if (awgona == 1 || awgonb == 1){
              awgtpa = awgona;
              awgtpb = awgonb;
              awgona = 0;
              awgonb = 0;
              while ( n != point || m != point ) {
                n = point;
                m = point;
              }
              delayMicroseconds(6);
              awgona = awgtpa;
              awgonb = awgtpb;
              delayMicroseconds(sync);
            }
          }
          ta = time_us_32();
          StartReal = ta;
          for (int i = 0; i < bs; i++){ // Fill Buffer
            adc_select_input(Ain1);
            measa = adc_read();
            adc_select_input(Ain2);
            measb = adc_read();
            adc_select_input(Ain3);
            measc = adc_read();
            scopea[i] = (measa & 0xFF00) >> 8;
            scopea[i+bs] = measa & 0xFF;
            scopea[i+tbs] = (measb & 0xFF00) >> 8;
            scopea[i+rbs] = measb & 0xFF;
            scopea[i+fbs] = (measc & 0xFF00) >> 8;
            scopea[i+vbs] = measc & 0xFF;
            ta+=st;
            while (ta>time_us_32());
          }
          TotalReal=time_us_32()-StartReal;
          //stReal=TotalReal/bs; // calculate the average time for each reading
          digitalWrite(led, HIGH); // Toggel LED High while sending data
          Serial.print("stReal= ");
          Serial.println(TotalReal);
          // Dump Buffer over serial
          Serial.write(scopea, sbs);
          Serial.println("");
          //
          digitalWrite(led, LOW);  // turn the LED off (HIGH is the voltage level)
          break;
        case 'x': // Reset all cross point switches to off
          digitalWrite(2, HIGH); // Toggel Reset pin High
          delayMicroseconds(6); // Wait
          digitalWrite(2, LOW); // Toggel Reset pin Low
          break;
          //
        case 'X': // set cross point switch at address x , y, on chip () to on / off
          xadr = Serial.parseInt();
          if(xadr>7){
            xadr=7;
          }
          yadr = Serial.parseInt();
          if(yadr>15){
            yadr=15;
          }
          cadr = Serial.parseInt();
          if(cadr>5){
            cadr=5;
          }
          if(cadr==1){
            dadr=7;
          }
          if(cadr==2){
            dadr=6;
          }
          if(cadr==3){
            dadr=5;
          }
          if(cadr==4){
            dadr=3;
          }
          if(cadr==5){
            dadr=4;
          }
          swon = Serial.parseInt();
          digitalWrite(led, HIGH); // Toggel LED High while sending data
          // Send x y address to chip(s)
          digitalWrite(0, HIGH); // CLK input idles High
          // Send first data bit
          if(xadr & 0b100) {
            digitalWrite(1, HIGH); // Data is High
          }else{
            digitalWrite(1, LOW); // Data is Low
          }
          delayMicroseconds(1); // Wait
          digitalWrite(0, LOW); // CLK Low
          delayMicroseconds(5); // Wait
          digitalWrite(0, HIGH); // CLK High
          delayMicroseconds(1); // Wait
          // Send Second data bit
          if(xadr & 0b010) {
            digitalWrite(1, HIGH); // Data is High
          }else{
            digitalWrite(1, LOW); // Data is Low
          }
          delayMicroseconds(4); // Wait
          digitalWrite(0, LOW); // CLK Low
          delayMicroseconds(5); // Wait
          digitalWrite(0, HIGH); // CLK High
          delayMicroseconds(1); // Wait
          // Send third data bit
          if(xadr & 0b001) {
            digitalWrite(1, HIGH); // Data is High
          }else{
            digitalWrite(1, LOW); // Data is Low
          }
          delayMicroseconds(4); // Wait
          digitalWrite(0, LOW); // CLK Low
          delayMicroseconds(5); // Wait
          digitalWrite(0, HIGH); // CLK High
          delayMicroseconds(1); // Wait
          // Now Yaddr
          // Send first data bit
          if(yadr & 0b1000) {
            digitalWrite(1, HIGH); // Data is High
          }else{
            digitalWrite(1, LOW); // Data is Low
          }
          delayMicroseconds(4); // Wait
          digitalWrite(0, LOW); // CLK Low
          delayMicroseconds(5); // Wait
          digitalWrite(0, HIGH); // CLK High
          delayMicroseconds(1); // Wait
          // Send Second data bit
          if(yadr & 0b0100) {
            digitalWrite(1, HIGH); // Data is High
          }else{
            digitalWrite(1, LOW); // Data is Low
          }
          delayMicroseconds(4); // Wait
          digitalWrite(0, LOW); // CLK Low
          delayMicroseconds(5); // Wait
          digitalWrite(0, HIGH); // CLK High
          delayMicroseconds(1); // Wait
          // Send Third data bit
          if(yadr & 0b0010) {
            digitalWrite(1, HIGH); // Data is High
          }else{
            digitalWrite(1, LOW); // Data is Low
          }
          delayMicroseconds(4); // Wait
          digitalWrite(0, LOW); // CLK Low
          delayMicroseconds(5); // Wait
          digitalWrite(0, HIGH); // CLK High
          delayMicroseconds(1); // Wait
          // Send fourth data bit
          if(yadr & 0b0001) {
            digitalWrite(1, HIGH); // Data is High
          }else{
            digitalWrite(1, LOW); // Data is Low
          }
          delayMicroseconds(4); // Wait
          digitalWrite(0, LOW); // CLK Low
          delayMicroseconds(5); // Wait
          digitalWrite(0, HIGH); // CLK High
          delayMicroseconds(1); // Wait
          // Now Strobe which chip
          if(swon == 1){
            digitalWrite(1, HIGH); // Data is High switch on
          }else{
            digitalWrite(1, LOW); // Data is Low switch off
          }
          //
          delayMicroseconds(4); // Wait
          digitalWrite(dadr, HIGH); // STB High
          delayMicroseconds(5); // Wait
          digitalWrite(dadr, LOW); // STB Low
          delayMicroseconds(5); // Wait
          digitalWrite(1, LOW); // Data is Low switch off
          digitalWrite(led, LOW); // Toggel LED Low after sending data
          break;
          //
      }
    }
  }
}

