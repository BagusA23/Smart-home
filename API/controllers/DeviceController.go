package controllers

import (
	"api/models"
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

// ... (Konstanta dan struct lain tidak berubah) ...

const (
	telegramBotToken = "7636954400:AAG5gUN5LE5i5k6YlNQtCaYTRsDLGr52apY"
	telegramChatID   = "6161774045"
)

type DeviceController struct {
	DB *gorm.DB
}

type FanOverrideInput struct {
	Override bool `json:"override"`
}

func NewDeviceController(db *gorm.DB) *DeviceController {
	db.AutoMigrate(&models.DeviceReading{}, &models.Device{})
	return &DeviceController{DB: db}
}

func determineFanStatus(pwm int) string {
	if pwm == 0 {
		return "Mati"
	} else if pwm > 0 && pwm <= 130 {
		return "Pelan"
	} else if pwm > 130 && pwm <= 190 {
		return "Sedang"
	} else {
		return "Cepat"
	}
}

// CreateDeviceReading sekarang menangani logika untuk PIR
func (ctrl *DeviceController) CreateDeviceReading(c *gin.Context) {
	deviceID := c.Param("deviceID")
	if deviceID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Device ID tidak boleh kosong"})
		return
	}

	var reading models.DeviceReading
	if err := c.ShouldBindJSON(&reading); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Input tidak valid: " + err.Error()})
		return
	}

	reading.DeviceID = deviceID

	// Tentukan status pintu dari nilai magnetik
	if reading.MagneticValue == 0 {
		reading.DoorStatus = "CLOSED"
	} else {
		reading.DoorStatus = "OPEN"
	}

	// DITAMBAHKAN: Logika baru untuk menentukan status gerakan dari nilai PIR
	// Logika ini hanya berjalan jika perangkat mengirimkan 'pir_value'.
	if reading.PirValue != nil {
		var motionStatus string
		if *reading.PirValue == 1 { // Asumsi nilai 1 berarti ada gerakan
			motionStatus = "MOTION_DETECTED"
		} else {
			motionStatus = "NO_MOTION"
		}
		reading.MotionStatus = &motionStatus // Simpan status sebagai pointer string
	}

	// Tentukan status kipas dari nilai PWM
	reading.FanStatus = determineFanStatus(reading.FanPWM)

	// Simpan semua data ke database
	if err := ctrl.DB.Create(&reading).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal menyimpan data: " + err.Error()})
		return
	}

	go ctrl.handleNotifications(reading)

	c.JSON(http.StatusCreated, gin.H{
		"message": fmt.Sprintf("Data untuk perangkat '%s' berhasil disimpan", deviceID),
		"data":    reading,
	})
}

// ... (Sisa controller tidak perlu diubah) ...
// handleNotifications, GetReadingsByDevice, dll. tetap sama

func (ctrl *DeviceController) handleNotifications(reading models.DeviceReading) {
	var emergencyMessage string
	isDoorAlert := false

	switch reading.DeviceID {
	case "dapur":
		if reading.FlameValue != nil && *reading.FlameValue == 0 {
			emergencyMessage = "🚨🔥 *PERINGATAN KEBAKARAN DI DAPUR!* 🔥🚨"
		} else if reading.GasValue != nil && *reading.GasValue == 1 {
			emergencyMessage = "⚠️💨 *GAS BERBAHAYA TERDETEKSI DI DAPUR!* 💨⚠️"
		} else if reading.DoorStatus == "OPEN" {
			emergencyMessage = "🚪❗️ *PINTU DAPUR TERBUKA!* ❗️🚪"
			isDoorAlert = true
		} else if reading.MotionStatus != nil && *reading.MotionStatus == "MOTION_DETECTED" {
			emergencyMessage = "👀❗️ *GERAKAN TERDETEKSI DI DAPUR!* ❗️👀"
		}

	case "ruang_tamu":
		if reading.DoorStatus == "OPEN" {
			emergencyMessage = "🚪❗️ *PINTU RUANG TAMU TERBUKA!* ❗️🚪"
			isDoorAlert = true
		} else if reading.MotionStatus != nil && *reading.MotionStatus == "MOTION_DETECTED" {
			emergencyMessage = "👀❗️ *GERAKAN TERDETEKSI DI RUANG TAMU!* ❗️👀"
		}

	case "kamar":
		if reading.DoorStatus == "OPEN" {
			emergencyMessage = "🚪❗️ *PINTU KAMAR TERBUKA!* ❗️🚪"
			isDoorAlert = true
		}

	default:
		log.Printf("Menerima data dari perangkat tidak dikenal '%s', tidak ada notifikasi dikirim.", reading.DeviceID)
	}

	if emergencyMessage != "" {
		if isDoorAlert {
			log.Printf("Delay 5 detik sebelum kirim notifikasi pintu terbuka untuk %s...", reading.DeviceID)
			time.Sleep(5 * time.Second)
		}
		log.Printf("Mengirim notifikasi darurat untuk %s: %s", reading.DeviceID, emergencyMessage)
		sendTelegramNotification(emergencyMessage)
	}
}

