#include <MQUnifiedsensor.h>
#include <SoftwareSerial.h>
#include <LiquidCrystal.h>
#include <GP2YDustSensor.h>

// --- CẤU HÌNH ---
#define LED_BLUE_PIN   3  
#define LED_YELLOW_PIN 4  
#define LED_RED_PIN    5  
#define BUZZER_PIN     A4 

LiquidCrystal lcd(6, 7, 8, 9, 10, 11);
SoftwareSerial espSerial(13, 12); 

#define DUST_LED_PIN  2
#define DUST_PIN      A2
#define SOUND_PIN     A3

GP2YDustSensor dustSensor(GP2YDustSensorType::GP2Y1010AU0F, DUST_LED_PIN, DUST_PIN);

#define Board "Arduino UNO"
MQUnifiedsensor MQ135(Board, 5, 10, A0, "MQ-135");
MQUnifiedsensor MQ7(Board, 5, 10, A1, "MQ-7");

int currentAlert = 0; 

void setup() {
  Serial.begin(9600);
  espSerial.begin(9600);
  
  pinMode(LED_BLUE_PIN, OUTPUT);
  pinMode(LED_YELLOW_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW); 

  dustSensor.begin();
  lcd.begin(16, 2);
  lcd.print("System Init...");
  
  MQ135.setRegressionMethod(1); MQ135.setA(110.47); MQ135.setB(-2.862); MQ135.init(); MQ135.setR0(10.0);
  MQ7.setRegressionMethod(1); MQ7.setA(99.042); MQ7.setB(-1.518); MQ7.init(); MQ7.setR0(10.0);
  
  delay(1000); lcd.clear();
}

float getDust() {
  float dust = dustSensor.getDustDensity();
  return (dust < 0) ? 0 : dust;
}

float getSound() {
  long sum = 0;
  for(int i=0; i<32; i++) sum += analogRead(SOUND_PIN);
  float avg = sum/32.0;
  return map(avg, 0, 800, 35, 90); 
}

// --- [TỐI ƯU] HÀM LOA KHÔNG DELAY ---
void controlBuzzer(int level) {
  static unsigned long lastChange = 0;
  static bool state = false;
  unsigned long now = millis();
  unsigned long onDuration = 0;
  unsigned long offDuration = 0;

  if (level == 0) {
    digitalWrite(BUZZER_PIN, LOW);
    state = false;
    return;
  }
  else if (level == 1 || level == 2) {
    // Kêu 200ms, nghỉ 500ms
    onDuration = 200;
    offDuration = 500;
  }
  else if (level == 3) {
    // Kêu 100ms, nghỉ 100ms (Gấp)
    onDuration = 100;
    offDuration = 100;
  }

  // Logic chớp tắt dựa trên millis
  if (state) { // Đang kêu
    if (now - lastChange >= onDuration) {
      digitalWrite(BUZZER_PIN, LOW);
      state = false;
      lastChange = now;
    }
  } else { // Đang nghỉ
    if (now - lastChange >= offDuration) {
      digitalWrite(BUZZER_PIN, HIGH);
      state = true;
      lastChange = now;
    }
  }
}

void loop() {
  // 1. ĐỌC CẢM BIẾN
  MQ135.update(); float v135 = MQ135.readSensor();
  MQ7.update();   float v7 = MQ7.readSensor();
  float vDust = getDust();
  float vSound = getSound();

  // 2. GỬI ESP (1 giây/lần)
  static unsigned long lastSend = 0;
  if (millis() - lastSend > 1000) {
    espSerial.print(v135); espSerial.print(",");
    espSerial.print(v7);   espSerial.print(",");
    espSerial.print(vDust);espSerial.print(",");
    espSerial.println(vSound);
    lastSend = millis();
  }

  // 3. NHẬN LỆNH TỪ ESP (Dùng while để đọc sạch bộ đệm)
  while (espSerial.available()) {
    String resp = espSerial.readStringUntil('\n');
    resp.trim();
    if (resp.startsWith("ALERT:")) {
      currentAlert = resp.substring(6).toInt();
    }
  }

  // 4. XỬ LÝ OUTPPUT (Loa & LED & LCD)
  controlBuzzer(currentAlert); // Hàm này giờ không còn delay nữa -> Chạy mượt

  if (currentAlert == 0) {
    digitalWrite(LED_BLUE_PIN, HIGH); digitalWrite(LED_YELLOW_PIN, LOW); digitalWrite(LED_RED_PIN, LOW);
  } else if (currentAlert <= 2) {
    digitalWrite(LED_BLUE_PIN, LOW); digitalWrite(LED_YELLOW_PIN, HIGH); digitalWrite(LED_RED_PIN, LOW);
  } else { 
    digitalWrite(LED_BLUE_PIN, LOW); digitalWrite(LED_YELLOW_PIN, LOW); digitalWrite(LED_RED_PIN, HIGH);
  }

  static unsigned long lastLCD = 0;
  if (millis() - lastLCD > 500) { 
    lcd.setCursor(0, 0);
    if (currentAlert == 0) lcd.print("   FRESH AIR    ");
    else if (currentAlert == 1) lcd.print(" AIR POLLUTION  ");
    else if (currentAlert == 2) lcd.print(" NOISE POLLUTION");
    else lcd.print("   DANGER !!!   ");
    lastLCD = millis();
  }
}