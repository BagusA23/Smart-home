#ifndef PINTU_H
#define PINTU_H

#include <Arduino.h>

// ===================================================================
//              KONFIGURASI PIN PINTU (Ubah di sini)
// ===================================================================
// Catatan: Buzzer bisa jadi digunakan bersama oleh sistem dapur dan pintu.
// Pastikan tidak ada konflik pin.
#define PIN_BUZZER_ALARM 26

// Masukkan semua pin sensor magnetik pintu/jendela di sini
const int PINS_SENSOR_PINTU[] = {12, 25, 32}; // Contoh: pin D12, D25, D32

// ===================================================================
//     KODE PUSTAKA (Tidak perlu diubah)
// ===================================================================

const int JUMLAH_SENSOR_PINTU = sizeof(PINS_SENSOR_PINTU) / sizeof(PINS_SENSOR_PINTU[0]);

/**
 * @brief Menginisialisasi pin untuk sensor pintu dan buzzer.
 */
inline void setupPintu() {
  pinMode(PIN_BUZZER_ALARM, OUTPUT);
  digitalWrite(PIN_BUZZER_ALARM, LOW); // Pastikan buzzer mati saat mulai
  
  for (int i = 0; i < JUMLAH_SENSOR_PINTU; i++) {
    pinMode(PINS_SENSOR_PINTU[i], INPUT_PULLUP);
  }
}

/**
 * @brief Memeriksa status sensor pintu dan mengontrol buzzer.
 * Versi ini memperbaiki logika buzzer dan pesan serial.
 */
inline void loopPintu() {
  // Variabel statis untuk menyimpan status buzzer terakhir
  static bool buzzerSedangAktif = false;
  bool alarmHarusAktif = false;

  // Periksa setiap sensor pintu
  for (int i = 0; i < JUMLAH_SENSOR_PINTU; i++) {
    // Dengan INPUT_PULLUP, HIGH berarti sirkuit terbuka (pintu/jendela DIBUKA)
    if (digitalRead(PINS_SENSOR_PINTU[i]) == HIGH) {
      alarmHarusAktif = true;
      break; 
    }
  }

  // Logika untuk mengontrol buzzer dan hanya print saat ada perubahan
  if (alarmHarusAktif && !buzzerSedangAktif) {
    // Kondisi baru: Alarm harus aktif, tapi sebelumnya tidak.
    // === KESALAHAN 1 DIPERBAIKI ===
    // Untuk menyalakan buzzer, kita kirim sinyal HIGH.
    digitalWrite(PIN_BUZZER_ALARM, HIGH); 
    buzzerSedangAktif = true;

    // === KESALAHAN 2 DIPERBAIKI ===
    // Pesan disesuaikan dengan logika: HIGH = Pintu Terbuka
    Serial.println("!!! PERINGATAN: Pintu/Jendela Terbuka -> Alarm AKTIF!");

  } else if (!alarmHarusAktif && buzzerSedangAktif) {
    // Kondisi baru: Alarm harus mati, tapi sebelumnya aktif.
    // Untuk mematikan buzzer, kita kirim sinyal LOW.
    digitalWrite(PIN_BUZZER_ALARM, LOW);
    buzzerSedangAktif = false;
    
    // Pesan disesuaikan dengan logika: semua sensor tidak HIGH (artinya LOW) = Pintu Tertutup
    Serial.println("INFO: Semua Pintu/Jendela Tertutup -> Alarm MATI.");
  }
}

#endif // PINTU_H