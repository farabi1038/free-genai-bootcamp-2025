package service

import (
	"database/sql"
	"log"
)

// Global database connection used by all services
var db *sql.DB

// InitDB initializes the database connection for all services
func InitDB(database *sql.DB) {
	db = database
	log.Println("Service layer initialized with database connection")
} 