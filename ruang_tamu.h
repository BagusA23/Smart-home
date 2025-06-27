#ifndef RUANG_TAMU_CONTROL_H
#define RUANG_TAMU_CONTROL_H

#include <Arduino.h>
#include <DHT.h>
#include <Fuzzy.h>
#include "api_handler.h"

// --- Konfigurasi Pin (Tidak berubah) ---
#define DHT_PIN_RUANG_TAMU      16
#define DHT_TYPE_RUANG_TAMU     DHT11
#define FAN_PIN_RUANG_TAMU      4
#define MAGNETIC_PIN_RUANG_TAMU 14
#define BUZZER_PIN_RUANG_TAMU   12 // Mengganti pin agar tidak bentrok
#define PWM_CHANNEL_RUANG_TAMU  2
#define PWM_FREQ_RUANG_TAMU     1000
#define PWM_RESOLUTION_RUANG_TAMU 8

DHT dht_ruang_tamu(DHT_PIN_RUANG_TAMU, DHT_TYPE_RUANG_TAMU);
Fuzzy* fuzzy_ruang_tamu = new Fuzzy();

// --- Variabel Global Status Ruang Tamu ---
float lastTemperature_ruang_tamu = 0;
float lastHumidity_ruang_tamu = 0;
int   lastMagneticValue_ruang_tamu = 0;
String lastDoorStatus_ruang_tamu = "CLOSED";
int   lastFanPWM_ruang_tamu = 0;

// --- DITAMBAHKAN: Flag untuk Manual Override ---
bool manualFanOverride_ruang_tamu = false;

unsigned long lastSendTime_ruang_tamu = 0;
const unsigned long sendInterval_ruang_tamu = 30000;

