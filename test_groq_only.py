#!/usr/bin/env python3
"""
Simple Groq API Test
"""
import sys
import os
sys.path.append('ai_service')

def test_groq_simple():
    """Test Groq API with minimal setup"""
    print("🧪 Testing Groq API...")
    
    try:
        from app.config import settings
        from groq import Groq
        
        print(f"Using API key: {settings.groq_api_key[:10]}...{settings.groq_api_key[-4:]}")
        
        client = Groq(api_key=settings.groq_api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say 'Hello, Groq API is working!'"}],
            max_tokens=20
        )
        
        print("✅ Groq API working!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Groq API failed: {e}")
        return False

if __name__ == "__main__":
    success = test_groq_simple()
    if success:
        print("\n🎉 Ready to run full validation!")
        print("Run: python validate_groq_setup.py")
    else:
        print("\n❌ Fix the API key first")
    sys.exit(0 if success else 1)