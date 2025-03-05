package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

// Word represents a vocabulary word for seeding
type Word struct {
	Japanese string          `json:"japanese"`
	Romaji   string          `json:"romaji"`
	English  string          `json:"english"`
	Parts    json.RawMessage `json:"parts,omitempty"`
}

// Group represents a word group for seeding
type Group struct {
	Name string `json:"name"`
}

const dbFile = "words.db"

func main() {
	fmt.Println("Adding additional words and groups to the database...")
	
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		fmt.Printf("Failed to open database: %v\n", err)
		os.Exit(1)
	}
	defer db.Close()
	
	// Add new groups
	err = addGroups(db, "db/seeds/05_additional_groups.json")
	if err != nil {
		fmt.Printf("Error adding groups: %v\n", err)
		os.Exit(1)
	}
	
	// Add new words
	err = addWords(db, "db/seeds/04_additional_words.json")
	if err != nil {
		fmt.Printf("Error adding words: %v\n", err)
		os.Exit(1)
	}
	
	// Assign words to groups
	err = assignWordCategories(db)
	if err != nil {
		fmt.Printf("Error assigning words to groups: %v\n", err)
		os.Exit(1)
	}
	
	fmt.Println("Successfully added additional words and groups to the database!")
}

// addGroups adds new groups from a JSON file
func addGroups(db *sql.DB, filePath string) error {
	fmt.Println("Adding new groups...")
	
	groups, err := loadGroups(filePath)
	if err != nil {
		return err
	}
	
	for _, group := range groups {
		// Check if group already exists
		var count int
		err = db.QueryRow("SELECT COUNT(*) FROM groups WHERE name = ?", group.Name).Scan(&count)
		if err != nil {
			return fmt.Errorf("failed to check if group exists: %v", err)
		}
		
		if count == 0 {
			fmt.Printf("Inserting group: %s\n", group.Name)
			_, err = db.Exec("INSERT INTO groups (name) VALUES (?)", group.Name)
			if err != nil {
				return fmt.Errorf("failed to insert group: %v", err)
			}
		} else {
			fmt.Printf("Group already exists: %s\n", group.Name)
		}
	}
	
	return nil
}

// addWords adds new words from a JSON file
func addWords(db *sql.DB, filePath string) error {
	fmt.Println("Adding new words...")
	
	words, err := loadWords(filePath)
	if err != nil {
		return err
	}
	
	for _, word := range words {
		// Check if word already exists
		var count int
		err = db.QueryRow("SELECT COUNT(*) FROM words WHERE japanese = ? AND english = ?", 
			word.Japanese, word.English).Scan(&count)
		if err != nil {
			return fmt.Errorf("failed to check if word exists: %v", err)
		}
		
		if count == 0 {
			fmt.Printf("Inserting word: %s (%s)\n", word.Japanese, word.English)
			_, err = db.Exec(
				"INSERT INTO words (japanese, romaji, english, parts) VALUES (?, ?, ?, ?)",
				word.Japanese, word.Romaji, word.English, word.Parts,
			)
			if err != nil {
				return fmt.Errorf("failed to insert word: %v", err)
			}
		} else {
			fmt.Printf("Word already exists: %s (%s)\n", word.Japanese, word.English)
		}
	}
	
	return nil
}

// assignWordCategories assigns words to their respective categories
func assignWordCategories(db *sql.DB) error {
	fmt.Println("Assigning words to categories...")
	
	// Numbers category
	numbers := []string{"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"}
	err := assignWordsToGroup(db, numbers, "Numbers")
	if err != nil {
		return err
	}
	
	// Colors category
	colors := []string{"red", "blue", "yellow", "green", "black", "white", "orange", "pink", "purple", "brown"}
	err = assignWordsToGroup(db, colors, "Colors")
	if err != nil {
		return err
	}
	
	// Food and Drinks category
	foodAndDrinks := []string{"water", "tea", "coffee", "rice", "bread", "meat", "fish", "vegetables", "fruit", "apple"}
	err = assignWordsToGroup(db, foodAndDrinks, "Food and Drinks")
	if err != nil {
		return err
	}
	
	// Days and Time category
	daysAndTime := []string{"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
	err = assignWordsToGroup(db, daysAndTime, "Days and Time")
	if err != nil {
		return err
	}
	
	// Seasons category
	seasons := []string{"spring", "summer", "autumn", "winter"}
	err = assignWordsToGroup(db, seasons, "Seasons")
	if err != nil {
		return err
	}
	
	// Animals category
	animals := []string{"dog", "cat", "bird", "fish"}
	err = assignWordsToGroup(db, animals, "Animals")
	if err != nil {
		return err
	}
	
	// Family category
	family := []string{"family", "mother", "father", "older sister", "older brother", "younger sister", "younger brother"}
	err = assignWordsToGroup(db, family, "Family")
	if err != nil {
		return err
	}
	
	// School and Education category
	school := []string{"school", "teacher", "student", "friend", "book", "pen", "pencil"}
	err = assignWordsToGroup(db, school, "School and Education")
	if err != nil {
		return err
	}
	
	// Transportation category
	transportation := []string{"car", "bicycle", "train", "bus", "airplane"}
	err = assignWordsToGroup(db, transportation, "Transportation")
	if err != nil {
		return err
	}
	
	return nil
}

// loadWords loads word data from a JSON file
func loadWords(filePath string) ([]Word, error) {
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read words seed file: %v", err)
	}
	
	var words []Word
	err = json.Unmarshal(data, &words)
	if err != nil {
		return nil, fmt.Errorf("failed to parse words seed data: %v", err)
	}
	
	return words, nil
}

// loadGroups loads group data from a JSON file
func loadGroups(filePath string) ([]Group, error) {
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read groups seed file: %v", err)
	}
	
	var groups []Group
	err = json.Unmarshal(data, &groups)
	if err != nil {
		return nil, fmt.Errorf("failed to parse groups seed data: %v", err)
	}
	
	return groups, nil
}

// assignWordsToGroup assigns words to a group based on their English translation
func assignWordsToGroup(db *sql.DB, englishWords []string, groupName string) error {
	var groupID int
	err := db.QueryRow("SELECT id FROM groups WHERE name = ?", groupName).Scan(&groupID)
	if err != nil {
		return fmt.Errorf("failed to find group '%s': %v", groupName, err)
	}
	
	for _, english := range englishWords {
		var wordID int
		err := db.QueryRow("SELECT id FROM words WHERE english = ?", english).Scan(&wordID)
		if err != nil {
			fmt.Printf("Warning: Word '%s' not found, skipping assignment to group '%s'\n", english, groupName)
			continue
		}
		
		// Check if word is already in the group
		var count int
		err = db.QueryRow("SELECT COUNT(*) FROM word_groups WHERE word_id = ? AND group_id = ?", 
			wordID, groupID).Scan(&count)
		if err != nil {
			return fmt.Errorf("failed to check if word is already in group: %v", err)
		}
		
		if count == 0 {
			fmt.Printf("Assigning word '%s' to group '%s'\n", english, groupName)
			_, err = db.Exec("INSERT INTO word_groups (word_id, group_id) VALUES (?, ?)", wordID, groupID)
			if err != nil {
				return fmt.Errorf("failed to assign word to group: %v", err)
			}
		} else {
			fmt.Printf("Word '%s' is already in group '%s'\n", english, groupName)
		}
	}
	
	return nil
} 