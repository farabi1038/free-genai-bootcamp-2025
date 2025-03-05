package repository

import (
	"database/sql"
)

// Repository represents a database repository
type Repository struct {
	db *sql.DB
}

// WordRepository handles database operations for words
type WordRepository struct {
	db *sql.DB
}

// GroupRepository handles database operations for groups
type GroupRepository struct {
	db *sql.DB
}

// StudySessionRepository handles database operations for study sessions
type StudySessionRepository struct {
	db *sql.DB
}

// NewRepository creates a new repository instance
func NewRepository(db *sql.DB) *Repository {
	return &Repository{db: db}
}

// NewWordRepository creates a new word repository instance
func NewWordRepository(db *sql.DB) *WordRepository {
	return &WordRepository{db: db}
}

// NewGroupRepository creates a new group repository instance
func NewGroupRepository(db *sql.DB) *GroupRepository {
	return &GroupRepository{db: db}
}

// NewStudySessionRepository creates a new study session repository instance
func NewStudySessionRepository(db *sql.DB) *StudySessionRepository {
	return &StudySessionRepository{db: db}
} 