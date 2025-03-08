import os
import logging
import requests
import random
import json
from typing import Dict, Any, List, Optional, Tuple, Union

# Import configuration
from config import (LLM_PROVIDER, 
                   OPENAI_API_ENDPOINT, OPENAI_API_KEY, OPENAI_MODEL,
                   OLLAMA_API_ENDPOINT, OLLAMA_MODEL, 
                   DEBUG)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Examples for each complexity level
BEGINNER_EXAMPLES = [
    "I eat an apple every day.",
    "The cat sleeps on the bed.",
    "She drinks water in the morning.",
    "He reads a book at night.",
    "We study Japanese on Monday."
]

def get_llm_response(prompt: str, max_tokens: int = 100) -> Optional[str]:
    """
    Get a response from the configured LLM provider
    
    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        The generated text or None if request failed
    """
    if LLM_PROVIDER == "openai":
        return get_openai_response(prompt, max_tokens)
    elif LLM_PROVIDER == "ollama":
        return get_ollama_response(prompt, max_tokens)
    else:
        logger.error(f"Unknown LLM provider: {LLM_PROVIDER}")
        return None

def get_openai_response(prompt: str, max_tokens: int = 100) -> Optional[str]:
    """
    Get a response from the OpenAI API
    
    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        The generated text or None if request failed
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "system", "content": "You are a helpful assistant that generates simple English sentences for Japanese language learners."},
                    {"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(OPENAI_API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        return None

def get_ollama_response(prompt: str, max_tokens: int = 100) -> Optional[str]:
    """
    Get a response from Ollama running locally
    
    Args:
        prompt: The prompt to send to Ollama
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        The generated text or None if request failed
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    # Fix for Ollama API endpoint format - use base API instead of chat
    api_base = OLLAMA_API_ENDPOINT.split('/api/')[0].rstrip('/')
    api_endpoint = f"{api_base}/api/generate"
    
    # Use the generate endpoint with stream=false to get a complete response
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"You are a helpful assistant that generates simple English sentences for Japanese language learners.\n\n{prompt}\n\nProvide only a single simple sentence, no explanations.",
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.7
        }
    }
    
    try:
        logger.info(f"Sending request to Ollama at {api_endpoint}")
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # Parse the non-streaming response
        try:
            response_json = response.json()
            
            if DEBUG:
                logger.info(f"Ollama response: {json.dumps(response_json, indent=2)}")
            
            if "response" in response_json:
                # Extract just the simple sentence
                full_response = response_json["response"].strip()
                
                # Try to extract just a single sentence if multiple are returned
                sentences = [s.strip() for s in full_response.split('.') if s.strip()]
                if sentences:
                    # Return the first complete sentence with a period
                    return sentences[0] + "."
                
                return full_response
            else:
                logger.error(f"Unexpected Ollama response format: {response_json}")
                return None
                
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parsing error: {json_err}")
            logger.error(f"Response content: {response.text[:500]}")  # Log first 500 chars
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Ollama API: {str(e)}")
        if DEBUG:
            logger.error(f"Request: {payload}")
            logger.error(f"Response: {response.text[:500] if 'response' in locals() else 'No response'}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error with Ollama: {str(e)}")
        return None

def get_japanese_translation(english_sentence: str) -> str:
    """
    Get a Japanese translation of an English sentence using Ollama
    
    Args:
        english_sentence: The English sentence to translate
        
    Returns:
        The Japanese translation or error message
    """
    prompt = f"""
    Translate the following English sentence to Japanese:
    
    ```
    {english_sentence}
    ```
    
    Important requirements:
    1. Use actual Japanese characters (hiragana, katakana, and basic kanji)
    2. DO NOT use romaji or Latin characters
    3. DO NOT include pronunciation guides or explanations
    4. DO NOT include parentheses or bracketed text
    5. Provide ONLY the direct Japanese translation
    
    Example:
    English: "I drink water every day."
    Japanese: "私は毎日水を飲みます。"
    
    Your translation should look like:
    "水は体にとても良いです。" (for "Water is very good for your body.")
    """
    
    translation = get_ollama_response(prompt)
    
    if not translation:
        logger.warning("Failed to get Japanese translation, using fallback")
        return "翻訳できませんでした。" # "Could not translate."
    
    # Clean up the translation to remove any English or parentheses
    import re
    # Remove any text in parentheses
    translation = re.sub(r'\([^)]*\)', '', translation)
    # Remove any English words or phrases
    translation = re.sub(r'[a-zA-Z]+', '', translation)
    # Remove quotes if present
    translation = translation.replace('"', '').replace('"', '').strip()
    
    # If after cleaning there's no Japanese text, use fallback
    if not translation or all(ord(c) < 128 for c in translation):
        logger.warning("No Japanese characters in translation, using fallback")
        return "翻訳できませんでした。" # "Could not translate."
    
    logger.info(f"Japanese translation: {translation}")
    return translation

def create_sentence_prompt(word: str) -> str:
    """
    Create a prompt for sentence generation
    
    Args:
        word: The vocabulary word to include in the sentence
        
    Returns:
        A formatted prompt for the LLM
    """
    return f"""
    Generate a clear, beginner-friendly English sentence using the word: '{word}'.
    
    Requirements:
    - Ensure grammar simplicity suitable for Japanese learners at the JLPT N5 proficiency level.
    - Use only common, descriptive, beginner-level vocabulary.
    - The sentence should be natural and practical for everyday use.
    - Return only the sentence, with no additional explanation.
    
    Examples of appropriate sentences:
    - "I eat an apple every day."
    - "The cat sleeps on the bed."
    - "She drinks water in the morning."
    """

def generate_sentence(word: str, include_japanese: bool = False) -> Union[str, Tuple[str, str]]:
    """
    Generate a sentence containing the given word
    
    Args:
        word: The vocabulary word to include in the sentence
        include_japanese: Whether to also return a Japanese translation
        
    Returns:
        English sentence or (English sentence, Japanese translation) if include_japanese is True
    """
    prompt = create_sentence_prompt(word)
    logger.info(f"Generating sentence for word: {word}")
    
    # Try to get a response from the LLM
    english_sentence = get_ollama_response(prompt)
    
    # If the LLM request failed, use a template sentence
    if not english_sentence:
        logger.warning("LLM request failed, using fallback sentence")
        templates = [
            f"I have a {word}.",
            f"She likes the {word}.",
            f"He uses the {word} every day.",
            f"We can see the {word}.",
            f"The {word} is very nice."
        ]
        english_sentence = random.choice(templates)
    
    logger.info(f"Generated sentence: {english_sentence}")
    
    # If Japanese translation is also needed
    if include_japanese:
        # Try to get translation from LLM
        japanese_sentence = get_japanese_translation(english_sentence)
        
        # If we got an English template sentence and translation failed, use a hardcoded fallback
        if japanese_sentence == "翻訳できませんでした。":
            # Check which template we used and provide appropriate Japanese
            if english_sentence == f"I have a {word}.":
                japanese_sentence = f"私は{word}を持っています。"
            elif english_sentence == f"She likes the {word}.":
                japanese_sentence = f"彼女は{word}が好きです。"
            elif english_sentence == f"He uses the {word} every day.":
                japanese_sentence = f"彼は毎日{word}を使います。"
            elif english_sentence == f"We can see the {word}.":
                japanese_sentence = f"私たちは{word}を見ることができます。"
            elif english_sentence == f"The {word} is very nice.":
                japanese_sentence = f"{word}はとても素敵です。"
        
        return english_sentence, japanese_sentence
    
    return english_sentence 