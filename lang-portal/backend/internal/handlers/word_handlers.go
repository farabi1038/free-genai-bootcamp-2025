package handlers

import (
	"log"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterWordRoutes registers word-related routes
func RegisterWordRoutes(router *gin.RouterGroup, wordService *service.WordService) {
	router.GET("", getAllWords(wordService))
	router.GET("/:id", getWordByID(wordService))
	router.POST("", createWord(wordService))
}

// CreateWordRequest represents the request body for creating a new word
type CreateWordRequest struct {
	Japanese string `json:"japanese" binding:"required"`
	Romaji   string `json:"romaji" binding:"required"`
	English  string `json:"english" binding:"required"`
	GroupIDs []int  `json:"group_ids"`
}

// getAllWords returns all words with pagination
func getAllWords(wordService *service.WordService) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Parse pagination parameters
		pageStr := c.DefaultQuery("page", "1")
		limitStr := c.DefaultQuery("limit", "100")
		
		page, err := strconv.Atoi(pageStr)
		if err != nil || page < 1 {
			page = 1
		}
		
		limit, err := strconv.Atoi(limitStr)
		if err != nil || limit < 1 || limit > 100 {
			limit = 100
		}
		
		// Get words from service
		words, err := wordService.GetAllWords(page, limit)
		if err != nil {
			log.Printf("Error retrieving words: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve words"})
			return
		}
		
		c.JSON(http.StatusOK, words)
	}
}

// getWordByID returns a specific word by ID
func getWordByID(wordService *service.WordService) gin.HandlerFunc {
	return func(c *gin.Context) {
		idStr := c.Param("id")
		id, err := strconv.Atoi(idStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid word ID"})
			return
		}
		
		word, err := wordService.GetWordByIDWithGroups(id)
		if err != nil {
			log.Printf("Error retrieving word: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve word"})
			return
		}
		
		if word == nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
			return
		}
		
		c.JSON(http.StatusOK, word)
	}
}

// createWord creates a new word
func createWord(wordService *service.WordService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var request CreateWordRequest
		if err := c.ShouldBindJSON(&request); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		
		// Create a new word model
		word := &models.Word{
			Japanese: request.Japanese,
			Romaji:   request.Romaji,
			English:  request.English,
		}
		
		// Create the word
		err := wordService.CreateWord(word)
		if err != nil {
			log.Printf("Error creating word: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create word"})
			return
		}
		
		// If group IDs are provided, associate the word with the groups
		if len(request.GroupIDs) > 0 {
			for _, groupID := range request.GroupIDs {
				err := wordService.AddWordToGroup(word.ID, groupID)
				if err != nil {
					log.Printf("Error adding word to group: %v", err)
					// Continue with other groups, don't fail the entire request
				}
			}
		}
		
		c.JSON(http.StatusCreated, word)
	}
} 