func (ctrl *DeviceController) GetReadingsByDevice(c *gin.Context) {
	deviceID := c.Param("deviceID")
	limitStr := c.DefaultQuery("limit", "20")
	limit, _ := strconv.Atoi(limitStr)

	var readings []models.DeviceReading
	result := ctrl.DB.Where("device_id = ?", deviceID).Order("created_at desc").Limit(limit).Find(&readings)

	if result.Error != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal mengambil data perangkat"})
		return
	}

	if len(readings) == 0 {
		c.JSON(http.StatusNotFound, gin.H{"message": "Tidak ada data ditemukan untuk perangkat " + deviceID})
		return
	}

	c.JSON(http.StatusOK, readings)
}

func (ctrl *DeviceController) SetFanOverride(c *gin.Context) {
	deviceID := c.Param("deviceID")
	var input FanOverrideInput
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Input tidak valid"})
		return
	}
	var device models.Device
	if err := ctrl.DB.Where("device_id = ?", deviceID).First(&device).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			device = models.Device{DeviceID: deviceID, Name: deviceID, IsFanOverrideActive: input.Override}
			if err := ctrl.DB.Create(&device).Error; err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal membuat perangkat baru"})
				return
			}
		} else {
			c.JSON(http.StatusNotFound, gin.H{"error": "Perangkat tidak ditemukan"})
			return
		}
	} else {
		device.IsFanOverrideActive = input.Override
		if err := ctrl.DB.Save(&device).Error; err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal update status perangkat"})
			return
		}
	}

	log.Printf("Perintah override untuk '%s' diubah menjadi %v.", deviceID, input.Override)
	c.JSON(http.StatusOK, gin.H{
		"message":                "Mode kipas berhasil diubah",
		"device_id":              deviceID,
		"is_fan_override_active": device.IsFanOverrideActive,
	})
}

func (ctrl *DeviceController) GetDeviceStatus(c *gin.Context) {
	deviceID := c.Param("deviceID")

	var device models.Device
	if err := ctrl.DB.Where("device_id = ?", deviceID).First(&device).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusOK, gin.H{
				"device_id":              deviceID,
				"is_fan_override_active": false,
			})
			return
		}
		c.JSON(http.StatusNotFound, gin.H{"error": "Perangkat tidak ditemukan"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"device_id":              deviceID,
		"is_fan_override_active": device.IsFanOverrideActive,
	})
}

func sendTelegramNotification(message string) {
	if telegramBotToken == "" || telegramChatID == "" {
		log.Println("Peringatan: Token atau Chat ID Telegram belum diatur. Notifikasi dibatalkan.")
		return
	}
	apiURL := fmt.Sprintf("https://api.telegram.org/bot%s/sendMessage", telegramBotToken)
	payload := map[string]string{
		"chat_id":    telegramChatID,
		"text":       message,
		"parse_mode": "HTML", // ← ganti ini dari MarkdownV2 jadi HTML
	}
	jsonPayload, _ := json.Marshal(payload)
	resp, err := http.Post(apiURL, "application/json", bytes.NewBuffer(jsonPayload))
	if err != nil {
		log.Printf("Gagal mengirim request ke Telegram: %v", err)
		return
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		log.Printf("Telegram API merespons dengan status error: %s", resp.Status)
	} else {
		log.Println("Notifikasi darurat BERHASIL dikirim ke Telegram.")
	}
}

