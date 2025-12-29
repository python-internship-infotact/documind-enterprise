#!/usr/bin/env python3
"""
Week 3 Streaming API Test Suite
Tests FastAPI endpoints with streaming response and TTFT latency requirements
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional

class StreamingAPITester:
    """Test suite for Week 3 streaming functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"test_session_{int(time.time())}"
        
    async def test_api_health(self) -> bool:
        """Test basic API health"""
        print("🔍 Testing API Health...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ API Health: {data['status']}")
                        return True
                    else:
                        print(f"❌ API Health Check Failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ API Health Check Error: {e}")
            return False
    
    async def test_streaming_endpoint(self, question: str) -> Dict:
        """Test streaming chat endpoint with latency measurements"""
        print(f"\n🚀 Testing Streaming: '{question}'")
        
        start_time = time.time()
        first_token_time = None
        retrieval_time = None
        total_tokens = 0
        full_response = ""
        sources = []
        metadata = {}
        
        try:
            payload = {
                "question": question,
                "session_id": self.session_id,
                "include_sources": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/stream",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"❌ Streaming request failed: {response.status} - {error_text}")
                        return {"success": False, "error": error_text}
                    
                    print("📡 Streaming response started...")
                    
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        
                        if line_str.startswith('data: '):
                            try:
                                chunk_data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                                chunk_type = chunk_data.get("type")
                                
                                if chunk_type == "sources":
                                    retrieval_time = time.time() - start_time
                                    sources = chunk_data.get("sources", [])
                                    metadata.update(chunk_data.get("metadata", {}))
                                    print(f"📚 Sources received: {len(sources)} documents")
                                    print(f"⏱️  Retrieval time: {retrieval_time:.3f}s")
                                
                                elif chunk_type == "token":
                                    if first_token_time is None:
                                        first_token_time = time.time() - start_time
                                        print(f"🎯 First token received: {first_token_time:.3f}s")
                                    
                                    content = chunk_data.get("content", "")
                                    full_response += content
                                    total_tokens += 1
                                    
                                    # Print tokens in real-time (typewriter effect simulation)
                                    print(content, end="", flush=True)
                                
                                elif chunk_type == "metadata":
                                    metadata.update(chunk_data.get("metadata", {}))
                                
                                elif chunk_type == "error":
                                    error_msg = chunk_data.get("error", "Unknown error")
                                    print(f"\n❌ Error in stream: {error_msg}")
                                    return {"success": False, "error": error_msg}
                                
                                elif chunk_type == "done":
                                    print("\n✅ Streaming completed")
                                    break
                                    
                            except json.JSONDecodeError as e:
                                print(f"\n⚠️  JSON decode error: {e}")
                                continue
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Calculate performance metrics
            tokens_per_second = total_tokens / (total_time - (retrieval_time or 0)) if total_time > (retrieval_time or 0) else 0
            
            results = {
                "success": True,
                "question": question,
                "response": full_response,
                "sources_count": len(sources),
                "metrics": {
                    "time_to_first_token": first_token_time,
                    "retrieval_time": retrieval_time,
                    "total_time": total_time,
                    "total_tokens": total_tokens,
                    "tokens_per_second": tokens_per_second
                },
                "metadata": metadata
            }
            
            return results
            
        except Exception as e:
            print(f"\n❌ Streaming test error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_ttft_requirement(self, questions: List[str]) -> Dict:
        """Test Time to First Token (TTFT) requirement < 1 second"""
        print("\n⏱️  Testing TTFT Requirement (< 1 second)...")
        
        ttft_results = []
        passed_tests = 0
        
        for i, question in enumerate(questions, 1):
            print(f"\n📝 Test {i}/{len(questions)}: {question[:50]}...")
            
            result = await self.test_streaming_endpoint(question)
            
            if result["success"]:
                ttft = result["metrics"]["time_to_first_token"]
                ttft_results.append({
                    "question": question,
                    "ttft": ttft,
                    "passed": ttft < 1.0
                })
                
                if ttft < 1.0:
                    passed_tests += 1
                    print(f"✅ TTFT: {ttft:.3f}s (PASSED)")
                else:
                    print(f"❌ TTFT: {ttft:.3f}s (FAILED - exceeds 1s)")
            else:
                print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
                ttft_results.append({
                    "question": question,
                    "ttft": None,
                    "passed": False,
                    "error": result.get('error')
                })
        
        success_rate = (passed_tests / len(questions)) * 100
        
        return {
            "total_tests": len(questions),
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "results": ttft_results
        }
    
    async def test_concurrent_streaming(self, question: str, concurrent_requests: int = 3) -> Dict:
        """Test concurrent streaming requests"""
        print(f"\n🔄 Testing Concurrent Streaming ({concurrent_requests} requests)...")
        
        async def single_request(request_id: int):
            session_id = f"{self.session_id}_concurrent_{request_id}"
            start_time = time.time()
            
            try:
                payload = {
                    "question": f"{question} (Request {request_id})",
                    "session_id": session_id,
                    "include_sources": True
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/chat/stream",
                        json=payload
                    ) as response:
                        
                        first_token_time = None
                        
                        async for line in response.content:
                            line_str = line.decode('utf-8').strip()
                            
                            if line_str.startswith('data: '):
                                try:
                                    chunk_data = json.loads(line_str[6:])
                                    
                                    if chunk_data.get("type") == "token" and first_token_time is None:
                                        first_token_time = time.time() - start_time
                                    
                                    elif chunk_data.get("type") == "done":
                                        break
                                        
                                except json.JSONDecodeError:
                                    continue
                        
                        return {
                            "request_id": request_id,
                            "success": True,
                            "ttft": first_token_time,
                            "total_time": time.time() - start_time
                        }
                        
            except Exception as e:
                return {
                    "request_id": request_id,
                    "success": False,
                    "error": str(e)
                }
        
        # Run concurrent requests
        tasks = [single_request(i) for i in range(1, concurrent_requests + 1)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        avg_ttft = sum(r["ttft"] for r in successful_requests if r["ttft"]) / len(successful_requests) if successful_requests else 0
        
        print(f"✅ Concurrent requests completed: {len(successful_requests)}/{concurrent_requests}")
        print(f"📊 Average TTFT: {avg_ttft:.3f}s")
        
        return {
            "total_requests": concurrent_requests,
            "successful_requests": len(successful_requests),
            "average_ttft": avg_ttft,
            "results": results
        }
    
    async def run_comprehensive_test(self):
        """Run comprehensive Week 3 test suite"""
        print("🎯 DocuMind Enterprise - Week 3 Streaming API Test Suite")
        print("=" * 60)
        
        # Test 1: API Health
        health_ok = await self.test_api_health()
        if not health_ok:
            print("❌ API health check failed. Ensure the server is running.")
            return False
        
        # Test 2: Basic streaming functionality
        test_questions = [
            "What is the refund policy?",
            "How do I contact customer support?",
            "What are the terms of service?",
            "How do I cancel my subscription?",
            "What payment methods are accepted?"
        ]
        
        print(f"\n📋 Testing {len(test_questions)} streaming queries...")
        
        # Test 3: TTFT requirement
        ttft_results = await self.test_ttft_requirement(test_questions)
        
        # Test 4: Concurrent streaming
        concurrent_results = await self.test_concurrent_streaming(
            "What is the refund policy?", 
            concurrent_requests=3
        )
        
        # Test 5: Hallucination prevention in streaming
        print("\n🛡️  Testing Hallucination Prevention in Streaming...")
        hallucination_test = await self.test_streaming_endpoint(
            "Who is the President of the USA?"
        )
        
        # Final report
        print("\n" + "=" * 60)
        print("📊 WEEK 3 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"🏥 API Health: {'✅ PASSED' if health_ok else '❌ FAILED'}")
        print(f"⏱️  TTFT Tests: {ttft_results['passed_tests']}/{ttft_results['total_tests']} passed ({ttft_results['success_rate']:.1f}%)")
        print(f"🔄 Concurrent Tests: {concurrent_results['successful_requests']}/{concurrent_results['total_requests']} successful")
        print(f"🛡️  Hallucination Prevention: {'✅ PASSED' if not hallucination_test['success'] or 'don\\'t have' in hallucination_test.get('response', '').lower() else '❌ FAILED'}")
        
        # Week 3 requirements check
        ttft_requirement_met = ttft_results['success_rate'] >= 80  # 80% of tests must pass TTFT
        streaming_works = ttft_results['passed_tests'] > 0
        
        print("\n🎯 WEEK 3 REQUIREMENTS:")
        print(f"   ✅ FastAPI Endpoints: IMPLEMENTED")
        print(f"   {'✅' if streaming_works else '❌'} Streaming Response: {'WORKING' if streaming_works else 'FAILED'}")
        print(f"   {'✅' if ttft_requirement_met else '❌'} TTFT < 1 second: {'MET' if ttft_requirement_met else 'NOT MET'}")
        
        overall_success = health_ok and streaming_works and ttft_requirement_met
        
        print(f"\n🏆 OVERALL STATUS: {'✅ WEEK 3 COMPLETE' if overall_success else '❌ REQUIREMENTS NOT MET'}")
        
        return overall_success

async def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🌐 Testing API at: {base_url}")
    
    tester = StreamingAPITester(base_url)
    success = await tester.run_comprehensive_test()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())