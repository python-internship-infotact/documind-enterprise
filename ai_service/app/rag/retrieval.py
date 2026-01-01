"""
Advanced retrieval system with hybrid search and context ranking
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Represents a single retrieval result"""
    content: str
    metadata: Dict
    score: float
    retrieval_method: str  # "semantic", "keyword", "hybrid"
    rank: int

class HybridRetriever:
    """Combines semantic and keyword search for better retrieval"""
    
    def __init__(self, vector_store, documents=None):
        self.vector_store = vector_store
        self.documents = documents or []
        
        # Weights for combining different retrieval methods
        self.semantic_weight = 0.7
        self.keyword_weight = 0.3
        
    def retrieve(self, query: str, top_k: int = 10, filter_dict: Optional[Dict] = None) -> List[RetrievalResult]:
        """Perform hybrid retrieval combining semantic and keyword search"""
        try:
            # Semantic search using vector store
            semantic_results = self._semantic_search(query, top_k * 2, filter_dict)
            
            # Keyword search using BM25-like scoring
            keyword_results = self._keyword_search(query, top_k * 2, filter_dict)
            
            # Combine and rank results
            combined_results = self._combine_results(semantic_results, keyword_results, top_k)
            
            logger.info(f"Retrieved {len(combined_results)} results for query: {query[:50]}...")
            return combined_results
            
        except Exception as e:
            logger.error(f"Error in hybrid retrieval: {e}")
            # Fallback to semantic search only
            return self._semantic_search(query, top_k, filter_dict)
    
    def _semantic_search(self, query: str, top_k: int, filter_dict: Optional[Dict] = None) -> List[RetrievalResult]:
        """Perform semantic search using vector similarity"""
        try:
            results = self.vector_store.search_similar(query, top_k, filter_dict)
            
            retrieval_results = []
            for i, result in enumerate(results):
                retrieval_results.append(RetrievalResult(
                    content=result.get('content', ''),
                    metadata=result.get('metadata', {}),
                    score=1.0 - result.get('score', 0.5),  # Convert distance to similarity
                    retrieval_method="semantic",
                    rank=i + 1
                ))
            
            return retrieval_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def _keyword_search(self, query: str, top_k: int, filter_dict: Optional[Dict] = None) -> List[RetrievalResult]:
        """Perform keyword-based search using TF-IDF-like scoring"""
        try:
            # Simple keyword matching - could be enhanced with proper BM25
            query_terms = query.lower().split()
            scored_docs = []
            
            # Get all documents from vector store (simplified approach)
            # In production, you'd want a proper inverted index
            all_results = self.vector_store.search_similar("", top_k * 5, filter_dict)
            
            for result in all_results:
                content = result.get('content', '').lower()
                score = self._calculate_keyword_score(query_terms, content)
                
                if score > 0:
                    scored_docs.append((result, score))
            
            # Sort by score and take top results
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            retrieval_results = []
            for i, (result, score) in enumerate(scored_docs[:top_k]):
                retrieval_results.append(RetrievalResult(
                    content=result.get('content', ''),
                    metadata=result.get('metadata', {}),
                    score=score,
                    retrieval_method="keyword",
                    rank=i + 1
                ))
            
            return retrieval_results
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []
    
    def _calculate_keyword_score(self, query_terms: List[str], content: str) -> float:
        """Calculate keyword matching score"""
        if not query_terms or not content:
            return 0.0
        
        content_words = content.split()
        total_words = len(content_words)
        
        if total_words == 0:
            return 0.0
        
        # Count term frequencies
        term_scores = []
        for term in query_terms:
            term_count = content.count(term)
            if term_count > 0:
                # Simple TF score
                tf_score = term_count / total_words
                term_scores.append(tf_score)
        
        # Return average term score
        return sum(term_scores) / len(query_terms) if term_scores else 0.0
    
    def _combine_results(self, semantic_results: List[RetrievalResult], 
                        keyword_results: List[RetrievalResult], top_k: int) -> List[RetrievalResult]:
        """Combine semantic and keyword results using weighted scoring"""
        
        # Create a map of document ID to results
        doc_map = {}
        
        # Add semantic results
        for result in semantic_results:
            doc_id = self._get_doc_id(result.metadata)
            if doc_id not in doc_map:
                doc_map[doc_id] = {
                    'result': result,
                    'semantic_score': result.score,
                    'keyword_score': 0.0
                }
            else:
                doc_map[doc_id]['semantic_score'] = max(doc_map[doc_id]['semantic_score'], result.score)
        
        # Add keyword results
        for result in keyword_results:
            doc_id = self._get_doc_id(result.metadata)
            if doc_id not in doc_map:
                doc_map[doc_id] = {
                    'result': result,
                    'semantic_score': 0.0,
                    'keyword_score': result.score
                }
            else:
                doc_map[doc_id]['keyword_score'] = max(doc_map[doc_id]['keyword_score'], result.score)
        
        # Calculate combined scores
        combined_results = []
        for doc_id, data in doc_map.items():
            combined_score = (
                self.semantic_weight * data['semantic_score'] + 
                self.keyword_weight * data['keyword_score']
            )
            
            result = data['result']
            result.score = combined_score
            result.retrieval_method = "hybrid"
            combined_results.append(result)
        
        # Sort by combined score and return top results
        combined_results.sort(key=lambda x: x.score, reverse=True)
        
        # Update ranks
        for i, result in enumerate(combined_results[:top_k]):
            result.rank = i + 1
        
        return combined_results[:top_k]
    
    def _get_doc_id(self, metadata: Dict) -> str:
        """Generate a unique document ID from metadata"""
        source_file = metadata.get('source_file', 'unknown')
        page_number = metadata.get('page_number', 0)
        chunk_id = metadata.get('chunk_id', '')
        
        return f"{source_file}_{page_number}_{chunk_id}"

