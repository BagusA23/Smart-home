#ifndef LED_CONTROL_H
#define LED_CONTROL_H

#include <Arduino.h>
#include <ArduinoJson.h>
#include "api_handler.h" // Asumsi api_handler.h sudah ada

// =================================================================
//          --- KONFIGURASI UNTUK 3 LED ---
// Tambahkan pin LED Anda di sini.
// =================================================================
const int ledPins[] = {26,5, 13}; // Contoh: LED 1 di pin 5, LED 2 di pin 13, LED 3 di pin 14
const int numLeds = sizeof(ledPins) / sizeof(ledPins[0]);

// Variabel untuk mengelola kedipan non-blocking untuk setiap LED
unsigned long previousBlinkMillis[numLeds] = {0};
bool isBlinkingEnabled[numLeds] = {false};
const long ledBlinkInterval = 500;

/**
 * @brief Menginisialisasi semua pin LED yang terdaftar.
 */
void setupLeds() {
    for (int i = 0; i < numLeds; i++) {
        pinMode(ledPins[i], OUTPUT);
        digitalWrite(ledPins[i], LOW); // Matikan semua LED saat startup
        isBlinkingEnabled[i] = false;
    }
    Serial.println("Sistem multi-LED siap.");
}

/**
 * @brief Menjalankan logika kedip untuk semua LED.
 * Panggil fungsi ini di dalam loop() utama.
 */
void runAllLedBlinks() {
    unsigned long currentMillis = millis();
    for (int i = 0; i < numLeds; i++) {
        if (isBlinkingEnabled[i]) {
            if (currentMillis - previousBlinkMillis[i] >= ledBlinkInterval) {
                previousBlinkMillis[i] = currentMillis;
                digitalWrite(ledPins[i], !digitalRead(ledPins[i]));
            }
        }
    }
}

/**
 * @brief Mengambil status SEMUA LED dari server dan menyesuaikannya.
 * Ini adalah fungsi kontrol utama yang baru.
 */
void syncAllLedStates() {
    if (WiFi.status() != WL_CONNECTED) return;

    // Panggil API baru: GET /api/leds/states
    String url = String(serverBaseUrl) + "/leds/states";
    HTTPClient http;
    http.begin(url);
    int httpCode = http.GET();

    if (httpCode != HTTP_CODE_OK) {
        http.end();
        return;
    }

    String payload = http.getString();
    http.end();

    // Ukuran JSON disesuaikan untuk menampung data beberapa LED
    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, payload);
    if (error) {
        Serial.println("Gagal parsing JSON status LED.");
        return;
    }

    JsonArray array = doc.as<JsonArray>();
    if(array.isNull()){
        return;
    }

    // Loop melalui setiap objek JSON di dalam array
    for (JsonObject ledState : array) {
        int pin = ledState["pin"];
        const char* state = ledState["state"];

        // Cari pin ini di dalam array ledPins kita
        for (int i = 0; i < numLeds; i++) {
            if (ledPins[i] == pin) {
                // Pin ditemukan, set statusnya
                if (strcmp(state, "ON") == 0) {
                    isBlinkingEnabled[i] = false;
                    digitalWrite(pin, HIGH);
                } else if (strcmp(state, "OFF") == 0) {
                    isBlinkingEnabled[i] = false;
                    digitalWrite(pin, LOW);
                } else if (strcmp(state, "BLINKING") == 0) {
                    isBlinkingEnabled[i] = true;
                }
                break; // Keluar dari loop pencarian
            }
        }
    }
}

#endif // LED_CONTROL_H
