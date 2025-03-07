import requests
import logging
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:1b"):
        """Initialize the LLM client.
        
        Args:
            base_url: The base URL of the Ollama API
            model: The model ID to use for generating responses
        """
        self.base_url = base_url
        self.model = model
        self.chat_endpoint = f"{base_url}/api/chat"
        logger.info(f"LLM client initialized with URL: {base_url}, model: {model}")
    
    def check_health(self, max_retries: int = 1, retry_delay: int = 1) -> bool:
        """Check if the LLM API is available and responsive.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            bool: True if the API is available and responsive, False otherwise
        """
        for attempt in range(max_retries):
            try:
                # Ollama API provides a /api/tags endpoint to list available models
                logger.info(f"Health check attempt {attempt+1}/{max_retries} for {self.base_url}")
                response = requests.get(f"{self.base_url}/api/tags", timeout=2)  # Shorter timeout
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_count = len(models)
                    logger.info(f"LLM API is healthy with {model_count} available models")
                    return True
                logger.warning(f"LLM API health check failed with status code: {response.status_code}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error during health check to {self.base_url}")
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout during health check to {self.base_url}")
            except Exception as e:
                logger.error(f"LLM API health check failed with error: {str(e)}")
            
            # Only sleep if we're going to retry
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        
        return False
    
    def generate_text(self, prompt: str, max_tokens: int = 1024, system_prompt: Optional[str] = None, max_retries: int = 2) -> str:
        """Generate text using the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum number of tokens to generate
            system_prompt: Optional system prompt to set context
            max_retries: Maximum number of retry attempts
            
        Returns:
            str: The generated text
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user prompt
        messages.append({"role": "user", "content": prompt})
        
        # Determine timeout based on request complexity
        # Longer timeouts for Japanese/complex language generation
        if "japanese" in prompt.lower() or "kanji" in prompt.lower() or "romaji" in prompt.lower():
            request_timeout = 120  # 2 minutes for Japanese generation
        else:
            request_timeout = 60   # 1 minute for other languages
            
        # Adjust for large token requests
        if max_tokens > 2000:
            request_timeout = max(request_timeout, 180)  # At least 3 minutes for large generations
        
        for attempt in range(max_retries + 1):
            try:
                request_data = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7,  # Add some randomness but not too much
                        "top_p": 0.9,        # Filter out less likely tokens for better quality
                        "top_k": 40          # Consider top 40 tokens for better variety
                    }
                }
                
                logger.debug(f"Sending request to LLM API: {request_data}")
                logger.info(f"Generation request with timeout: {request_timeout}s")
                
                response = requests.post(self.chat_endpoint, json=request_data, timeout=request_timeout)
                
                if response.status_code == 200:
                    response_data = response.json()
                    generated_text = response_data.get("message", {}).get("content", "")
                    logger.info(f"Successfully generated text of length {len(generated_text)}")
                    return generated_text
                
                error_message = f"LLM API request failed: {response.status_code}"
                try:
                    # Try to get more detailed error info
                    error_detail = response.json().get("error", "")
                    if error_detail:
                        error_message += f", Details: {error_detail}"
                except:
                    pass
                    
                logger.error(error_message)
                
                # Only sleep if we're going to retry
                if attempt < max_retries:
                    retry_delay = (attempt + 1) * 3  # Exponential backoff: 3s, 6s
                    logger.info(f"Retrying in {retry_delay} seconds... (attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                
                return f"Error: Failed to generate text (Status code: {response.status_code})"
            
            except requests.exceptions.Timeout:
                logger.error(f"LLM API request timed out after {request_timeout} seconds")
                if attempt < max_retries:
                    retry_delay = (attempt + 1) * 3
                    logger.info(f"Retrying in {retry_delay} seconds... (attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                return "Error: Request timed out. The model might be too slow or unavailable."
            
            except Exception as e:
                logger.error(f"LLM API request failed with error: {str(e)}")
                if attempt < max_retries:
                    retry_delay = (attempt + 1) * 3
                    logger.info(f"Retrying in {retry_delay} seconds... (attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                return f"Error: {str(e)}" 