// =================================================================
// Deklarasi dan Implementasi Fungsi
// =================================================================
void initializeFuzzySystemRuangTamu(Fuzzy* fuzzyObj) {
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

void setupMagneticSensor_ruang_tamu() {
  pinMode(MAGNETIC_PIN_RUANG_TAMU, INPUT_PULLUP);
  lastMagneticValue_ruang_tamu = digitalRead(MAGNETIC_PIN_RUANG_TAMU);
  lastDoorStatus_ruang_tamu = (lastMagneticValue_ruang_tamu == HIGH) ? "OPEN" : "CLOSED";
  Serial.print("Magnetic Sensor Ruang Tamu - Status Awal Pintu: ");
  Serial.println(lastDoorStatus_ruang_tamu);
}

void setupBuzzer_ruang_tamu() {
  pinMode(BUZZER_PIN_RUANG_TAMU, OUTPUT);
  digitalWrite(BUZZER_PIN_RUANG_TAMU, LOW);
}

void setupPWMFan_ruang_tamu() {
  ledcSetup(PWM_CHANNEL_RUANG_TAMU, PWM_FREQ_RUANG_TAMU, PWM_RESOLUTION_RUANG_TAMU);
  ledcAttachPin(FAN_PIN_RUANG_TAMU, PWM_CHANNEL_RUANG_TAMU);
  ledcWrite(PWM_CHANNEL_RUANG_TAMU, 0);
}

void setupRuangTamu() {
  dht_ruang_tamu.begin();
  setupPWMFan_ruang_tamu();
  setupMagneticSensor_ruang_tamu();
  setupBuzzer_ruang_tamu();
  initializeFuzzySystemRuangTamu(fuzzy_ruang_tamu);
}

int readMagneticSensor_ruang_tamu() {
  return digitalRead(MAGNETIC_PIN_RUANG_TAMU);
}

// --- DITAMBAHKAN: Fungsi untuk mengontrol mode kipas ruang tamu ---
void setFanOverride_ruang_tamu(bool isManual) {
  manualFanOverride_ruang_tamu = isManual;
  Serial.printf("[Ruang Tamu] Mode kipas diubah ke: %s\n", isManual ? "MANUAL" : "OTOMATIS");
}

void updateDoorStatus_ruang_tamu() {
  int previousValue = lastMagneticValue_ruang_tamu;
  lastMagneticValue_ruang_tamu = readMagneticSensor_ruang_tamu();
  lastDoorStatus_ruang_tamu = (lastMagneticValue_ruang_tamu == HIGH) ? "OPEN" : "CLOSED";
  if (previousValue != lastMagneticValue_ruang_tamu) {
    Serial.print("Status Pintu Ruang Tamu Berubah: ");
    Serial.println(lastDoorStatus_ruang_tamu);
  }
}

void handleBuzzerAlarms_ruang_tamu() {
  bool isDoorOpen = (lastMagneticValue_ruang_tamu == HIGH);
  if (isDoorOpen) {
    Serial.println("!!! Ruang Tamu: PINTU/JENDELA TERBUKA !!!");
    digitalWrite(BUZZER_PIN_RUANG_TAMU, HIGH);
  } else {
    digitalWrite(BUZZER_PIN_RUANG_TAMU, LOW);
  }
}

// --- Fungsi Kontrol Utama (Loop) ---
void loopRuangTamu() {
  float temperature = dht_ruang_tamu.readTemperature();
  float humidity = dht_ruang_tamu.readHumidity();
  lastMagneticValue_ruang_tamu = digitalRead(MAGNETIC_PIN_RUANG_TAMU);
  lastDoorStatus_ruang_tamu = (lastMagneticValue_ruang_tamu == HIGH) ? "OPEN" : "CLOSED";

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("[Ruang Tamu] Gagal membaca dari sensor DHT!");
    return;
  }
  lastTemperature_ruang_tamu = temperature;
  lastHumidity_ruang_tamu = humidity;

  // Kontrol Buzzer
  digitalWrite(BUZZER_PIN_RUANG_TAMU, lastMagneticValue_ruang_tamu == HIGH ? HIGH : LOW);

  int fanSpeedOutput;
  // --- LOGIKA MANUAL OVERRIDE ---
  if (manualFanOverride_ruang_tamu) {
      fanSpeedOutput = 255; // Paksa kecepatan 100%
  } else {
      // Mode Otomatis (Fuzzy)
      fuzzy_ruang_tamu->setInput(1, temperature);
      fuzzy_ruang_tamu->setInput(2, humidity);
      fuzzy_ruang_tamu->fuzzify();
      fanSpeedOutput = fuzzy_ruang_tamu->defuzzify(1);
  }

  ledcWrite(PWM_CHANNEL_RUANG_TAMU, fanSpeedOutput);
  lastFanPWM_ruang_tamu = fanSpeedOutput;

  Serial.printf("[Ruang Tamu] Suhu:%.1fC, Lembab:%.1f%%, Pintu:%s, KipasPWM:%d\n",
    lastTemperature_ruang_tamu, lastHumidity_ruang_tamu, lastDoorStatus_ruang_tamu.c_str(), lastFanPWM_ruang_tamu);

  // --- LOGIKA PENGIRIMAN DATA GENERIK ---
  bool isUrgent = (lastDoorStatus_ruang_tamu == "OPEN");
  if (isUrgent || (millis() - lastSendTime_ruang_tamu >= sendInterval_ruang_tamu)) {
      StaticJsonDocument<256> doc;
      doc["temperature"] = lastTemperature_ruang_tamu;
      doc["humidity"] = lastHumidity_ruang_tamu;
      doc["magnetic_value"] = lastMagneticValue_ruang_tamu;
      doc["fan_pwm"] = lastFanPWM_ruang_tamu;

      // Memanggil fungsi generik dari api_handler.h
      sendDeviceDataToServer("ruang_tamu", doc);
      
      lastSendTime_ruang_tamu = millis();
  }
}
#endif // RUANG_TAMU_CONTROL_H