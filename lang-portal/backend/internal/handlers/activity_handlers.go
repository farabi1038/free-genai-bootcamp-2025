package handlers

import (
	"net/http"
	"strconv"
	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterActivityRoutes registers activity API routes
func RegisterActivityRoutes(router *gin.Engine, activityService *service.ActivityService) {
	activityGroup := router.Group("/api/activities")
	{
		activityGroup.GET("", getAllActivities(activityService))
		activityGroup.GET("/:id", getActivityByID(activityService))
	}
}

// getAllActivities returns all study activities
func getAllActivities(service *service.ActivityService) gin.HandlerFunc {
	return func(c *gin.Context) {
		activities, err := service.GetAllActivities()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get activities"})
			return
		}
		
		c.JSON(http.StatusOK, activities)
	}
}

// getActivityByID returns a single activity by ID
func getActivityByID(service *service.ActivityService) gin.HandlerFunc {
	return func(c *gin.Context) {
		idStr := c.Param("id")
		id, err := strconv.Atoi(idStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid activity ID"})
			return
		}
		
		activity, err := service.GetActivityByID(id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Activity not found"})
			return
		}
		
		c.JSON(http.StatusOK, activity)
	}
} 