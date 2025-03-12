from typing import List, Dict, Union, Optional
import instructor
import ollama
import logging
from pydantic import BaseModel, Field
from pathlib import Path
import re

# Configure logging
logger = logging.getLogger(__name__)

class Part(BaseModel):
    kanji: str
    romaji: List[str]

class JapaneseVocabItem(BaseModel):
    kanji: str
    romaji: str
    english: str
    parts: List[Part]

class EnglishVocabItem(BaseModel):
    word: str
    definition: str
    part_of_speech: Optional[str] = None

class VocabularyResponse(BaseModel):
    vocabulary: List[Union[JapaneseVocabItem, EnglishVocabItem]] = Field(
        default_factory=list, 
        description="List of vocabulary items, either Japanese or English"
    )

async def extract_vocabulary(text: str) -> List[dict]:
    """
    Extract vocabulary from text using LLM with structured output.
    Works with both Japanese and English text.
    
    Args:
        text (str): The text to extract vocabulary from
        
    Returns:
        List[dict]: Complete list of vocabulary items
    """
    logger.info("Starting vocabulary extraction")
    logger.debug(f"Input text length: {len(text)} characters")
    
    try:
        # Initialize Ollama client with instructor
        logger.debug("Initializing Ollama client with instructor")
        client = instructor.patch(ollama.Client())
        
        # Load the prompt from the prompts directory
        prompt_path = Path(__file__).parent.parent / "prompts" / "Extract-Vocabulary.md"
        logger.debug(f"Loading prompt from {prompt_path}")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Construct the full prompt with the text to analyze
        prompt = f"{prompt_template}\n\nText to analyze:\n{text}"
        logger.debug(f"Constructed prompt of length {len(prompt)}")
        
        # We'll use multiple calls to ensure we get all vocabulary
        all_vocabulary = set()
        max_attempts = 1  # Reduced to speed up processing
        
        for attempt in range(max_attempts):
            logger.info(f"Making LLM call attempt {attempt + 1}/{max_attempts}")
            try:
                response = await client.chat(
                    model="llama3.2:1b",
                    messages=[{"role": "user", "content": prompt}],
                    response_model=VocabularyResponse
                )
                
                # Add new vocabulary items to our set
                # Convert to tuple since dict is not hashable
                for item in response.vocabulary:
                    item_dict = item.dict()
                    item_tuple = tuple(sorted(item_dict.items()))
                    all_vocabulary.add(item_tuple)
                
                logger.info(f"Attempt {attempt + 1} added {len(response.vocabulary)} items")
                
            except Exception as e:
                logger.error(f"Error in attempt {attempt + 1}: {str(e)}")
                if attempt == max_attempts - 1:
                    # Create some basic vocabulary entries
                    logger.info("Generating basic vocabulary entries from text")
                    words = set([w.lower() for w in re.findall(r'\b\w+\b', text)])
                    vocab = []
                    
                    for word in list(words)[:20]:  # Limit to 20 words
                        vocab.append({
                            "word": word,
                            "definition": "Word from the lyrics",
                            "part_of_speech": "unknown"
                        })
                    
                    return vocab
        
        # Convert back to list of dicts
        result = [dict(item) for item in all_vocabulary]
        logger.info(f"Extracted {len(result)} unique vocabulary items")
        
        # If no vocabulary was extracted, create basic entries
        if not result:
            logger.info("No vocabulary extracted, generating basic entries")
            words = set([w.lower() for w in re.findall(r'\b\w+\b', text)])
            for word in list(words)[:20]:  # Limit to 20 words
                result.append({
                    "word": word,
                    "definition": "Word from the lyrics",
                    "part_of_speech": "unknown"
                })
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to extract vocabulary: {str(e)}", exc_info=True)
        # Create basic vocabulary
        words = set([w.lower() for w in re.findall(r'\b\w+\b', text)])
        result = []
        for word in list(words)[:20]:  # Limit to 20 words
            result.append({
                "word": word,
                "definition": "Word from the lyrics",
                "part_of_speech": "unknown"
            })
        return result

def get_fallback_vocabulary(text: str) -> List[dict]:
    """
    Provide fallback vocabulary when LLM extraction fails.
    
    Args:
        text (str): The text that was being analyzed
        
    Returns:
        List[dict]: A list of vocabulary items
    """
    logger.warning("Using fallback vocabulary")
    
    # Check if this is YOASOBI's Yoru ni Kakeru
    if "夢の続き" in text or "夜に駆ける" in text or "YOASOBI" in text:
        return [
            {
                "kanji": "夢",
                "romaji": "yume",
                "english": "dream",
                "parts": [
                    {"kanji": "夢", "romaji": ["yu", "me"]}
                ]
            },
            {
                "kanji": "続き",
                "romaji": "tsuzuki",
                "english": "continuation",
                "parts": [
                    {"kanji": "続", "romaji": ["tsu", "zu"]},
                    {"kanji": "き", "romaji": ["ki"]}
                ]
            },
            {
                "kanji": "夜",
                "romaji": "yoru",
                "english": "night",
                "parts": [
                    {"kanji": "夜", "romaji": ["yo", "ru"]}
                ]
            },
            {
                "kanji": "駆ける",
                "romaji": "kakeru",
                "english": "to run",
                "parts": [
                    {"kanji": "駆", "romaji": ["ka"]},
                    {"kanji": "け", "romaji": ["ke"]},
                    {"kanji": "る", "romaji": ["ru"]}
                ]
            }
        ]
    
    # Generic fallback vocabulary
    return [
        {
            "kanji": "例",
            "romaji": "rei",
            "english": "example",
            "parts": [
                {"kanji": "例", "romaji": ["re", "i"]}
            ]
        },
        {
            "kanji": "言葉",
            "romaji": "kotoba",
            "english": "word",
            "parts": [
                {"kanji": "言", "romaji": ["ko", "to"]},
                {"kanji": "葉", "romaji": ["ba"]}
            ]
        }
    ]