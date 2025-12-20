"""
RAG (Retrieval-Augmented Generation) Engine Module
Provides context-aware chat with hallucination prevention
"""

from .engine import DocuMindRAGEngine
from .prompts import ENTERPRISE_SYSTEM_PROMPT, QUERY_REFORMULATION_PROMPT
from .safety import HallucinationGuard, ResponseFilter
from .memory import EnterpriseConversationMemory

__all__ = [
    "DocuMindRAGEngine",
    "ENTERPRISE_SYSTEM_PROMPT",
    "QUERY_REFORMULATION_PROMPT",
    "HallucinationGuard",
    "ResponseFilter",
    "EnterpriseConversationMemory",
]
