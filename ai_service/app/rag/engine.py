"""
Main RAG Engine with hallucination prevention and history-aware retrieval
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from groq import Groq
from ..config import settings
from ..database.pinecone_client import PineconeManager
from .prompts import ENTERPRISE_SYSTEM_PROMPT, QUERY_REFORMULATION_PROMPT, REFUSAL_TEMPLATES
from .safety import HallucinationGuard, ResponseFilter, QueryClassifier
from .memory import EnterpriseConversationMemory, HistoryAwareQueryProcessor
from .retrieval import HybridRetriever, ContextRanker, RetrievalAnalyzer

logger = logging.getLogger(__name__)

class DocuMindRAGEngine:
    """Enterprise RAG engine with advanced safety and context awareness"""
    
    def __init__(self):
        # Initialize core components
        self.groq_client = Groq(api_key=settings.groq_api_key)
        self.vector_store = PineconeManager()
        
        # Initialize RAG components
        self.retriever = HybridRetriever(self.vector_store)
        self.context_ranker = ContextRanker(max_context_length=4000)
        self.retrieval_analyzer = RetrievalAnalyzer()
        
        # Initialize safety components
        self.hallucination_guard = HallucinationGuard()
        self.response_filter = ResponseFilter()
        self.query_classifier = QueryClassifier()
        
        # Initialize memory components
        self.memory = EnterpriseConversationMemory()
        self.history_processor = HistoryAwareQueryProcessor(self.memory)
        
        logger.info("DocuMind RAG Engine initialized successfully")
    
    async def query(self, question: str, session_id: str = "default") -> Dict[str, any]:
        """Process a query with full RAG pipeline"""
        start_time = datetime.now()
        
        try:
            # Step 1: Query classification and safety check
            query_analysis = self.query_classifier.classify_query(question)
            
            if query_analysis["is_external"]:
                logger.warning(f"External knowledge query detected: {question}")
                return self._create_refusal_response(
                    question, 
                    REFUSAL_TEMPLATES["external_knowledge"],
                    "external_knowledge_detected"
                )
            
            # Step 2: Process query with conversation history
            processed_query = self.history_processor.process_query(question, session_id)
            search_query = processed_query["search_query"]
            
            logger.info(f"Processing query: {question}")
            if processed_query["is_followup"]:
                logger.info(f"Follow-up detected, reformulated to: {search_query}")
            
            # Step 3: Retrieve relevant documents
            retrieval_results = self.retriever.retrieve(search_query, top_k=10)
            
            if not retrieval_results:
                logger.warning(f"No documents retrieved for query: {question}")
                return self._create_refusal_response(
                    question,
                    REFUSAL_TEMPLATES["insufficient_context"],
                    "no_documents_found"
                )
            
            # Step 4: Rank and filter context
            ranked_results = self.context_ranker.rank_and_filter(retrieval_results, search_query)
            
            # Step 5: Analyze retrieval quality
            retrieval_analysis = self.retrieval_analyzer.analyze_retrieval(search_query, ranked_results)
            
            if retrieval_analysis["confidence"] == "low":
                logger.warning(f"Low confidence retrieval for query: {question}")
                return self._create_refusal_response(
                    question,
                    REFUSAL_TEMPLATES["insufficient_context"],
                    "low_confidence_retrieval"
                )
            
            # Step 6: Generate response
            response_data = await self._generate_response(
                question, 
                search_query, 
                ranked_results, 
                processed_query["context"]
            )
            
            # Step 7: Safety validation
            is_safe, violations = self.hallucination_guard.is_safe_response(
                response_data["answer"], 
                [{"metadata": r.metadata} for r in ranked_results]
            )
            
            if not is_safe:
                logger.error(f"Unsafe response detected with {len(violations)} violations")
                return self._create_refusal_response(
                    question,
                    REFUSAL_TEMPLATES["insufficient_context"],
                    "safety_violation"
                )
            
            # Step 8: Store conversation turn
            sources_used = [
                {
                    "source_file": r.metadata.get("source_file", ""),
                    "page_number": r.metadata.get("page_number", 0),
                    "score": r.score,
                    "content_preview": r.content[:100] + "..." if len(r.content) > 100 else r.content
                }
                for r in ranked_results
            ]
            
            self.memory.add_turn(
                session_id=session_id,
                user_query=question,
                ai_response=response_data["answer"],
                sources_used=sources_used
            )
            
            # Step 9: Prepare final response
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "answer": response_data["answer"],
                "sources": sources_used,
                "confidence": retrieval_analysis["confidence"],
                "retrieval_quality": retrieval_analysis["quality_score"],
                "processing_time": processing_time,
                "session_id": session_id,
                "is_followup": processed_query["is_followup"],
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing query '{question}': {str(e)}")
            return self._create_error_response(question, str(e))
    
    async def _generate_response(self, original_query: str, search_query: str, 
                               results: List, conversation_context: Dict) -> Dict[str, str]:
        """Generate AI response using Groq"""
        
        # Prepare context from retrieved documents
        context_parts = []
        for i, result in enumerate(results, 1):
            source_info = f"Source {i}: {result.metadata.get('source_file', 'Unknown')} (Page {result.metadata.get('page_number', 'N/A')})"
            context_parts.append(f"{source_info}\n{result.content}\n")
        
        context_text = "\n---\n".join(context_parts)
        
        # Prepare conversation history if available
        history_text = ""
        if conversation_context.get("has_context"):
            recent_history = conversation_context["chat_history"][-2:]  # Last 2 exchanges
            history_parts = []
            for exchange in recent_history:
                history_parts.append(f"User: {exchange['user']}\nAssistant: {exchange['assistant']}")
            history_text = "\n\n".join(history_parts)
        
        # Create the prompt
        system_prompt = ENTERPRISE_SYSTEM_PROMPT
        
        history_section = f"Recent Conversation History:\n{history_text}\n" if history_text else ""
        
        user_prompt = f"""Context Documents:
{context_text}

