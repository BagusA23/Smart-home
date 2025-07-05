package config

import (
	"api/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB // Public variable agar bisa digunakan dari luar package

// ConnectDB establishes a connection to the database using the provided DSN.
func ConnectDB() (*gorm.DB, error) {
	dsn := "host=localhost user=postgres password=yourpassword dbname=smart_home_db port=5432 sslmode=disable TimeZone=Asia/Jakarta"

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	// Simpan koneksi global
	DB = db
	// Auto migrate models
	if err := db.AutoMigrate(&models.User{}); err != nil {
		return nil, err
	}


	return db, nil
}
