"""
YouTube processing utilities for the Listening Learning App frontend
"""

import re
import streamlit as st
import requests
import logging
import json
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

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

def process_custom_video(video_url):
    """
    Process a custom YouTube video URL
    
    This function sends the video URL to the backend for processing.
    
    Parameters:
        video_url (str): YouTube URL
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Validate the URL
    video_id = extract_youtube_id(video_url)
    if not video_id:
        st.error("Invalid YouTube URL format")
        return False
    
    # Check if backend is available
    if not st.session_state.get("backend_available", False):
        st.error("Backend server is not running")
        return False
    
    # Make API request to backend
    try:
        backend_url = st.session_state.get("backend_url", "http://localhost:8000")
        api_url = f"{backend_url}/api/videos/process"
        
        response = requests.post(
            api_url,
            json={"video_url": video_url},
            timeout=5  # 5 second timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"Processing started for video: {video_id}")
            
            # Store the processing job ID in session state
            st.session_state.processing_job_id = result.get("job_id")
            return True
        else:
            st.error(f"Error processing video: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        return False

def load_exercises(video_id):
    """
    Load exercises for a specific video
    
    Parameters:
        video_id (str): YouTube video ID
    
    Returns:
        list: List of exercises, or None if not found
    """
    # Check if backend is available
    if not st.session_state.get("backend_available", False):
        st.error("Backend server is not running. Cannot load exercises.")
        return None
    
    # Make API request to backend
    try:
        backend_url = st.session_state.get("backend_url", "http://localhost:8000")
        api_url = f"{backend_url}/api/exercises/video/{video_id}"
        
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            exercises = response.json()
            st.session_state.exercises = exercises
            return exercises
        elif response.status_code == 404:
            st.warning("No exercises found for this video")
            return []
        else:
            st.error(f"Error loading exercises: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error loading exercises: {str(e)}")
        return None 