"""
Conversation memory and history-aware retrieval
Maintains context across multi-turn conversations
"""

import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation"""
    timestamp: str
    user_query: str
    ai_response: str
    sources_used: List[Dict]
    session_id: str
    turn_id: int

@dataclass
class ConversationSession:
    """Represents a complete conversation session"""
    session_id: str
    created_at: str
    last_activity: str
    turns: List[ConversationTurn]
    context_summary: str = ""

class EnterpriseConversationMemory:
    """Manages conversation memory with enterprise-grade features"""
    
    def __init__(self, max_turns_per_session: int = 10, session_timeout_hours: int = 24):
        self.max_turns_per_session = max_turns_per_session
        self.session_timeout_hours = session_timeout_hours
        self.sessions: Dict[str, ConversationSession] = {}
        self.turn_counter = defaultdict(int)
        
    def add_turn(self, session_id: str, user_query: str, ai_response: str, sources_used: List[Dict] = None) -> ConversationTurn:
        """Add a new conversation turn"""
        if sources_used is None:
            sources_used = []
            
        # Create session if it doesn't exist
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationSession(
                session_id=session_id,
                created_at=datetime.now().isoformat(),
                last_activity=datetime.now().isoformat(),
                turns=[]
            )
        
        session = self.sessions[session_id]
        self.turn_counter[session_id] += 1
        
        # Create new turn
        turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            user_query=user_query,
            ai_response=ai_response,
            sources_used=sources_used,
            session_id=session_id,
            turn_id=self.turn_counter[session_id]
        )
        
        # Add turn to session
        session.turns.append(turn)
        session.last_activity = datetime.now().isoformat()
        
        # Maintain session size limit
        if len(session.turns) > self.max_turns_per_session:
            session.turns = session.turns[-self.max_turns_per_session:]
        
        logger.info(f"Added turn {turn.turn_id} to session {session_id}")
        return turn
    
    def get_conversation_history(self, session_id: str, max_turns: int = 5) -> List[ConversationTurn]:
        """Get recent conversation history for a session"""
        if session_id not in self.sessions:
            return []
        
        session = self.sessions[session_id]
        
        # Check if session has expired
        if self._is_session_expired(session):
            logger.info(f"Session {session_id} has expired, clearing history")
            del self.sessions[session_id]
            return []
        
        # Return recent turns
        return session.turns[-max_turns:] if session.turns else []
    
    def get_context_for_query(self, session_id: str, current_query: str) -> Dict[str, any]:
        """Get relevant context for the current query"""
        history = self.get_conversation_history(session_id)
        
        if not history:
            return {
                "has_context": False,
                "chat_history": [],
                "relevant_topics": [],
                "last_sources": []
            }
        
        # Extract relevant information from history
        chat_history = []
        relevant_topics = set()
        last_sources = []
        
        for turn in history:
            chat_history.append({
                "user": turn.user_query,
                "assistant": turn.ai_response,
                "timestamp": turn.timestamp
            })
            
            # Extract topics/keywords from previous queries
            topics = self._extract_topics(turn.user_query)
            relevant_topics.update(topics)
            
            # Keep track of recent sources
            if turn.sources_used:
                last_sources.extend(turn.sources_used)
        
        # Remove duplicates from sources
        unique_sources = []
        seen_sources = set()
        for source in last_sources:
            source_key = f"{source.get('source_file', '')}_{source.get('page_number', '')}"
            if source_key not in seen_sources:
                unique_sources.append(source)
                seen_sources.add(source_key)
        
        return {
            "has_context": True,
            "chat_history": chat_history[-3:],  # Last 3 exchanges
            "relevant_topics": list(relevant_topics),
            "last_sources": unique_sources[-5:],  # Last 5 unique sources
            "session_length": len(history)
        }
    
    def _extract_topics(self, query: str) -> List[str]:
        """Extract key topics/keywords from a query"""
        # Simple keyword extraction - could be enhanced with NLP
        import re
        
        # Remove common words
        stop_words = {
            'what', 'how', 'when', 'where', 'why', 'who', 'which', 'is', 'are', 
            'was', 'were', 'do', 'does', 'did', 'can', 'could', 'should', 'would',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'about', 'our', 'my', 'your', 'their', 'this', 'that'
        }
        
        # Extract words
        words = re.findall(r'\b\w+\b', query.lower())
        topics = [word for word in words if word not in stop_words and len(word) > 2]
        
        return topics[:5]  # Return top 5 topics
    
    def _is_session_expired(self, session: ConversationSession) -> bool:
        """Check if a session has expired"""
        try:
            last_activity = datetime.fromisoformat(session.last_activity)
            expiry_time = last_activity + timedelta(hours=self.session_timeout_hours)
            return datetime.now() > expiry_time
        except Exception as e:
            logger.error(f"Error checking session expiry: {e}")
            return True
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            if session_id in self.turn_counter:
                del self.turn_counter[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_session_stats(self, session_id: str) -> Dict[str, any]:
        """Get statistics for a session"""
        if session_id not in self.sessions:
            return {"exists": False}
        
        session = self.sessions[session_id]
        
        return {
            "exists": True,
            "session_id": session_id,
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "total_turns": len(session.turns),
            "is_expired": self._is_session_expired(session)
        }

class HistoryAwareQueryProcessor:
    """Processes queries with conversation history context"""
    
    def __init__(self, memory: EnterpriseConversationMemory):
        self.memory = memory
        
    def process_query(self, query: str, session_id: str) -> Dict[str, any]:
        """Process a query with conversation context"""
        context = self.memory.get_context_for_query(session_id, query)
        
        # Analyze if this is a follow-up question
        is_followup = self._is_followup_question(query, context)
        
        # Reformulate query if needed
        reformulated_query = self._reformulate_query(query, context) if is_followup else query
        
        return {
            "original_query": query,
            "reformulated_query": reformulated_query,
            "is_followup": is_followup,
            "context": context,
            "search_query": reformulated_query
        }
    
    def _is_followup_question(self, query: str, context: Dict) -> bool:
        """Determine if this is a follow-up question"""
        if not context["has_context"]:
            return False
        
        # Simple heuristics for follow-up detection
        followup_indicators = [
            "how long", "how much", "when", "where", "why",
            "what about", "and what", "also", "additionally",
            "can i", "do i", "should i", "will i",
            "it", "that", "this", "they", "them"
        ]
        
        query_lower = query.lower()
        
        # Check for pronouns and short questions
        if len(query.split()) <= 5:  # Short questions are often follow-ups
            return True
        
        # Check for follow-up indicators
        for indicator in followup_indicators:
            if indicator in query_lower:
                return True
        
        return False
    
    def _reformulate_query(self, query: str, context: Dict) -> str:
        """Reformulate a follow-up query to be standalone"""
        if not context["has_context"]:
            return query
        
        # Get the last user query and AI response for context
        last_exchange = context["chat_history"][-1] if context["chat_history"] else None
        
        if not last_exchange:
            return query
        
        # Simple reformulation based on context
        last_query = last_exchange["user"]
        relevant_topics = context["relevant_topics"]
        
        # If query is very short, try to add context
        if len(query.split()) <= 3 and relevant_topics:
            # Add the most relevant topic from previous conversation
            main_topic = relevant_topics[0] if relevant_topics else ""
            reformulated = f"{query} about {main_topic}"
            logger.info(f"Reformulated query: '{query}' -> '{reformulated}'")
            return reformulated
        
        return query