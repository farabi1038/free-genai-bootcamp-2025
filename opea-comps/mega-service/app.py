import json
import os
import logging
import asyncio
from typing import Dict, Any, Optional
from contextlib import contextmanager

import aiohttp
from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse

# Set up enhanced logging to replace tracing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a dummy tracing system using logging
@contextmanager
def log_span(name):
    logger.debug(f"Starting span: {name}")
    try:
        yield None
    finally:
        logger.debug(f"Ending span: {name}")

class DummyTracer:
    def start_as_current_span(self, name):
        return log_span(name)

# Create a dummy trace module for compatibility
class DummyTrace:
    def get_tracer(self, name):
        return DummyTracer()

# Create globals
trace = DummyTrace()
HAS_TELEMETRY = False

from comps.cores.proto.api_protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatMessage,
    UsageInfo
)
from comps.cores.mega.constants import ServiceType, ServiceRoleType
from comps.cores.proto.docarray import LLMParams
from comps import MicroService, ServiceOrchestrator

# Environment variables with defaults
LLM_SERVICE_HOST_IP = os.getenv("LLM_SERVICE_HOST_IP", "0.0.0.0")
LLM_SERVICE_PORT = int(os.getenv("LLM_SERVICE_PORT", "9000"))
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:1b")
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1024"))
CONNECTION_RETRY_COUNT = int(os.getenv("CONNECTION_RETRY_COUNT", "3"))
CONNECTION_RETRY_DELAY = int(os.getenv("CONNECTION_RETRY_DELAY", "5"))
SERVICE_NAME_VALUE = os.getenv("SERVICE_NAME", "llm-mega-service")

# Replace tracing setup with logging
def setup_tracing():
    """Set up enhanced logging instead of tracing."""
    logger.info("Using enhanced logging instead of OpenTelemetry tracing")
    return None

