from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = "test-key"  # Default for testing
    groq_api_key: str = "test-key"  # Groq API key
    pinecone_api_key: str = "test-key"  # Default for testing  
    pinecone_environment: str = "test-env"  # Default for testing
    pinecone_index_name: str = "documind-enterprise"
    
    # Embedding Configuration
    embedding_provider: str = "huggingface"  # Options: "openai", "huggingface"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # Free HuggingFace model
    
    # Optional settings with defaults
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size_mb: int = 50
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()