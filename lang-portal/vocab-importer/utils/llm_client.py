import requests
import logging
import time
import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

# -------------------- OPEA Protocol Classes --------------------

class ServiceType:
    """Defines the types of services in OPEA architecture."""
    LLM = "llm"
    EMBEDDING = "embedding"
    RETRIEVER = "retriever"
    RERANKER = "reranker"

class ServiceRoleType:
    """Defines the roles services can play in OPEA architecture."""
    MICROSERVICE = "microservice"
    MEGASERVICE = "megaservice"

class LLMParams:
    """Parameters for LLM service requests."""
    def __init__(self, 
                 model: str = "llama2",
                 temperature: float = 0.7,
                 top_p: float = 0.9,
                 top_k: int = 40,
                 max_tokens: int = 1024,
                 system_prompt: Optional[str] = None):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary for API requests."""
        params = {
            "model": self.model,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "num_predict": self.max_tokens
            }
        }
        return params

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMParams':
        """Create LLMParams from dictionary."""
        options = data.get("options", {})
        return cls(
            model=data.get("model", "llama2"),
            temperature=options.get("temperature", 0.7),
            top_p=options.get("top_p", 0.9),
            top_k=options.get("top_k", 40),
            max_tokens=options.get("num_predict", 1024)
        )

class ChatMessage:
    """Represents a message in a chat conversation."""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary for API requests."""
        return {
            "role": self.role,
            "content": self.content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ChatMessage':
        """Create ChatMessage from dictionary."""
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", "")
        )

class ChatCompletionRequest:
    """Request format for chat completion API."""
    def __init__(self, 
                 messages: List[ChatMessage],
                 model: str = "llama2",
                 temperature: float = 0.7,
                 max_tokens: int = 1024,
                 stream: bool = False):
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for API requests."""
        return {
            "model": self.model,
            "messages": [m.to_dict() for m in self.messages],
            "stream": self.stream,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionRequest':
        """Create ChatCompletionRequest from dictionary."""
        messages = [ChatMessage.from_dict(m) for m in data.get("messages", [])]
        options = data.get("options", {})
        return cls(
            messages=messages,
            model=data.get("model", "llama2"),
            temperature=options.get("temperature", 0.7),
            max_tokens=options.get("num_predict", 1024),
            stream=data.get("stream", False)
        )

class UsageInfo:
    """Information about token usage in a request/response."""
    def __init__(self, prompt_tokens: int = 0, completion_tokens: int = 0):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = prompt_tokens + completion_tokens
    
    def to_dict(self) -> Dict[str, int]:
        """Convert usage info to dictionary."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }

class ChatCompletionResponseChoice:
    """A single response choice from a chat completion."""
    def __init__(self, message: ChatMessage, finish_reason: str = "stop", index: int = 0):
        self.message = message
        self.finish_reason = finish_reason
        self.index = index
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response choice to dictionary."""
        return {
            "message": self.message.to_dict(),
            "finish_reason": self.finish_reason,
            "index": self.index
        }

class ChatCompletionResponse:
    """Response from a chat completion API."""
    def __init__(self, 
                 choices: List[ChatCompletionResponseChoice],
                 model: str = "llama2",
                 usage: Optional[UsageInfo] = None,
                 id: Optional[str] = None):
        self.choices = choices
        self.model = model
        self.usage = usage or UsageInfo()
        self.id = id or f"chatcmpl-{int(time.time())}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "id": self.id,
            "model": self.model,
            "choices": [c.to_dict() for c in self.choices],
            "usage": self.usage.to_dict()
        }
    
    @property
    def content(self) -> str:
        """Get the content from the first choice's message."""
        if not self.choices:
            return ""
        return self.choices[0].message.content

# -------------------- OPEA Service Classes --------------------

