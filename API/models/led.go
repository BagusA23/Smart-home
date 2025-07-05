package models

import (
	"time"
	"gorm.io/gorm"
)

// =================================================================
//          --- MODEL BARU UNTUK KONDISI LED ---
// Model ini akan menyimpan kondisi TERAKHIR dari setiap LED.
// Akan ada satu baris untuk setiap LED yang Anda daftarkan.
// =================================================================
type LedState struct {
	// Pin adalah nomor pin GPIO, kita jadikan Primary Key karena unik.
	Pin       int       `gorm:"primaryKey" json:"pin"`
	// Name adalah nama yang mudah dibaca, untuk ditampilkan di UI.
	Name      string    `gorm:"type:varchar(100)" json:"name"`
	// State adalah kondisi terakhir yang diinginkan ("ON", "OFF", "BLINKING").
	State     string    `gorm:"type:varchar(10);not null;default:'OFF'" json:"state"`
	UpdatedAt time.Time `json:"updated_at"`
}

func (LedState) TableName() string {
	return "led_states"
}


// =================================================================
//        --- MODEL LAMA UNTUK LOG/RIWAYAT (TETAP ADA) ---
// Model ini tetap berguna untuk mencatat setiap perubahan yang terjadi.
// =================================================================
type LedStatusLog struct {
	ID        uint           `gorm:"primaryKey" json:"id"`
	Pin       int            `gorm:"not null;index" json:"pin"`
	State     string         `gorm:"type:varchar(10);not null" json:"state"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

func (LedStatusLog) TableName() string {
	return "led_status_logs"
}
