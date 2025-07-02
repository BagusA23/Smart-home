package main

import (
	"api/config"
	"api/routes"
	"log"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func main() {
	// Hubungkan ke database menggunakan GORM
	database, err := config.ConnectDB()
	if err != nil {
		log.Fatal("Gagal terhubung ke database: ", err.Error())
	}

	// Ambil koneksi sql.DB dari GORM untuk manajemen koneksi
	sqlDB, err := database.DB()
	if err != nil {
		log.Fatal("Gagal mendapatkan sql.DB: ", err.Error())
	}
	defer sqlDB.Close()

	// Buat instance router Gin
	router := gin.Default()

	// Setup middleware CORS
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"}, // Gunakan domain spesifik di production
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
	}))

	// Middleware untuk logging dan recovery
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Endpoint untuk health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "ok",
			"message": "Smart Home API is running",
		})
	})

	// === Memuat Semua Rute Aplikasi ===
	// Cukup panggil satu fungsi ini untuk mendaftarkan semua rute
	// (publik dan terproteksi).
	routes.SetupRoutes(router, database)

	// Mulai server
	log.Println("🚀 Memulai server pada port 8080...")
	if err := router.Run("0.0.0.0:8080"); err != nil {
		log.Fatal("❌ Gagal memulai server: ", err.Error())
	}
}
