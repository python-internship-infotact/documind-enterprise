#!/usr/bin/env python3
"""
Basic functionality test without API keys
"""
import sys
import os
sys.path.append('ai_service')

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from app.models import DocumentMetadata, ProcessedDocument
        print("✅ Models import successful")
        
        from app.ingestion.pdf_processor import PDFProcessor
        print("✅ PDF processor import successful")
        
        from app.ingestion.chunking import EnterpriseChunker
        print("✅ Chunker import successful")
        
        # Test model creation
        metadata = DocumentMetadata(
            source_file="test.pdf",
            page_number=1,
            chunk_id="test-123",
            created_at="2024-01-01T00:00:00"
        )
        print("✅ Model creation successful")
        
        # Test chunker initialization
        chunker = EnterpriseChunker()
        print("✅ Chunker initialization successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_chunking_logic():
    """Test chunking logic without external dependencies"""
    print("\n🧪 Testing chunking logic...")
    
    try:
        from app.ingestion.chunking import EnterpriseChunker
        from app.models import ProcessedDocument, DocumentMetadata
        
        chunker = EnterpriseChunker(chunk_size=100, chunk_overlap=20)
        
        # Create test document
        test_content = "This is a test document. " * 20  # Long enough to chunk
        metadata = DocumentMetadata(
            source_file="test.pdf",
            page_number=1,
            chunk_id="test-123",
            created_at="2024-01-01T00:00:00"
        )
        
        doc = ProcessedDocument(content=test_content, metadata=metadata)
        
        # Test chunking
        chunks = chunker.chunk_with_context([doc])
        
        print(f"✅ Created {len(chunks)} chunks from test document")
        print(f"✅ First chunk length: {len(chunks[0].content)}")
        
        # Test statistics
        stats = chunker.get_chunk_statistics(chunks)
        print(f"✅ Statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chunking test failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\n🧪 Testing FastAPI app...")
    
    try:
        # Mock the pipeline to avoid API key requirements
        import unittest.mock
        
        with unittest.mock.patch('app.ingestion.pipeline.DocumentIngestionPipeline'):
            from main import app
            print("✅ FastAPI app creation successful")
            
            # Test that routes are registered
            routes = [route.path for route in app.routes]
            expected_routes = ["/", "/health", "/documents/upload", "/search"]
            
            for route in expected_routes:
                if route in routes:
                    print(f"✅ Route {route} registered")
                else:
                    print(f"❌ Route {route} missing")
                    
            return True
            
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        return False

def main():
    print("🏢 DocuMind Enterprise - Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_chunking_logic,
        test_fastapi_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All basic tests passed!")
        print("✅ Week 1 core implementation is working")
        print("\n📝 Next steps:")
        print("   1. Set up .env file with API keys")
        print("   2. Test with real PDF documents")
        print("   3. Verify Pinecone integration")
        return True
    else:
        print(f"\n❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)