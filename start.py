#!/usr/bin/env python3
"""
DocuMind Enterprise Startup Script

This script provides a convenient way to start the DocuMind Enterprise system
with proper environment validation and dependency management.

Features:
- Environment file validation
- Automatic dependency installation
- Server startup with proper error handling
- User-friendly status messages

Usage:
    python start.py

Requirements:
    - Python 3.8+
    - .env file with required API keys
    - Internet connection for dependency installation
"""

import os
import sys
import subprocess

def check_env_file():
    """
    Validate that the .env file exists with required configuration.
    
    Returns:
        bool: True if .env file exists, False otherwise
    """
    if not os.path.exists('.env'):
        print("Warning: .env file not found!")
        print("Please copy .env.example to .env and configure your API keys:")
        print("   cp .env.example .env")
        print("   # Edit .env with your OpenAI and Pinecone API keys")
        return False
    return True

def install_dependencies():
    """
    Install Python dependencies from requirements.txt.
    
    Returns:
        bool: True if installation successful, False otherwise
    """
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "ai_service/requirements.txt"], 
                      check=True, cwd=".")
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def start_server():
    """
    Start the FastAPI server using uvicorn.
    
    Returns:
        bool: True if server started successfully, False otherwise
    """
    print("Starting DocuMind Enterprise API...")
    try:
        os.chdir("ai_service")
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start server: {e}")
        return False
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return True

def main():
    """
    Main startup sequence with validation and error handling.
    """
    print("DocuMind Enterprise - Document Intelligence System")
    print("=" * 50)
    
    # Check environment configuration
    if not check_env_file():
        sys.exit(1)
    
    # Install required dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()