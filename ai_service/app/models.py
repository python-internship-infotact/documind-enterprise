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

# Chat-related models for Week 2
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"
    include_sources: bool = True
    stream: bool = False  # New field for streaming support

class ChatSource(BaseModel):
    source_file: str
    page_number: int
    score: float
    content_preview: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource] = []
    confidence: str  # "high", "medium", "low", "n/a"
    retrieval_quality: float
    processing_time: float
    session_id: str
    is_followup: bool = False
    status: str  # "success", "refused", "error"
    refusal_reason: Optional[str] = None
    error_message: Optional[str] = None

class ConversationHistoryRequest(BaseModel):
    session_id: str
    max_turns: Optional[int] = 10

class ConversationTurn(BaseModel):
    timestamp: str
    user_query: str
    ai_response: str
    sources_count: int
    turn_id: int

class ConversationHistoryResponse(BaseModel):
    session_id: str
    turns: List[ConversationTurn]
    total_turns: int

class SystemStatsResponse(BaseModel):
    vector_database: Dict[str, Any]
    conversation_memory: Dict[str, Any]
    system_health: Dict[str, Any]

# Week 3 Streaming Models
class StreamingChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"
    include_sources: bool = True

class StreamingChunk(BaseModel):
    type: str  # "token", "sources", "metadata", "error", "done"
    content: Optional[str] = None
    sources: Optional[List[ChatSource]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
class LatencyMetrics(BaseModel):
    time_to_first_token: float
    total_processing_time: float
    retrieval_time: float
    generation_time: float
    tokens_per_second: Optional[float] = None