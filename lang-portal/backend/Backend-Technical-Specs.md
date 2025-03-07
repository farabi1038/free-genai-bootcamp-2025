# Backend Server Technical Specifications

This document outlines the detailed technical specifications for building a backend server prototype for a language learning portal. The portal serves three main purposes: managing vocabulary inventory, recording study results, and acting as a unified launchpad for various learning applications.

---

## 1. Business Goal

The language learning school requires a prototype that will:

- **Manage Vocabulary Inventory:**  
  Maintain a comprehensive collection of vocabulary words that students can learn.

- **Learning Record Store (LRS):**  
  Record practice sessions by tracking correct and incorrect answers for each vocabulary word.

- **Unified Launchpad:**  
  Provide a single entry point from which different learning applications or activities can be launched.

---

## 2. Technical Requirements

- **Programming Language:**  
  The backend must be developed in **Go**.

- **Database:**  
  Use **SQLite3** as the storage engine with a single database file (`words.db`).

- **API Framework:**  
  Build the API using the **Gin** web framework.  
  - **JSON-only Responses:** All API endpoints must return responses in JSON format.

- **Task Runner:**  
  Utilize **Mage** to manage and run various backend tasks (e.g., database initialization, migrations, seeding).

- **User Model:**  
  There is no need for authentication or authorization. The system will operate as if there is only a single user for all operations.

---

## 3. Directory Structure

Organize your project with the following directory hierarchy to separate concerns clearly:

```
backend_go/
├── cmd/
│   └── server/                # Contains the main entry point for launching the server.
├── internal/
│   ├── models/                # Data structures and database operations.
│   ├── handlers/              # HTTP handlers, organized by feature (dashboard, words, groups, etc.).
│   └── service/               # Business logic and application services.
├── db/
│   ├── migrations/            # SQL migration files to create or update database schema.
│   └── seeds/                 # JSON seed files for initial data population.
├── magefile.go                # Mage task definitions.
├── go.mod                     # Go module file.
└── words.db                   # SQLite3 database file (located at the project root).
```

---

## 4. Database Schema

The project uses a single SQLite database (`words.db`). The database includes the following tables:

### **words** – Stores vocabulary words.  
| Column  | Type    | Description |
|---------|--------|-------------|
| `id`    | integer | Unique identifier |
| `japanese` | string | Word in Japanese |
| `romaji` | string | Phonetic representation |
| `english` | string | English translation |
| `parts` | json | Additional metadata, such as parts of speech |

### **words_groups** – Join table linking words to groups (many-to-many).  
| Column  | Type    | Description |
|---------|--------|-------------|
| `id`    | integer | Unique identifier |
| `word_id` | integer | Foreign key referencing a word |
| `group_id` | integer | Foreign key referencing a group |

### **groups** – Thematic groups of words.  
| Column  | Type    | Description |
|---------|--------|-------------|
| `id`    | integer | Unique identifier |
| `name`  | string  | Name of the group (e.g., "Basic Greetings") |

### **study_sessions** – Records study sessions that include multiple word review items.  
| Column  | Type    | Description |
|---------|--------|-------------|
| `id`    | integer | Unique identifier |
| `group_id` | integer | Foreign key referencing a group |
| `created_at` | datetime | Timestamp of session creation |
| `study_activity_id` | integer | Foreign key linking to a study activity |

---

## 5. API Endpoints

### **5.1 Dashboard Endpoints**

#### **GET /api/dashboard/last_study_session**
- **Response Example:**
```json
{
  "id": 123,
  "group_id": 456,
  "created_at": "2025-02-08T17:20:23-05:00",
  "study_activity_id": 789,
  "group_name": "Basic Greetings"
}
```

#### **GET /api/dashboard/study_progress**
- **Response Example:**
```json
{
  "total_words_studied": 3,
  "total_available_words": 124
}
```

---

### **5.2 Study Activities Endpoints**

#### **GET /api/study_activities/:id**
- **Response Example:**
```json
{
  "id": 1,
  "name": "Vocabulary Quiz",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "description": "Practice your vocabulary with flashcards"
}
```

#### **POST /api/study_activities**
- **Request Parameters:**
  - `group_id` (integer)
  - `study_activity_id` (integer)
- **Response Example:**
```json
{
  "id": 124,
  "group_id": 123
}
```

---

## 6. Task Runner Tasks

Mage is used to automate development tasks.

### **Initialize Database**
- Creates the `words.db` SQLite database file if it does not exist.

### **Migrate Database**
- Runs migration SQL files in order from `db/migrations/`.

### **Seed Data**
- Imports JSON seed files from `db/seeds/` and populates the database.

  **Example JSON Seed Data Format:**
  ```json
  [
    {
      "kanji": "払う",
      "romaji": "harau",
      "english": "to pay"
    }
  ]
  ```

---

## 7. Reset Endpoints

#### **POST /api/reset_history**
- **Response Example:**
```json
{
  "success": true,
  "message": "Study history has been reset"
}
```

#### **POST /api/full_reset**
- **Response Example:**
```json
{
  "success": true,
  "message": "System has been fully reset"
}
```

---

This `README.md` provides a clear and structured guide for setting up and using the backend server for the language learning portal.
