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
import traceback
import subprocess

# Import synthetic questions generator
from synthetic_questions import generate_synthetic_questions

# Function to check and install missing packages
def check_and_install_requirements():
    """Check and install any missing packages required for the application"""
    required_packages = {
        "youtube-transcript-api": "youtube_transcript_api",
        "streamlit": "streamlit",
        "pydub": "pydub",
        "gtts": "gtts",
        "beautifulsoup4": "bs4"  # Add beautifulsoup4 to the required packages
    }
    
    missing_packages = []
    
    # Check if packages are installed
    for package_name, import_name in required_packages.items():
        try:
            # Try to import the package
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    # Install missing packages
    if missing_packages:
        st.warning(f"Installing missing packages: {', '.join(missing_packages)}")
        try:
            for package in missing_packages:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            st.success("All required packages installed successfully!")
            st.info("Please restart the application for changes to take effect.")
            # Give the user a moment to read the message
            time.sleep(3)
        except Exception as e:
            st.error(f"Failed to install packages: {str(e)}")
            st.info("Please manually install the required packages using:")
            st.code(f"pip install {' '.join(missing_packages)}")

# Try to run the check at startup
try:
    check_and_install_requirements()
except Exception as e:
    logging.warning(f"Could not check and install requirements: {str(e)}")

from youtube_transcript_api import YouTubeTranscriptApi
import json

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
    """
    Find the backend server by checking various ports.
    Uses a retry mechanism with shorter timeouts to avoid hanging.
    """
    # First try the configured port
    config = load_config()
    configured_port = config.get("backend_port", 8004)
    logger.info(f"Looking for backend on configured port: {configured_port}")
    
    # Try the configured port first
    if is_port_in_use(configured_port):
        for attempt in range(3):  # Retry up to 3 times with short timeout
            try:
                response = requests.get(f"http://localhost:{configured_port}/health", timeout=1)
                if response.status_code == 200:
                    logger.info(f"Backend found on configured port: {configured_port}")
                    return configured_port
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout connecting to configured port: {configured_port} (attempt {attempt+1}/3)")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on configured port: {configured_port} (attempt {attempt+1}/3)")
            except Exception as e:
                logger.warning(f"Error checking configured port: {configured_port}: {str(e)}")
            # Short delay between retries
            time.sleep(0.5)
    
    # If that fails, try common ports
    common_ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 
                    8020, 8030, 8040, 8050, 8060, 8070, 8080, 8090]
    
    logger.info("Configured port not available, scanning common ports...")
    for port in common_ports:
        if port == configured_port:
            continue  # Already tried this one
        
        if is_port_in_use(port):
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=1)
                if response.status_code == 200:
                    # Backend found, update the config
                    logger.info(f"Backend found on alternative port: {port}")
                    config["backend_port"] = port
                    with open(Path(__file__).parent.parent / "config.json", 'w') as f:
                        json.dump(config, f, indent=2)
                    return port
            except Exception as e:
                logger.warning(f"Port {port} is in use but not by our backend: {str(e)}")
    
    # If we couldn't find a working backend, return the configured port
    logger.warning(f"No backend found on any port, defaulting to configured port: {configured_port}")
    return configured_port

# Find the backend server with better error handling
backend_port = find_backend_server()
BACKEND_URL = f"http://localhost:{backend_port}"

# Check if backend is running
backend_running = False
try:
    # Use a shorter timeout when checking if backend is running
    logger.info(f"Checking if backend is running on port {backend_port}...")
    response = requests.get(f"{BACKEND_URL}/health", timeout=2)
    
    if response.status_code == 200:
        backend_running = True
        logger.info(f"Backend server is running on port {backend_port}")
        # Success message will be shown in the sidebar
    else:
        logger.warning(f"Backend server returned status code: {response.status_code}")
except requests.exceptions.Timeout:
    logger.error(f"Timeout connecting to backend on port {backend_port}")
except requests.exceptions.ConnectionError:
    logger.error(f"Connection error to backend on port {backend_port}")
except Exception as e:
    logger.error(f"Error checking backend: {str(e)}")

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

# Add new app state constant after the existing app states
APP_STATE_EXTRACT_QUESTIONS = "EXTRACT_QUESTIONS"

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
    except Exception as e:
        return f"Error checking audio file size: {str(e)}"
    
    # Use a try-finally block to ensure file handles are closed
    audio_base64 = None
    try:
        audio_format = audio_path.split(".")[-1].lower()
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        # Encode to base64 and immediately delete the raw bytes to free memory
        audio_base64 = base64.b64encode(audio_bytes).decode()
        del audio_bytes  # Explicitly delete to free memory
        
        # Force garbage collection
        import gc
        gc.collect()
        
        autoplay_attr = 'autoplay' if autoplay else ''
        
        # Create the HTML audio player
        audio_html = f"""
        <audio controls {autoplay_attr} style="width: 100%;">
            <source src="data:audio/{audio_format};base64,{audio_base64}" type="audio/{audio_format}">
            Your browser does not support the audio element.
        </audio>
        """
        return audio_html
    except Exception as e:
        return f"Error creating audio player: {str(e)}"
    finally:
        # Help the garbage collector by clearing references
        if 'audio_bytes' in locals():
            del audio_bytes
        if 'audio_base64' in locals() and audio_base64:
            # We can't delete audio_base64 if it's being returned,
            # but we can hint to Python that we're done with it in this scope
            audio_base64 = None

# State transition functions
def go_to_home():
    st.session_state.app_state = APP_STATES["HOME"]

def go_to_video_selection():
    st.session_state.app_state = APP_STATES["VIDEO_SELECTION"]

def go_to_practice(video_id):
    """Transition to the practice page with a specific video"""
    # Validate the video_id
    if not video_id:
        logger.warning("Attempted to go to practice with empty video_id")
        st.session_state.app_state = APP_STATES["VIDEO_SELECTION"]
        st.experimental_rerun()
        return
        
    # Store the video ID in session state - handle string or dict case
    if isinstance(video_id, dict) and "id" in video_id:
        # If we got passed a full video object instead of just the ID
        st.session_state.current_video = video_id
        video_id = video_id["id"]
    else:
        # Just the ID was passed
        st.session_state.current_video = video_id
    
    # Update the application state
    st.session_state.app_state = APP_STATES["PRACTICE"]
    
    # Only try to load exercises if video_id is not None or empty
    if video_id:
        # Only try to load exercises from backend if it's running
        if backend_running:
            try:
                # Load exercises for this video with a timeout
                load_exercises(video_id)
            except Exception as e:
                logger.error(f"Error loading exercises: {str(e)}")
                st.session_state.exercises = []  # Initialize with empty list on error
        else:
            # Backend is not running, use empty exercises list
            logger.warning("Backend is not running, using empty exercises list")
            st.session_state.exercises = []
            
    # Force UI update
    st.experimental_rerun()

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
    # First, clean up any potential resources that might be causing memory issues
    if 'audio_exercise' in st.session_state and st.session_state.audio_exercise:
        # If we have an exercise with audio, make sure we're not keeping references to it
        if 'main_audio' in st.session_state.audio_exercise:
            st.session_state.audio_exercise['main_audio'] = None
    
    # Explicitly clean up TTS engine if it was initialized
    if 'tts_engine' in st.session_state:
        st.session_state.tts_engine = None
    
    # Clean up any audio player references 
    if 'audio_player' in st.session_state:
        st.session_state.audio_player = None
    
    # Clear exercise when coming from anywhere but the generate function
    if ('from_generate' not in st.session_state) or (not st.session_state.get('from_generate', False)):
        # Clear any previous answers
        st.session_state.audio_answers = {}
        # Clear the current exercise to show the selection form again
        st.session_state.audio_exercise = None
        st.session_state.audio_exercise_id = None
    
    # Reset the from_generate flag if it exists
    if 'from_generate' in st.session_state:
        st.session_state.from_generate = False
    
    # Now set the app state
    st.session_state.app_state = APP_STATES["AUDIO_EXERCISE"]

