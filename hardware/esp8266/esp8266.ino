#define BLYNK_TEMPLATE_ID "TMPL6FYw_SVcK"
#define BLYNK_TEMPLATE_NAME "iot"
#define BLYNK_AUTH_TOKEN "-JtyN9CYCudclKkkfClXNl-i3hQNEGpA"

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <BlynkSimpleEsp8266.h>

char ssid[] = "PTIT.HCM_SV"; 
char pass[] = ""; 
char auth[] = BLYNK_AUTH_TOKEN;

const char* SERVER_URL = "http://10.251.5.56:5000/api/predict";

WiFiClient client;
HTTPClient http;

unsigned long lastPredictTime = 0;
const unsigned long PREDICT_INTERVAL = 1000; 

void setup() {
  Serial.begin(9600);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  Blynk.begin(auth, ssid, pass);
  Serial.print("Ket noi thanh cong");
}

// Ham gui lenh ve Arduino
void sendAlertToArduino(int alertLevel) {
  // Format: ALERT:X (X la muc do 0-3)
  Serial.print("ALERT:");
  Serial.println(alertLevel);
}

// Ham doc JSON thu cong de lay alert_level
int parseAlertLevel(String jsonResponse) {

  int keyIdx = jsonResponse.indexOf("\"alert_level\"");
  if (keyIdx < 0) return -1;
  
  int valStart = jsonResponse.indexOf(":", keyIdx);
  if (valStart < 0) return -1;
  

  int valEnd = jsonResponse.indexOf(",", valStart);
  if (valEnd < 0) valEnd = jsonResponse.indexOf("}", valStart);
  if (valEnd < 0) return -1;
  
  String valStr = jsonResponse.substring(valStart + 1, valEnd);
  return valStr.toInt();
}

int getAlertFromAI(float mq135, float mq7, float pm25, float sound) {
  if (WiFi.status() != WL_CONNECTED) return -1;
  
  http.begin(client, SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(500);
  
  //
  String jsonData = "{";
  jsonData += "\"mq135\":" + String(mq135) + ",";
  jsonData += "\"mq7\":" + String(mq7) + ",";
  jsonData += "\"pm25\":" + String(pm25) + ",";
  jsonData += "\"sound\":" + String(sound);
  jsonData += "}";
  
  int httpCode = http.POST(jsonData);
  int level = -1;
  Serial.println(httpCode);
  if (httpCode == 200) {
    String response = http.getString();
    level = parseAlertLevel(response);
  }
  http.end();
  return level;
}

void loop() {
  Blynk.run();
  
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    
    int c1 = data.indexOf(',');
    int c2 = data.indexOf(',', c1 + 1);
    int c3 = data.indexOf(',', c2 + 1);
    
    if (c1 > 0 && c2 > c1 && c3 > c2) {
      float mq135 = data.substring(0, c1).toFloat();
      float mq7   = data.substring(c1 + 1, c2).toFloat();
      float pm25  = data.substring(c2 + 1, c3).toFloat();
      float sound = data.substring(c3 + 1).toFloat();
      
      // Gui Blynk
      Blynk.virtualWrite(V0, mq135);
      Blynk.virtualWrite(V1, mq7);
      Blynk.virtualWrite(V2, pm25);
      Blynk.virtualWrite(V3, sound);
      
      //
      if (millis() - lastPredictTime >= PREDICT_INTERVAL) {
        int alert = getAlertFromAI(mq135, mq7, pm25, sound);
        if (alert >= 0) {
          sendAlertToArduino(alert);
          Blynk.virtualWrite(V4, alert); //Hien thi muc do len Blynk

          if (alert >= 3) { 
                Blynk.logEvent("canh_bao", "CẢNH BÁO: Môi trường đang ô nhiễm nguy hiểm!");
                Serial.println(">> Da gui thong bao Blynk!");
 

          }
        }
        lastPredictTime = millis();
      }
    }
  }
}