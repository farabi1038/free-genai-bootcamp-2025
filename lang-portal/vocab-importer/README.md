# Language Learning Vocabulary Generator

A Streamlit web application for generating vocabulary words and groups for the Language Learning Portal.

## Features

- Generate vocabulary words using a language model (Ollama)
- Generate vocabulary groups using a language model
- Export generated data to JSON files
- Import data from existing JSON files
- View and manage generated data in a user-friendly interface

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running
- A language model installed in Ollama (default: llama3.2:1b)

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure Ollama is installed and running:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags
```

If Ollama is not running, start it:

```bash
# Start Ollama in the background
ollama serve &
```

3. Ensure you have the required model installed:

```bash
# Pull the llama model (or another model of your choice)
ollama pull llama3.2:1b
```

## Running the Application

Start the Streamlit application:

```bash
cd lang-portal/vocab-importer
streamlit run app.py
```

The application will be available at http://localhost:8501

## Environment Variables

You can configure the application using environment variables:

- `LLM_SERVICE_HOST`: Hostname of the Ollama service (default: localhost)
- `LLM_SERVICE_PORT`: Port of the Ollama service (default: 11434)
- `LLM_MODEL_ID`: Model to use for generation (default: llama3.2:1b)

## Using the Application

### Generating Vocabulary

1. Navigate to the "Generate Vocabulary" page
2. Select the target language
3. Enter a category name
4. Choose the number of words and difficulty level
5. Click "Generate Vocabulary"

### Generating Groups

1. Navigate to the "Generate Groups" page
2. Select the target language
3. Choose the number of groups
4. Click "Generate Groups"

### Exporting Data

1. Navigate to the "Export Data" page
2. Choose whether to export vocabulary, groups, or both
3. Specify a filename
4. Click "Export" button
5. Download the exported JSON file

### Importing Data

1. Navigate to the "Import Data" page
2. Upload a JSON file containing vocabulary items, groups, or both
3. The application will automatically detect the format and import the data

## JSON Format

### Vocabulary Items

```json
[
  {
    "japanese": "こんにちは",
    "romaji": "konnichiwa",
    "english": "hello"
  }
]
```

### Vocabulary Groups

```json
[
  {
    "name": "Basic Greetings"
  }
]
```

### Combined Format

```json
{
  "vocabulary": [
    {
      "japanese": "こんにちは",
      "romaji": "konnichiwa",
      "english": "hello"
    }
  ],
  "groups": [
    {
      "name": "Basic Greetings"
    }
  ]
}
```

## Data Storage

Generated and imported data is stored in memory during the session. To persist data between sessions, export it to JSON files.

Generated files are saved in the `output` directory.

## Troubleshooting

- If the application fails to connect to Ollama, check that it's running and accessible at the configured host and port.
- If the LLM fails to generate vocabulary, check that you have the specified model installed in Ollama.
- For any other issues, check the application logs for details. 