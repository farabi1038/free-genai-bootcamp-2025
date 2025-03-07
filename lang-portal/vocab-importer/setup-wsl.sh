#!/bin/bash
set -e

echo "=========================================="
echo "WSL Setup Script for Vocabulary Generator"
echo "=========================================="

# Fix potential DNS issues in WSL
echo "Fixing WSL DNS configuration..."
cat > /tmp/fix_dns.sh << 'EOF'
#!/bin/bash

# Get the nameserver from /etc/resolv.conf
NAMESERVER=$(grep nameserver /etc/resolv.conf | awk '{print $2}' | head -1)

# If no nameserver is found or it's the WSL default, use Google DNS
if [ -z "$NAMESERVER" ] || [ "$NAMESERVER" = "172.26.240.1" ] || [ "$NAMESERVER" = "172.24.224.1" ]; then
    echo "Setting up Google DNS..."
    echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf > /dev/null
    echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf > /dev/null
    echo "DNS configured to use Google DNS servers"
else
    echo "Existing DNS server found: $NAMESERVER"
fi

# Test connectivity
echo "Testing internet connectivity..."
if ping -c 1 google.com > /dev/null 2>&1; then
    echo "✅ Internet connectivity successful!"
else
    echo "❌ Internet connectivity failed. Please check your network."
    exit 1
fi
EOF

# Run the DNS fix script with sudo
sudo bash /tmp/fix_dns.sh
rm /tmp/fix_dns.sh

echo "Setting up pip configuration to use alternative package index..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
timeout = 60
index-url = https://pypi.org/simple
trusted-host = pypi.org
               files.pythonhosted.org
EOF

echo "Installing requirements..."
pip install --no-cache-dir -r requirements.txt || {
    echo "Regular pip install failed, trying with --prefer-binary option..."
    pip install --no-cache-dir --prefer-binary -r requirements.txt
}

# Create output directory
mkdir -p output

echo "Checking Ollama connection..."
if curl -s --connect-timeout 5 http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running and accessible!"
else 
    echo "❌ Ollama is not accessible. Checking alternative options..."
    
    # Check if Ollama is running on the Windows host
    WINDOWS_HOST=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}' | head -1)
    if [ -n "$WINDOWS_HOST" ] && curl -s --connect-timeout 5 http://${WINDOWS_HOST}:11434/api/tags > /dev/null; then
        echo "✅ Ollama found on Windows host at ${WINDOWS_HOST}:11434"
        # Update the .env file to use the Windows host
        sed -i "s/LLM_SERVICE_HOST=localhost/LLM_SERVICE_HOST=${WINDOWS_HOST}/" .env
        echo "Updated .env file to use Ollama on Windows host"
    else
        echo "⚠️ Ollama not found. Please ensure Ollama is running before starting the application."
    fi
fi

echo "Setup complete! You can now run the application with:"
echo "streamlit run app.py" 