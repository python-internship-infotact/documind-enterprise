#!/usr/bin/env python3
"""
Upload sample document to DocuMind Enterprise for testing
"""

import requests
import time

def upload_sample_document():
    """Upload the sample company policy PDF"""
    
    print("📄 Uploading sample company policy document...")
    
    # Check if file exists
    try:
        with open("sample_company_policy.pdf", "rb") as f:
            files = {"file": ("sample_company_policy.pdf", f, "application/pdf")}
            
            response = requests.post(
                "http://localhost:8001/documents/upload",
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Document uploaded successfully!")
                print(f"   Chunks created: {result.get('chunks_created', 'N/A')}")
                print(f"   Processing time: {result.get('processing_time', 'N/A')}s")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
    except FileNotFoundError:
        print("❌ sample_company_policy.pdf not found!")
        print("   Please run: python sample_company_policy.py")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def test_query_after_upload():
    """Test a query after document upload"""
    
    print("\n⏳ Waiting for document indexing...")
    time.sleep(5)
    
    print("🧪 Testing query with uploaded document...")
    
    try:
        response = requests.post(
            "http://localhost:8001/chat",
            json={
                "question": "What is the refund policy?",
                "session_id": "test_session",
                "include_sources": True
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   Sources: {len(result.get('sources', []))} documents")
            print(f"   Status: {result.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DocuMind Enterprise - Sample Document Upload")
    print("=" * 50)
    
    # Upload document
    upload_success = upload_sample_document()
    
    if upload_success:
        # Test query
        query_success = test_query_after_upload()
        
        if query_success:
            print("\n🎉 SUCCESS! System is ready for full testing")
            print("📋 You can now test:")
            print("   • What is the refund policy?")
            print("   • How do I contact customer support?")
            print("   • What are the vacation policies?")
            print("   • What are the working hours?")
        else:
            print("\n⚠️  Document uploaded but query test failed")
    else:
        print("\n❌ Document upload failed")
    
    print("\n🎬 Ready for streaming demo!")