package test

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"testing"
	"time"

	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
	"github.com/stretchr/testify/assert"
)

// E2ETest performs a comprehensive end-to-end test that simulates a user workflow
// by interacting with the API endpoints in sequence to verify the integration
// of different components.
func TestE2EUserWorkflow(t *testing.T) {
	// Create http client with timeout
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	baseURL := "http://localhost:8080/api"

	// 1. Create a new word
	t.Run("Create Word", func(t *testing.T) {
		word := models.Word{
			Japanese: "テスト",
			Romaji:   "tesuto",
			English:  "test",
			Notes:    "This is a test word",
		}

		wordJSON, err := json.Marshal(word)
		assert.NoError(t, err)

		resp, err := client.Post(baseURL+"/words", "application/json", bytes.NewBuffer(wordJSON))
		if err != nil {
			t.Skipf("Backend not running, skipping E2E test: %v", err)
			return
		}
		defer resp.Body.Close()

		assert.Equal(t, http.StatusCreated, resp.StatusCode)

		var createdWord models.Word
		err = json.NewDecoder(resp.Body).Decode(&createdWord)
		assert.NoError(t, err)
		assert.NotZero(t, createdWord.ID)
		assert.Equal(t, "テスト", createdWord.Japanese)
		
		// Save the ID for later tests
		t.Logf("Created word with ID: %d", createdWord.ID)
	})

	// 2. Create a new group
	var groupID int64
	t.Run("Create Group", func(t *testing.T) {
		group := models.Group{
			Name:        "Test Group E2E",
			Description: "A group created during E2E testing",
		}

		groupJSON, err := json.Marshal(group)
		assert.NoError(t, err)

		resp, err := client.Post(baseURL+"/groups", "application/json", bytes.NewBuffer(groupJSON))
		if err != nil {
			t.Skipf("Backend not running, skipping test: %v", err)
			return
		}
		defer resp.Body.Close()

		assert.Equal(t, http.StatusCreated, resp.StatusCode)

		var createdGroup models.Group
		err = json.NewDecoder(resp.Body).Decode(&createdGroup)
		assert.NoError(t, err)
		assert.NotZero(t, createdGroup.ID)
		assert.Equal(t, "Test Group E2E", createdGroup.Name)
		
		// Save the group ID for later use
		groupID = createdGroup.ID
		t.Logf("Created group with ID: %d", groupID)
	})

	// 3. Get all words
	t.Run("Get All Words", func(t *testing.T) {
		resp, err := client.Get(baseURL + "/words")
		if err != nil {
			t.Skipf("Backend not running, skipping test: %v", err)
			return
		}
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var words []models.Word
		err = json.NewDecoder(resp.Body).Decode(&words)
		assert.NoError(t, err)
		assert.NotEmpty(t, words)
	})

	// 4. Get all groups
	t.Run("Get All Groups", func(t *testing.T) {
		resp, err := client.Get(baseURL + "/groups")
		if err != nil {
			t.Skipf("Backend not running, skipping test: %v", err)
			return
		}
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var groups []models.Group
		err = json.NewDecoder(resp.Body).Decode(&groups)
		assert.NoError(t, err)
		assert.NotEmpty(t, groups)
	})

	// 5. Add word to group (assuming we have word ID 1)
	t.Run("Add Word to Group", func(t *testing.T) {
		if groupID == 0 {
			t.Skip("Group ID not available, skipping test")
			return
		}

		// Assume first word has ID 1, or get the first word ID from the API
		wordID := int64(1)
		url := fmt.Sprintf("%s/groups/%d/words/%d", baseURL, groupID, wordID)
		
		req, err := http.NewRequest("POST", url, nil)
		assert.NoError(t, err)
		
		resp, err := client.Do(req)
		if err != nil {
			t.Skipf("Backend not running, skipping test: %v", err)
			return
		}
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)
	})

	// 6. Get words in group
	t.Run("Get Words in Group", func(t *testing.T) {
		if groupID == 0 {
			t.Skip("Group ID not available, skipping test")
			return
		}

		url := fmt.Sprintf("%s/groups/%d/words", baseURL, groupID)
		resp, err := client.Get(url)
		if err != nil {
			t.Skipf("Backend not running, skipping test: %v", err)
			return
		}
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var words []models.Word
		err = json.NewDecoder(resp.Body).Decode(&words)
		assert.NoError(t, err)
		assert.NotEmpty(t, words)
	})

	// 7. Create a study session
	t.Run("Create Study Session", func(t *testing.T) {
		if groupID == 0 {
			t.Skip("Group ID not available, skipping test")
			return
		}

		// Assume activity ID 1 for flashcards
		activityID := int64(1)
		
		session := models.StudySession{
			ActivityID: activityID,
			GroupID:    groupID,
			StartTime:  time.Now(),
			Status:     "in_progress",
			TotalWords: 10,
		}

		sessionJSON, err := json.Marshal(session)
		assert.NoError(t, err)

		url := fmt.Sprintf("%s/study-sessions", baseURL)
		resp, err := client.Post(url, "application/json", bytes.NewBuffer(sessionJSON))
		if err != nil {
			t.Skipf("Backend not running, skipping test: %v", err)
			return
		}
		defer resp.Body.Close()

		// This might be 201 Created or 200 OK depending on implementation
		assert.True(t, resp.StatusCode == http.StatusCreated || resp.StatusCode == http.StatusOK)

		var createdSession models.StudySession
		err = json.NewDecoder(resp.Body).Decode(&createdSession)
		assert.NoError(t, err)
		assert.NotZero(t, createdSession.ID)
	})

	// 8. Get study sessions for a group
	t.Run("Get Study Sessions for Group", func(t *testing.T) {
		if groupID == 0 {
			t.Skip("Group ID not available, skipping test")
			return
		}

		url := fmt.Sprintf("%s/groups/%d/study-sessions", baseURL, groupID)
		resp, err := client.Get(url)
		if err != nil {
			t.Skipf("Backend not running, skipping test: %v", err)
			return
		}
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var sessions []models.StudySession
		err = json.NewDecoder(resp.Body).Decode(&sessions)
		assert.NoError(t, err)
		// We might have sessions or not, depending on the test database state
	})

	// 9. Get dashboard statistics
	t.Run("Get Dashboard Statistics", func(t *testing.T) {
		url := fmt.Sprintf("%s/dashboard/stats", baseURL)
		resp, err := client.Get(url)
		if err != nil {
			t.Skipf("Backend not running, skipping test: %v", err)
			return
		}
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		// The structure will depend on your API design
		var stats map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&stats)
		assert.NoError(t, err)
	})

	// 10. Test error handling - Try to get a non-existent group
	t.Run("Error Handling - Non-existent Resource", func(t *testing.T) {
		url := fmt.Sprintf("%s/groups/999999", baseURL)
		resp, err := client.Get(url)
		if err != nil {
			t.Skipf("Backend not running, skipping test: %v", err)
			return
		}
		defer resp.Body.Close()

		assert.Equal(t, http.StatusNotFound, resp.StatusCode)

		var errorResponse map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&errorResponse)
		assert.NoError(t, err)
		assert.Contains(t, errorResponse, "error")
	})
} 