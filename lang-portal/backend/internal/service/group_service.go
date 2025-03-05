package service

import (
	"database/sql"
	"time"

	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/repository"
)

// GroupService handles business logic for word groups
type GroupService struct {
	db *sql.DB
	repo *repository.Repository
}

// NewGroupService creates a new group service
func NewGroupService(db *sql.DB) *GroupService {
	return &GroupService{
		db: db,
		repo: nil, // Just to use the repository package
	}
}

// GetAllGroups retrieves all word groups
func (s *GroupService) GetAllGroups() ([]models.Group, error) {
	query := `SELECT g.id, g.name, 
              (SELECT COUNT(*) FROM group_words WHERE group_id = g.id) as word_count
              FROM groups g
              ORDER BY g.name ASC`
	
	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var groups []models.Group
	for rows.Next() {
		var group models.Group
		err := rows.Scan(
			&group.ID,
			&group.Name,
			&group.WordCount,
		)
		if err != nil {
			return nil, err
		}
		// Set default timestamps since they're not in the query
		group.CreatedAt = time.Now()
		group.UpdatedAt = time.Now()
		groups = append(groups, group)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return groups, nil
}

// GetGroupByID retrieves a group by ID
func (s *GroupService) GetGroupByID(id int) (*models.Group, error) {
	query := `SELECT g.id, g.name, 
              (SELECT COUNT(*) FROM group_words WHERE group_id = g.id) as word_count
              FROM groups g
              WHERE g.id = ?`
	
	var group models.Group
	err := s.db.QueryRow(query, id).Scan(
		&group.ID,
		&group.Name,
		&group.WordCount,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}

	if err != nil {
		return nil, err
	}

	// Set default timestamps since they're not in the query
	group.CreatedAt = time.Now()
	group.UpdatedAt = time.Now()

	return &group, nil
}

// GetWordsByGroupID retrieves words that belong to a specific group
func (s *GroupService) GetWordsByGroupID(groupID, page, limit int) ([]models.Word, error) {
	offset := (page - 1) * limit
	
	query := `SELECT w.id, w.japanese, w.romaji, w.english
              FROM words w
              JOIN group_words gw ON w.id = gw.word_id
              WHERE gw.group_id = ?
              ORDER BY w.id ASC
              LIMIT ? OFFSET ?`
	
	rows, err := s.db.Query(query, groupID, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	var words []models.Word
	for rows.Next() {
		var word models.Word
		err := rows.Scan(
			&word.ID,
			&word.Japanese,
			&word.Romaji,
			&word.English,
		)
		if err != nil {
			return nil, err
		}
		
		// Set default values for stats and timestamps
		word.CorrectCount = 0
		word.WrongCount = 0
		word.CreatedAt = time.Now()
		word.UpdatedAt = time.Now()
		
		words = append(words, word)
	}
	
	if err = rows.Err(); err != nil {
		return nil, err
	}
	
	return words, nil
}

// GetStudySessionsByGroupID retrieves study sessions for a specific group
func GetStudySessionsByGroupID(groupID, page, limit int) ([]models.StudySessionResponse, error) {
	offset := (page - 1) * limit
	
	query := `SELECT s.id, s.group_id, g.name as group_name, s.activity_id, 
              a.name as activity_name, s.score, s.total, s.created_at
              FROM study_sessions s
              JOIN groups g ON s.group_id = g.id
              JOIN study_activities a ON s.activity_id = a.id
              WHERE s.group_id = ?
              ORDER BY s.created_at DESC
              LIMIT ? OFFSET ?`
	
	rows, err := db.Query(query, groupID, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var sessions []models.StudySessionResponse
	for rows.Next() {
		var session models.StudySessionResponse
		err := rows.Scan(
			&session.ID,
			&session.GroupID,
			&session.GroupName,
			&session.ActivityID,
			&session.ActivityName,
			&session.Score,
			&session.Total,
			&session.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		sessions = append(sessions, session)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return sessions, nil
}

// CreateGroup creates a new group
func CreateGroup(group *models.Group) (*models.Group, error) {
	// Set created and updated times
	now := time.Now()
	group.CreatedAt = now
	group.UpdatedAt = now

	query := `INSERT INTO groups (name, created_at, updated_at)
              VALUES (?, ?, ?)`
	
	result, err := db.Exec(
		query,
		group.Name,
		group.CreatedAt,
		group.UpdatedAt,
	)
	if err != nil {
		return nil, err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}

	group.ID = int(id)
	return group, nil
}

// CountWordsInGroup counts the number of words in a group
func CountWordsInGroup(groupID int) (int, error) {
	var count int
	query := "SELECT COUNT(*) FROM group_words WHERE group_id = ?"
	err := db.QueryRow(query, groupID).Scan(&count)
	if err != nil {
		return 0, err
	}
	return count, nil
}

// AddWordToGroup adds a word to a group
func (s *GroupService) AddWordToGroup(wordID, groupID int) error {
	return models.AddWordToGroup(s.db, wordID, groupID)
}

// GetGroupStudySessions retrieves all study sessions for a group
func (s *GroupService) GetGroupStudySessions(groupID, page, limit int) ([]models.StudySessionResponse, error) {
	// For now, implement a simple mock response
	now := time.Now()
	sessions := []models.StudySessionResponse{
		{
			ID:           1,
			GroupID:      groupID,
			GroupName:    "Example Group",
			ActivityID:   1,
			ActivityName: "Flashcards",
			Score:        8,
			Total:        10,
			CreatedAt:    now.AddDate(0, 0, -1),
		},
		{
			ID:           2,
			GroupID:      groupID,
			GroupName:    "Example Group",
			ActivityID:   2,
			ActivityName: "Matching Game",
			Score:        7,
			Total:        10,
			CreatedAt:    now.AddDate(0, 0, -2),
		},
	}
	
	return sessions, nil
}

// CreateGroup creates a new group
func (s *GroupService) CreateGroup(group *models.Group) error {
	query := "INSERT INTO groups (name) VALUES (?)"
	
	result, err := s.db.Exec(query, group.Name)
	if err != nil {
		return err
	}
	
	id, err := result.LastInsertId()
	if err != nil {
		return err
	}
	
	group.ID = int(id)
	return nil
} 