# Song-Vocab Application

## Overview

Song-Vocab is an intelligent application designed to help language learners expand their Japanese vocabulary through song lyrics. The application automatically finds lyrics for target songs, extracts vocabulary items, and formats them for learning purposes.

## Features

- **Automated Lyric Discovery**: Searches the web to find authentic Japanese song lyrics based on user queries
- **Intelligent Content Extraction**: Analyzes web pages to extract the most relevant lyrics content
- **Vocabulary Extraction**: Identifies and breaks down Japanese vocabulary from lyrics
- **Structured Data Output**: Converts raw lyrics into structured vocabulary items with kanji, romaji, and meanings
- **Persistence**: Saves lyrics and vocabulary to both files and database for future reference

## Technical Architecture

### Tech Stack

- **Backend Framework**: FastAPI
- **LLM Integration**: Ollama with Llama 3.2 (1B parameter model)
- **Structured Output**: Instructor for JSON schema validation
- **Database**: SQLite3 for local storage
- **Web Search**: DuckDuckGo Search API and SERP API for finding lyrics

### ReAct Agent Framework

The core of Song-Vocab is a ReAct (Reasoning and Acting) agent that:
1. Reasons about the user's request
2. Decides which tools to use
3. Executes tools to collect information
4. Extracts vocabulary from the collected content
5. Saves results for retrieval

## Installation

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai/) installed with the Llama 3.2 (1B) model

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/song-vocab.git
   cd song-vocab
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create a `.env` file in the project root with the following:
   ```
   SERP_API_KEY="your_serp_api_key_here"
   OLLAMA_HOST="http://localhost:11434"
   ```

5. Ensure Ollama is running with the required model:
   ```bash
   ollama pull llama3.2:1b
   ```

## Usage

### Starting the Server

Run the FastAPI server:
```bash
python main.py
```

The server will be available at `http://localhost:8000`.

### API Endpoints

#### POST /api/agent

Request song lyrics and extract vocabulary.

**Request Format**:
```json
{
  "message_request": "YOASOBI 夜に駆ける"
}
```

**Response Format**:
```json
{
  "song_id": "yoasobi-yorunikakeru",
  "lyrics": "夢の続き 見させて...",
  "vocabulary": [
    {
      "kanji": "夢",
      "romaji": "yume",
      "english": "dream",
      "parts": [
        { "kanji": "夢", "romaji": ["yu", "me"] }
      ]
    },
    // More vocabulary items...
  ]
}
```

## Project Structure

```
song-vocab/
│
├── outputs/              # Storage for processed data
│   ├── lyrics/           # Text files of song lyrics
│   └── vocabulary/       # JSON files of extracted vocabulary
│
├── prompts/              # LLM prompts
│   ├── Lyrics-Agent.md   # Main agent prompt
│   └── Extract-Vocabulary.md # Vocabulary extraction prompt
│
├── tools/                # Agent tools
│   ├── extract_vocabulary.py    # LLM-based vocabulary extraction
│   ├── get_page_content.py      # Web page content extraction
│   ├── search_web_serp.py       # SERP API search
│   ├── search_web_duckduckgo.py # DuckDuckGo search
│   ├── generate_song_id.py      # ID generation for songs
│   └── save_results.py          # File storage utilities
│
├── main.py              # FastAPI server
├── agent.py             # ReAct agent implementation
├── database.py          # SQLite database operations
├── requirements.txt     # Project dependencies
└── .env                 # Environment variables (not in repo)
```

## How It Works

1. User submits a song request via the API
2. The ReAct agent searches for lyrics using DuckDuckGo or SERP API
3. The agent extracts content from the most relevant page
4. LLM-based vocabulary extraction processes the lyrics
5. Results are saved to files and database
6. API returns the song_id, lyrics, and structured vocabulary

## Agent Tools

- **search_web_duckduckgo**: Searches for lyrics using DuckDuckGo
- **search_web_serp**: Alternative search using SERP API
- **get_page_content**: Extracts clean content from web pages
- **extract_vocabulary**: Uses LLM to extract vocabulary items
- **generate_song_id**: Creates unique identifiers for songs
- **save_results**: Persists data to file system

## Database Schema

The SQLite database maintains a vocabulary table with:
- Word (kanji form)
- Definition
- Example usage
- Related song and artist
- Creation timestamp

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**:
   - Ensure Ollama is running (`ollama serve`)
   - Verify OLLAMA_HOST in .env points to the correct host

2. **API Key Problems**:
   - Check that SERP_API_KEY is properly set in .env
   - For free usage, prefer the DuckDuckGo search tool

3. **Model Not Found**:
   - Run `ollama pull llama3.2:1b` to download the required model

## Development

### Adding New Tools

To extend the agent's capabilities:
1. Create a new tool in the `tools/` directory
2. Register it in the `ToolRegistry` class in `agent.py`
3. Update the prompts to include the new tool

### Modifying LLM Prompts

Prompts are stored in the `prompts/` directory:
- `Lyrics-Agent.md`: Main system prompt for the ReAct agent
- `Extract-Vocabulary.md`: Instructions for vocabulary extraction

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project uses the [Ollama](https://ollama.ai/) framework for local LLM inference
- Instructor library for structured output from LLMs
- DuckDuckGo and SERP API for web search capabilities