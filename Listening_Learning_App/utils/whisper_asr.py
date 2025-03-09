import os
import whisper
import logging
import json
import tempfile
from pathlib import Path
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default model settings
DEFAULT_MODEL = "base"
AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

# Cache for loaded models
_model_cache = {}

def get_whisper_model(model_name=DEFAULT_MODEL):
    """
    Load and cache a Whisper model
    
    Args:
        model_name: Name of the Whisper model to load
        
    Returns:
        whisper.Model: Loaded model
    """
    if model_name not in AVAILABLE_MODELS:
        logger.warning(f"Unknown model '{model_name}'. Using '{DEFAULT_MODEL}' instead.")
        model_name = DEFAULT_MODEL
    
    # Check if model is already loaded
    if model_name in _model_cache:
        return _model_cache[model_name]
    
    # Load the model
    logger.info(f"Loading Whisper model: {model_name}")
    model = whisper.load_model(model_name)
    
    # Cache the model
    _model_cache[model_name] = model
    
    return model

async def transcribe_audio(audio_path, model_name=DEFAULT_MODEL, language="ja"):
    """
    Transcribe audio using Whisper
    
    Args:
        audio_path: Path to the audio file
        model_name: Name of the Whisper model to use
        language: Language of the audio
        
    Returns:
        dict: Transcription result
    """
    try:
        # Check if audio file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load the model
        model = get_whisper_model(model_name)
        
        # Load and preprocess audio
        logger.info(f"Transcribing audio: {audio_path}")
        
        # Set transcription options
        options = {
            "language": language,
            "task": "transcribe",
        }
        
        # Perform transcription
        result = model.transcribe(audio_path, **options)
        
        logger.info(f"Transcription complete: {len(result['segments'])} segments")
        
        return result
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise

async def save_transcription(transcription, output_path):
    """
    Save transcription result to a JSON file
    
    Args:
        transcription: Whisper transcription result
        output_path: Path to save the transcription
        
    Returns:
        str: Path to the saved file
    """
    try:
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcription, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Transcription saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error saving transcription: {str(e)}")
        raise

async def transcribe_segment(audio_path, start_time, end_time, model_name=DEFAULT_MODEL, language="ja"):
    """
    Transcribe a specific segment of an audio file
    
    Args:
        audio_path: Path to the audio file
        start_time: Start time in seconds
        end_time: End time in seconds
        model_name: Name of the Whisper model to use
        language: Language of the audio
        
    Returns:
        dict: Transcription result for the segment
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(audio_path)
        
        # Extract the segment
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)
        segment = audio[start_ms:end_ms]
        
        # Create a temporary file for the segment
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            segment_path = temp_file.name
            segment.export(segment_path, format="mp3")
        
        try:
            # Transcribe the segment
            result = await transcribe_audio(segment_path, model_name, language)
            return result
        finally:
            # Clean up the temporary file
            if os.path.exists(segment_path):
                os.unlink(segment_path)
        
    except Exception as e:
        logger.error(f"Error transcribing segment: {str(e)}")
        raise

async def process_audio_file(audio_path, output_dir, model_name=DEFAULT_MODEL, language="ja"):
    """
    Process an audio file with Whisper ASR and save the results
    
    Args:
        audio_path: Path to the audio file
        output_dir: Directory to save the results
        model_name: Name of the Whisper model to use
        language: Language of the audio
        
    Returns:
        str: Path to the saved transcription
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the base filename without extension
        base_name = Path(audio_path).stem
        output_path = output_dir / f"{base_name}_transcription.json"
        
        # Check if transcription already exists
        if output_path.exists():
            logger.info(f"Transcription already exists at {output_path}")
            with open(output_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Transcribe the audio
        transcription = await transcribe_audio(audio_path, model_name, language)
        
        # Save the transcription
        await save_transcription(transcription, output_path)
        
        return transcription
        
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        raise