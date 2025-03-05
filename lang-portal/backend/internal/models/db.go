package models

import (
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
)

// DB is the global database instance
var DB *sql.DB

// InitDB initializes the database connection
func InitDB(dataSourceName string) (*sql.DB, error) {
	db, err := sql.Open("sqlite3", dataSourceName)
	if err != nil {
		return nil, err
	}

	if err = db.Ping(); err != nil {
		return nil, err
	}

	DB = db
	return db, nil
} 