def go_to_audio_exercise_review():
    """Transition to the audio exercise review screen"""
    st.session_state.app_state = APP_STATES["AUDIO_EXERCISE_REVIEW"]
    # Add a rerun to force the state change
    st.rerun()

def go_to_extract_questions():
    """Navigate to the extract questions page"""
    st.session_state.app_state = APP_STATE_EXTRACT_QUESTIONS
    
    # Clear any previous extraction results when navigating to the page
    if "extracted_content" in st.session_state:
        del st.session_state["extracted_content"]

def load_audio_exercise(exercise_id):
    """Load an audio exercise by ID"""
    if exercise_id:
        st.info(f"Loading exercise {exercise_id}...")
        
        audio_generator = get_audio_exercise_generator()
        if audio_generator is None:
            st.error("Audio exercise generator is not available")
            return
        
        try:
            exercise = audio_generator.get_exercise_by_id(exercise_id)
            if exercise:
                # Check if audio exists but don't block loading if it doesn't
                if exercise.get('main_audio') and not os.path.exists(exercise.get('main_audio', '')):
                    exercise['has_audio'] = False
                
                # Always load the exercise, even if audio is missing
                st.session_state.audio_exercise = exercise
                st.session_state.audio_exercise_id = exercise_id
                
                # Clear any previous answers
                st.session_state.audio_answers = {}
                
                # Set the from_generate flag to false since we're loading an existing exercise
                st.session_state.from_generate = False
                
                # Set the app state to audio exercise to show the loaded exercise
                st.session_state.app_state = APP_STATES["AUDIO_EXERCISE"]
                
                # Force UI update with a rerun
                st.rerun()
            else:
                st.error(f"Could not load exercise with ID: {exercise_id}")
        except Exception as e:
            st.error(f"Error loading exercise: {str(e)}")
            st.error(traceback.format_exc())

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
            st.rerun()
            return exercise
        else:
            st.error("Failed to generate exercise")
            return None
    except Exception as e:
        st.error(f"Error generating audio exercise: {str(e)}")
        return None

