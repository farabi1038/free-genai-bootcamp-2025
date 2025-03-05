#!/bin/bash

# Language Learning Portal - Dependency Installation Script
# This script helps install all necessary dependencies for the project

echo "================================================="
echo "Language Learning Portal - Dependency Installer"
echo "================================================="

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="MacOS"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="Windows"
else
    OS="Unknown"
fi

echo "Detected OS: $OS"
echo ""

# Check for Go
echo "Checking for Go..."
if command -v go &> /dev/null; then
    GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
    echo "✅ Go is installed (version $GO_VERSION)"
    
    # Check if Go version is sufficient
    if [[ "$(printf '%s\n' "1.16" "$GO_VERSION" | sort -V | head -n1)" != "1.16" ]]; then
        echo "⚠️ Go version is below 1.16. Please update Go to version 1.16 or higher."
    fi
else
    echo "❌ Go is not installed"
    echo "Please install Go 1.16 or higher:"
    
    if [[ "$OS" == "Linux" ]]; then
        echo "  For Ubuntu/Debian: sudo apt-get install golang-go"
        echo "  For other distributions, see: https://golang.org/doc/install"
    elif [[ "$OS" == "MacOS" ]]; then
        echo "  Using Homebrew: brew install go"
        echo "  Or download from: https://golang.org/doc/install"
    elif [[ "$OS" == "Windows" ]]; then
        echo "  Download from: https://golang.org/doc/install"
        echo "  Or using Chocolatey: choco install golang"
    fi
fi

# Check for Node.js
echo -e "\nChecking for Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v | sed 's/v//')
    echo "✅ Node.js is installed (version $NODE_VERSION)"
    
    # Check if Node version is sufficient
    if [[ "$(printf '%s\n' "16.0.0" "$NODE_VERSION" | sort -V | head -n1)" != "16.0.0" ]]; then
        echo "⚠️ Node.js version is below 16. Please update Node.js to version 16 or higher."
    fi
else
    echo "❌ Node.js is not installed"
    echo "Please install Node.js 16 or higher:"
    
    if [[ "$OS" == "Linux" ]]; then
        echo "  For Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash - && sudo apt-get install -y nodejs"
        echo "  For other distributions, see: https://nodejs.org/en/download/"
    elif [[ "$OS" == "MacOS" ]]; then
        echo "  Using Homebrew: brew install node"
        echo "  Or download from: https://nodejs.org/en/download/"
    elif [[ "$OS" == "Windows" ]]; then
        echo "  Download from: https://nodejs.org/en/download/"
        echo "  Or using Chocolatey: choco install nodejs"
    fi
fi

# Check for npm
echo -e "\nChecking for npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    echo "✅ npm is installed (version $NPM_VERSION)"
else
    echo "❌ npm is not installed (should be included with Node.js)"
    echo "Please reinstall Node.js to get npm"
fi

# Check for PostgreSQL (optional)
echo -e "\nChecking for PostgreSQL (optional)..."
if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version | awk '{print $3}')
    echo "✅ PostgreSQL is installed (version $PSQL_VERSION)"
else
    echo "⚠️ PostgreSQL is not installed (optional, SQLite is used by default)"
    echo "If you want to use PostgreSQL:"
    
    if [[ "$OS" == "Linux" ]]; then
        echo "  For Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
        echo "  For other distributions, see: https://www.postgresql.org/download/"
    elif [[ "$OS" == "MacOS" ]]; then
        echo "  Using Homebrew: brew install postgresql"
        echo "  Or download from: https://www.postgresql.org/download/macosx/"
    elif [[ "$OS" == "Windows" ]]; then
        echo "  Download from: https://www.postgresql.org/download/windows/"
        echo "  Or using Chocolatey: choco install postgresql"
    fi
fi

# Check for Git
echo -e "\nChecking for Git..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    echo "✅ Git is installed (version $GIT_VERSION)"
else
    echo "❌ Git is not installed"
    echo "Please install Git:"
    
    if [[ "$OS" == "Linux" ]]; then
        echo "  For Ubuntu/Debian: sudo apt-get install git"
        echo "  For other distributions, see: https://git-scm.com/download/linux"
    elif [[ "$OS" == "MacOS" ]]; then
        echo "  Using Homebrew: brew install git"
        echo "  Or download from: https://git-scm.com/download/mac"
    elif [[ "$OS" == "Windows" ]]; then
        echo "  Download from: https://git-scm.com/download/win"
        echo "  Or using Chocolatey: choco install git"
    fi
fi

# Install frontend dependencies
echo -e "\nWould you like to install frontend dependencies now? (y/n)"
read -r INSTALL_FRONTEND

if [[ "$INSTALL_FRONTEND" == "y" || "$INSTALL_FRONTEND" == "Y" ]]; then
    echo "Installing frontend dependencies..."
    pushd frontend > /dev/null
    npm install
    FRONTEND_RESULT=$?
    popd > /dev/null
    
    if [ $FRONTEND_RESULT -eq 0 ]; then
        echo "✅ Frontend dependencies installed successfully"
    else
        echo "❌ Failed to install frontend dependencies"
    fi
fi

# Install backend dependencies
echo -e "\nWould you like to install backend dependencies now? (y/n)"
read -r INSTALL_BACKEND

if [[ "$INSTALL_BACKEND" == "y" || "$INSTALL_BACKEND" == "Y" ]]; then
    echo "Installing backend dependencies..."
    pushd backend > /dev/null
    go mod download
    BACKEND_RESULT=$?
    popd > /dev/null
    
    if [ $BACKEND_RESULT -eq 0 ]; then
        echo "✅ Backend dependencies installed successfully"
    else
        echo "❌ Failed to install backend dependencies"
    fi
fi

echo -e "\n================================================="
echo "Dependency check complete!"
echo "================================================="
echo "For detailed setup instructions, see SETUP.md"
echo "To start the application, run: ./test-integration.sh"
echo "=================================================" 