class LLMService:
    """Service orchestrating LLM requests through a DAG workflow."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Initialize the service with host and port configuration."""
        self.host = host
        self.port = port
        self.endpoint = "/v1/example-service"
        self.orchestrator = ServiceOrchestrator()
        self.services = {}  # Store reference to services for easier access
        os.environ["LOGFLAG"] = "true"  # Enable detailed logging
        self.tracer = DummyTracer()
        logger.info(f"Initializing service on {host}:{port}")
    
    async def verify_connections(self) -> bool:
        """Verify connections to external services."""
        with self.tracer.start_as_current_span("verify_connections"):
            # Check connection to the LLM service
            retry_count = int(os.getenv("CONNECTION_RETRY_COUNT", "5"))
            retry_delay = int(os.getenv("CONNECTION_RETRY_DELAY", "10"))
            
            if retry_count < 10:
                retry_count = 10  # Increase the number of retries to give Ollama more time to start
                
            if retry_delay < 10:
                retry_delay = 10  # Ensure a minimum 10 second delay between retries
                
            logger.info(f"Attempting to connect to Ollama with {retry_count} retries and {retry_delay}s delay")
            
            # URL for the API to check status
            api_url = f"http://{LLM_SERVICE_HOST_IP}:{LLM_SERVICE_PORT}/api/tags"
            
            for attempt in range(retry_count):
                try:
                    logger.info(f"Attempt {attempt+1}/{retry_count} to connect to LLM service: {api_url}")
                    async with aiohttp.ClientSession() as session:
                        async with session.get(api_url) as response:
                            if response.status == 200:
                                models = await response.json()
                                model_count = len(models.get("models", []))
                                logger.info(f"Successfully connected to LLM service with {model_count} available models")
                                return True
                            else:
                                logger.warning(f"Failed to connect to LLM service, status: {response.status}")
                except Exception as e:
                    logger.warning(f"Failed to connect to LLM service: {str(e)}")
            
            if attempt < retry_count - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                
            logger.error("All connection attempts to LLM service failed")
            return False
    
    def setup_services(self) -> None:
        """Set up microservices and define the workflow DAG."""
        with self.tracer.start_as_current_span("setup_services"):
            # Create the LLM microservice
            llm = MicroService(
                name="llm",
                host=LLM_SERVICE_HOST_IP,
                port=LLM_SERVICE_PORT,
                endpoint="/v1/chat/completions",
                use_remote_service=True,
                service_type=ServiceType.LLM,
                service_role=ServiceRoleType.MICROSERVICE,
            )
            
            logger.info(f"Adding LLM service: http://{LLM_SERVICE_HOST_IP}:{LLM_SERVICE_PORT}{llm.endpoint}")
            
            # Store reference to services
            self.services["llm"] = llm
            
            # Add to orchestrator (in more complex flows, flow_to() would connect multiple services)
            self.orchestrator.add(llm)
            
            # Example of a more complex flow (commented out, just for demonstration)
            # Could be extended for a RAG pipeline or other workflows
            """
            # Create an embedding service
            embedding = MicroService(
                name="embedding",
                host=EMBEDDING_HOST_IP,
                port=EMBEDDING_PORT,
                endpoint="/v1/embeddings",
                use_remote_service=True,
                service_type=ServiceType.EMBEDDING,
                service_role=ServiceRoleType.MICROSERVICE,
            )
            
            # Create a retriever service
            retriever = MicroService(
                name="retriever",
                host=RETRIEVER_HOST_IP,
                port=RETRIEVER_PORT,
                endpoint="/v1/retrieve",
                use_remote_service=True,
                service_type=ServiceType.RETRIEVER,
                service_role=ServiceRoleType.MICROSERVICE,
            )
            
            # Add all services to the orchestrator
            self.orchestrator.add(embedding).add(retriever).add(llm)
            
            # Define the flow between services
            self.orchestrator.flow_to(embedding, retriever)
            self.orchestrator.flow_to(retriever, llm)
            
            # Store references
            self.services["embedding"] = embedding
            self.services["retriever"] = retriever
            """
    
    async def initialize(self) -> bool:
        """Initialize the service and verify connections.
        
        Returns:
            bool: True if initialization is successful, False otherwise
        """
        with self.tracer.start_as_current_span("initialize"):
            # Set up services
            self.setup_services()
            
            # Verify connections
            return await self.verify_connections()
    
    def start(self) -> None:
        """Start the service and register routes."""
        with self.tracer.start_as_current_span("start_service"):
            # Create mega-service endpoint
            self.service = MicroService(
                name=self.__class__.__name__,
                service_role=ServiceRoleType.MEGASERVICE,
                host=self.host,
                port=self.port,
                endpoint=self.endpoint,
                input_datatype=ChatCompletionRequest,
                output_datatype=ChatCompletionResponse,
            )

            # Add health check route
            self.service.add_route("/health", self.health_check, methods=["GET"])
            
            # Add model list route
            self.service.add_route("/models", self.list_models, methods=["GET"])

            # Register request handler and start service
            self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])
            
            logger.info(f"Starting service with endpoint: {self.endpoint}")
            self.service.start()
    
    async def health_check(self, request: Request):
        """Health check endpoint."""
        with self.tracer.start_as_current_span("health_check"):
            healthy = await self.verify_connections()
            return {"status": "healthy" if healthy else "unhealthy"}
    
    async def list_models(self, request: Request):
        """List available models from the LLM service."""
        with self.tracer.start_as_current_span("list_models"):
            try:
                if "llm" not in self.services:
                    return {"error": "LLM service not configured"}
                    
                llm_service = self.services["llm"]
                llm_url = f"http://{llm_service.host}:{llm_service.port}/api/tags"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(llm_url) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            return {"error": f"Failed to get models, status: {response.status}"}
            except Exception as e:
                logger.exception(f"Error listing models: {e}")
                return {"error": str(e)}
        
    async def handle_request(self, request: Request) -> ChatCompletionResponse:
        """Handle incoming chat completion requests."""
        with self.tracer.start_as_current_span("handle_request"):
            try:
                # Parse and validate request
                data = await request.json()
                chat_request = ChatCompletionRequest.model_validate(data)
                
                # Create LLM parameters
                llm_params = LLMParams(
                    max_tokens=chat_request.max_tokens or DEFAULT_MAX_TOKENS,
                    temperature=chat_request.temperature or 0.7,
                    top_p=chat_request.top_p or 0.95,
                    stream=chat_request.stream or False,
                    model=chat_request.model or DEFAULT_MODEL,
                    top_k=chat_request.top_k or 10,
                    frequency_penalty=chat_request.frequency_penalty or 0.0,
                    presence_penalty=chat_request.presence_penalty or 0.0,
                    repetition_penalty=chat_request.repetition_penalty or 1.03,
                    chat_template=chat_request.chat_template,
                )
                
                # Prepare initial inputs for the service orchestrator
                initial_inputs = {"messages": chat_request.messages}
                
                # Execute the workflow through the orchestrator
                with self.tracer.start_as_current_span("orchestrator_schedule"):
                    result_dict, runtime_graph = await self.orchestrator.schedule(
                        initial_inputs=initial_inputs,
                        llm_parameters=llm_params
                    )
                
                # Handle streaming response if available
                for node, response in result_dict.items():
                    if isinstance(response, StreamingResponse):
                        return response
                
                # Process regular response
                last_node = runtime_graph.all_leaves()[-1]
                if last_node not in result_dict:
                    raise HTTPException(status_code=500, detail="No response received from LLM service")
                
                # Extract content from response
                service_result = result_dict[last_node]
                content = self._extract_content(service_result)
                
                # Return formatted response
                return ChatCompletionResponse(
                    model=chat_request.model or DEFAULT_MODEL,
                    choices=[
                        ChatCompletionResponseChoice(
                            index=0,
                            message=ChatMessage(role="assistant", content=content),
                            finish_reason="stop",
                        )
                    ],
                    usage=UsageInfo(prompt_tokens=0, completion_tokens=0, total_tokens=0)
                )
                
            except Exception as e:
                logger.exception(f"Error processing request: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _extract_content(self, result: Any) -> str:
        """Extract content from various response formats."""
        if isinstance(result, dict):
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0].get('message', {}).get('content', '')
            elif 'error' in result:
                error = result['error']
                raise HTTPException(
                    status_code=400 if error.get('type') == 'invalid_request_error' else 500,
                    detail=error.get('message', 'Unknown error')
                )
        
        return str(result)