def extract_youtube_id(url):
    """Extract the video ID from a YouTube URL"""
    if not url:
        return None
        
    # Clean the URL first (trim whitespace, handle copy-paste issues)
    url = url.strip()
    
    # Handle common issues with copied URLs
    if url.startswith('"') and url.endswith('"'):
        url = url[1:-1]  # Remove quotes
        
    if url.startswith("'") and url.endswith("'"):
        url = url[1:-1]  # Remove quotes
        
    # YouTube URL patterns
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([^\/&\?#\s]+)',  # Standard and shortened
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^\/&\?#\s]+)',  # Embed URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^\/&\?#\s]+)',      # Old embed URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/user\/[^\/]+\/([^\/&\?#\s]+)', # User URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/.*[?&]v=([^&\s]+)'       # Other formats with v parameter
    ]
    
    import re
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # Validate the video ID format (should be 11 characters for standard videos)
            if 11 <= len(video_id) <= 12:
                return video_id
    
    # If no patterns match, this might be a direct video ID
    if 11 <= len(url) <= 12 and url.isalnum() or url.replace('-', '').replace('_', '').isalnum():
        return url
        
    return None

def process_custom_video(video_url):
    """Process a custom YouTube video URL"""
    try:
        # Extract YouTube ID first to validate the URL
        youtube_id = extract_youtube_id(video_url)
        
        if not youtube_id:
            st.error("Invalid YouTube URL. Please provide a valid YouTube video URL.")
            st.info("Example of valid URL: https://www.youtube.com/watch?v=XXXXXXXXXXX")
            return
            
        # Create a placeholder for status messages
        status_placeholder = st.empty()
        status_placeholder.info(f"Processing YouTube video ID: {youtube_id}...")
        
        # Check if backend is running - essential for YouTube processing
        if not backend_running:
            status_placeholder.error("⚠️ Backend server is not running")
            st.error("The backend server is required for YouTube video processing.")
            
            st.markdown("""
            ### Troubleshooting Steps:
            1. Make sure the application was started using `python run.py` without the `--skip-backend` flag
            2. Check for any error messages in the terminal
            3. The backend is needed to download and process YouTube videos
            
            If you don't need YouTube features, you can still use the JLPT audio exercises.
            """)
            return
        
        # Proceed with backend requests with proper timeouts and error handling
        try:
            # Check if video already exists in the database
            response = requests.get(
                f"{BACKEND_URL}/videos", 
                params={"youtube_id": youtube_id}, 
                timeout=3
            )
            
            if response.status_code == 200 and response.json():
                # Video already exists, use the existing one
                video = response.json()[0]
                video_id = video["id"]
                status_placeholder.success(f"Video found in database: {video.get('title', youtube_id)}")
                
                # Initialize the answers dictionary if it doesn't exist
                if 'answers' not in st.session_state:
                    st.session_state.answers = {}
                
                # Load exercises for this video before redirecting
                try:
                    exercise_response = requests.get(
                        f"{BACKEND_URL}/exercises/{video_id}", 
                        timeout=3
                    )
                    
                    if exercise_response.status_code == 200:
                        st.session_state.exercises = exercise_response.json()
                        logger.info(f"Loaded {len(st.session_state.exercises)} exercises for video {video_id}")
                        
                        # Update the current video in session state
                        st.session_state.current_video = video
                        
                        # Change state and immediately force a rerun
                        st.session_state.app_state = APP_STATES["PRACTICE"]
                        st.experimental_rerun()
                        return
                    else:
                        status_placeholder.error(f"Error loading exercises: {exercise_response.text}")
                        st.error("Failed to load exercises for this video. Please try again.")
                        return
                        
                except requests.exceptions.Timeout:
                    status_placeholder.error("Request to load exercises timed out")
                    st.error("The request timed out. Please try again.")
                    return
                except Exception as e:
                    status_placeholder.error(f"Error loading exercises: {str(e)}")
                    st.error("Failed to load exercises for this video. Please try again.")
                    return
                
            # If video doesn't exist, add it to the database
            status_placeholder.info(f"Adding new video: {youtube_id}")
            
            # Add new video
            video_info = {
                "youtube_id": youtube_id,
                "title": f"YouTube Video: {youtube_id}",  # Will be updated with actual title later
                "url": video_url,
                "language": "ja"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/videos", 
                json=video_info, 
                timeout=5
            )
            
            if response.status_code == 200:
                video = response.json()
                video_id = video["id"]
                status_placeholder.info(f"Video added successfully. Processing transcript... (ID: {video_id})")
                
                # Request transcript processing
                transcript_request = {
                    "youtube_url": video_url
                }
                
                try:
                    transcript_response = requests.post(
                        f"{BACKEND_URL}/transcript", 
                        json=transcript_request,
                        timeout=10  # Longer timeout for transcript processing
                    )
                    
                    if transcript_response.status_code in [200, 202]:
                        # Success! Prepare session state and redirect
                        status_placeholder.success("Transcript processed successfully!")
                        
                        # Initialize the answers dictionary if it doesn't exist
                        if 'answers' not in st.session_state:
                            st.session_state.answers = {}
                        
                        # Load exercises for this video
                        try:
                            exercise_response = requests.get(
                                f"{BACKEND_URL}/exercises/{video_id}", 
                                timeout=3
                            )
                            
                            if exercise_response.status_code == 200:
                                st.session_state.exercises = exercise_response.json()
                                logger.info(f"Loaded {len(st.session_state.exercises)} exercises for video {video_id}")
                                
                                # Update the current video in session state
                                st.session_state.current_video = video
                                
                                # Show success message before redirecting
                                status_placeholder.success(f"Successfully processed video with {len(st.session_state.exercises)} exercises!")
                                
                                # Change state and force rerun
                                st.session_state.app_state = APP_STATES["PRACTICE"]
                                st.experimental_rerun()
                                return
                            else:
                                status_placeholder.error(f"Error loading exercises: {exercise_response.text}")
                                st.error("Failed to load exercises for this video. Please try again.")
                                return
                                
                        except Exception as e:
                            status_placeholder.error(f"Error loading exercises: {str(e)}")
                            st.error("Failed to load exercises for this video. Please try again.")
                            return
                    else:
                        status_placeholder.error(f"Failed to process transcript: {transcript_response.text}")
                        st.error("The video may not have Japanese captions available. Try another video.")
                        return
                        
                except requests.exceptions.Timeout:
                    status_placeholder.error("Transcript processing timed out")
                    st.error("Processing timed out. The video might be too long. Try a shorter video.")
                    return
                except Exception as e:
                    status_placeholder.error(f"Error processing transcript: {str(e)}")
                    st.error("Failed to process transcript. Please try again or use a different video.")
                    return
            else:
                status_placeholder.error(f"Failed to add video: {response.text}")
                st.error("Failed to add the video to the database. Please try again.")
                return
                
        except requests.exceptions.Timeout:
            status_placeholder.error("Request timed out")
            st.error("The request to the backend server timed out. Please try again.")
            return
        except requests.exceptions.ConnectionError:
            status_placeholder.error("Connection error")
            st.error("Failed to connect to the backend server. Make sure it's running.")
            return
        except Exception as e:
            status_placeholder.error(f"Error: {str(e)}")
            st.error(f"Unexpected error: {str(e)}. Please try again.")
            return
            
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        logger.error(f"Error in process_custom_video: {str(e)}")
        logger.error(traceback.format_exc())
        return

def load_exercises(video_id):
    """Load exercises for a specific video from the backend"""
    try:
        # Only attempt to load if backend is running
        if not backend_running:
            logger.warning("Backend server is not running, cannot load exercises")
            st.session_state.exercises = []
            return
            
        # Use a timeout to prevent hanging
        response = requests.get(f"{BACKEND_URL}/exercises/{video_id}", timeout=5)
        if response.status_code == 200:
            st.session_state.exercises = response.json()
        else:
            st.error(f"Failed to load exercises: {response.text}")
            st.session_state.exercises = []
    except requests.exceptions.Timeout:
        st.error("Request to load exercises timed out")
        st.session_state.exercises = []
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to backend server")
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
    - Extract questions directly from Japanese YouTube videos
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
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("YouTube Videos", on_click=go_to_video_selection, use_container_width=True)
    
    with col2:
        st.button("JLPT-Style Audio Exercises", on_click=go_to_audio_exercise, use_container_width=True)
        
    with col3:
        # Add a button to directly go to the question extraction page
        st.button("Extract Questions from YouTube", on_click=go_to_extract_questions, use_container_width=True)

def render_video_selection():
    """Render the video selection page with YouTube URL input and saved videos"""
    st.title("Select a Video")
    
    # Check if backend is running and show status
    if not backend_running:
        st.warning("⚠️ Backend server is not running - Some features will be limited")
        
    # Add new option for direct question extraction
    with st.expander("Extract Questions from Japanese YouTube Videos", expanded=True):
        st.write("Enter a Japanese YouTube URL to extract natural questions and their context:")
        
        # Add examples of valid YouTube URLs
        st.caption("""
        **Examples of valid YouTube URLs:**
        - https://www.youtube.com/watch?v=XXXXXXXXXXX
        - https://youtu.be/XXXXXXXXXXX
        """)
        
        st.info("This feature works best with Japanese language videos. The system will extract questions in Japanese and provide English translations when possible.")
        
        youtube_url = st.text_input(
            "Japanese YouTube URL", 
            placeholder="https://www.youtube.com/watch?v=...",
            key="direct_extract_url"
        )
        
        col1, col2 = st.columns([3, 1])
        with col2:
            extract_button = st.button("Extract Questions", use_container_width=True)
            
        # Process URL when button is clicked
        if extract_button:
            if not youtube_url:
                st.error("Please enter a YouTube URL")
            else:
                st.session_state["youtube_url"] = youtube_url
                st.session_state.app_state = APP_STATE_EXTRACT_QUESTIONS
                st.rerun()
    
    # Original custom Video URL Input
    with st.expander("Process with backend (full features)", expanded=False):
        st.write("Enter a YouTube URL to practice with a specific video:")
        
        # Add examples of valid YouTube URLs
        st.caption("""
        **Examples of valid YouTube URLs:**
        - https://www.youtube.com/watch?v=XXXXXXXXXXX
        - https://youtu.be/XXXXXXXXXXX
        - https://m.youtube.com/watch?v=XXXXXXXXXXX
        """)
        
        youtube_url = st.text_input(
            "YouTube URL", 
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste a YouTube URL with Japanese content for practice"
        )
        
        col1, col2 = st.columns([3, 1])
        with col2:
            submit_button = st.button("Add Video", use_container_width=True)
            
        # Process URL when button is clicked
        if submit_button:
            if not youtube_url:
                st.error("Please enter a YouTube URL")
            else:
                # Show a spinner while processing
                with st.spinner("Processing YouTube URL..."):
                    # Validate URL format
                    youtube_id = extract_youtube_id(youtube_url)
                    if not youtube_id:
                        st.error("Invalid YouTube URL format. Please check the URL and try again.")
                    else:
                        st.info(f"Processing video with ID: {youtube_id}...")
                        # Store URL and redirect to processing page
                        st.session_state.custom_video_url = youtube_url
                        go_to_processing_video(youtube_url)
    
    # Search functionality
    with st.expander("Search for videos", expanded=False):
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_query = st.text_input("Search for Japanese videos", placeholder="Enter keywords...")
        with search_col2:
            search_button = st.button("Search", use_container_width=True)
        
        if search_button and search_query:
            st.info(f"Searching for: {search_query}")
            st.warning("Search functionality is under development. Please use the URL input for now.")
    
    # Navigation
    st.button("Back to Home", on_click=go_to_home)

def render_processing_video():
    """Render the processing state for a custom video"""
    st.title("Processing YouTube Video")
    
    video_url = st.session_state.custom_video_url
    video_id = extract_youtube_id(video_url) or "Unknown"
    
    # Create columns for video info and progress
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"Processing YouTube video: {video_url}")
        
        # Embed a thumbnail of the video if we have the ID
        if video_id != "Unknown":
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
            st.image(thumbnail_url, caption="Video Thumbnail", use_column_width=True)
        
        st.markdown(f"""
        ### Video Details
        - **URL**: {video_url}
        - **YouTube ID**: {video_id}
        """)
    
    with col2:
        st.subheader("Processing Status")
        st.info("This process may take several minutes depending on the video length.")
    
    # Progress information with more details
    st.markdown("""
    ### Processing Steps
    
    1. ⏳ **Extracting Video Information**
       - Getting video title, duration, and metadata
       
    2. ⏳ **Downloading Audio**
       - Extracting audio track for processing
       
    3. ⏳ **Generating Transcript**
       - Getting Japanese transcript from YouTube
       - If not available, generating via speech recognition
       
    4. ⏳ **Analyzing Content Structure**
       - Identifying introduction section
       - Locating main conversation parts
       
    5. ⏳ **Creating Exercises**
       - Generating introduction questions
       - Creating targeted conversation questions
       - Preparing multiple-choice options
    
    ### How It Works
    
    The system analyzes the video and distinguishes between introduction sections (where the topic, participants, or context are introduced) and the main conversation. This allows for more targeted questions:
    
    - **Introduction questions** focus on the video's topic, purpose, and context
    - **Conversation questions** test your understanding of specific dialogue content
    
    Each question includes a timestamp so you can focus on the relevant part of the video.
    """)
    
    # Show spinner while processing
    with st.spinner("Processing video... (This may take a few minutes)"):
        st.empty()
    
    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel and go back", use_container_width=True):
            go_to_video_selection()
    with col2:
        if st.button("Check Progress", use_container_width=True):
            st.info("Refreshing progress information...")
            time.sleep(1)
            st.experimental_rerun()

