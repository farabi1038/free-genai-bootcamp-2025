from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional, Any
import uvicorn
import json
import os
import sys
import sqlite3
from pathlib import Path
import logging
import time
import uuid
import asyncio
import traceback

# Add parent directory to path to allow imports from other project modules
sys.path.append(str(Path(__file__).parent.parent))

# Import utility modules
from utils.youtube import extract_video_id, get_video_info, get_youtube_transcript, download_youtube_audio, get_or_download_transcript
from utils.whisper_asr import transcribe_audio
from utils.ollama_integration import generate_exercises, check_answer, extract_natural_questions_from_transcript
from utils.tts import text_to_speech

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Japanese Listening Practice API",
    description="Backend API for the Japanese Listening Practice application",
    version="0.1.0"
)

# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directory paths
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "database.sqlite"
AUDIO_DIR = DATA_DIR / "audio"
TRANSCRIPT_DIR = DATA_DIR / "transcripts"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)
TRANSCRIPT_DIR.mkdir(exist_ok=True)

# Database setup
def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    """Initialize the database with necessary tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Videos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id TEXT PRIMARY KEY,
        youtube_id TEXT NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        duration INTEGER,
        language TEXT,
        difficulty TEXT,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Transcripts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transcripts (
        id TEXT PRIMARY KEY,
        video_id TEXT NOT NULL,
        content TEXT NOT NULL,
        language TEXT NOT NULL,
        is_machine_generated BOOLEAN,
        FOREIGN KEY (video_id) REFERENCES videos (id)
    )
    ''')
    
    # Exercises table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        id TEXT PRIMARY KEY,
        video_id TEXT NOT NULL,
        segment_start REAL,
        segment_end REAL,
        question TEXT NOT NULL,
        type TEXT NOT NULL,
        options TEXT,
        correct_answer TEXT,
        difficulty TEXT,
        FOREIGN KEY (video_id) REFERENCES videos (id)
    )
    ''')
    
    # User progress table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_progress (
        id TEXT PRIMARY KEY,
        exercise_id TEXT NOT NULL,
        user_answer TEXT,
        is_correct BOOLEAN,
        attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (exercise_id) REFERENCES exercises (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    logger.info("Database initialized successfully")

# Initialize database on startup
initialize_db()

# Pydantic models for API requests and responses
class VideoBase(BaseModel):
    youtube_id: str
    title: str
    url: HttpUrl
    duration: Optional[int] = None
    language: Optional[str] = "ja"
    difficulty: Optional[str] = "intermediate"

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: str
    added_date: str

class ExerciseBase(BaseModel):
    video_id: str
    segment_start: Optional[float] = None
    segment_end: Optional[float] = None
    question: str
    type: str  # multiple_choice, fill_in, free_form
    options: Optional[List[str]] = None
    correct_answer: str
    difficulty: Optional[str] = "intermediate"

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: str

class AnswerSubmission(BaseModel):
    exercise_id: str
    answer: str

class AnswerCheck(BaseModel):
    correct: bool
    feedback: str

class TranscriptRequest(BaseModel):
    youtube_url: HttpUrl

class HealthCheck(BaseModel):
    status: str
    version: str

# API Routes
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint to verify API is running"""
    return {
        "status": "OK",
        "version": "0.1.0"
    }

