"""
Pinecone Vector Database Client

This module provides a comprehensive interface for interacting with Pinecone vector database.
It handles document embeddings, vector storage, similarity search, and document management
with support for both OpenAI and HuggingFace embedding models.

Key Features:
- Dynamic embedding model support (OpenAI/HuggingFace)
- Batch document processing with error handling
- Semantic similarity search with filtering
- Document deletion by source file
- Health monitoring and statistics
"""

from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from typing import List, Dict, Optional, Any
import logging
import time
import uuid
from ..models import ProcessedDocument
from ..config import settings

logger = logging.getLogger(__name__)

class PineconeManager:
    """
    Manages Pinecone vector database operations for document storage and retrieval.
    
    This class handles:
    - Embedding model initialization (OpenAI or HuggingFace)
    - Pinecone index creation and management
    - Document vectorization and storage
    - Similarity search operations
    - Document deletion and cleanup
    """
    
    def __init__(self, config=None):
        """
        Initialize the Pinecone manager with embedding model and database connection.
        
        Args:
            config: Configuration object containing API keys and settings
        """
        if config is None:
            config = settings
            
        self.config = config
        
        # Initialize embeddings based on configured provider
        if config.embedding_provider == "openai":
            # Use OpenAI's text-embedding-ada-002 model (1536 dimensions)
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=config.openai_api_key,
                model="text-embedding-ada-002"
            )
            self.embedding_dimension = 1536
        else:  # Default to HuggingFace
            # Use HuggingFace sentence transformer model (384 dimensions)
            self.embeddings = HuggingFaceEmbeddings(
                model_name=config.embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            # Get dimension from the model (384 for all-MiniLM-L6-v2)
            self.embedding_dimension = 384
            
        logger.info(f"Using {config.embedding_provider} embeddings with dimension {self.embedding_dimension}")
        
        # Initialize Pinecone connection and index
        try:
            self.pc = Pinecone(api_key=config.pinecone_api_key)
            
            # Check if index exists, create if not
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if config.pinecone_index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {config.pinecone_index_name}")
                self.pc.create_index(
                    name=config.pinecone_index_name,
                    dimension=self.embedding_dimension,  # Use dynamic dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                # Wait for index to be ready
                time.sleep(10)
            
            self.index = self.pc.Index(config.pinecone_index_name)
            logger.info(f"Connected to Pinecone index: {config.pinecone_index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise
    
    def upsert_documents(self, documents: List[ProcessedDocument], batch_size: int = 100) -> Dict[str, Any]:
        """
        Upsert documents to Pinecone with batch processing and error handling
        """
        try:
            total_docs = len(documents)
            processed_count = 0
            failed_count = 0
            
            logger.info(f"Starting upsert of {total_docs} documents")
            
            # Process in batches
            for i in range(0, total_docs, batch_size):
                batch = documents[i:i + batch_size]
                
                try:
                    # Prepare batch data
                    texts = [doc.content for doc in batch]
                    metadatas = [self._prepare_metadata(doc.metadata, doc.content) for doc in batch]
                    ids = [doc.metadata.chunk_id for doc in batch]
                    
                    # Generate embeddings
                    embeddings = self.embeddings.embed_documents(texts)
                    
                    # Prepare vectors for upsert
                    vectors = []
                    for j, (doc_id, embedding, metadata) in enumerate(zip(ids, embeddings, metadatas)):
                        vectors.append({
                            "id": doc_id,
                            "values": embedding,
                            "metadata": metadata
                        })
                    
                    # Upsert to Pinecone
                    self.index.upsert(vectors=vectors)
                    processed_count += len(batch)
                    
                    logger.info(f"Processed batch {i//batch_size + 1}/{(total_docs-1)//batch_size + 1}")
                    
                    # Rate limiting - be gentle with API
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Failed to process batch {i//batch_size + 1}: {str(e)}")
                    failed_count += len(batch)
                    continue
            
            # Get index stats
            stats = self.index.describe_index_stats()
            
            result = {
                "success": True,
                "total_documents": total_docs,
                "processed_count": processed_count,
                "failed_count": failed_count,
                "index_stats": stats
            }
            
            logger.info(f"Upsert completed: {processed_count}/{total_docs} successful")
            return result
            
        except Exception as e:
            logger.error(f"Upsert operation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "total_documents": len(documents),
                "processed_count": 0,
                "failed_count": len(documents)
            }
    
    def _prepare_metadata(self, metadata, content: str = None) -> Dict[str, Any]:
        """
        Prepare metadata for Pinecone storage (must be JSON serializable)
        """
        # Handle all optional fields safely
        prepared = {
            "source_file": str(metadata.source_file),
            "page_number": int(metadata.page_number),
            "document_title": str(metadata.document_title) if metadata.document_title else "",
            "section_header": str(metadata.section_header) if metadata.section_header else "",
            "created_at": str(metadata.created_at),
            "chunk_index": int(metadata.chunk_index) if metadata.chunk_index is not None else 0,
            "total_chunks": int(metadata.total_chunks) if metadata.total_chunks is not None else 1,
            "parent_chunk_id": str(metadata.parent_chunk_id) if metadata.parent_chunk_id else "",
            "file_size": int(metadata.file_size) if metadata.file_size is not None else 0,
            "total_pages": int(metadata.total_pages) if metadata.total_pages is not None else 1
        }
        
        # Add content to metadata for retrieval (truncate if too long for Pinecone limits)
        if content:
            # Pinecone metadata has size limits, so truncate content if needed
            max_content_length = 8000  # Conservative limit
            if len(content) > max_content_length:
                prepared["content"] = content[:max_content_length] + "... [truncated]"
            else:
                prepared["content"] = content
        
        return prepared
    
    def search_similar(self, query: str, top_k: int = 5, 
                      filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar documents using semantic similarity
        """
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata,
                    "content": match.metadata.get("content", "")  # If stored in metadata
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    def delete_by_source(self, source_file: str) -> bool:
        """
        Delete all chunks from a specific source file
        """
        try:
            # Query to get all IDs for the source file
            filter_dict = {"source_file": {"$eq": source_file}}
            
            # Note: This is a simplified approach
            # In production, you might need to implement pagination for large deletions
            results = self.index.query(
                vector=[0] * self.embedding_dimension,  # Use correct dimension
                top_k=10000,  # Large number to get all
                include_metadata=True,
                filter=filter_dict
            )
            
            # Extract IDs and delete
            ids_to_delete = [match.id for match in results.matches]
            
            if ids_to_delete:
                self.index.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} chunks from {source_file}")
                return True
            else:
                logger.info(f"No chunks found for {source_file}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete chunks for {source_file}: {str(e)}")
            return False
    
    def get_index_stats(self) -> Dict:
        """
        Get current index statistics
        """
        try:
            return self.index.describe_index_stats()
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return {}
    
    def health_check(self) -> bool:
        """
        Check if Pinecone connection is healthy
        """
        try:
            stats = self.index.describe_index_stats()
            return True
        except Exception as e:
            logger.error(f"Pinecone health check failed: {str(e)}")
            return False