import os
import logging
import tempfile
import pyttsx3
from gtts import gTTS
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TTS engines
ENGINE_PYTTSX3 = "pyttsx3"
ENGINE_GTTS = "gtts"

def text_to_speech(text, output_path=None, engine=ENGINE_PYTTSX3, language="ja"):
    """
    Convert text to speech and save to a file or return path to temporary file
    
    Args:
        text: Text to convert to speech
        output_path: Path to save the speech file (optional)
        engine: TTS engine to use (pyttsx3 or gtts)
        language: Language code for TTS
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        # Default to a temporary file if no output path is provided
        if not output_path:
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            output_path = temp_file.name
            temp_file.close()
        
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Generate speech
        if engine == ENGINE_PYTTSX3:
            _pyttsx3_tts(text, output_path)
        else:  # Default to gTTS
            _gtts_tts(text, output_path, language)
        
        logger.info(f"Text-to-speech generated at {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        raise

def _pyttsx3_tts(text, output_path):
    """
    Generate speech using pyttsx3 (works offline)
    
    Args:
        text: Text to convert to speech
        output_path: Path to save the speech file
    """
    try:
        engine = pyttsx3.init()
        
        # Save to file
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
    except Exception as e:
        logger.error(f"Error with pyttsx3: {str(e)}")
        raise

def _gtts_tts(text, output_path, language):
    """
    Generate speech using gTTS (requires internet)
    
    Args:
        text: Text to convert to speech
        output_path: Path to save the speech file
        language: Language code for TTS
    """
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Save to file
        tts.save(output_path)
        
    except Exception as e:
        logger.error(f"Error with gTTS: {str(e)}")
        raise

def get_available_voices(engine=ENGINE_PYTTSX3):
    """
    Get list of available voices for the specified engine
    
    Args:
        engine: TTS engine to use
        
    Returns:
        list: Available voices
    """
    if engine == ENGINE_PYTTSX3:
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            return voices
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return []
    else:
        # gTTS doesn't provide voice selection API
        return []

def set_speech_properties(rate=200, volume=1.0, voice=None, engine=ENGINE_PYTTSX3):
    """
    Set properties for speech generation (only works with pyttsx3)
    
    Args:
        rate: Speech rate (words per minute)
        volume: Volume (0.0 to 1.0)
        voice: Voice to use
        engine: TTS engine to use
    """
    if engine != ENGINE_PYTTSX3:
        logger.warning(f"Speech properties can only be set for {ENGINE_PYTTSX3}")
        return
    
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
        
        if voice:
            engine.setProperty('voice', voice)
            
    except Exception as e:
        logger.error(f"Error setting speech properties: {str(e)}")
        raise

def play_text(text, engine=ENGINE_PYTTSX3, language="ja"):
    """
    Play text as speech without saving to file
    
    Args:
        text: Text to convert to speech
        engine: TTS engine to use
        language: Language code for TTS
    """
    if engine == ENGINE_PYTTSX3:
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"Error playing speech: {str(e)}")
            raise
    else:
        # gTTS requires saving to a file, so we'll use a temporary file
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                output_path = temp_file.name
                
            _gtts_tts(text, output_path, language)
            
            # In a real implementation, this would play the audio
            # For simplicity, we're just returning the path
            logger.info(f"Speech saved to temporary file: {output_path}")
            logger.info("You would need to implement audio playback for this platform")
            
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)
                
        except Exception as e:
            logger.error(f"Error playing speech: {str(e)}")
            raise 