/*************************************************** 
  Written by Ashwath Murali for BE5 hackathon
  Warema window blinds challenge
 ****************************************************/
#include <Arduino.h>
#include <Wire.h>
#include "Adafruit_SI1145.h" // IR sensor
#include "Adafruit_SHT31.h" // Temp sensor
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <string>
#include <sstream>
#include "Adafruit_VL6180X.h"

Adafruit_VL6180X vl = Adafruit_VL6180X();
Adafruit_SI1145 uv = Adafruit_SI1145();
Adafruit_SHT31 sht31 = Adafruit_SHT31();

// Globals

/*
 * 0 - Reset/Undefined
 * 1 - Move UP
 * 2 - Move DOWN
 * 3 - Open
 * 4 - Close
 * 5 - Reset
*/

uint8_t range, getStatus;
bool sendProxData = false;
bool range_valid = false;
float t, h; // temperature humidity
float UVindex; 
int IR, VIS;

const int UVdelay = 1000;
const int thDelay = 1000;
const int proxDelay = 10;
const int blindOpenDelay = 1000;
const int blindCloseDelay = 1000;
const int resetBlindDelay = 40000;
const int basicOpenDelay = 3000;
const int basicCloseDelay = 3000;
const int serverGeneralDelay = 500;
const int proxyServerDelay = 500; 


void setup() {
  pinMode(12, OUTPUT); //go down
  pinMode(13, OUTPUT); //go up
  digitalWrite(13, HIGH);
  digitalWrite(12, HIGH);
  
  Serial.begin(9600);
  
  Serial.println("Adafruit SI1145 test");
  
  if (! uv.begin()) {
    Serial.println("Didn't find Si1145");
    while (1);
  }
  Serial.println("SHT31 test");
  if (! sht31.begin(0x44)) {   // Set to 0x45 for alternate i2c addr
    Serial.println("Couldn't find SHT31");
    while (1) delay(1);
  }
  WiFi.begin("1-UTUM-Guest-psk", "be54wifi");   //WiFi connection
 
  while (WiFi.status() != WL_CONNECTED) {  //Wait for the WiFI connection completion
 
    delay(500);
    Serial.println("Waiting for connection");
 
  }
  if (! vl.begin()) {
    Serial.println("Failed to find sensor");
    while (1);
  }
  

  Serial.println("OK!");
}

void goDown(int time_t){
  digitalWrite(13, LOW);
  digitalWrite(12, HIGH);
  Serial.println("Moved Down");
  delay(time_t);
  digitalWrite(13, HIGH);
  digitalWrite(12, HIGH);
}

void goUp(int time_t){
  digitalWrite(13, HIGH);
  digitalWrite(12, LOW);
  Serial.println("Moved Up");
  delay(time_t);
  digitalWrite(13, HIGH);
  digitalWrite(12, HIGH);
}

void getTH(){
  Serial.println("===================");
  t = sht31.readTemperature();
  h = sht31.readHumidity();

  if (! isnan(t)) {  // check if 'is not a number'
    Serial.print("Temp *C = "); Serial.println(t);
  } else { 
    Serial.println("Failed to read temperature");
  }
  
  if (! isnan(h)) {  // check if 'is not a number'
    Serial.print("Hum. % = "); Serial.println(h);
  } else { 
    Serial.println("Failed to read humidity");
  }
  Serial.println();
  delay(thDelay);
}

void getUV(){
  Serial.print("Vis: "); Serial.println(uv.readVisible());
  Serial.print("IR: "); Serial.println(uv.readIR());
  
  // Uncomment if you have an IR LED attached to LED pin!
  //Serial.print("Prox: "); Serial.println(uv.readProx());

  UVindex = uv.readUV();
  // the index is multiplied by 100 so to get the
  // integer index, divide by 100!
  UVindex /= 100.0;  
  IR = uv.readIR();
  VIS = uv.readVisible();
  Serial.print("UV: ");  Serial.println(UVindex);

  delay(UVdelay);
}


void getProx(){
  range = vl.readRange();
  uint8_t status = vl.readRangeStatus();

  if (status == VL6180X_ERROR_NONE) {
    Serial.print("Range: "); Serial.println(range);
    range_valid = true;
  }

  // Some error occurred, print it out!
  
  if  ((status >= VL6180X_ERROR_SYSERR_1) && (getStatus <= VL6180X_ERROR_SYSERR_5)) {
    range = 250;
    Serial.println("System error");
  }
  else if (status == VL6180X_ERROR_ECEFAIL) {
    range = 250;
    Serial.println("ECE failure");
  }
  else if (status == VL6180X_ERROR_NOCONVERGE) {
    range = 250;
    Serial.println("No convergence");
  }
  else if (status == VL6180X_ERROR_RANGEIGNORE) {
    range = 250;
    Serial.println("Ignoring range");
  }
  else if (status == VL6180X_ERROR_SNR) {
    range = 250;
    Serial.println("Signal/Noise error");
  }
  else if (status == VL6180X_ERROR_RAWUFLOW) {
    range = 250;
    Serial.println("Raw reading underflow");
  }
  else if (status == VL6180X_ERROR_RAWOFLOW) {
    range = 250;
    Serial.println("Raw reading overflow");
  }
  else if (status == VL6180X_ERROR_RANGEUFLOW) {
    range = 250;
    Serial.println("Range reading underflow");
  }
  else if (status == VL6180X_ERROR_RANGEOFLOW) {
    range = 250;
    Serial.println("Range reading overflow");
  }
  if(range < 150 && range_valid){
    sendProxData = true;
  }
  delay(proxDelay);
}

