package handlers

import (
	"log"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterStudySessionsRoutes registers study session related routes
func RegisterStudySessionsRoutes(router *gin.RouterGroup) {
	sessionsGroup := router.Group("/study_sessions")
	{
		sessionsGroup.GET("", getAllStudySessions)
		sessionsGroup.GET("/:id", getStudySessionByID)
		sessionsGroup.GET("/:id/words", getStudySessionWords)
	}
}

// getAllStudySessions returns all study sessions with pagination
func getAllStudySessions(c *gin.Context) {
	// Parse pagination parameters
	pageStr := c.DefaultQuery("page", "1")
	limitStr := c.DefaultQuery("limit", "20")

	page, err := strconv.Atoi(pageStr)
	if err != nil || page < 1 {
		page = 1
	}

	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit < 1 || limit > 100 {
		limit = 20
	}

	// Get sessions from service
	sessions, err := service.GetAllStudySessions(page, limit)
	if err != nil {
		log.Printf("Error retrieving study sessions: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve study sessions"})
		return
	}

	c.JSON(http.StatusOK, sessions)
}

// getStudySessionByID returns a specific study session by ID
func getStudySessionByID(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid session ID"})
		return
	}

	session, err := service.GetStudySessionByIDWithDetails(id)
	if err != nil {
		log.Printf("Error retrieving study session: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve study session"})
		return
	}

	if session == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Study session not found"})
		return
	}

	c.JSON(http.StatusOK, session)
}

// getStudySessionWords returns words reviewed in a specific study session
func getStudySessionWords(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid session ID"})
		return
	}

	// First verify that the session exists
	session, err := service.GetStudySessionByID(id)
	if err != nil {
		log.Printf("Error retrieving study session: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve study session"})
		return
	}

	if session == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Study session not found"})
		return
	}

	// Get words reviewed in the session
	records, err := service.GetStudyRecordsBySessionID(id)
	if err != nil {
		log.Printf("Error retrieving study records: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve study records"})
		return
	}

	c.JSON(http.StatusOK, records)
} 