package controllers

import (
	"api/models"
	"log"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type LedController struct {
	DB *gorm.DB
}

// NewLedController membuat instance baru dan melakukan migrasi DB
func NewLedController(db *gorm.DB) *LedController {
	db.AutoMigrate(&models.LedState{}, &models.LedStatusLog{})
	return &LedController{DB: db}
}

// --- Tipe Data untuk Input ---
type SetLedStateInput struct {
	State string `json:"state" binding:"required,oneof=ON OFF BLINKING"`
}

// ========================================================
//          --- HANDLER BARU UNTUK KONTROL LED ---
// ========================================================

// SetLedState mengontrol status sebuah LED berdasarkan pin-nya.
// Ini adalah endpoint yang akan Anda panggil dari Postman atau frontend.
func (ctrl *LedController) SetLedState(c *gin.Context) {
	pinStr := c.Param("pin")
	pin, err := strconv.Atoi(pinStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Pin tidak valid"})
		return
	}

	var input SetLedStateInput
	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Input tidak valid: " + err.Error()})
		return
	}

	// Buat atau Update state LED di tabel 'led_states'
	ledState := models.LedState{
		Pin:   pin,
		State: input.State,
	}
	// `Save` akan melakukan UPDATE jika data dengan primary key (pin) sudah ada,
	// atau INSERT jika belum ada.
	if err := ctrl.DB.Save(&ledState).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal menyimpan state LED"})
		return
	}

	// (Opsional) Buat juga log riwayat perubahannya
	go func() {
		// PERBAIKAN: Ganti nama variabel 'log' menjadi 'statusLog' untuk menghindari shadowing.
		statusLog := models.LedStatusLog{Pin: pin, State: input.State}
		ctrl.DB.Create(&statusLog)
		// Sekarang 'log.Printf' akan merujuk ke package 'log' yang benar.
		log.Printf("LED state for pin %d changed to %s. Log created.", pin, input.State)
	}()


	c.JSON(http.StatusOK, ledState)
}


// GetAllLedStates mengembalikan kondisi terakhir dari SEMUA LED yang terdaftar.
// Ini adalah endpoint yang akan dipanggil oleh ESP32 untuk sinkronisasi.
func (ctrl *LedController) GetAllLedStates(c *gin.Context) {
	var states []models.LedState
	if err := ctrl.DB.Find(&states).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal mengambil data state LED"})
		return
	}
	c.JSON(http.StatusOK, states)
}
