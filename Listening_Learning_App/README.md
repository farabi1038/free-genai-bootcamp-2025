# Japanese Listening Learning App

A fully local and open-source application for Japanese listening comprehension practice.

## Overview

This application helps Japanese language learners practice their listening comprehension by:
- Fetching Japanese listening comprehension videos from YouTube
- Generating JLPT-style listening exercises with realistic audio
- Creating practice content using local AI models
- Storing information locally with SQLite3
- Providing a user-friendly Streamlit interface for practice sessions

## Features

- **Local-First Design**: All processing and content storage happens on your machine
- **YouTube Integration**: Fetch content from YouTube for authentic Japanese listening materials
- **JLPT-Style Audio Generation**: Create realistic listening exercises with both male and female voices
- **Automatic Speech Recognition**: Utilize Whisper ASR for high-quality, local transcription
- **LLM-Generated Practice**: Generate questions and exercises using locally-hosted Ollama
- **Multi-Speaker Audio**: Dialogues with distinct speakers for a more authentic experience
- **Text-to-Speech**: Convert text to speech using free, open-source tools
- **Progress Tracking**: Store learning history and track progress over time

## Technical Components

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **ASR**: Whisper (local, free and open-source)
- **LLM**: Ollama (local)
- **TTS**: Combination of pyttsx3 (offline) and gTTS (online)
- **Audio Processing**: FFmpeg for combining multiple audio segments
- **Database**: SQLite3
- **YouTube Integration**: youtube-transcript-api, yt-dlp

## Directory Structure

- `frontend/`: Streamlit UI and user interaction
- `backend/`: FastAPI server and business logic
- `utils/`: Helper functions and utilities including TTS and exercise generation
- `data/`: Storage for SQLite database, audio files, and cached content
- `models/`: Configuration for local AI models

## Installation

1. Clone the repository
2. Set up a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Make sure you have Ollama installed and running with a Japanese-capable model (default: llama3.2:1b)
   ```
   # Install Ollama from https://ollama.com/
   # Then run:
   ollama pull llama3.2:1b
   ```
5. Make sure you have FFmpeg installed (required for audio processing)
   - Windows: Download from https://ffmpeg.org/download.html
   - MacOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

6. For Linux users, install espeak for better local TTS support:
   ```
   sudo apt-get install espeak
   ```
   (Note: If espeak is not installed, the app will fall back to online gTTS)

## Usage

### Quick Start

Use the provided startup scripts which will automatically check for dependencies and install any missing ones:

- **Windows**: Double-click `start.bat`
- **Linux/MacOS**: Run `./start.sh` (make it executable first with `chmod +x start.sh`)

### Manual Start

Run the application using the Python script:
```
python run.py
```

Additional options:
```
python run.py --auto-install  # Automatically install missing Python packages
python run.py --skip-checks   # Skip dependency checks
python run.py --frontend-only # Start only the frontend
python run.py --backend-only  # Start only the backend
```

### YouTube Video Practice

1. Start the app and click on "YouTube Videos"
2. Enter a YouTube URL or choose from the available videos
3. Listen to the content and answer the comprehension questions
4. Submit your answers to see your results

### JLPT-Style Audio Practice

1. Start the app and click on "JLPT-Style Audio Exercises"
2. Choose to create a new exercise or load a previously generated one
3. When creating a new exercise:
   - Select a JLPT level (N5-N1)
   - Optionally specify a topic (restaurant, travel, etc.)
   - Choose the number of questions
4. The app will generate:
   - A realistic JLPT-style listening script with announcer and speakers
   - Audio for the script with different voices for each speaker
   - Multiple-choice questions for comprehension
5. Listen to the audio and answer the questions
6. Submit your answers to see your score

### Dependency Checks

The application automatically checks for:
- Required Python packages
- System dependencies (FFmpeg)
- Ollama availability and models
- Whisper models (will be downloaded automatically if not found)

## Troubleshooting

### Ollama Issues
- Make sure Ollama is running with `ollama serve`
- If you're getting model errors, verify your available models with `ollama list`
- The app is configured to use "llama3.2:1b" by default. If you have a different model, specify it when running:
  ```
  python run.py --ollama-model llama3:latest
  ```
- If you encounter out-of-memory errors, stick with the smaller "llama3.2:1b" model (1.3GB) instead of "llama3:latest" (4.7GB)
- For better generation quality with lower memory usage, try closing other applications while running the app

### TTS Issues
- On Linux, if you're getting errors about "libespeak.so.1", install the espeak library:
  ```
  sudo apt-get install espeak
  ```
- If offline TTS (pyttsx3) fails, the app will automatically fall back to online TTS (gTTS)

### FFmpeg Issues
- Make sure FFmpeg is installed and available in your PATH
- Test with `ffmpeg -version` to verify it's working

## New Features

### Text-to-Audio Generation

The app now supports generating realistic JLPT-style listening exercises with:
- Multiple speakers (male and female voices)
- Announcer role for questions
- Proper formatting of Japanese questions and answers
- Exercise storage and retrieval
- Automatic scoring

### Audio Exercise Storage

- Generated exercises are stored locally for future use
- Exercises can be selected from the sidebar or exercise list
- Audio files are cached to avoid regeneration

## License

This project is open-source and free to use. 