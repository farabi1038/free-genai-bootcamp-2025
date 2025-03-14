import streamlit as st
import pandas as pd
import os
import json
import logging
import socket
import requests
import subprocess
import time
import asyncio
import nest_asyncio
from datetime import datetime
from dotenv import load_dotenv
from utils.llm_client import (
    LLMClient, 
    LLMService, 
    ServiceOrchestrator, 
    get_llm_service
)
from utils.vocab_generator import VocabGenerator

# Apply nest_asyncio to allow nested event loops (needed for Streamlit + asyncio)
nest_asyncio.apply()

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create output directory if it doesn't exist
os.makedirs("output", exist_ok=True)

# Detect if running in Docker
IN_DOCKER = os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER', False)
logger.info(f"Running in Docker: {IN_DOCKER}")

# List of fallback models to try in order of preference
FALLBACK_MODELS = [
    "llama3.2:1b",
    "llama3:latest",
    "llama3",
    "llama2",
    "gemma:2b",
    "gemma:7b",
    "mistral",
    "mixtral",
    "phi"
]

# Helper function to get all possible host IPs to try
def get_potential_host_ips():
    """Get all potential host IPs where Ollama might be running."""
    potential_ips = []
    
    # When running in Docker, we should connect to the service name
    if IN_DOCKER:
        # Docker-compose sets up DNS resolution by service name
        ollama_host = os.environ.get("LLM_SERVICE_HOST", "ollama-server")
        logger.info(f"In Docker mode, connecting to service: {ollama_host}")
        return [ollama_host]
    
    # Standard list for non-Docker environments
    potential_ips = ["localhost", "127.0.0.1"]
    
    # Add configured IP first if it exists
    config_ip = os.environ.get("LLM_SERVICE_HOST", "")
    if config_ip and config_ip not in potential_ips:
        potential_ips.insert(0, config_ip)  # Try the configured one first
    
    # Try to get the host.docker.internal which works in some WSL2 setups
    try:
        host_ip = socket.gethostbyname("host.docker.internal")
        potential_ips.append(host_ip)
    except:
        pass
    
    # Try to get the WSL2 gateway IP from /etc/resolv.conf
    try:
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                if 'nameserver' in line and '8.8.8.8' not in line and '8.8.4.4' not in line:
                    ip = line.split()[1]
                    potential_ips.append(ip)
    except:
        pass
    
    # Try common WSL2 gateway IPs
    potential_ips.extend([
        "172.17.0.1",  # Common Docker bridge
        "172.18.0.1", 
        "172.19.0.1", 
        "172.20.0.1",
        "172.21.0.1",
        "172.22.0.1",
        "172.23.0.1",
        "172.24.0.1",
        "172.25.0.1",
        "172.26.0.1",
        "172.27.0.1",
        "172.28.0.1",
        "172.29.0.1",
        "172.30.0.1",
        "172.31.0.1",
        "192.168.0.1",
        "192.168.1.1",
    ])
    
    logger.debug(f"Potential host IPs: {potential_ips}")
    return potential_ips

# Check for available models on a connected Ollama instance
def get_available_models(host, port):
    """Get list of available models from a connected Ollama instance."""
    try:
        response = requests.get(f"http://{host}:{port}/api/tags", timeout=3)
        if response.status_code == 200:
            data = response.json()
            available_models = []
            for model in data.get('models', []):
                available_models.append(model.get('name'))
            logger.info(f"Available models: {available_models}")
            return available_models
        return []
    except Exception as e:
        logger.warning(f"Failed to get available models: {str(e)}")
        return []

# Try to pull a model if it's not available
def pull_model(host, port, model_name):
    """Try to pull a model if not available."""
    try:
        logger.info(f"Attempting to pull model {model_name}...")
        # Try the subprocess method first (if running in same environment as Ollama)
        try:
            result = subprocess.run(
                ["ollama", "pull", model_name], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10  # Just to start the pull, not wait for completion
            )
            logger.info(f"Ollama pull initiated: {result.stdout}")
            return True
        except Exception as e:
            logger.warning(f"Failed to pull using subprocess: {str(e)}")
        
        # If subprocess failed, try using the API
        response = requests.post(
            f"http://{host}:{port}/api/pull",
            json={"name": model_name, "stream": False},
            timeout=10  # Just to start the pull, not wait for completion
        )
        if response.status_code == 200:
            logger.info(f"Model pull initiated via API for {model_name}")
            return True
        else:
            logger.warning(f"Failed to pull model via API: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error pulling model: {str(e)}")
        return False

