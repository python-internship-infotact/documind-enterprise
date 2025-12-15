import os
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime

from .pdf_processor import PDFProcessor
from .chunking import EnterpriseChunker
from ..database.pinecone_client import PineconeManager
from ..models import ProcessedDocument, DocumentUploadResponse, ProcessingStatus
from ..config import settings

logger = logging.getLogger(__name__)

class DocumentIngestionPipeline:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.chunker = EnterpriseChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        self.vector_store = PineconeManager()
        
    async def process_document(self, file_path: str, filename: str = None) -> DocumentUploadResponse:
        """
        Complete end-to-end document processing pipeline
        PDF -> Chunks -> Embeddings -> Pinecone
        """
        start_time = time.time()
        
        try:
            if not filename:
                filename = os.path.basename(file_path)
                
            logger.info(f"Starting pipeline processing for: {filename}")
            
            # Step 1: Validate PDF
            self.pdf_processor.validate_pdf(file_path, settings.max_file_size_mb)
            
            # Step 2: Extract text with metadata
            logger.info("Extracting text from PDF...")
            documents = self.pdf_processor.extract_with_metadata(file_path, filename)
            
            if not documents:
                return DocumentUploadResponse(
                    success=False,
                    message="No content extracted from PDF",
                    processing_time=time.time() - start_time
                )
            
            # Step 3: Chunk documents intelligently
            logger.info(f"Chunking {len(documents)} pages...")
            chunked_documents = self.chunker.chunk_with_context(documents)
            
            # Step 4: Store in vector database
            logger.info(f"Storing {len(chunked_documents)} chunks in Pinecone...")
            upsert_result = self.vector_store.upsert_documents(chunked_documents)
            
            processing_time = time.time() - start_time
            
            if upsert_result.get("success", False):
                return DocumentUploadResponse(
                    success=True,
                    message=f"Successfully processed {filename}",
                    document_id=filename,
                    chunks_created=len(chunked_documents),
                    processing_time=processing_time
                )
            else:
                return DocumentUploadResponse(
                    success=False,
                    message=f"Failed to store chunks: {upsert_result.get('error', 'Unknown error')}",
                    processing_time=processing_time
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Pipeline processing failed for {filename}: {str(e)}")
            
            return DocumentUploadResponse(
                success=False,
                message=f"Processing failed: {str(e)}",
                processing_time=processing_time
            )
    
    def get_processing_status(self, document_id: str) -> ProcessingStatus:
        """
        Get processing status for a document (placeholder for async processing)
        """
        # This is a simplified version - in production you'd track actual progress
        return ProcessingStatus(
            status="completed",
            progress=1.0,
            message="Processing completed",
            chunks_processed=0,
            total_chunks=0
        )
    
    def delete_document(self, filename: str) -> bool:
        """
        Delete all chunks for a specific document
        """
        try:
            return self.vector_store.delete_by_source(filename)
        except Exception as e:
            logger.error(f"Failed to delete document {filename}: {str(e)}")
            return False
    
    def get_pipeline_stats(self) -> Dict:
        """
        Get pipeline and index statistics
        """
        try:
            index_stats = self.vector_store.get_index_stats()
            
            return {
                "index_stats": index_stats,
                "pipeline_config": {
                    "chunk_size": settings.chunk_size,
                    "chunk_overlap": settings.chunk_overlap,
                    "max_file_size_mb": settings.max_file_size_mb
                },
                "health_check": self.vector_store.health_check()
            }
        except Exception as e:
            logger.error(f"Failed to get pipeline stats: {str(e)}")
            return {"error": str(e)}
    
    def search_documents(self, query: str, top_k: int = 5, 
                        source_filter: Optional[str] = None) -> List[Dict]:
        """
        Search documents using the vector store
        """
        try:
            filter_dict = None
            if source_filter:
                filter_dict = {"source_file": {"$eq": source_filter}}
                
            return self.vector_store.search_similar(
                query=query,
                top_k=top_k,
                filter_dict=filter_dict
            )
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []