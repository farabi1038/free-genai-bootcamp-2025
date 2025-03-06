package handlers

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterSettingsRoutes registers settings-related API endpoints
func RegisterSettingsRoutes(router *gin.RouterGroup) {
	router.POST("/reset_history", resetHistory)
	router.POST("/full_reset", fullReset)
}

// resetHistory resets all study history
func resetHistory(c *gin.Context) {
	err := service.ResetStudyHistory()
	if err != nil {
		log.Printf("Error resetting study history: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to reset study history"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Study history has been reset",
	})
}

// fullReset performs a full database reset
func fullReset(c *gin.Context) {
	err := service.FullReset()
	if err != nil {
		log.Printf("Error performing full reset: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to perform full reset"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "System has been fully reset",
	})
} 