"""
Main entry point for the Listening Learning App frontend

This version uses direct imports but keeps the code clean and modular.
"""

import streamlit as st
import traceback
import logging
import requests
import sys
import os
from pathlib import Path
import json
import time
import socket
import re
from youtube_transcript_api import YouTubeTranscriptApi

# Fix import path
# Get the path to the parent directory of the Listening_Learning_App folder
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # Go up to Listening_Learning_App directory
sys.path.insert(0, str(project_root))  # Add to Python path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Additional app states
APP_STATE_EXTRACT_QUESTIONS = "EXTRACT_QUESTIONS"

# Function to check for Ollama availability
def check_ollama_availability():
    """Check if Ollama is available and set session state accordingly"""
    logger.info("Checking Ollama availability...")
    
    # First try to get the preferred model from config
    preferred_model = "llama3.2:1b"
    try:
        config_path = Path(__file__).parent.parent / "config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                if "ollama_model" in config:
                    preferred_model = config["ollama_model"]
                    logger.info(f"Found preferred Ollama model in config: {preferred_model}")
    except Exception as e:
        logger.warning(f"Error reading Ollama model from config: {e}")
    
    try:
        # Try to get available models from Ollama
        try:
            # Try tags endpoint first which shows available models
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                st.session_state["ollama_available"] = True
                
                # Parse the models from the response
                models_data = response.json()
                available_models = [model["name"] for model in models_data.get("models", [])]
                logger.info(f"Available Ollama models: {available_models}")
                
                # Set the model in the session state
                if available_models:
                    # Try to use the preferred model if available
                    if preferred_model in available_models:
                        st.session_state["ollama_model"] = preferred_model
                    else:
                        # Otherwise use the first available model
                        st.session_state["ollama_model"] = available_models[0]
                    
                    logger.info(f"Using Ollama model: {st.session_state['ollama_model']}")
                else:
                    # No models available, but Ollama is running
                    st.session_state["ollama_model"] = preferred_model
                    logger.warning(f"No models available in Ollama. Using default: {preferred_model}")
                
                return
        except Exception as e:
            # If tags endpoint fails, try version endpoint
            logger.warning(f"Error checking Ollama tags: {e}")
            
            try:
                response = requests.get("http://localhost:11434/api/version", timeout=2)
                if response.status_code == 200:
                    # Ollama is running but we couldn't get models
                    st.session_state["ollama_available"] = True
                    st.session_state["ollama_model"] = preferred_model
                    logger.info(f"Ollama is available but couldn't get models. Using default: {preferred_model}")
                    return
            except Exception as e2:
                logger.warning(f"Error checking Ollama version: {e2}")
        
        # If we get here, Ollama is not available
        logger.warning("Ollama is not available - couldn't connect to API")
        st.session_state["ollama_available"] = False
        st.session_state["ollama_model"] = preferred_model  # Still store the preferred model
        
    except Exception as e:
        logger.error(f"Error in Ollama availability check: {str(e)}")
        st.session_state["ollama_available"] = False
        st.session_state["ollama_model"] = preferred_model

# Is port in use
def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Find backend server
def find_backend_server():
    """
    Find the backend server by checking common ports.
    Returns the backend URL if found, otherwise None.
    """
    logger.info("Searching for backend server...")
    backend_url = None
    
    # First try to read from config file
    try:
        config_path = Path(__file__).parent.parent / "config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                backend_port = config.get('backend_port')
                if backend_port:
                    logger.info(f"Found backend port {backend_port} in config file")
                    # Try this port first
                    try:
                        url = f"http://localhost:{backend_port}/health"
                        response = requests.get(url, timeout=1)
                        if response.status_code == 200:
                            backend_url = f"http://localhost:{backend_port}"
                            logger.info(f"Successfully connected to backend at {backend_url}")
                            return backend_url
                    except:
                        logger.warning(f"Backend not found on configured port {backend_port}")
    except Exception as e:
        logger.warning(f"Could not read backend port from config: {e}")
    
    # Check common ports including the specific port 8040 used in your logs
    default_ports = [8040, 8000, 8080, 5000]
    
    # First check default ports
    for port in default_ports:
        try:
            url = f"http://localhost:{port}/health"
            response = requests.get(url, timeout=0.5)
            if response.status_code == 200:
                backend_url = f"http://localhost:{port}"
                logger.info(f"Found backend server at: {backend_url}")
                return backend_url
        except:
            continue
    
    # Narrow the port range to be more efficient
    # Focus on ports around 8040 where the backend is likely running
    range_ports = list(range(8030, 8050))
    logger.info(f"Checking port range {range_ports[0]}-{range_ports[-1]} for backend server...")
    
    for port in range_ports:
        try:
            url = f"http://localhost:{port}/health"
            response = requests.get(url, timeout=0.2)  # Use shorter timeout for range scan
            if response.status_code == 200:
                backend_url = f"http://localhost:{port}"
                logger.info(f"Found backend server at: {backend_url}")
                return backend_url
        except:
            continue

    if not backend_url:
        logger.warning("Could not find a running backend server")

    return backend_url

