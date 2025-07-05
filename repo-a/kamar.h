#ifndef KAMAR_CONTROL_H
#define KAMAR_CONTROL_H

#include <Arduino.h>
#include <DHT.h>
#include <Fuzzy.h>
#include "api_handler.h"

// --- Konfigurasi Pin (Tidak berubah) ---
#define DHT_PIN_KAMAR      32
#define DHT_TYPE_KAMAR     DHT11
#define FAN_PIN_KAMAR      33
#define MAGNETIC_PIN_KAMAR 27
#define BUZZER_PIN_KAMAR   25 // Mengganti pin agar tidak bentrok dengan Dapur jika buzzer bersamaan
#define PWM_CHANNEL_KAMAR  1
#define PWM_FREQ_KAMAR     1000
#define PWM_RESOLUTION_KAMAR 8

DHT dht_kamar(DHT_PIN_KAMAR, DHT_TYPE_KAMAR);
Fuzzy* fuzzy_kamar = new Fuzzy();

// --- Variabel Global Status Kamar ---
float lastTemperature_kamar = 0;
float lastHumidity_kamar = 0;
int   lastMagneticValue_kamar = 0;
String lastDoorStatus_kamar = "CLOSED";
int   lastFanPWM_kamar = 0;

// --- DITAMBAHKAN: Flag untuk Manual Override ---
bool manualFanOverride_kamar = false;

unsigned long lastSendTime_kamar = 0;
const unsigned long sendInterval_kamar = 30000;

// =================================================================
// Deklarasi dan Implementasi Fungsi
// =================================================================
void initializeFuzzySystemKamar(Fuzzy* fuzzyObj) {
  FuzzySet* suhuDingin = new FuzzySet(26, 28, 30, 32);
  FuzzySet* suhuSedang = new FuzzySet(31, 32, 34, 36);
  FuzzySet* suhuPanas  = new FuzzySet(35, 36, 50, 50);
  FuzzySet* kelembabanKering = new FuzzySet(0, 0, 40, 60);
  FuzzySet* kelembabanNormal = new FuzzySet(55, 60, 70, 75);
  FuzzySet* kelembabanLembab = new FuzzySet(70, 75, 100, 100);
  FuzzySet* kipasMati   = new FuzzySet(0, 0, 0, 0);
  FuzzySet* kipasPelan  = new FuzzySet(80, 90, 110, 130);
  FuzzySet* kipasSedang = new FuzzySet(130, 150, 170, 190);
  FuzzySet* kipasCepat  = new FuzzySet(190, 210, 255, 255);
  FuzzyInput* temperature = new FuzzyInput(1);
  temperature->addFuzzySet(suhuDingin);
  temperature->addFuzzySet(suhuSedang);
  temperature->addFuzzySet(suhuPanas);
  fuzzyObj->addFuzzyInput(temperature);
  FuzzyInput* humidity = new FuzzyInput(2);
  humidity->addFuzzySet(kelembabanKering);
  humidity->addFuzzySet(kelembabanNormal);
  humidity->addFuzzySet(kelembabanLembab);
  fuzzyObj->addFuzzyInput(humidity);
  FuzzyOutput* fanSpeed = new FuzzyOutput(1);
  fanSpeed->addFuzzySet(kipasMati);
  fanSpeed->addFuzzySet(kipasPelan);
  fanSpeed->addFuzzySet(kipasSedang);
  fanSpeed->addFuzzySet(kipasCepat);
  fuzzyObj->addFuzzyOutput(fanSpeed);
  FuzzyRuleAntecedent* ifSuhuPanas = new FuzzyRuleAntecedent();
  ifSuhuPanas->joinSingle(suhuPanas);
  FuzzyRuleConsequent* thenKipasCepat = new FuzzyRuleConsequent();
  thenKipasCepat->addOutput(kipasCepat);
  FuzzyRule* rule1 = new FuzzyRule(1, ifSuhuPanas, thenKipasCepat);
  fuzzyObj->addFuzzyRule(rule1);
  FuzzyRuleAntecedent* ifLembab = new FuzzyRuleAntecedent();
  ifLembab->joinSingle(kelembabanLembab);
  FuzzyRuleConsequent* thenKipasSedang = new FuzzyRuleConsequent();
  thenKipasSedang->addOutput(kipasSedang);
  FuzzyRule* rule2 = new FuzzyRule(2, ifLembab, thenKipasSedang);
  fuzzyObj->addFuzzyRule(rule2);
  FuzzyRuleAntecedent* ifSuhuSedangDanNormal = new FuzzyRuleAntecedent();
  ifSuhuSedangDanNormal->joinWithAND(suhuSedang, kelembabanNormal);
  FuzzyRuleConsequent* thenKipasPelan = new FuzzyRuleConsequent();
  thenKipasPelan->addOutput(kipasPelan);
  FuzzyRule* rule3 = new FuzzyRule(3, ifSuhuSedangDanNormal, thenKipasPelan);
  fuzzyObj->addFuzzyRule(rule3);
  FuzzyRuleAntecedent* ifSuhuDingin = new FuzzyRuleAntecedent();
  ifSuhuDingin->joinSingle(suhuDingin);
  FuzzyRuleConsequent* thenKipasMati = new FuzzyRuleConsequent();
  thenKipasMati->addOutput(kipasMati);
  FuzzyRule* rule4 = new FuzzyRule(4, ifSuhuDingin, thenKipasMati);
  fuzzyObj->addFuzzyRule(rule4);
}

