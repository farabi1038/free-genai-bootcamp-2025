# GenAI Language Learning Tools

![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-prototype-orange)
![Framework](https://img.shields.io/badge/frameworks-React%20%7C%20Go%20%7C%20Python-brightgreen)

A comprehensive collection of generative AI powered tools for language learning, prototyping, and research. This repository contains various components for creating, managing, and deploying language learning applications with a focus on AI-enhanced capabilities.

## 🌟 Repository Overview

This repository is a monorepo containing several interconnected projects that demonstrate different aspects of using generative AI in language learning applications:

| Project | Description | Technologies |
|---------|-------------|--------------|
| [Language Portal](#language-portal) | Core language learning application with vocabulary management, study activities, and progress tracking | React, TypeScript, Go, SQLite |
| [Vocabulary Importer](#vocabulary-importer) | Internal tool for generating vocabulary datasets using LLMs | Python, Streamlit, Ollama, OPEA |
| [Sentence Constructor](#sentence-constructor) | Tool for generating and analyzing grammatical structures | Python, NLP libraries |
| [GenAI Architecting](#genai-architecting) | Reference architectures and patterns for GenAI applications | Documentation, diagrams |
| [OPEA Components](#opea-components) | Reference implementation of Open and Pluggable Enterprise AI patterns | Python, Docker |

## 🔍 Projects in Detail

### Language Portal

The core application for language learning, featuring vocabulary management, study activities, progress tracking, and personalized learning experiences.

**Technical Architecture:**

The Language Portal follows a modern, full-stack architecture:

- **Frontend**: A React 18 single-page application built with TypeScript, providing interactive UI components for language learning activities. Uses styled-components for styling, React Router v6 for navigation, Vite for fast builds with HMR, and Context API for state management. The architecture emphasizes component reusability and strong typing for enhanced developer experience.

- **Backend**: A Go-based RESTful API server with a clean, modular architecture. Organized into cmd (entry points), internal (business logic), and db (data access) packages following Go best practices. Uses Chi Router for HTTP routing, SQLite for data persistence with prepared statements to prevent SQL injection, and implements CORS middleware for secure cross-origin requests.

- **Database**: SQLite database with a structured schema for vocabulary items, word groups, study activities, and user progress tracking. Migrations are handled via SQL scripts in the db/migrations directory.

**Key Features:**
- Full-stack application with React frontend and Go backend
- Interactive vocabulary study tools with flashcards, quizzes, and matching games
- Progress tracking and analytics dashboard with visualization
- RESTful API for CRUD operations on language learning data
- Mobile-responsive design

**Directory:** [/lang-portal](/lang-portal)  
**Documentation:** [Language Portal README](/lang-portal/README.md)

### Vocabulary Importer

An internal tool that uses Large Language Models to generate vocabulary datasets for the Language Portal. Built with OPEA (Open and Pluggable Enterprise AI) architecture.

**Technical Architecture:**

The Vocabulary Importer implements the OPEA architecture for a robust and maintainable AI integration:

- **Frontend**: Streamlit-based web interface providing an intuitive way to generate, view, and manage vocabulary datasets. The UI includes forms for generating vocabulary, tables for displaying results, and export/import functionality.

- **OPEA Components**: Implements service orchestration patterns with modular services, standardized communication protocols, and pluggable components. Services are defined as microservices with well-defined interfaces, allowing for future expansion.

- **LLM Integration**: Connects to Ollama for local LLM inference, with support for multiple models and fallback mechanisms to ensure reliability. The architecture handles both synchronous and asynchronous requests, with comprehensive error handling and timeout management.

- **Deployment Options**: Supports both direct installation and Docker-based deployment, with Docker Compose for orchestrating containerized services following the OPEA pattern.

**Key Features:**
- Generate vocabulary words with proper translations and pronunciations
- Create categorized word groups
- Export data to JSON format for import into the main application
- Special handling for Japanese language with romaji support
- Docker-based deployment option following OPEA patterns
- Fallback mechanisms for robust operation even when LLM services are unavailable

**Directory:** [/lang-portal/vocab-importer](/lang-portal/vocab-importer)  
**Documentation:** [Vocabulary Importer README](/lang-portal/vocab-importer/README.md)

### Sentence Constructor

A tool for analyzing and comparing different AI models' approaches to language transcription and learning, with a focus on sentence construction across multiple languages.

**Technical Approach:**

The Sentence Constructor project takes an analytical approach to evaluating AI models for language learning:

- **Model Evaluation**: Conducts in-depth evaluations of leading AI models (Claude, ChatGPT, Perplexity AI, Meta-AI) for language transcription tasks, comparing their effectiveness for student assistance.

- **Learning Methodology**: Analyzes each model's ability to present vocabulary tables, provide clear sentence structure templates, and offer progressive clues that guide without revealing answers.

- **Language Support**: Focuses on English-to-Japanese and English-to-Spanish transcription, with considerations for different proficiency levels (JLPT N5 for Japanese, CEFR C1 for Spanish).

- **Educational Framework**: Implements a state-based teaching methodology that progresses from initial setup through student attempts to subsequent clues and corrections.

**Key Findings:**
- Different AI models show varying strengths in vocabulary presentation, structure guidance, and feedback quality
- Models exhibit unique approaches to balancing challenge and support for language learners
- Specific recommendations for which models work best for different language learning scenarios

**Directory:** [/sentence-constructor](/sentence-constructor)  
**Documentation:** [Sentence Constructor README](/sentence-constructor/README.md)

### GenAI Architecting

Reference architectures, patterns, and best practices for building Generative AI applications, with a focus on language learning use cases and practical infrastructure considerations.

**Architecture Focus:**

The GenAI Architecting component provides concrete guidance for implementating GenAI in production:

- **Infrastructure Planning**: Outlines approaches for building cost-effective AI infrastructure, including specifications for dedicated AI workstations within defined budgets ($10,000-$15,000 range).

- **Deployment Strategies**: Provides patterns for self-hosted AI services to maintain control over user data privacy while mitigating the costs of managed AI services.

- **Data Management**: Addresses practical concerns like copyright compliance with strategies for legal acquisition and secure storage of learning materials.

- **Model Selection**: Evaluates different open-source LLMs for specific use cases, with considerations for transparency, licensing, and performance on consumer hardware.

**Key Recommendations:**
- Focus on open-source models like IBM Granite that offer transparency in training data
- Design for specific capacity needs (e.g., 300 active students within a single location)
- Implement proper data management to avoid copyright issues
- Optimize model deployment for consumer-grade hardware

**Directory:** [/genai-architecting](/genai-architecting)  
**Documentation:** [GenAI Architecting README](/genai-architecting/README.md)

### OPEA Components

Reference implementation of the Open and Pluggable Enterprise AI (OPEA) architectural pattern, demonstrating how to build modular, maintainable AI systems.

**Architecture Components:**

The OPEA implementation provides a complete framework for enterprise AI integration:

- **Service Orchestration**: Core `ServiceOrchestrator` class that manages the flow of requests between microservices in a directed acyclic graph (DAG), allowing for complex multi-step AI processing pipelines.

- **Standardized Protocols**: Defines protocol classes for standardized communication between services, including request/response formats optimized for LLMs and other AI services.

- **Microservices Framework**: Provides a base `MicroService` class that can be extended for specific service types (LLM, embedding, retrieval, etc.), with built-in health checks, retry logic, and error handling.

- **Docker Integration**: Includes complete Docker and Docker Compose configurations for containerized deployment, with service discovery, networking, and volume management.

- **Observability**: Implements tracing and monitoring for all requests through the processing pipeline, with detailed logs and health metrics.

**Key Applications:**
- LLM API Gateway for interacting with language models through Ollama
- Extensible foundation for RAG (Retrieval-Augmented Generation) workflows
- Enterprise-ready implementation with support for containerization and production deployment
- Reference architecture for building complex AI orchestration systems

**Directory:** [/opea-comps](/opea-comps) and [/lang-portal/opea-comps](/lang-portal/opea-comps)  
**Documentation:** [OPEA Components README](/opea-comps/README.md)

## 🚀 Getting Started

### Prerequisites

- **Frontend:** Node.js 16+, npm or yarn
- **Backend:** Go 1.18+
- **AI Components:** Python 3.8+, Docker (recommended)
- **Databases:** SQLite (included)

### Docker Installation

Many components in this repository use Docker for containerization. If you don't have Docker installed, follow these steps:

#### Windows
1. **Download Docker Desktop for Windows**:
   - Visit [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - Click on "Download for Windows"

2. **Install Docker Desktop**:
   - Run the downloaded installer (Docker Desktop Installer.exe)
   - Follow the installation wizard instructions
   - If using WSL, ensure "Use WSL 2 instead of Hyper-V" is selected
   - Click "Ok" to install

3. **Start Docker Desktop**:
   - After installation, launch Docker Desktop from the Start menu
   - Wait for Docker to start (look for the whale icon in your system tray)
   - Docker must be running before executing any Docker commands

#### macOS
1. **Download Docker Desktop for Mac**:
   - Visit [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
   - Click on "Download for Mac"

2. **Install Docker Desktop**:
   - Open the downloaded .dmg file
   - Drag the Docker icon to your Applications folder
   - Open Docker from your Applications folder

#### Linux (Ubuntu/Debian)
1. **Install Docker Engine**:
   ```bash
   # Update package index
   sudo apt-get update

   # Install dependencies
   sudo apt-get install apt-transport-https ca-certificates curl software-properties-common

   # Add Docker's official GPG key
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

   # Add Docker repository
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

   # Install Docker
   sudo apt-get update
   sudo apt-get install docker-ce docker-ce-cli containerd.io

   # Install Docker Compose
   sudo apt-get install docker-compose
   ```

2. **Add Your User to Docker Group** (to run Docker without sudo):
   ```bash
   sudo usermod -aG docker $USER
   ```
   (You'll need to log out and back in for this to take effect)

3. **Start Docker Service**:
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

### Verifying Docker Installation

To verify Docker is installed and running correctly:

```bash
# Check Docker version
docker --version

# Verify Docker is running
docker info

# Run a test container
docker run hello-world
```

If you see `Error: Cannot connect to the Docker daemon`, make sure Docker is running:

- **Windows/macOS**: Launch Docker Desktop application
- **Linux**: Run `sudo systemctl start docker`

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/farabi1038/free-genai-bootcamp-2025.git
   cd free-genai-bootcamp-2025
   ```

2. Run the installation script:
   ```bash
   # Linux/macOS
   ./install-dependencies.sh
   
   # Windows
   .\install-dependencies.ps1
   ```

3. For detailed setup instructions for each component, refer to their individual READMEs.

## 📋 Project Structure

```
free-genai-bootcamp-2025/
├── lang-portal/                 # Core language learning application
│   ├── frontend/                # React frontend
│   ├── backend/                 # Go backend
│   ├── vocab-importer/          # Vocabulary generation tool
│   └── opea-comps/              # OPEA component instances
├── sentence-constructor/        # Sentence analysis tool
├── genai-architecting/          # Architecture documentation
├── opea-comps/                  # OPEA reference implementation
└── docs/                        # Additional documentation
```

## 🔧 Technologies Used

This repository uses a variety of technologies to demonstrate different approaches to building AI-powered language learning applications:

- **Frontend:** 
  - React 18 with TypeScript for type safety
  - Styled Components for CSS-in-JS styling
  - React Router v6 for navigation
  - Context API for state management
  - Vite for fast builds with HMR
  - Material UI components for consistent UI elements

- **Backend:** 
  - Go (1.18+) for high-performance API services
  - Chi Router for HTTP routing with middleware support
  - SQLite for lightweight, embedded database
  - Mage for build automation and task running
  - RESTful API design with proper status codes and error handling

- **AI Components:** 
  - Python 3.8+ for AI services and tools
  - Streamlit for rapid prototyping of data apps
  - OPEA architecture for modular, maintainable AI systems
  - AsyncIO for non-blocking service communication
  - Robust error handling and fallback mechanisms

- **LLM Integration:** 
  - Ollama for self-hosted, local LLM inference
  - Support for multiple models (llama, mixtral, gemma, phi)
  - Containerized deployment with Docker and Docker Compose
  - Service orchestration for complex AI workflows

- **Development Tools:** 
  - Git for version control
  - Docker for containerization
  - Environment-based configuration management
  - Comprehensive logging and diagnostics

## 🔎 Troubleshooting

### Docker Issues

#### "Docker is not running or not installed"

If you encounter this error when running scripts:

1. **Verify Docker is installed**:
   ```bash
   docker --version
   ```

2. **Check if Docker daemon is running**:
   - Windows/macOS: Make sure Docker Desktop is running (look for the whale icon in system tray/menu bar)
   - Linux: Check service status with `sudo systemctl status docker`

3. **Start Docker if needed**:
   - Windows/macOS: Open Docker Desktop application
   - Linux: `sudo systemctl start docker`

4. **Verify connectivity**:
   ```bash
   docker info
   ```

#### Docker Compose Command Not Found

If you see "docker-compose command not found":

1. **For Docker Desktop users**: Make sure Docker Desktop is up to date
2. **For Linux users**: Install Docker Compose separately:
   ```bash
   sudo apt-get install docker-compose
   ```

#### Permission Denied Errors

If you see "permission denied" when running Docker commands:

1. **Add your user to the docker group** (Linux):
   ```bash
   sudo usermod -aG docker $USER
   ```
   Then log out and back in for changes to take effect.

2. **Run with sudo** (temporary solution for Linux):
   ```bash
   sudo docker info
   ```

### WSL-Specific Issues

If running in Windows Subsystem for Linux (WSL):

1. **Docker Desktop integration**: Ensure Docker Desktop has WSL integration enabled
   - Open Docker Desktop settings
   - Go to "Resources" > "WSL Integration"
   - Enable integration for your distro

2. **WSL networking issues**: If services in WSL can't be accessed from Windows:
   - Run services with explicit address binding: `--server.address=0.0.0.0`
   - Access using the WSL IP address instead of localhost

### Non-Docker Alternatives

If you continue to have Docker issues, some components can be run without Docker:

1. **Vocabulary Importer**:
   ```bash
   cd lang-portal/vocab-importer
   pip install -r requirements.txt
   streamlit run app.py
   ```

2. **Language Portal Backend**:
   ```bash
   cd lang-portal/backend
   go run ./cmd/server/main.go
   ```

Refer to each component's README for detailed non-Docker setup instructions.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please check out our [Contributing Guidelines](CONTRIBUTING.md) for details on how to get involved.

## 📬 Contact

For questions or feedback, please open an issue in this repository. 
