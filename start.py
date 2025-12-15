#!/usr/bin/env python3
"""
DocuMind Enterprise Startup Script
"""
import os
import sys
import subprocess

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found!")
        print("📝 Please copy .env.example to .env and configure your API keys:")
        print("   cp .env.example .env")
        print("   # Edit .env with your OpenAI and Pinecone API keys")
        return False
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "ai_service/requirements.txt"], 
                      check=True, cwd=".")
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting DocuMind Enterprise API...")
    try:
        os.chdir("ai_service")
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return True

def main():
    print("🏢 DocuMind Enterprise - Document Intelligence System")
    print("=" * 50)
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()