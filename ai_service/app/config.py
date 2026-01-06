"""
Application Configuration Settings

This module defines the configuration schema and default values for the
DocuMind Enterprise application using Pydantic settings management.

Configuration includes:
- API keys for external services (OpenAI, Groq, Pinecone)
- Embedding model configuration
- Document processing parameters
- System limits and constraints

Environment variables are automatically loaded from .env file.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    All settings can be overridden via environment variables.
    For example, GROQ_API_KEY environment variable will override groq_api_key.
    """
    
    # External API Keys
    openai_api_key: str = "test-key"  # OpenAI API key for embeddings (if using OpenAI provider)
    groq_api_key: str = "test-key"  # Groq API key for LLM inference
    pinecone_api_key: str = "test-key"  # Pinecone API key for vector database
    pinecone_environment: str = "test-env"  # Pinecone environment (deprecated in newer versions)
    pinecone_index_name: str = "documind-enterprise"  # Name of the Pinecone index
    
    # Embedding Model Configuration
    embedding_provider: str = "huggingface"  # Options: "openai", "huggingface"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # HuggingFace model name
    
    # Document Processing Parameters
    chunk_size: int = 1000  # Size of text chunks for processing
    chunk_overlap: int = 200  # Overlap between consecutive chunks
    max_file_size_mb: int = 50  # Maximum allowed file size in MB
    
    class Config:
        """Pydantic configuration to load from .env file"""
        env_file = ".env"

# Global settings instance
settings = Settings()