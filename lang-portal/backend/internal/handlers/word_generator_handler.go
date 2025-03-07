package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
)

// WordGeneratorHandler handles requests for word generation
type WordGeneratorHandler struct {
	generator *service.WordGenerator
}

// NewWordGeneratorHandler creates a new WordGeneratorHandler
func NewWordGeneratorHandler(generator *service.WordGenerator) *WordGeneratorHandler {
	return &WordGeneratorHandler{generator: generator}
}

// RegisterWordGeneratorRoutes registers the routes for word generation
func RegisterWordGeneratorRoutes(router *gin.RouterGroup, generator *service.WordGenerator) {
	handler := NewWordGeneratorHandler(generator)
	
	router.POST("/generate", handler.GenerateWords)
}

// GenerateWords handles the request to generate words
func (h *WordGeneratorHandler) GenerateWords(c *gin.Context) {
	var req service.WordGenerationRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request parameters"})
		return
	}

	// Set defaults if not provided
	if req.TargetLanguage == "" {
		req.TargetLanguage = "Japanese"
	}
	if req.Count <= 0 {
		req.Count = 5
	}
	
	words, err := h.generator.GenerateWords(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to generate words",
			"details": err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"words": words,
	})
} 