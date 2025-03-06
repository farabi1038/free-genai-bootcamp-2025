package models

import (
	"database/sql"
)

// GetAllGroups retrieves all groups from the database
func GetAllGroups(db *sql.DB) ([]Group, error) {
	query := `SELECT id, name FROM groups`
	rows, err := db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var groups []Group
	for rows.Next() {
		var group Group
		if err := rows.Scan(&group.ID, &group.Name); err != nil {
			return nil, err
		}
		groups = append(groups, group)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return groups, nil
}

// GetGroupByID retrieves a group by ID
func GetGroupByID(db *sql.DB, id int) (*Group, error) {
	query := `SELECT id, name FROM groups WHERE id = ?`
	var group Group
	err := db.QueryRow(query, id).Scan(&group.ID, &group.Name)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	return &group, nil
}

// CreateGroup creates a new group in the database
func CreateGroup(db *sql.DB, name string) (*Group, error) {
	query := `INSERT INTO groups (name) VALUES (?)`
	result, err := db.Exec(query, name)
	if err != nil {
		return nil, err
	}
	
	id, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}
	
	return &Group{
		ID:   int(id),
		Name: name,
	}, nil
}

// AddWordToGroup adds a word to a group
func AddWordToGroup(db *sql.DB, wordID, groupID int) error {
	query := `INSERT INTO words_groups (word_id, group_id) VALUES (?, ?)`
	_, err := db.Exec(query, wordID, groupID)
	return err
} 