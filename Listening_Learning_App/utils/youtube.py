import os
import logging
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from pathlib import Path
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_video_id(youtube_url):
    """Extract the video ID from a YouTube URL"""
    # Regular expression to match YouTube video IDs
    patterns = [
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract video ID from URL: {youtube_url}")

async def get_video_info(youtube_url):
    """
    Get metadata about a YouTube video including title, duration, etc.
    
    Args:
        youtube_url: URL of the YouTube video
        
    Returns:
        dict: Video metadata
    """
    try:
        video_id = extract_video_id(youtube_url)
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'no_color': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
        return {
            'id': video_id,
            'title': info.get('title', 'Unknown Title'),
            'duration': info.get('duration', 0),
            'language': info.get('language', 'ja'),
            'description': info.get('description', ''),
            'url': youtube_url,
            'thumbnail': info.get('thumbnail', '')
        }
    
    except Exception as e:
        logger.error(f"Error fetching video info: {str(e)}")
        raise

async def get_youtube_transcript(youtube_url, language_code='ja'):
    """
    Get the transcript for a YouTube video in the specified language
    
    Args:
        youtube_url: URL of the YouTube video
        language_code: Language code for the transcript
        
    Returns:
        list: List of transcript segments
    """
    try:
        video_id = extract_video_id(youtube_url)
        
        # Try to get transcript in the specified language
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        except Exception as e:
            logger.warning(f"Could not get transcript in {language_code}, trying auto-generated: {str(e)}")
            # Try to get auto-generated transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # If we have a transcript, return it
        if transcript:
            return transcript
        else:
            logger.warning(f"No transcript available for video {video_id}")
            return []
            
    except Exception as e:
        logger.error(f"Error fetching transcript: {str(e)}")
        return []

async def save_transcript(transcript, output_dir, video_id, language_code='ja'):
    """
    Save the transcript to a JSON file
    
    Args:
        transcript: List of transcript segments
        output_dir: Directory to save the transcript
        video_id: YouTube video ID
        language_code: Language code for the transcript
        
    Returns:
        str: Path to the saved transcript file
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Format transcript to JSON
        formatter = JSONFormatter()
        json_formatted = formatter.format_transcript(transcript)
        
        # Save to file
        output_file = output_dir / f"{video_id}_{language_code}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_formatted)
        
        logger.info(f"Transcript saved to {output_file}")
        return str(output_file)
        
    except Exception as e:
        logger.error(f"Error saving transcript: {str(e)}")
        raise

async def download_youtube_audio(youtube_url, output_dir):
    """
    Download the audio from a YouTube video
    
    Args:
        youtube_url: URL of the YouTube video
        output_dir: Directory to save the audio
        
    Returns:
        str: Path to the downloaded audio file
    """
    try:
        video_id = extract_video_id(youtube_url)
        
        # Create output directory if it doesn't exist
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{video_id}.mp3"
        
        # Check if file already exists
        if output_path.exists():
            logger.info(f"Audio file already exists at {output_path}")
            return str(output_path)
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(output_path).replace('.mp3', ''),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True
        }
        
        # Download the audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        logger.info(f"Audio downloaded to {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Error downloading audio: {str(e)}")
        raise

async def get_or_download_transcript(youtube_url, output_dir, language_code='ja'):
    """
    Get the transcript for a YouTube video, either from an existing file or by downloading it
    
    Args:
        youtube_url: URL of the YouTube video
        output_dir: Directory to save the transcript
        language_code: Language code for the transcript
        
    Returns:
        list: List of transcript segments
    """
    video_id = extract_video_id(youtube_url)
    output_file = Path(output_dir) / f"{video_id}_{language_code}.json"
    
    # Check if transcript already exists
    if output_file.exists():
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                transcript = json.load(f)
            logger.info(f"Loaded existing transcript from {output_file}")
            return transcript
        except Exception as e:
            logger.warning(f"Error loading existing transcript: {str(e)}. Will download again.")
    
    # Download and save transcript
    transcript = await get_youtube_transcript(youtube_url, language_code)
    if transcript:
        await save_transcript(transcript, output_dir, video_id, language_code)
    
    return transcript 