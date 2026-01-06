#!/usr/bin/env python3
"""
Document Cleanup Utility

This utility script provides a convenient way to clear all documents
from the Pinecone vector database. Useful for development, testing,
or when you need to start fresh with a clean database.

Features:
- Complete database cleanup
- Progress reporting
- Error handling
- Status confirmation

Usage:
    python clear_documents.py

Warning:
    This operation is irreversible. All document vectors and metadata
    will be permanently deleted from the Pinecone index.
"""

import sys
import os
# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service.app.database.pinecone_client import PineconeManager
from ai_service.app.config import settings
import logging

# Configure logging for the cleanup process
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_all_documents():
    """
    Clear all documents from the vector database.
    
    This function connects to Pinecone and deletes all vectors
    from the configured index, effectively clearing all stored documents.
    
    Returns:
        bool: True if cleanup successful, False otherwise
    """
    
    try:
        print("Clearing all documents from vector database...")
        
        # Initialize Pinecone manager with current settings
        pinecone_manager = PineconeManager()
        
        # Get current database statistics
        stats = pinecone_manager.get_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        
        if total_vectors == 0:
            print("Vector database is already empty")
            return True
        
        print(f"Found {total_vectors} vectors in the database")
        
        # Delete all vectors from the index
        # Note: This is a complete deletion - use with caution in production
        pinecone_manager.index.delete(delete_all=True)
        
        print("All documents cleared from vector database")
        print("The system is now ready for fresh document uploads")
        
        return True
        
    except Exception as e:
        print(f"Failed to clear documents: {str(e)}")
        return False

if __name__ == "__main__":
    """
    Main execution block with user-friendly output and status reporting.
    """
    print("DocuMind Enterprise - Clear Documents")
    print("=" * 50)
    
    success = clear_all_documents()
    
    if success:
        print("\nSUCCESS! Vector database cleared")
        print("You can now:")
        print("   • Upload new documents via the frontend")
        print("   • Test with fresh document uploads")
        print("   • Verify document processing pipeline")
    else:
        print("\nFailed to clear documents")
    
    print("\nReady for testing!")