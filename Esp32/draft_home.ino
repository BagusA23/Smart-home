// =================================================================
//                 SMART HOME INTEGRATED SYSTEM
//             File Utama (.ino) - Penanggung Jawab Loop
// =================================================================

// --- Pustaka Pihak Ketiga ---
#include <Arduino.h>

// --- Header Konfigurasi & Penyedia Fungsi ---
// Letakkan file yang menyediakan fungsi (seperti wifi dan api) di bagian atas.
#include "wifi_config.h"
#include "api_handler.h"      // Diperbaiki dan menyediakan fungsi untuk file di bawahnya.

// --- Header Modul Ruangan ---
// File-file ini menggunakan fungsi dari api_handler.h
#include "fuzzy_controller.h" // Diperlukan oleh dapur.h
#include "dapur.h"
#include "kamar.h"
#include "ruang_tamu.h"
#include "led.h"

// --- Variabel Global untuk Manajemen Waktu ---
unsigned long previousDapurMillis = 0;
const long dapurInterval = 10000;

unsigned long previousKamarMillis = 0;
const long kamarInterval = 10000;

unsigned long previousRuangTamuMillis = 0;
const long ruangTamuInterval = 10000;

unsigned long previousLedSyncMillis = 0;
const long ledSyncInterval = 10000;

unsigned long previousSyncMillis = 0;
const long syncInterval = 10000; // Tanya ke server setiap 5 detik

// --- Fungsi setup() ---
void setup() {
    Serial.begin(115200);
    while (!Serial);
    Serial.println("Booting up Integrated Smart Home System...");
    
    connectToWiFi();
    
    Serial.println("Initializing Systems...");
    setupDapur();
    setupKamar();
    setupRuangTamu();
    setupLeds();
    Serial.println("Setup Complete. System is running.");
    Serial.println("====================================");
}

// --- Fungsi loop() ---
void loop() {
    unsigned long currentMillis = millis();
    runAllLedBlinks();

    if (currentMillis - previousLedSyncMillis >= ledSyncInterval) { // Buat timer baru
     previousLedSyncMillis = currentMillis;
     syncAllLedStates();
    }

    // Jalankan pengecekan sensor untuk setiap ruangan
    if (currentMillis - previousDapurMillis >= dapurInterval) {
        previousDapurMillis = currentMillis;
        runSystemCheck();
    }
    if (currentMillis - previousKamarMillis >= kamarInterval) {
        previousKamarMillis = currentMillis;
        loopKamar();
    }
    if (currentMillis - previousRuangTamuMillis >= ruangTamuInterval) {
        previousRuangTamuMillis = currentMillis;
        loopRuangTamu();
    }

    // Sinkronisasi Status Kipas dari Server
    if (currentMillis - previousSyncMillis >= syncInterval) {
        previousSyncMillis = currentMillis;
        Serial.println("\n>>> Checking remote fan status from server...");
        
        // Panggil fungsi sinkronisasi untuk setiap ruangan
        syncFanStatusFromServer("dapur");
        delay(100);
        syncFanStatusFromServer("kamar");
        delay(100);
        syncFanStatusFromServer("ruang_tamu");
    }
}