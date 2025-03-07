#!/bin/bash
# Script to run the Vocabulary Importer using Docker

# Text formatting
BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Set default model if not specified
export LLM_MODEL_ID=${LLM_MODEL_ID:-llama2:13b}
echo -e "${BOLD}Using LLM model:${NC} $LLM_MODEL_ID"

# Create output directory if it doesn't exist
mkdir -p output

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed${NC}"
    echo -e "${YELLOW}Please install Docker before continuing:${NC}"
    echo -e "  ${BLUE}Windows:${NC} https://docs.docker.com/desktop/install/windows-install/"
    echo -e "  ${BLUE}macOS:${NC} https://docs.docker.com/desktop/install/mac-install/"
    echo -e "  ${BLUE}Linux:${NC} https://docs.docker.com/engine/install/"
    echo ""
    echo -e "${YELLOW}Would you like to run without Docker instead? (y/n)${NC}"
    read -r use_non_docker
    if [[ "$use_non_docker" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Starting in non-Docker mode...${NC}"
        echo "Checking Python environment..."
        
        # Check if the required packages are installed
        if ! pip show streamlit &> /dev/null || ! pip show pandas &> /dev/null; then
            echo "Installing required packages..."
            pip install -r requirements.txt
        fi
        
        echo -e "${GREEN}Starting Streamlit application...${NC}"
        streamlit run app.py --server.address=0.0.0.0
        exit 0
    else
        echo "Exiting. Please install Docker and try again."
        exit 1
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    echo -e "${YELLOW}Please start Docker and try again:${NC}"
    echo -e "  ${BLUE}Windows/macOS:${NC} Start Docker Desktop application"
    echo -e "  ${BLUE}Linux:${NC} Run 'sudo systemctl start docker'"
    
    echo ""
    echo -e "${YELLOW}Would you like to run without Docker instead? (y/n)${NC}"
    read -r use_non_docker
    if [[ "$use_non_docker" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Starting in non-Docker mode...${NC}"
        echo "Checking Python environment..."
        
        # Check if the required packages are installed
        if ! pip show streamlit &> /dev/null || ! pip show pandas &> /dev/null; then
            echo "Installing required packages..."
            pip install -r requirements.txt
        fi
        
        echo -e "${GREEN}Starting Streamlit application...${NC}"
        streamlit run app.py --server.address=0.0.0.0
        exit 0
    else
        echo "Exiting. Please start Docker and try again."
        exit 1
    fi
fi

# Check Docker Compose version and use appropriate command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo -e "${GREEN}Using Docker Compose V2${NC}"
elif docker-compose --version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo -e "${GREEN}Using Docker Compose V1${NC}"
else
    echo -e "${RED}❌ Error: Docker Compose not found${NC}"
    echo -e "${YELLOW}Please install Docker Compose.${NC}"
    exit 1
fi

# Clean up any existing containers to avoid conflicts
echo -e "${BLUE}Cleaning up any existing containers...${NC}"
$COMPOSE_CMD down --remove-orphans

# Start the Docker Compose stack
echo -e "${BLUE}Starting Vocabulary Importer stack with Docker Compose...${NC}"
$COMPOSE_CMD up -d

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to be ready...${NC}"
MAX_WAIT=60  # Maximum wait time in seconds
WAIT_INTERVAL=5  # Check every 5 seconds
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${GREEN}✅ Ollama service is ready!${NC}"
        break
    fi
    echo "Waiting for Ollama to be ready... ($ELAPSED/$MAX_WAIT seconds)"
    sleep $WAIT_INTERVAL
    ELAPSED=$((ELAPSED + WAIT_INTERVAL))
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo -e "${YELLOW}⚠️ Ollama service is taking longer than expected to start${NC}"
    echo "The application may still be initializing. Check logs for details."
fi

# Provide user information
echo ""
echo -e "${GREEN}🚀 Vocabulary Importer is running!${NC}"
echo -e "${BLUE}📊 Access the application at:${NC} http://localhost:8501"
echo ""
echo -e "${BLUE}📝 To view logs:${NC}"
echo "  $COMPOSE_CMD logs -f"
echo ""
echo -e "${BLUE}🛑 To stop the application:${NC}"
echo "  $COMPOSE_CMD down"
echo ""
echo -e "${YELLOW}If the application doesn't work correctly, check the troubleshooting guide in the README.${NC}" 