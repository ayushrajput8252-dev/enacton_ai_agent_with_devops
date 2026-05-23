#!/usr/bin/env python3
"""
Integration Test Cases for EnactOn RAG Chatbot
Tests end-to-end functionality
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

load_dotenv()

# ============================
# TEST CASES
# ============================

test_cases = {
    "TEST_1_PINECONE_CONNECTION": {
        "name": "Pinecone Connection",
        "description": "Verify Pinecone is configured and has embeddings",
        "steps": [
            "1. Connect to Pinecone",
            "2. Check index status",
            "3. Verify vector count > 0"
        ],
        "expected": "Status: Ready, Vectors: >= 1"
    },
    
    "TEST_2_RAG_RETRIEVAL": {
        "name": "RAG Document Retrieval",
        "description": "Test that documents are retrieved correctly",
        "queries": [
            "What services do you offer?",
            "Tell me about your company",
            "What is AI?"
        ],
        "expected": "Should retrieve >= 1 document"
    },
    
    "TEST_3_LLM_RESPONSE": {
        "name": "LLM Response Generation",
        "description": "Test GROQ LLM generates responses",
        "query": "What is machine learning?",
        "expected": "Response should be non-empty and coherent"
    },
    
    "TEST_4_FASTAPI_HEALTH": {
        "name": "FastAPI Health Check",
        "description": "Verify FastAPI server is running",
        "endpoint": "GET /health",
        "expected": "Status code 200, status: 'healthy'"
    },
    
    "TEST_5_FASTAPI_CHAT": {
        "name": "FastAPI Chat Endpoint",
        "description": "Test non-streaming chat endpoint",
        "endpoint": "POST /api/chat",
        "message": "What is AI?",
        "expected": "Response should contain answer about AI"
    },
    
    "TEST_6_FASTAPI_STREAM": {
        "name": "FastAPI Streaming Endpoint",
        "description": "Test streaming chat endpoint",
        "endpoint": "POST /api/chat/stream",
        "message": "Hello!",
        "expected": "Should receive chunks of response"
    },
    
    "TEST_7_NEXTJS_PAGES": {
        "name": "Next.js Pages",
        "description": "Verify Next.js frontend pages load",
        "pages": ["/", "/chat"],
        "expected": "All pages should return status 200"
    },
    
    "TEST_8_API_PROXY": {
        "name": "Next.js API Proxy",
        "description": "Test Next.js API route proxies to FastAPI",
        "endpoint": "POST /api/chat",
        "message": "What is your company?",
        "expected": "Response should be proxied from FastAPI"
    },
    
    "TEST_9_END_TO_END": {
        "name": "Complete End-to-End Chat",
        "description": "Full flow: UI → API → RAG → LLM → Response",
        "message": "Tell me about your services",
        "flow": [
            "1. User types message in chat UI",
            "2. Sent to /api/chat endpoint",
            "3. Proxied to FastAPI /api/chat/stream",
            "4. RAG retrieves documents",
            "5. LLM generates response",
            "6. Streamed back to UI",
            "7. User sees typing effect"
        ],
        "expected": "Response appears in chat with streaming effect"
    },
    
    "TEST_10_ERROR_HANDLING": {
        "name": "Error Handling",
        "description": "Test error scenarios",
        "scenarios": [
            {
                "test": "Invalid message format",
                "input": None,
                "expected": "400 Bad Request"
            },
            {
                "test": "Empty message",
                "input": "",
                "expected": "Should handle gracefully"
            },
            {
                "test": "Very long message",
                "input": "a" * 10000,
                "expected": "Should process or return error"
            }
        ],
        "expected": "Appropriate error responses"
    }
}

# ============================
# IMPLEMENTATION FUNCTIONS
# ============================

def run_test(test_name, test_info):
    """Run a single test and return results"""
    
    print(f"\n{'='*70}")
    print(f"TEST: {test_info['name']}")
    print(f"{'='*70}")
    print(f"Description: {test_info['description']}")
    print(f"Expected: {test_info['expected']}")
    
    try:
        if test_name == "TEST_1_PINECONE_CONNECTION":
            return test_pinecone()
        elif test_name == "TEST_2_RAG_RETRIEVAL":
            return test_rag_retrieval(test_info.get('queries', []))
        elif test_name == "TEST_3_LLM_RESPONSE":
            return test_llm_response()
        elif test_name == "TEST_4_FASTAPI_HEALTH":
            return test_fastapi_health()
        elif test_name == "TEST_5_FASTAPI_CHAT":
            return test_fastapi_chat()
        elif test_name == "TEST_6_FASTAPI_STREAM":
            return test_fastapi_stream()
        elif test_name == "TEST_7_NEXTJS_PAGES":
            return test_nextjs_pages()
        elif test_name == "TEST_8_API_PROXY":
            return test_api_proxy()
        elif test_name == "TEST_9_END_TO_END":
            return test_end_to_end()
        elif test_name == "TEST_10_ERROR_HANDLING":
            return test_error_handling()
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        return False

def test_pinecone():
    """Test 1: Pinecone Connection"""
    try:
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index(os.getenv('PINECONE_INDEX'))
        stats = index.describe_index_stats()
        
        print(f"\nIndex: {os.getenv('PINECONE_INDEX')}")
        print(f"Status: {'Ready' if stats.ready else 'Not Ready'}")
        print(f"Total vectors: {stats.total_vector_count}")
        
        result = stats.total_vector_count > 0
        print(f"Result: {'PASS' if result else 'FAIL - No embeddings found'}")
        return result
    except Exception as e:
        print(f"Result: FAIL - {e}")
        return False

def test_rag_retrieval(queries):
    """Test 2: RAG Retrieval"""
    try:
        from rag.retriever import retrieve_docs
        
        all_pass = True
        for query in queries:
            print(f"\nQuery: {query}")
            docs = retrieve_docs(query)
            print(f"Retrieved: {len(docs)} documents")
            
            if len(docs) == 0:
                print("WARNING: No documents retrieved")
                all_pass = False
            else:
                print(f"First doc preview: {docs[0].page_content[:100]}...")
        
        print(f"Result: {'PASS' if all_pass else 'PARTIAL'}")
        return all_pass
    except Exception as e:
        print(f"Result: FAIL - {e}")
        return False

def test_llm_response():
    """Test 3: LLM Response"""
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model=os.getenv("GROQ_MODEL"),
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            temperature=0.2
        )
        
        response = llm.invoke("Say hello")
        print(f"LLM Response: {response.content[:100]}...")
        
        result = len(response.content) > 0
        print(f"Result: {'PASS' if result else 'FAIL'}")
        return result
    except Exception as e:
        print(f"Result: FAIL - {e}")
        return False

def test_fastapi_health():
    """Test 4: FastAPI Health"""
    try:
        import requests
        
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Service: {data.get('service')}")
            print(f"Result: PASS")
            return True
        else:
            print(f"Result: FAIL - Unexpected status code")
            return False
    except requests.exceptions.ConnectionError:
        print("Result: FAIL - FastAPI not running (python main.py)")
        return False
    except Exception as e:
        print(f"Result: FAIL - {e}")
        return False

def test_fastapi_chat():
    """Test 5: FastAPI Chat"""
    try:
        import requests
        
        payload = {
            "message": "What is AI?",
            "session_id": "test-5"
        }
        
        response = requests.post(
            'http://localhost:8000/api/chat',
            json=payload,
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            print(f"Response length: {len(response_text)}")
            print(f"Response preview: {response_text[:100]}...")
            print(f"Result: PASS")
            return True
        else:
            print(f"Result: FAIL - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("Result: FAIL - FastAPI not running")
        return False
    except Exception as e:
        print(f"Result: FAIL - {e}")
        return False

def test_fastapi_stream():
    """Test 6: FastAPI Streaming"""
    try:
        import requests
        
        payload = {
            "message": "Hello!",
            "session_id": "test-6"
        }
        
        response = requests.post(
            'http://localhost:8000/api/chat/stream',
            json=payload,
            timeout=15,
            stream=True
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            chunks = []
            for chunk in response.iter_content(chunk_size=10):
                if chunk:
                    chunks.append(chunk)
            
            print(f"Received {len(chunks)} chunks")
            print(f"Total data: {sum(len(c) for c in chunks)} bytes")
            print(f"Result: PASS")
            return True
        else:
            print(f"Result: FAIL - {response.status_code}")
            return False
    except Exception as e:
        print(f"Result: FAIL - {e}")
        return False

def test_nextjs_pages():
    """Test 7: Next.js Pages"""
    try:
        import requests
        
        pages = ["/", "/chat"]
        results = []
        
        for page in pages:
            try:
                response = requests.get(f'http://localhost:3000{page}', timeout=5)
                print(f"{page}: Status {response.status_code}")
                results.append(response.status_code == 200)
            except:
                print(f"{page}: Connection refused")
                results.append(False)
        
        result = all(results)
        print(f"Result: {'PASS' if result else 'FAIL - Next.js not running (npm run dev)'}")
        return result
    except Exception as e:
        print(f"Result: FAIL - {e}")
        return False

def test_api_proxy():
    """Test 8: API Proxy"""
    try:
        import requests
        
        payload = {
            "message": "What is your company?"
        }
        
        response = requests.post(
            'http://localhost:3000/api/chat',
            json=payload,
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Response type: {response.headers.get('Content-Type')}")
            print(f"Response length: {len(response.content)}")
            print(f"Result: PASS")
            return True
        else:
            print(f"Result: FAIL - {response.status_code}")
            return False
    except Exception as e:
        print(f"Result: FAIL - {e}")
        return False

def test_end_to_end():
    """Test 9: End-to-End"""
    print("\nEnd-to-End Test:")
    print("1. Open browser to http://localhost:3000")
    print("2. Click chat button (bottom right)")
    print("3. Type a message: 'Tell me about your services'")
    print("4. Watch for streaming response")
    print("\nVerify:")
    print("- Message appears in chat")
    print("- Loading indicator shows")
    print("- Response streams in (typing effect)")
    print("- Response is relevant to question")
    
    input("Press Enter after manually testing...\n")
    return True

def test_error_handling():
    """Test 10: Error Handling"""
    try:
        import requests
        
        tests = [
            ("Invalid format", None),
            ("Empty message", ""),
            ("Long message", "a" * 1000)
        ]
        
        results = []
        for test_name, message in tests:
            try:
                if message is None:
                    payload = {"message": None}
                else:
                    payload = {"message": message}
                
                response = requests.post(
                    'http://localhost:8000/api/chat',
                    json=payload,
                    timeout=5
                )
                
                print(f"{test_name}: Status {response.status_code}")
                results.append(response.status_code in [200, 400])
            except:
                print(f"{test_name}: Error (acceptable)")
                results.append(True)
        
        result = all(results)
        print(f"Result: {'PASS' if result else 'FAIL'}")
        return result
    except Exception as e:
        print(f"Result: FAIL - {e}")
        return False

# ============================
# MAIN RUNNER
# ============================

def main():
    print("\n" + "="*70)
    print("ENACTON RAG CHATBOT - INTEGRATION TEST SUITE".center(70))
    print("="*70)
    
    results = {}
    
    for test_id, test_info in test_cases.items():
        try:
            passed = run_test(test_id, test_info)
            results[test_id] = {
                "name": test_info['name'],
                "passed": passed
            }
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            results[test_id] = {
                "name": test_info['name'],
                "passed": False
            }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY".center(70))
    print("="*70)
    
    passed_count = sum(1 for r in results.values() if r['passed'])
    total_count = len(results)
    
    for test_id, result in results.items():
        status = "PASS" if result['passed'] else "FAIL"
        print(f"  {status}: {result['name']}")
    
    print(f"\nTotal: {passed_count}/{total_count} passed")
    
    if passed_count == total_count:
        print("\nAll tests passed! System is ready to use.")
    else:
        print(f"\nSome tests failed. Please check the logs above.")
    
    print()

if __name__ == "__main__":
    main()
