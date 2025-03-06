import json
import os
import logging
import asyncio
from typing import Dict, Any, Optional

import aiohttp
from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.aiohttp import AioHttpClientInstrumentor

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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables with defaults
LLM_SERVICE_HOST_IP = os.getenv("LLM_SERVICE_HOST_IP", "0.0.0.0")
LLM_SERVICE_PORT = int(os.getenv("LLM_SERVICE_PORT", "9000"))
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:1b")
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1024"))
CONNECTION_RETRY_COUNT = int(os.getenv("CONNECTION_RETRY_COUNT", "3"))
CONNECTION_RETRY_DELAY = int(os.getenv("CONNECTION_RETRY_DELAY", "5"))
JAEGER_HOST = os.getenv("JAEGER_HOST", "jaeger")
JAEGER_PORT = int(os.getenv("JAEGER_PORT", "6831"))
SERVICE_NAME_VALUE = os.getenv("SERVICE_NAME", "llm-mega-service")


def setup_tracing():
    """Configure OpenTelemetry tracing with Jaeger exporter."""
    # Create a resource with service name
    resource = Resource(attributes={
        SERVICE_NAME: SERVICE_NAME_VALUE
    })
    
    # Create a tracer provider
    tracer_provider = TracerProvider(resource=resource)
    
    # Create a Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=JAEGER_HOST,
        agent_port=JAEGER_PORT,
    )
    
    # Add the exporter to the tracer provider
    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    
    # Set the tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    # Instrument aiohttp client
    AioHttpClientInstrumentor().instrument()
    
    return tracer_provider


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
        self.tracer = trace.get_tracer(__name__)
        logger.info(f"Initializing service on {host}:{port}")
    
    async def verify_connections(self) -> bool:
        """Verify connections to all dependent services.
        
        Returns:
            bool: True if all connections are successful, False otherwise
        """
        with self.tracer.start_as_current_span("verify_connections"):
            if "llm" not in self.services:
                logger.error("LLM service has not been set up yet")
                return False
            
            llm_service = self.services["llm"]
            llm_url = f"http://{llm_service.host}:{llm_service.port}/api/tags"
            
            for attempt in range(CONNECTION_RETRY_COUNT):
                try:
                    logger.info(f"Attempt {attempt+1}/{CONNECTION_RETRY_COUNT} to connect to LLM service: {llm_url}")
                    async with aiohttp.ClientSession() as session:
                        async with session.get(llm_url) as response:
                            if response.status == 200:
                                models = await response.json()
                                model_count = len(models.get("models", []))
                                logger.info(f"Successfully connected to LLM service with {model_count} available models")
                                return True
                            else:
                                logger.warning(f"Failed to connect to LLM service, status: {response.status}")
                except Exception as e:
                    logger.warning(f"Failed to connect to LLM service: {str(e)}")
            
            if attempt < CONNECTION_RETRY_COUNT - 1:
                logger.info(f"Retrying in {CONNECTION_RETRY_DELAY} seconds...")
                await asyncio.sleep(CONNECTION_RETRY_DELAY)
                
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
            
            # Instrument FastAPI app with OpenTelemetry
            FastAPIInstrumentor.instrument_app(self.service.app)
            
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
        with self.tracer.start_as_current_span("handle_request") as span:
            try:
                # Parse and validate request
                data = await request.json()
                chat_request = ChatCompletionRequest.model_validate(data)
                
                # Add metadata to span
                span.set_attribute("llm.model", chat_request.model or DEFAULT_MODEL)
                span.set_attribute("llm.max_tokens", chat_request.max_tokens or DEFAULT_MAX_TOKENS)
                span.set_attribute("llm.temperature", chat_request.temperature or 0.7)
                span.set_attribute("llm.stream", chat_request.stream or False)
                
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
                span.record_exception(e)
                span.set_status(trace.StatusCode.ERROR, str(e))
                raise HTTPException(status_code=500, detail=str(e))
    
    def _extract_content(self, result: Any) -> str:
        """Extract content from various response formats."""
        with self.tracer.start_as_current_span("extract_content"):
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
        service.start()
    else:
        logger.error("Failed to initialize service, exiting...")
        exit(1)


if __name__ == "__main__":
    # Create and start the service
    asyncio.run(startup())