"""
Hallucination prevention and safety mechanisms
Ensures responses are strictly based on provided context
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SafetyViolation:
    """Represents a detected safety violation"""
    violation_type: str
    description: str
    severity: str  # "critical", "warning", "info"
    detected_text: str

class HallucinationGuard:
    """Advanced hallucination detection and prevention"""
    
    def __init__(self):
        # Patterns that indicate external knowledge usage
        self.external_knowledge_patterns = [
            r"according to general knowledge",
            r"it is widely known",
            r"typically", r"usually", r"generally",
            r"in most cases", r"common practice",
            r"as everyone knows", r"obviously",
            r"it's well established", r"studies show",
            r"research indicates", r"experts say",
            r"according to.*(?:wikipedia|google|internet)",
        ]
        
        # Current events and external topics
        self.forbidden_topics = {
            "politics": [
                r"president", r"election", r"congress", r"senate",
                r"democrat", r"republican", r"political party",
                r"government", r"white house", r"capitol"
            ],
            "current_events": [
                r"covid", r"coronavirus", r"pandemic",
                r"ukraine", r"russia", r"war",
                r"inflation", r"recession", r"economy",
                r"stock market", r"cryptocurrency", r"bitcoin"
            ],
            "real_time": [
                r"weather", r"temperature", r"forecast",
                r"current time", r"today's date",
                r"stock price", r"exchange rate",
                r"breaking news", r"latest news"
            ],
            "general_knowledge": [
                r"photosynthesis", r"gravity", r"evolution",
                r"history of", r"world war", r"ancient",
                r"scientific fact", r"mathematical formula",
                r"physics", r"chemistry", r"biology"
            ]
        }
        
        # Speculation indicators
        self.speculation_patterns = [
            r"i think", r"i believe", r"probably",
            r"might be", r"could be", r"perhaps",
            r"it seems", r"appears to be",
            r"my guess", r"i assume", r"likely"
        ]
        
        # Required citation patterns
        self.citation_pattern = r"\[Source:\s*([^,]+),\s*Page\s*(\d+)\]"
        
    def detect_violations(self, response: str, context: str = "") -> List[SafetyViolation]:
        """Detect all safety violations in a response"""
        violations = []
        response_lower = response.lower()
        
        # Check for external knowledge patterns
        for pattern in self.external_knowledge_patterns:
            if re.search(pattern, response_lower):
                violations.append(SafetyViolation(
                    violation_type="external_knowledge",
                    description=f"Uses external knowledge pattern: {pattern}",
                    severity="critical",
                    detected_text=pattern
                ))
        
        # Check for forbidden topics
        for topic_category, patterns in self.forbidden_topics.items():
            for pattern in patterns:
                if re.search(pattern, response_lower):
                    violations.append(SafetyViolation(
                        violation_type="forbidden_topic",
                        description=f"References forbidden topic ({topic_category}): {pattern}",
                        severity="critical",
                        detected_text=pattern
                    ))
        
        # Check for speculation
        for pattern in self.speculation_patterns:
            if re.search(pattern, response_lower):
                violations.append(SafetyViolation(
                    violation_type="speculation",
                    description=f"Contains speculation: {pattern}",
                    severity="warning",
                    detected_text=pattern
                ))
        
        # Check citation requirements
        citations = re.findall(self.citation_pattern, response)
        factual_sentences = self._extract_factual_sentences(response)
        
        if factual_sentences and not citations:
            violations.append(SafetyViolation(
                violation_type="missing_citations",
                description="Contains factual claims without citations",
                severity="critical",
                detected_text="No citations found"
            ))
        
        return violations
    
    def _extract_factual_sentences(self, text: str) -> List[str]:
        """Extract sentences that appear to make factual claims"""
        sentences = re.split(r'[.!?]+', text)
        factual_sentences = []
        
        factual_indicators = [
            r"is", r"are", r"was", r"were", r"has", r"have",
            r"according to", r"states that", r"indicates",
            r"shows", r"requires", r"allows", r"prohibits"
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Ignore very short sentences
                for indicator in factual_indicators:
                    if re.search(indicator, sentence.lower()):
                        factual_sentences.append(sentence)
                        break
        
        return factual_sentences
    
    def validate_citations(self, response: str, context_docs: List[Dict]) -> List[SafetyViolation]:
        """Validate that all citations are accurate"""
        violations = []
        citations = re.findall(self.citation_pattern, response)
        
        # Create a lookup of available documents
        available_docs = {}
        for doc in context_docs:
            filename = doc.get('metadata', {}).get('source_file', '')
            page = doc.get('metadata', {}).get('page_number', 0)
            if filename:
                if filename not in available_docs:
                    available_docs[filename] = set()
                available_docs[filename].add(page)
        
        # Validate each citation
        for filename, page_str in citations:
            try:
                page_num = int(page_str)
                if filename not in available_docs:
                    violations.append(SafetyViolation(
                        violation_type="invalid_citation",
                        description=f"Citation references non-existent document: {filename}",
                        severity="critical",
                        detected_text=f"[Source: {filename}, Page {page_str}]"
                    ))
                elif page_num not in available_docs[filename]:
                    violations.append(SafetyViolation(
                        violation_type="invalid_citation",
                        description=f"Citation references non-existent page: {filename}, Page {page_num}",
                        severity="critical",
                        detected_text=f"[Source: {filename}, Page {page_str}]"
                    ))
            except ValueError:
                violations.append(SafetyViolation(
                    violation_type="malformed_citation",
                    description=f"Invalid page number in citation: {page_str}",
                    severity="warning",
                    detected_text=f"[Source: {filename}, Page {page_str}]"
                ))
        
        return violations
    
    def is_safe_response(self, response: str, context_docs: List[Dict] = None) -> Tuple[bool, List[SafetyViolation]]:
        """Check if a response is safe to return"""
        violations = self.detect_violations(response)
        
        if context_docs:
            citation_violations = self.validate_citations(response, context_docs)
            violations.extend(citation_violations)
        
        # Check for critical violations
        critical_violations = [v for v in violations if v.severity == "critical"]
        is_safe = len(critical_violations) == 0
        
        return is_safe, violations

class ResponseFilter:
    """Filters and modifies responses to ensure safety"""
    
    def __init__(self):
        self.guard = HallucinationGuard()
        
    def filter_response(self, response: str, context_docs: List[Dict] = None) -> str:
        """Filter response to remove unsafe content"""
        is_safe, violations = self.guard.is_safe_response(response, context_docs)
        
        if not is_safe:
            logger.warning(f"Unsafe response detected with {len(violations)} violations")
            
            # For critical violations, return a safe refusal
            critical_violations = [v for v in violations if v.severity == "critical"]
            if critical_violations:
                return self._generate_safe_refusal(critical_violations)
        
        return response
    
    def _generate_safe_refusal(self, violations: List[SafetyViolation]) -> str:
        """Generate a safe refusal message based on violation types"""
        violation_types = {v.violation_type for v in violations}
        
        if "forbidden_topic" in violation_types:
            return "I don't have that information in the available company documents. I can only provide information based on the internal documents that have been uploaded to the system."
        
        if "external_knowledge" in violation_types:
            return "I can only provide information from the company documents available to me. I cannot access external information or general knowledge."
        
        if "missing_citations" in violation_types or "invalid_citation" in violation_types:
            return "I don't have enough information in the available company documents to answer that question accurately. Please check with the relevant department or refer to the specific policy document."
        
        # Default safe refusal
        return "I don't have that information in the available company documents. Please check with the relevant department for assistance."

class QueryClassifier:
    """Classifies queries to detect potentially unsafe requests"""
    
    def __init__(self):
        self.external_query_patterns = [
            # Current events
            r"who is the (current )?president",
            r"latest news", r"current events", r"breaking news",
            r"what.*(happened|happening) (today|now|recently)",
            
            # Real-time data
            r"what.*(weather|temperature)", r"stock price",
            r"current time", r"what time is it",
            
            # General knowledge
            r"how does .* work", r"what is .*\?$",
            r"explain .*", r"tell me about .*",
            r"definition of", r"meaning of",
            
            # External entities
            r"(google|microsoft|apple|amazon|facebook)",
            r"(wikipedia|internet|web)",
        ]
        
    def is_external_query(self, query: str) -> bool:
        """Check if query is asking for external knowledge"""
        query_lower = query.lower().strip()
        
        for pattern in self.external_query_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def classify_query(self, query: str) -> Dict[str, any]:
        """Classify query and return safety assessment"""
        return {
            "query": query,
            "is_external": self.is_external_query(query),
            "requires_context": not self.is_external_query(query),
            "safety_level": "safe" if not self.is_external_query(query) else "requires_review"
        }