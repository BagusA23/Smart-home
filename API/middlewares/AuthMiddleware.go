// File: middlewares/AuthMiddleware.go

package middlewares

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

// --- PERBAIKAN 1: SAMAKAN KUNCI DENGAN YANG ADA DI CreateToken.go ---
var jwtSecret = []byte("kunci_rahasia_super_aman_123")

// AuthMiddleware untuk proteksi route
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")

		if authHeader == "" || !strings.HasPrefix(authHeader, "Bearer ") {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header missing or invalid"})
			c.Abort()
			return
		}

		tokenString := strings.TrimPrefix(authHeader, "Bearer ")

		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, jwt.ErrSignatureInvalid
			}
			return jwtSecret, nil
		})

		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid or expired token"})
			c.Abort()
			return
		}

		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token claims"})
			c.Abort()
			return
		}

		// --- PERBAIKAN 2: AMBIL 'user_id' DAN 'role', LALU SET KE CONTEXT ---
		userID, userOK := claims["user_id"].(float64)
		userRole, roleOK := claims["role"].(string)

		if !userOK || !roleOK {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token data"})
			c.Abort()
			return
		}
		
		c.Set("user_id", uint(userID))
		c.Set("role", userRole)

		c.Next()
	}
}