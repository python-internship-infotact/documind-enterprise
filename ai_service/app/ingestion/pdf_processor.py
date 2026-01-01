from unstructured.partition.pdf import partition_pdf
from langchain_core.documents import Document
import os
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import logging
from ..models import DocumentMetadata, ProcessedDocument
import pypdf

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.processed_docs = []
        
    def extract_with_metadata(self, file_path: str, filename: str = None) -> List[ProcessedDocument]:
        """
        Extract text from PDF with comprehensive metadata including page numbers
        """
        try:
            if not filename:
                filename = os.path.basename(file_path)
                
            logger.info(f"Processing PDF: {filename}")
            
            # Use pypdf as primary method (no external dependencies)
            try:
                return self._extract_with_pypdf(file_path, filename)
            except Exception as e:
                logger.warning(f"pypdf processing failed: {e}, trying unstructured")
                return self._extract_with_unstructured(file_path, filename)
                
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {str(e)}")
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def _extract_with_unstructured(self, file_path: str, filename: str) -> List[ProcessedDocument]:
        """Extract using unstructured library (requires poppler)"""
        # Use unstructured to partition PDF with page numbers
        elements = partition_pdf(
            filename=file_path,
            strategy="fast",  # Use fast strategy instead of hi_res to avoid poppler dependency
            infer_table_structure=False,  # Disable to avoid dependencies
            include_page_breaks=True,
            extract_images_in_pdf=False  # Skip images for now
        )
        
        processed_docs = []
        current_page = 1
        
        # Group elements by page and extract text
        page_content = {}
        
        for element in elements:
            # Get page number from metadata
            page_num = getattr(element.metadata, 'page_number', current_page) if hasattr(element, 'metadata') else current_page
            
            if page_num not in page_content:
                page_content[page_num] = []
                
            # Extract text content
            text = str(element).strip()
            if text:
                page_content[page_num].append(text)
        
        # Create documents for each page
        total_pages = max(page_content.keys()) if page_content else 1
        
        for page_num, content_list in page_content.items():
            if content_list:  # Only create document if there's content
                content = "\n".join(content_list)
                
                # Create metadata
                metadata = DocumentMetadata(
                    source_file=filename,
                    page_number=page_num,
                    chunk_id=str(uuid.uuid4()),
                    document_title=self._extract_title(content_list[0] if content_list else ""),
                    created_at=datetime.now().isoformat(),
                    file_size=os.path.getsize(file_path) if os.path.exists(file_path) else None,
                    total_pages=total_pages
                )
                
                processed_doc = ProcessedDocument(
                    content=content,
                    metadata=metadata
                )
                
                processed_docs.append(processed_doc)
        
        return processed_docs
    
    def _extract_with_pypdf(self, file_path: str, filename: str) -> List[ProcessedDocument]:
        """Extract using pypdf library (no external dependencies)"""
        processed_docs = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    # Extract text from page
                    content = page.extract_text()
                    
                    if content.strip():  # Only create document if there's content
                        # Create metadata
                        metadata = DocumentMetadata(
                            source_file=filename,
                            page_number=page_num,
                            chunk_id=str(uuid.uuid4()),
                            document_title=self._extract_title(content.split('\n')[0] if content else ""),
                            created_at=datetime.now().isoformat(),
                            file_size=os.path.getsize(file_path) if os.path.exists(file_path) else None,
                            total_pages=total_pages
                        )
                        
                        processed_doc = ProcessedDocument(
                            content=content,
                            metadata=metadata
                        )
                        
                        processed_docs.append(processed_doc)
                        
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    continue
        
        logger.info(f"Successfully processed {len(processed_docs)} pages from {filename} using pypdf")
        return processed_docs
    
    def _extract_title(self, first_line: str) -> Optional[str]:
        """
        Extract document title from first line or header
        """
        if len(first_line) > 100:  # Too long to be a title
            return None
            
        # Simple heuristics for title detection
        if first_line.isupper() or first_line.istitle():
            return first_line.strip()
            
        return None
    
    def validate_pdf(self, file_path: str, max_size_mb: int = 50) -> bool:
        """
        Validate PDF file before processing
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
            
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ValueError(f"File size ({file_size_mb:.1f}MB) exceeds limit ({max_size_mb}MB)")
            
        return True