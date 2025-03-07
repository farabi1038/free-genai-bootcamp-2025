package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

// OllamaRequest represents a request to the Ollama API
type OllamaRequest struct {
	Model    string        `json:"model"`
	Messages []ChatMessage `json:"messages"`
	Stream   bool          `json:"stream"`
}

// ChatMessage represents a message in a chat conversation
type ChatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// OllamaResponse represents a response from the Ollama API
type OllamaResponse struct {
	Message ChatMessage `json:"message"`
}

// WordGenerationRequest defines parameters for word generation
type WordGenerationRequest struct {
	TargetLanguage string `json:"target_language"`
	Category       string `json:"category"`
	Count          int    `json:"count"`
}

// GeneratedWord represents a generated word
type GeneratedWord struct {
	Japanese string `json:"japanese"`
	Romaji   string `json:"romaji"`
	English  string `json:"english"`
}

// WordGenerator provides methods for generating vocabulary words using LLM
type WordGenerator struct {
	ollamaURL string
	modelID   string
}

// NewWordGenerator creates a new WordGenerator
func NewWordGenerator(ollamaURL, modelID string) *WordGenerator {
	return &WordGenerator{
		ollamaURL: ollamaURL,
		modelID:   modelID,
	}
}

// GenerateWords generates new vocabulary words using the Ollama LLM
func (wg *WordGenerator) GenerateWords(req WordGenerationRequest) ([]GeneratedWord, error) {
	// Create prompt for the LLM
	prompt := fmt.Sprintf(
		"Generate %d Japanese vocabulary words in the category '%s'. "+
			"Format each word as a JSON object with 'japanese', 'romaji', and 'english' fields. "+
			"Return only valid JSON array without any explanations or comments.",
		req.Count, req.Category,
	)

	// Create request to Ollama
	ollamaReq := OllamaRequest{
		Model: wg.modelID,
		Messages: []ChatMessage{
			{
				Role:    "user",
				Content: prompt,
			},
		},
		Stream: false,
	}

	// Marshal request to JSON
	reqBody, err := json.Marshal(ollamaReq)
	if err != nil {
		return nil, fmt.Errorf("error marshaling request: %w", err)
	}

	// Send request to Ollama
	resp, err := http.Post(
		fmt.Sprintf("%s/api/chat", wg.ollamaURL),
		"application/json",
		bytes.NewBuffer(reqBody),
	)
	if err != nil {
		return nil, fmt.Errorf("error connecting to Ollama: %w", err)
	}
	defer resp.Body.Close()

	// Check response status
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("error from Ollama API: status %d", resp.StatusCode)
	}

	// Decode response
	var ollamaResp OllamaResponse
	if err := json.NewDecoder(resp.Body).Decode(&ollamaResp); err != nil {
		return nil, fmt.Errorf("error decoding response: %w", err)
	}

	// Parse generated words from response
	var words []GeneratedWord
	if err := json.Unmarshal([]byte(ollamaResp.Message.Content), &words); err != nil {
		return nil, fmt.Errorf("error parsing generated words: %w", err)
	}

	return words, nil
} 