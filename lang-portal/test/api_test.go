package test

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/free-genai-bootcamp-2025/lang-portal/internal/handlers"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/service"
	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

var router *gin.Engine

// setupTestDB creates a test database and initializes it with test data
func setupTestDB() (*models.TestDB, error) {
	// Create a temporary test database
	db, err := models.InitDB(":memory:")
	if err != nil {
		return nil, fmt.Errorf("failed to initialize test database: %v", err)
	}

	// Apply the database schema
	schemaSQL, err := os.ReadFile("../db/migrations/01_create_tables.sql")
	if err != nil {
		return nil, fmt.Errorf("failed to read schema file: %v", err)
	}

	_, err = db.Exec(string(schemaSQL))
	if err != nil {
		return nil, fmt.Errorf("failed to apply schema: %v", err)
	}

	// Seed the database with test data
	testData := models.TestData{
		Words: []models.Word{
			{Japanese: "テスト", Romaji: "tesuto", English: "test"},
			{Japanese: "例", Romaji: "rei", English: "example"},
		},
		Groups: []models.Group{
			{Name: "Test Group"},
			{Name: "Example Group"},
		},
		Activities: []models.StudyActivity{
			{Name: "Test Activity", ThumbnailURL: "http://example.com/test.jpg", Description: "A test activity"},
		},
	}

	return models.SeedTestData(db, testData)
}

// setupTestRouter sets up a test Gin router with all routes registered
func setupTestRouter(testDB *models.TestDB) *gin.Engine {
	gin.SetMode(gin.TestMode)
	router := gin.Default()

	// Create services
	wordService := service.NewWordService(testDB.DB)
	groupService := service.NewGroupService(testDB.DB)
	studyService := service.NewStudyService(testDB.DB)
	activityService := service.NewActivityService(testDB.DB)
	dashboardService := service.NewDashboardService(testDB.DB)

	// Register routes
	handlers.RegisterDashboardRoutes(router, dashboardService)
	handlers.RegisterWordRoutes(router, wordService)
	handlers.RegisterGroupRoutes(router, groupService)
	handlers.RegisterStudyRoutes(router, studyService, groupService)
	handlers.RegisterActivityRoutes(router, activityService)
	handlers.RegisterSystemRoutes(router, studyService)

	return router
}

func TestMain(m *testing.M) {
	// Set up test database and router
	testDB, err := setupTestDB()
	if err != nil {
		fmt.Printf("Failed to set up test database: %v\n", err)
		os.Exit(1)
	}
	defer testDB.DB.Close()

	router = setupTestRouter(testDB)

	// Run all tests
	exitCode := m.Run()

	// Exit with the test's exit code
	os.Exit(exitCode)
}

// performRequest is a helper function to perform a test request
func performRequest(method, path string, body interface{}) *httptest.ResponseRecorder {
	var reqBody *bytes.Buffer
	if body != nil {
		jsonData, _ := json.Marshal(body)
		reqBody = bytes.NewBuffer(jsonData)
	} else {
		reqBody = bytes.NewBuffer(nil)
	}

	req, _ := http.NewRequest(method, path, reqBody)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	resp := httptest.NewRecorder()
	router.ServeHTTP(resp, req)
	return resp
}

// Test cases for each API endpoint
func TestGetAllWords(t *testing.T) {
	resp := performRequest("GET", "/api/words", nil)
	
	if resp.Code != http.StatusOK {
		t.Errorf("Expected status code %d, got %d", http.StatusOK, resp.Code)
	}

	var words []models.Word
	err := json.Unmarshal(resp.Body.Bytes(), &words)
	if err != nil {
		t.Errorf("Error unmarshaling response: %v", err)
	}

	if len(words) != 2 {
		t.Errorf("Expected 2 words, got %d", len(words))
	}
}

func TestGetWordByID(t *testing.T) {
	resp := performRequest("GET", "/api/words/1", nil)
	
	if resp.Code != http.StatusOK {
		t.Errorf("Expected status code %d, got %d", http.StatusOK, resp.Code)
	}

	var word models.Word
	err := json.Unmarshal(resp.Body.Bytes(), &word)
	if err != nil {
		t.Errorf("Error unmarshaling response: %v", err)
	}

	if word.ID != 1 {
		t.Errorf("Expected word ID 1, got %d", word.ID)
	}
}

