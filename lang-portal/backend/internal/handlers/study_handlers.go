package handlers

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// StudySessionRequest defines the structure for creating a study session
type StudySessionRequest struct {
	GroupID         int `json:"group_id" binding:"required"`
	StudyActivityID int `json:"study_activity_id" binding:"required"`
}

// RegisterStudyRoutes registers study API routes
func RegisterStudyRoutes(router *gin.Engine, studyService *service.StudyService, groupService *service.GroupService) {
	studyGroup := router.Group("/api/study_activities")
	{
		studyGroup.GET("/:id", getStudyActivityByID(studyService))
		studyGroup.POST("", createStudySession(studyService, groupService))
	}
}

// getStudyActivityByID returns a single study activity by ID
func getStudyActivityByID(service *service.StudyService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// This would need to call the activity service
		// For now, we'll just return a placeholder
		c.JSON(http.StatusOK, gin.H{
			"id": 1,
			"name": "Vocabulary Quiz",
			"thumbnail_url": "https://example.com/thumbnail.jpg",
			"description": "Practice your vocabulary with flashcards",
		})
	}
}

// createStudySession creates a new study session
func createStudySession(studyService *service.StudyService, groupService *service.GroupService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var request StudySessionRequest
		if err := c.ShouldBindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}
		
		// Verify that the group exists
		_, err := groupService.GetGroupByID(request.GroupID)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
			return
		}
		
		// Create the study session
		session, err := studyService.CreateStudySession(request.GroupID, request.StudyActivityID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create study session"})
			return
		}
		
		c.JSON(http.StatusCreated, gin.H{
			"id": session.ID,
			"group_id": session.GroupID,
		})
	}
} 