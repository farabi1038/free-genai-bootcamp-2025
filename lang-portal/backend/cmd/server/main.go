package main

import (
	"log"
	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/handlers"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

func main() {
	// Initialize database
	db, err := models.InitDB("words.db")
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	// Create service instances
	wordService := service.NewWordService(db)
	groupService := service.NewGroupService(db)
	studyService := service.NewStudyService(db)
	activityService := service.NewActivityService(db)
	dashboardService := service.NewDashboardService(db)

	// Initialize router
	router := gin.Default()

	// Register routes
	handlers.RegisterDashboardRoutes(router, dashboardService)
	handlers.RegisterWordRoutes(router, wordService)
	handlers.RegisterGroupRoutes(router, groupService)
	handlers.RegisterStudyRoutes(router, studyService, groupService)
	handlers.RegisterActivityRoutes(router, activityService)
	handlers.RegisterSystemRoutes(router, studyService)

	// Start server
	log.Println("Starting server on :8080")
	if err := router.Run(":8080"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
} 