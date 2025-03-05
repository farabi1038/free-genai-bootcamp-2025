package handlers

import (
	"net/http"
	"strconv"
	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// RegisterWordRoutes registers word API routes
func RegisterWordRoutes(router *gin.Engine, wordService *service.WordService) {
	wordGroup := router.Group("/api/words")
	{
		wordGroup.GET("", getAllWords(wordService))
		wordGroup.GET("/:id", getWordByID(wordService))
	}
}

// getAllWords returns all words
func getAllWords(service *service.WordService) gin.HandlerFunc {
	return func(c *gin.Context) {
		words, err := service.GetAllWords()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get words"})
			return
		}
		
		c.JSON(http.StatusOK, words)
	}
}

// getWordByID returns a single word by ID
func getWordByID(service *service.WordService) gin.HandlerFunc {
	return func(c *gin.Context) {
		idStr := c.Param("id")
		id, err := strconv.Atoi(idStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid word ID"})
			return
		}
		
		word, err := service.GetWordByID(id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
			return
		}
		
		c.JSON(http.StatusOK, word)
	}
} 