def render_practice():
    """Render the practice page for a YouTube video with exercises"""
    st.title("Listening Practice")
    
    if not st.session_state.current_video or not st.session_state.exercises:
        st.warning("No exercises available. Please select a video first.")
        st.button("Back to Video Selection", on_click=go_to_video_selection)
        return
    
    # Get current video info
    video_id = st.session_state.current_video.get("youtube_id", "")
    video_title = st.session_state.current_video.get("title", "Unknown Video")
    
    # Show video information
    st.header(video_title)
    
    # Video player (embedded YouTube iframe)
    if video_id:
        st.subheader("Video")
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Create YouTube embed HTML
        embed_html = f"""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; border-radius: 8px;">
            <iframe 
                src="https://www.youtube.com/embed/{video_id}" 
                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
            </iframe>
        </div>
        """
        st.markdown(embed_html, unsafe_allow_html=True)
        
        # Direct link to video
        st.markdown(f"[Open video in YouTube]({video_url})", unsafe_allow_html=True)
    else:
        st.info("Video player is not available for this content.")
    
    # Instructions
    st.markdown("""
    ### How to Use
    1. Watch the video or specific segments referenced in each question
    2. Answer all questions in the form below
    3. Click "Submit Answers" when you're finished
    4. Review your results and explanations
    """)
    
    # Organize exercises by type (introduction vs conversation)
    exercises = st.session_state.exercises
    intro_exercises = []
    conversation_exercises = []
    
    # Identify intro exercises (usually about the first 20% of the video)
    if exercises:
        # Get video duration if available, handling the case when current_video might be None or not a dictionary
        video_duration = 0  # Default to 0
        
        # Safely get video duration if current_video is a dictionary
        if isinstance(st.session_state.current_video, dict):
            video_duration = st.session_state.current_video.get("duration", 0)
            # Ensure it's a number
            if not isinstance(video_duration, (int, float)) or video_duration is None:
                video_duration = 0
        
        if video_duration > 0:
            intro_threshold = video_duration * 0.2
            
            for exercise in exercises:
                segment_start = exercise.get("segment_start", 0)
                # Ensure segment_start is a number
                if not isinstance(segment_start, (int, float)) or segment_start is None:
                    segment_start = 0
                    
                if segment_start < intro_threshold:
                    intro_exercises.append(exercise)
                else:
                    conversation_exercises.append(exercise)
        else:
            # If we don't have duration, assume first exercise is intro
            if len(exercises) > 0:
                intro_exercises = [exercises[0]]
                conversation_exercises = exercises[1:]
            else:
                conversation_exercises = exercises
    
    # Exercises form
    st.subheader("Comprehension Exercises")
    
    exercise_form = st.form("exercise_form")
    with exercise_form:
        # Introduction exercises
        if intro_exercises:
            st.markdown("### Introduction Questions")
            st.info("These questions focus on understanding the topic and context of the video.")
            
            for i, exercise in enumerate(intro_exercises):
                render_exercise(exercise, i)
        
        # Conversation exercises
        if conversation_exercises:
            st.markdown("### Conversation Questions")
            st.info("These questions test your understanding of the specific dialogue content.")
            
            for i, exercise in enumerate(conversation_exercises):
                render_exercise(exercise, i + len(intro_exercises))
        
        submit_button = st.form_submit_button("Submit Answers", use_container_width=True)
        if submit_button:
            go_to_review()
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        st.button("Back to Video Selection", on_click=go_to_video_selection)
    with col2:
        st.button("Back to Home", on_click=go_to_home)

