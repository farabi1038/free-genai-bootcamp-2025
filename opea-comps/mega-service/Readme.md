# Mega Service LLM API

This service demonstrates the OPEA microservices architecture by implementing a simple API for LLM interactions using Ollama. The service is built on the OPEA components framework with a ServiceOrchestrator to manage the workflow.

## Description

The Mega Service LLM API is a flexible, production-ready orchestration layer for Large Language Models (LLMs) that implements the OPEA (Open and Pluggable Enterprise AI) architectural principles. This service provides the following capabilities:

### What It Does

- **LLM API Gateway**: Provides a standardized API for interacting with language models through Ollama
- **Service Orchestration**: Routes requests through a configurable pipeline of AI services
- **Observability**: Delivers detailed tracing and monitoring for all requests
- **Extensibility**: Serves as a foundation for building complex AI workflows

### Key Benefits

- **Simplified Integration**: Abstracts away the complexities of direct LLM API interactions
- **Scalable Architecture**: Built on microservices principles for horizontal scaling
- **Enhanced Reliability**: Connection verification, retry logic, and robust error handling
- **Comprehensive Monitoring**: Full tracing of requests through the entire processing pipeline
- **Enterprise Ready**: Supports containerization, health checks, and production deployment patterns

### Use Cases

1. **Chat Applications**: Power interactive chat interfaces with LLM capabilities
2. **Knowledge Systems**: Extend to RAG (Retrieval-Augmented Generation) workflows by adding embedding and retrieval services
3. **AI Orchestration**: Serve as a foundation for complex multi-step AI processing pipelines
4. **Enterprise Integration**: Provide a consistent interface for LLM capabilities within larger enterprise systems

### How It Works

The service receives requests through its API, processes them through the service orchestrator (which can be configured with multiple services in a directed acyclic graph), and returns the results. All steps are traced for observability, with robust error handling throughout the process.

### Visual Overview

#### Basic Architecture
```
┌─────────────┐      ┌───────────────────┐      ┌─────────────┐
│             │      │                   │      │             │
│   Client    │──────▶  Mega Service API │──────▶    LLM      │
│             │      │                   │      │  Service    │
└─────────────┘      └───────────────────┘      └─────────────┘
                               │
                               │
                      ┌────────▼─────────┐
                      │                  │
                      │  Jaeger Tracing  │
                      │                  │
                      └──────────────────┘
```

#### Detailed Data Flow
```
┌──────────┐     ┌──────────────────────────────────────────────┐     ┌──────────┐
│          │     │                Mega Service                   │     │          │
│          │     │ ┌────────────┐  ┌─────────────────────────┐  │     │          │
│  Client  │────▶│ │ FastAPI    │─▶│ Service Orchestrator    │──┼────▶│  Ollama  │
│ Request  │     │ │ Endpoint   │  │ (Directed Acyclic Graph)│  │     │  LLM API │
│          │     │ └────────────┘  └─────────────────────────┘  │     │          │
└──────────┘     │        ▲                     │               │     └──────────┘
                 └────────┼─────────────────────┼───────────────┘
                          │                     │
                          │                     ▼
                 ┌────────┴─────────┐  ┌───────────────────┐
                 │                  │  │                   │
                 │    Response      │  │  OpenTelemetry    │
                 │                  │  │  Tracing (Jaeger) │
                 └──────────────────┘  └───────────────────┘
```

#### Complex RAG Pipeline Example
```
┌─────────┐    ┌───────────────────────────────────────────────────────────┐
│         │    │                       Mega Service                         │
│ Client  │───▶│                                                           │
│ Request │    │  ┌──────────┐   ┌──────────┐   ┌─────────┐   ┌────────┐   │
└─────────┘    │  │          │   │          │   │         │   │        │   │
               │  │Embedding │──▶│Retriever │──▶│ Reranker│──▶│  LLM   │   │
               │  │ Service  │   │ Service  │   │ Service │   │Service │   │
               │  └──────────┘   └──────────┘   └─────────┘   └────────┘   │
               │                                                           │
               └───────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │                 │
                              │  LLM Response   │
                              │                 │
                              └─────────────────┘
```

## Architecture

This service demonstrates key concepts of the OPEA architecture:

- **MicroService**: Each service component (LLM service in this case) is implemented as a MicroService with specific service types and roles
- **ServiceOrchestrator**: Manages the flow of data between services through a Directed Acyclic Graph (DAG) 
- **Protocol Models**: Standardized data models for requests and responses
- **OpenTelemetry Tracing**: Distributed tracing with Jaeger integration

## Features

