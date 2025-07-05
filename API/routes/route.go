// File: routes/route.go

package routes

import (
	"api/controllers"
	middlewares "api/middlewares"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

func SetupRoutes(router *gin.Engine, db *gorm.DB) {
	deviceController := controllers.NewDeviceController(db)
	ledController := controllers.NewLedController(db)
	
	// --- RUTE PUBLIK ---
	router.POST("/register", controllers.RegisterUser(db))
	router.POST("/login", controllers.LoginUser(db))
	router.POST("/sensors/data/:deviceID", deviceController.CreateDeviceReading)
	router.GET("/devices/:deviceID/status", deviceController.GetDeviceStatus)
	router.GET("/leds/states", ledController.GetAllLedStates)

	// --- RUTE TERLINDUNGI ---
	api := router.Group("/api")
	api.Use(middlewares.AuthMiddleware())
	{
		api.GET("/devices/:deviceID", deviceController.GetReadingsByDevice)
		api.POST("/leds/:pin/state", ledController.SetLedState)
		api.POST("/devices/:deviceID/fan-override", deviceController.SetFanOverride)

		// --- RUTE BARU UNTUK UPDATE PASSWORD ---
		// Metode PUT lebih cocok untuk operasi update
		api.PUT("/user/password", controllers.UpdatePassword(db))

		// ... rute terproteksi lainnya ...

		// --- RUTE BARU UNTUK MANAJEMEN ROLE ---
		// Hanya admin yang bisa mengakses endpoint ini
		adminRoutes := api.Group("/admin")
		adminRoutes.Use(middlewares.AdminAuthMiddleware()) // Middleware kedua khusus admin
		{
			// Contoh: PUT /api/admin/users/123/role
			// Body: {"role": "admin"}
			adminRoutes.PUT("/users/:id/role", controllers.SetUserRole(db))
			adminRoutes.GET("/users", controllers.GetAllUsers(db))
			adminRoutes.DELETE("/users/:id", controllers.DeleteUser(db))
			// Rute untuk update role yang sudah ada
		}
	}
}	