# Navigation functions
def go_to_home():
    """Navigate to home page"""
    st.session_state.app_state = APP_STATES["HOME"]

def go_to_video_selection():
    """Navigate to video selection page"""
    st.session_state.app_state = APP_STATES["VIDEO_SELECTION"]

def go_to_extract_questions():
    """Navigate to extract questions page"""
    st.session_state.app_state = APP_STATE_EXTRACT_QUESTIONS
    
    # Clear any previous extraction results when navigating to the page
    if "extracted_content" in st.session_state:
        del st.session_state["extracted_content"]

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if "app_state" not in st.session_state:
        st.session_state["app_state"] = APP_STATES["HOME"]
        
    # Check if backend is running
    if "backend_available" not in st.session_state:
        st.session_state["backend_available"] = False
        
    # Check if Ollama is available
    if "ollama_available" not in st.session_state:
        st.session_state["ollama_available"] = False
        st.session_state["ollama_model"] = "mistral"

# Extract YouTube ID
def extract_youtube_id(url):
    """
    Extract the video ID from a YouTube URL
    
    Parameters:
        url (str): YouTube URL
    
    Returns:
        str: YouTube video ID, or None if not found
    """
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

# Extract questions from YouTube
def extract_questions_from_youtube(video_url):
    """
    Extract questions from a YouTube video transcript
    
    Parameters:
        video_url (str): YouTube URL
    
    Returns:
        dict: Dictionary with extracted content (questions or conversations)
    """
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
            
        # Clean and format transcript for processing
        formatted_transcript = []
        for segment in transcript:
            # Clean the text - remove special characters and normalize
            text = segment["text"]
            # Replace common transcript artifacts
            text = text.replace("\n", " ")
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
            
            # Remove non-Japanese artifacts (often seen in auto-generated transcripts)
            text = re.sub(r'[a-zA-Z]\s\d+', '', text)  # Remove patterns like "n 5"
            text = re.sub(r'\(\d+\)', '', text)  # Remove patterns like "(123)"
            
            formatted_transcript.append({
                "start": segment["start"],
                "text": text.strip(),
                "duration": segment["duration"]
            })
            
        # Show transcript preview for debugging
        with st.expander("字幕の内容 (Transcript Content)", expanded=False):
            st.write(f"取得した字幕セグメント: {len(formatted_transcript)}個 (Found {len(formatted_transcript)} transcript segments)")
            if len(formatted_transcript) > 0:
                st.write("字幕の内容 (Transcript content):")
                for segment in formatted_transcript[:20]:  # Show first 20 segments to avoid overwhelming the UI
                    st.write(f"{segment['start']:.1f}s: {segment['text']}")
        
        # Combine segments into meaningful units for better context
        cleaned_transcript = []
        current_text = ""
        current_start = 0
        current_duration = 0
        
        for segment in formatted_transcript:
            # If the segment is very short, combine it with the previous one
            if len(current_text) == 0:
                # First segment
                current_text = segment["text"]
                current_start = segment["start"]
                current_duration = segment["duration"]
            elif len(segment["text"]) < 10 or len(current_text) < 20:
                # Combine short segments
                current_text += " " + segment["text"]
                current_duration += segment["duration"]
            else:
                # Add the current segment to the cleaned transcript
                cleaned_transcript.append({
                    "start": current_start,
                    "text": current_text,
                    "duration": current_duration
                })
                # Start a new segment
                current_text = segment["text"]
                current_start = segment["start"]
                current_duration = segment["duration"]
        
        # Add the last segment
        if current_text:
            cleaned_transcript.append({
                "start": current_start,
                "text": current_text,
                "duration": current_duration
            })
        
        # If cleaned transcript is too short, use the original
        if len(cleaned_transcript) < 5 and len(formatted_transcript) > 5:
            cleaned_transcript = formatted_transcript
        
        # Extract ONLY REAL questions from the transcript (questions actually asked in the video)
        actual_questions = []
        
        # Combine all transcript text for pattern matching
        full_text = " ".join([segment["text"] for segment in cleaned_transcript])
        st.info(f"字幕内の文字数: {len(full_text)}文字 (Transcript length: {len(full_text)} characters)")
        
        # Japanese question detection patterns
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
        
        # Process each segment for questions
        for segment_idx, segment in enumerate(cleaned_transcript):
            segment_text = segment["text"]
            
            # Apply each pattern to find questions in this segment
            for pattern in question_patterns:
                matches = re.finditer(pattern, segment_text)
                for match in matches:
                    question_text = match.group(0).strip()
                    
                    # Skip very short questions or duplicates
                    if len(question_text) < 10:
                        continue
                        
                    if question_text in [q["question_text"] for q in actual_questions]:
                        continue
                    
                    # Get context (surrounding segments)
                    # Get more context for better understanding
                    context_before = []
                    for i in range(max(0, segment_idx - 3), segment_idx):
                        if cleaned_transcript[i]["text"].strip():
                            context_before.append(cleaned_transcript[i]["text"])
                    
                    context_after = []
                    for i in range(segment_idx + 1, min(len(cleaned_transcript), segment_idx + 4)):
                        if cleaned_transcript[i]["text"].strip():
                            context_after.append(cleaned_transcript[i]["text"])
                    
                    # Join context with meaningful separators
                    context_before_text = " ... ".join(context_before) if context_before else ""
                    context_after_text = " ... ".join(context_after) if context_after else ""
                    
                    # Add the question
                    actual_questions.append({
                        "question_text": question_text,
                        "segment_start": segment["start"],
                        "segment_end": segment["start"] + segment["duration"],
                        "context_before": context_before_text,
                        "context_after": context_after_text,
                        "content_type": "質問 (Question)"
                    })
        
        # Check if we found any questions
        if not actual_questions:
            st.warning("動画から直接質問を見つけることができませんでした。(No direct questions found in the video.)")
            
            # Extract conversation segments as a fallback
            conversations = extract_conversations(cleaned_transcript, min_length=50)
            
            # If we have conversations, show them
            if conversations:
                st.success(f"{len(conversations)}個の会話を見つけました。(Found {len(conversations)} conversations.)")
                # Add content type to each conversation
                for conversation in conversations:
                    conversation["content_type"] = "会話 (Conversation)"
                return {
                    "type": "conversations",
                    "conversations": conversations
                }
            else:
                st.error("この動画から質問や会話を抽出できませんでした。(Could not extract questions or conversations.)")
                return None
                
        # Sort questions by timestamp
        actual_questions.sort(key=lambda q: q["segment_start"])
        
        # Return the list of questions
        return {
            "type": "questions",
            "questions": actual_questions
        }
        
    except Exception as e:
        st.error(f"Error extracting questions: {str(e)}")
        st.exception(e)  # Show the full exception for debugging
        return None