- Simple API for sending chat completion requests
- Support for streaming responses
- Configurable LLM parameters (temperature, max tokens, etc.)
- Connection verification with retry logic
- Integration with Jaeger for observability
- Extensible architecture for complex pipelines
- Health check and model listing endpoints
- Full distributed tracing with OpenTelemetry

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9 or higher
- [Optional] jq for pretty JSON output

### Step 1: Start the Infrastructure

Start Ollama and Jaeger using Docker Compose:

```sh
LLM_ENDPOINT_PORT=9000 docker compose up -d
```

This will:
- Start Jaeger UI on port 16686
- Start Ollama on port 9000 (configurable via LLM_ENDPOINT_PORT)

### Step 2: Download an LLM Model

Download a model via the Ollama API:

```sh
curl http://localhost:9000/api/pull -d '{
  "model": "llama3.2:1b"
}'
```

### Step 3: Install Dependencies

```sh
pip install -r requirements.txt
```

### Step 4: Start the Service

```sh
python app.py
```

The service will be available at `http://localhost:8000/v1/example-service`.

The service will automatically:
1. Set up the microservices
2. Verify connections to dependent services (with retries)
3. Configure OpenTelemetry tracing with Jaeger
4. Start the API server if connections are successful

### Step 5: Test the Service

Run the included test script to verify that the service is working correctly:

```sh
python test_service.py
```

The test script will:
1. Test Ollama directly to verify it's working
2. Test the health check endpoint
3. Test the models listing endpoint
4. Test the chat completion endpoint

You can customize the test with command-line arguments:

```sh
python test_service.py --base-url http://localhost:8000 --ollama-url http://localhost:9000 --model llama3.2:1b
```

If all tests pass, you'll see a success message. If any tests fail, the script will provide detailed error information to help troubleshoot.

## Comprehensive Installation Guide

This section provides a more detailed installation process for different environments.

### Local Development Setup

1. **Clone the repository**
   ```sh
   git clone https://github.com/your-org/mega-service.git
   cd mega-service
   ```

2. **Create a virtual environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Start the infrastructure services**
   ```sh
   LLM_ENDPOINT_PORT=9000 docker compose up -d
   ```

5. **Pull an LLM model**
   ```sh
   curl http://localhost:9000/api/pull -d '{
     "model": "llama3.2:1b"
   }'
   ```

6. **Start the service**
   ```sh
   python app.py
   ```

### Docker-Based Deployment

1. **Build the Docker image**
   ```sh
   docker build -t mega-service:latest .
   ```

2. **Start all services with Docker Compose**
   ```sh
   docker compose up -d
   ```

3. **Pull an LLM model**
   ```sh
   curl http://localhost:9000/api/pull -d '{
     "model": "llama3.2:1b"
   }'
   ```

4. **Verify the services are running**
   ```sh
   docker ps
   ```

5. **Check the service logs**
   ```sh
   docker logs mega-service
   ```

### Production Deployment Considerations

For production deployments, consider the following:

1. **Resource Requirements**
   - CPU: 2+ cores recommended
   - RAM: 4GB+ recommended (depends on LLM model size)
   - Disk: 2GB for service + space for LLM models

2. **Security**
   - Set up proper firewall rules
   - Consider adding authentication to the API
   - Use HTTPS for all external communications

3. **High Availability**
   - Deploy multiple instances behind a load balancer
   - Configure health checks for automatic recovery
   - Set up monitoring and alerting

4. **Configuration**
   - Use environment variables for all configuration
   - Consider using a configuration management system
   - Separate configuration for development, staging, and production

5. **Monitoring**
   - Set up Prometheus for metrics collection
   - Configure alerts for service health
   - Use Jaeger for distributed tracing

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| LLM_SERVICE_HOST_IP | Host for LLM service | 0.0.0.0 |
| LLM_SERVICE_PORT | Port for LLM service | 9000 |
| DEFAULT_MODEL | Default LLM model | llama3.2:1b |
| DEFAULT_MAX_TOKENS | Default max tokens | 1024 |
| CONNECTION_RETRY_COUNT | Number of connection retry attempts | 3 |
| CONNECTION_RETRY_DELAY | Delay in seconds between retries | 5 |
| JAEGER_HOST | Hostname for Jaeger agent | jaeger |
| JAEGER_PORT | Port for Jaeger agent | 6831 |
| SERVICE_NAME | Service name for tracing | llm-mega-service |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/example-service` | POST | Main chat completion endpoint |
| `/health` | GET | Health check endpoint |
| `/models` | GET | List available LLM models |
| `/v1/health_check` | GET | Built-in health check (from MicroService) |
| `/v1/health` | GET | Alias for /v1/health_check |
| `/v1/statistics` | GET | Get service statistics |

## Example Usage

### Health Check

```sh
curl http://localhost:8000/health
```

Example response:
```json
{
  "status": "healthy"
}
```

### List Available Models

```sh
curl http://localhost:8000/models
```

Example response:
```json
{
  "models": [
    {
      "name": "llama3.2:1b",
      "modified_at": "2023-07-15T12:30:45Z",
      "size": 1073741824,
      "digest": "sha256:abc123..."
    }
  ]
}
```

### Basic Chat Request

```sh
curl -X POST http://localhost:8000/v1/example-service \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello, how are you?"
      }
    ],
    "model": "llama3.2:1b",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### Chat with History

