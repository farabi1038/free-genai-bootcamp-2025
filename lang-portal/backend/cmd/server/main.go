package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/handlers"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/repository"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

func setupRoutes(router *gin.Engine, db *sql.DB) {
	log.Println("Registering API routes...")
	
	// Initialize repositories
	wordRepo := repository.NewWordRepository(db)
	groupRepo := repository.NewGroupRepository(db)
	sessionRepo := repository.NewStudySessionRepository(db)
	
	// Initialize services
	wordService := service.NewWordService(db)
	groupService := service.NewGroupService(db)
	dashboardService := service.NewDashboardService(
		wordRepo,
		groupRepo, 
		sessionRepo,
	)
	studyActivityService := service.NewStudyActivityService(
		db,
		wordRepo,
		groupRepo,
		sessionRepo,
	)
	
	// Initialize word generator service
	ollamaURL := os.Getenv("OLLAMA_URL")
	if ollamaURL == "" {
		ollamaURL = "http://localhost:11434" // Default Ollama URL
	}
	modelID := os.Getenv("LLM_MODEL_ID")
	if modelID == "" {
		modelID = "llama3.2:1b" // Default model
	}
	wordGenerator := service.NewWordGenerator(ollamaURL, modelID)
	
	// Create the main API group
	apiGroup := router.Group("/api")
	
	// Register all routes using specific paths to avoid conflicts
	handlers.RegisterDashboardRoutes(apiGroup, dashboardService)
	handlers.RegisterStudyActivityRoutes(apiGroup.Group("/study-activities"), studyActivityService)
	handlers.RegisterWordRoutes(apiGroup.Group("/words"), wordService)
	handlers.RegisterGroupRoutes(apiGroup.Group("/groups"), groupService)
	handlers.RegisterStudySessionsRoutes(apiGroup.Group("/study-sessions"))
	handlers.RegisterStudyTrackingRoutes(apiGroup.Group("/study-tracking"))
	handlers.RegisterSettingsRoutes(apiGroup.Group("/settings"))
	
	// Register word generator routes
	handlers.RegisterWordGeneratorRoutes(apiGroup.Group("/word-generator"), wordGenerator)
	
	log.Println("API routes registered successfully")
}

func main() {
	log.Println("Starting language portal backend...")
	
	// Initialize database
	log.Println("Initializing database connection...")
	db, err := models.InitDB("words.db")
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()
	log.Println("Database connection established successfully")

	// Initialize database in service package
	service.InitDB(db)

	// Initialize router
	router := gin.Default()
	
	// Add middleware
	router.Use(cors.Default())
	router.Use(gin.Recovery())
	
	// Setup routes
	setupRoutes(router, db)

	// Add health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	// Start server
	log.Println("Starting server on :8080")
	if err := router.Run(":8080"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
} 