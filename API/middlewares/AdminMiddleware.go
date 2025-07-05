package middlewares

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// AdminAuthMiddleware memeriksa apakah pengguna yang login memiliki role 'admin'.
// Middleware ini harus dijalankan SETELAH AuthMiddleware.
func AdminAuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Ambil role dari context, yang seharusnya sudah di-set oleh AuthMiddleware
		userRole, exists := c.Get("role")

		if !exists {
			c.JSON(http.StatusForbidden, gin.H{"error": "Forbidden: Role information not found"})
			c.Abort()
			return
		}

		// Cek apakah rolenya adalah 'admin'
		if userRole.(string) != "admin" {
			c.JSON(http.StatusForbidden, gin.H{"error": "Forbidden: Administrator access required"})
			c.Abort()
			return
		}

		// Jika role adalah 'admin', lanjutkan ke handler berikutnya
		c.Next()
	}
}
