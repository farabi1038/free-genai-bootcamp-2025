package handlers

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterDashboardRoutes registers dashboard API endpoints
func RegisterDashboardRoutes(router *gin.RouterGroup, dashboardService *service.DashboardService) {
	router.GET("/last_session", getLastStudySession(dashboardService))
	router.GET("/progress", getStudyProgress(dashboardService))
	router.GET("/stats", getQuickStats(dashboardService))
}

// getLastStudySession returns the most recent study session
func getLastStudySession(dashboardService *service.DashboardService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get the most recent study session from the service
		session, err := dashboardService.GetLastStudySession()
		if err != nil {
			log.Printf("Error retrieving last study session: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve last study session"})
			return
		}

		if session == nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "No study sessions found"})
			return
		}

		c.JSON(http.StatusOK, session)
	}
}

// getStudyProgress returns the user's study progress
func getStudyProgress(dashboardService *service.DashboardService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get study progress from the service
		progress, err := dashboardService.GetStudyProgress()
		if err != nil {
			log.Printf("Error retrieving study progress: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve study progress"})
			return
		}

		c.JSON(http.StatusOK, progress)
	}
}

// getQuickStats returns quick statistics for the dashboard
func getQuickStats(dashboardService *service.DashboardService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get quick stats from the service
		stats, err := dashboardService.GetQuickStats()
		if err != nil {
			log.Printf("Error retrieving quick stats: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve quick stats"})
			return
		}

		c.JSON(http.StatusOK, stats)
	}
} 