class MicroService:
    """Represents a microservice in the OPEA architecture."""
    
    def __init__(self, 
                 name: str,
                 host: str = "localhost",
                 port: int = 11434,
                 endpoint: str = "/api/chat",
                 use_remote_service: bool = True,
                 service_type: str = ServiceType.LLM,
                 service_role: str = ServiceRoleType.MICROSERVICE):
        """Initialize a microservice.
        
        Args:
            name: Service name
            host: Hostname or IP
            port: Port number
            endpoint: API endpoint
            use_remote_service: Whether to connect to a remote service
            service_type: Type of service (LLM, embedding, etc.)
            service_role: Role in the architecture
        """
        self.name = name
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.use_remote_service = use_remote_service
        self.service_type = service_type
        self.service_role = service_role
        self.base_url = f"http://{host}:{port}"
        self.full_url = f"{self.base_url}{endpoint}"
        
        # For tracking flow connections
        self.connected_to = []
        
        logger.info(f"Initialized {service_type} service '{name}' at {self.full_url}")
    
    async def health_check(self) -> bool:
        """Check if the service is available and responsive."""
        try:
            async with requests.sessions.AsyncSession() as session:
                response = await session.get(f"{self.base_url}/api/tags", timeout=3)
                if response.status_code == 200:
                    return True
            return False
        except Exception as e:
            logger.warning(f"Health check failed for service {self.name}: {str(e)}")
            return False
    
    async def process(self, data: Any) -> Any:
        """Process a request through this service.
        
        This is a placeholder that should be overridden by specific service implementations.
        """
        logger.info(f"Processing request through {self.name} service")
        return data
    
    def connect_to(self, service: 'MicroService') -> None:
        """Connect this service to another in the workflow."""
        if service not in self.connected_to:
            self.connected_to.append(service)
            logger.info(f"Connected service {self.name} to {service.name}")