void setupMagneticSensor_kamar() {
  pinMode(MAGNETIC_PIN_KAMAR, INPUT_PULLUP);
  lastMagneticValue_kamar = digitalRead(MAGNETIC_PIN_KAMAR);
  lastDoorStatus_kamar = (lastMagneticValue_kamar == HIGH) ? "OPEN" : "CLOSED";
  Serial.print("Magnetic Sensor Kamar - Status Awal Pintu: ");
  Serial.println(lastDoorStatus_kamar);
}

void setupBuzzer_kamar() {
  pinMode(BUZZER_PIN_KAMAR, OUTPUT);
  digitalWrite(BUZZER_PIN_KAMAR, LOW);
}

void setupPWMFan_kamar() {
  ledcSetup(PWM_CHANNEL_KAMAR, PWM_FREQ_KAMAR, PWM_RESOLUTION_KAMAR);
  ledcAttachPin(FAN_PIN_KAMAR, PWM_CHANNEL_KAMAR);
  ledcWrite(PWM_CHANNEL_KAMAR, 0);
}

void setupKamar() {
  dht_kamar.begin();
  setupPWMFan_kamar();
  setupMagneticSensor_kamar();
  setupBuzzer_kamar();
  initializeFuzzySystemKamar(fuzzy_kamar);
}

int readMagneticSensor_kamar() {
  return digitalRead(MAGNETIC_PIN_KAMAR);
}

// --- DITAMBAHKAN: Fungsi untuk mengontrol mode kipas kamar ---
void setFanOverride_kamar(bool isManual) {
  manualFanOverride_kamar = isManual;
  Serial.printf("[Kamar] Mode kipas diubah ke: %s\n", isManual ? "MANUAL" : "OTOMATIS");
}

void updateDoorStatus_kamar() {
  int previousValue = lastMagneticValue_kamar;
  lastMagneticValue_kamar = readMagneticSensor_kamar();
  lastDoorStatus_kamar = (lastMagneticValue_kamar == HIGH) ? "OPEN" : "CLOSED";
  if (previousValue != lastMagneticValue_kamar) {
    Serial.print("Status Pintu Kamar Berubah: ");
    Serial.println(lastDoorStatus_kamar);
  }
}

void handleBuzzerAlarms_kamar() {
  bool isDoorOpen = (lastMagneticValue_kamar == HIGH);
  if (isDoorOpen) {
    Serial.println("!!! Kamar: PINTU/JENDELA TERBUKA !!!");
    digitalWrite(BUZZER_PIN_KAMAR, HIGH);
  } else {
    digitalWrite(BUZZER_PIN_KAMAR, LOW);
  }
}

// --- Fungsi Kontrol Utama (Loop) ---
void loopKamar() {
  float temperature = dht_kamar.readTemperature();
  float humidity = dht_kamar.readHumidity();
  lastMagneticValue_kamar = digitalRead(MAGNETIC_PIN_KAMAR);
  lastDoorStatus_kamar = (lastMagneticValue_kamar == HIGH) ? "OPEN" : "CLOSED";

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("[Kamar] Gagal membaca dari sensor DHT!");
    return;
  }
  lastTemperature_kamar = temperature;
  lastHumidity_kamar = humidity;

  // Kontrol Buzzer
  digitalWrite(BUZZER_PIN_KAMAR, lastMagneticValue_kamar == HIGH ? HIGH : LOW);

  int fanSpeedOutput;
  // --- LOGIKA MANUAL OVERRIDE ---
  if (manualFanOverride_kamar) {
      fanSpeedOutput = 255; // Paksa kecepatan 100%
  } else {
      // Mode Otomatis (Fuzzy)
      fuzzy_kamar->setInput(1, temperature);
      fuzzy_kamar->setInput(2, humidity);
      fuzzy_kamar->fuzzify();
      fanSpeedOutput = fuzzy_kamar->defuzzify(1);
  }

  ledcWrite(PWM_CHANNEL_KAMAR, fanSpeedOutput);
  lastFanPWM_kamar = fanSpeedOutput;

  Serial.printf("[Kamar] Suhu:%.1fC, Lembab:%.1f%%, Pintu:%s, KipasPWM:%d\n",
    lastTemperature_kamar, lastHumidity_kamar, lastDoorStatus_kamar.c_str(), lastFanPWM_kamar);

  // --- LOGIKA PENGIRIMAN DATA GENERIK ---
  bool isUrgent = (lastDoorStatus_kamar == "OPEN");
  if (isUrgent || (millis() - lastSendTime_kamar >= sendInterval_kamar)) {
      StaticJsonDocument<256> doc;
      doc["temperature"] = lastTemperature_kamar;
      doc["humidity"] = lastHumidity_kamar;
      doc["magnetic_value"] = lastMagneticValue_kamar;
      doc["fan_pwm"] = lastFanPWM_kamar;

      // Memanggil fungsi generik dari api_handler.h
      sendDeviceDataToServer("kamar", doc);
      
      lastSendTime_kamar = millis();
  }
}
#endif // KAMAR_CONTROL_H