```sh
curl -X POST http://localhost:8000/v1/example-service \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello, who are you?"
      },
      {
        "role": "assistant",
        "content": "I am an AI assistant powered by an LLM. How can I help you today?"
      },
      {
        "role": "user",
        "content": "Can you explain what a microservice is?"
      }
    ],
    "model": "llama3.2:1b",
    "max_tokens": 500,
    "temperature": 0.7
  }'
```

### Streaming Response

Enable streaming to receive the response incrementally:

```sh
curl -X POST http://localhost:8000/v1/example-service \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Write a short poem about artificial intelligence"
      }
    ],
    "model": "llama3.2:1b",
    "stream": true,
    "max_tokens": 200,
    "temperature": 0.8
  }'
```

### Saving Response to File

```sh
curl -X POST http://localhost:8000/v1/example-service \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What is machine learning?"
      }
    ],
    "model": "llama3.2:1b",
    "max_tokens": 200,
    "temperature": 0.5
  }' | jq '.' > output/$(date +%s)-response.json
```

## OPEA Architecture Details

### MicroService vs MegaService

This implementation uses two types of MicroService instances:

1. **LLM MicroService**: Acts as an API Gateway to the Ollama LLM service
   ```python
   llm = MicroService(
       name="llm",
       host=LLM_SERVICE_HOST_IP,
       port=LLM_SERVICE_PORT,
       endpoint="/v1/chat/completions",
       use_remote_service=True,
       service_type=ServiceType.LLM,
       service_role=ServiceRoleType.MICROSERVICE,
   )
   ```

2. **MegaService**: Exposes the external API endpoint for users
   ```python
   self.service = MicroService(
       name=self.__class__.__name__,
       service_role=ServiceRoleType.MEGASERVICE,
       host=self.host,
       port=self.port,
       endpoint=self.endpoint,
       input_datatype=ChatCompletionRequest,
       output_datatype=ChatCompletionResponse,
   )
   ```

### ServiceOrchestrator

The ServiceOrchestrator orchestrates the flow between services using a DAG:

```python
# Create the orchestrator
self.orchestrator = ServiceOrchestrator()

# Add services to the orchestrator
self.orchestrator.add(llm)

# In more complex scenarios with multiple services, you'd define the flow:
# self.orchestrator.flow_to(service1, service2)
# self.orchestrator.flow_to(service2, service3)
```

### Example: Complex RAG Pipeline

The service can be extended to implement a full Retrieval-Augmented Generation (RAG) pipeline:

```python
# Create services
embedding = MicroService(
    name="embedding",
    host=EMBEDDING_HOST_IP,
    port=EMBEDDING_PORT,
    endpoint="/v1/embeddings",
    use_remote_service=True,
    service_type=ServiceType.EMBEDDING,
)

retriever = MicroService(
    name="retriever",
    host=RETRIEVER_HOST_IP,
    port=RETRIEVER_PORT,
    endpoint="/v1/retrieve",
    use_remote_service=True,
    service_type=ServiceType.RETRIEVER,
)

reranker = MicroService(
    name="reranker",
    host=RERANKER_HOST_IP,
    port=RERANKER_PORT,
    endpoint="/v1/rerank",
    use_remote_service=True,
    service_type=ServiceType.RERANK,
)

llm = MicroService(
    name="llm",
    host=LLM_HOST_IP,
    port=LLM_PORT,
    endpoint="/v1/chat/completions",
    use_remote_service=True,
    service_type=ServiceType.LLM,
)

# Add all services to the orchestrator
self.orchestrator.add(embedding).add(retriever).add(reranker).add(llm)

# Define the flow between services
self.orchestrator.flow_to(embedding, retriever)
self.orchestrator.flow_to(retriever, reranker)
self.orchestrator.flow_to(reranker, llm)
```

