"""
Home page module for the Listening Learning App frontend
"""

import streamlit as st
from Listening_Learning_App.frontend.utils.session import go_to_video_selection, go_to_audio_exercise, go_to_extract_questions

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
        st.button("JLPT-Style Audio Exercises", on_click=go_to_audio_exercise, use_container_width=True)
        
    with col3:
        # Add a button to directly go to the question extraction page
        st.button("Extract Questions from YouTube", on_click=go_to_extract_questions, use_container_width=True) 