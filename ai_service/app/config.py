from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: str = "test-key"  # Default for testing
    pinecone_api_key: str = "test-key"  # Default for testing  
    pinecone_environment: str = "test-env"  # Default for testing
    pinecone_index_name: str = "documind-enterprise"
    
    # Optional settings with defaults
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size_mb: int = 50
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()