def render_exercise(exercise, index):
    """Helper function to render a single exercise"""
    question_number = index + 1
    
    # Get exercise details
    question = exercise.get('question', f'Question {question_number}')
    exercise_type = exercise.get('type', 'multiple_choice')
    segment_start = exercise.get('segment_start')
    segment_end = exercise.get('segment_end')
    
    # Create container for the exercise
    with st.container():
        # Question with timestamp info
        timestamp_info = ""
        if segment_start is not None and segment_end is not None:
            timestamp_info = f" (Timestamp: {segment_start:.1f}s - {segment_end:.1f}s)"
        
        st.write(f"**Question {question_number}:{timestamp_info}**")
        st.write(question)
        
        # Different types of exercises
        if exercise_type == 'multiple_choice':
            options = exercise.get('options', [])
            answer = st.radio(
                f"Select your answer for question {question_number}:",
                options,
                key=f"radio_{exercise.get('id', f'q{question_number}')}"
            )
        elif exercise_type == 'fill_in':
            answer = st.text_input(
                f"Your answer for question {question_number}:",
                key=f"text_{exercise.get('id', f'q{question_number}')}"
            )
        else:  # Free form
            answer = st.text_area(
                f"Your answer for question {question_number}:",
                key=f"textarea_{exercise.get('id', f'q{question_number}')}"
            )
        
        # Store answer in session state
        submit_answer(exercise.get('id', f'q{question_number}'), answer)
        
        st.divider()

def render_review():
    """Render the review page for answers to YouTube video exercises"""
    st.title("Review Your Answers")
    
    if not st.session_state.current_video or not st.session_state.exercises:
        st.warning("No exercises available to review. Please select a video first.")
        st.button("Back to Video Selection", on_click=go_to_video_selection)
        return
    
    # Get video info
    video_id = st.session_state.current_video.get("youtube_id", "")
    video_title = st.session_state.current_video.get("title", "Unknown Video")
    
    # Display video information
    st.header(f"Results for: {video_title}")
    
    # Calculate results
    results = calculate_results()
    total_correct = sum(1 for result in results.values() if result.get("correct", False))
    total_questions = len(results)
    
    # Display score
    if total_questions > 0:
        score_percentage = (total_correct / total_questions) * 100
        
        # Display appropriate message based on score
        if score_percentage >= 80:
            st.success(f"Great job! You scored {score_percentage:.1f}% ({total_correct}/{total_questions} correct)")
        elif score_percentage >= 60:
            st.warning(f"Good effort! You scored {score_percentage:.1f}% ({total_correct}/{total_questions} correct)")
        else:
            st.error(f"Keep practicing! You scored {score_percentage:.1f}% ({total_correct}/{total_questions} correct)")
        
        # Visual progress bar
        st.progress(score_percentage / 100)
    else:
        st.warning("No questions were answered")
    
    # Video player for reference (smaller version)
    if video_id:
        with st.expander("Rewatch Video", expanded=False):
            embed_html = f"""
            <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; border-radius: 8px;">
                <iframe 
                    src="https://www.youtube.com/embed/{video_id}" 
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
                </iframe>
            </div>
            """
            st.markdown(embed_html, unsafe_allow_html=True)
    
    # Review all exercises
    st.subheader("Detailed Review")
    
    # Organize exercises by type (introduction vs conversation)
    exercises = st.session_state.exercises
    intro_exercises = []
    conversation_exercises = []
    
    # Identify intro exercises (usually about the first 20% of the video)
    if exercises:
        # Get video duration if available, handling the case when current_video might be None or not a dictionary
        video_duration = 0  # Default to 0
        
        # Safely get video duration if current_video is a dictionary
        if isinstance(st.session_state.current_video, dict):
            video_duration = st.session_state.current_video.get("duration", 0)
            # Ensure it's a number
            if not isinstance(video_duration, (int, float)) or video_duration is None:
                video_duration = 0
        
        if video_duration > 0:
            intro_threshold = video_duration * 0.2
            
            for exercise in exercises:
                segment_start = exercise.get("segment_start", 0)
                # Ensure segment_start is a number
                if not isinstance(segment_start, (int, float)) or segment_start is None:
                    segment_start = 0
                    
                if segment_start < intro_threshold:
                    intro_exercises.append(exercise)
                else:
                    conversation_exercises.append(exercise)
        else:
            # If we don't have duration, assume first exercise is intro
            if len(exercises) > 0:
                intro_exercises = [exercises[0]]
                conversation_exercises = exercises[1:]
            else:
                conversation_exercises = exercises
    
    # Introduction exercises review
    if intro_exercises:
        st.markdown("### Introduction Questions")
        
        for i, exercise in enumerate(intro_exercises):
            render_exercise_review(exercise, i, results)
    
    # Conversation exercises review
    if conversation_exercises:
        st.markdown("### Conversation Questions")
        
        for i, exercise in enumerate(conversation_exercises):
            render_exercise_review(exercise, i + len(intro_exercises), results)
    
    # Learning tips based on performance
    st.subheader("Learning Tips")
    
    if total_questions > 0:
        if score_percentage >= 80:
            st.success("""
            ### Excellent Work!
            - Try videos with more complex conversations
            - Practice with faster speech or regional dialects
            - Focus on nuanced cultural expressions
            """)
        elif score_percentage >= 60:
            st.info("""
            ### Good Progress
            - Watch videos at slightly slower speed first, then normal speed
            - Focus on the questions you missed - what vocabulary tripped you up?
            - Practice listening for key words in sentences
            """)
        else:
            st.warning("""
            ### Keep Practicing
            - Try videos with simpler language or clearer speech
            - Study the key vocabulary from this video before rewatching
            - Practice with shorter clips first
            - Consider using subtitles initially, then removing them
            """)
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        # Only enable Try Again if current_video is a dictionary with an id
        if isinstance(st.session_state.current_video, dict) and "id" in st.session_state.current_video:
            st.button("Try Again", on_click=go_to_practice, args=(st.session_state.current_video["id"],))
        else:
            st.button("Try Again", on_click=go_to_video_selection)  # Fallback to video selection
    with col2:
        st.button("Choose Another Video", on_click=go_to_video_selection)
    with col3:
        st.button("Back to Home", on_click=go_to_home)

