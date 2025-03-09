# Kana Writing Practice App

## Overview
The Kana Writing Practice App is an interactive educational tool designed to help students practice translating English sentences into written Japanese (Kana). The application leverages local AI technologies, combining Ollama for LLM tasks and MangaOCR for handwriting recognition to provide a complete offline learning experience.

![Kana Writing Practice Screenshot](https://i.imgur.com/placeholder.png) _(Replace with actual screenshot)_

## Features

### Core Functionality
- **AI-Generated Practice Sentences**: Creates English sentences with corresponding Japanese translations
- **Multiple Input Methods**: Draw directly in the app or upload photos of handwritten Japanese
- **Local OCR Processing**: Uses MangaOCR for offline Japanese text recognition
- **Intelligent Grading**: Provides feedback on translation accuracy with letter grades (S-F)
- **Detailed Feedback**: Shows transcription, translation, and improvement suggestions
- **Completely Offline**: Works without internet once dependencies are installed

### Drawing Tools
- **Interactive Canvas**: User-friendly drawing interface for practicing kana writing
- **Brush Customization**: Adjust stroke width, color, and background color
- **Built-in Controls**: Includes undo/redo functionality and clear canvas option
- **Support for Multiple Devices**: Works with mouse, trackpad, and touchscreens

## Requirements

- Python 3.10 or higher
- Ollama installed locally ([ollama.com/download](https://ollama.com/download))
- llama3.2:1b model (or other compatible model)
- Sufficient RAM (4GB+) and disk space for models

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/kana-writing-app.git
   cd kana-writing-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```

5. Ensure Ollama is installed and running with the llama3.2:1b model:
   ```
   # If you haven't already installed the model
   ollama pull llama3.2:1b
   ```

## Usage

1. Start the application:
   ```
   python run.py
   ```

2. The application will:
   - Check for and initialize Ollama 
   - Verify or download the MangaOCR model
   - Start the Streamlit interface
   - Automatically open in your browser (or provide a URL)

3. Learning Flow:
   - Click "Generate Sentence" to get an English sentence with Japanese translation
   - Draw the Japanese characters using the canvas or upload a photo of handwritten text
   - Submit for review to receive feedback on your translation
   - View detailed analysis of your writing with grading and suggestions
   - Continue with another sentence to practice more

## Technical Implementation

### Architecture
The application is built with a modular architecture:

- **app.py**: Main Streamlit interface and user workflow
- **sentence_generator.py**: Handles English sentence generation and Japanese translation
- **grading_system.py**: Processes handwritten text and provides evaluation
- **config.py**: Centralized configuration management
- **run.py**: Application launcher with environment checks

### AI Integration
- **Local LLM (Ollama)**:
  - Sentence generation using vocabulary words
  - Translation between English and Japanese
  - Evaluation of translation accuracy
  - Uses llama3.2:1b model by default (lightweight, fast performance)

- **MangaOCR**:
  - Local Japanese OCR processing
  - Trained specifically for handwritten Japanese text
  - Runs completely offline once downloaded

### User Interface
- **Streamlit**: Powers the interactive web interface
- **streamlit-drawable-canvas**: Provides the drawing functionality
- **Three-state flow**: Setup → Practice → Review

## Configuration Options

The application can be configured through environment variables in the `.env` file:

- `LLM_PROVIDER`: Set to "ollama" for local inference
- `OLLAMA_MODEL`: The model to use (default: llama3.2:1b)
- `OLLAMA_API_ENDPOINT`: API endpoint for Ollama (default: http://localhost:11434/api/chat)
- `DEBUG`: Enable/disable debug mode (default: True)
- `VOCABULARY_API_URL`: URL for vocabulary API (fallbacks to built-in vocabulary)

## Troubleshooting

- **Ollama Connection Issues**: Ensure Ollama is running (`ollama serve`)
- **Model Not Found**: Run `ollama pull llama3.2:1b` to download the model
- **Drawing Problems**: Make sure streamlit-drawable-canvas is installed
- **OCR Quality Issues**: Ensure clear handwriting with good contrast
- **Grading System Errors**: Restart the application or try a different Ollama model

## Performance Considerations

- **RAM Usage**: MangaOCR and Ollama models require significant RAM
- **GPU Acceleration**: Speeds up OCR if available
- **Model Size**: llama3.2:1b is chosen for balance between quality and speed
- **First-Time Startup**: Initial model downloads may take time

## Future Improvements

- Custom vocabulary list management
- User performance tracking over time
- Additional writing practice modes
- Support for kanji recognition and learning
- Export/import functionality for progress tracking

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the web application framework
- [MangaOCR](https://github.com/kha-white/manga-ocr) for Japanese text recognition
- [Ollama](https://ollama.com/) for local LLM capabilities
- [streamlit-drawable-canvas](https://github.com/andfanilo/streamlit-drawable-canvas) for the drawing interface 