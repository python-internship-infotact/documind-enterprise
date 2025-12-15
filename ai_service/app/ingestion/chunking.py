from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List, Dict, Optional
import uuid
import logging
from ..models import ProcessedDocument, DocumentMetadata
from datetime import datetime

logger = logging.getLogger(__name__)

class EnterpriseChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize text splitter with enterprise-optimized settings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
            keep_separator=True,
            length_function=len
        )
        
    def chunk_with_context(self, documents: List[ProcessedDocument]) -> List[ProcessedDocument]:
        """
        Chunk documents while preserving context and metadata
        Implements parent document retrieval strategy
        """
        chunked_documents = []
        
        for doc in documents:
            try:
                # Split the document content
                text_chunks = self.text_splitter.split_text(doc.content)
                
                # If document is small enough, keep as single chunk
                if len(text_chunks) <= 1:
                    chunked_documents.append(doc)
                    continue
                
                # Create chunks with enhanced metadata
                for i, chunk_text in enumerate(text_chunks):
                    if chunk_text.strip():  # Only create non-empty chunks
                        # Create new metadata for chunk
                        chunk_metadata = DocumentMetadata(
                            source_file=doc.metadata.source_file,
                            page_number=doc.metadata.page_number,
                            chunk_id=str(uuid.uuid4()),
                            document_title=doc.metadata.document_title,
                            section_header=self._extract_section_header(chunk_text),
                            created_at=datetime.now().isoformat(),
                            file_size=doc.metadata.file_size,
                            total_pages=doc.metadata.total_pages
                        )
                        
                        # Add chunk-specific metadata (as dict for flexibility)
                        chunk_metadata.chunk_index = i
                        chunk_metadata.total_chunks = len(text_chunks)
                        chunk_metadata.parent_chunk_id = doc.metadata.chunk_id
                        
                        # Create enhanced chunk with context
                        enhanced_chunk = self._add_context(
                            chunk_text, 
                            text_chunks, 
                            i, 
                            doc.metadata.source_file,
                            doc.metadata.page_number
                        )
                        
                        chunked_doc = ProcessedDocument(
                            content=enhanced_chunk,
                            metadata=chunk_metadata
                        )
                        
                        chunked_documents.append(chunked_doc)
                        
            except Exception as e:
                logger.error(f"Error chunking document {doc.metadata.source_file}: {str(e)}")
                # Keep original document if chunking fails
                chunked_documents.append(doc)
        
        logger.info(f"Created {len(chunked_documents)} chunks from {len(documents)} documents")
        return chunked_documents
    
    def _extract_section_header(self, chunk_text: str) -> Optional[str]:
        """
        Extract section header from chunk text using heuristics
        """
        lines = chunk_text.split('\n')
        
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check for header patterns
            if (len(line) < 100 and  # Not too long
                (line.isupper() or  # ALL CAPS
                 line.istitle() or  # Title Case
                 line.endswith(':') or  # Ends with colon
                 any(char.isdigit() for char in line[:5]))):  # Starts with number
                return line
                
        return None
    
    def _add_context(self, chunk_text: str, all_chunks: List[str], 
                    chunk_index: int, source_file: str, page_number: int) -> str:
        """
        Add contextual information to chunk for better retrieval
        """
        context_parts = []
        
        # Add source context
        context_parts.append(f"Source: {source_file} (Page {page_number})")
        
        # Add previous chunk context if available
        if chunk_index > 0 and len(all_chunks[chunk_index - 1]) > 50:
            prev_snippet = all_chunks[chunk_index - 1][-100:].strip()
            context_parts.append(f"Previous context: ...{prev_snippet}")
        
        # Add main chunk content
        context_parts.append(chunk_text)
        
        # Add next chunk context if available
        if chunk_index < len(all_chunks) - 1 and len(all_chunks[chunk_index + 1]) > 50:
            next_snippet = all_chunks[chunk_index + 1][:100].strip()
            context_parts.append(f"Following context: {next_snippet}...")
        
        return "\n\n".join(context_parts)
    
    def optimize_chunk_boundaries(self, text: str) -> List[str]:
        """
        Optimize chunk boundaries to avoid breaking sentences or paragraphs
        """
        # This is a placeholder for more sophisticated boundary optimization
        # Could implement sentence boundary detection, paragraph preservation, etc.
        return self.text_splitter.split_text(text)
    
    def get_chunk_statistics(self, chunks: List[ProcessedDocument]) -> Dict:
        """
        Get statistics about the chunking process
        """
        if not chunks:
            return {}
            
        chunk_lengths = [len(chunk.content) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "avg_chunk_length": sum(chunk_lengths) / len(chunk_lengths),
            "min_chunk_length": min(chunk_lengths),
            "max_chunk_length": max(chunk_lengths),
            "total_characters": sum(chunk_lengths)
        }