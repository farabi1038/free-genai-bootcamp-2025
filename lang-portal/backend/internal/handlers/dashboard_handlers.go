package handlers

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterDashboardRoutes registers dashboard API routes
func RegisterDashboardRoutes(router *gin.Engine, dashboardService *service.DashboardService) {
	dashboardGroup := router.Group("/api/dashboard")
	{
		dashboardGroup.GET("/last_study_session", getLastStudySession(dashboardService))
		dashboardGroup.GET("/study_progress", getStudyProgress(dashboardService))
	}
}

// getLastStudySession returns the most recent study session
func getLastStudySession(service *service.DashboardService) gin.HandlerFunc {
	return func(c *gin.Context) {
		session, err := service.GetLastStudySession()
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "No study sessions found"})
			return
		}
		
		c.JSON(http.StatusOK, session)
	}
}

// getStudyProgress returns the study progress statistics
func getStudyProgress(service *service.DashboardService) gin.HandlerFunc {
	return func(c *gin.Context) {
		progress, err := service.GetStudyProgress()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get study progress"})
			return
		}
		
		c.JSON(http.StatusOK, progress)
	}
} 