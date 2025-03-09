import streamlit as st
import requests
import os
import sys
import json
import time
import base64
from pathlib import Path
import re
import asyncio
import threading
import gc
import socket
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Force garbage collection to free memory
gc.collect()

# Add parent directory to path to allow imports from other project directories
sys.path.append(str(Path(__file__).parent.parent))

# Set page configuration before any other Streamlit commands
st.set_page_config(
    page_title="Japanese Listening Practice",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Show a loading message while we initialize
startup_placeholder = st.empty()
startup_placeholder.info("Initializing application... Please wait.")

# Load configuration to get the backend port
def load_config():
    config_path = Path(__file__).parent.parent / "config.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        return {"backend_port": 8004}  # Default fallback

# Function to check if a port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Function to find the backend server
def find_backend_server():
    # First try the configured port
    config = load_config()
    configured_port = config.get("backend_port", 8004)
    
    # Try the configured port first
    if is_port_in_use(configured_port):
        try:
            response = requests.get(f"http://localhost:{configured_port}/health", timeout=2)
            if response.status_code == 200:
                return configured_port
        except:
            pass
    
    # If that fails, try common ports
    common_ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010]
    for port in common_ports:
        if port == configured_port:
            continue  # Already tried this one
        
        if is_port_in_use(port):
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    # Update the config with the found port
                    config["backend_port"] = port
                    with open(Path(__file__).parent.parent / "config.json", 'w') as f:
                        json.dump(config, f, indent=2)
                    return port
            except:
                pass
    
    # If we couldn't find a working backend, return the configured port
    return configured_port

# Find the backend server
backend_port = find_backend_server()
BACKEND_URL = f"http://localhost:{backend_port}"

# Check if backend is running
backend_running = False
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if response.status_code == 200:
        backend_running = True
        st.success(f"Connected to backend server on port {backend_port}")
    else:
        st.warning(f"Backend server returned status code: {response.status_code}")
except Exception as e:
    st.error(f"Backend server not available: {str(e)}")
    st.info(f"Please make sure the backend is running on port {backend_port} (python run.py)")
    st.info("If you've started the backend on a different port, please update the config.json file.")

# App states
APP_STATES = {
    "HOME": "home",
    "VIDEO_SELECTION": "video_selection",
    "PRACTICE": "practice", 
    "REVIEW": "review",
    "PROCESSING_VIDEO": "processing_video",
    "AUDIO_EXERCISE": "audio_exercise", 
    "AUDIO_EXERCISE_REVIEW": "audio_exercise_review"
}

# Initialize session state
if "app_state" not in st.session_state:
    st.session_state.app_state = APP_STATES["HOME"]
    
if "current_video" not in st.session_state:
    st.session_state.current_video = None
    
if "exercises" not in st.session_state:
    st.session_state.exercises = []
    
if "answers" not in st.session_state:
    st.session_state.answers = {}
    
if "results" not in st.session_state:
    st.session_state.results = {}

if "custom_video_url" not in st.session_state:
    st.session_state.custom_video_url = ""

if "custom_video_id" not in st.session_state:
    st.session_state.custom_video_id = None

if "audio_exercise" not in st.session_state:
    st.session_state.audio_exercise = None
    
if "audio_exercise_id" not in st.session_state:
    st.session_state.audio_exercise_id = None

if "audio_answers" not in st.session_state:
    st.session_state.audio_answers = {}

# Keep track of dependency loading status manually
if "dependencies_loaded" not in st.session_state:
    st.session_state.dependencies_loaded = {
        "audio_generator": False,
        "tts_engine": False
    }

# Remove the cache_resource decorator and use simple functions instead
def get_audio_exercise_generator():
    """Get the audio exercise generator"""
    if "audio_generator" not in st.session_state:
        try:
            from utils.audio_exercise_generator import AudioExerciseGenerator
            st.session_state.audio_generator = AudioExerciseGenerator()
            st.session_state.dependencies_loaded["audio_generator"] = True
            return st.session_state.audio_generator
        except Exception as e:
            st.error(f"Failed to load audio exercise generator: {str(e)}")
            st.session_state.dependencies_loaded["audio_generator"] = False
            return None
    return st.session_state.audio_generator

def get_tts_engine():
    """Get the TTS engine"""
    if "tts_engine" not in st.session_state:
        try:
            from utils.japanese_tts import JapaneseTTS
            st.session_state.tts_engine = JapaneseTTS()
            st.session_state.dependencies_loaded["tts_engine"] = True
            return st.session_state.tts_engine
        except Exception as e:
            st.error(f"Failed to load TTS engine: {str(e)}")
            st.session_state.dependencies_loaded["tts_engine"] = False
            return None
    return st.session_state.tts_engine

