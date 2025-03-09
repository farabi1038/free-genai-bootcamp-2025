"""
Session state management for the Listening Learning App frontend
"""

import streamlit as st

# Define app states
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

# Navigation functions
def go_to_home():
    """Navigate to home page"""
    st.session_state.app_state = APP_STATES["HOME"]

def go_to_video_selection():
    """Navigate to video selection page"""
    st.session_state.app_state = APP_STATES["VIDEO_SELECTION"]

def go_to_practice(video_id):
    """
    Navigate to practice page for a specific video
    
    Parameters:
        video_id (str): The video ID to practice with
    """
    st.session_state.app_state = APP_STATES["PRACTICE"]
    st.session_state.video_id = video_id
    
    # Load exercises for this video
    try:
        from processors.video import load_exercises
        load_exercises(video_id)
    except:
        # Will be handled in the practice page
        pass

def go_to_review():
    """Navigate to review page"""
    st.session_state.app_state = APP_STATES["REVIEW"]

def go_to_processing_video(video_url):
    """
    Navigate to video processing page
    
    Parameters:
        video_url (str): The YouTube URL to process
    """
    st.session_state.app_state = APP_STATES["PROCESSING_VIDEO"]
    st.session_state.processing_video_url = video_url

def go_to_audio_exercise():
    """Navigate to audio exercise page"""
    st.session_state.app_state = APP_STATES["AUDIO_EXERCISE"]

def go_to_audio_exercise_review():
    """Navigate to audio exercise review page"""
    st.session_state.app_state = APP_STATES["AUDIO_EXERCISE_REVIEW"]

def go_to_extract_questions():
    """Navigate to extract questions page"""
    st.session_state.app_state = APP_STATE_EXTRACT_QUESTIONS
    
    # Clear any previous extraction results when navigating to the page
    if "extracted_content" in st.session_state:
        del st.session_state["extracted_content"] 