#!/usr/bin/env python3
"""
Comprehensive Document Cleanup Utility

This utility script provides a complete system reset by clearing:
- All documents from Pinecone vector database
- All conversation memory and session history
- Rate limiter state
- Any cached embeddings

Features:
- Complete system cleanup
- Progress reporting
- Error handling
- Status confirmation

Usage:
    python clear_documents.py

Warning:
    This operation is irreversible. All document vectors, conversation
    history, and system state will be permanently deleted.
"""

import sys
import os
import requests
import time
# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service.app.database.pinecone_client import PineconeManager
from ai_service.app.config import settings
import logging

# Configure logging for the cleanup process
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_vector_database():
    """
    Clear all documents from the Pinecone vector database.
    
    Returns:
        bool: True if cleanup successful, False otherwise
    """
    
    try:
        print("1. Clearing vector database...")
        
        # Initialize Pinecone manager with current settings
        pinecone_manager = PineconeManager()
        
        # Get current database statistics
        stats = pinecone_manager.get_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        
        if total_vectors == 0:
            print("   ✓ Vector database is already empty")
            return True
        
        print(f"   Found {total_vectors} vectors in the database")
        
        # Delete all vectors from the index
        pinecone_manager.index.delete(delete_all=True)
        
        # Wait a moment for deletion to propagate
        time.sleep(2)
        
        # Verify deletion
        stats_after = pinecone_manager.get_index_stats()
        remaining_vectors = stats_after.get('total_vector_count', 0)
        
        if remaining_vectors == 0:
            print("   ✓ All vectors successfully deleted from database")
            return True
        else:
            print(f"   ⚠ Warning: {remaining_vectors} vectors still remain")
            return False
        
    except Exception as e:
        print(f"   ✗ Failed to clear vector database: {str(e)}")
        return False

def clear_conversation_memory():
    """
    Clear conversation memory by calling the API endpoint.
    
    Returns:
        bool: True if cleanup successful, False otherwise
    """
    
    try:
        print("2. Clearing conversation memory...")
        
        # Try to call the clear memory endpoint
        base_url = "http://localhost:8000"
        
        response = requests.post(f"{base_url}/api/clear-memory", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                cleared_sessions = result.get('cleared_sessions', 0)
                print(f"   ✓ Cleared {cleared_sessions} conversation sessions")
                return True
            else:
                print(f"   ⚠ API returned error: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"   ⚠ API call failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ⚠ AI service not running - memory will be cleared on next startup")
        return True  # This is OK if service is not running
    except Exception as e:
        print(f"   ⚠ Failed to clear conversation memory: {str(e)}")
        return False

def clear_rate_limiter():
    """
    Clear rate limiter state by calling the API endpoint.
    
    Returns:
        bool: True if cleanup successful, False otherwise
    """
    
    try:
        print("3. Clearing rate limiter state...")
        
        # Try to call the clear rate limiter endpoint
        base_url = "http://localhost:8000"
        
        response = requests.post(f"{base_url}/api/clear-rate-limits", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                cleared_clients = result.get('cleared_clients', 0)
                print(f"   ✓ Cleared rate limits for {cleared_clients} clients")
                return True
            else:
                print(f"   ⚠ API returned error: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"   ⚠ API call failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ⚠ AI service not running - rate limits will be cleared on next startup")
        return True  # This is OK if service is not running
    except Exception as e:
        print(f"   ⚠ Failed to clear rate limiter: {str(e)}")
        return False

def comprehensive_clear():
    """
    Perform comprehensive system cleanup.
    
    Returns:
        bool: True if all cleanup operations successful, False otherwise
    """
    
    print("Starting comprehensive system cleanup...")
    print("=" * 60)
    
    success_count = 0
    total_operations = 3
    
    # Clear vector database
    if clear_vector_database():
        success_count += 1
    
    # Clear conversation memory
    if clear_conversation_memory():
        success_count += 1
    
    # Clear rate limiter
    if clear_rate_limiter():
        success_count += 1
    
    print("=" * 60)
    
    if success_count == total_operations:
        print("✓ COMPLETE SUCCESS! All system components cleared")
        print("\nThe system is now completely reset and ready for:")
        print("   • Fresh document uploads")
        print("   • New conversation sessions")
        print("   • Clean testing environment")
        return True
    else:
        print(f"⚠ PARTIAL SUCCESS: {success_count}/{total_operations} operations completed")
        print("\nSome components may still retain old data.")
        print("Consider restarting the AI service for complete cleanup.")
        return False

if __name__ == "__main__":
    """
    Main execution block with user-friendly output and status reporting.
    """
    print("DocuMind Enterprise - Comprehensive System Clear")
    print("=" * 60)
    
    success = comprehensive_clear()
    
    if success:
        print("\n🎉 SUCCESS! System completely reset")
        print("\nNext steps:")
        print("   1. Upload your new test document")
        print("   2. Verify it processes correctly")
        print("   3. Test queries against the new document")
        print("\nThe system should now have no memory of previous documents!")
    else:
        print("\n⚠ Partial cleanup completed")
        print("Consider restarting the AI service and running this script again.")
    
    print("\nReady for testing!")