async def startup() -> None:
    """Async startup function to initialize and start the service."""
    # Set up tracing
    tracer_provider = setup_tracing()
    
    # Create and start the service
    service = LLMService()
    if await service.initialize():
        # Don't call start() directly - modify to use async pattern instead
        try:
            # Register routes directly here
            from fastapi import FastAPI
            from uvicorn import Config, Server
            
            # Create FastAPI app
            app = FastAPI()
            
            # Add routes manually
            @app.get("/health")
            async def health():
                logger.info("Health check endpoint called")
                return await service.health_check(None)
                
            @app.get("/models")
            async def models():
                logger.info("Models endpoint called")
                return await service.list_models(None)
                
            @app.post(service.endpoint)
            async def handle_request(request: Request):
                logger.info(f"Request received at {service.endpoint}")
                try:
                    result = await service.handle_request(request)
                    logger.info(f"Request processed successfully: {type(result)}")
                    return result
                except Exception as e:
                    logger.exception(f"Error processing request: {e}")
                    raise
                
            # Log startup with VERY visible messages
            logger.info("=" * 50)
            logger.info(f"MEGA SERVICE STARTING ON {service.host}:{service.port}")
            logger.info(f"ENDPOINT: {service.endpoint}")
            logger.info(f"OLLAMA HOST: {LLM_SERVICE_HOST_IP}")
            logger.info(f"OLLAMA PORT: {LLM_SERVICE_PORT}")
            logger.info(f"DEFAULT MODEL: {DEFAULT_MODEL}")
            logger.info("=" * 50)
            
            # Start the server using uvicorn directly
            config = Config(app, host=service.host, port=service.port)
            server = Server(config)
            await server.serve()
        except Exception as e:
            logger.exception(f"Error starting service: {e}")
            exit(1)
    else:
        logger.error("Failed to initialize service, exiting...")
        exit(1)


if __name__ == "__main__":
    # Use asyncio.run to start the async function
    asyncio.run(startup())