### OpenTelemetry Tracing

The service uses OpenTelemetry to provide distributed tracing through Jaeger:

```python
# Set up tracing
def setup_tracing():
    resource = Resource(attributes={
        SERVICE_NAME: SERVICE_NAME_VALUE
    })
    
    tracer_provider = TracerProvider(resource=resource)
    
    jaeger_exporter = JaegerExporter(
        agent_host_name=JAEGER_HOST,
        agent_port=JAEGER_PORT,
    )
    
    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    trace.set_tracer_provider(tracer_provider)
    
    # Instrument HTTP clients and FastAPI
    AioHttpClientInstrumentor().instrument()
    FastAPIInstrumentor.instrument_app(self.service.app)
```

Every operation is traced with appropriate spans:

```python
with self.tracer.start_as_current_span("operation_name"):
    # Operation code
```

This provides end-to-end visibility of each request through the system.

### Data Flow

1. Request comes into the LLMService
2. Request is validated and transformed
3. Connection to services is verified (with retry logic)
4. ServiceOrchestrator processes the request through the DAG
5. Response is transformed and returned to the user
6. All steps are traced with OpenTelemetry

## Debugging

### Jaeger UI

Access the Jaeger UI for tracing at:

```
http://localhost:16686/
```

You can search for traces by:
- Service name: "llm-mega-service"
- Operation: "handle_request", "orchestrator_schedule", etc.
- Tags: "llm.model", "llm.temperature", etc.

### Testing Ollama Directly

You can test Ollama directly with:

```sh
curl -X POST http://localhost:9000/api/chat \
  -d '{
    "model": "llama3.2:1b",
    "messages": [
      {
        "role": "user", 
        "content": "Hello, how are you?"
      }
    ]
  }'
```

## Error Handling

The service includes robust error handling:

1. Connection errors - The service retries connections to dependent services
2. Request validation errors - Bad requests return 400 status codes
3. Service errors - Internal errors return 500 status codes
4. Timeouts - Configurable through environment variables
5. Error traces - All errors are captured in Jaeger traces with full context

## Troubleshooting

### Common Issues and Solutions

#### Connection Issues

**Problem**: Service fails to start with "Failed to connect to LLM service" error.

**Solutions**:
- Verify that Ollama is running: `docker ps | grep ollama`
- Check Ollama logs: `docker logs ollama-server`
- Verify the LLM_SERVICE_HOST_IP and LLM_SERVICE_PORT environment variables
- Increase CONNECTION_RETRY_COUNT and CONNECTION_RETRY_DELAY
- Ensure network connectivity between services

#### Model Not Found

**Problem**: Requests fail with "Model not found" error.

**Solutions**:
- Verify the model is pulled: `curl http://localhost:9000/api/tags`
- Pull the model if missing: 
  ```sh
  curl http://localhost:9000/api/pull -d '{
    "model": "llama3.2:1b"
  }'
  ```
- Check model name spelling in your requests
- Check Ollama logs for model loading issues

#### Request Timeouts

**Problem**: Requests timeout before completion.

**Solutions**:
- Reduce the `max_tokens` parameter in your request
- Set a higher timeout value in your client
- Check system resources (CPU, memory)
- Consider using streaming responses for long generations

#### Jaeger Not Showing Traces

**Problem**: No traces appear in Jaeger UI.

**Solutions**:
- Verify Jaeger is running: `docker ps | grep jaeger`
- Check Jaeger logs: `docker logs jaeger`
- Verify JAEGER_HOST and JAEGER_PORT environment variables
- Ensure the service has network connectivity to Jaeger
- Check for errors in the application logs

#### Performance Issues

**Problem**: Service is slow to respond.

**Solutions**:
- Use a smaller LLM model
- Reduce the `max_tokens` parameter
- Increase system resources (CPU, memory)
- Check Jaeger traces for bottlenecks
- Consider scaling horizontally with multiple instances

### Diagnostic Commands

Here are useful commands for diagnosing issues:

```sh
# Check service logs
docker logs mega-service

# Check Ollama logs
docker logs ollama-server

# Check Jaeger logs
docker logs jaeger

# Verify Ollama is healthy
curl http://localhost:9000/api/tags

# Check service health
curl http://localhost:8000/health

# List available models
curl http://localhost:8000/models
```

### Getting Help

If you encounter issues not covered here:

1. Check the application logs for detailed error messages
2. Look at the Jaeger traces for the failing request
3. File an issue on the GitHub repository with:
   - Error message and stack trace
   - Steps to reproduce
   - Environment details (OS, Docker version, etc.)
   - Relevant logs and traces