@app.get("/videos", response_model=List[Video])
async def get_videos(
    difficulty: Optional[str] = None,
    youtube_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get a list of available videos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM videos"
    params = []
    where_clauses = []
    
    if difficulty:
        where_clauses.append("difficulty = ?")
        params.append(difficulty)
    
    if youtube_id:
        where_clauses.append("youtube_id = ?")
        params.append(youtube_id)
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " ORDER BY added_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    videos = []
    for row in rows:
        videos.append({
            "id": row["id"],
            "youtube_id": row["youtube_id"],
            "title": row["title"],
            "url": row["url"],
            "duration": row["duration"],
            "language": row["language"],
            "difficulty": row["difficulty"],
            "added_date": row["added_date"]
        })
    
    return videos

@app.post("/videos", response_model=Video)
async def add_video(video: VideoCreate, background_tasks: BackgroundTasks):
    """Add a new video to the database and process it in the background"""
    video_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO videos (id, youtube_id, title, url, duration, language, difficulty) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (video_id, video.youtube_id, video.title, str(video.url), video.duration, video.language, video.difficulty)
    )
    
    conn.commit()
    conn.close()
    
    # Add background task to process the video (download audio, generate transcript, create exercises)
    background_tasks.add_task(process_video, video_id, str(video.url))
    
    return {
        "id": video_id,
        **video.dict(),
        "added_date": time.strftime('%Y-%m-%d %H:%M:%S')
    }

@app.get("/videos/{video_id}", response_model=Video)
async def get_video(video_id: str):
    """Get details of a specific video"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {
        "id": row["id"],
        "youtube_id": row["youtube_id"],
        "title": row["title"],
        "url": row["url"],
        "duration": row["duration"],
        "language": row["language"],
        "difficulty": row["difficulty"],
        "added_date": row["added_date"]
    }

@app.get("/exercises/{video_id}", response_model=List[Exercise])
async def get_exercises(video_id: str):
    """Get exercises for a specific video"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM exercises WHERE video_id = ?", (video_id,))
    rows = cursor.fetchall()
    conn.close()
    
    # For demo purposes, if no exercises found, return sample exercises
    if not rows:
        return get_sample_exercises(video_id)
    
    exercises = []
    for row in rows:
        options = json.loads(row["options"]) if row["options"] else None
        exercises.append({
            "id": row["id"],
            "video_id": row["video_id"],
            "segment_start": row["segment_start"],
            "segment_end": row["segment_end"],
            "question": row["question"],
            "type": row["type"],
            "options": options,
            "correct_answer": row["correct_answer"],
            "difficulty": row["difficulty"]
        })
    
    return exercises

def get_sample_exercises(video_id: str) -> List[Dict[str, Any]]:
    """Return sample exercises for demo purposes"""
    return [
        {
            "id": f"ex1_{video_id}",
            "video_id": video_id,
            "segment_start": 10.5,
            "segment_end": 20.2,
            "question": "What is the main topic of the conversation?",
            "type": "multiple_choice",
            "options": ["Weather", "Food", "Travel", "Work"],
            "correct_answer": "Travel",
            "difficulty": "beginner"
        },
        {
            "id": f"ex2_{video_id}",
            "video_id": video_id,
            "segment_start": 25.0,
            "segment_end": 35.5,
            "question": "Complete the sentence: '明日は天気が＿＿ですね。'",
            "type": "fill_in",
            "options": None,
            "correct_answer": "いい",
            "difficulty": "beginner"
        },
        {
            "id": f"ex3_{video_id}",
            "video_id": video_id,
            "segment_start": 40.2,
            "segment_end": 55.0,
            "question": "Summarize the main points of the conversation in English.",
            "type": "free_form",
            "options": None,
            "correct_answer": "The speakers are discussing their travel plans to Kyoto next weekend. They talk about which landmarks they want to visit and where they will stay.",
            "difficulty": "intermediate"
        }
    ]

