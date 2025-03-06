package handlers

import (
	"log"
	"net/http"
	"strconv"
	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterStudyActivityRoutes registers study activity API routes
func RegisterStudyActivityRoutes(router *gin.RouterGroup, studyActivityService *service.StudyActivityService) {
	// Study activity endpoints
	activityGroup := router.Group("")
	{
		activityGroup.GET("", getAllStudyActivities(studyActivityService))
		activityGroup.GET("/:id", getStudyActivityById(studyActivityService))
		activityGroup.GET("/:id/study_sessions", getStudySessionsByActivityId(studyActivityService))
		activityGroup.POST("", launchStudyActivity(studyActivityService))
	}

	// Study session endpoints are now registered in study_sessions_handlers.go

	// Word stats endpoints - moved to the main API group
	statsGroup := router.Group("/stats")
	{
		statsGroup.POST("/words", updateWordStats(studyActivityService))
		statsGroup.POST("/activity", recordStudyActivity(studyActivityService))
	}
	
	// Settings endpoints are now registered in settings_handlers.go
}

// StudySessionRequest represents the request to create a study session
type StudySessionRequest struct {
	GroupID int `json:"group_id" binding:"required"`
	Score   int `json:"score" binding:"required"`
	Total   int `json:"total" binding:"required"`
}

// WordStatsRequest represents the request to update word stats
type WordStatsRequest struct {
	WordID  int  `json:"word_id" binding:"required"`
	Correct bool `json:"correct" binding:"required"`
}

// StudyActivityRequest represents a study activity record
type StudyActivityRequest struct {
	WordID    int  `json:"word_id" binding:"required"`
	SessionID int  `json:"session_id" binding:"required"`
	Correct   bool `json:"correct" binding:"required"`
}

// LaunchStudyActivityRequest represents a request to launch a study activity
type LaunchStudyActivityRequest struct {
	ActivityID int `json:"activity_id" binding:"required"`
	GroupID    int `json:"group_id" binding:"required"`
}

// getAllStudyActivities returns all study activities
func getAllStudyActivities(service *service.StudyActivityService) gin.HandlerFunc {
	return func(c *gin.Context) {
		activities, err := service.GetAllStudyActivities()
		if err != nil {
			log.Printf("Error getting activities: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get activities"})
			return
		}
		c.JSON(http.StatusOK, activities)
	}
}

// getStudyActivityById returns a study activity by ID
func getStudyActivityById(service *service.StudyActivityService) gin.HandlerFunc {
	return func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
			return
		}
		
		activity, err := service.GetStudyActivityByID(id)
		if err != nil {
			log.Printf("Error fetching study activity with ID %d: %v", id, err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch study activity"})
			return
		}
		
		if activity == nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Study activity not found"})
			return
		}
		
		c.JSON(http.StatusOK, activity)
	}
}

// getStudySessionsByActivityId returns study sessions for an activity
func getStudySessionsByActivityId(service *service.StudyActivityService) gin.HandlerFunc {
	return func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
			return
		}
		
		sessions, err := service.GetStudySessionsByActivityID(id)
		if err != nil {
			log.Printf("Error fetching study sessions for activity ID %d: %v", id, err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch study sessions"})
			return
		}
		
		c.JSON(http.StatusOK, sessions)
	}
}

// launchStudyActivity launches a study activity for a group
func launchStudyActivity(service *service.StudyActivityService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req LaunchStudyActivityRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		
		result, err := service.LaunchStudyActivity(req.ActivityID, req.GroupID)
		if err != nil {
			log.Printf("Error launching study activity: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to launch study activity"})
			return
		}
		
		c.JSON(http.StatusOK, result)
	}
}

// getStudySessionById returns a study session by ID
func getStudySessionById(service *service.StudyActivityService) gin.HandlerFunc {
	return func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
			return
		}
		
		session, err := service.GetStudySessionByID(id)
		if err != nil {
			log.Printf("Error fetching study session with ID %d: %v", id, err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch study session"})
			return
		}
		
		if session == nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Study session not found"})
			return
		}
		
		c.JSON(http.StatusOK, session)
	}
}

// createStudySession creates a new study session
func createStudySession(service *service.StudyActivityService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req StudySessionRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		
		session := &models.StudySession{
			GroupID: req.GroupID,
			Score:   req.Score,
			Total:   req.Total,
		}
		
		if err := service.CreateStudySession(session); err != nil {
			log.Printf("Error creating study session: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create study session"})
			return
		}
		
		c.JSON(http.StatusCreated, session)
	}
}

// updateWordStats updates word statistics
func updateWordStats(service *service.StudyActivityService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req WordStatsRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		
		if err := service.UpdateWordStats(req.WordID, req.Correct); err != nil {
			log.Printf("Error updating word stats: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update word stats"})
			return
		}
		
		c.JSON(http.StatusOK, gin.H{"success": true})
	}
}

// recordStudyActivity records a study activity
func recordStudyActivity(service *service.StudyActivityService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req StudyActivityRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		
		if err := service.RecordStudyActivity(req.WordID, req.SessionID, req.Correct); err != nil {
			log.Printf("Error recording study activity: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to record study activity"})
			return
		}
		
		c.JSON(http.StatusCreated, gin.H{"success": true})
	}
} 