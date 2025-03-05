package service

import (
	"log"
	"time"
)

// ResetStudyHistory resets all study history by clearing study sessions and records,
// and resetting word statistics
func ResetStudyHistory() error {
	log.Println("Resetting study history...")
	
	// Begin a transaction to ensure consistency
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer func() {
		if err != nil {
			tx.Rollback()
		}
	}()

	// Delete all study records
	_, err = tx.Exec("DELETE FROM study_records")
	if err != nil {
		log.Printf("Error deleting study records: %v", err)
		return err
	}

	// Delete all study sessions
	_, err = tx.Exec("DELETE FROM study_sessions")
	if err != nil {
		log.Printf("Error deleting study sessions: %v", err)
		return err
	}

	// Reset word statistics
	_, err = tx.Exec("UPDATE words SET correct_count = 0, wrong_count = 0, updated_at = ?", time.Now())
	if err != nil {
		log.Printf("Error resetting word statistics: %v", err)
		return err
	}

	// Commit the transaction
	err = tx.Commit()
	if err != nil {
		return err
	}

	log.Println("Study history has been reset successfully")
	return nil
}

// FullReset performs a full database reset by clearing all data and reseeding
func FullReset() error {
	log.Println("Performing full database reset...")
	
	// Begin a transaction to ensure consistency
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer func() {
		if err != nil {
			tx.Rollback()
		}
	}()

	// Delete all study records
	_, err = tx.Exec("DELETE FROM study_records")
	if err != nil {
		log.Printf("Error deleting study records: %v", err)
		return err
	}

	// Delete all study sessions
	_, err = tx.Exec("DELETE FROM study_sessions")
	if err != nil {
		log.Printf("Error deleting study sessions: %v", err)
		return err
	}

	// Delete all group-word associations
	_, err = tx.Exec("DELETE FROM group_words")
	if err != nil {
		log.Printf("Error deleting group-word associations: %v", err)
		return err
	}

	// Delete all words
	_, err = tx.Exec("DELETE FROM words")
	if err != nil {
		log.Printf("Error deleting words: %v", err)
		return err
	}

	// Delete all groups
	_, err = tx.Exec("DELETE FROM groups")
	if err != nil {
		log.Printf("Error deleting groups: %v", err)
		return err
	}

	// Commit the transaction
	err = tx.Commit()
	if err != nil {
		return err
	}

	// Reseed the database
	// We're calling a function from the models package to insert default data
	err = reseedDatabase()
	if err != nil {
		return err
	}

	log.Println("Database has been fully reset and reseeded")
	return nil
}

// reseedDatabase reseeds the database with default data
func reseedDatabase() error {
	// Insert default group
	result, err := db.Exec("INSERT INTO groups (name) VALUES (?)", "Basic Japanese")
	if err != nil {
		return err
	}

	groupID, err := result.LastInsertId()
	if err != nil {
		return err
	}

	// Insert default words
	words := []struct {
		japanese string
		romaji   string
		english  string
	}{
		{japanese: "こんにちは", romaji: "konnichiwa", english: "hello"},
		{japanese: "ありがとう", romaji: "arigatou", english: "thank you"},
		{japanese: "さようなら", romaji: "sayounara", english: "goodbye"},
		{japanese: "はい", romaji: "hai", english: "yes"},
		{japanese: "いいえ", romaji: "iie", english: "no"},
	}

	for _, word := range words {
		// Insert the word
		result, err := db.Exec(
			"INSERT INTO words (japanese, romaji, english) VALUES (?, ?, ?)",
			word.japanese,
			word.romaji,
			word.english,
		)
		if err != nil {
			return err
		}

		// Get the ID of the inserted word
		wordID, err := result.LastInsertId()
		if err != nil {
			return err
		}

		// Associate the word with the default group
		_, err = db.Exec(
			"INSERT INTO group_words (group_id, word_id) VALUES (?, ?)",
			groupID,
			wordID,
		)
		if err != nil {
			return err
		}
	}

	return nil
} 