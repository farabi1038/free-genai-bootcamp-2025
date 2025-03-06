package repository

import (
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
)

// CountGroups returns the total number of groups in the database
func (r *GroupRepository) CountGroups() (int, error) {
	var count int
	query := "SELECT COUNT(*) FROM groups"
	
	err := r.db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}
	
	return count, nil
}

// GetGroupByID retrieves a group by its ID
func (r *GroupRepository) GetGroupByID(id int) (*models.Group, error) {
	query := "SELECT id, name, created_at, updated_at FROM groups WHERE id = ?"
	
	var group models.Group
	err := r.db.QueryRow(query, id).Scan(
		&group.ID,
		&group.Name,
		&group.CreatedAt,
		&group.UpdatedAt,
	)
	
	if err != nil {
		return nil, err
	}
	
	return &group, nil
} 