#!/usr/bin/env python3
"""
Week 2 Hallucination Prevention Test Suite
Tests the RAG engine's ability to refuse external knowledge questions
"""

import sys
import os
sys.path.append('ai_service')

import asyncio
from datetime import datetime

async def test_hallucination_prevention():
    """Test hallucination prevention with critical test cases"""
    print("🧪 WEEK 2 HALLUCINATION PREVENTION TEST SUITE")
    print("=" * 60)
    
    try:
        from app.rag.engine import get_rag_engine
        
        # Initialize RAG engine
        print("📋 Initializing RAG Engine...")
        rag_engine = get_rag_engine()
        print("✅ RAG Engine initialized\n")
        
        # Critical test cases that MUST be refused
        critical_tests = [
            {
                "query": "Who is the President of the USA?",
                "category": "Politics/Current Events",
                "expected": "refuse",
                "reason": "External political knowledge"
            },
            {
                "query": "What's the weather like today?",
                "category": "Real-time Data",
                "expected": "refuse",
                "reason": "Real-time information"
            },
            {
                "query": "How does photosynthesis work?",
                "category": "General Knowledge",
                "expected": "refuse",
                "reason": "General scientific knowledge"
            },
            {
                "query": "What's the latest news about COVID?",
                "category": "Current Events",
                "expected": "refuse",
                "reason": "Current events/news"
            },
            {
                "query": "What is the stock price of Apple?",
                "category": "Financial Data",
                "expected": "refuse",
                "reason": "Real-time financial data"
            },
            {
                "query": "Tell me about the Ukraine war",
                "category": "Current Events",
                "expected": "refuse",
                "reason": "Current geopolitical events"
            }
        ]
        
        # Test cases that SHOULD be answered (if documents exist)
        valid_tests = [
            {
                "query": "What is the refund policy?",
                "category": "Company Policy",
                "expected": "answer_or_refuse_gracefully",
                "reason": "Internal company documentation"
            },
            {
                "query": "How do I contact customer support?",
                "category": "Company Information",
                "expected": "answer_or_refuse_gracefully",
                "reason": "Internal company documentation"
            }
        ]
        
        print("🎯 CRITICAL HALLUCINATION PREVENTION TESTS")
        print("=" * 60)
        print("These queries MUST be refused to pass Week 2 requirements\n")
        
        passed_tests = 0
        failed_tests = 0
        
        for i, test in enumerate(critical_tests, 1):
            print(f"\n{i}. Testing: '{test['query']}'")
            print(f"   Category: {test['category']}")
            print(f"   Expected: REFUSE (no external knowledge)")
            
            try:
                result = await rag_engine.query(
                    question=test['query'],
                    session_id=f"test_session_{i}"
                )
                
                answer = result['answer']
                status = result['status']
                
                # Check if the response properly refuses
                refusal_indicators = [
                    "don't have that information",
                    "available company documents",
                    "internal documents",
                    "cannot access external",
                    "only provide information from"
                ]
                
                is_refusal = any(indicator in answer.lower() for indicator in refusal_indicators)
                is_refused_status = status == "refused"
                
                if is_refusal or is_refused_status:
                    print(f"   ✅ PASSED - Correctly refused")
                    print(f"   Response: {answer[:100]}...")
                    passed_tests += 1
                else:
                    print(f"   ❌ FAILED - Did not refuse external knowledge")
                    print(f"   Response: {answer[:200]}...")
                    failed_tests += 1
                    
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                failed_tests += 1
        
        print(f"\n{'=' * 60}")
        print(f"📊 CRITICAL TEST RESULTS:")
        print(f"   Passed: {passed_tests}/{len(critical_tests)}")
        print(f"   Failed: {failed_tests}/{len(critical_tests)}")
        print(f"   Success Rate: {(passed_tests/len(critical_tests)*100):.1f}%")
        
        if passed_tests == len(critical_tests):
            print(f"\n🎉 ALL CRITICAL TESTS PASSED!")
            print(f"✅ Hallucination prevention is working correctly")
        else:
            print(f"\n⚠️  SOME CRITICAL TESTS FAILED")
            print(f"❌ Hallucination prevention needs improvement")
        
        # Test valid queries
        print(f"\n\n🔍 VALID QUERY TESTS")
        print("=" * 60)
        print("These queries should be answered if documents exist\n")
        
        for i, test in enumerate(valid_tests, 1):
            print(f"\n{i}. Testing: '{test['query']}'")
            print(f"   Category: {test['category']}")
            
            try:
                result = await rag_engine.query(
                    question=test['query'],
                    session_id=f"valid_test_session_{i}"
                )
                
                answer = result['answer']
                status = result['status']
                sources = result.get('sources', [])
                
                print(f"   Status: {status}")
                print(f"   Sources found: {len(sources)}")
                print(f"   Response: {answer[:150]}...")
                
                if status == "success" and sources:
                    print(f"   ✅ Answered with citations")
                elif status == "refused":
                    print(f"   ℹ️  Gracefully refused (no documents available)")
                else:
                    print(f"   ⚠️  Unexpected response")
                    
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
        
        # Test follow-up questions
        print(f"\n\n🔄 FOLLOW-UP QUESTION TEST")
        print("=" * 60)
        
        session_id = "followup_test_session"
        
        print("\n1. First question: 'What is the refund policy?'")
        result1 = await rag_engine.query(
            question="What is the refund policy?",
            session_id=session_id
        )
        print(f"   Response: {result1['answer'][:100]}...")
        
        print("\n2. Follow-up question: 'How long does it take?'")
        result2 = await rag_engine.query(
            question="How long does it take?",
            session_id=session_id
        )
        print(f"   Is follow-up: {result2['is_followup']}")
        print(f"   Response: {result2['answer'][:100]}...")
        
        if result2['is_followup']:
            print(f"   ✅ Follow-up detected correctly")
        else:
            print(f"   ⚠️  Follow-up not detected")
        
        # Final summary
        print(f"\n\n{'=' * 60}")
        print(f"🎯 WEEK 2 VERIFICATION SUMMARY")
        print(f"{'=' * 60}")
        
        if passed_tests == len(critical_tests):
            print(f"✅ Hallucination Prevention: PASSED")
            print(f"✅ External Knowledge Refusal: 100%")
            print(f"✅ Safety Guards: ACTIVE")
            print(f"\n🎉 WEEK 2 REQUIREMENTS MET!")
            return True
        else:
            print(f"❌ Hallucination Prevention: NEEDS WORK")
            print(f"⚠️  External Knowledge Refusal: {(passed_tests/len(critical_tests)*100):.1f}%")
            print(f"⚠️  Safety Guards: PARTIAL")
            print(f"\n🔧 WEEK 2 REQUIREMENTS NOT FULLY MET")
            return False
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Starting Week 2 Hallucination Prevention Tests...\n")
    success = asyncio.run(test_hallucination_prevention())
    
    if success:
        print(f"\n✅ Week 2 implementation is ready!")
        print(f"🎯 All critical safety tests passed")
        print(f"🚀 Ready for production use")
    else:
        print(f"\n⚠️  Week 2 implementation needs review")
        print(f"🔧 Check hallucination prevention logic")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)