func TestGetAllGroups(t *testing.T) {
	resp := performRequest("GET", "/api/groups", nil)
	
	if resp.Code != http.StatusOK {
		t.Errorf("Expected status code %d, got %d", http.StatusOK, resp.Code)
	}

	var groups []models.Group
	err := json.Unmarshal(resp.Body.Bytes(), &groups)
	if err != nil {
		t.Errorf("Error unmarshaling response: %v", err)
	}

	if len(groups) != 2 {
		t.Errorf("Expected 2 groups, got %d", len(groups))
	}
}

func TestGetGroupByID(t *testing.T) {
	resp := performRequest("GET", "/api/groups/1", nil)
	
	if resp.Code != http.StatusOK {
		t.Errorf("Expected status code %d, got %d", http.StatusOK, resp.Code)
	}

	var group models.Group
	err := json.Unmarshal(resp.Body.Bytes(), &group)
	if err != nil {
		t.Errorf("Error unmarshaling response: %v", err)
	}

	if group.ID != 1 {
		t.Errorf("Expected group ID 1, got %d", group.ID)
	}
}

func TestCreateStudySession(t *testing.T) {
	requestBody := map[string]int{
		"group_id":          1,
		"study_activity_id": 1,
	}
	
	resp := performRequest("POST", "/api/study_activities", requestBody)
	
	if resp.Code != http.StatusCreated {
		t.Errorf("Expected status code %d, got %d", http.StatusCreated, resp.Code)
	}

	var response map[string]interface{}
	err := json.Unmarshal(resp.Body.Bytes(), &response)
	if err != nil {
		t.Errorf("Error unmarshaling response: %v", err)
	}

	if response["group_id"] != float64(1) {
		t.Errorf("Expected group_id 1, got %v", response["group_id"])
	}
}

func TestGetLastStudySession(t *testing.T) {
	// First, create a study session
	requestBody := map[string]int{
		"group_id":          1,
		"study_activity_id": 1,
	}
	
	performRequest("POST", "/api/study_activities", requestBody)
	
	// Then get the last study session
	resp := performRequest("GET", "/api/dashboard/last_study_session", nil)
	
	if resp.Code != http.StatusOK {
		t.Errorf("Expected status code %d, got %d", http.StatusOK, resp.Code)
	}

	var session models.StudySession
	err := json.Unmarshal(resp.Body.Bytes(), &session)
	if err != nil {
		t.Errorf("Error unmarshaling response: %v", err)
	}

	if session.GroupID != 1 {
		t.Errorf("Expected group ID 1, got %d", session.GroupID)
	}
}

func TestGetStudyProgress(t *testing.T) {
	resp := performRequest("GET", "/api/dashboard/study_progress", nil)
	
	if resp.Code != http.StatusOK {
		t.Errorf("Expected status code %d, got %d", http.StatusOK, resp.Code)
	}

	var progress map[string]int
	err := json.Unmarshal(resp.Body.Bytes(), &progress)
	if err != nil {
		t.Errorf("Error unmarshaling response: %v", err)
	}

	if _, ok := progress["total_available_words"]; !ok {
		t.Errorf("Expected total_available_words field in response")
	}
	
	if _, ok := progress["total_words_studied"]; !ok {
		t.Errorf("Expected total_words_studied field in response")
	}
}

func TestResetHistory(t *testing.T) {
	resp := performRequest("POST", "/api/reset_history", nil)
	
	if resp.Code != http.StatusOK {
		t.Errorf("Expected status code %d, got %d", http.StatusOK, resp.Code)
	}

	var response map[string]interface{}
	err := json.Unmarshal(resp.Body.Bytes(), &response)
	if err != nil {
		t.Errorf("Error unmarshaling response: %v", err)
	}

	if success, ok := response["success"].(bool); !ok || !success {
		t.Errorf("Expected success to be true, got %v", response["success"])
	}
}

func TestFullReset(t *testing.T) {
	resp := performRequest("POST", "/api/full_reset", nil)
	
	if resp.Code != http.StatusOK {
		t.Errorf("Expected status code %d, got %d", http.StatusOK, resp.Code)
	}

	var response map[string]interface{}
	err := json.Unmarshal(resp.Body.Bytes(), &response)
	if err != nil {
		t.Errorf("Error unmarshaling response: %v", err)
	}

	if success, ok := response["success"].(bool); !ok || !success {
		t.Errorf("Expected success to be true, got %v", response["success"])
	}
} 