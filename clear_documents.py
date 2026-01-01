#!/usr/bin/env python3
"""
Clear all documents from DocuMind Enterprise vector database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service.app.database.pinecone_client import PineconeManager
from ai_service.app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_all_documents():
    """Clear all documents from the vector database"""
    
    try:
        print("🗑️  Clearing all documents from vector database...")
        
        # Initialize Pinecone manager
        pinecone_manager = PineconeManager()
        
        # Get current stats
        stats = pinecone_manager.get_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        
        if total_vectors == 0:
            print("✅ Vector database is already empty")
            return True
        
        print(f"📊 Found {total_vectors} vectors in the database")
        
        # Delete all vectors (this is a nuclear option)
        # In production, you might want to be more selective
        pinecone_manager.index.delete(delete_all=True)
        
        print("✅ All documents cleared from vector database")
        print("🔄 The system is now ready for fresh document uploads")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to clear documents: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 DocuMind Enterprise - Clear Documents")
    print("=" * 50)
    
    success = clear_all_documents()
    
    if success:
        print("\n🎉 SUCCESS! Vector database cleared")
        print("📋 You can now:")
        print("   • Upload new documents via the frontend")
        print("   • Test with fresh document uploads")
        print("   • Verify document processing pipeline")
    else:
        print("\n❌ Failed to clear documents")
    
    print("\n🎬 Ready for testing!")