# Extract conversations from transcript
def extract_conversations(transcript_segments, min_length=50, max_segments=5):
    """
    Extract complete conversation segments from the transcript
    
    Parameters:
        transcript_segments (list): List of transcript segments
        min_length (int): Minimum length of a conversation in characters
        max_segments (int): Maximum number of conversation segments to extract
    
    Returns:
        list: List of conversation segments
    """
    conversations = []
    
    if not transcript_segments or len(transcript_segments) < 3:
        return conversations
    
    # Group transcript segments into meaningful conversations
    current_conversation = {
        "start_time": transcript_segments[0]["start"],
        "text": transcript_segments[0]["text"],
        "segments": [transcript_segments[0]],
        "end_time": transcript_segments[0]["start"] + transcript_segments[0]["duration"]
    }
    
    # Look for natural breaks in conversation (pauses, speaker changes, etc.)
    for i in range(1, len(transcript_segments)):
        current_segment = transcript_segments[i]
        previous_segment = transcript_segments[i-1]
        
        # Check if there's a significant pause between segments (more than 3 seconds)
        time_gap = current_segment["start"] - (previous_segment["start"] + previous_segment["duration"])
        
        # Check for segment breaks: significant time gap or very different content
        if time_gap > 3.0 or len(current_conversation["text"]) > 500:  # New conversation if gap > 3s or current is already long
            # Save previous conversation if it's long enough
            if len(current_conversation["text"]) >= min_length:
                # Calculate midpoint of conversation for timestamp
                mid_time = (current_conversation["start_time"] + current_conversation["end_time"]) / 2
                current_conversation["timestamp"] = mid_time
                conversations.append(current_conversation)
            
            # Start a new conversation
            current_conversation = {
                "start_time": current_segment["start"],
                "text": current_segment["text"],
                "segments": [current_segment],
                "end_time": current_segment["start"] + current_segment["duration"]
            }
        else:
            # Continue current conversation
            current_conversation["text"] += " " + current_segment["text"]
            current_conversation["segments"].append(current_segment)
            current_conversation["end_time"] = current_segment["start"] + current_segment["duration"]
    
    # Add the last conversation if it's long enough
    if len(current_conversation["text"]) >= min_length:
        # Calculate midpoint of conversation for timestamp
        mid_time = (current_conversation["start_time"] + current_conversation["end_time"]) / 2
        current_conversation["timestamp"] = mid_time
        conversations.append(current_conversation)
    
    # Clean up conversation text and split into meaningful segments if too long
    refined_conversations = []
    for conv in conversations:
        # Clean up text
        text = conv["text"]
        text = re.sub(r'\s+', ' ', text).strip()
        
        # If conversation is very long, try to split it into meaningful segments
        if len(text) > 1000:
            # Look for natural break points like sentence endings
            sentences = re.split(r'[。！？.!?]\s*', text)
            current_part = ""
            parts = []
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                
                if len(current_part) < 300:
                    current_part += sentence + "。 "
                else:
                    parts.append(current_part)
                    current_part = sentence + "。 "
            
            if current_part:
                parts.append(current_part)
            
            # Create a separate conversation for each meaningful part
            start_offset = 0
            for idx, part in enumerate(parts):
                segment_length = len(part) / len(text)  # Proportion of this segment
                duration = (conv["end_time"] - conv["start_time"]) * segment_length
                
                refined_conversations.append({
                    "start_time": conv["start_time"] + start_offset,
                    "text": part,
                    "timestamp": conv["start_time"] + start_offset + (duration / 2)
                })
                start_offset += duration
        else:
            # For shorter conversations, keep them as is but with cleaned text
            conv["text"] = text
            refined_conversations.append(conv)
    
    # Sort conversations by quality (based on length and completeness)
    # Higher quality conversations tend to be longer and contain complete sentences
    def conversation_quality(conv):
        text = conv["text"]
        # Higher scores for:
        # 1. Length (longer is better, up to a point)
        length_score = min(len(text) / 200, 5)  # Max score of 5 for length
        
        # 2. Completeness (ends with sentence ending)
        completeness_score = 2 if re.search(r'[。！？.!?]\s*$', text) else 0
        
        # 3. Question content (conversations with questions are interesting)
        question_score = text.count('？') + text.count('?') + text.count('か。') + text.count('ですか') + text.count('ますか')
        
        return length_score + completeness_score + question_score
    
    refined_conversations.sort(key=conversation_quality, reverse=True)
    
    # Limit to max_segments
    return refined_conversations[:max_segments]