@app.post("/check_answer", response_model=AnswerCheck)
async def check_answer(submission: AnswerSubmission):
    """Check the user's answer against the correct answer"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM exercises WHERE id = ?", (submission.exercise_id,))
    exercise = cursor.fetchone()
    
    if not exercise:
        # For demo purposes, simulate checking with sample exercises
        return check_sample_answer(submission.exercise_id, submission.answer)
    
    is_correct = False
    feedback = "Incorrect answer. Try again!"
    
    # Simple check - in a real app, we'd use more sophisticated checking
    # including AI verification for free-form answers
    if exercise["type"] == "multiple_choice" or exercise["type"] == "fill_in":
        is_correct = submission.answer.strip().lower() == exercise["correct_answer"].strip().lower()
        if is_correct:
            feedback = "Correct! Good job!"
    else:  # free_form
        # In a real app, we'd use an LLM to evaluate the answer
        # For now, check if answer contains key words from the correct answer
        key_words = set(exercise["correct_answer"].lower().split())
        answer_words = set(submission.answer.lower().split())
        
        common_words = key_words.intersection(answer_words)
        similarity = len(common_words) / len(key_words) if key_words else 0
        
        is_correct = similarity > 0.5
        if is_correct:
            feedback = "Good answer! You captured the main points."
        else:
            feedback = f"Your answer is incomplete. Consider including more key details about {', '.join(list(key_words)[:3])}."
    
    # Record this attempt in the database
    progress_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO user_progress (id, exercise_id, user_answer, is_correct) VALUES (?, ?, ?, ?)",
        (progress_id, submission.exercise_id, submission.answer, is_correct)
    )
    
    conn.commit()
    conn.close()
    
    return {
        "correct": is_correct,
        "feedback": feedback
    }

def check_sample_answer(exercise_id: str, answer: str) -> Dict[str, Any]:
    """Check answers against sample exercises for demo purposes"""
    # Check first digit of exercise ID to determine correct response
    ex_num = exercise_id.split('_')[0]
    
    if ex_num == "ex1":
        is_correct = answer.strip().lower() == "travel"
        feedback = "Correct! The conversation is about travel plans." if is_correct else "Incorrect. The conversation is about travel plans."
    elif ex_num == "ex2":
        is_correct = answer.strip().lower() == "いい" or answer.strip().lower() == "ii"
        feedback = "Correct! The complete sentence is '明日は天気がいいですね。' (Tomorrow's weather will be nice.)" if is_correct else "Incorrect. The answer is 'いい' (good/nice)."
    else:  # ex3
        # For free-form, check if key words are present
        key_words = ["kyoto", "travel", "weekend", "landmarks", "visit"]
        answer_words = set(answer.lower().split())
        
        common_words = [word for word in key_words if word in answer_words]
        is_correct = len(common_words) >= 2
        
        if is_correct:
            feedback = "Good answer! You captured some key points of the conversation."
        else:
            feedback = "Your answer is incomplete. The conversation is about travel plans to Kyoto."
    
    return {
        "correct": is_correct,
        "feedback": feedback
    }

@app.post("/transcript", status_code=202)
async def get_transcript(request: TranscriptRequest, background_tasks: BackgroundTasks):
    """
    Request a transcript for a YouTube video. 
    This will be processed asynchronously in the background.
    """
    # Extract the video ID from URL
    video_id = extract_video_id(str(request.youtube_url))
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    # Check if video exists in the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM videos WHERE youtube_id = ?", (video_id,))
    row = cursor.fetchone()
    conn.close()
    
    # If video exists, process it
    if row:
        video_db_id = row["id"]
        background_tasks.add_task(process_video, video_db_id, str(request.youtube_url))
        return {"message": f"Processing transcript for video {video_id}", "video_id": video_db_id}
    
    # If video doesn't exist, add it first
    try:
        # Get video info
        video_info = await get_video_info(str(request.youtube_url))
        
        # Create video in database
        video_db_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO videos (id, youtube_id, title, url, duration, language, difficulty) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (video_db_id, video_id, video_info.get("title", f"YouTube Video {video_id}"), 
             str(request.youtube_url), video_info.get("duration", 0), "ja", "intermediate")
        )
        conn.commit()
        conn.close()
        
        # Process the video
        background_tasks.add_task(process_video, video_db_id, str(request.youtube_url))
        
        return {"message": f"Added and processing transcript for video {video_id}", "video_id": video_db_id}
    
    except Exception as e:
        logger.error(f"Error processing transcript request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

async def process_video(video_id: str, youtube_url: str):
    """Process a video: download audio, generate transcript, create exercises"""
    try:
        logger.info(f"Processing video {video_id} from URL {youtube_url}")
        
        # 1. Download the audio
        audio_path = await download_youtube_audio(youtube_url, AUDIO_DIR)
        logger.info(f"Downloaded audio to {audio_path}")
        
        # 2. Get or create transcript
        transcript = await get_or_download_transcript(youtube_url, TRANSCRIPT_DIR)
        
        # If no transcript available via YouTube API, generate with Whisper
        if not transcript:
            logger.info(f"No transcript available via YouTube API, generating with Whisper")
            transcript_result = await transcribe_audio(audio_path)
            transcript = transcript_result["segments"]
            
            # Save the transcript
            transcript_id = str(uuid.uuid4())
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO transcripts (id, video_id, content, language, is_machine_generated) VALUES (?, ?, ?, ?, ?)",
                (transcript_id, video_id, json.dumps(transcript), "ja", True)
            )
            conn.commit()
            conn.close()
        
        # 3. Try to extract natural questions from the transcript
        natural_exercises = await extract_natural_questions_from_transcript(transcript, max_questions=5)
        
        # If we found natural questions, use those
        if natural_exercises and len(natural_exercises) > 0:
            logger.info(f"Using {len(natural_exercises)} natural questions extracted from transcript")
            exercises = natural_exercises
        else:
            # 4. Fall back to generating exercises with our regular approach
            logger.info("No natural questions found, generating exercises instead")
            exercises = await generate_exercises(transcript, num_exercises=5)
        
        # 5. Save exercises to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for exercise in exercises:
            exercise_id = exercise.get("id", str(uuid.uuid4()))
            options_json = json.dumps(exercise.get("options")) if exercise.get("options") else None
            
            # Get context fields if present
            context_before = exercise.get("context_before", "")
            context_after = exercise.get("context_after", "")
            question_type = exercise.get("question_type", "generated")
            
            # Adjust the question field
            question = exercise.get("question_text", exercise.get("question", ""))
            
            cursor.execute(
                """
                INSERT INTO exercises (
                    id, video_id, type, segment_start, segment_end, 
                    question, options, correct_answer, context_before, context_after, question_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exercise_id, video_id, exercise.get("type", "multiple_choice"),
                    exercise.get("segment_start"), exercise.get("segment_end"),
                    question, options_json, exercise.get("correct_answer", 0),
                    context_before, context_after, question_type
                )
            )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully processed video {video_id} with {len(exercises)} exercises")
        return exercises
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        logger.error(traceback.format_exc())
        return []

# Run the server when script is executed directly
if __name__ == "__main__":
    # Initialize the database first
    initialize_db()
    logger.info("Database initialized successfully")
    
    # Check if port is specified in environment
    port = int(os.environ.get("PORT", 8000))
    
    # Disable auto-reload to prevent memory issues with directory scanning
    reload_enabled = os.environ.get("ENABLE_RELOAD", "false").lower() == "true"
    
    # Update the config file with the port we're using
    try:
        config_path = Path(__file__).parent.parent / "config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update the port in the config
            if config.get("backend_port") != port:
                config["backend_port"] = port
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                logger.info(f"Updated configuration with port {port}")
    except Exception as e:
        logger.warning(f"Could not update config file: {str(e)}")
    
    logger.info(f"Starting FastAPI server on port {port}, reload={'enabled' if reload_enabled else 'disabled'}")
    
    # Determine the correct import path based on how the script is run
    import inspect
    current_file = inspect.getfile(inspect.currentframe())
    if os.path.basename(current_file) == "main.py" and os.path.dirname(current_file).endswith("backend"):
        # Running directly from the backend directory
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload_enabled)
    else:
        # Running as a module
        uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=reload_enabled) 