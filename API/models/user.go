// File: models/User.go

package models

import (
	"time"
)

type User struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	Username  string    `gorm:"size:100;uniqueIndex:idx_users_username" json:"username"`
	Email     string    `gorm:"size:100;uniqueIndex:idx_users_email" json:"email"`
	Password  string    `gorm:"type:text" json:"-"` // Jangan kirim password ke JSON response
	Role      string    `gorm:"size:50;default:'user'" json:"role"` // --- FIELD BARU ---
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}