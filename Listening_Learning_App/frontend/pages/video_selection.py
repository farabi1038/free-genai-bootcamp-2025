"""
Video selection page module for the Listening Learning App frontend
"""

import streamlit as st
from Listening_Learning_App.frontend.processors.youtube import extract_youtube_id, process_custom_video
from Listening_Learning_App.frontend.utils.session import go_to_home, go_to_processing_video, go_to_extract_questions

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