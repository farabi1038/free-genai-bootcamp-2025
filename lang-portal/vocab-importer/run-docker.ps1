# PowerShell script to run the Vocabulary Importer using Docker

# Text formatting for PowerShell
function Write-ColorOutput($ForegroundColor) {
    # Store old colors
    $originalForeground = $host.UI.RawUI.ForegroundColor
    
    # Set colors
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    
    # Process pipeline
    try {
        $input | ForEach-Object { Write-Output $_ }
    }
    finally {
        # Restore colors
        $host.UI.RawUI.ForegroundColor = $originalForeground
    }
}

# Set default model if not specified
if (-not $env:LLM_MODEL_ID) {
    $env:LLM_MODEL_ID = "llama2:13b"
}
Write-Host "Using LLM model: $env:LLM_MODEL_ID" -ForegroundColor Cyan

# Create output directory if it doesn't exist
if (-not (Test-Path -Path "output")) {
    New-Item -Path "output" -ItemType Directory | Out-Null
    Write-Host "Created output directory" -ForegroundColor Green
}

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Host "Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker is not installed" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    
    $useNonDocker = Read-Host "Would you like to run without Docker instead? (y/n)"
    if ($useNonDocker -eq "y") {
        Write-Host "Starting in non-Docker mode..." -ForegroundColor Green
        
        # Check if required packages are installed
        $streamlitInstalled = $false
        try {
            $streamlitInstalled = (pip show streamlit) -ne $null
        } catch {
            $streamlitInstalled = $false
        }
        
        if (-not $streamlitInstalled) {
            Write-Host "Installing required packages..." -ForegroundColor Yellow
            pip install -r requirements.txt
        }
        
        Write-Host "Starting Streamlit application..." -ForegroundColor Green
        streamlit run app.py --server.address=0.0.0.0
        exit
    } else {
        Write-Host "Exiting. Please install Docker and try again." -ForegroundColor Red
        exit 1
    }
}

# Check if Docker is running
try {
    docker info | Out-Null
    if (-not $?) {
        throw "Docker check failed"
    }
    Write-Host "Docker service is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again" -ForegroundColor Yellow
    
    $useNonDocker = Read-Host "Would you like to run without Docker instead? (y/n)"
    if ($useNonDocker -eq "y") {
        Write-Host "Starting in non-Docker mode..." -ForegroundColor Green
        
        # Check if required packages are installed
        $streamlitInstalled = $false
        try {
            $streamlitInstalled = (pip show streamlit) -ne $null
        } catch {
            $streamlitInstalled = $false
        }
        
        if (-not $streamlitInstalled) {
            Write-Host "Installing required packages..." -ForegroundColor Yellow
            pip install -r requirements.txt
        }
        
        Write-Host "Starting Streamlit application..." -ForegroundColor Green
        streamlit run app.py --server.address=0.0.0.0
        exit
    } else {
        Write-Host "Exiting. Please start Docker and try again." -ForegroundColor Red
        exit 1
    }
}

# Check if Docker Compose is available
try {
    # Try the modern "docker compose" command first (Docker Desktop)
    docker compose version | Out-Null
    $composeCmd = "docker compose"
    Write-Host "Using modern Docker Compose command" -ForegroundColor Green
} catch {
    try {
        # Try the legacy "docker-compose" command
        docker-compose --version | Out-Null
        $composeCmd = "docker-compose"
        Write-Host "Using legacy docker-compose command" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error: Docker Compose is not available" -ForegroundColor Red
        Write-Host "Make sure Docker Desktop includes Compose, or install it separately" -ForegroundColor Yellow
        
        $useNonDocker = Read-Host "Would you like to run without Docker instead? (y/n)"
        if ($useNonDocker -eq "y") {
            Write-Host "Starting in non-Docker mode..." -ForegroundColor Green
            
            # Check if required packages are installed
            $streamlitInstalled = $false
            try {
                $streamlitInstalled = (pip show streamlit) -ne $null
            } catch {
                $streamlitInstalled = $false
            }
            
            if (-not $streamlitInstalled) {
                Write-Host "Installing required packages..." -ForegroundColor Yellow
                pip install -r requirements.txt
            }
            
            Write-Host "Starting Streamlit application..." -ForegroundColor Green
            streamlit run app.py --server.address=0.0.0.0
            exit
        } else {
            Write-Host "Exiting. Please install Docker Compose and try again." -ForegroundColor Red
            exit 1
        }
    }
}

# Pull model before starting (optional but recommended)
Write-Host "Pre-pulling Ollama model $env:LLM_MODEL_ID..." -ForegroundColor Cyan
try {
    docker run --rm -v ollama-data:/root/.ollama ollama/ollama pull $env:LLM_MODEL_ID
    Write-Host "✅ Model pre-pulled successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Warning: Failed to pre-pull model. Container will attempt to pull on startup." -ForegroundColor Yellow
}

# Start the Docker Compose stack
Write-Host "Starting Vocabulary Importer stack with Docker Compose..." -ForegroundColor Cyan
if ($composeCmd -eq "docker compose") {
    docker compose up -d
} else {
    docker-compose up -d
}

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Cyan
$ready = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Ollama service is ready!" -ForegroundColor Green
            $ready = $true
            break
        }
    } catch {
        Write-Host "Waiting for Ollama to be ready... ($i/10)"
        Start-Sleep -Seconds 3
    }
    
    # If we've waited the maximum time, inform the user but don't exit
    if ($i -eq 10 -and -not $ready) {
        Write-Host "⚠️ Ollama service is taking longer than expected to start" -ForegroundColor Yellow
        Write-Host "The application may still be initializing. Check logs for details."
    }
}

# Provide user information
Write-Host ""
Write-Host "🚀 Vocabulary Importer is running!" -ForegroundColor Green
Write-Host "📊 Access the application at: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 To view logs:" -ForegroundColor Cyan
if ($composeCmd -eq "docker compose") {
    Write-Host "  docker compose logs -f"
} else {
    Write-Host "  docker-compose logs -f"
}
Write-Host ""
Write-Host "🛑 To stop the application:" -ForegroundColor Cyan
if ($composeCmd -eq "docker compose") {
    Write-Host "  docker compose down"
} else {
    Write-Host "  docker-compose down"
}
Write-Host ""
Write-Host "If the application doesn't work correctly, check the troubleshooting guide in the README." -ForegroundColor Yellow

# Open browser automatically if desired
$openBrowser = Read-Host "Open browser now? (y/n)"
if ($openBrowser -eq "y") {
    Start-Process "http://localhost:8501"
} 