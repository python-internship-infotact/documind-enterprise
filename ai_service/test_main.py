import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from main import app
from app.ingestion.pipeline import DocumentIngestionPipeline

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "DocuMind Enterprise API"
    assert data["version"] == "1.0.0"

def test_health_endpoint():
    """Test the health check endpoint"""
    with patch.object(DocumentIngestionPipeline, 'get_pipeline_stats') as mock_stats:
        mock_stats.return_value = {"health_check": True}
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

def test_search_endpoint():
    """Test the search endpoint"""
    with patch.object(DocumentIngestionPipeline, 'search_documents') as mock_search:
        mock_search.return_value = [
            {
                "id": "test-chunk-1",
                "score": 0.95,
                "metadata": {
                    "source_file": "test.pdf",
                    "page_number": 1,
                    "content": "Test content about refunds"
                }
            }
        ]
        
        response = client.get("/search?query=refund policy")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "refund policy"
        assert len(data["results"]) == 1

def test_search_empty_query():
    """Test search with empty query"""
    response = client.get("/search?query=")
    assert response.status_code == 400

def test_upload_non_pdf():
    """Test uploading non-PDF file"""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(b"This is not a PDF")
        temp_file_path = temp_file.name
    
    try:
        with open(temp_file_path, 'rb') as f:
            response = client.post(
                "/documents/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        assert response.status_code == 400
        assert "Only PDF files are supported" in response.json()["detail"]
    finally:
        os.unlink(temp_file_path)

if __name__ == "__main__":
    pytest.main([__file__])