# Helper functions for audio playback
def get_audio_player(audio_path, autoplay=False):
    """Create an HTML audio player for the given audio file"""
    if not audio_path or not os.path.exists(audio_path):
        return "Audio file not found"
    
    # Check the file size to avoid loading huge files
    try:
        file_size = os.path.getsize(audio_path) / (1024 * 1024)  # Size in MB
        if file_size > 10:  # Limit to 10 MB
            return f"Audio file is too large: {file_size:.2f} MB (limit is 10 MB)"
    except:
        return "Error checking audio file size"
    
    try:
        audio_format = audio_path.split(".")[-1].lower()
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        autoplay_attr = 'autoplay' if autoplay else ''
        
        return f'<audio controls {autoplay_attr}><source src="data:audio/{audio_format};base64,{audio_base64}" type="audio/{audio_format}"></audio>'
    except Exception as e:
        logger.error(f"Error creating audio player: {str(e)}")
        return f"Error loading audio: {str(e)}"

# State transition functions
def go_to_home():
    st.session_state.app_state = APP_STATES["HOME"]

def go_to_video_selection():
    st.session_state.app_state = APP_STATES["VIDEO_SELECTION"]

def go_to_practice(video_id):
    st.session_state.current_video = video_id
    st.session_state.app_state = APP_STATES["PRACTICE"]
    # Load exercises for this video
    load_exercises(video_id)

def go_to_review():
    st.session_state.app_state = APP_STATES["REVIEW"]
    # Calculate results
    calculate_results()

def go_to_processing_video(video_url):
    """Transition to processing a custom video URL"""
    st.session_state.custom_video_url = video_url
    st.session_state.app_state = APP_STATES["PROCESSING_VIDEO"]
    process_custom_video(video_url)

def go_to_audio_exercise():
    """Transition to the audio exercise generator"""
    st.session_state.app_state = APP_STATES["AUDIO_EXERCISE"]
    
    # Only clear if we're not coming from generate_audio_exercise
    # Don't clear any exercises if we already have one generated
    if 'clear_exercise' in st.session_state and st.session_state.clear_exercise:
        # Clear any previous answers
        st.session_state.audio_answers = {}
        # Clear the current exercise to show the selection form again
        st.session_state.audio_exercise = None
        st.session_state.audio_exercise_id = None
        st.session_state.clear_exercise = False
    
    # Set a flag if we were redirected from the generate function
    if 'from_generate' in st.session_state and st.session_state.from_generate:
        st.session_state.from_generate = False

def go_to_audio_exercise_review():
    """Transition to the audio exercise review screen"""
    st.session_state.app_state = APP_STATES["AUDIO_EXERCISE_REVIEW"]
    # Add a rerun to force the state change
    st.rerun()

def load_audio_exercise(exercise_id):
    """Load an audio exercise by ID"""
    if exercise_id:
        audio_generator = get_audio_exercise_generator()
        if audio_generator is None:
            st.error("Audio exercise generator is not available")
            return
        
        exercise = audio_generator.get_exercise_by_id(exercise_id)
        if exercise:
            # Verify audio file exists before loading
            has_audio = False
            if exercise.get('main_audio') and os.path.exists(exercise.get('main_audio', '')):
                has_audio = True
                
            if not has_audio:
                st.error("Cannot load exercise: Audio file is missing")
                st.warning("Please generate a new exercise with audio")
                return
                
            # Load the exercise since audio exists
            st.session_state.audio_exercise = exercise
            st.session_state.audio_exercise_id = exercise_id
            go_to_audio_exercise()
        else:
            st.error(f"Could not load exercise with ID: {exercise_id}")

