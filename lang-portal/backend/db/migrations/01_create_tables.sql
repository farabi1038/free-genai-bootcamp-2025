-- Create words table
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    japanese TEXT NOT NULL,
    romaji TEXT NOT NULL,
    english TEXT NOT NULL,
    parts TEXT,
    correct_count INTEGER DEFAULT 0,
    wrong_count INTEGER DEFAULT 0
);

-- Create groups table
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Create words_groups join table
CREATE TABLE IF NOT EXISTS words_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words (id),
    FOREIGN KEY (group_id) REFERENCES groups (id)
);

-- Create study_activities table
CREATE TABLE IF NOT EXISTS study_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    thumbnail_url TEXT NOT NULL,
    description TEXT NOT NULL
);

-- Create study_sessions table
CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    study_activity_id INTEGER NOT NULL,
    score INTEGER DEFAULT 0,
    total INTEGER DEFAULT 0,
    activity_id INTEGER DEFAULT 0,
    FOREIGN KEY (group_id) REFERENCES groups (id),
    FOREIGN KEY (study_activity_id) REFERENCES study_activities (id)
);

-- Create words_studied table for tracking learning records
CREATE TABLE IF NOT EXISTS words_studied (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    study_session_id INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words (id),
    FOREIGN KEY (study_session_id) REFERENCES study_sessions (id)
); 