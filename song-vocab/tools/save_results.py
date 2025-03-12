from typing import List, Dict, Any
import json
import logging
from pathlib import Path
import os

logger = logging.getLogger('song_vocab')

def save_results(song_id: str, lyrics: str = None, vocabulary: List[Dict[str, Any]] = None, lyrics_path: Path = None, vocabulary_path: Path = None) -> str:
    """
    Save lyrics and vocabulary to their respective files.
    
    Args:
        song_id (str): ID of the song
        lyrics (str): Japanese lyrics text
        vocabulary (List[Dict[str, Any]]): List of vocabulary items
        lyrics_path (Path): Directory to save lyrics files
        vocabulary_path (Path): Directory to save vocabulary files
    
    Returns:
        str: The song_id that was used to save the files
    """
    # Ensure song_id is clean and safe
    if not song_id:
        song_id = "default-song"
    
    # Ensure we have valid content
    lyrics = lyrics or "No lyrics were found for this song."
    vocabulary = vocabulary or []
    
    # Handle path defaults if not provided
    if lyrics_path is None:
        base_path = Path(os.getcwd())
        lyrics_path = base_path / "outputs" / "lyrics"
        lyrics_path.mkdir(parents=True, exist_ok=True)
        
    if vocabulary_path is None:
        base_path = Path(os.getcwd())
        vocabulary_path = base_path / "outputs" / "vocabulary"
        vocabulary_path.mkdir(parents=True, exist_ok=True)
    
    # Make sure directories exist
    lyrics_path.mkdir(parents=True, exist_ok=True)
    vocabulary_path.mkdir(parents=True, exist_ok=True)
    
    # Save lyrics
    lyrics_file = lyrics_path / f"{song_id}.txt"
    lyrics_file.write_text(lyrics)
    logger.info(f"Saved lyrics to {lyrics_file}")
    
    # Save vocabulary
    vocab_file = vocabulary_path / f"{song_id}.json"
    vocab_file.write_text(json.dumps(vocabulary, ensure_ascii=False, indent=2))
    logger.info(f"Saved vocabulary to {vocab_file}")
    
    return song_id
