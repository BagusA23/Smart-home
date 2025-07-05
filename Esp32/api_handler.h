#ifndef API_HANDLER_H
#define API_HANDLER_H

#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WiFi.h>

// =================================================================
//          --- FORWARD DECLARATIONS (INI PERBAIKANNYA) ---
// Memberitahu file ini bahwa fungsi-fungsi berikut ada di file lain.
// Ini untuk mengatasi error 'was not declared in this scope'.
// =================================================================
void setFanOverride_dapur(bool isManual);
void setFanOverride_kamar(bool isManual);
void setFanOverride_ruang_tamu(bool isManual);


// --- Konfigurasi URL Server ---
const char* serverBaseUrl = "http://192.168.250.208:8080";

/** 
 * @brief Mengirim data dari perangkat manapun ke server menggunakan endpoint generik.
 */
void sendDeviceDataToServer(const char* deviceID, const JsonDocument& doc) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.printf("[%s] WiFi tidak terhubung, pengiriman data dibatalkan.\n", deviceID);
    return;
  }
  String apiUrl = String(serverBaseUrl) + "/sensors/data/" + String(deviceID);
  HTTPClient http;
  http.begin(apiUrl);
  http.addHeader("Content-Type", "application/json");
  String requestBody;
  serializeJson(doc, requestBody);
  int httpResponseCode = http.POST(requestBody);
  if (httpResponseCode > 0) {
    Serial.printf("[%s] Laporan sensor terkirim, kode: %d\n", deviceID, httpResponseCode);
  } else {
    Serial.printf("[%s] Gagal mengirim laporan sensor, error: %s\n", deviceID, http.errorToString(httpResponseCode).c_str());
  }
  http.end();
}

/**
 * @brief Bertanya ke server mengenai status override kipas dan menyinkronkannya.
 */
void syncFanStatusFromServer(const char* deviceID) {
    if (WiFi.status() != WL_CONNECTED) {
        return; 
    }

    // ==================================================================
    //          --- PERBAIKAN: HAPUS AWALAN "/api" ---
    // URL ini sekarang disesuaikan dengan rute yang terdaftar di GIN
    // ==================================================================
    String statusUrl = String(serverBaseUrl) + "/devices/" + String(deviceID) + "/status";

    HTTPClient http;
    http.begin(statusUrl);
    http.setTimeout(3000);

    int httpCode = http.GET();

    if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        StaticJsonDocument<128> doc;
        DeserializationError error = deserializeJson(doc, payload);

        if (error) {
            Serial.printf("[%s] Gagal parsing JSON status: %s\n", deviceID, error.c_str());
            http.end();
            return;
        }

        bool isOverrideActive = doc["is_fan_override_active"];

        // Memanggil fungsi yang sudah di-deklarasikan di atas
        if (strcmp(deviceID, "dapur") == 0) {
            setFanOverride_dapur(isOverrideActive);
        } else if (strcmp(deviceID, "kamar") == 0) {
            setFanOverride_kamar(isOverrideActive);
        } else if (strcmp(deviceID, "ruang_tamu") == 0) {
            setFanOverride_ruang_tamu(isOverrideActive);
        }

    }
    http.end();
}

#endif // API_HANDLER_H
