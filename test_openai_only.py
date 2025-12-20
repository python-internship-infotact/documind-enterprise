#!/usr/bin/env python3
"""
Test OpenAI connection only
"""
import sys
import os
sys.path.append('ai_service')

def test_openai():
    print("🧪 Testing OpenAI Connection")
    print("=" * 40)
    
    try:
        from app.config import settings
        print(f"✅ OpenAI API Key: {settings.openai_api_key[:10]}...{settings.openai_api_key[-4:]}")
        
        from langchain_openai import OpenAIEmbeddings
        
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model="text-embedding-ada-002"
        )
        
        print("✅ OpenAI Embeddings client created")
        
        # Test embedding generation
        test_text = "This is a test for embedding generation."
        print(f"🧪 Testing embedding for: '{test_text}'")
        
        embedding = embeddings.embed_query(test_text)
        
        print(f"✅ Generated embedding with {len(embedding)} dimensions")
        print(f"✅ First 5 values: {embedding[:5]}")
        
        if len(embedding) == 1536:
            print("✅ Correct OpenAI embedding dimension")
            return True
        else:
            print(f"❌ Wrong dimension: {len(embedding)}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False

if __name__ == "__main__":
    if test_openai():
        print("\n🎉 OpenAI connection successful!")
    else:
        print("\n❌ OpenAI connection failed!")