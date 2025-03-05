package handlers

import (
	"net/http"
	"strconv"
	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterGroupRoutes registers group API routes
func RegisterGroupRoutes(router *gin.Engine, groupService *service.GroupService) {
	groupGroup := router.Group("/api/groups")
	{
		groupGroup.GET("", getAllGroups(groupService))
		groupGroup.GET("/:id", getGroupByID(groupService))
		groupGroup.GET("/:id/words", getWordsByGroupID(groupService))
	}
}

// getAllGroups returns all groups
func getAllGroups(service *service.GroupService) gin.HandlerFunc {
	return func(c *gin.Context) {
		groups, err := service.GetAllGroups()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get groups"})
			return
		}
		
		c.JSON(http.StatusOK, groups)
	}
}

// getGroupByID returns a single group by ID
func getGroupByID(service *service.GroupService) gin.HandlerFunc {
	return func(c *gin.Context) {
		idStr := c.Param("id")
		id, err := strconv.Atoi(idStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
			return
		}
		
		group, err := service.GetGroupByID(id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
			return
		}
		
		c.JSON(http.StatusOK, group)
	}
}

// getWordsByGroupID returns all words in a group
func getWordsByGroupID(service *service.GroupService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// This endpoint would need to call the word service
		// For now, we'll just return a placeholder
		c.JSON(http.StatusOK, gin.H{"message": "Get words by group ID not implemented yet"})
	}
} 