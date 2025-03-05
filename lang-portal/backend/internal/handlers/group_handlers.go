package handlers

import (
	"log"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterGroupRoutes registers group-related routes
func RegisterGroupRoutes(router *gin.RouterGroup, groupService *service.GroupService) {
	router.GET("", getAllGroups(groupService))
	router.GET("/:id", getGroupByID(groupService))
	router.GET("/:id/words", getWordsByGroupID(groupService))
	router.GET("/:id/study_sessions", getGroupStudySessions(groupService))
	router.POST("", createGroup(groupService))
}

// CreateGroupRequest represents the request body for creating a new group
type CreateGroupRequest struct {
	Name    string `json:"name" binding:"required"`
	WordIDs []int  `json:"word_ids"`
}

// getAllGroups returns all word groups
func getAllGroups(groupService *service.GroupService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get all groups from the service
		groups, err := groupService.GetAllGroups()
		if err != nil {
			log.Printf("Error retrieving groups: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve groups"})
			return
		}
		
		c.JSON(http.StatusOK, groups)
	}
}

// getGroupByID returns a specific group by ID
func getGroupByID(groupService *service.GroupService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Parse the group ID from the URL
		idStr := c.Param("id")
		id, err := strconv.Atoi(idStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
			return
		}
		
		// Get the group from the service
		group, err := groupService.GetGroupByID(id)
		if err != nil {
			log.Printf("Error retrieving group: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve group"})
			return
		}
		
		if group == nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
			return
		}
		
		c.JSON(http.StatusOK, group)
	}
}

// getWordsByGroupID returns words belonging to a specific group
func getWordsByGroupID(groupService *service.GroupService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Parse the group ID from the URL
		idStr := c.Param("id")
		id, err := strconv.Atoi(idStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
			return
		}
		
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
		
		// Get words for the group from the service
		words, err := groupService.GetWordsByGroupID(id, page, limit)
		if err != nil {
			log.Printf("Error retrieving words: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve words"})
			return
		}
		
		c.JSON(http.StatusOK, words)
	}
}

// getGroupStudySessions returns study sessions for a specific group
func getGroupStudySessions(groupService *service.GroupService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Parse the group ID from the URL
		idStr := c.Param("id")
		id, err := strconv.Atoi(idStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
			return
		}
		
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
		
		// Get study sessions for the group from the service
		sessions, err := groupService.GetGroupStudySessions(id, page, limit)
		if err != nil {
			log.Printf("Error retrieving study sessions: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve study sessions"})
			return
		}
		
		c.JSON(http.StatusOK, sessions)
	}
}

// createGroup creates a new word group
func createGroup(groupService *service.GroupService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var request CreateGroupRequest
		if err := c.ShouldBindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		
		// Create a new group
		group := &models.Group{
			Name: request.Name,
		}
		
		// Call the service to create the group
		err := groupService.CreateGroup(group)
		if err != nil {
			log.Printf("Error creating group: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create group"})
			return
		}
		
		// If word IDs are provided, add them to the group
		if len(request.WordIDs) > 0 {
			for _, wordID := range request.WordIDs {
				err := groupService.AddWordToGroup(wordID, group.ID)
				if err != nil {
					log.Printf("Error adding word to group: %v", err)
					// Continue with other words, don't fail the entire request
				}
			}
		}
		
		c.JSON(http.StatusCreated, group)
	}
} 