# Frontend Technical Specification

This document defines the purpose, components, and required API endpoints for each page in the study portal web application. It is intended as a clear guide for frontend development.

---

## 1. Dashboard (`/dashboard`)

### Purpose
- Provide a summary of the user’s learning activities.
- Serve as the default landing page upon accessing the web app.

### Components
- **Last Study Session**
  - Display the most recent activity.
  - Show the timestamp of the last activity.
  - Summarize the results (wrong vs. correct answers) of the last activity.
  - Provide a link to the associated group.
- **Study Progress**
  - Display total words studied (e.g., "3/124") across all sessions.
  - Show mastery progress (e.g., "0%").
- **Quick Stats**
  - Success rate (e.g., "80%").
  - Total number of study sessions (e.g., "4").
  - Total active groups (e.g., "3").
  - Study streak (e.g., "4 days").
- **Start Studying Button**
  - Redirects to the Study Activities page.

### API Endpoints
- `GET /api/dashboard/last_study_session`
- `GET /api/dashboard/study_progress`
- `GET /api/dashboard/quick_stats`

---

## 2. Study Activities Index (`/study_activities`)

### Purpose
- Display a collection of study activities with a thumbnail and name.
- Provide options to either launch a study activity or view more details about it.

### Components
- **Study Activity Card**
  - Thumbnail image.
  - Study activity name.
  - **Launch Button:** Redirects to the Study Activity Launch page.
  - **View Details Link:** Opens more information about past study sessions for the activity.

### API Endpoints
- `GET /api/study_activities`

---

## 3. Study Activity Details (`/study_activities/:id`)

### Purpose
- Present detailed information about a specific study activity.
- List past study sessions associated with the activity.

### Components
- Display the following:
  - Name of the study activity.
  - Thumbnail image.
  - Description.
- **Launch Button:** Initiates the study activity.
- **Study Sessions List (Paginated)**
  - Columns:
    - ID
    - Activity Name
    - Group Name
    - Start Time
    - End Time (inferred from the last word review item)
    - Number of review items

### API Endpoints
- `GET /api/study_activities/:id`
- `GET /api/study_activities/:id/study_sessions`

---

## 4. Study Activity Launch (`/study_activities/:id/launch`)

### Purpose
- Launch a specific study activity.

### Components
- Display the name of the study activity.
- **Launch Form:**
  - Group selection dropdown.
  - **Launch Now Button:** Submits the form to start the activity.

### Behavior
- Upon form submission:
  - Open a new tab with the study activity URL provided in the database.
  - Redirect the current page to the Study Session Details page.

### API Endpoints
- `POST /api/study_activities`

---

## 5. Words Index (`/words`)

### Purpose
- Display all words stored in the database.

### Components
- **Paginated Word List**
  - Table columns:
    - Japanese
    - Romaji
    - English
    - Correct Count
    - Wrong Count
  - Pagination set to 100 items per page.
  - Clicking on a Japanese word navigates to its detailed view.

### API Endpoints
- `GET /api/words`

---

## 6. Word Details (`/words/:id`)

### Purpose
- Show detailed information for a specific word.

### Components
- **Word Information:**
  - Japanese
  - Romaji
  - English
- **Study Statistics:**
  - Correct Count
  - Wrong Count
- **Word Groups:**
  - Display associated groups as clickable tags.
  - Clicking a tag navigates to the respective Group Details page.

### API Endpoints
- `GET /api/words/:id`

---

## 7. Word Groups Index (`/groups`)

### Purpose
- List all word groups available in the database.

### Components
- **Paginated Group List**
  - Table columns:
    - Group Name
    - Word Count
  - Clicking on a group name navigates to its details page.

### API Endpoints
- `GET /api/groups`

---

## 8. Group Details (`/groups/:id`)

### Purpose
- Provide detailed information about a specific group.

### Components
- **Group Information:**
  - Group Name.
  - Total Word Count.
- **Words in Group:**
  - Paginated list (reuse the Words Index component).
- **Study Sessions:**
  - Paginated list (reuse the Study Sessions Index component).

### API Endpoints
- `GET /api/groups/:id` (for group name and statistics)
- `GET /api/groups/:id/words`
- `GET /api/groups/:id/study_sessions`

---

## 9. Study Sessions Index (`/study_sessions`)

### Purpose
- Display all study sessions recorded in the database.

### Components
- **Paginated Study Session List**
  - Table columns:
    - ID
    - Activity Name
    - Group Name
    - Start Time
    - End Time
    - Number of Review Items
  - Clicking on a session ID navigates to its detailed view.

### API Endpoints
- `GET /api/study_sessions`

---

## 10. Study Session Details (`/study_sessions/:id`)

### Purpose
- Show detailed information for a specific study session.

### Components
- **Session Details:**
  - Activity Name.
  - Group Name.
  - Start Time.
  - End Time.
  - Number of Review Items.
- **Word Review Items:**
  - Paginated list of words (reuse the Words Index component).

### API Endpoints
- `GET /api/study_sessions/:id`
- `GET /api/study_sessions/:id/words`

---

## 11. Settings (`/settings`)

### Purpose
- Allow users to configure study portal settings.

### Components
- **Theme Selection:**
  - Options: Light, Dark, System Default.
- **Reset History Button:**
  - Deletes all study sessions and word review items.
- **Full Reset Button:**
  - Drops all tables and recreates them with seed data.

### API Endpoints
- `POST /api/reset_history`
- `POST /api/full_reset`
