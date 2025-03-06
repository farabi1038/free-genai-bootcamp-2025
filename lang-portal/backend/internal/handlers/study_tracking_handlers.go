package handlers

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterStudyTrackingRoutes registers study tracking routes
func RegisterStudyTrackingRoutes(router *gin.RouterGroup) {
	router.POST("/sessions", trackCreateStudySession)
	router.POST("/word-stats", trackUpdateWordStats)
	router.POST("/activities", trackRecordStudyActivity)
}

// TrackingSessionRequest represents the request body for creating a study session
type TrackingSessionRequest struct {
	GroupID int `json:"group_id" binding:"required"`
	Score   int `json:"score" binding:"required"`
	Total   int `json:"total" binding:"required"`
}

// TrackingWordStatsRequest represents the request body for updating word statistics
type TrackingWordStatsRequest struct {
	WordID  int  `json:"word_id" binding:"required"`
	Correct bool `json:"correct" binding:"required"`
}

// TrackingActivityRequest represents the request body for recording a study activity
type TrackingActivityRequest struct {
	WordID    int  `json:"word_id" binding:"required"`
	SessionID int  `json:"session_id" binding:"required"`
	Correct   bool `json:"correct" binding:"required"`
}

// trackCreateStudySession handles the creation of a new study session
func trackCreateStudySession(c *gin.Context) {
	var request TrackingSessionRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// Create a new study session
	session := &models.StudySession{
		GroupID: request.GroupID,
		Score:   request.Score,
		Total:   request.Total,
	}
	
	// Call the service to create the session
	createdSession, err := service.CompleteStudySession(session)
	if err != nil {
		log.Printf("Error creating study session: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create study session"})
		return
	}
	
	c.JSON(http.StatusCreated, createdSession)
}

// trackUpdateWordStats updates the statistics for a word
func trackUpdateWordStats(c *gin.Context) {
	var request TrackingWordStatsRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// Call the service to update word stats
	err := service.UpdateWordStats(request.WordID, request.Correct)
	if err != nil {
		log.Printf("Error updating word stats: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update word stats"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"success": true})
}

// trackRecordStudyActivity records a study activity for a word
func trackRecordStudyActivity(c *gin.Context) {
	var request TrackingActivityRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// Call the service to record the study activity
	err := service.RecordStudyActivity(request.WordID, request.SessionID, request.Correct)
	if err != nil {
		log.Printf("Error recording study activity: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to record study activity"})
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{"success": true})
} 