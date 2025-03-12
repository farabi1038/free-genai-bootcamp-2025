import re
from typing import Dict
import logging

logger = logging.getLogger('song_vocab')

def generate_song_id(title: str) -> Dict[str, str]:
    """
    Generate a URL-safe song ID from a song title which may include artist name.
    
    Args:
        title (str): The song title, possibly including artist name
        
    Returns:
        Dict[str, str]: Dictionary containing the generated song_id
    """
    logger.info(f"Generating song ID for: {title}")
    
    def clean_string(s: str) -> str:
        # Remove special characters and convert to lowercase
        s = re.sub(r'[^\w\s-]', '', s.lower())
        # Replace spaces with hyphens
        return re.sub(r'[-\s]+', '-', s).strip('-')
    
    # Try to split artist and song if possible
    parts = title.split(' - ')
    if len(parts) > 1:
        artist, song = parts[0], parts[1]
    else:
        # Try to find artist name at the beginning
        parts = title.split(' ', 1)
        if len(parts) > 1:
            artist, song = parts[0], parts[1]
        else:
            # Just use the whole string
            artist = ""
            song = title
    
    # Clean the strings
    artist_clean = clean_string(artist) if artist else ""
    song_clean = clean_string(song)
    
    # Generate the song ID
    if artist_clean:
        song_id = f"{artist_clean}-{song_clean}"
    else:
        song_id = song_clean
    
    # Ensure the ID isn't too long for a filename
    if len(song_id) > 100:
        song_id = song_id[:100]
    
    logger.info(f"Generated song ID: {song_id}")
    return {"song_id": song_id}