async def generate_audio_exercise(topic=None, jlpt_level="N4", num_questions=1):
    """Generate a new audio exercise with the specified JLPT level"""
    # Get the audio exercise generator
    audio_generator = get_audio_exercise_generator()
    if audio_generator is None:
        st.error("Audio exercise generator is not available")
        return None
    
    try:
        # Set JLPT level in the generator
        audio_generator.jlpt_level = jlpt_level
        st.info(f"Generating exercise for JLPT level: {jlpt_level}")
        
        # Generate the exercise with audio
        with st.spinner(f"Generating {jlpt_level} exercise..."):
            exercise = await audio_generator.generate_listening_exercise(
                topic=topic, 
                num_questions=num_questions,
                with_audio=True,
                jlpt_level=jlpt_level  # Explicitly pass the JLPT level
            )
        
        if exercise:
            # Check if questions are present in the exercise
            has_questions = 'questions' in exercise and exercise['questions']
            if not has_questions:
                st.warning("No questions found in the generated exercise. Adding default questions.")
                exercise['questions'] = [{
                    "question": "この会話は何についてですか？ (What is this conversation about?)",
                    "options": ["勉強について (About studying)", 
                               "趣味について (About hobbies)", 
                               "仕事について (About work)", 
                               "天気について (About the weather)"]
                }]
            
            # Save to session state
            st.session_state.audio_exercise = exercise
            st.session_state.audio_exercise_id = exercise["id"]
            
            # Show debug info
            st.info(f"Exercise has {len(exercise.get('questions', []))} questions")
            
            # Success message (shown once)
            st.success(f"{jlpt_level} exercise generated successfully!")
            
            # Set a flag to indicate we're coming from the generate function
            st.session_state.from_generate = True
            
            # Force UI update by redirecting to the exercise page
            st.experimental_rerun()
            return exercise
        else:
            st.error("Failed to generate exercise")
            return None
    except Exception as e:
        st.error(f"Error generating audio exercise: {str(e)}")
        return None