# Set up page configuration
def setup_page():
    """Set up page configuration and styling"""
    st.set_page_config(
        page_title="Japanese Listening Practice",
        page_icon="🇯🇵",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom styles
    st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .main-header {
        color: #1E88E5;
    }
    </style>
    """, unsafe_allow_html=True)

# Render the home page
def render_home():
    """Render the home page"""
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
        st.button("JLPT-Style Audio Exercises", use_container_width=True)
        
    with col3:
        # Add a button to directly go to the question extraction page
        st.button("Extract Questions from YouTube", on_click=go_to_extract_questions, use_container_width=True)

# Render the video selection page
def render_video_selection():
    """Render the video selection page with YouTube URL input and saved videos"""
    st.title("Select a Video")
    
    # Check if backend is running and show status
    backend_running = st.session_state.get("backend_available", False)
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
                go_to_extract_questions()
    
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

# Render the question extraction page
def render_extract_questions():
    """Render the question extraction page"""
    st.title("YouTube動画から質問・会話を抽出 (Extract Questions/Conversations from YouTube)")
    
    if "youtube_url" not in st.session_state:
        st.session_state["youtube_url"] = ""
        
    if "extracted_content" not in st.session_state:
        st.session_state["extracted_content"] = None
    
    # Form for URL input
    st.write("### 日本語YouTubeのURLを入力 (Enter a Japanese YouTube URL)")
    youtube_url = st.text_input(
        "日本語 YouTube URL", 
        value=st.session_state.get("youtube_url", ""), 
        key="youtube_url_input",
        help="例: https://www.youtube.com/watch?v=2aqVJS6QOoY"
    )
    
    # Method selection
    st.write("### 抽出方法を選択 (Select Extraction Method)")
    
    extraction_methods = [
        "字幕から抽出 (Extract from Captions)",
        "AI抽出 (Whisper + Ollama)"
    ]
    
    # Default to AI method if Ollama is available, otherwise use captions method
    default_method_idx = 1 if st.session_state.get("ollama_available", False) else 0
    
    # Check if we already have a selected method in the session state
    if "extraction_method" not in st.session_state:
        st.session_state["extraction_method"] = extraction_methods[default_method_idx]
    
    # Display method selection
    col1, col2 = st.columns([3, 1])
    with col1:
        method = st.radio(
            "抽出方法 (Extraction Method)",
            extraction_methods,
            index=extraction_methods.index(st.session_state["extraction_method"]),
            horizontal=True
        )
        st.session_state["extraction_method"] = method
    
    # Extract button
    with col2:
        extract_btn = st.button("質問・会話を抽出する (Extract Questions/Conversations)", key="extract_btn", use_container_width=True)
    
    # Display help for methods - removed as per user request
    
    # Check if Ollama is available for AI method
    if method == "AI抽出 (Whisper + Ollama)" and not st.session_state.get("ollama_available", False):
        st.warning("""
        ⚠️ AI抽出にはOllamaが必要です。Ollamaが実行されていません。
        
        Ollamaをインストールしてから、`ollama serve`コマンドを実行してください。
        
        (AI extraction requires Ollama. Ollama is not running. Please install Ollama and run the `ollama serve` command.)
        """)
    
    if extract_btn:
        if not youtube_url:
            st.error("YouTubeのURLを入力してください。(Please enter a YouTube URL.)")
        else:
            st.session_state["youtube_url"] = youtube_url
            with st.spinner("動画から質問・会話を抽出しています... (Extracting content from video...)"):
                try:
                    # Use the selected method
                    if method == "AI抽出 (Whisper + Ollama)":
                        if st.session_state.get("ollama_available", False):
                            result = extract_questions_with_ai(youtube_url)
                        else:
                            st.error("Ollama が利用できないため、AI抽出を使用できません。字幕からの抽出を使用します。")
                            result = extract_questions_from_youtube(youtube_url)
                    else:
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
                    st.exception(e)
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
                with st.expander(f"質問 {i+1}: {question['question_text'][:30]}...", expanded=True):
                    # Display content type badge
                    st.markdown(f"**{question.get('content_type', '質問 (Question)')}**")
                    
                    # Display the full question
                    st.subheader(f"{question['question_text']}")
                    
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
                        # Use timestamp if available, otherwise use segment_start
                        if "timestamp" in question:
                            start_time = int(question["timestamp"])
                        else:
                            start_time = int(question["segment_start"])
                        st.markdown(f"[この質問を動画で見る (Watch this question in the video)](https://www.youtube.com/watch?v={video_id}&t={start_time}s)")
        else:
            # Display conversations
            conversations = content["conversations"]
            
            st.markdown("## 動画から抽出された会話 (Conversations Extracted from Video)")
            
            for i, conversation in enumerate(conversations):
                # Prepare a preview of the conversation (first ~30 chars)
                preview = conversation['text'][:30] + "..." if len(conversation['text']) > 30 else conversation['text']
                
                # Use the timestamp for linking to the video if available, otherwise use start_time
                timestamp = conversation.get('timestamp', conversation.get('start_time', 0))
                
                with st.expander(f"会話 {i+1}: {preview}", expanded=True):
                    # Display content type badge
                    st.markdown(f"**{conversation.get('content_type', '会話 (Conversation)')}**")
                    
                    # Display the conversation
                    st.markdown("### 会話内容 (Conversation Content)")
                    st.markdown(f"*{conversation['text']}*")
                    
                    # Add timestamp link
                    video_id = extract_youtube_id(st.session_state["youtube_url"])
                    if video_id:
                        start_time = int(timestamp)
                        st.markdown(f"[この会話を動画で見る (Watch this conversation in the video)](https://www.youtube.com/watch?v={video_id}&t={start_time}s)")
                        
                    # Add additional metadata if available
                    if 'start_time' in conversation and 'end_time' in conversation:
                        duration = conversation.get('end_time', 0) - conversation.get('start_time', 0)
                        if duration > 0:
                            st.caption(f"会話の時間: {int(conversation['start_time'])}秒 - {int(conversation['end_time'])}秒 (約{int(duration)}秒間)")
    
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

# Extract questions using Whisper + Llama
def extract_questions_with_ai(video_url):
    """
    Extract questions from a YouTube video using Whisper for transcription
    and a local LLM for question extraction and analysis
    
    Parameters:
        video_url (str): YouTube URL
    
    Returns:
        dict: Dictionary with extracted content (questions with context)
    """
    try:
        # Validate the YouTube URL
        video_id = extract_youtube_id(video_url)
        if not video_id:
            st.error("無効なYouTube URLです。有効なURLを入力してください。(Invalid YouTube URL. Please provide a valid URL.)")
            return None
        
        st.info(f"処理中のビデオID: {video_id} (Processing video ID: {video_id})")
        
        # Check if Ollama is available
        if not st.session_state.get("ollama_available", False):
            st.warning("Ollama が利用できないため、この機能は使用できません。(This feature requires Ollama to be available.)")
            return None
        
        # Step 1: Download audio from YouTube
        with st.spinner("YouTubeから音声をダウンロード中... (Downloading audio from YouTube...)"):
            try:
                # Check if yt-dlp is installed
                try:
                    import subprocess
                    subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
                except (FileNotFoundError, subprocess.CalledProcessError):
                    st.error("yt-dlp がインストールされていません。`pip install yt-dlp` を実行してください。(yt-dlp is not installed. Please run `pip install yt-dlp`.)")
                    return None
                
                # Create a temporary directory for downloaded files
                import tempfile
                import os
                
                temp_dir = tempfile.mkdtemp()
                audio_file = os.path.join(temp_dir, f"{video_id}.mp3")
                
                # Download audio only
                cmd = [
                    "yt-dlp", 
                    "-x", "--audio-format", "mp3", 
                    "--audio-quality", "0",
                    "-o", audio_file,
                    f"https://www.youtube.com/watch?v={video_id}"
                ]
                
                process = subprocess.run(cmd, capture_output=True, text=True)
                
                if process.returncode != 0:
                    st.error(f"音声のダウンロードに失敗しました: {process.stderr} (Failed to download audio)")
                    return None
                
                if not os.path.exists(audio_file):
                    # Check if .webm file was created instead
                    webm_file = os.path.join(temp_dir, f"{video_id}.webm")
                    if os.path.exists(webm_file):
                        audio_file = webm_file
                    else:
                        # Look for any audio file
                        files = os.listdir(temp_dir)
                        for file in files:
                            if file.startswith(video_id) and os.path.isfile(os.path.join(temp_dir, file)):
                                audio_file = os.path.join(temp_dir, file)
                                break
                        
                        if not os.path.exists(audio_file):
                            st.error("音声ファイルが見つかりませんでした。(Audio file not found.)")
                            return None
                
                st.success(f"音声ダウンロード完了: {audio_file} (Audio download complete)")
            
            except Exception as e:
                st.error(f"音声ダウンロード中にエラーが発生しました: {str(e)} (Error during audio download)")
                return None
        
        # Step 2: Transcribe audio using Whisper
        with st.spinner("Whisperで音声を文字起こし中... (Transcribing audio with Whisper...)"):
            try:
                # Check if whisper is installed
                try:
                    import whisper
                except ImportError:
                    st.error("Whisper がインストールされていません。`pip install openai-whisper` を実行してください。(Whisper is not installed. Please run `pip install openai-whisper`.)")
                    return None
                
                # Load the Whisper model
                model_size = "base"  # Options: tiny, base, small, medium, large
                model = whisper.load_model(model_size)
                
                # Transcribe the audio
                result = model.transcribe(audio_file, language="ja")
                transcript = result["text"]
                
                if not transcript:
                    st.error("文字起こしに失敗しました。(Transcription failed.)")
                    return None
                
                # Get segments with timestamps
                segments = result["segments"]
                
                # Display the transcript
                with st.expander("文字起こし結果 (Transcript)", expanded=False):
                    st.write(transcript)
                    st.write("---")
                    st.write("### セグメント (Segments)")
                    for segment in segments:
                        st.write(f"{segment['start']:.1f}s - {segment['end']:.1f}s: {segment['text']}")
                
                st.success(f"文字起こし完了: {len(transcript)} 文字 (Transcription complete: {len(transcript)} characters)")
                
            except Exception as e:
                st.error(f"文字起こし中にエラーが発生しました: {str(e)} (Error during transcription)")
                st.exception(e)
                return None
        
        # Step 3: Use Llama model to extract questions and context
        with st.spinner("LLMで質問と文脈を抽出中... (Extracting questions and context with LLM...)"):
            try:
                # Prepare the system prompt
                system_prompt = """
                あなたは日本語の会話から質問と会話の文脈を抽出する専門家です。
                以下の文字起こしから、実際に話し手が発した質問を抽出し、各質問の前後の文脈も含めてリストにしてください。

                質問の基準:
                - 「か？」「ですか？」「ますか？」などで終わる文
                - 疑問詞（何、どう、なぜ、どこ、誰、いつ、どんな）を含む文で、質問の意図があるもの
                - 明らかに質問として発せられた文

                出力形式:
                {
                    "questions": [
                        {
                            "question_text": "質問の文字列",
                            "context_before": "質問の前の文脈",
                            "context_after": "質問の後の文脈",
                            "timestamp": "質問が発せられたおおよその時間（秒）"
                        },
                        ...
                    ]
                }

                質問がない場合は、代わりに会話の重要な部分を以下の形式で抽出してください:
                {
                    "conversations": [
                        {
                            "text": "会話の重要な部分",
                            "timestamp": "会話が発せられたおおよその時間（秒）"
                        },
                        ...
                    ]
                }

                注意:
                - 質問が少なくとも1つある場合は questions 形式を使用してください
                - 質問がない場合のみ conversations 形式を使用してください
                - JSONとして有効な形式で出力してください
                - 実際の質問のみを抽出し、文字起こしエラーや不明瞭な部分は無視してください
                - 各質問には十分な文脈（前後少なくとも1-2文）を含めてください
                """
                
                # Get the selected model
                model = st.session_state.get("ollama_model", "llama3.2:1b")
                
                # Prepare the transcript (truncate if too long)
                max_length = 6000  # Avoid context length issues
                if len(transcript) > max_length:
                    # Try to find a good break point
                    truncated_transcript = transcript[:max_length]
                    last_period = truncated_transcript.rfind('。')
                    if last_period > max_length * 0.8:  # At least 80% of the max length
                        truncated_transcript = truncated_transcript[:last_period+1]
                    transcript = truncated_transcript
                    st.warning(f"文字起こしが長すぎるため、最初の{len(truncated_transcript)}文字のみを分析します。(Transcript is too long, analyzing only the first {len(truncated_transcript)} characters.)")
                
                # Call Ollama with the transcript
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": transcript,
                        "system": system_prompt,
                        "stream": False,
                        "format": "json"
                    },
                    timeout=60  # Increased timeout for longer processing
                )
                
                if response.status_code != 200:
                    st.error(f"LLMからのレスポンスエラー: {response.status_code} (LLM response error)")
                    return None
                
                result = response.json()
                ai_response = result.get('response', '')
                
                # Try to parse the JSON from the response
                import json
                try:
                    # Find JSON in the response
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = ai_response[json_start:json_end]
                        content = json.loads(json_str)
                    else:
                        # Try to parse the entire response
                        content = json.loads(ai_response)
                        
                    # Check if we have questions or conversations
                    if "questions" in content and content["questions"]:
                        # Add content type to each question
                        for question in content["questions"]:
                            question["content_type"] = "質問 (Question)"
                            # Ensure timestamp is an int or float
                            if "timestamp" in question and question["timestamp"]:
                                try:
                                    question["timestamp"] = float(question["timestamp"])
                                    question["segment_start"] = question["timestamp"]
                                    question["segment_end"] = question["timestamp"] + 5  # Approximate 5 seconds for the question
                                except:
                                    # If timestamp can't be converted, use 0
                                    question["timestamp"] = 0
                                    question["segment_start"] = 0
                                    question["segment_end"] = 5
                                    
                        st.success(f"✅ 成功! {len(content['questions'])}個の質問を抽出しました (Successfully extracted {len(content['questions'])} questions)")
                        return {
                            "type": "questions",
                            "questions": content["questions"]
                        }
                    elif "conversations" in content and content["conversations"]:
                        # Add content type to each conversation
                        for conversation in content["conversations"]:
                            conversation["content_type"] = "会話 (Conversation)"
                            # Ensure timestamp is an int or float
                            if "timestamp" in conversation and conversation["timestamp"]:
                                try:
                                    conversation["timestamp"] = float(conversation["timestamp"])
                                    conversation["start_time"] = conversation["timestamp"]
                                    conversation["end_time"] = conversation["timestamp"] + 10  # Approximate 10 seconds for the conversation
                                except:
                                    # If timestamp can't be converted, use 0
                                    conversation["timestamp"] = 0
                                    conversation["start_time"] = 0
                                    conversation["end_time"] = 10
                        
                        st.success(f"✅ 成功! {len(content['conversations'])}個の会話を抽出しました (Successfully extracted {len(content['conversations'])} conversations)")
                        return {
                            "type": "conversations",
                            "conversations": content["conversations"]
                        }
                    else:
                        st.error("LLMからの応答に質問または会話が含まれていませんでした。(No questions or conversations in LLM response.)")
                        with st.expander("LLMからの応答 (LLM Response)", expanded=False):
                            st.code(ai_response)
                        return None
                
                except json.JSONDecodeError as e:
                    st.error(f"JSONの解析に失敗しました: {str(e)} (Failed to parse JSON)")
                    with st.expander("LLMからの応答 (LLM Response)", expanded=False):
                        st.code(ai_response)
                    return None
                
            except Exception as e:
                st.error(f"質問抽出中にエラーが発生しました: {str(e)} (Error during question extraction)")
                st.exception(e)
                return None
            
        # Clean up
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass
        
    except Exception as e:
        st.error(f"Error in AI extraction process: {str(e)}")
        st.exception(e)
        return None

# Main app function
def main():
    """Main application function"""
    # Set up page
    setup_page()
    
    # Add a startup placeholder for initial loading
    startup_placeholder = st.empty()
    with startup_placeholder:
        st.info("Starting application...")
    
    try:
        # Initialize session state
        initialize_session_state()
            
        # Check if backend is running
        backend_url = find_backend_server()
        st.session_state["backend_available"] = backend_url is not None
        st.session_state["backend_url"] = backend_url
        
        # Check if Ollama is available
        if "ollama_available" not in st.session_state:
            check_ollama_availability()
        
        # Clear the startup placeholder once initialization is complete
        startup_placeholder.empty()
        
        # Render the appropriate page based on app_state
        if st.session_state["app_state"] == APP_STATES["HOME"]:
            render_home()
        elif st.session_state["app_state"] == APP_STATES["VIDEO_SELECTION"]:
            render_video_selection()
        elif st.session_state["app_state"] == APP_STATE_EXTRACT_QUESTIONS:
            render_extract_questions()
        # Additional pages can be added here as they are implemented
        else:
            # For now, any other state will default to home
            st.session_state["app_state"] = APP_STATES["HOME"]
            render_home()
            
    except Exception as e:
        # Provide a friendly error message and recovery options
        st.error(f"An error occurred in the application: {str(e)}")
        
        # Show detailed error in an expander for debugging
        with st.expander("Error Details", expanded=False):
            st.code(traceback.format_exc())
            
        # Offer recovery options
        st.warning("You can try to restart the application or reload the page.")
    
    # Sidebar with app information
    with st.sidebar:
        st.title("Japanese Listening Practice")
        st.markdown("---")
        
        # Display backend status
        if st.session_state.get("backend_available", False):
            st.success("✅ Backend server is running")
        else:
            st.warning("⚠️ Backend server is not running")
            st.info("Some features may be limited without a backend server.")
        
        # Display Ollama status with retry button
        if st.session_state.get("ollama_available", False):
            st.success("✅ Ollama is available")
            # Display model selection
            current_model = st.session_state.get("ollama_model", "llama3.2:1b")
            
            # Standard models that might be available
            standard_models = ["llama3.2:1b", "llama3", "mistral", "gemma", "codellama", "phi3", "wizardcoder", "solar", "qwen"]
            
            # Try to get available models from Ollama
            available_models = []
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=1)
                if response.status_code == 200:
                    models_data = response.json()
                    available_models = [model["name"] for model in models_data.get("models", [])]
            except:
                pass
            
            # Combine standard models with any discovered models
            model_options = list(set(standard_models + available_models))
            
            # If current model isn't in the list, add it
            if current_model not in model_options:
                model_options.append(current_model)
                
            # Sort the model options
            model = st.selectbox(
                "Selected model:",
                model_options,
                index=model_options.index(current_model) if current_model in model_options else 0
            )
            
            # Update model in session state
            if model != st.session_state.get("ollama_model"):
                st.session_state["ollama_model"] = model
                st.info(f"Model changed to {model}. This will be used for translations.")
                
            # Show a button to test the model
            if st.button("Test Translation"):
                with st.spinner("Testing model..."):
                    try:
                        test_text = "こんにちは、元気ですか？"
                        response = requests.post(
                            "http://localhost:11434/api/generate",
                            json={
                                "model": model,
                                "prompt": f"Translate this Japanese text to English: {test_text}",
                                "system": "You are a translator that translates Japanese to English.",
                                "stream": False
                            },
                            timeout=5
                        )
                        if response.status_code == 200:
                            translation = response.json().get('response', '').strip()
                            st.success(f"Translation successful! ({test_text} → {translation})")
                        else:
                            st.error(f"Error testing model: HTTP {response.status_code}")
                    except Exception as e:
                        st.error(f"Error testing model: {str(e)}")
        else:
            st.warning("⚠️ Ollama is not available")
            st.info("Ollama provides AI models for translation and analysis. Translation features will be limited without it.")
            
            # Add instructions to start Ollama
            with st.expander("How to start Ollama", expanded=True):
                st.markdown("""
                1. Open a terminal/command prompt
                2. Run the command: `ollama serve`
                3. Wait for Ollama to start
                4. Click the 'Retry Ollama Connection' button below
                """)
            
            # Add retry button
            if st.button("Retry Ollama Connection"):
                with st.spinner("Checking Ollama connection..."):
                    check_ollama_availability()
                if st.session_state.get("ollama_available", False):
                    st.success("✅ Successfully connected to Ollama!")
                    st.info("Please refresh the page to apply changes.")
                else:
                    st.error("❌ Still unable to connect to Ollama.")
                    st.info("Ensure Ollama is running with the command 'ollama serve' in a terminal window.")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app helps Japanese learners practice 
        listening comprehension through YouTube videos
        and AI-generated exercises.
        """)
        
        st.markdown("### Version")
        st.markdown("v1.0.0")

# Run the app
if __name__ == "__main__":
    main() 