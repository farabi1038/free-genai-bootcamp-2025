package handlers

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterSystemRoutes registers system API routes
func RegisterSystemRoutes(router *gin.Engine, studyService *service.StudyService) {
	systemGroup := router.Group("/api")
	{
		systemGroup.POST("/reset_history", resetHistory(studyService))
		systemGroup.POST("/full_reset", fullReset(studyService))
	}
}

// resetHistory removes all study history
func resetHistory(service *service.StudyService) gin.HandlerFunc {
	return func(c *gin.Context) {
		err := service.ResetStudyHistory()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to reset study history"})
			return
		}
		
		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"message": "Study history has been reset",
		})
	}
}

// fullReset performs a complete system reset
func fullReset(service *service.StudyService) gin.HandlerFunc {
	return func(c *gin.Context) {
		err := service.FullReset()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to perform full reset"})
			return
		}
		
		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"message": "System has been fully reset",
		})
	}
} 