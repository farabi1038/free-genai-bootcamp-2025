"""
Audio utilities for the Listening Learning App frontend
"""

import streamlit as st
import os
import base64
import logging
from pathlib import Path
import tempfile

# Configure logging
logger = logging.getLogger(__name__)

def get_audio_exercise_generator():
    """Get the configured audio exercise generator engine"""
    # For now, always return 'ollama' as it's the default
    return 'ollama'

def get_tts_engine():
    """Get the configured TTS engine"""
    # For now, always return 'gtts' as it's the default
    return 'gtts'

def get_audio_player(audio_path, autoplay=False):
    """
    Generate an HTML audio player for the given audio file
    
    Parameters:
        audio_path (str): Path to the audio file
        autoplay (bool): Whether to autoplay the audio
    
    Returns:
        str: HTML audio player markup
    """
    try:
        # Check if the file exists
        if not os.path.isfile(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return f"<p>Audio file not found: {audio_path}</p>"
        
        # Get file extension
        file_ext = os.path.splitext(audio_path)[1].lower()
        
        # Set MIME type based on file extension
        mime_types = {
            '.mp3': 'audio/mp3',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.m4a': 'audio/mp4',
        }
        mime_type = mime_types.get(file_ext, 'audio/mpeg')
        
        # Read audio file
        audio_bytes = Path(audio_path).read_bytes()
        
        # Encode as base64
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # Create HTML audio element
        audio_html = f"""
        <audio {' autoplay' if autoplay else ''} controls>
            <source src="data:{mime_type};base64,{audio_base64}" type="{mime_type}">
            Your browser does not support the audio element.
        </audio>
        """
        
        return audio_html
    except Exception as e:
        logger.error(f"Error creating audio player: {e}")
        return f"<p>Error loading audio: {str(e)}</p>"

def text_to_speech(text, output_path=None, engine='gtts', language='ja'):
    """
    Convert text to speech using the specified engine
    
    Parameters:
        text (str): Text to convert to speech
        output_path (str, optional): Path to save the audio file. If None, a temporary file is created.
        engine (str): TTS engine to use ('gtts' or 'pyttsx3')
        language (str): Language code (for gtts)
    
    Returns:
        str: Path to the generated audio file
    """
    if not output_path:
        # Create a temporary file
        fd, output_path = tempfile.mkstemp(suffix='.mp3')
        os.close(fd)
    
    try:
        if engine == 'gtts':
            # Use Google Text-to-Speech
            from gtts import gTTS
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(output_path)
        elif engine == 'pyttsx3':
            # Use pyttsx3 (offline TTS)
            import pyttsx3
            engine = pyttsx3.init()
            engine.save_to_file(text, output_path)
            engine.runAndWait()
        else:
            logger.error(f"Unsupported TTS engine: {engine}")
            return None
            
        return output_path
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        return None 