void sendUserNearby(){
  if(WiFi.status()== WL_CONNECTED){   //Check WiFi connection status
 
   HTTPClient http;    //Declare object of class HTTPClient
   char range_buf[10];
   dtostrf(range, 4, 4, range_buf);
   std::string range_var(range_buf);
   http.begin(("http://10.25.12.154/proximity/?prox="+range_var).c_str());      //Specify request destination
   http.addHeader("Content-Type", "text/plain");  //Specify content-type header
 
   int httpCode = http.GET();   //Send the request
   String payload = http.getString();                  //Get the response payload 
   
 
   //Serial.println(httpCode);   //Print HTTP return code
   //Serial.println(payload);    //Print request response payload
   Serial.println("Prximity data sent");
 
   http.end();  //Close connection
 
   }else
   {
      Serial.println("Error in WiFi connection");
   }
 
  delay(proxyServerDelay);  //Send a request every 30 seconds
}

void sendServerData(){
  if(WiFi.status()== WL_CONNECTED){   //Check WiFi connection status
 
   HTTPClient http;    //Declare object of class HTTPClient
   char t_buf[10];
   dtostrf(t, 4, 4, t_buf);
   std::string t_var(t_buf);
   char h_buf[10];
   dtostrf(h, 4, 4, h_buf);
   std::string h_var(h_buf);
   char uv_buf[10];
   dtostrf(UVindex, 4, 4, uv_buf);
   std::string uv_var(uv_buf);
   char vis_buf[10];
   dtostrf(VIS, 4, 4, vis_buf);
   std::string vis_var(vis_buf);
   char ir_buf[10];
   dtostrf(IR, 4, 4, ir_buf);
   std::string ir_var(ir_buf);
   http.begin(("http://10.25.12.154/data/?temp="+t_var+"&hum="+h_var+"&uv="+uv_var+"&lum="+vis_var+"&ir="+ir_var).c_str());      //Specify request destination
   http.addHeader("Content-Type", "text/plain");  //Specify content-type header
 
   int httpCode = http.GET();   //Send the request
   String payload = http.getString();                  //Get the response payload 
   
 
   //Serial.println(httpCode);   //Print HTTP return code
   //Serial.println(payload);    //Print request response payload
   Serial.println("Data Sent");
 
   http.end();  //Close connection
 
   }else
   {
      Serial.println("Error in WiFi connection");
   }
 
  delay(serverGeneralDelay);  //Send a request every 30 seconds
}

void getServerData(){
  if(WiFi.status()== WL_CONNECTED){   //Check WiFi connection status
 
   HTTPClient http;    //Declare object of class HTTPClient
   http.begin("http://10.25.12.154");      //Specify request destination
   http.addHeader("Content-Type", "text/plain");  //Specify content-type header
 
   int httpCode = http.GET();   //Send the request
   String payload = http.getString();                  //Get the response payload 
   
   Serial.println("===================");
   Serial.println(httpCode);   //Print HTTP return code
   Serial.println("Received data:");
   Serial.println(payload[0]);    //Print request response payload

   if(payload[0] == '1'){
    goUp(basicOpenDelay);
   }
   else if(payload[0] == '2'){
    //Serial.println("Debug 2/5");
    goDown(basicCloseDelay);
   }
   else if(payload[0] == '5'){
    goDown(resetBlindDelay);
   }
   else if(payload[0] == '3'){
    //think about this 
    // open blinds
    goUp(blindOpenDelay);
   }
   else if(payload[0] == '4'){
    goDown(blindCloseDelay);
   }
   else if(payload[0] == '6'){
    goUp(resetBlindDelay);
   }
   else{
    digitalWrite(12, HIGH);
    digitalWrite(13,HIGH);
   }
 
   http.end();  //Close connection
 
   }
   else
   {
      Serial.println("Error in WiFi connection");
   }
   if(sendProxData){
    delay(proxyServerDelay);
   }
   else{
   delay(serverGeneralDelay);
   }
}

void loop() {

  // PROXIMITY SENSOR
  getProx();

  if(sendProxData){
    // send proximity data to server
    sendUserNearby();
  }

  else{
    // TEMP SENSOR
    getTH();
  
    // IR SENSOR
    getUV();
    
    // WIFI ADAPTER SEND DATA
    sendServerData();
  }  
  
  // reset bool
  sendProxData = false;
  range_valid = false;

  // WIFI ADAPTER RECEIVE COMMAND
  getServerData();
  

}