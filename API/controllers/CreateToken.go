// File: controllers/token.go

package controllers

import (
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// Pastikan Anda mengatur JWT_SECRET di environment variable Anda
var jwtSecret = []byte("kunci_rahasia_super_aman_123")

// CreateToken membuat token JWT baru untuk user ID dan role tertentu.
func CreateToken(userID uint, userRole string) (string, error) {
	// Token berlaku selama 24 jam
	expirationTime := time.Now().Add(24 * time.Hour)

	// Membuat claims (data yang disimpan di dalam token)
	claims := &jwt.MapClaims{
		"authorized": true,
		"user_id":    userID,
		"role":       userRole,
		"exp":        expirationTime.Unix(),
	}

	// Membuat token baru dengan claims
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	// Menandatangani token dengan secret key
	return token.SignedString(jwtSecret)
}

// --- KURUNG KURAWAL EKSTRA DIHAPUS DARI SINI ---