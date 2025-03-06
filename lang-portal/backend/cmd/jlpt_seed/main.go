package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

// Word represents a vocabulary word
type Word struct {
	ID       int    `json:"id,omitempty"`
	Japanese string `json:"japanese"`
	Romaji   string `json:"romaji"`
	English  string `json:"english"`
}

// Group represents a category of words
type Group struct {
	ID          int    `json:"id,omitempty"`
	Name        string `json:"name"`
	Description string `json:"description"`
}

// WordGroup represents a relationship between words and groups
type WordGroup struct {
	WordID  int
	GroupID int
}

func main() {
	// Open database connection
	db, err := sql.Open("sqlite3", "./words.db")
	if err != nil {
		fmt.Println("Error opening database:", err)
		return
	}
	defer db.Close()

	// Add JLPT groups
	jlptGroups, err := addGroups(db, "db/seeds/08_jlpt_groups.json")
	if err != nil {
		fmt.Println("Error adding JLPT groups:", err)
		return
	}
	fmt.Printf("Added %d JLPT groups\n", len(jlptGroups))

	// Add JLPT N5 words
	n5Words, err := addWords(db, "db/seeds/06_jlpt_n5_words.json")
	if err != nil {
		fmt.Println("Error adding JLPT N5 words:", err)
		return
	}
	fmt.Printf("Added %d JLPT N5 words\n", len(n5Words))

	// Add JLPT N4 words
	n4Words, err := addWords(db, "db/seeds/07_jlpt_n4_words.json")
	if err != nil {
		fmt.Println("Error adding JLPT N4 words:", err)
		return
	}
	fmt.Printf("Added %d JLPT N4 words\n", len(n4Words))

	// Assign words to appropriate JLPT groups
	n5GroupID := jlptGroups[0].ID
	n4GroupID := jlptGroups[1].ID

	// Assign N5 words to N5 group
	assignedN5, err := assignWordsToGroup(db, n5Words, n5GroupID)
	if err != nil {
		fmt.Println("Error assigning N5 words to group:", err)
		return
	}
	fmt.Printf("Assigned %d words to JLPT N5 group\n", assignedN5)

	// Assign N4 words to N4 group
	assignedN4, err := assignWordsToGroup(db, n4Words, n4GroupID)
	if err != nil {
		fmt.Println("Error assigning N4 words to group:", err)
		return
	}
	fmt.Printf("Assigned %d words to JLPT N4 group\n", assignedN4)

	fmt.Println("JLPT vocabulary and groups added successfully!")
}

// addGroups reads groups from a JSON file and adds them to the database
func addGroups(db *sql.DB, filePath string) ([]Group, error) {
	// Read and parse groups JSON
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("error reading groups file: %w", err)
	}

	var groups []Group
	if err := json.Unmarshal(data, &groups); err != nil {
		return nil, fmt.Errorf("error parsing groups JSON: %w", err)
	}

	// Insert groups into database
	stmt, err := db.Prepare("INSERT INTO groups (name, description) VALUES (?, ?)")
	if err != nil {
		return nil, fmt.Errorf("error preparing statement: %w", err)
	}
	defer stmt.Close()

	for i, group := range groups {
		result, err := stmt.Exec(group.Name, group.Description)
		if err != nil {
			if strings.Contains(err.Error(), "UNIQUE constraint failed") {
				// Group already exists, get its ID
				row := db.QueryRow("SELECT id FROM groups WHERE name = ?", group.Name)
				var id int
				if err := row.Scan(&id); err != nil {
					return nil, fmt.Errorf("error getting existing group ID: %w", err)
				}
				groups[i].ID = id
			} else {
				return nil, fmt.Errorf("error inserting group: %w", err)
			}
		} else {
			id, _ := result.LastInsertId()
			groups[i].ID = int(id)
		}
	}

	return groups, nil
}

// addWords reads words from a JSON file and adds them to the database
func addWords(db *sql.DB, filePath string) ([]Word, error) {
	// Read and parse words JSON
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("error reading words file: %w", err)
	}

	var words []Word
	if err := json.Unmarshal(data, &words); err != nil {
		return nil, fmt.Errorf("error parsing words JSON: %w", err)
	}

	// Insert words into database
	stmt, err := db.Prepare("INSERT INTO words (japanese, romaji, english) VALUES (?, ?, ?)")
	if err != nil {
		return nil, fmt.Errorf("error preparing statement: %w", err)
	}
	defer stmt.Close()

	for i, word := range words {
		result, err := stmt.Exec(word.Japanese, word.Romaji, word.English)
		if err != nil {
			if strings.Contains(err.Error(), "UNIQUE constraint failed") {
				// Word already exists, get its ID
				row := db.QueryRow("SELECT id FROM words WHERE japanese = ?", word.Japanese)
				var id int
				if err := row.Scan(&id); err != nil {
					return nil, fmt.Errorf("error getting existing word ID: %w", err)
				}
				words[i].ID = id
			} else {
				return nil, fmt.Errorf("error inserting word: %w", err)
			}
		} else {
			id, _ := result.LastInsertId()
			words[i].ID = int(id)
		}
	}

	return words, nil
}

// assignWordsToGroup assigns a list of words to a specific group
func assignWordsToGroup(db *sql.DB, words []Word, groupID int) (int, error) {
	stmt, err := db.Prepare("INSERT INTO word_groups (word_id, group_id) VALUES (?, ?)")
	if err != nil {
		return 0, fmt.Errorf("error preparing statement: %w", err)
	}
	defer stmt.Close()

	count := 0
	for _, word := range words {
		_, err := stmt.Exec(word.ID, groupID)
		if err != nil {
			if strings.Contains(err.Error(), "UNIQUE constraint failed") {
				// Relationship already exists, skip
				continue
			}
			return count, fmt.Errorf("error inserting word-group relationship: %w", err)
		}
		count++
	}

	return count, nil
} 