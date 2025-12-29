from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import os
import tempfile
import logging
from typing import Dict, Any
import asyncio
import json

from ai_service.app.ingestion.pipeline import DocumentIngestionPipeline
from ai_service.app.models import (
    DocumentUploadResponse, ProcessingStatus, 
    ChatRequest, ChatResponse, ConversationHistoryRequest, 
    ConversationHistoryResponse, SystemStatsResponse,
    StreamingChatRequest, StreamingChunk, LatencyMetrics
)
from ai_service.app.rag.engine import get_rag_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DocuMind Enterprise API",
    description="Enterprise Document Intelligence and RAG System with Chat Capabilities and Streaming",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pipeline = DocumentIngestionPipeline()

@app.on_event("startup")
async def startup_event():
    """Initialize RAG engine on startup"""
    try:
        # Initialize RAG engine
        rag_engine = get_rag_engine()
        logger.info("RAG engine initialized successfully")
        
        # Start background cleanup task
        asyncio.create_task(periodic_cleanup())
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG engine: {e}")

async def periodic_cleanup():
    """Periodic cleanup of expired sessions"""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            rag_engine = get_rag_engine()
            rag_engine.cleanup_expired_sessions()
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")

@app.get("/")
async def root():
    """API status endpoint"""
    return {
        "message": "DocuMind Enterprise API",
        "version": "3.0.0",
        "status": "operational",
        "features": [
            "Document ingestion and processing",
            "Semantic search and retrieval",
            "AI-powered chat with hallucination prevention",
            "History-aware conversations",
            "Citation-based responses",
            "Real-time streaming responses",
            "Sub-second Time to First Token (TTFT)"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        rag_engine = get_rag_engine()
        stats = rag_engine.get_system_stats()
        
        return {
            "status": "healthy",
            "timestamp": "2025-12-29T14:43:00Z",  # Fixed timestamp
            "system_stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

# Document Management Endpoints
@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process document through pipeline
            result = await pipeline.process_document(temp_file_path, file.filename)
            return result
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document and all its chunks"""
    try:
        success = pipeline.delete_document(filename)
        
        if success:
            return {"message": f"Document {filename} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except Exception as e:
        logger.error(f"Document deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@app.get("/documents/search")
async def search_documents(query: str, top_k: int = 5, source_filter: str = None):
    """Search documents using semantic similarity"""
    try:
        results = pipeline.search_documents(
            query=query,
            top_k=top_k,
            source_filter=source_filter
        )
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Chat Endpoints (Week 2 + Week 3 Streaming)
@app.post("/chat", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """Process a chat query with RAG and safety checks"""
    try:
        rag_engine = get_rag_engine()
        
        # Check if streaming is requested
        if request.stream:
            # Redirect to streaming endpoint
            raise HTTPException(
                status_code=400, 
                detail="Use /chat/stream endpoint for streaming responses"
            )
        
        result = await rag_engine.query(
            question=request.question,
            session_id=request.session_id
        )
        
        # Convert to response format
        sources = []
        if request.include_sources:
            for source in result.get("sources", []):
                sources.append({
                    "source_file": source["source_file"],
                    "page_number": source["page_number"],
                    "score": source["score"],
                    "content_preview": source["content_preview"]
                })
        
        return ChatResponse(
            answer=result["answer"],
            sources=sources,
            confidence=result["confidence"],
            retrieval_quality=result["retrieval_quality"],
            processing_time=result["processing_time"],
            session_id=result["session_id"],
            is_followup=result["is_followup"],
            status=result["status"],
            refusal_reason=result.get("refusal_reason"),
            error_message=result.get("error_message")
        )
        
    except Exception as e:
        logger.error(f"Chat query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(request: StreamingChatRequest):
    """Process a chat query with streaming response for real-time UX"""
    
    async def generate_stream():
        """Generate streaming response chunks"""
        try:
            rag_engine = get_rag_engine()
            
            async for chunk in rag_engine.query_stream(
                question=request.question,
                session_id=request.session_id
            ):
                # Format chunk for SSE
                chunk_data = json.dumps(chunk, ensure_ascii=False)
                yield f"data: {chunk_data}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming chat failed: {e}")
            error_chunk = {
                "type": "error",
                "error": f"Streaming failed: {str(e)}"
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    )

@app.get("/chat/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(session_id: str, max_turns: int = 10):
    """Get conversation history for a session"""
    try:
        rag_engine = get_rag_engine()
        history = rag_engine.get_conversation_history(session_id)
        
        # Limit to max_turns
        limited_history = history[-max_turns:] if len(history) > max_turns else history
        
        return ConversationHistoryResponse(
            session_id=session_id,
            turns=limited_history,
            total_turns=len(history)
        )
        
    except Exception as e:
        logger.error(f"Failed to get conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")

@app.delete("/chat/history/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a session"""
    try:
        rag_engine = get_rag_engine()
        success = rag_engine.clear_conversation(session_id)
        
        if success:
            return {"message": f"Conversation history cleared for session {session_id}"}
        else:
            return {"message": f"No conversation history found for session {session_id}"}
            
    except Exception as e:
        logger.error(f"Failed to clear conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"History clearing failed: {str(e)}")

# System Management Endpoints
@app.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats():
    """Get comprehensive system statistics"""
    try:
        rag_engine = get_rag_engine()
        stats = rag_engine.get_system_stats()
        
        return SystemStatsResponse(
            vector_database=stats["vector_database"],
            conversation_memory=stats["conversation_memory"],
            system_health=stats["system_health"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@app.post("/admin/cleanup")
async def manual_cleanup():
    """Manually trigger cleanup of expired sessions"""
    try:
        rag_engine = get_rag_engine()
        rag_engine.cleanup_expired_sessions()
        
        return {"message": "Cleanup completed successfully"}
        
    except Exception as e:
        logger.error(f"Manual cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)