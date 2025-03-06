#!/usr/bin/env python
"""
Test script for the Mega Service LLM API.
This script tests connectivity to the service and basic functionality.
"""

import argparse
import json
import sys
import time
import requests
from typing import Dict, Any, Optional, List

# Default endpoint URLs
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_OLLAMA_URL = "http://localhost:9000"
DEFAULT_MODEL = "llama3.2:1b"


def test_health(base_url: str) -> bool:
    """Test the health endpoint of the service."""
    print(f"Testing health endpoint at {base_url}/health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Health check successful: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check failed with error: {str(e)}")
        return False


def test_models(base_url: str) -> bool:
    """Test the models endpoint of the service."""
    print(f"Testing models endpoint at {base_url}/models...")
    try:
        response = requests.get(f"{base_url}/models", timeout=10)
        if response.status_code == 200:
            print(f"✅ Models endpoint successful: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Models endpoint failed with status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Models endpoint failed with error: {str(e)}")
        return False


def test_chat_completion(base_url: str, model: str) -> bool:
    """Test the chat completion endpoint of the service."""
    endpoint = f"{base_url}/v1/example-service"
    print(f"Testing chat completion endpoint at {endpoint}...")
    
    request_data = {
        "messages": [
            {
                "role": "user",
                "content": "Hello, provide a very brief response to test that you're working correctly."
            }
        ],
        "model": model,
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        print(f"Request: {json.dumps(request_data, indent=2)}")
        start_time = time.time()
        response = requests.post(endpoint, json=request_data, timeout=60)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            response_data = response.json()
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0].get('message', {}).get('content', '')
                print(f"✅ Chat completion successful ({elapsed_time:.2f}s):")
                print(f"Response: {content}")
                return True
            else:
                print(f"❌ Chat completion response missing choices: {json.dumps(response_data, indent=2)}")
                return False
        else:
            print(f"❌ Chat completion failed with status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat completion failed with error: {str(e)}")
        return False


def test_ollama_directly(ollama_url: str, model: str) -> bool:
    """Test Ollama directly to verify it's working."""
    print(f"Testing Ollama directly at {ollama_url}/api/chat...")
    
    request_data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Hello, provide a very brief response to test that you're working correctly."
            }
        ]
    }
    
    try:
        print(f"Request: {json.dumps(request_data, indent=2)}")
        start_time = time.time()
        response = requests.post(f"{ollama_url}/api/chat", json=request_data, timeout=60)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Ollama test successful ({elapsed_time:.2f}s):")
            print(f"Response: {response_data.get('message', {}).get('content', '')}")
            return True
        else:
            print(f"❌ Ollama test failed with status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ollama test failed with error: {str(e)}")
        return False


def run_tests(base_url: str, ollama_url: str, model: str) -> None:
    """Run all tests and report results."""
    print("=" * 50)
    print(f"TESTING MEGA SERVICE LLM API")
    print(f"Base URL: {base_url}")
    print(f"Ollama URL: {ollama_url}")
    print(f"Model: {model}")
    print("=" * 50)
    print()
    
    # Test Ollama first
    ollama_ok = test_ollama_directly(ollama_url, model)
    print()
    
    if not ollama_ok:
        print("⚠️ Ollama test failed, service tests will likely fail as well.")
    
    # Test service endpoints
    health_ok = test_health(base_url)
    print()
    
    models_ok = test_models(base_url)
    print()
    
    completion_ok = test_chat_completion(base_url, model)
    print()
    
    # Print summary
    print("=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Ollama Direct: {'✅ PASSED' if ollama_ok else '❌ FAILED'}")
    print(f"Health Check: {'✅ PASSED' if health_ok else '❌ FAILED'}")
    print(f"Models List: {'✅ PASSED' if models_ok else '❌ FAILED'}")
    print(f"Chat Completion: {'✅ PASSED' if completion_ok else '❌ FAILED'}")
    print()
    
    if all([ollama_ok, health_ok, models_ok, completion_ok]):
        print("🎉 All tests passed! The service is working correctly.")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Please check the logs above for details.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the Mega Service LLM API")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Base URL of the service (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL, help=f"URL of the Ollama service (default: {DEFAULT_OLLAMA_URL})")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model to use for testing (default: {DEFAULT_MODEL})")
    
    args = parser.parse_args()
    run_tests(args.base_url, args.ollama_url, args.model) 