class ContextRanker:
    """Ranks and filters retrieved documents for optimal context"""
    
    def __init__(self, max_context_length: int = 4000):
        self.max_context_length = max_context_length
        
    def rank_and_filter(self, results: List[RetrievalResult], query: str) -> List[RetrievalResult]:
        """Rank results and filter to fit context window"""
        if not results:
            return []
        
        # Re-rank based on query relevance and diversity
        ranked_results = self._rerank_by_relevance(results, query)
        
        # Filter for diversity (avoid too many results from same document)
        diverse_results = self._ensure_diversity(ranked_results)
        
        # Filter by context length
        filtered_results = self._filter_by_length(diverse_results)
        
        logger.info(f"Ranked and filtered to {len(filtered_results)} results")
        return filtered_results
    
    def _rerank_by_relevance(self, results: List[RetrievalResult], query: str) -> List[RetrievalResult]:
        """Re-rank results based on query relevance"""
        query_terms = set(query.lower().split())
        
        for result in results:
            content_terms = set(result.content.lower().split())
            
            # Calculate additional relevance factors
            term_overlap = len(query_terms.intersection(content_terms)) / len(query_terms) if query_terms else 0
            content_length_factor = min(len(result.content) / 1000, 1.0)  # Prefer moderate length
            
            # Adjust score based on additional factors
            relevance_boost = term_overlap * 0.1 + content_length_factor * 0.05
            result.score += relevance_boost
        
        # Sort by adjusted score
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def _ensure_diversity(self, results: List[RetrievalResult], max_per_document: int = 3) -> List[RetrievalResult]:
        """Ensure diversity by limiting results per document"""
        doc_counts = defaultdict(int)
        diverse_results = []
        
        for result in results:
            source_file = result.metadata.get('source_file', 'unknown')
            
            if doc_counts[source_file] < max_per_document:
                diverse_results.append(result)
                doc_counts[source_file] += 1
        
        return diverse_results
    
    def _filter_by_length(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """Filter results to fit within context length limit"""
        filtered_results = []
        current_length = 0
        
        for result in results:
            content_length = len(result.content)
            
            if current_length + content_length <= self.max_context_length:
                filtered_results.append(result)
                current_length += content_length
            else:
                # Try to fit a truncated version
                remaining_space = self.max_context_length - current_length
                if remaining_space > 200:  # Only if we have reasonable space left
                    truncated_content = result.content[:remaining_space - 50] + "..."
                    result.content = truncated_content
                    filtered_results.append(result)
                break
        
        return filtered_results

class RetrievalAnalyzer:
    """Analyzes retrieval quality and provides insights"""
    
    def analyze_retrieval(self, query: str, results: List[RetrievalResult]) -> Dict[str, any]:
        """Analyze the quality of retrieval results"""
        if not results:
            return {
                "quality_score": 0.0,
                "coverage": "none",
                "diversity": 0.0,
                "confidence": "low",
                "recommendations": ["No results found - consider rephrasing the query"]
            }
        
        # Calculate quality metrics
        avg_score = sum(r.score for r in results) / len(results)
        score_variance = np.var([r.score for r in results]) if len(results) > 1 else 0
        
        # Analyze source diversity
        unique_sources = len(set(r.metadata.get('source_file', '') for r in results))
        diversity_score = unique_sources / len(results)
        
        # Determine confidence level
        confidence = self._determine_confidence(avg_score, score_variance, len(results))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(results, avg_score, diversity_score)
        
        return {
            "quality_score": avg_score,
            "coverage": self._assess_coverage(results),
            "diversity": diversity_score,
            "confidence": confidence,
            "num_results": len(results),
            "unique_sources": unique_sources,
            "recommendations": recommendations
        }
    
    def _determine_confidence(self, avg_score: float, variance: float, num_results: int) -> str:
        """Determine confidence level in retrieval results"""
        if avg_score > 0.7 and num_results >= 2:
            return "high"
        elif avg_score > 0.4 and num_results >= 1:
            return "medium"
        else:
            return "low"
    
    def _assess_coverage(self, results: List[RetrievalResult]) -> str:
        """Assess how well the results cover the query"""
        if not results:
            return "none"
        
        total_content_length = sum(len(r.content) for r in results)
        
        if total_content_length > 2000:
            return "comprehensive"
        elif total_content_length > 1000:
            return "good"
        elif total_content_length > 500:
            return "partial"
        else:
            return "limited"
    
    def _generate_recommendations(self, results: List[RetrievalResult], 
                                avg_score: float, diversity_score: float) -> List[str]:
        """Generate recommendations for improving retrieval"""
        recommendations = []
        
        if avg_score < 0.5:
            recommendations.append("Consider rephrasing your query with different keywords")
        
        if diversity_score < 0.3:
            recommendations.append("Results are from limited sources - try broader search terms")
        
        if len(results) < 3:
            recommendations.append("Few results found - consider using more general terms")
        
        if not recommendations:
            recommendations.append("Good retrieval quality - results should be relevant")
        
        return recommendations