def render_exercise_review(exercise, index, results):
    """Helper function to render a single exercise review"""
    question_number = index + 1
    exercise_id = exercise.get('id', f'q{question_number}')
    
    # Get exercise details
    question = exercise.get('question', f'Question {question_number}')
    exercise_type = exercise.get('type', 'multiple_choice')
    segment_start = exercise.get('segment_start')
    segment_end = exercise.get('segment_end')
    
    # Get result for this exercise
    result = results.get(exercise_id, {"correct": False, "feedback": "No result available"})
    
    # Determine the expander title and state based on correctness
    if result.get("correct", False):
        title = f"Question {question_number}: ✓ Correct"
        expanded = False
    else:
        title = f"Question {question_number}: ✗ Incorrect"
        expanded = True
    
    # Create expander for the exercise review
    with st.expander(title, expanded=expanded):
        # Question with timestamp info
        timestamp_info = ""
        if segment_start is not None and segment_end is not None:
            timestamp_info = f" (Timestamp: {segment_start:.1f}s - {segment_end:.1f}s)"
            
            # Add a link to jump to that part of the video
            video_id = st.session_state.current_video.get("youtube_id", "")
            if video_id:
                timestamp_seconds = int(segment_start)
                timestamp_url = f"https://youtu.be/{video_id}?t={timestamp_seconds}"
                st.markdown(f"[Jump to this part of the video ↗]({timestamp_url})")
        
        st.write(f"**Question:** {question} {timestamp_info}")
        
        # User's answer
        user_answer = st.session_state.answers.get(exercise_id, "No answer provided")
        st.write("**Your answer:**")
        st.info(user_answer)
        
        # Correct answer
        st.write("**Correct answer:**")
        correct_answer = exercise.get("correct_answer", "No correct answer specified")
        st.success(correct_answer)
        
        # For multiple choice, show all options
        if exercise_type == 'multiple_choice' and 'options' in exercise:
            st.write("**All options were:**")
            
            options = exercise.get('options', [])
            for option in options:
                if option == correct_answer:
                    st.success(f"✓ {option}")
                else:
                    st.write(f"- {option}")
        
        # Feedback
        st.write("**Feedback:**")
        if result.get("correct", False):
            st.success(result.get("feedback", "Correct!"))
        else:
            st.error(result.get("feedback", "Incorrect"))

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
                # Create columns for the exercise list
                for ex in saved_exercises:
                    with st.container():
                        ex_id = ex['id']
                        title = f"{ex['jlpt_level']} - {ex['topic'] if ex['topic'] else 'General'}"
                        
                        # Create two columns for info and button
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**{title}**")
                            st.write(f"Questions: {ex['num_questions']} | Has Audio: {'Yes' if ex['has_audio'] else 'No'}")
                        
                        with col2:
                            # Create a unique key for each button
                            button_key = f"load_{ex_id}_{hash(str(ex))}"
                            
                            # When button is clicked, directly set the session state and rerun
                            if st.button("Load", key=button_key):
                                try:
                                    st.info(f"Loading exercise {ex_id}...")
                                    
                                    # Get the full exercise data
                                    exercise = audio_generator.get_exercise_by_id(ex_id)
                                    
                                    if exercise:
                                        # Check audio file existence
                                        if exercise.get('main_audio') and not os.path.exists(exercise.get('main_audio', '')):
                                            exercise['has_audio'] = False
                                        
                                        # Set up the session state directly
                                        st.session_state.audio_exercise = exercise
                                        st.session_state.audio_exercise_id = ex_id
                                        st.session_state.audio_answers = {}
                                        st.session_state.from_generate = False
                                        
                                        # Force UI refresh
                                        st.rerun()
                                    else:
                                        st.error(f"Could not load exercise: {ex_id}")
                                except Exception as e:
                                    st.error(f"Error loading exercise: {str(e)}")
                                    st.error(traceback.format_exc())
                        st.divider()
            else:
                st.info("No saved exercises found. Generate a new one!")
        except Exception as e:
            st.error(f"Error loading saved exercises: {str(e)}")
            st.error(traceback.format_exc())
    else:
        exercise = st.session_state.audio_exercise
        
        # Display exercise details
        jlpt_level = exercise.get('jlpt_level', 'N4')
        display_level = exercise.get('display_level', f"JLPT {jlpt_level}")
        st.header(f"{display_level} Listening Exercise")
        
        if exercise.get('topic'):
            st.subheader(f"Topic: {exercise['topic']}")
        
        # Audio playback
        has_audio = False
        try:
            if exercise.get('main_audio') and os.path.exists(exercise['main_audio']):
                has_audio = True
                st.subheader("Listen to the Audio")
                audio_player_html = get_audio_player(exercise['main_audio'])
                st.markdown(audio_player_html, unsafe_allow_html=True)
                st.info("Listen to the audio carefully, then answer the questions below.")
                
                # Clear the HTML reference after displaying
                del audio_player_html
                gc.collect()
            else:
                st.warning("No audio available for this exercise. You can still answer the questions.")
                # Update the exercise to mark audio as missing
                exercise['has_audio'] = False
        except Exception as e:
            st.error(f"Error playing audio: {str(e)}")
            st.warning("Audio playback failed, but you can still answer the questions.")
        
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
                # Clear the exercise and navigate back to the exercise generator
                st.session_state.audio_exercise = None
                st.session_state.audio_exercise_id = None
                st.session_state.audio_answers = {}
                # Make sure the from_generate flag is not set
                st.session_state.from_generate = False
                # Force refresh
                st.rerun()
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
    try:
        if exercise.get('main_audio') and os.path.exists(exercise['main_audio']):
            st.subheader("Listen to the Audio Again")
            audio_player_html = get_audio_player(exercise['main_audio'])
            st.markdown(audio_player_html, unsafe_allow_html=True)
            
            # Clear the HTML reference after displaying
            del audio_player_html
            gc.collect()
    except Exception as e:
        st.error(f"Error playing audio: {str(e)}")
        st.warning("Audio playback failed, but you can still review your answers.")
    
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
        if st.button("Try Another Exercise"):
            # Clear the exercise and navigate back to the exercise generator
            st.session_state.audio_exercise = None
            st.session_state.audio_exercise_id = None
            st.session_state.audio_answers = {}
            # Make sure the from_generate flag is not set
            st.session_state.from_generate = False
            st.session_state.app_state = APP_STATES["AUDIO_EXERCISE"]
            st.rerun()
    with col2:
        st.button("Back to Home", on_click=go_to_home)

