import os
import json
import logging
import requests
import random
import time
import gc
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default Ollama configuration
DEFAULT_MODEL = "llama3.2:1b"  # Use the smaller model by default
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 11434
DEFAULT_TIMEOUT = 60  # seconds
DEFAULT_MAX_TOKENS = 1024  # Limit token count to save memory

class OllamaClient:
    """Client for interacting with the Ollama API"""
    
    def __init__(self, model=DEFAULT_MODEL, host=DEFAULT_HOST, port=DEFAULT_PORT, timeout=DEFAULT_TIMEOUT):
        """Initialize the Ollama client"""
        self.model = model
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        
        # Run GC to clean up any lingering memory
        gc.collect()
        
    def check_availability(self):
        """Check if Ollama is available and the model is loaded"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                logger.error(f"Ollama API returned status code: {response.status_code}")
                return False
            
            available_models = response.json().get("models", [])
            model_names = [model.get("name") for model in available_models]
            
            # Check if the exact model name is available
            if self.model in model_names:
                return True
                
            # If not, split the model name by ":" to handle tagged models
            model_base = self.model.split(":")[0]
            for available_model in model_names:
                if available_model.startswith(f"{model_base}:"):
                    logger.info(f"Found model {available_model} matching requested {self.model}")
                    # Update the model name to use the found tag
                    self.model = available_model
                    return True
            
            logger.warning(f"Model '{self.model}' is not available. Available models: {model_names}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking Ollama availability: {str(e)}")
            return False
    
    async def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=DEFAULT_MAX_TOKENS, stream=False):
        """
        Generate a response from Ollama
        
        Args:
            prompt: The prompt to send to Ollama
            system_prompt: Optional system prompt to set context
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            
        Returns:
            str: Generated text
        """
        # Run GC before making the API call to free up memory
        gc.collect()
        
        # Ensure max_tokens doesn't exceed our limit
        if max_tokens > DEFAULT_MAX_TOKENS:
            logger.warning(f"Reducing max_tokens from {max_tokens} to {DEFAULT_MAX_TOKENS} to save memory")
            max_tokens = DEFAULT_MAX_TOKENS
            
        try:
            # Check if Ollama is available
            if not self.check_availability():
                raise ConnectionError("Ollama is not available or the model is not loaded")
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            # Stream or not
            api_endpoint = "/api/generate/stream" if stream else "/api/generate"
            
            # Make the API call
            response = requests.post(
                f"{self.base_url}{api_endpoint}",
                json=payload,
                stream=stream,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API returned status code: {response.status_code}")
                logger.error(f"Error response: {response.text}")
                raise Exception(f"Ollama API error: {response.text}")
            
            if stream:
                # Handle streaming response
                full_response = ""
                try:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    full_response += data.get("response", "")
                                elif "error" in data:
                                    logger.error(f"Ollama streaming error: {data['error']}")
                                    return f"Error in Ollama response: {data['error']}"
                            except json.JSONDecodeError as e:
                                logger.warning(f"Error parsing JSON from streaming response: {str(e)}")
                                logger.warning(f"Problematic line: {line}")
                                continue
                    return full_response
                except Exception as e:
                    logger.error(f"Error processing streaming response: {str(e)}")
                    # Don't return the raw streaming data as it will be confusing to users
                    return "Error processing Ollama streaming response. Please try again."
            else:
                # Handle regular response with better error handling
                try:
                    result = response.json()
                    return result["response"]
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON response: {str(e)}")
                    logger.error(f"Raw response: {response.text[:500]}")  # Log first 500 chars of response
                    # Try to extract text using a simple text approach as fallback
                    text = response.text
                    if '"response": "' in text:
                        start = text.find('"response": "') + 12
                        end = text.find('",', start)
                        if end > start:
                            return text[start:end]
                    # If all else fails, return an error message instead of raw response
                    return "Error parsing Ollama response. Please try again."
                except KeyError:
                    logger.error(f"Missing 'response' key in Ollama response: {response.json()}")
                    return "Error: Invalid response format from Ollama"
            
        except Exception as e:
            logger.error(f"Error generating response from Ollama: {str(e)}")
            raise
        finally:
            # Clean up after API call
            gc.collect()

async def generate_exercises(
    transcript_segments, 
    num_exercises=5, 
    difficulty="intermediate", 
    ollama_model=DEFAULT_MODEL
):
    """
    Generate exercises based on transcript segments, with special handling for
    introduction and conversation parts.
    
    Args:
        transcript_segments: List of transcript segments
        num_exercises: Number of exercises to generate
        difficulty: Difficulty level of exercises (beginner, intermediate, advanced)
        ollama_model: Ollama model to use
        
    Returns:
        list: List of generated exercises
    """
    try:
        # Initialize Ollama client
        client = OllamaClient(model=ollama_model)
        
        # Analyze the transcript to identify introduction and conversation parts
        # Typically, introductions are at the beginning and shorter than the main content
        total_duration = sum(segment.get("duration", 0) for segment in transcript_segments)
        
        # Basic heuristic: first 15-20% is likely introduction
        intro_threshold = total_duration * 0.2
        current_time = 0
        intro_segments = []
        conversation_segments = []
        
        for segment in transcript_segments:
            start_time = segment.get("start", 0)
            duration = segment.get("duration", 0)
            
            if current_time < intro_threshold:
                intro_segments.append(segment)
            else:
                conversation_segments.append(segment)
                
            current_time += duration
        
        # Prepare the intro and conversation texts
        intro_text = ""
        for segment in intro_segments:
            start_time = segment.get("start", 0)
            end_time = start_time + segment.get("duration", 0)
            text = segment.get("text", "")
            intro_text += f"[{start_time:.2f}-{end_time:.2f}] {text}\n"
            
        conversation_text = ""
        for segment in conversation_segments:
            start_time = segment.get("start", 0)
            end_time = start_time + segment.get("duration", 0)
            text = segment.get("text", "")
            conversation_text += f"[{start_time:.2f}-{end_time:.2f}] {text}\n"
        
        # Combine all segments for full context
        complete_transcript = intro_text + "\n" + conversation_text
        
        # System prompt to set context with awareness of structure
        system_prompt = """
        You are a Japanese language teacher creating listening comprehension exercises for students. 
        You will receive a transcript of a Japanese video with timestamps, divided into introduction and conversation parts.
        Your task is to create exercises that test the student's understanding of the content.
        
        Important guidelines:
        1. Create more challenging questions about the conversation section
        2. For the introduction section, focus on identifying the topic and purpose
        3. Always include timestamps with each question so students know which part to focus on
        4. Include both Japanese text and English translations in questions and answers
        """
        
        # Create different exercise types based on difficulty
        exercise_types = get_exercise_types_by_difficulty(difficulty)
        
        # Prepare the prompt
        prompt = f"""
        Please create {num_exercises} Japanese listening comprehension exercises based on this transcript.
        The transcript has introduction and conversation parts:

        INTRODUCTION:
        {intro_text}
        
        MAIN CONVERSATION:
        {conversation_text}
        
        Create {num_exercises} exercises with this distribution:
        - 1 question about the introduction (what is the video about)
        - {num_exercises-1} questions about the conversation content
        
        Use these exercise types: {', '.join(exercise_types)}
        
        For each exercise, include:
        1. The segment timestamps it refers to
        2. A question in both Japanese and English
        3. For multiple choice: 4 options with the correct one marked
        4. For fill-in: The word or phrase to fill in (max 3 words)
        
        Format your response as JSON:
        ```json
        [
          {
            "id": "unique_id",
            "segment_start": start_time,
            "segment_end": end_time,
            "question": "Question text in Japanese (English translation)",
            "type": "multiple_choice|fill_in|free_form",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answer": "The correct answer",
            "difficulty": "intermediate"
          }
        ]
        ```
        
        Only respond with valid JSON. No additional text or explanations.
        """
        
        # Generate exercises
        logger.info(f"Generating {num_exercises} exercises with model {ollama_model}")
        response = await client.generate(prompt, system_prompt, temperature=0.7)
        logger.info(f"Got response of length {len(response)}")
        
        # Try to extract JSON
        try:
            exercises = json.loads(response)
            logger.info(f"Successfully parsed {len(exercises)} exercises")
            
            # Add a unique ID to each exercise if not present
            for i, exercise in enumerate(exercises):
                if "id" not in exercise:
                    exercise["id"] = f"ex_{int(time.time())}_{i}"
            
            return exercises
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, attempting manual extraction")
            # Try to manually extract exercises
            exercises = manual_exercise_extraction(response, difficulty)
            return exercises
            
    except Exception as e:
        logger.error(f"Error generating exercises: {str(e)}")
        # Return some default exercises
        return generate_default_exercises(difficulty, num_exercises)

def get_exercise_types_by_difficulty(difficulty):
    """Get appropriate exercise types based on difficulty level"""
    if difficulty == "beginner":
        return ["multiple_choice", "fill_in"]
    elif difficulty == "intermediate":
        return ["multiple_choice", "fill_in", "free_form"]
    else:  # advanced
        return ["fill_in", "free_form"]

def manual_exercise_extraction(response, difficulty):
    """
    Manually extract exercises from an Ollama response that doesn't contain valid JSON
    
    Args:
        response: Raw text response from Ollama
        difficulty: Difficulty level
        
    Returns:
        list: Extracted exercises
    """
    # This is a fallback method for when JSON parsing fails
    # In a real implementation, this would be more sophisticated
    exercises = []
    
    # For now, just return default exercises
    return generate_default_exercises(difficulty)

def generate_default_exercises(difficulty, num_exercises=3):
    """
    Generate default exercises in case of error
    
    Args:
        difficulty: Difficulty level
        num_exercises: Number of exercises to generate
        
    Returns:
        list: Default exercises
    """
    timestamp = int(time.time())
    exercises = []
    
    if difficulty == "beginner":
        exercises = [
            {
                "id": f"ex1_{timestamp}",
                "type": "multiple_choice",
                "segment_start": 10.0,
                "segment_end": 20.0,
                "question": "What is the speaker talking about?",
                "options": ["Food", "Weather", "Hobbies", "Work"],
                "correct_answer": "Weather",
                "difficulty": "beginner"
            },
            {
                "id": f"ex2_{timestamp}",
                "type": "fill_in",
                "segment_start": 30.0,
                "segment_end": 40.0,
                "question": "Complete the sentence: '私は日本語を＿＿＿います。'",
                "correct_answer": "勉強して",
                "difficulty": "beginner"
            }
        ]
    elif difficulty == "intermediate":
        exercises = [
            {
                "id": f"ex1_{timestamp}",
                "type": "multiple_choice",
                "segment_start": 15.0,
                "segment_end": 30.0,
                "question": "What is the main topic of the conversation?",
                "options": ["Travel plans", "Work meeting", "Family dinner", "School project"],
                "correct_answer": "Travel plans",
                "difficulty": "intermediate"
            },
            {
                "id": f"ex2_{timestamp}",
                "type": "fill_in",
                "segment_start": 45.0,
                "segment_end": 60.0,
                "question": "According to the speaker, when will they arrive in Tokyo?",
                "correct_answer": "来週の金曜日",
                "difficulty": "intermediate"
            },
            {
                "id": f"ex3_{timestamp}",
                "type": "free_form",
                "segment_start": 75.0,
                "segment_end": 90.0,
                "question": "Summarize the speaker's plans for their trip to Japan.",
                "correct_answer": "The speaker plans to visit Tokyo next Friday, stay for a week, and visit several landmarks including Tokyo Tower and Asakusa.",
                "difficulty": "intermediate"
            }
        ]
    else:  # advanced
        exercises = [
            {
                "id": f"ex1_{timestamp}",
                "type": "fill_in",
                "segment_start": 20.0,
                "segment_end": 40.0,
                "question": "What economic factor did the speaker identify as the main cause of the current situation?",
                "correct_answer": "インフレーション",
                "difficulty": "advanced"
            },
            {
                "id": f"ex2_{timestamp}",
                "type": "free_form",
                "segment_start": 60.0,
                "segment_end": 90.0,
                "question": "Explain the speaker's position on the new government policy and the reasons they provided.",
                "correct_answer": "The speaker believes the new government policy will be ineffective because it doesn't address the root causes of inflation and may exacerbate existing economic inequalities.",
                "difficulty": "advanced"
            },
            {
                "id": f"ex3_{timestamp}",
                "type": "free_form",
                "segment_start": 100.0,
                "segment_end": 130.0,
                "question": "Compare and contrast the two solutions proposed in the discussion.",
                "correct_answer": "The first solution involves increasing interest rates to control inflation but risks slowing economic growth. The second solution proposes targeted subsidies for affected industries, which may be more effective but costlier to implement.",
                "difficulty": "advanced"
            }
        ]
    
    return exercises[:num_exercises]

async def check_answer(exercise, user_answer):
    """
    Check user's answer against the correct answer using Ollama
    
    Args:
        exercise: Exercise data
        user_answer: User's answer
        
    Returns:
        dict: Result with correctness and feedback
    """
    try:
        # For simple exercise types, we can check answers directly
        if exercise["type"] in ["multiple_choice", "fill_in"]:
            correct = user_answer.strip().lower() == exercise["correct_answer"].strip().lower()
            
            if correct:
                feedback = "Correct! Well done."
            else:
                feedback = f"Incorrect. The correct answer is: {exercise['correct_answer']}"
                
            return {"correct": correct, "feedback": feedback}
        
        # For free-form answers, use Ollama to evaluate
        client = OllamaClient()
        
        system_prompt = """
        You are a Japanese language teacher evaluating a student's answer to a listening comprehension question.
        Your task is to determine if the student's answer is correct and provide helpful feedback.
        Be forgiving of minor linguistic errors and focus on comprehension of the content.
        """
        
        prompt = f"""
        Question: {exercise['question']}
        
        Correct answer: {exercise['correct_answer']}
        
        Student's answer: {user_answer}
        
        Is the student's answer correct? Evaluate based on comprehension of content, not exact wording.
        Provide a score (0-100%) and specific feedback about what was correct or incorrect.
        
        Format your response as a JSON object with these fields:
        {{
            "correct": true/false,
            "score": percentage (0-100),
            "feedback": "Your detailed feedback here"
        }}
        """
        
        response = await client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )
        
        # Try to extract JSON from the response
        try:
            # Find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                return {
                    "correct": result.get("correct", False),
                    "feedback": result.get("feedback", "No specific feedback provided.")
                }
        except:
            logger.warning("Failed to parse JSON from Ollama response for answer check")
        
        # Fallback: Simple heuristic check
        return fallback_answer_check(exercise, user_answer)
        
    except Exception as e:
        logger.error(f"Error checking answer with Ollama: {str(e)}")
        # Fallback to simple check
        return fallback_answer_check(exercise, user_answer)

def fallback_answer_check(exercise, user_answer):
    """
    Fallback method for checking answers when Ollama is unavailable
    
    Args:
        exercise: Exercise data
        user_answer: User's answer
        
    Returns:
        dict: Result with correctness and feedback
    """
    if exercise["type"] in ["multiple_choice", "fill_in"]:
        correct = user_answer.strip().lower() == exercise["correct_answer"].strip().lower()
        
        if correct:
            feedback = "Correct! Well done."
        else:
            feedback = f"Incorrect. The correct answer is: {exercise['correct_answer']}"
            
        return {"correct": correct, "feedback": feedback}
    
    else:  # free_form
        # Check for keyword overlap
        correct_keywords = set(exercise["correct_answer"].lower().split())
        answer_keywords = set(user_answer.lower().split())
        
        common_keywords = correct_keywords.intersection(answer_keywords)
        keyword_ratio = len(common_keywords) / len(correct_keywords) if correct_keywords else 0
        
        if keyword_ratio >= 0.7:
            return {
                "correct": True,
                "feedback": "Good answer! You captured the key points."
            }
        elif keyword_ratio >= 0.4:
            return {
                "correct": True,
                "feedback": "Partially correct. You understood some key points, but missed others."
            }
        else:
            return {
                "correct": False,
                "feedback": "Your answer missed most of the key points. Try listening again and focus on the main ideas."
            }

def translate_text(text, source_lang="ja", target_lang="en"):
    """
    Translate text using Ollama
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        str: Translated text
    """
    try:
        client = OllamaClient()
        
        system_prompt = f"""
        You are a professional translator from {source_lang} to {target_lang}.
        Translate the given text accurately, maintaining the original meaning and nuance.
        Respond ONLY with the translation, without any additional comments or explanations.
        """
        
        prompt = f"Translate this text from {source_lang} to {target_lang}:\n\n{text}"
        
        translation = client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )
        
        return translation.strip()
        
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        return f"Translation error: {str(e)}" 