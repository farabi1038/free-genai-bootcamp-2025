import os
import logging
import requests
import json
from typing import Dict, Any, List, Optional
import subprocess
import tempfile
from PIL import Image
import re

# Import configuration
from config import (LLM_PROVIDER, 
                   OPENAI_API_ENDPOINT, OPENAI_API_KEY, OPENAI_MODEL,
                   OLLAMA_API_ENDPOINT, OLLAMA_MODEL, 
                   DEBUG)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if MangaOCR is installed
try:
    import manga_ocr
    MANGA_OCR_AVAILABLE = True
    logger.info("MangaOCR is available.")
except ImportError:
    MANGA_OCR_AVAILABLE = False
    logger.warning("MangaOCR is not installed. Will use fallback for OCR.")

class JapaneseOCR:
    """Class to handle OCR for Japanese text"""
    
    def __init__(self):
        """Initialize OCR engine if available"""
        self.mocr = None
        if MANGA_OCR_AVAILABLE:
            try:
                logger.info("Initializing MangaOCR...")
                self.mocr = manga_ocr.MangaOcr()
                logger.info("MangaOCR loaded successfully")
            except Exception as e:
                logger.error(f"Error loading MangaOCR: {str(e)}")
                self.mocr = None
    
    def recognize_text(self, image_path: str) -> str:
        """
        Recognize Japanese text from an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Recognized text or fallback message if OCR fails
        """
        if self.mocr:
            try:
                # Use MangaOCR
                logger.info(f"Running MangaOCR on image: {image_path}")
                text = self.mocr(image_path)
                logger.info(f"OCR result: {text}")
                return text
            except Exception as e:
                logger.error(f"Error during OCR: {str(e)}")
        
        # Fallback: just acknowledge we received an image but couldn't process it
        logger.warning("Using fallback OCR method")
        return "OCRエラー (OCR error)"

def get_llm_response(prompt: str, max_tokens: int = 256) -> Optional[str]:
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

def get_openai_response(prompt: str, max_tokens: int = 256) -> Optional[str]:
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
        "messages": [{"role": "system", "content": "You are a helpful assistant that helps grade Japanese translations."},
                    {"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(OPENAI_API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        return None

def get_ollama_response(prompt: str, max_tokens: int = 256) -> Optional[str]:
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
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.3
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
                return response_json["response"].strip()
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

def translate_japanese_to_english(japanese_text: str) -> str:
    """
    Translate Japanese text to English using Ollama
    
    Args:
        japanese_text: The Japanese text to translate
        
    Returns:
        English translation or error message
    """
    prompt = f"""
    Translate the following Japanese text to English:
    
    ```
    {japanese_text}
    ```
    
    Provide ONLY the direct English translation, with no additional comments or explanations.
    """
    
    translation = get_ollama_response(prompt)
    
    if not translation:
        return "Translation service unavailable"
    
    return translation

def evaluate_translation(original_sentence: str, transcribed_text: str, translation: str) -> Dict[str, Any]:
    """
    Evaluate the quality of a translation using Ollama
    
    Args:
        original_sentence: The original English sentence
        transcribed_text: The transcribed Japanese text
        translation: The English translation of the transcribed text
        
    Returns:
        A dictionary containing the grade and feedback
    """
    prompt = f"""
    Evaluate this Japanese language learner's translation.
    
    Original English sentence: "{original_sentence}"
    
    Transcribed Japanese text: "{transcribed_text}"
    
    Translation back to English: "{translation}"
    
    Grade the translation using the following scale:
    - S: Perfect - Flawless translation with correct grammar and word choice
    - A: Excellent - Minor errors but conveys meaning perfectly
    - B: Good - Some errors but meaning is still clear
    - C: Fair - Several errors, meaning somewhat changed
    - D: Poor - Major errors, meaning significantly changed
    - F: Failed - Incomprehensible or completely incorrect
    
    Respond ONLY with a JSON object in this exact format:
    {{\"grade\": \"LETTER_GRADE\", \"feedback\": \"Detailed feedback\"}}
    
    Where LETTER_GRADE is one of: S, A, B, C, D, or F.
    """
    
    response = get_ollama_response(prompt)
    
    # Default values in case of failure
    grade_info = {
        "grade": "C",
        "feedback": "The grading system is currently unavailable. Please try again later."
    }
    
    if response:
        try:
            # First, try to find the JSON object in the response using a simpler regex pattern
            import re
            # Simple pattern to match a JSON object - looking for text between { and }
            json_match = re.search(r'\{[^{}]*\}', response)
            
            if json_match:
                # Clean up the JSON string - replace escaped quotes, etc.
                json_str = json_match.group(0)
                json_str = json_str.replace('\\"', '"').replace('\\n', ' ')
                
                logger.info(f"Found JSON object: {json_str}")
                
                # Try to parse the JSON
                try:
                    parsed_response = json.loads(json_str)
                    if "grade" in parsed_response and "feedback" in parsed_response:
                        grade_info = parsed_response
                        logger.info(f"Successfully parsed JSON: {grade_info}")
                except json.JSONDecodeError as json_err:
                    logger.error(f"JSON parse error: {json_err} - {json_str}")
                    
                    # Try extracting grade and feedback directly with regex
                    grade_match = re.search(r'"grade"\s*:\s*"([A-F]|S)"', json_str)
                    feedback_match = re.search(r'"feedback"\s*:\s*"([^"]*)"', json_str)
                    
                    if grade_match and feedback_match:
                        grade = grade_match.group(1)
                        feedback = feedback_match.group(1)
                        grade_info = {
                            "grade": grade,
                            "feedback": feedback
                        }
                        logger.info(f"Extracted from regex: {grade_info}")
            else:
                # Look for letter grades in the response
                logger.info("No JSON object found, looking for letter grades in response")
                for grade in ["S", "A", "B", "C", "D", "F"]:
                    if grade in response:
                        grade_info = {
                            "grade": grade,
                            "feedback": f"Your translation received a grade of {grade}."
                        }
                        logger.info(f"Found grade {grade} in response")
                        break
        except Exception as e:
            logger.error(f"Error processing grading response: {str(e)}")
            logger.error(f"Response: {response[:200]}...")  # Log first 200 chars of response
    else:
        logger.warning("No response received from Ollama for grading")
    
    logger.info(f"Final grade info: {grade_info}")
    return grade_info

def grade_submission(image_path: str, original_sentence: str, target_word: Dict[str, str]) -> Dict[str, Any]:
    """
    Process a submission and return feedback
    
    Args:
        image_path: Path to the image file
        original_sentence: The original English sentence
        target_word: The target vocabulary word (dict with 'japanese' and 'english' keys)
        
    Returns:
        A dictionary with transcription, translation, grade, and feedback
    """
    logger.info(f"Starting grading for submission with target word: {target_word['english']}")
    
    # Step 1: Transcribe the handwritten text using MangaOCR
    ocr = JapaneseOCR()
    transcription = ocr.recognize_text(image_path)
    logger.info(f"OCR Transcription: {transcription}")
    
    # Step 2: Translate the transcription back to English using Ollama
    logger.info("Translating transcription back to English...")
    translation = translate_japanese_to_english(transcription)
    logger.info(f"Translation: {translation}")
    
    # Step 3: Evaluate the translation using Ollama
    logger.info("Evaluating translation quality...")
    evaluation = evaluate_translation(original_sentence, transcription, translation)
    logger.info(f"Evaluation result: {evaluation}")
    
    # Return the complete feedback
    return {
        "transcription": transcription,
        "translation": translation,
        "grade": evaluation["grade"],
        "feedback": evaluation["feedback"],
        "target_word": target_word
    } 