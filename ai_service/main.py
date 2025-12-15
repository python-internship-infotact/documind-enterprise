from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import logging
from typing import List, Optional

from app.ingestion.pipeline import DocumentIngestionPipeline
from app.models import DocumentUploadResponse, ProcessingStatus
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DocuMind Enterprise API",
    description="Enterprise Document Intelligence and RAG System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = DocumentIngestionPipeline()

@app.get("/")
async def root():
    return {
        "message": "DocuMind Enterprise API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        stats = pipeline.get_pipeline_stats()
        return {
            "status": "healthy" if stats.get("health_check", False) else "unhealthy",
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a PDF document
    """
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
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/documents/{document_id}/status", response_model=ProcessingStatus)
async def get_document_status(document_id: str):
    """
    Get processing status for a document
    """
    try:
        status = pipeline.get_processing_status(document_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """
    Delete a document and all its chunks
    """
    try:
        success = pipeline.delete_document(filename)
        if success:
            return {"message": f"Document {filename} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found or deletion failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_documents(
    query: str,
    top_k: int = 5,
    source_filter: Optional[str] = None
):
    """
    Search documents using semantic similarity
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
            
        results = pipeline.search_documents(
            query=query,
            top_k=top_k,
            source_filter=source_filter
        )
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/stats")
async def get_pipeline_stats():
    """
    Get pipeline and index statistics
    """
    try:
        return pipeline.get_pipeline_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)