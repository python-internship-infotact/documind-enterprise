#!/usr/bin/env python3
"""
Groq + HuggingFace API Validation Helper
Tests the new API configuration before running the full system
"""
import sys
import os
sys.path.append('ai_service')

def validate_groq():
    """Test Groq API key"""
    print("🧪 Testing Groq API...")
    
    try:
        from app.config import settings
        from groq import Groq
        
        client = Groq(api_key=settings.groq_api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Hello, respond with just 'API working'"}],
            max_tokens=10
        )
        
        print("✅ Groq API working!")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Groq API failed: {e}")
        if "invalid" in str(e).lower() or "unauthorized" in str(e).lower():
            print("   💡 Solution: Check your API key at https://console.groq.com/keys")
        return False

def validate_huggingface_embeddings():
    """Test HuggingFace embeddings"""
    print("\n🧪 Testing HuggingFace Embeddings...")
    
    try:
        from app.config import settings
        from langchain_huggingface import HuggingFaceEmbeddings
        
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Test embedding generation
        test_text = "This is a test document for embedding generation."
        embedding = embeddings.embed_query(test_text)
        
        print("✅ HuggingFace Embeddings working!")
        print(f"   Model: {settings.embedding_model}")
        print(f"   Embedding dimension: {len(embedding)}")
        print(f"   Sample values: {embedding[:3]}...")
        return True, len(embedding)
        
    except Exception as e:
        print(f"❌ HuggingFace Embeddings failed: {e}")
        print("   💡 Solution: Install required packages: pip install sentence-transformers")
        return False, None

def validate_pinecone():
    """Test Pinecone API key and create index if needed"""
    print("\n🧪 Testing Pinecone API...")
    
    try:
        from app.config import settings
        from pinecone import Pinecone, ServerlessSpec
        import time
        
        pc = Pinecone(api_key=settings.pinecone_api_key)
        
        # Test by listing indexes
        indexes = list(pc.list_indexes())
        
        print("✅ Pinecone API working!")
        print(f"   Found {len(indexes)} indexes")
        
        # Check if our index exists
        index_names = [idx.name for idx in indexes]
        if settings.pinecone_index_name in index_names:
            print(f"   ✅ Index '{settings.pinecone_index_name}' exists")
            
            # Check index dimension
            index = pc.Index(settings.pinecone_index_name)
            stats = index.describe_index_stats()
            print(f"   Index stats: {stats}")
            
        else:
            print(f"   ⚠️  Index '{settings.pinecone_index_name}' not found")
            print(f"   Available indexes: {index_names}")
            
            # Ask if we should create it
            create_index = input("\n   Create new index for HuggingFace embeddings (384 dim)? (y/n): ")
            if create_index.lower() == 'y':
                print(f"   Creating index '{settings.pinecone_index_name}'...")
                pc.create_index(
                    name=settings.pinecone_index_name,
                    dimension=384,  # HuggingFace all-MiniLM-L6-v2 dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print("   ⏳ Waiting for index to be ready...")
                time.sleep(10)
                print(f"   ✅ Index '{settings.pinecone_index_name}' created!")
        
        return True
        
    except Exception as e:
        print(f"❌ Pinecone API failed: {e}")
        if "unauthorized" in str(e).lower() or "invalid" in str(e).lower():
            print("   💡 Solution: Get a valid API key at https://app.pinecone.io/")
        return False

def validate_environment():
    """Check environment configuration"""
    print("\n📋 Environment Configuration:")
    
    try:
        from app.config import settings
        
        print(f"   Groq Key: {settings.groq_api_key[:10]}...{settings.groq_api_key[-4:]}")
        print(f"   Pinecone Key: {settings.pinecone_api_key[:8]}...{settings.pinecone_api_key[-4:]}")
        print(f"   Pinecone Env: {settings.pinecone_environment}")
        print(f"   Index Name: {settings.pinecone_index_name}")
        print(f"   Embedding Provider: {settings.embedding_provider}")
        print(f"   Embedding Model: {settings.embedding_model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment config failed: {e}")
        return False

def test_full_pipeline():
    """Test the complete pipeline with a simple document"""
    print("\n🧪 Testing Full Pipeline...")
    
    try:
        from app.database.pinecone_client import PineconeManager
        from app.models import DocumentMetadata, ProcessedDocument
        from datetime import datetime
        
        # Initialize Pinecone manager
        pm = PineconeManager()
        
        # Create a test document
        test_doc = ProcessedDocument(
            content="This is a test document about refund policies. Customers can get money back within 30 days.",
            metadata=DocumentMetadata(
                source_file="test_policy.pdf",
                page_number=1,
                document_title="Test Policy",
                section_header="Refund Policy",
                created_at=datetime.now().isoformat(),
                chunk_id="test-chunk-001",
                file_size=1024,
                total_pages=1
            )
        )
        
        # Test upsert
        print("   📤 Testing document upsert...")
        result = pm.upsert_documents([test_doc])
        
        if result["success"]:
            print(f"   ✅ Upsert successful: {result['processed_count']}/{result['total_documents']}")
            
            # Test search
            print("   🔍 Testing search...")
            search_results = pm.search_similar("How do I get money back?", top_k=1)
            
            if search_results:
                print(f"   ✅ Search successful! Found {len(search_results)} results")
                print(f"   Best match score: {search_results[0]['score']:.4f}")
                print(f"   Content preview: {search_results[0]['metadata'].get('content', 'N/A')[:100]}...")
                return True
            else:
                print("   ❌ Search returned no results")
                return False
        else:
            print(f"   ❌ Upsert failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Pipeline test failed: {e}")
        return False

def main():
    print("🔍 Groq + HuggingFace API Validation Tool")
    print("=" * 60)
    
    # Check environment
    if not validate_environment():
        print("\n❌ Environment configuration failed")
        return False
    
    # Test APIs
    groq_ok = validate_groq()
    hf_ok, embedding_dim = validate_huggingface_embeddings()
    pinecone_ok = validate_pinecone()
    
    print("\n" + "="*60)
    
    if groq_ok and hf_ok and pinecone_ok:
        print("🎉 ALL APIs WORKING!")
        
        # Test full pipeline
        pipeline_ok = test_full_pipeline()
        
        if pipeline_ok:
            print("\n✅ COMPLETE SYSTEM READY!")
            print("\n🚀 Next Steps:")
            print("   python demo_week1_working.py")
            print("   python test_real_integration.py")
        else:
            print("\n⚠️  APIs work but pipeline needs debugging")
        
        return True
    else:
        print("❌ API Setup Needed")
        print("\n🔧 Next Steps:")
        
        if not groq_ok:
            print("   1. Fix Groq API:")
            print("      - Get valid key: https://console.groq.com/keys")
            print("      - Update GROQ_API_KEY in .env")
        
        if not hf_ok:
            print("   2. Fix HuggingFace Embeddings:")
            print("      - Install: pip install sentence-transformers")
        
        if not pinecone_ok:
            print("   3. Fix Pinecone API:")
            print("      - Get valid key: https://app.pinecone.io/")
            print("      - Update PINECONE_API_KEY in .env")
        
        print("\n   4. Update .env file and run this script again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)