# Add a new function to extract questions from YouTube transcript using Ollama (which is open source)
def extract_questions_from_youtube(video_url):
    try:
        # Validate the YouTube URL
        video_id = extract_youtube_id(video_url)
        if not video_id:
            st.error("無効なYouTube URLです。有効なURLを入力してください。(Invalid YouTube URL. Please provide a valid URL.)")
            # Show examples of valid URLs
            st.info("有効なURL例 (Valid URL examples):\n- https://www.youtube.com/watch?v=2aqVJS6QOoY\n- https://youtu.be/2aqVJS6QOoY")
            return None
            
        st.info(f"処理中のビデオID: {video_id} (Processing video ID: {video_id})")
        
        # Get transcript using youtube_transcript_api (open source)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'ja-JP'])
            st.success("日本語字幕を正常に取得しました！(Japanese transcript successfully retrieved!)")
        except Exception as e:
            st.error(f"日本語字幕の取得に失敗しました: {str(e)} (Failed to get Japanese transcript)")
            st.info("いずれかの利用可能な字幕を取得しようとしています... (Trying to get any available transcript...)")
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                st.success("字幕を取得しました（非日本語）。(Transcript retrieved (non-Japanese).)")
            except Exception as e2:
                st.error(f"いずれの字幕も取得できませんでした: {str(e2)} (Failed to get any transcript)")
                # Try to get auto-generated transcript as last resort
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en', 'auto'])
                    st.success("自動生成された字幕を取得しました。(Auto-generated transcript retrieved.)")
                except Exception as e3:
                    st.error("このビデオに利用可能な字幕がありません。(No transcript available for this video.)")
                    return None
            
        # Format transcript for processing
        formatted_transcript = []
        for segment in transcript:
            formatted_transcript.append({
                "start": segment["start"],
                "text": segment["text"],
                "duration": segment["duration"]
            })
            
        # Show transcript preview for debugging
        with st.expander("字幕の内容 (Transcript Content)", expanded=False):
            st.write(f"取得した字幕セグメント: {len(formatted_transcript)}個 (Found {len(formatted_transcript)} transcript segments)")
            if len(formatted_transcript) > 0:
                st.write("字幕の内容 (Transcript content):")
                for segment in formatted_transcript:
                    st.write(f"{segment['start']:.1f}s: {segment['text']}")
        
        # Extract ONLY REAL questions from the transcript (questions actually asked in the video)
        actual_questions = []
        
        # Combine all transcript text
        full_text = " ".join([segment["text"] for segment in formatted_transcript])
        st.info(f"字幕内の文字数: {len(full_text)}文字 (Transcript length: {len(full_text)} characters)")
        
        # Japanese question detection patterns
        import re
        question_patterns = [
            # Pattern for questions ending with ka (か) and question mark
            r'([^。？！]*[か][？])',
            # Pattern for questions ending with ka (か) and period
            r'([^。？！]*[か][。])',
            # Pattern for questions ending with a question mark
            r'([^。？！]*[？])',
            # Pattern for polite questions
            r'([^。？！]*(?:ですか|ますか|のですか|のでしょうか)[？。]?)',
            # Pattern for questions with interrogatives
            r'([^。？！]*(?:何|なに|どう|なぜ|どこ|誰|だれ|いつ|どんな|どの)[^。？！]*[か][？。]?)'
        ]
        
        # Find all questions in the transcript
        for pattern in question_patterns:
            matches = re.finditer(pattern, full_text)
            for match in matches:
                question_text = match.group(0).strip()
                
                # Skip very short questions or duplicates
                if len(question_text) < 10:
                    continue
                    
                if question_text in [q["question_text"] for q in actual_questions]:
                    continue
                
                # Find which segment this question appears in
                segment_idx = None
                for idx, segment in enumerate(formatted_transcript):
                    if question_text in segment["text"]:
                        segment_idx = idx
                        break
                
                # If we couldn't find the segment, try to find the most relevant one
                if segment_idx is None:
                    for idx, segment in enumerate(formatted_transcript):
                        for word in question_text.split():
                            if len(word) > 2 and word in segment["text"]:
                                segment_idx = idx
                                break
                        if segment_idx is not None:
                            break
                
                # If we still couldn't find a segment, use the first segment
                if segment_idx is None:
                    segment_idx = 0
                
                # Get the segment containing this question
                segment = formatted_transcript[segment_idx]
                
                # Get context (surrounding segments)
                context_before = []
                for i in range(max(0, segment_idx - 2), segment_idx):
                    context_before.append(formatted_transcript[i]["text"])
                    
                context_after = []
                for i in range(segment_idx + 1, min(len(formatted_transcript), segment_idx + 3)):
                    context_after.append(formatted_transcript[i]["text"])
                
                # Add the question
                actual_questions.append({
                    "question_text": question_text,
                    "segment_start": segment["start"],
                    "segment_end": segment["start"] + segment["duration"],
                    "context_before": " ".join(context_before),
                    "context_after": " ".join(context_after)
                })
        
        # Check if we found any questions
        if not actual_questions:
            st.warning("動画から直接質問を見つけることができませんでした。(No direct questions found in the video.)")
            
            # Extract conversation segments as a fallback
            conversations = extract_conversations(formatted_transcript)
            
            # If we have conversations, show them
            if conversations:
                st.success(f"{len(conversations)}個の会話を見つけました。(Found {len(conversations)} conversations.)")
                return {
                    "type": "conversations",
                    "conversations": conversations
                }
            else:
                st.error("この動画から質問や会話を抽出できませんでした。(Could not extract questions or conversations.)")
                return None
                
        # Sort questions by timestamp
        actual_questions.sort(key=lambda q: q["segment_start"])
        
        # If Ollama is available, try to translate the questions
        if st.session_state.get("ollama_available", False):
            for question in actual_questions:
                try:
                    import requests
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": st.session_state.get("ollama_model", "mistral"),
                            "prompt": f"Translate this Japanese text to English: {question['question_text']}",
                        },
                        stream=False,
                        timeout=5
                    )
                    if response.status_code == 200:
                        question["english_translation"] = response.json().get('response', '')
                except:
                    question["english_translation"] = "(Translation unavailable)"
        
        # Return the list of questions
        return {
            "type": "questions",
            "questions": actual_questions
        }
        
    except Exception as e:
        st.error(f"Error extracting questions: {str(e)}")
        return None

def generate_options_for_question(question_text, context):
    """Generate plausible answer options for a question based on its content and context"""
    # Default options if generation fails
    default_options = ["はい (Yes)", "いいえ (No)", "わかりません (Not sure)"]
    
    try:
        # Import requests for Ollama API
        import requests
        
        # Prepare a prompt that asks for realistic options based on the question and context
        prompt = f"""Based on this Japanese question: "{question_text}" 
        And its context: "{context}"
        
        Generate 3-4 plausible answer options in Japanese (with English translations in parentheses).
        Format each option on a new line starting with a dash.
        
        Example:
        - はい、好きです (Yes, I like it)
        - いいえ、好きではありません (No, I don't like it)
        - 時々好きです (I like it sometimes)
        """
        
        # Call Ollama to generate options
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": st.session_state.get("ollama_model", "mistral"),
                "prompt": prompt,
            },
            stream=False,
            timeout=5
        )
        
        if response.status_code == 200:
            # Extract the generated options
            options_text = response.json().get('response', '')
            
            # Parse the options from the text
            import re
            option_pattern = r'[-•*]\s*(.*?)(?=\n[-•*]|\n\n|$)'
            matches = re.finditer(option_pattern, options_text, re.DOTALL)
            
            options = []
            for match in matches:
                option = match.group(1).strip()
                if option:
                    options.append(option)
            
            # If we got valid options, return them
            if len(options) >= 2:
                return options
    except:
        pass
    
    # Return default options if generation failed
    return default_options

