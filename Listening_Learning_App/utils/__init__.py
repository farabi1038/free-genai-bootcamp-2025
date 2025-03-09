"""
Utilities for the Japanese Listening Learning App

This package contains utility modules for:
- YouTube integration (fetching videos and transcripts)
- Whisper ASR (automatic speech recognition)
- Ollama integration (LLM-based content generation and answer checking)
- TTS (text-to-speech)
"""

# Import key functions for convenience
from .youtube import (
    extract_video_id,
    get_video_info,
    get_youtube_transcript,
    download_youtube_audio,
    get_or_download_transcript
)

from .whisper_asr import (
    transcribe_audio,
    process_audio_file,
    transcribe_segment
)

from .ollama_integration import (
    OllamaClient,
    generate_exercises,
    check_answer,
    translate_text
)

from .tts import (
    text_to_speech,
    play_text,
    get_available_voices
) 