#!/usr/bin/env python3
"""
Pinecone Setup Helper
Creates the index and verifies connection
"""
import sys
import os
sys.path.append('ai_service')

def setup_pinecone():
    print("🔧 Pinecone Setup Helper")
    print("=" * 60)
    
    try:
        from app.config import settings
        from pinecone import Pinecone, ServerlessSpec
        
        print(f"\n📋 Configuration:")
        print(f"   API Key: {settings.pinecone_api_key[:8]}...{settings.pinecone_api_key[-4:]}")
        print(f"   Environment: {settings.pinecone_environment}")
        print(f"   Index Name: {settings.pinecone_index_name}")
        
        # Initialize Pinecone
        print("\n1️⃣ Connecting to Pinecone...")
        pc = Pinecone(api_key=settings.pinecone_api_key)
        print("✅ Connected to Pinecone successfully!")
        
        # List existing indexes
        print("\n2️⃣ Checking existing indexes...")
        existing_indexes = [index.name for index in pc.list_indexes()]
        print(f"   Found {len(existing_indexes)} existing indexes: {existing_indexes}")
        
        # Check if our index exists
        if settings.pinecone_index_name in existing_indexes:
            print(f"✅ Index '{settings.pinecone_index_name}' already exists!")
            
            # Get index info
            index = pc.Index(settings.pinecone_index_name)
            stats = index.describe_index_stats()
            print(f"   Vectors: {stats.get('total_vector_count', 0)}")
            print(f"   Dimension: {stats.get('dimension', 'unknown')}")
            
        else:
            print(f"⚠️  Index '{settings.pinecone_index_name}' does not exist")
            print("\n3️⃣ Creating new index...")
            
            # Create the index
            pc.create_index(
                name=settings.pinecone_index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=settings.pinecone_environment
                )
            )
            
            print(f"✅ Created index '{settings.pinecone_index_name}'")
            print("   Dimension: 1536")
            print("   Metric: cosine")
            print(f"   Region: {settings.pinecone_environment}")
            print("\n⏳ Waiting for index to be ready (this may take 30-60 seconds)...")
            
            import time
            time.sleep(10)
            
            # Verify index is ready
            index = pc.Index(settings.pinecone_index_name)
            stats = index.describe_index_stats()
            print(f"✅ Index is ready! Current vectors: {stats.get('total_vector_count', 0)}")
        
        print("\n🎉 Pinecone setup complete!")
        print("\n📝 Next steps:")
        print("   1. Make sure OpenAI API has credits")
        print("   2. Run: python test_real_integration.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\n🔍 Troubleshooting:")
        print("   1. Verify your Pinecone API key at: https://app.pinecone.io/")
        print("   2. Check that your account is active")
        print("   3. Ensure the environment matches your Pinecone project")
        print("   4. Try regenerating your API key if needed")
        
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_pinecone()
    sys.exit(0 if success else 1)