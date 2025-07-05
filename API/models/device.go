package models

import (
	"time"

	"gorm.io/gorm"
)

// =================================================================================
// Model untuk Konfigurasi & State Perangkat
// =================================================================================
type Device struct {
	ID uint `gorm:"primaryKey" json:"id"`

	// DIUBAH: Tag 'uniqueIndex' diganti dengan 'unique' untuk stabilitas migrasi GORM.
	// Perubahan ini membantu GORM mengenali constraint yang ada tanpa menyebabkan error.
	DeviceID string `gorm:"column:device_id;type:varchar(50);not null;unique" json:"device_id"`

	Name                string     `gorm:"column:name;type:varchar(100)" json:"name"`
	IsFanOverrideActive bool       `gorm:"column:is_fan_override_active;default:false" json:"is_fan_override_active"`
	LastTemperature     *float64   `gorm:"column:last_temperature" json:"last_temperature"`
	LastHumidity        *float64   `gorm:"column:last_humidity" json:"last_humidity"`
	LastDoorStatus      *string    `gorm:"column:last_door_status" json:"last_door_status"`
	LastSeen            *time.Time `gorm:"column:last_seen" json:"last_seen"`
	CreatedAt           time.Time  `json:"created_at"`
	UpdatedAt           time.Time  `json:"updated_at"`
}

// TableName secara eksplisit memberi tahu GORM nama tabel yang harus digunakan.
func (Device) TableName() string {
	return "devices"
}

// =================================================================================
// Model untuk Riwayat Data Sensor
// =================================================================================
// Struct ini sudah benar dan tidak memerlukan perubahan.
type DeviceReading struct {
	ID uint `gorm:"primaryKey" json:"id"`

	DeviceID string `gorm:"column:device_id;type:varchar(50);not null;index" json:"device_id"`

	// --- Field Umum (ada di semua ruangan) ---
	Temperature   float64 `gorm:"column:temperature" json:"temperature"`
	Humidity      float64 `gorm:"column:humidity" json:"humidity"`
	MagneticValue int     `gorm:"column:magnetic_value" json:"magnetic_value"`
	DoorStatus    string  `gorm:"column:door_status;type:varchar(10)" json:"door_status"`
	FanPWM        int     `gorm:"column:fan_pwm" json:"fan_pwm"`
	FanStatus     string  `gorm:"column:fan_status;type:varchar(15)" json:"fan_status"`

	// --- Field Spesifik (hanya ada di beberapa ruangan, dibuat nullable) ---
	GasValue   *int    `gorm:"column:gas_value" json:"gas_value,omitempty"`
	FlameValue *int    `gorm:"column:flame_value" json:"flame_value,omitempty"`
	FireStatus *string `gorm:"column:fire_status;type:varchar(20)" json:"fire_status,omitempty"`

	// Field baru untuk sensor gerak (PIR)
	PirValue     *int    `gorm:"column:pir_value" json:"pir_value,omitempty"`
	MotionStatus *string `gorm:"column:motion_status;type:varchar(20)" json:"motion_status,omitempty"`

	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

// TableName secara eksplisit memberi tahu GORM nama tabel yang harus digunakan.
func (DeviceReading) TableName() string {
	return "device_readings"
}
