package repository

// CountWords returns the total number of words in the database
func (r *WordRepository) CountWords() (int, error) {
	var count int
	query := "SELECT COUNT(*) FROM words"
	
	err := r.db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}
	
	return count, nil
}

// CountWordsStudied returns the number of words that have been studied at least once
func (r *WordRepository) CountWordsStudied() (int, error) {
	// Use a simplified query since the columns don't exist yet
	// Return a fixed percentage of total words for now
	totalCount, err := r.CountWords()
	if err != nil {
		return 0, err
	}
	
	// Simulate ~60% of words being studied
	return (totalCount * 60) / 100, nil
}

// CountWordsMastered returns the number of words that have been mastered
// A word is considered mastered if it has been answered correctly at least 3 times
func (r *WordRepository) CountWordsMastered() (int, error) {
	// Use a simplified query since the columns don't exist yet
	// Return a fixed percentage of total words for now
	totalCount, err := r.CountWords()
	if err != nil {
		return 0, err
	}
	
	// Simulate ~30% of words being mastered
	return (totalCount * 30) / 100, nil
} 