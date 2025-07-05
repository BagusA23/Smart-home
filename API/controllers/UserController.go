package controllers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"

	"api/models"
)

// hashPassword hashes a plain password
func hashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	return string(bytes), err
}

// checkPasswordHash checks a password against a hash
func checkPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}

// RegisterUser handles user registration
func RegisterUser(db *gorm.DB) gin.HandlerFunc {
	return func(ctx *gin.Context) {
		db.AutoMigrate(&models.User{})

		// --- PERBAIKAN DI SINI ---
		// Tambahkan Email ke struct input dan berikan validasi
		var input struct {
			Username string `json:"username" binding:"required"`
			Email    string `json:"email" binding:"required,email"` // Wajib diisi dan harus berformat email
			Password string `json:"password" binding:"required"`
		}

		// Jika input tidak valid (misal: email kosong atau format salah),
		// Gin akan otomatis mengembalikan error 400 Bad Request.
		if err := ctx.ShouldBindJSON(&input); err != nil {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input: " + err.Error()})
			return
		}

		// Cek apakah username atau email sudah ada
		var existingUser models.User
		if err := db.Where("username = ? OR email = ?", input.Username, input.Email).First(&existingUser).Error; err == nil {
			if existingUser.Username == input.Username {
				ctx.JSON(http.StatusBadRequest, gin.H{"error": "Username already exists"})
			} else {
				ctx.JSON(http.StatusBadRequest, gin.H{"error": "Email already exists"})
			}
			return
		}

		// Hash password
		hashedPassword, err := hashPassword(input.Password)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
			return
		}

		// Buat user baru dengan menyertakan email
		newUser := models.User{
			Username: input.Username,
			Email:    input.Email, // --- SERTAKAN EMAIL ---
			Password: hashedPassword,
		}

		if err := db.Create(&newUser).Error; err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to register user"})
			return
		}

		ctx.JSON(http.StatusCreated, gin.H{
			"message": "User registered successfully",
			"user": gin.H{
				"id":       newUser.ID,
				"username": newUser.Username,
				"email":    newUser.Email,
			},
		})
	}

}

// LoginUser handles user login and returns a JWT token
// LoginUser handles user login and returns a JWT token
func LoginUser(db *gorm.DB) gin.HandlerFunc {
	return func(ctx *gin.Context) {
		var input struct {
			Username string `json:"username" binding:"required"`
			Password string `json:"password" binding:"required"`
		}

		if err := ctx.ShouldBindJSON(&input); err != nil {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
			return
		}

		var user models.User
		if err := db.Where("username = ?", input.Username).First(&user).Error; err != nil {
			ctx.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
			return
		}

		if !checkPasswordHash(input.Password, user.Password) {
			ctx.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
			return
		}

		// --- PERBAIKAN: Gunakan user.Role, bukan user.Username ---
		token, err := CreateToken(user.ID, user.Role)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
			return
		}

		ctx.JSON(http.StatusOK, gin.H{
			"message": "Login successful",
			"token":   token,
		})
	}
}
// --- FUNGSI BARU: UpdatePassword ---
// UpdatePassword menangani perubahan password untuk pengguna yang sedang login.
func UpdatePassword(db *gorm.DB) gin.HandlerFunc {
	return func(ctx *gin.Context) {
		// Ambil user_id dari konteks yang sudah divalidasi oleh AuthMiddleware
		userID, exists := ctx.Get("user_id")
		if !exists {
			ctx.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized: user ID not found in token"})
			return
		}

		// Definisikan struct untuk input JSON
		var input struct {
			OldPassword string `json:"old_password" binding:"required"`
			NewPassword string `json:"new_password" binding:"required"`
		}

		// Bind JSON ke struct
		if err := ctx.ShouldBindJSON(&input); err != nil {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input: " + err.Error()})
			return
		}

		// Cari pengguna di database berdasarkan ID dari token
		var user models.User
		if err := db.First(&user, userID).Error; err != nil {
			ctx.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
			return
		}

		// Verifikasi password lama
		if !checkPasswordHash(input.OldPassword, user.Password) {
			ctx.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid old password"})
			return
		}

		// Hash password baru
		newHashedPassword, err := hashPassword(input.NewPassword)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash new password"})
			return
		}

		// Update password di database
		if err := db.Model(&user).Update("password", newHashedPassword).Error; err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update password"})
			return
		}

		ctx.JSON(http.StatusOK, gin.H{"message": "Password updated successfully"})
	}
}

// --- FUNGSI BARU: SetUserRole ---
// SetUserRole mengubah role seorang pengguna. Hanya bisa diakses oleh admin.
func SetUserRole(db *gorm.DB) gin.HandlerFunc {
	return func(ctx *gin.Context) {
		// Ambil ID user yang akan diubah dari parameter URL
		targetUserID, err := strconv.ParseUint(ctx.Param("id"), 10, 32)
		if err != nil {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid user ID"})
			return
		}

		var input struct {
			Role string `json:"role" binding:"required"`
		}

		if err := ctx.ShouldBindJSON(&input); err != nil {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input: role is required"})
			return
		}

		// Validasi role yang diizinkan
		if input.Role != "user" && input.Role != "admin" {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid role: must be 'user' or 'admin'"})
			return
		}

		// Cari pengguna yang akan diubah
		var targetUser models.User
		if err := db.First(&targetUser, targetUserID).Error; err != nil {
			ctx.JSON(http.StatusNotFound, gin.H{"error": "Target user not found"})
			return
		}

		// Update role
		db.Model(&targetUser).Update("role", input.Role)

		ctx.JSON(http.StatusOK, gin.H{
			"message":  "User role updated successfully",
			"user_id":  targetUser.ID,
			"new_role": input.Role,
		})
	}
}


// --- FUNGSI BARU: GetAllUsers ---
// GetAllUsers mengambil daftar semua pengguna di sistem. Hanya untuk admin.
func GetAllUsers(db *gorm.DB) gin.HandlerFunc {
	return func(ctx *gin.Context) {
		var users []models.User
		// Mengambil semua user dan mengurutkannya berdasarkan ID
		if err := db.Order("id asc").Find(&users).Error; err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve users"})
			return
		}

		ctx.JSON(http.StatusOK, users)
	}
}

// --- FUNGSI BARU: DeleteUser ---
// DeleteUser menghapus seorang pengguna berdasarkan ID. Hanya untuk admin.
func DeleteUser(db *gorm.DB) gin.HandlerFunc {
	return func(ctx *gin.Context) {
		// Ambil ID dari pengguna yang login (admin)
		adminID, _ := ctx.Get("user_id")

		// Ambil ID dari pengguna yang akan dihapus dari URL
		targetUserID, err := strconv.ParseUint(ctx.Param("id"), 10, 32)
		if err != nil {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid user ID"})
			return
		}

		// --- PENTING: Mencegah admin menghapus dirinya sendiri ---
		if adminID.(uint) == uint(targetUserID) {
			ctx.JSON(http.StatusForbidden, gin.H{"error": "Administrator cannot delete their own account"})
			return
		}

		// Hapus pengguna dari database
		result := db.Delete(&models.User{}, targetUserID)
		if result.Error != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete user"})
			return
		}

		// Cek apakah ada baris yang terpengaruh (apakah user ada)
		if result.RowsAffected == 0 {
			ctx.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
			return
		}

		ctx.JSON(http.StatusOK, gin.H{"message": "User deleted successfully"})
	}
}