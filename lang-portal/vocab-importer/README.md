# Language Learning Vocabulary Generator

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Ollama](https://img.shields.io/badge/Ollama-compatible-green)

A Streamlit web application for generating vocabulary words and groups for the Language Learning Portal. This internal tool streamlines the process of populating language learning databases with high-quality vocabulary.


## Business Goal: 
The prototype of the language learning app is built, but we need to quickly populate the application with word and word groups so students can begin testing the system.

There is currently no interface for manually adding words or words groups and the process would be too tedious. 

You have been asked to:
- create an internal facing tool to generate vocab 

- Be able to export the generated vocab to json for later import

- Be able  to import to import json files

## Technical Restrictions
Since this is an internal facing tool the fractional CTO wants you to use an app prototyping framework of your choice:

-Gradio

-Streamlit (Used)

-FastHTML

You need to use an LLM in order to generate the target words and word groups.
You can use either an:

- Managed/Serverless LLM API

- Local LLM serving the model via OPEA (used)


## Features

- Generate vocabulary words using a language model (Ollama)
- Specialized handling for Japanese language with proper kanji and romaji support
- Generate vocabulary groups organized by category and difficulty level
- Export generated data to JSON files for import into the main application
- Import data from existing JSON files
- View and manage generated data in a user-friendly interface
- Fallback mechanism to ensure functionality even without LLM connectivity

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running
- A language model installed in Ollama (more details in [Model Selection](#model-selection))

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
# Pull a recommended model (options below)
ollama pull llama2:13b
```

## Running the Application

Start the Streamlit application:

```bash
cd lang-portal/vocab-importer
streamlit run app.py
```

The application will be available at http://localhost:8501

If you're running in WSL and need to access from Windows, use:

```bash
streamlit run app.py --server.address=0.0.0.0
```

Then access via http://WSL_IP_ADDRESS:8501 (where WSL_IP_ADDRESS is found using `hostname -I`)

## Environment Variables

You can configure the application using the `.env` file or environment variables:

- `LLM_SERVICE_HOST`: Hostname of the Ollama service (default: localhost)
- `LLM_SERVICE_PORT`: Port of the Ollama service (default: 11434)
- `LLM_MODEL_ID`: Model to use for generation (default: llama3.2:1b)

### WSL-Specific Configuration

If running in WSL with Ollama on Windows:

1. Identify the Windows host IP:
   ```bash
   ip route | grep default | awk '{print $3}'
   ```

2. Update `.env` with this IP:
   ```
   LLM_SERVICE_HOST=172.17.0.1  # Replace with your Windows host IP
   LLM_SERVICE_PORT=11434
   LLM_MODEL_ID=llama2:13b
   ```

## Model Selection

### Recommended Models for Japanese

For optimal Japanese vocabulary generation, the following models are recommended:

| Model | Size | Japanese Quality | Hardware Requirements |
|-------|------|-----------------|----------------------|
| llama3:70b | 70B | Excellent | High (24GB+ VRAM) |
| mixtral:8x7b | 47B | Very Good | High (16GB+ VRAM) |
| llama2:13b | 13B | Good | Moderate (8GB+ VRAM) |
| gemma:7b | 7B | Good | Moderate (6GB+ VRAM) |
| phi:2b | 2B | Basic | Low (2GB+ VRAM) |

To change the model, edit the `.env` file and update `LLM_MODEL_ID`, then restart the application.

## Using the Application

### Generating Vocabulary

1. Navigate to the "Generate Vocabulary" page
2. Select the target language (e.g., Japanese)
3. Enter a category name (e.g., "Food", "Basic Greetings")
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

## Technical Architecture

The application follows a modular architecture:

```
vocab-importer/
├── app.py                   # Main Streamlit application
├── requirements.txt         # Dependencies
├── .env                     # Configuration file
├── README.md                # Documentation
├── output/                  # Directory for exported files
└── utils/
    ├── llm_client.py        # LLM communication layer
    └── vocab_generator.py   # Vocabulary generation logic
```

## Data Storage

Generated and imported data is stored in memory during the session. To persist data between sessions, export it to JSON files.

Generated files are saved in the `output` directory.

## Troubleshooting

### Common Issues

#### Ollama Connection Issues

**Problem**: "Failed to connect to Ollama" error

**Solution**: 
- Verify Ollama is running (`curl http://localhost:11434/api/tags`)
- If using WSL, verify the correct host IP in `.env`
- Try different ports or hosts as suggested in the UI

#### Japanese Generation Issues

**Problem**: Poor quality Japanese vocabulary or incorrect romaji

**Solution**:
- Try a more capable model (llama2:13b or larger)
- Check if the model has good multilingual capabilities
- Verify the model is properly loaded in Ollama

#### WSL-Specific Issues

**Problem**: "Cannot access localhost" from browser

**Solution**:
- Run Streamlit with explicit binding: `streamlit run app.py --server.address=0.0.0.0`
- Access using the WSL IP address instead of localhost

#### Fallback Mode

If the LLM service is unavailable or no models are found, the application will automatically switch to fallback mode, providing pre-defined vocabulary. This ensures the application remains functional for testing purposes. 
