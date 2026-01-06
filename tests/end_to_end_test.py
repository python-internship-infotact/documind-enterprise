#!/usr/bin/env python3
"""
End-to-End Integration Test for DocuMind Enterprise
Tests complete workflow from document upload to query responses
"""

import requests
import json
import time
import sys
import os
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class EndToEndTester:
    def __init__(self, backend_url: str = "http://localhost:8000", frontend_url: str = "http://localhost:8080"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.session_id = f"e2e_test_{int(time.time())}"
        self.uploaded_documents = []
    
    def create_comprehensive_test_pdf(self) -> bytes:
        """Create a comprehensive test PDF with rich content"""
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
/Kids [3 0 R 5 0 R]
/Count 2
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
/Length 400
>>
stream
BT
/F1 16 Tf
100 750 Td
(DocuMind Enterprise - Week 4 Implementation) Tj
0 -30 Td
/F1 12 Tf
(Project Overview:) Tj
0 -20 Td
(This document contains comprehensive information about the) Tj
0 -15 Td
(Week 4 implementation of DocuMind Enterprise system.) Tj
0 -30 Td
(Key Features:) Tj
0 -20 Td
(- Enhanced source metadata and citations) Tj
0 -15 Td
(- Complete Dockerization for production deployment) Tj
0 -15 Td
(- API Rate Limiting for abuse prevention) Tj
0 -15 Td
(- Comprehensive stress testing and monitoring) Tj
0 -30 Td
(Technical Implementation:) Tj
0 -20 Td
(The system uses FastAPI for the backend with Pinecone) Tj
0 -15 Td
(for vector storage and Groq for AI processing.) Tj
ET
endstream
endobj
5 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 6 0 R
>>
endobj
6 0 obj
<<
/Length 300
>>
stream
BT
/F1 14 Tf
100 750 Td
(Performance Metrics:) Tj
0 -30 Td
/F1 12 Tf
(- Sub-second Time to First Token (TTFT)) Tj
0 -15 Td
(- Real-time streaming responses) Tj
0 -15 Td
(- 100% hallucination prevention) Tj
0 -15 Td
(- Scalable architecture with Docker) Tj
0 -30 Td
(Security Features:) Tj
0 -20 Td
(- Rate limiting prevents API abuse) Tj
0 -15 Td
(- Input validation and sanitization) Tj
0 -15 Td
(- Secure document processing pipeline) Tj
0 -15 Td
(- Citation verification and source tracking) Tj
ET
endstream
endobj
xref
0 7
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
0000000656 00000 n 
0000000747 00000 n 
trailer
<<
/Size 7
/Root 1 0 R
>>
startxref
1097
%%EOF"""
        return pdf_content
    
    def test_backend_health(self) -> Dict[str, Any]:
        """Test backend health endpoint"""
        print("1. Testing Backend Health...")
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds() * 1000
            }
            if response.status_code == 200:
                result['data'] = response.json()
                print(f"   ✅ Backend healthy (Response time: {result['response_time']:.1f}ms)")
            else:
                print(f"   ❌ Backend unhealthy (Status: {response.status_code})")
            return result
        except Exception as e:
            print(f"   ❌ Backend connection failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_frontend_health(self) -> Dict[str, Any]:
        """Test frontend accessibility"""
        print("2. Testing Frontend Accessibility...")
        try:
            response = requests.get(f"{self.frontend_url}/", timeout=10)
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds() * 1000
            }
            if response.status_code == 200:
                print(f"   ✅ Frontend accessible (Response time: {result['response_time']:.1f}ms)")
            else:
                print(f"   ❌ Frontend not accessible (Status: {response.status_code})")
            return result
        except Exception as e:
            print(f"   ❌ Frontend connection failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_document_upload(self) -> Dict[str, Any]:
        """Test document upload functionality"""
        print("3. Testing Document Upload...")
        try:
            pdf_content = self.create_comprehensive_test_pdf()
            files = {'file': ('week4_test_document.pdf', pdf_content, 'application/pdf')}
            
            start_time = time.time()
            response = requests.post(f"{self.backend_url}/documents/upload", files=files, timeout=60)
            end_time = time.time()
            
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': (end_time - start_time) * 1000
            }
            
            if response.status_code == 200:
                data = response.json()
                result['data'] = data
                if data.get('success'):
                    self.uploaded_documents.append('week4_test_document.pdf')
                    print(f"   ✅ Document uploaded successfully")
                    print(f"      📄 Chunks created: {data.get('chunks_created', 0)}")
                    print(f"      ⏱️  Processing time: {data.get('processing_time', 0):.2f}s")
                else:
                    print(f"   ❌ Upload failed: {data.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ Upload request failed (Status: {response.status_code})")
                result['error'] = response.text
            
            return result
        except Exception as e:
            print(f"   ❌ Upload test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_vector_database_status(self) -> Dict[str, Any]:
        """Test vector database status"""
        print("4. Testing Vector Database Status...")
        try:
            response = requests.get(f"{self.backend_url}/stats", timeout=10)
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code
            }
            
            if response.status_code == 200:
                data = response.json()
                result['data'] = data
                vector_count = data.get('vector_database', {}).get('total_vectors', 0)
                print(f"   ✅ Vector database accessible")
                print(f"      📊 Total vectors: {vector_count}")
                print(f"      🔧 Dimension: {data.get('vector_database', {}).get('dimension', 0)}")
            else:
                print(f"   ❌ Vector database not accessible (Status: {response.status_code})")
            
            return result
        except Exception as e:
            print(f"   ❌ Vector database test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_chat_query(self, question: str) -> Dict[str, Any]:
        """Test chat query functionality"""
        print(f"5. Testing Chat Query: '{question[:50]}...'")
        try:
            payload = {
                'question': question,
                'session_id': self.session_id,
                'include_sources': True
            }
            
            start_time = time.time()
            response = requests.post(f"{self.backend_url}/chat", json=payload, timeout=30)
            end_time = time.time()
            
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': (end_time - start_time) * 1000
            }
            
            if response.status_code == 200:
                data = response.json()
                result['data'] = data
                
                if data.get('status') == 'success':
                    print(f"   ✅ Query successful")
                    print(f"      💬 Answer length: {len(data.get('answer', ''))}")
                    print(f"      📚 Sources found: {len(data.get('sources', []))}")
                    print(f"      🎯 Confidence: {data.get('confidence', 'unknown')}")
                    print(f"      ⏱️  Processing time: {data.get('processing_time', 0):.2f}s")
                elif data.get('status') == 'refused':
                    print(f"   ⚠️  Query refused: {data.get('refusal_reason', 'Unknown reason')}")
                else:
                    print(f"   ❓ Query status: {data.get('status', 'unknown')}")
            else:
                print(f"   ❌ Query failed (Status: {response.status_code})")
                result['error'] = response.text
            
            return result
        except Exception as e:
            print(f"   ❌ Query test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_streaming_query(self, question: str) -> Dict[str, Any]:
        """Test streaming query functionality"""
        print(f"6. Testing Streaming Query: '{question[:50]}...'")
        try:
            payload = {
                'question': question,
                'session_id': f"{self.session_id}_stream",
                'include_sources': True
            }
            
            start_time = time.time()
            response = requests.post(f"{self.backend_url}/chat/stream", json=payload, timeout=30, stream=True)
            
            if response.status_code != 200:
                print(f"   ❌ Streaming failed (Status: {response.status_code})")
                return {'success': False, 'status_code': response.status_code, 'error': response.text}
            
            first_token_time = None
            total_tokens = 0
            sources_count = 0
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            if data.get('type') == 'token':
                                if first_token_time is None:
                                    first_token_time = time.time() - start_time
                                total_tokens += 1
                            elif data.get('type') == 'sources':
                                sources_count = len(data.get('sources', []))
                            elif data.get('type') == 'done':
                                break
                            elif data.get('type') == 'error':
                                print(f"   ❌ Streaming error: {data.get('error', 'Unknown error')}")
                                return {'success': False, 'error': data.get('error')}
                        except json.JSONDecodeError:
                            continue
            
            end_time = time.time()
            
            result = {
                'success': True,
                'status_code': 200,
                'response_time': (end_time - start_time) * 1000,
                'ttft': first_token_time * 1000 if first_token_time else None,
                'total_tokens': total_tokens,
                'sources_count': sources_count
            }
            
            print(f"   ✅ Streaming successful")
            print(f"      ⚡ TTFT: {result['ttft']:.1f}ms" if result['ttft'] else "      ⚡ TTFT: N/A")
            print(f"      🔤 Total tokens: {total_tokens}")
            print(f"      📚 Sources: {sources_count}")
            print(f"      ⏱️  Total time: {result['response_time']:.1f}ms")
            
            return result
        except Exception as e:
            print(f"   ❌ Streaming test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting functionality"""
        print("7. Testing Rate Limiting...")
        try:
            # Make rapid requests to trigger rate limiting
            rate_limited = False
            requests_made = 0
            
            for i in range(35):  # Try to exceed the 30 requests/minute limit
                response = requests.get(f"{self.backend_url}/health", timeout=5)
                requests_made += 1
                
                if response.status_code == 429:
                    rate_limited = True
                    print(f"   ✅ Rate limiting triggered after {requests_made} requests")
                    break
                
                time.sleep(0.1)  # Small delay
            
            if not rate_limited:
                print(f"   ⚠️  Rate limiting not triggered after {requests_made} requests")
            
            return {
                'success': rate_limited,
                'requests_made': requests_made,
                'rate_limited': rate_limited
            }
        except Exception as e:
            print(f"   ❌ Rate limiting test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_document_deletion(self) -> Dict[str, Any]:
        """Test document deletion functionality"""
        print("8. Testing Document Deletion...")
        try:
            if not self.uploaded_documents:
                print("   ⚠️  No documents to delete")
                return {'success': True, 'message': 'No documents to delete'}
            
            filename = self.uploaded_documents[0]
            response = requests.delete(f"{self.backend_url}/documents/{filename}", timeout=10)
            
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code
            }
            
            if response.status_code == 200:
                print(f"   ✅ Document deleted successfully: {filename}")
                self.uploaded_documents.remove(filename)
            else:
                print(f"   ❌ Document deletion failed (Status: {response.status_code})")
                result['error'] = response.text
            
            return result
        except Exception as e:
            print(f"   ❌ Document deletion test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_end_to_end_test(self) -> Dict[str, Any]:
        """Run complete end-to-end test"""
        print("🚀 DocuMind Enterprise - End-to-End Integration Test")
        print("=" * 60)
        
        results = {}
        
        # Test sequence
        results['backend_health'] = self.test_backend_health()
        results['frontend_health'] = self.test_frontend_health()
        results['document_upload'] = self.test_document_upload()
        results['vector_database'] = self.test_vector_database_status()
        
        # Only proceed with queries if upload was successful
        if results['document_upload'].get('success'):
            results['chat_query'] = self.test_chat_query(
                "What are the key features of the Week 4 implementation?"
            )
            results['streaming_query'] = self.test_streaming_query(
                "Tell me about the performance metrics mentioned in the document."
            )
        else:
            print("   ⚠️  Skipping query tests due to upload failure")
        
        results['rate_limiting'] = self.test_rate_limiting()
        results['document_deletion'] = self.test_document_deletion()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 END-TO-END TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(results)
        successful_tests = sum(1 for result in results.values() if result.get('success', False))
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful Tests: {successful_tests}")
        print(f"Success Rate: {successful_tests/total_tests*100:.1f}%")
        
        # Detailed results
        for test_name, result in results.items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        # Overall grade
        success_rate = successful_tests / total_tests * 100
        if success_rate == 100:
            print("\n🏆 Overall Grade: EXCELLENT - All systems operational!")
        elif success_rate >= 85:
            print("\n🥈 Overall Grade: GOOD - Minor issues detected")
        elif success_rate >= 70:
            print("\n🥉 Overall Grade: ACCEPTABLE - Some issues need attention")
        else:
            print("\n⚠️  Overall Grade: NEEDS IMPROVEMENT - Critical issues detected")
        
        return results

def main():
    """Run the end-to-end test"""
    tester = EndToEndTester()
    
    try:
        results = tester.run_end_to_end_test()
        
        # Save results
        with open('e2e_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📁 Detailed results saved to: e2e_test_results.json")
        
        return results
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return None

if __name__ == "__main__":
    main()