def render_extract_questions():
    st.title("Extract Questions from YouTube")
    
    if "youtube_url" not in st.session_state:
        st.session_state["youtube_url"] = ""
        
    if "extracted_content" not in st.session_state:
        st.session_state["extracted_content"] = None
    
    # Form for URL input
    st.write("### Enter a Japanese YouTube URL")
    youtube_url = st.text_input(
        "日本語 YouTube URL (Japanese YouTube URL)", 
        value=st.session_state.get("youtube_url", ""), 
        key="youtube_url_input",
        help="例: https://www.youtube.com/watch?v=2aqVJS6QOoY"
    )
    
    # Extract button
    col1, col2 = st.columns([3, 1])
    with col2:
        extract_btn = st.button("質問を抽出する (Extract Questions)", key="extract_btn", use_container_width=True)
    
    if extract_btn:
        if not youtube_url:
            st.error("YouTubeのURLを入力してください (Please enter a YouTube URL)")
        else:
            st.session_state["youtube_url"] = youtube_url
            with st.spinner("動画から質問を抽出しています... (Extracting questions from video...)"):
                try:
                    result = extract_questions_from_youtube(youtube_url)
                    if result:
                        st.session_state["extracted_content"] = result
                        if result["type"] == "questions":
                            st.success(f"✅ 成功! {len(result['questions'])}個の質問を抽出しました (Successfully extracted {len(result['questions'])} questions)")
                        else:
                            st.success(f"✅ 成功! {len(result['conversations'])}個の会話を抽出しました (Successfully extracted {len(result['conversations'])} conversations)")
                        st.rerun()  # Refresh to display the content
                    else:
                        st.error("この動画から質問を抽出できませんでした。他の動画を試してください。(Could not extract any questions from this video.)")
                except Exception as e:
                    st.error(f"エラー: {str(e)} (Error processing video)")
                    st.info("別の動画を試すか、インターネット接続を確認してください。(Try a different video URL or check your internet connection.)")
    
    # Display the video if we have content
    if st.session_state.get("extracted_content") and st.session_state.get("youtube_url"):
        video_id = extract_youtube_id(st.session_state["youtube_url"])
        if video_id:
            st.video(f"https://www.youtube.com/watch?v={video_id}")
    
    # Display content if we have it
    if st.session_state.get("extracted_content"):
        content = st.session_state["extracted_content"]
        
        if content["type"] == "questions":
            # Display questions
            questions = content["questions"]
            
            st.markdown("## 動画から抽出された質問 (Questions Extracted from Video)")
            
            for i, question in enumerate(questions):
                with st.expander(f"質問 {i+1}", expanded=True):
                    st.subheader(f"{question['question_text']}")
                    
                    # Display English translation if available
                    if question.get("english_translation"):
                        st.info(f"English: {question['english_translation']}")
                    
                    # Display context
                    st.markdown("### 会話の文脈 (Conversation Context)")
                    
                    if question.get("context_before"):
                        st.markdown("**前 (Before):**")
                        st.markdown(f"*{question['context_before']}*")
                    
                    if question.get("context_after"):
                        st.markdown("**後 (After):**")
                        st.markdown(f"*{question['context_after']}*")
                    
                    # Add timestamp link
                    video_id = extract_youtube_id(st.session_state["youtube_url"])
                    if video_id:
                        start_time = int(question["segment_start"])
                        st.markdown(f"[この質問を動画で見る (Watch this question in the video)](https://www.youtube.com/watch?v={video_id}&t={start_time}s)")
        else:
            # Display conversations
            conversations = content["conversations"]
            
            st.markdown("## 動画から抽出された会話 (Conversations Extracted from Video)")
            
            for i, conversation in enumerate(conversations):
                with st.expander(f"会話 {i+1}", expanded=True):
                    st.markdown("### 会話内容 (Conversation)")
                    st.markdown(f"*{conversation['text']}*")
                    
                    # Try to translate if Ollama is available
                    if st.session_state.get("ollama_available", False):
                        if st.button(f"翻訳する (Translate)", key=f"translate_{i}"):
                            try:
                                import requests
                                with st.spinner("翻訳中... (Translating...)"):
                                    response = requests.post(
                                        "http://localhost:11434/api/generate",
                                        json={
                                            "model": st.session_state.get("ollama_model", "mistral"),
                                            "prompt": f"Translate this Japanese text to English: {conversation['text']}",
                                        },
                                        stream=False,
                                        timeout=10
                                    )
                                    if response.status_code == 200:
                                        translation = response.json().get('response', '')
                                        st.markdown("### 英語訳 (English Translation)")
                                        st.markdown(f"*{translation}*")
                            except Exception as e:
                                st.error(f"翻訳エラー: {str(e)} (Translation error)")
                    
                    # Add timestamp link
                    video_id = extract_youtube_id(st.session_state["youtube_url"])
                    if video_id:
                        start_time = int(conversation["start_time"])
                        st.markdown(f"[この会話を動画で見る (Watch this conversation in the video)](https://www.youtube.com/watch?v={video_id}&t={start_time}s)")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ホームに戻る (Return to Home)", use_container_width=True):
            # Clear extraction results
            if "extracted_content" in st.session_state:
                del st.session_state["extracted_content"]
            go_to_home()
    with col2:
        if st.button("別の動画を選ぶ (Select Another Video)", use_container_width=True):
            # Clear extraction results
            if "extracted_content" in st.session_state:
                del st.session_state["extracted_content"]
            go_to_video_selection()

# Update main app logic to handle the new state
def main():
    # Initialize session state for app_state if it doesn't exist
    if "app_state" not in st.session_state:
        st.session_state["app_state"] = APP_STATES["HOME"]
        
    try:
        # First, check and install any missing requirements
        check_and_install_requirements()
            
        # Check if backend is running
        backend_url = find_backend_server()
        st.session_state["backend_available"] = backend_url is not None
        
        # Check if Ollama is available
        if "ollama_available" not in st.session_state:
            try:
                import requests
                response = requests.get("http://localhost:11434/api/version", timeout=2)
                st.session_state["ollama_available"] = response.status_code == 200
                # Default model
                st.session_state["ollama_model"] = "mistral"
            except:
                st.session_state["ollama_available"] = False
        
        # Render the appropriate page based on app_state
        if st.session_state["app_state"] == APP_STATES["HOME"]:
            render_home()
        elif st.session_state["app_state"] == APP_STATES["VIDEO_SELECTION"]:
            render_video_selection()
        elif st.session_state["app_state"] == APP_STATES["PRACTICE"]:
            render_practice()
        elif st.session_state["app_state"] == APP_STATES["REVIEW"]:
            render_review()
        elif st.session_state["app_state"] == APP_STATES["PROCESSING_VIDEO"]:
            render_processing_video()
        elif st.session_state["app_state"] == APP_STATES["AUDIO_EXERCISE"]:
            render_audio_exercise()
        elif st.session_state["app_state"] == APP_STATES["AUDIO_EXERCISE_REVIEW"]:
            render_audio_exercise_review()
        elif st.session_state["app_state"] == APP_STATE_EXTRACT_QUESTIONS:
            render_extract_questions()
        else:
            # Invalid state, reset to home
            st.session_state["app_state"] = APP_STATES["HOME"]
            render_home()
    except Exception as e:
        # Provide a friendly error message and recovery options
        st.error(f"An error occurred in the application: {str(e)}")
        
        # Show detailed error in an expander for debugging
        with st.expander("Error Details", expanded=False):
            st.code(traceback.format_exc())
            
        # Offer recovery options
        st.warning("You can try to restart the application or go back to the home page")
        
        if st.button("Go to Home Page"):
            st.session_state["app_state"] = APP_STATES["HOME"]
            st.rerun()

# Main app rendering based on state - update this section to call main() or to include the new app state
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
elif st.session_state.app_state == APP_STATE_EXTRACT_QUESTIONS:
    # Clear the startup placeholder once we're in the main UI
    startup_placeholder.empty()
    render_extract_questions()

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
    
    # System status indicator
    st.subheader("System Status")
    if backend_running:
        st.success("Backend: Connected")
    else:
        st.error("Backend: Not connected")
        st.info("YouTube processing requires the backend server to be running.")
        st.caption("JLPT exercises will still work without the backend.")
    
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