def extract_youtube_id(url):
    """Extract YouTube video ID from a URL"""
    # Regular expression to match YouTube video IDs in various URL formats
    patterns = [
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def process_custom_video(video_url):
    """Process a custom YouTube video URL"""
    try:
        # Extract YouTube ID
        youtube_id = extract_youtube_id(video_url)
        
        if not youtube_id:
            st.error("Invalid YouTube URL. Please provide a valid YouTube video URL.")
            return
        
        # Check if video already exists in the database
        response = requests.get(f"{BACKEND_URL}/videos", params={"youtube_id": youtube_id})
        
        if response.status_code == 200 and response.json():
            # Video already exists, use the existing one
            video = response.json()[0]
            st.session_state.custom_video_id = video["id"]
            go_to_practice(video["id"])
            return
        
        # Add new video
        video_info = {
            "youtube_id": youtube_id,
            "title": f"Custom Video ({youtube_id})",  # We'll update this with actual title later
            "url": video_url,
            "language": "ja"
        }
        
        # Send request to backend to add video
        response = requests.post(f"{BACKEND_URL}/videos", json=video_info)
        
        if response.status_code == 200:
            video = response.json()
            st.session_state.custom_video_id = video["id"]
            
            # Request transcript processing
            transcript_request = {
                "youtube_url": video_url
            }
            transcript_response = requests.post(f"{BACKEND_URL}/transcript", json=transcript_request)
            
            if transcript_response.status_code in [200, 202]:
                # Go to practice with the new video
                go_to_practice(video["id"])
            else:
                st.error(f"Failed to process transcript: {transcript_response.text}")
        else:
            st.error(f"Failed to add video: {response.text}")
            
    except Exception as e:
        st.error(f"Error processing video: {str(e)}")

def load_exercises(video_id):
    """Load exercises for a specific video from the backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/exercises/{video_id}")
        if response.status_code == 200:
            st.session_state.exercises = response.json()
        else:
            st.error(f"Failed to load exercises: {response.text}")
            st.session_state.exercises = []
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        st.session_state.exercises = []

def submit_answer(exercise_id, answer):
    """Store user's answer"""
    st.session_state.answers[exercise_id] = answer

def submit_audio_answer(question_number, answer):
    """Store user's answer for audio exercise"""
    # Initialize the answers dictionary if it doesn't exist
    if 'audio_answers' not in st.session_state:
        st.session_state.audio_answers = {}
    
    # Always store the question number as a string to ensure consistent access
    st.session_state.audio_answers[str(question_number)] = answer

def calculate_results():
    """Calculate results based on user answers"""
    results = {}
    for exercise in st.session_state.exercises:
        ex_id = exercise["id"]
        if ex_id in st.session_state.answers:
            # In a real app, we'd send the answer to the backend for evaluation
            # Here we're simulating that
            try:
                response = requests.post(
                    f"{BACKEND_URL}/check_answer", 
                    json={
                        "exercise_id": ex_id,
                        "answer": st.session_state.answers[ex_id]
                    }
                )
                if response.status_code == 200:
                    result = response.json()
                    results[ex_id] = result
                else:
                    results[ex_id] = {"correct": False, "feedback": "Error processing answer"}
            except Exception as e:
                results[ex_id] = {"correct": False, "feedback": f"Connection error: {str(e)}"}
    
    st.session_state.results = results

def check_audio_answers():
    """Check user answers for the audio exercise"""
    if 'audio_exercise' not in st.session_state or not st.session_state.audio_exercise:
        return {}
    
    # Get the exercise
    exercise = st.session_state.audio_exercise
    
    # Get user answers
    user_answers = st.session_state.get('audio_answers', {})
    
    # Results will store the feedback for each question
    results = {}
    
    # Check each question
    if 'questions' in exercise:
        for i, q in enumerate(exercise['questions']):
            question_num = i + 1
            question_key = str(question_num)
            
            # Initialize result for this question
            results[question_key] = {
                "correct": False,
                "feedback": "No answer provided"
            }
            
            # Check if user answered this question
            if question_key in user_answers:
                user_answer = user_answers[question_key]
                
                # Check if this is a multiple choice question with a correct answer
                if 'options' in q and 'correct_answer' in q:
                    correct_index = q['correct_answer']
                    # Get the correct option text
                    if 0 <= correct_index < len(q['options']):
                        correct_answer = q['options'][correct_index]
                        
                        # Compare answers
                        if user_answer == correct_answer:
                            results[question_key] = {
                                "correct": True,
                                "feedback": "Correct! Your answer matches exactly."
                            }
                        else:
                            results[question_key] = {
                                "correct": False,
                                "feedback": f"Incorrect. The correct answer is: {correct_answer}"
                            }
                    else:
                        results[question_key] = {
                            "correct": False,
                            "feedback": "Invalid question format - couldn't determine correct answer"
                        }
                # Without specified correct answer, just mark as reviewed
                else:
                    results[question_key] = {
                        "correct": False,  # We can't determine correctness
                        "feedback": "Answer recorded but no correct answer specified for comparison"
                    }
            
    return results

# UI Components for different states
def render_home():
    st.title("Japanese Listening Practice")
    
    st.markdown("""
    Welcome to the Japanese Listening Practice app! This application will help you improve your Japanese 
    listening comprehension skills using authentic content from YouTube or AI-generated JLPT-style exercises.
    
    ## Features
    
    - Practice with real Japanese content from YouTube
    - Generate JLPT-style listening exercises with audio
    - Get automatic transcriptions and translations
    - Answer comprehension questions
    - Track your progress over time
    
    ## How to Use
    
    1. Choose the type of practice you want
    2. Listen to the audio and try to understand
    3. Answer the comprehension questions
    4. Review your results and learn from mistakes
    """)
    
    st.write("### Choose Practice Type")
    col1, col2 = st.columns(2)
    with col1:
        st.button("YouTube Videos", on_click=go_to_video_selection, use_container_width=True)
    
    with col2:
        st.button("JLPT-Style Audio Exercises", on_click=go_to_audio_exercise, use_container_width=True)

def render_video_selection():
    st.title("Select a Video")
    
    # Custom Video URL Input
    with st.expander("Add your own YouTube video", expanded=True):
        st.write("Enter a YouTube URL to practice with a specific video:")
        youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Add Video", use_container_width=True):
                if youtube_url:
                    go_to_processing_video(youtube_url)
                else:
                    st.error("Please enter a valid YouTube URL")
    
    # Search functionality
    with st.expander("Search for videos", expanded=True):
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_query = st.text_input("Search for Japanese videos", placeholder="Enter keywords...")
        with search_col2:
            search_button = st.button("Search", use_container_width=True)
    
    # Simulated video results
    # In a real app, we'd fetch this from the backend
    sample_videos = [
        {"id": "video1", "title": "Basic Japanese Conversation", "duration": "5:30", "level": "Beginner"},
        {"id": "video2", "title": "Intermediate Japanese Listening", "duration": "10:15", "level": "Intermediate"},
        {"id": "video3", "title": "Advanced Japanese News Segment", "duration": "8:45", "level": "Advanced"},
    ]
    
    st.subheader("Available Videos")
    
    # Video card display
    for video in sample_videos:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{video['title']}**")
                st.write(f"Duration: {video['duration']} | Level: {video['level']}")
            with col2:
                st.button("Preview", key=f"preview_{video['id']}", disabled=True)  # Future feature
            with col3:
                st.button("Practice", key=f"practice_{video['id']}", on_click=go_to_practice, args=(video['id'],))
            
            st.divider()
    
    # Back button
    st.button("Back to Home", on_click=go_to_home)

def render_processing_video():
    """Render the processing state for a custom video"""
    st.title("Processing Video")
    
    video_url = st.session_state.custom_video_url
    video_id = extract_youtube_id(video_url) or "Unknown"
    
    st.info(f"Processing video: {video_url}")
    
    st.markdown(f"""
    ### Video Details
    - **URL**: {video_url}
    - **YouTube ID**: {video_id}
    
    ### Processing Steps
    - ✅ Extracting video information
    - ⏳ Downloading audio
    - ⏳ Generating transcript
    - ⏳ Creating exercises
    
    This process may take a few minutes depending on the video length.
    Please wait while we prepare your practice content...
    """)
    
    # Show spinner while processing
    with st.spinner("Processing video..."):
        st.empty()
    
    # Cancel button
    if st.button("Cancel and go back", use_container_width=True):
        go_to_video_selection()

def render_practice():
    st.title("Listening Practice")
    
    if not st.session_state.current_video or not st.session_state.exercises:
        st.warning("No exercises available. Please select a video first.")
        st.button("Back to Video Selection", on_click=go_to_video_selection)
        return
    
    # Video player (simulated)
    st.subheader("Video")
    st.info("Video player would be embedded here in the full implementation")
    
    # Exercises
    st.subheader("Comprehension Exercises")
    
    exercise_form = st.form("exercise_form")
    with exercise_form:
        for i, exercise in enumerate(st.session_state.exercises):
            st.write(f"**Question {i+1}:** {exercise['question']}")
            
            # Different types of exercises
            if exercise['type'] == 'multiple_choice':
                options = exercise['options']
                answer = st.radio(
                    f"Select your answer for question {i+1}:",
                    options,
                    key=f"radio_{exercise['id']}"
                )
            elif exercise['type'] == 'fill_in':
                answer = st.text_input(
                    f"Your answer for question {i+1}:",
                    key=f"text_{exercise['id']}"
                )
            else:  # Free form
                answer = st.text_area(
                    f"Your answer for question {i+1}:",
                    key=f"textarea_{exercise['id']}"
                )
            
            # Store answer in session state
            submit_answer(exercise['id'], answer)
            
            st.divider()
        
        submit_button = st.form_submit_button("Submit Answers")
        if submit_button:
            go_to_review()
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        st.button("Back to Video Selection", on_click=go_to_video_selection)

def render_review():
    st.title("Review Your Answers")
    
    if not st.session_state.exercises or not st.session_state.results:
        st.warning("No exercises or results available.")
        st.button("Back to Home", on_click=go_to_home)
        return
    
    total_correct = sum(1 for result in st.session_state.results.values() if result.get("correct", False))
    total_questions = len(st.session_state.exercises)
    
    # Show score
    st.subheader("Your Score")
    score_percent = (total_correct / total_questions) * 100 if total_questions > 0 else 0
    st.progress(score_percent / 100)
    st.write(f"You got **{total_correct}** out of **{total_questions}** questions correct ({score_percent:.1f}%)")
    
    # Review each question
    st.subheader("Review Questions")
    
    for i, exercise in enumerate(st.session_state.exercises):
        ex_id = exercise["id"]
        result = st.session_state.results.get(ex_id, {"correct": False, "feedback": "No answer provided"})
        
        with st.expander(f"Question {i+1}: {exercise['question']}", expanded=True):
            st.write("**Your answer:**")
            if ex_id in st.session_state.answers:
                st.write(st.session_state.answers[ex_id])
            else:
                st.write("No answer provided")
            
            st.write("**Correct answer:**")
            st.write(exercise.get("correct_answer", "Not available"))
            
            st.write("**Feedback:**")
            if result.get("correct", False):
                st.success(result.get("feedback", "Correct!"))
            else:
                st.error(result.get("feedback", "Incorrect"))
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("Try Again", on_click=go_to_practice, args=(st.session_state.current_video,))
    with col2:
        st.button("Choose Another Video", on_click=go_to_video_selection)
    with col3:
        st.button("Back to Home", on_click=go_to_home)

def render_audio_exercise():
    st.title("JLPT-Style Listening Exercise")
    
    # Clear the startup placeholder
    startup_placeholder.empty()
    
    # Check if backend is running
    if not backend_running:
        st.error("Backend server is not running")
        st.info("Please run the backend server using: python run.py")
        if st.button("Go to Home"):
            go_to_home()
        return
    
    # Initialize the audio exercise generator if it's not loaded yet
    audio_generator = get_audio_exercise_generator()
    if audio_generator is None:
        st.error("Failed to initialize the audio exercise generator")
        st.info("Check the error messages above and try restarting the application")
        if st.button("Go to Home"):
            go_to_home()
        return
    
    # Generate a new exercise or see stored ones
    if not st.session_state.get('audio_exercise'):
        # Display form to create new exercise
        st.subheader("Generate a New Exercise")
        
        with st.form("generate_exercise_form"):
            # Select JLPT level
            st.subheader("Select JLPT Level")
            jlpt_level = st.selectbox(
                "Choose the difficulty level for your exercise:",
                ["N5", "N4", "N3", "N2", "N1"],
                index=1,
                help="N5 is the easiest, N1 is the most difficult"
            )
            
            # Add description of the selected level
            jlpt_descriptions = {
                "N5": "Basic Japanese - Beginner level with simple vocabulary and grammar",
                "N4": "Elementary Japanese - Basic daily conversations and simple reading",
                "N3": "Intermediate Japanese - More complex grammar and vocabulary",
                "N2": "Upper Intermediate - Understand Japanese used in daily situations",
                "N1": "Advanced - Comprehensive Japanese in various circumstances"
            }
            st.info(jlpt_descriptions[jlpt_level])
            
            # Exercise details
            st.subheader("Exercise Details")
            topic = st.text_input("Topic (optional)", placeholder="e.g., restaurant, travel, shopping")
            num_questions = st.slider("Number of Questions", min_value=1, max_value=5, value=1)
            
            # Generate button
            generate_button = st.form_submit_button("Generate Exercise")
            
            if generate_button:
                with st.spinner(f"Generating {jlpt_level} exercise..."):
                    exercise = asyncio.run(generate_audio_exercise(
                        topic=topic if topic else None,
                        jlpt_level=jlpt_level,
                        num_questions=num_questions
                    ))
        
        # Show saved exercises
        st.subheader("Saved Exercises")
        try:
            saved_exercises = audio_generator.list_stored_exercises()
            if saved_exercises:
                for ex in saved_exercises:
                    with st.container():
                        title = f"{ex['jlpt_level']} - {ex['topic'] if ex['topic'] else 'General'}"
                        st.write(f"**{title}**")
                        st.write(f"Questions: {ex['num_questions']} | Has Audio: {'Yes' if ex['has_audio'] else 'No'}")
                        st.button("Load", key=f"load_{ex['id']}", on_click=load_audio_exercise, args=(ex['id'],))
                        st.divider()
            else:
                st.info("No saved exercises found. Generate a new one!")
        except Exception as e:
            st.error(f"Error loading saved exercises: {str(e)}")
    else:
        exercise = st.session_state.audio_exercise
        
        # Display exercise details
        jlpt_level = exercise.get('jlpt_level', 'N4')
        display_level = exercise.get('display_level', f"JLPT {jlpt_level}")
        st.header(f"{display_level} Listening Exercise")
        
        if exercise.get('topic'):
            st.subheader(f"Topic: {exercise['topic']}")
        
        # Audio playback
        if exercise.get('main_audio') and os.path.exists(exercise['main_audio']):
            st.subheader("Listen to the Audio")
            st.markdown(get_audio_player(exercise['main_audio']), unsafe_allow_html=True)
            st.info("Listen to the audio carefully, then answer the questions below.")
        else:
            st.warning("No audio available for this exercise.")
        
        # Show script (collapsible)
        with st.expander("View Script (for reference only)", expanded=False):
            st.text(exercise.get('script', 'No script available'))
        
        # DIRECT QUESTIONS DISPLAY - always show questions from the exercise data
        st.subheader("Answer the Questions")
        st.write(f"**This exercise has {len(exercise.get('questions', []))} questions to answer:**")
            
        # Create form for answering questions
        with st.form("questions_form"):
            # Get the questions from exercise
            questions = exercise.get('questions', [])
            
            # If there are no questions, create a default one
            if not questions:
                st.warning("No questions found in the exercise data. Using default question.")
                questions = [{
                    "question": "この会話は何についてですか？ (What is this conversation about?)",
                    "options": ["勉強について (About studying)", 
                               "趣味について (About hobbies)", 
                               "仕事について (About work)", 
                               "天気について (About the weather)"]
                }]
            
            # Display each question
            for i, q in enumerate(questions):
                question_num = i + 1
                question_text = q.get('question', f'Question {question_num}')
                
                st.write(f"**Question {question_num}:** {question_text}")
                
                if 'options' in q and q['options']:
                    # Multiple choice question
                    options = q['options']
                    answer = st.radio(
                        f"Select your answer for question {question_num}:",
                        options,
                        key=f"q_{question_num}"
                    )
                else:
                    # Free form question
                    answer = st.text_input(
                        f"Your answer for question {question_num}:",
                        key=f"q_{question_num}"
                    )
                
                # Store answer
                submit_audio_answer(question_num, answer)
                
                st.divider()
            
            # Submit button
            st.write("### Submit Your Answers")
            submit_button = st.form_submit_button("Submit Answers", use_container_width=True)
            if submit_button:
                # Make sure all answers are properly saved
                for i, q in enumerate(questions):
                    question_num = i + 1
                    key = f"q_{question_num}"
                    if key in st.session_state:
                        answer = st.session_state[key]
                        # Save answer to session state
                        if 'audio_answers' not in st.session_state:
                            st.session_state.audio_answers = {}
                        st.session_state.audio_answers[str(question_num)] = answer
                
                st.success("Answers submitted! Redirecting to results...")
                time.sleep(0.5)
                
                # Directly set the app state and force rerun
                st.session_state.app_state = APP_STATES["AUDIO_EXERCISE_REVIEW"]
                st.rerun()
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate New Exercise"):
                # Set flag to clear the exercise when redirecting
                st.session_state.clear_exercise = True
                go_to_audio_exercise()
        with col2:
            st.button("Back to Home", on_click=go_to_home)

def render_audio_exercise_review():
    st.title("Review Your Answers")
    
    # Clear startup placeholder
    startup_placeholder.empty()
    
    # Check if backend is running
    if not backend_running:
        st.error("Backend server is not running")
        st.info("Please run the backend server using: python run.py")
        if st.button("Go to Home"):
            go_to_home()
        return
    
    # Check if we have an exercise to review
    if 'audio_exercise' not in st.session_state or not st.session_state.audio_exercise:
        st.error("No exercise found to review")
        st.info("Please generate or load an exercise first")
        if st.button("Go to Exercise Generator"):
            go_to_audio_exercise()
        return
    
    # Get the exercise
    exercise = st.session_state.audio_exercise
    
    # Display exercise details
    st.header(f"{exercise.get('display_level', 'JLPT')} Listening Exercise Results")
    
    if exercise.get('topic'):
        st.subheader(f"Topic: {exercise['topic']}")
    
    # Get user answers
    user_answers = st.session_state.get('audio_answers', {})
    
    # Display audio for reference
    if exercise.get('main_audio') and os.path.exists(exercise['main_audio']):
        st.subheader("Listen to the Audio Again")
        st.markdown(get_audio_player(exercise['main_audio']), unsafe_allow_html=True)
    
    # Review questions and answers
    st.subheader("Question Review")
    
    # Initialize counters
    total_questions = 0
    correct_answers = 0
    
    # Get the questions
    questions = exercise.get('questions', [])
    
    # Display each question and the user's answer
    for i, q in enumerate(questions):
        question_num = i + 1
        question_text = q.get('question', f'Question {question_num}')
        
        # Create columns for the question review
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**Question {question_num}:** {question_text}")
            
            # Get user answer
            user_answer = user_answers.get(str(question_num), None)
            
            # Get correct answer if available
            correct_index = q.get('correct_answer', 0)
            
            if 'options' in q and q['options']:
                options = q['options']
                
                # Get the correct answer text
                correct_answer = options[correct_index] if 0 <= correct_index < len(options) else options[0]
                
                # Display user answer
                if user_answer:
                    # Check if user answer matches correct answer
                    is_correct = user_answer == correct_answer
                    
                    # Update counters
                    total_questions += 1
                    if is_correct:
                        correct_answers += 1
                    
                    # Display the result
                    if is_correct:
                        st.success(f"✓ Your answer: {user_answer}")
                    else:
                        st.error(f"✗ Your answer: {user_answer}")
                        st.info(f"Correct answer: {correct_answer}")
                else:
                    st.warning("You did not answer this question")
                    st.info(f"Correct answer: {correct_answer}")
                    total_questions += 1
                
                # Display all options with the correct one highlighted
                st.write("**All options:**")
                for j, option in enumerate(options):
                    if j == correct_index:
                        st.success(f"✓ {option}")
                    else:
                        st.write(f"- {option}")
            else:
                # Free form question
                st.info("This was a free-form question without predefined correct answers")
                if user_answer:
                    st.write(f"Your answer: {user_answer}")
                else:
                    st.warning("You did not answer this question")
        
        with col2:
            # Display a visual indicator of correctness
            if 'options' in q and q['options'] and user_answer:
                correct_index = q.get('correct_answer', 0)
                correct_answer = options[correct_index] if 0 <= correct_index < len(options) else options[0]
                
                if user_answer == correct_answer:
                    st.success("CORRECT ✓")
                else:
                    st.error("INCORRECT ✗")
            elif user_answer:
                st.info("REVIEWED")
            else:
                st.warning("NOT ANSWERED")
        
        st.divider()
    
    # Display overall results
    st.subheader("Overall Results")
    
    # Calculate score
    score_percentage = 0
    if total_questions > 0:
        score_percentage = (correct_answers / total_questions) * 100
    
    # Display score
    st.write(f"**Score:** {correct_answers}/{total_questions} ({score_percentage:.1f}%)")
    
    # Performance feedback
    if score_percentage >= 80:
        st.success("Great job! You have a good understanding of the material.")
    elif score_percentage >= 60:
        st.info("Good effort! Keep practicing to improve.")
    else:
        st.warning("More practice needed. Don't give up!")
    
    # Provide JLPT level-specific feedback
    jlpt_level = exercise.get('jlpt_level', 'N4')
    if jlpt_level in ['N1', 'N2']:
        st.write(f"This was an advanced {jlpt_level} exercise. Scores above 60% indicate good progress at this level.")
    elif jlpt_level == 'N3':
        st.write(f"This was an intermediate {jlpt_level} exercise. Keep practicing to build your skills.")
    else:  # N4, N5
        st.write(f"This was a beginner-level {jlpt_level} exercise. Regular practice will help you improve quickly.")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        st.button("Try Another Exercise", on_click=go_to_audio_exercise)
    with col2:
        st.button("Back to Home", on_click=go_to_home)

# Main app rendering based on state
if st.session_state.app_state == APP_STATES["HOME"]:
    # Clear the startup placeholder once we're in the main UI
    startup_placeholder.empty()
    render_home()
elif st.session_state.app_state == APP_STATES["VIDEO_SELECTION"]:
    # Clear the startup placeholder once we're in the main UI
    startup_placeholder.empty()
    render_video_selection()
elif st.session_state.app_state == APP_STATES["PRACTICE"]:
    # Clear the startup placeholder once we're in the main UI
    startup_placeholder.empty()
    render_practice()
elif st.session_state.app_state == APP_STATES["REVIEW"]:
    # Clear the startup placeholder once we're in the main UI
    startup_placeholder.empty()
    render_review()
elif st.session_state.app_state == APP_STATES["PROCESSING_VIDEO"]:
    # Clear the startup placeholder once we're in the main UI
    startup_placeholder.empty()
    render_processing_video()
elif st.session_state.app_state == APP_STATES["AUDIO_EXERCISE"]:
    render_audio_exercise()
elif st.session_state.app_state == APP_STATES["AUDIO_EXERCISE_REVIEW"]:
    render_audio_exercise_review()

# Sidebar with app information
with st.sidebar:
    st.title("Navigation")
    st.button("Home", on_click=go_to_home)
    st.button("YouTube Videos", on_click=go_to_video_selection)
    st.button("JLPT Audio Exercises", on_click=go_to_audio_exercise)
    
    st.divider()
    
    st.subheader("About")
    st.info("""
    This application is designed to help you practice Japanese listening comprehension
    using authentic content from YouTube or AI-generated JLPT-style exercises.
    All processing happens locally on your machine.
    """)
    
    st.divider()
    
    # Show saved exercises if any
    if st.session_state.app_state not in [APP_STATES["AUDIO_EXERCISE"], APP_STATES["AUDIO_EXERCISE_REVIEW"]]:
        st.subheader("Saved Exercises")
        
        # Only show saved exercises if audio generator is available
        audio_generator = get_audio_exercise_generator()
        if audio_generator:
            try:
                saved_exercises = audio_generator.list_stored_exercises(max_count=5)
                
                if saved_exercises:
                    for ex in saved_exercises:
                        title = f"{ex['jlpt_level']} - {ex['topic'] if ex['topic'] else 'General'}"
                        if st.button(f"{title} ({ex['num_questions']} questions)", key=f"sidebar_{ex['id']}"):
                            load_audio_exercise(ex['id'])
                else:
                    st.write("No saved exercises found.")
            except Exception as e:
                st.error(f"Error loading exercises: {str(e)}")
        else:
            st.write("Exercise loader not available.")
    
    # Backend status indicator
    st.subheader("System Status")
    if backend_running:
        st.success("Backend: Connected")
    else:
        st.error("Backend: Not connected")
        st.info("Run 'python run.py' to start the backend") 