# Try to start Ollama if it's installed but not running
def ensure_ollama_running():
    """Try to ensure Ollama is running if installed."""
    try:
        # Check if ollama is installed
        result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
        if result.returncode == 0:
            # Try to start ollama
            logger.info("Attempting to start Ollama...")
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
            logger.info("Ollama start attempt complete")
    except Exception as e:
        logger.warning(f"Failed to start Ollama: {str(e)}")

# Initialize LLM service with OPEA architecture
async def init_llm_service():
    """Initialize LLM service using OPEA architecture."""
    # Get configuration from environment
    llm_port = os.environ.get("LLM_SERVICE_PORT", "11434")
    llm_model = os.environ.get("LLM_MODEL_ID", "llama3.2:1b")
    
    # Try potential hosts
    potential_ips = get_potential_host_ips()
    
    # Information to return
    working_host = None
    available_models = []
    active_model = llm_model
    llm_service = None
    
    # Try OPEA initialization with each potential host
    for host_ip in potential_ips:
        try:
            # Create service
            service = await get_llm_service(host=host_ip, port=int(llm_port), model=llm_model)
            
            # Check health
            if await service.health_check():
                logger.info(f"Successfully connected to Ollama at {host_ip}:{llm_port}")
                working_host = host_ip
                
                # Check available models
                available_models = get_available_models(host_ip, llm_port)
                
                # Try to find a working model
                if llm_model not in available_models:
                    # Try pulling the model
                    pull_success = pull_model(host_ip, llm_port, llm_model)
                    
                    # If pull initiated, check if it's available now
                    if pull_success:
                        time.sleep(3)  # Brief wait to see if it's immediately available
                        available_models = get_available_models(host_ip, llm_port)
                    
                    # If still not available, try fallbacks
                    if llm_model not in available_models:
                        for fallback in FALLBACK_MODELS:
                            if fallback in available_models:
                                logger.info(f"Using fallback model: {fallback}")
                                active_model = fallback
                                service = await get_llm_service(host=host_ip, port=int(llm_port), model=active_model)
                                break
                
                # Save working configuration
                with open(".env", "w") as f:
                    f.write(f"LLM_SERVICE_HOST={host_ip}\n")
                    f.write(f"LLM_SERVICE_PORT={llm_port}\n")
                    f.write(f"LLM_MODEL_ID={active_model}\n")
                
                # Setup complete, return service
                llm_service = service
                break
        except Exception as e:
            logger.warning(f"Failed to initialize LLM service with host {host_ip}: {str(e)}")
    
    return llm_service, working_host, available_models, active_model

# Initialize LLM client and vocab generator with OPEA architecture
@st.cache_resource
def initialize_generator():
    """Initialize the vocabulary generator with OPEA or fallback to legacy client."""
    # Ensure Ollama is running if possible
    ensure_ollama_running()
    
    # Get configuration
    llm_port = os.environ.get("LLM_SERVICE_PORT", "11434")
    llm_model = os.environ.get("LLM_MODEL_ID", "llama3.2:1b")
    
    try:
        # Run async initialization in an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        llm_service, working_host, available_models, active_model = loop.run_until_complete(
            init_llm_service()
        )
        
        # If OPEA service initialization successful
        if llm_service:
            logger.info(f"Using OPEA architecture with model {active_model}")
            generator = VocabGenerator(llm_service=llm_service)
            return generator, working_host, available_models, active_model, True  # True for OPEA
    except Exception as e:
        logger.error(f"Failed to initialize OPEA services: {str(e)}")
    
    # Fallback to legacy client
    logger.warning("Falling back to legacy LLM client")
    
    # Legacy client initialization with potential hosts
    potential_ips = get_potential_host_ips()
    working_host = None
    available_models = []
    active_model = llm_model
    
    for host_ip in potential_ips:
        base_url = f"http://{host_ip}:{llm_port}"
        logger.info(f"Trying to connect to Ollama at: {base_url}")
        
        client = LLMClient(base_url=base_url, model=llm_model)
        if client.check_health():
            logger.info(f"Successfully connected to Ollama at {base_url}")
            
            # Save this working configuration for future use
            with open(".env", "w") as f:
                f.write(f"LLM_SERVICE_HOST={host_ip}\n")
                f.write(f"LLM_SERVICE_PORT={llm_port}\n")
                f.write(f"LLM_MODEL_ID={llm_model}\n")
            
            working_host = host_ip
            available_models = get_available_models(host_ip, llm_port)
            
            # Check model availability and fallbacks
            if llm_model not in available_models and available_models:
                for fallback in FALLBACK_MODELS:
                    if fallback in available_models:
                        logger.info(f"Using fallback model: {fallback}")
                        active_model = fallback
                        client = LLMClient(base_url=base_url, model=active_model)
                        break
            
            generator = VocabGenerator(llm_client=client)
            return generator, working_host, available_models, active_model, False  # False for legacy
    
    # If all else fails, create a generator with empty client for fallback mode
    logger.error("Failed to connect to Ollama on any available host")
    default_client = LLMClient(base_url=f"http://localhost:{llm_port}", model=llm_model)
    generator = VocabGenerator(llm_client=default_client)
    return generator, None, [], llm_model, False

