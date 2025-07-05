#ifndef BUZZER_H
#define BUZZER_H

#include <Arduino.h>

// --- Konfigurasi Pin Buzzer ---
// Ganti angka 25 ini dengan pin GPIO yang Anda gunakan untuk buzzer.
#define BUZZER_PIN 12 

/**
 * @brief Inisialisasi pin buzzer.
 * Panggil fungsi ini sekali di dalam fungsi setup() utama.
 */
void setupBuzzer() {
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW); // Pastikan buzzer mati saat awal
}

/**
 * @brief Memainkan alarm "beep" sebanyak 4 kali.
 * @note Fungsi ini bersifat "blocking", artinya program akan berhenti sejenak
 * selama buzzer berbunyi sebelum melanjutkan ke baris kode berikutnya.
 */
void playBeepAlert() {
  for (int i = 0; i < 4; i++) {
    digitalWrite(BUZZER_PIN, HIGH); // Nyalakan buzzer
    delay(150);                     // Durasi beep
    digitalWrite(BUZZER_PIN, LOW);  // Matikan buzzer
    delay(200);                     // Jeda antar beep
  }
}

#endif // BUZZER_H
