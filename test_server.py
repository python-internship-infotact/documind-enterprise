#!/usr/bin/env python3
"""
Test server startup without external dependencies
"""
import sys
import os
sys.path.append('ai_service')

# Mock external dependencies
import unittest.mock

def test_server_startup():
    """Test that the server can start without real API keys"""
    print("🧪 Testing server startup...")
    
    try:
        # Mock the external services
        with unittest.mock.patch('app.database.pinecone_client.Pinecone'), \
             unittest.mock.patch('app.ingestion.pipeline.PineconeManager'), \
             unittest.mock.patch('langchain_openai.OpenAIEmbeddings'):
            
            from main import app
            print("✅ FastAPI app created successfully")
            
            # Test that we can import the app
            assert app is not None
            print("✅ App object is valid")
            
            # Check routes
            routes = [route.path for route in app.routes]
            print(f"✅ Found {len(routes)} routes: {routes}")
            
            return True
            
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🏢 DocuMind Enterprise - Server Startup Test")
    print("=" * 50)
    
    if test_server_startup():
        print("\n🎉 Server startup test passed!")
        print("✅ The FastAPI application is properly configured")
        print("\n📝 To run the actual server:")
        print("   1. Configure real API keys in .env")
        print("   2. cd ai_service")
        print("   3. python main.py")
        return True
    else:
        print("\n❌ Server startup test failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)