# Page configuration
st.set_page_config(
    page_title="Language Learning Vocabulary Importer",
    page_icon="📚",
    layout="wide"
)

# App title and description
st.title("📚 Language Learning Vocabulary Generator")
st.markdown("""
This tool helps you generate vocabulary for the language learning application.
You can generate vocabulary words, vocabulary groups, export to JSON, and import from JSON.
""")

# Handle and display connection status in the UI
def check_ollama_connection(generator, host, available_models, active_model, using_opea):
    # First check if we have a working client
    if using_opea:
        connection_ok = generator.llm_service is not None
    else:
        connection_ok = generator.llm_client.check_health() if generator.llm_client else False
    
    if connection_ok:
        st.success("✅ Connected to Ollama successfully!")
        
        # Show architecture info
        arch_label = "OPEA Architecture" if using_opea else "Legacy Client"
        st.write(f"**Using:** {arch_label}")
        
        # Show connection info
        if host:
            st.write(f"**Server:** {host}:{os.environ.get('LLM_SERVICE_PORT', '11434')}")
        st.write(f"**Active model:** {active_model}")
        
        # Show available models
        if available_models:
            with st.expander("Available models"):
                st.write(", ".join(available_models))
        
        # Show model pull interface if desired model not available
        desired_model = os.environ.get("LLM_MODEL_ID", "llama3.2:1b")
        if desired_model not in available_models and host:
            st.warning(f"Your desired model **{desired_model}** is not available.")
            if st.button("Pull Model"):
                if pull_model(host, 11434, desired_model):
                    st.info(f"Model pull initiated for {desired_model}. This may take several minutes. Refresh the page after a few minutes to check if it's available.")
                else:
                    st.error("Failed to initiate model pull. You may need to pull it manually.")
    else:
        st.error("❌ Failed to connect to Ollama. Please check that Ollama is running.")
        
        # Manual connection instructions for the user
        with st.expander("💡 Connection Troubleshooting"):
            st.markdown("""
            **Troubleshooting steps:**
            
            1. **Make sure Ollama is installed and running**
               - On Windows: Look for the Ollama app in your taskbar
               - In WSL: Run `ollama serve` in a separate terminal
            
            2. **If you're using WSL, try these options:**
               - Run Ollama in Windows and use one of these IPs in your .env file:
                 ```
                 # In lang-portal/vocab-importer/.env
                 LLM_SERVICE_HOST=172.17.0.1  # This seems to be working for you
                 LLM_SERVICE_PORT=11434
                 LLM_MODEL_ID=llama2:13b
                 ```
                 
               - Install Ollama directly in WSL:
                 ```
                 # Install Ollama
                 curl -fsSL https://ollama.com/install.sh | sh
                 
                 # Run Ollama in a separate terminal
                 ollama serve
                 ```
            
            3. **Pull required models:**
               ```
               ollama pull llama2:13b
               ```
               
               If that specific model doesn't work, try a different one:
               ```
               ollama pull llama2
               ```
               
               Then update your .env file with the model name:
               ```
               LLM_MODEL_ID=llama2
               ```
            
            After making changes, refresh this page to try connecting again.
            """)
    return connection_ok

# Initialize the generator
try:
    generator_info = initialize_generator()
    generator, working_host, available_models, active_model, using_opea = generator_info
    connection_ok = check_ollama_connection(generator, working_host, available_models, active_model, using_opea)
except Exception as e:
    st.error(f"Error initializing generator: {str(e)}")
    connection_ok = False
    generator = None
    working_host = None
    available_models = []
    active_model = None
    using_opea = False

# Add architecture indicator in the sidebar
st.sidebar.title("Architecture")
if using_opea:
    st.sidebar.success("Using OPEA Architecture")
