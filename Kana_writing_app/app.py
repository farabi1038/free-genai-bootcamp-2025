import streamlit as st
import requests
import json
import os
import tempfile
import time
import base64
from PIL import Image
import io
from io import BytesIO

# Try to import streamlit-drawable-canvas
try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False
    st.error("The streamlit-drawable-canvas package is not installed. Please run: pip install streamlit-drawable-canvas")

# Import custom modules
from sentence_generator import generate_sentence
from grading_system import grade_submission
from config import VOCABULARY_API_URL, DEFAULT_VOCABULARY, DEBUG

# Page configuration
st.set_page_config(
    page_title="Kana Writing Practice",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
        color: #2E2E2E; /* Dark gray for better readability */
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #333333; /* Dark gray for better readability */
    }
    .sentence-display {
        font-size: 1.7rem;
        padding: 1.5rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin: 2rem 0;
        text-align: center;
        color: #333333;
        font-weight: 500;
    }
    .japanese-sentence {
        font-size: 1.7rem;
        color: #2E7D32;
        margin-top: 0.5rem;
    }
    .feedback-container {
        padding: 1.5rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin: 1.5rem 0;
    }
    .grade {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
    }
    .grade-S {
        color: #4CAF50;
    }
    .grade-A {
        color: #8BC34A;
    }
    .grade-B {
        color: #CDDC39;
    }
    .grade-C {
        color: #FFC107;
    }
    .grade-D {
        color: #FF9800;
    }
    .grade-F {
        color: #F44336;
    }
    .drawing-instructions {
        margin-bottom: 15px;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        border-left: 4px solid #4CAF50;
        color: #333333; /* Adding dark text color for better readability */
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "state" not in st.session_state:
    st.session_state.state = "setup"
if "english_sentence" not in st.session_state:
    st.session_state.english_sentence = ""
if "japanese_sentence" not in st.session_state:
    st.session_state.japanese_sentence = ""
if "vocabulary" not in st.session_state:
    st.session_state.vocabulary = []
if "current_word" not in st.session_state:
    st.session_state.current_word = None
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "canvas_result" not in st.session_state:
    st.session_state.canvas_result = None

def fetch_vocabulary():
    """Fetch vocabulary from the API or use default if API is not available"""
    try:
        # Try connecting to the API server with a short timeout
        st.info(f"Connecting to vocabulary API at {VOCABULARY_API_URL}")
        response = requests.get(VOCABULARY_API_URL, timeout=2)
        if response.status_code == 200:
            data = response.json()
            st.success(f"Successfully connected to vocabulary API. Retrieved {len(data)} words.")
            return data
        else:
            st.warning(f"Could not fetch vocabulary from API: {response.status_code}. Using default vocabulary.")
            return DEFAULT_VOCABULARY
    except requests.exceptions.RequestException as e:
        # More user-friendly error message for connection issues
        if DEBUG:
            st.info(f"No vocabulary API found at {VOCABULARY_API_URL}. Using built-in vocabulary list.")
        else:
            st.info("Using built-in vocabulary list for practice.")
        return DEFAULT_VOCABULARY

def reset_to_setup():
    """Reset the app state to setup"""
    st.session_state.state = "setup"
    st.session_state.english_sentence = ""
    st.session_state.japanese_sentence = ""
    st.session_state.current_word = None
    st.session_state.feedback = None
    st.session_state.canvas_result = None

def move_to_practice(english_sentence, japanese_sentence, word):
    """Move to practice state with the generated sentences"""
    st.session_state.state = "practice"
    st.session_state.english_sentence = english_sentence
    st.session_state.japanese_sentence = japanese_sentence
    st.session_state.current_word = word

def move_to_review(feedback):
    """Move to review state with the feedback"""
    st.session_state.state = "review"
    st.session_state.feedback = feedback

def save_canvas_as_image(canvas_result):
    """Save the canvas result as an image file"""
    # Convert the canvas result image data to a PIL Image
    img_data = canvas_result.image_data
    
    # Create a temporary file to save the image
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        pil_image = Image.fromarray(img_data.astype('uint8'))
        pil_image.save(tmp.name)
        tmp_filename = tmp.name
    
    return tmp_filename

# Application header
st.markdown("<div class='main-header'>Kana Writing Practice</div>", unsafe_allow_html=True)

# Load vocabulary if not already loaded
if not st.session_state.vocabulary:
    with st.spinner("Loading vocabulary..."):
        st.session_state.vocabulary = fetch_vocabulary()

# Main application logic based on current state
if st.session_state.state == "setup":
    st.markdown("Welcome to Kana Writing Practice! Click the button below to generate an English sentence for translation practice.")
    
    if st.button("Generate Sentence", use_container_width=True):
        with st.spinner("Generating sentence using local Ollama LLM..."):
            # Random word selection from vocabulary
            if st.session_state.vocabulary:
                import random
                word = random.choice(st.session_state.vocabulary)
                
                # Generate sentence using our local LLM and get both English and Japanese
                english_sentence, japanese_sentence = generate_sentence(word["english"], include_japanese=True)
                
                # Debug output
                st.write(f"Generated English: {english_sentence}")
                st.write(f"Generated Japanese: {japanese_sentence}")
                
                move_to_practice(english_sentence, japanese_sentence, word)
                st.rerun()
            else:
                st.error("No vocabulary available. Please check your API connection or restart the application.")

elif st.session_state.state == "practice":
    st.markdown("<div class='sub-header'>Translate this sentence to Japanese:</div>", unsafe_allow_html=True)
    
    # Display the English sentence
    st.markdown(f"<div class='sentence-display'>{st.session_state.english_sentence}</div>", unsafe_allow_html=True)
    
    # Always show the reference Japanese translation - Make this more prominent
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #4CAF50;">
        <h3 style="margin-top: 0; color: #2E7D32; font-size: 1.2rem;">Reference Japanese Translation:</h3>
        <p style="font-size: 1.5rem; margin-bottom: 0; color: #2E7D32; font-weight: 500;">{}</p>
    </div>
    """.format(st.session_state.japanese_sentence), unsafe_allow_html=True)
    
    # Input method tabs
    tabs = st.tabs(["Draw with Mouse/Touchscreen", "Upload Photo"])
    
    # Tab 1: Draw with Mouse using streamlit-drawable-canvas
    with tabs[0]:
        if CANVAS_AVAILABLE:
            st.markdown("<div class='drawing-instructions'>Use your mouse or touchscreen to draw the Japanese characters below. Try to match the reference translation.</div>", unsafe_allow_html=True)
            
            # Create drawing controls
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                stroke_width = st.slider("Brush Size", 1, 25, 3)
            with col2:
                stroke_color = st.color_picker("Brush Color", "#000000")
            with col3:
                bg_color = st.color_picker("Background Color", "#FFFFFF")
            
            # Create the canvas for drawing
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0.0)",  # Transparent fill
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color=bg_color,
                height=350,
                width=600,
                drawing_mode="freedraw",
                key="canvas",
                display_toolbar=True,
            )
            
            # If there's drawing data on the canvas
            if canvas_result.image_data is not None and canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0:
                if st.button("Submit for Review", use_container_width=True, key="canvas_submit"):
                    with st.spinner("Processing your drawing..."):
                        # Save the canvas as an image
                        tmp_filename = save_canvas_as_image(canvas_result)
                        
                        # Add a small delay to show the spinner (purely for UX)
                        time.sleep(1)
                        
                        # Get feedback from the grading system
                        feedback = grade_submission(
                            image_path=tmp_filename,
                            original_sentence=st.session_state.english_sentence,
                            target_word=st.session_state.current_word
                        )
                        
                        # Clean up the temporary file
                        os.unlink(tmp_filename)
                        
                        move_to_review(feedback)
                        st.rerun()
        else:
            st.error("The streamlit-drawable-canvas package is not installed. Please run: pip install streamlit-drawable-canvas")
            if st.button("Continue without drawing"):
                st.rerun()
    
    # Tab 2: Upload Photo
    with tabs[1]:
        st.markdown("<div class='sub-header'>Upload your handwritten translation:</div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose an image of your handwritten Japanese...", type=["jpg", "jpeg", "png"])
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Your handwritten Japanese", use_column_width=True)
                
                if st.button("Submit for Review", use_container_width=True, key="upload_submit"):
                    with st.spinner("Processing with local MangaOCR and Ollama..."):
                        # Save the uploaded image to a temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                            img_bytes = uploaded_file.getvalue()
                            tmp.write(img_bytes)
                            tmp_filename = tmp.name
                        
                        # Add a small delay to show the spinner (purely for UX)
                        time.sleep(1)
                        
                        # Get feedback from the grading system
                        feedback = grade_submission(
                            image_path=tmp_filename,
                            original_sentence=st.session_state.english_sentence,
                            target_word=st.session_state.current_word
                        )
                        
                        # Clean up the temporary file
                        os.unlink(tmp_filename)
                        
                        move_to_review(feedback)
                        st.rerun()

elif st.session_state.state == "review":
    st.markdown("<div class='sub-header'>Original Sentence:</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sentence-display'>{st.session_state.english_sentence}</div>", unsafe_allow_html=True)
    
    feedback = st.session_state.feedback
    
    st.markdown("<div class='feedback-container'>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='grade grade-{feedback['grade']}'>Grade: {feedback['grade']}</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sub-header'>Transcription:</div>", unsafe_allow_html=True)
    st.markdown(f"<p>{feedback['transcription']}</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='sub-header'>Translation:</div>", unsafe_allow_html=True)
    st.markdown(f"<p>{feedback['translation']}</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='sub-header'>Feedback:</div>", unsafe_allow_html=True)
    st.markdown(f"<p>{feedback['feedback']}</p>", unsafe_allow_html=True)
    
    # Show the reference Japanese translation
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #4CAF50;">
        <h3 style="margin-top: 0; color: #2E7D32; font-size: 1.2rem;">Reference Japanese Translation:</h3>
        <p style="font-size: 1.5rem; margin-bottom: 0; color: #2E7D32; font-weight: 500;">{}</p>
    </div>
    """.format(st.session_state.japanese_sentence), unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Next Sentence", use_container_width=True):
        reset_to_setup()
        st.rerun() 