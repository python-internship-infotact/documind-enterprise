#!/usr/bin/env python3
"""
Comprehensive stress test for DocuMind Enterprise
Tests concurrent users, rate limiting, and system stability
"""

import asyncio
import aiohttp
import time
import json
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import statistics
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StressTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            'health_checks': [],
            'uploads': [],
            'queries': [],
            'rate_limits': [],
            'errors': []
        }
    
    async def health_check(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test health endpoint"""
        start_time = time.time()
        try:
            async with session.get(f"{self.base_url}/health") as response:
                end_time = time.time()
                result = {
                    'status_code': response.status,
                    'response_time': (end_time - start_time) * 1000,
                    'success': response.status == 200
                }
                if response.status == 200:
                    result['data'] = await response.json()
                return result
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': (time.time() - start_time) * 1000,
                'success': False,
                'error': str(e)
            }
    
    async def test_upload(self, session: aiohttp.ClientSession, file_content: bytes) -> Dict[str, Any]:
        """Test document upload"""
        start_time = time.time()
        try:
            data = aiohttp.FormData()
            data.add_field('file', file_content, filename='test_doc.pdf', content_type='application/pdf')
            
            async with session.post(f"{self.base_url}/documents/upload", data=data) as response:
                end_time = time.time()
                result = {
                    'status_code': response.status,
                    'response_time': (end_time - start_time) * 1000,
                    'success': response.status == 200
                }
                if response.status in [200, 429]:  # Include rate limited responses
                    result['data'] = await response.json()
                return result
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': (time.time() - start_time) * 1000,
                'success': False,
                'error': str(e)
            }
    
    async def test_query(self, session: aiohttp.ClientSession, question: str) -> Dict[str, Any]:
        """Test chat query"""
        start_time = time.time()
        try:
            payload = {
                "question": question,
                "session_id": f"stress_test_{int(time.time())}",
                "include_sources": True
            }
            
            async with session.post(f"{self.base_url}/chat", json=payload) as response:
                end_time = time.time()
                result = {
                    'status_code': response.status,
                    'response_time': (end_time - start_time) * 1000,
                    'success': response.status == 200
                }
                if response.status in [200, 429]:
                    result['data'] = await response.json()
                return result
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': (time.time() - start_time) * 1000,
                'success': False,
                'error': str(e)
            }
    
    async def test_streaming_query(self, session: aiohttp.ClientSession, question: str) -> Dict[str, Any]:
        """Test streaming chat query"""
        start_time = time.time()
        first_token_time = None
        total_tokens = 0
        
        try:
            payload = {
                "question": question,
                "session_id": f"stress_stream_{int(time.time())}",
                "include_sources": True
            }
            
            async with session.post(f"{self.base_url}/chat/stream", json=payload) as response:
                if response.status != 200:
                    return {
                        'status_code': response.status,
                        'response_time': (time.time() - start_time) * 1000,
                        'success': False,
                        'data': await response.text()
                    }
                
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            if data.get('type') == 'token':
                                if first_token_time is None:
                                    first_token_time = time.time() - start_time
                                total_tokens += 1
                            elif data.get('type') == 'done':
                                break
                        except json.JSONDecodeError:
                            continue
                
                end_time = time.time()
                return {
                    'status_code': response.status,
                    'response_time': (end_time - start_time) * 1000,
                    'ttft': first_token_time * 1000 if first_token_time else None,
                    'tokens': total_tokens,
                    'success': True
                }
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': (time.time() - start_time) * 1000,
                'success': False,
                'error': str(e)
            }
    
    async def test_rate_limiting(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test rate limiting by making rapid requests"""
        start_time = time.time()
        requests_made = 0
        rate_limited = 0
        
        try:
            # Make rapid requests to trigger rate limiting
            for i in range(50):  # Try to exceed rate limit
                async with session.get(f"{self.base_url}/health") as response:
                    requests_made += 1
                    if response.status == 429:
                        rate_limited += 1
                        break
                await asyncio.sleep(0.1)  # Small delay
            
            return {
                'requests_made': requests_made,
                'rate_limited': rate_limited,
                'success': rate_limited > 0,  # Success if rate limiting kicked in
                'response_time': (time.time() - start_time) * 1000
            }
        except Exception as e:
            return {
                'requests_made': requests_made,
                'rate_limited': rate_limited,
                'success': False,
                'error': str(e),
                'response_time': (time.time() - start_time) * 1000
            }
    
    def create_test_pdf(self) -> bytes:
        """Create a simple test PDF"""
        # Simple PDF content
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 100
>>
stream
BT
/F1 12 Tf
100 700 Td
(Stress Test Document - Week 4 Implementation) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
356
%%EOF"""
        return pdf_content
    
    async def run_concurrent_test(self, test_func, num_concurrent: int, *args) -> List[Dict[str, Any]]:
        """Run tests concurrently"""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            tasks = [test_func(session, *args) for _ in range(num_concurrent)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append({
                        'success': False,
                        'error': str(result),
                        'response_time': 0
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
    
    async def run_stress_test(self):
        """Run comprehensive stress test"""
        print("🚀 DocuMind Enterprise - Comprehensive Stress Test")
        print("=" * 60)
        
        # Test 1: Health Check Load Test
        print("\n1. Health Check Load Test (50 concurrent requests)")
        health_results = await self.run_concurrent_test(self.health_check, 50)
        self.results['health_checks'] = health_results
        
        success_rate = sum(1 for r in health_results if r.get('success', False)) / len(health_results) * 100
        avg_response_time = statistics.mean([r.get('response_time', 0) for r in health_results])
        print(f"   ✅ Success Rate: {success_rate:.1f}%")
        print(f"   ⏱️  Average Response Time: {avg_response_time:.1f}ms")
        
        # Test 2: Upload Stress Test
        print("\n2. Upload Stress Test (10 concurrent uploads)")
        test_pdf = self.create_test_pdf()
        upload_results = await self.run_concurrent_test(self.test_upload, 10, test_pdf)
        self.results['uploads'] = upload_results
        
        upload_success_rate = sum(1 for r in upload_results if r.get('success', False)) / len(upload_results) * 100
        avg_upload_time = statistics.mean([r.get('response_time', 0) for r in upload_results])
        print(f"   ✅ Success Rate: {upload_success_rate:.1f}%")
        print(f"   ⏱️  Average Upload Time: {avg_upload_time:.1f}ms")
        
        # Test 3: Query Load Test
        print("\n3. Query Load Test (20 concurrent queries)")
        test_questions = [
            "What is this document about?",
            "What are the key features?",
            "Tell me about the implementation",
            "What is mentioned in the document?",
            "Summarize the content"
        ]
        
        query_tasks = []
        for i in range(20):
            question = test_questions[i % len(test_questions)]
            query_tasks.extend(await self.run_concurrent_test(self.test_query, 1, question))
        
        self.results['queries'] = query_tasks
        query_success_rate = sum(1 for r in query_tasks if r.get('success', False)) / len(query_tasks) * 100
        avg_query_time = statistics.mean([r.get('response_time', 0) for r in query_tasks])
        print(f"   ✅ Success Rate: {query_success_rate:.1f}%")
        print(f"   ⏱️  Average Query Time: {avg_query_time:.1f}ms")
        
        # Test 4: Streaming Performance Test
        print("\n4. Streaming Performance Test (5 concurrent streams)")
        streaming_results = await self.run_concurrent_test(
            self.test_streaming_query, 5, "What are the key features mentioned in the document?"
        )
        
        successful_streams = [r for r in streaming_results if r.get('success', False)]
        if successful_streams:
            avg_ttft = statistics.mean([r.get('ttft', 0) for r in successful_streams if r.get('ttft')])
            avg_tokens = statistics.mean([r.get('tokens', 0) for r in successful_streams])
            print(f"   ✅ Successful Streams: {len(successful_streams)}/5")
            print(f"   ⚡ Average TTFT: {avg_ttft:.1f}ms")
            print(f"   🔤 Average Tokens: {avg_tokens:.1f}")
        
        # Test 5: Rate Limiting Test
        print("\n5. Rate Limiting Test")
        rate_limit_results = await self.run_concurrent_test(self.test_rate_limiting, 3)
        self.results['rate_limits'] = rate_limit_results
        
        rate_limit_triggered = sum(1 for r in rate_limit_results if r.get('success', False))
        print(f"   🛡️  Rate Limiting Triggered: {rate_limit_triggered}/3 tests")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 STRESS TEST SUMMARY")
        print("=" * 60)
        
        total_requests = len(health_results) + len(upload_results) + len(query_tasks) + len(streaming_results)
        total_successful = (
            sum(1 for r in health_results if r.get('success', False)) +
            sum(1 for r in upload_results if r.get('success', False)) +
            sum(1 for r in query_tasks if r.get('success', False)) +
            sum(1 for r in streaming_results if r.get('success', False))
        )
        
        overall_success_rate = total_successful / total_requests * 100
        
        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {total_successful}")
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"Rate Limiting Working: {'✅ Yes' if rate_limit_triggered > 0 else '❌ No'}")
        
        # Performance grades
        if overall_success_rate >= 95:
            print("🏆 Performance Grade: EXCELLENT")
        elif overall_success_rate >= 85:
            print("🥈 Performance Grade: GOOD")
        elif overall_success_rate >= 70:
            print("🥉 Performance Grade: ACCEPTABLE")
        else:
            print("⚠️  Performance Grade: NEEDS IMPROVEMENT")
        
        return self.results

async def main():
    """Run the stress test"""
    tester = StressTester()
    
    try:
        results = await tester.run_stress_test()
        
        # Save results to file
        with open('stress_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📁 Detailed results saved to: stress_test_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️  Stress test interrupted by user")
    except Exception as e:
        print(f"\n❌ Stress test failed: {e}")
        logger.exception("Stress test error")

if __name__ == "__main__":
    asyncio.run(main())