{history_section}

User Question: {original_query}

Please provide a helpful answer based ONLY on the context documents provided. Include proper citations in the format [Source: filename.pdf, Page X] for all factual claims."""
        
        try:
            # Generate response using Groq
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.1,  # Low temperature for consistency
                top_p=0.9
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Apply response filtering
            filtered_answer = self.response_filter.filter_response(
                answer, 
                [{"metadata": r.metadata} for r in results]
            )
            
            return {
                "answer": filtered_answer,
                "raw_answer": answer,
                "model_used": "llama-3.1-8b-instant"
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def _create_refusal_response(self, question: str, refusal_message: str, reason: str) -> Dict[str, any]:
        """Create a standardized refusal response"""
        return {
            "answer": refusal_message,
            "sources": [],
            "confidence": "n/a",
            "retrieval_quality": 0.0,
            "processing_time": 0.0,
            "session_id": "default",
            "is_followup": False,
            "status": "refused",
            "refusal_reason": reason
        }
    
    def _create_error_response(self, question: str, error_message: str) -> Dict[str, any]:
        """Create a standardized error response"""
        return {
            "answer": "I encountered an error processing your request. Please try again or contact support if the issue persists.",
            "sources": [],
            "confidence": "n/a",
            "retrieval_quality": 0.0,
            "processing_time": 0.0,
            "session_id": "default",
            "is_followup": False,
            "status": "error",
            "error_message": error_message
        }
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        history = self.memory.get_conversation_history(session_id)
        
        return [
            {
                "timestamp": turn.timestamp,
                "user_query": turn.user_query,
                "ai_response": turn.ai_response,
                "sources_count": len(turn.sources_used),
                "turn_id": turn.turn_id
            }
            for turn in history
        ]
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        try:
            if session_id in self.memory.sessions:
                del self.memory.sessions[session_id]
                if session_id in self.memory.turn_counter:
                    del self.memory.turn_counter[session_id]
                logger.info(f"Cleared conversation history for session {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing conversation {session_id}: {e}")
            return False
    
    def get_system_stats(self) -> Dict[str, any]:
        """Get system statistics"""
        try:
            # Get vector store stats
            vector_stats = self.vector_store.get_index_stats()
            
            # Get memory stats
            active_sessions = len(self.memory.sessions)
            total_turns = sum(len(session.turns) for session in self.memory.sessions.values())
            
            return {
                "vector_database": {
                    "total_vectors": vector_stats.get("total_vector_count", 0),
                    "dimension": vector_stats.get("dimension", 0),
                    "metric": vector_stats.get("metric", "unknown")
                },
                "conversation_memory": {
                    "active_sessions": active_sessions,
                    "total_turns": total_turns
                },
                "system_health": {
                    "vector_store_healthy": self.vector_store.health_check(),
                    "groq_api_configured": bool(settings.groq_api_key),
                    "safety_guards_active": True
                }
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}
    
    def cleanup_expired_sessions(self):
        """Clean up expired conversation sessions"""
        try:
            self.memory.cleanup_expired_sessions()
            logger.info("Cleaned up expired conversation sessions")
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")

# Global RAG engine instance
rag_engine = None

def get_rag_engine() -> DocuMindRAGEngine:
    """Get or create the global RAG engine instance"""
    global rag_engine
    if rag_engine is None:
        rag_engine = DocuMindRAGEngine()
    return rag_engine