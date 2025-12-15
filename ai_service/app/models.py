from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentMetadata(BaseModel):
    source_file: str
    page_number: int
    chunk_id: str
    document_title: Optional[str] = None
    section_header: Optional[str] = None
    created_at: str
    file_size: Optional[int] = None
    total_pages: Optional[int] = None
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None
    parent_chunk_id: Optional[str] = None

class ProcessedDocument(BaseModel):
    content: str
    metadata: DocumentMetadata
    
class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[str] = None
    chunks_created: Optional[int] = None
    processing_time: Optional[float] = None

class ProcessingStatus(BaseModel):
    status: str  # "processing", "completed", "failed"
    progress: float  # 0.0 to 1.0
    message: str
    chunks_processed: int = 0
    total_chunks: int = 0