class LLMService(MicroService):
    """Specific implementation of a Language Model microservice."""
    
    def __init__(self, 
                 name: str = "llm",
                 host: str = "localhost",
                 port: int = 11434,
                 model: str = "llama2"):
        """Initialize an LLM service.
        
        Args:
            name: Service name
            host: Hostname or IP
            port: Port number
            model: Default model to use
        """
        super().__init__(
            name=name,
            host=host,
            port=port,
            endpoint="/api/chat",
            service_type=ServiceType.LLM,
            service_role=ServiceRoleType.MICROSERVICE
        )
        self.model = model
    
    async def generate_text(self, 
                           prompt: str,
                           system_prompt: Optional[str] = None,
                           max_tokens: int = 1024,
                           temperature: float = 0.7,
                           max_retries: int = 2) -> str:
        """Generate text using the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            max_retries: Maximum number of retries
            
        Returns:
            Generated text content
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append(ChatMessage("system", system_prompt))
        
        # Add user prompt
        messages.append(ChatMessage("user", prompt))
        
        # Create request
        request = ChatCompletionRequest(
            messages=messages,
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Determine timeout based on request complexity
        timeout = 60
        if "japanese" in prompt.lower() or max_tokens > 2000:
            timeout = 120
        
        # Process request
        for attempt in range(max_retries + 1):
            try:
                request_data = request.to_dict()
                logger.debug(f"Sending request to LLM API: {request_data}")
                
                async with requests.sessions.AsyncSession() as session:
                    response = await session.post(
                        self.full_url,
                        json=request_data,
                        timeout=timeout
                    )
                
                if response.status_code == 200:
                    response_data = response.json()
                    message_content = response_data.get("message", {}).get("content", "")
                    logger.info(f"Successfully generated text of length {len(message_content)}")
                    return message_content
                
                error_message = f"LLM API request failed: {response.status_code}"
                try:
                    error_detail = response.json().get("error", "")
                    if error_detail:
                        error_message += f", Details: {error_detail}"
                except:
                    pass
                    
                logger.error(error_message)
                
                # Only retry if we haven't reached the limit
                if attempt < max_retries:
                    retry_delay = (attempt + 1) * 3
                    logger.info(f"Retrying in {retry_delay} seconds... (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                    continue
                
                return f"Error: Failed to generate text (Status code: {response.status_code})"
            
            except Exception as e:
                logger.error(f"LLM API request failed with error: {str(e)}")
                if attempt < max_retries:
                    retry_delay = (attempt + 1) * 3
                    logger.info(f"Retrying in {retry_delay} seconds... (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                    continue
                return f"Error: {str(e)}"
    
    async def process(self, data: Union[str, Dict, ChatCompletionRequest]) -> str:
        """Process a request through this LLM service.
        
        Args:
            data: Either a string prompt, a dictionary with request parameters,
                 or a ChatCompletionRequest object
                 
        Returns:
            Generated text
        """
        if isinstance(data, str):
            # Simple string prompt
            return await self.generate_text(data)
        
        elif isinstance(data, dict):
            # Dictionary with parameters
            prompt = data.get("prompt", "")
            system_prompt = data.get("system_prompt")
            max_tokens = data.get("max_tokens", 1024)
            temperature = data.get("temperature", 0.7)
            
            return await self.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
        
        elif isinstance(data, ChatCompletionRequest):
            # Full request object
            user_messages = [m for m in data.messages if m.role == "user"]
            system_messages = [m for m in data.messages if m.role == "system"]
            
            if not user_messages:
                return "Error: No user message provided"
            
            prompt = user_messages[-1].content
            system_prompt = system_messages[-1].content if system_messages else None
            
            return await self.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=data.max_tokens,
                temperature=data.temperature
            )
        
        else:
            return "Error: Unsupported request format"
        
class ServiceOrchestrator:
    """Manages the execution flow between multiple services."""
    
    def __init__(self):
        """Initialize a service orchestrator."""
        self.services = {}
        self.connections = {}
        logger.info("Initialized ServiceOrchestrator")
    
    def add(self, service: MicroService) -> 'ServiceOrchestrator':
        """Add a service to the orchestrator.
        
        Args:
            service: The microservice to add
            
        Returns:
            Self, for chaining
        """
        self.services[service.name] = service
        self.connections[service.name] = []
        logger.info(f"Added service '{service.name}' to orchestrator")
        return self
    
    def flow_to(self, from_service: MicroService, to_service: MicroService) -> 'ServiceOrchestrator':
        """Define a flow connection between two services.
        
        Args:
            from_service: Source service
            to_service: Destination service
            
        Returns:
            Self, for chaining
        """
        if from_service.name not in self.services:
            self.add(from_service)
        
        if to_service.name not in self.services:
            self.add(to_service)
        
        # Add the connection if it doesn't exist
        if to_service.name not in self.connections[from_service.name]:
            self.connections[from_service.name].append(to_service.name)
            from_service.connect_to(to_service)
            
        logger.info(f"Added flow from '{from_service.name}' to '{to_service.name}'")
        return self
    
    async def process(self, data: Any, start_service: str) -> Any:
        """Process data through the service flow.
        
        Args:
            data: The input data
            start_service: Name of the service to start with
            
        Returns:
            Processed data after flowing through services
        """
        if start_service not in self.services:
            raise ValueError(f"Service '{start_service}' not found in orchestrator")
        
        # Start with the initial service
        current_service = self.services[start_service]
        result = await current_service.process(data)
        
        # Follow the flow to connected services
        processed = {start_service}
        queue = self.connections[start_service][:]
        
        while queue:
            next_service_name = queue.pop(0)
            
            # Skip if already processed to avoid cycles
            if next_service_name in processed:
                continue
                
            # Process the data through this service
            next_service = self.services[next_service_name]
            result = await next_service.process(result)
            
            # Mark as processed and add its connections to the queue
            processed.add(next_service_name)
            queue.extend([conn for conn in self.connections[next_service_name] 
                          if conn not in processed])
        
        return result

# -------------------- Legacy LLMClient (Synchronous) --------------------

class LLMClient:
    """Legacy synchronous client for interacting with Ollama API."""
    
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

# Create async-compatible client
async def get_llm_service(host: str = "localhost", port: int = 11434, model: str = "llama2") -> LLMService:
    """Get an LLM service instance.
    
    Args:
        host: Hostname or IP
        port: Port number
        model: Default model to use
        
    Returns:
        An initialized LLM service
    """
    return LLMService(host=host, port=port, model=model) 