#ifndef KITCHEN_CONTROL_H
#define KITCHEN_CONTROL_H

#include <DHT.h>
#include <Fuzzy.h>
#include "api_handler.h"
#include "fuzzy_controller.h" // Asumsi file ini ada

// --- Definisi Pin & Konfigurasi ---
#define DHTPIN 23
#define DHTTYPE DHT11
#define FAN_PIN 18
#define MQ2_PIN 22
#define FLAME_PIN 21
#define MAGNETIC_PIN 19 // Dihapus
#define BUZZER_PIN 17
#define PWM_CHANNEL 0
#define PWM_FREQ 1000
#define PWM_RESOLUTION 8

DHT dht_dapur(DHTPIN, DHTTYPE);
Fuzzy* fuzzy_dapur = new Fuzzy();

// --- Variabel Global Status Dapur ---
float lastTemperature = 0;
float lastHumidity = 0;
int lastGasValue = 0;
int lastFlameValue = 0;
int lastMagneticValue = 0; // Dihapus
int lastFanPWM = 0;
String lastDoorStatus = "CLOSED"; // Dihapus

// --- Flag untuk Manual Override ---
bool manualFanOverride_dapur = false;

unsigned long lastSendTime = 0;
const unsigned long sendInterval = 60000;

// --- Fungsi Setup ---
void setupDapur() {
  dht_dapur.begin();
  pinMode(MQ2_PIN, INPUT);
  pinMode(FLAME_PIN, INPUT);
  // pinMode(MAGNETIC_PIN, INPUT_PULLUP); // Dihapus
  pinMode(BUZZER_PIN, OUTPUT);
  ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(FAN_PIN, PWM_CHANNEL);
  initializeFuzzySystem(fuzzy_dapur);
  Serial.println("Sistem Dapur Terinisialisasi.");
}

// --- Fungsi untuk mengontrol mode kipas dapur ---
void setFanOverride_dapur(bool isManual) {
  manualFanOverride_dapur = isManual;
  Serial.printf("[Dapur] Mode kipas diubah ke: %s\n", isManual ? "MANUAL" : "OTOMATIS");
}

// --- Fungsi Kontrol Utama (Loop) ---
void runSystemCheck() {
  float suhu = dht_dapur.readTemperature();
  float kelembaban = dht_dapur.readHumidity();
  int gasValue = digitalRead(MQ2_PIN);
  int flameValue = digitalRead(FLAME_PIN);
  lastMagneticValue = digitalRead(MAGNETIC_PIN); // Dihapus
  lastDoorStatus = (lastMagneticValue == HIGH) ? "OPEN" : "CLOSED"; // Dihapus

  if (isnan(suhu) || isnan(kelembaban)) {
    Serial.println("[Dapur] Gagal membaca dari sensor DHT!");
    return;
  }

  lastTemperature = suhu;
  lastHumidity = kelembaban;
  lastGasValue = gasValue;
  lastFlameValue = flameValue;

  // Kontrol Buzzer (logika pintu dihapus)
  if (gasValue == HIGH || flameValue == LOW) {
    digitalWrite(BUZZER_PIN, HIGH);
  } else {
    digitalWrite(BUZZER_PIN, LOW);
  }

  int fanPWM;
  // --- LOGIKA MANUAL OVERRIDE ---
  if (manualFanOverride_dapur) {
    fanPWM = 255; // Paksa kecepatan 100%
  } else {
    // Mode Otomatis (Fuzzy)
    fuzzy_dapur->setInput(1, suhu);
    fuzzy_dapur->setInput(2, kelembaban);
    fuzzy_dapur->setInput(3, gasValue);
    fuzzy_dapur->setInput(4, flameValue);
    fuzzy_dapur->setInput(5, lastMagneticValue); // Dihapus
    fuzzy_dapur->fuzzify();
    fanPWM = fuzzy_dapur->defuzzify(1);
  }
  
  ledcWrite(PWM_CHANNEL, fanPWM);
  lastFanPWM = fanPWM;

  // Cetak status ke Serial Monitor (info pintu dihapus)
  Serial.printf("[Dapur] Suhu:%.1fC, Lembab:%.1f%%, Gas:%d, Api:%d, KipasPWM:%d\n",
    lastTemperature, lastHumidity, lastGasValue, lastFlameValue, lastFanPWM);

  // --- LOGIKA PENGIRIMAN DATA GENERIK ---
  // Kondisi darurat tidak lagi menyertakan status pintu
  bool isUrgent = (gasValue == HIGH || flameValue == LOW);
  if (isUrgent || (millis() - lastSendTime >= sendInterval)) {
    StaticJsonDocument<512> doc;
    doc["temperature"] = lastTemperature;
    doc["humidity"] = lastHumidity;
    doc["magnetic_value"] = lastMagneticValue; // Dihapus
    doc["fan_pwm"] = lastFanPWM;
    doc["gas_value"] = lastGasValue;
    doc["flame_value"] = lastFlameValue;
    
    // Memanggil fungsi generik dari api_handler.h
    sendDeviceDataToServer("dapur", doc);
    
    lastSendTime = millis();
  }
}

#endif // KITCHEN_CONTROL_H