else:
    st.sidebar.info("Using Legacy Client")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", [
    "Generate Vocabulary", 
    "Generate Groups", 
    "Export Data", 
    "Import Data"
])

# Initialize session state for generated data
if "generated_vocab" not in st.session_state:
    st.session_state.generated_vocab = []

if "generated_groups" not in st.session_state:
    st.session_state.generated_groups = []

# Function to display vocabulary in a table
def display_vocab_table(vocab_list):
    if not vocab_list:
        st.info("No vocabulary items to display.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(vocab_list)
    st.dataframe(df, use_container_width=True)

# Function to display groups in a table
def display_groups_table(group_list):
    if not group_list:
        st.info("No vocabulary groups to display.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(group_list)
    st.dataframe(df, use_container_width=True)

# Only show generation functionality if connection is OK
if not connection_ok:
    st.warning("Generation features are disabled until Ollama connection is fixed.")

# Page: Generate Vocabulary
if page == "Generate Vocabulary":
    st.header("Generate Vocabulary Words")
    
    if connection_ok:
        with st.form("vocab_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                language = st.selectbox("Language", ["Japanese", "French", "Spanish", "German", "Chinese", "Korean"])
                category = st.text_input("Category", "Basic Greetings")
            
            with col2:
                count = st.slider("Number of words", 5, 30, 10)
                difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
            
            generate_button = st.form_submit_button("Generate Vocabulary")
        
        if generate_button:
            with st.spinner("Generating vocabulary..."):
                try:
                    vocab_list = generator.generate_vocab_words(
                        language=language,
                        category=category,
                        count=count,
                        difficulty=difficulty
                    )
                    
                    if vocab_list:
                        st.session_state.generated_vocab = vocab_list
                        st.success(f"Generated {len(vocab_list)} vocabulary items!")
                    else:
                        st.error("Failed to generate vocabulary. Please check the logs.")
                except Exception as e:
                    st.error(f"Error generating vocabulary: {str(e)}")
        
        # Display generated vocabulary
        if st.session_state.generated_vocab:
            st.subheader("Generated Vocabulary")
            display_vocab_table(st.session_state.generated_vocab)
            
            # Allow clearing the generated vocabulary
            if st.button("Clear Generated Vocabulary"):
                st.session_state.generated_vocab = []
                st.experimental_rerun()

# Page: Generate Groups
elif page == "Generate Groups":
    st.header("Generate Vocabulary Groups")
    
    if connection_ok:
        with st.form("groups_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                language = st.selectbox("Language", ["Japanese", "French", "Spanish", "German", "Chinese", "Korean"])
            
            with col2:
                count = st.slider("Number of groups", 3, 20, 5)
            
            generate_button = st.form_submit_button("Generate Groups")
        
        if generate_button:
            with st.spinner("Generating vocabulary groups..."):
                try:
                    group_list = generator.generate_vocab_groups(
                        count=count,
                        language=language
                    )
                    
                    if group_list:
                        st.session_state.generated_groups = group_list
                        st.success(f"Generated {len(group_list)} vocabulary groups!")
                    else:
                        st.error("Failed to generate vocabulary groups. Please check the logs.")
                except Exception as e:
                    st.error(f"Error generating groups: {str(e)}")
        
        # Display generated groups
        if st.session_state.generated_groups:
            st.subheader("Generated Groups")
            display_groups_table(st.session_state.generated_groups)
            
            # Allow clearing the generated groups
            if st.button("Clear Generated Groups"):
                st.session_state.generated_groups = []
                st.experimental_rerun()

# Page: Export Data
elif page == "Export Data":
    st.header("Export Generated Data")
    
    tab1, tab2, tab3 = st.tabs(["Export Vocabulary", "Export Groups", "Export Both"])
    
    with tab1:
        st.subheader("Export Vocabulary to JSON")
        
        if not st.session_state.generated_vocab:
            st.info("No vocabulary has been generated yet. Go to the 'Generate Vocabulary' page first.")
        else:
            st.write(f"You have {len(st.session_state.generated_vocab)} vocabulary items ready to export.")
            
            # Preview the data
            with st.expander("Preview Data"):
                display_vocab_table(st.session_state.generated_vocab)
            
            # Export options
            export_filename = st.text_input("Filename", f"vocabulary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            if st.button("Export Vocabulary"):
                # Create the JSON string
                json_str = json.dumps(st.session_state.generated_vocab, indent=2, ensure_ascii=False)
                
                # Save to file
                output_path = os.path.join("output", export_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
                
                st.success(f"Exported vocabulary to {output_path}")
                
                # Provide download link
                st.download_button(
                    label="Download JSON File",
                    data=json_str,
                    file_name=export_filename,
                    mime="application/json"
                )
    
    with tab2:
        st.subheader("Export Groups to JSON")
        
        if not st.session_state.generated_groups:
            st.info("No groups have been generated yet. Go to the 'Generate Groups' page first.")
        else:
            st.write(f"You have {len(st.session_state.generated_groups)} vocabulary groups ready to export.")
            
            # Preview the data
            with st.expander("Preview Data"):
                display_groups_table(st.session_state.generated_groups)
            
            # Export options
            export_filename = st.text_input("Filename", f"groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            if st.button("Export Groups"):
                # Create the JSON string
                json_str = json.dumps(st.session_state.generated_groups, indent=2, ensure_ascii=False)
                
                # Save to file
                output_path = os.path.join("output", export_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
                
                st.success(f"Exported groups to {output_path}")
                
                # Provide download link
                st.download_button(
                    label="Download JSON File",
                    data=json_str,
                    file_name=export_filename,
                    mime="application/json"
                )
    
    with tab3:
        st.subheader("Export Both Vocabulary and Groups")
        
        if not st.session_state.generated_vocab and not st.session_state.generated_groups:
            st.info("No data has been generated yet. Go to the 'Generate' pages first.")
        else:
            vocab_count = len(st.session_state.generated_vocab)
            groups_count = len(st.session_state.generated_groups)
            
            st.write(f"You have {vocab_count} vocabulary items and {groups_count} vocabulary groups ready to export.")
            
            # Export options
            export_filename = st.text_input("Filename", f"vocab_and_groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            if st.button("Export All Data"):
                # Create a combined dictionary
                combined_data = {
                    "vocabulary": st.session_state.generated_vocab,
                    "groups": st.session_state.generated_groups
                }
                
                # Create the JSON string
                json_str = json.dumps(combined_data, indent=2, ensure_ascii=False)
                
                # Save to file
                output_path = os.path.join("output", export_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
                
                st.success(f"Exported all data to {output_path}")
                
                # Provide download link
                st.download_button(
                    label="Download JSON File",
                    data=json_str,
                    file_name=export_filename,
                    mime="application/json"
                )

# Page: Import Data
elif page == "Import Data":
    st.header("Import Data from JSON")
    
    st.write("Import vocabulary data from JSON files.")
    
    uploaded_file = st.file_uploader("Choose a JSON file", type=["json"])
    
    if uploaded_file is not None:
        try:
            # Read and parse the JSON
            content = uploaded_file.read().decode("utf-8")
            data = json.loads(content)
            
            if isinstance(data, list):
                # Check if it's vocabulary or groups
                if data and "japanese" in data[0] and "english" in data[0]:
                    st.session_state.generated_vocab = data
                    st.success(f"Imported {len(data)} vocabulary items!")
                    
                    with st.expander("Preview Imported Vocabulary"):
                        display_vocab_table(data)
                
                elif data and "name" in data[0]:
                    st.session_state.generated_groups = data
                    st.success(f"Imported {len(data)} vocabulary groups!")
                    
                    with st.expander("Preview Imported Groups"):
                        display_groups_table(data)
                
                else:
                    st.error("Unrecognized JSON format. The file should contain vocabulary items or groups.")
            
            elif isinstance(data, dict):
                # Check for combined format
                vocab_data = data.get("vocabulary", [])
                groups_data = data.get("groups", [])
                
                if vocab_data:
                    st.session_state.generated_vocab = vocab_data
                    st.success(f"Imported {len(vocab_data)} vocabulary items!")
                    
                    with st.expander("Preview Imported Vocabulary"):
                        display_vocab_table(vocab_data)
                
                if groups_data:
                    st.session_state.generated_groups = groups_data
                    st.success(f"Imported {len(groups_data)} vocabulary groups!")
                    
                    with st.expander("Preview Imported Groups"):
                        display_groups_table(groups_data)
                
                if not vocab_data and not groups_data:
                    st.error("Unrecognized JSON format. The file should contain vocabulary items or groups.")
            
            else:
                st.error("Unrecognized JSON format. The file should contain vocabulary items, groups, or both.")
        
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")

# Footer
st.markdown("---")
st.markdown("📚 Language Learning Vocabulary Generator - Internal Tool (OPEA-powered)") 