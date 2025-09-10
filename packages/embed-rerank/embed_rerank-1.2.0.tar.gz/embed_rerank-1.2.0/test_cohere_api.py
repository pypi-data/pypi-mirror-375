"""
Test script for Cohere-compatible reranking endpoints.

🚀 Testing MLX-powered Cohere compatibility!
"""

import json
import requests
import time

# Server configuration
BASE_URL = "http://localhost:11438"

def test_cohere_v1_rerank():
    """Test Cohere v1 rerank endpoint."""
    print("🧪 Testing Cohere v1 rerank endpoint...")
    
    url = f"{BASE_URL}/v1/rerank"
    payload = {
        "query": "What is machine learning?",
        "documents": [
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning uses neural networks with many layers.",
            "Natural language processing helps computers understand text.",
            "Cats are fluffy animals that like to sleep.",
            "Python is a popular programming language."
        ],
        "top_n": 3,
        "return_documents": True
    }
    
    print(f"📤 Request: POST {url}")
    print(f"📝 Payload: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    response = requests.post(url, json=payload)
    end_time = time.time()
    
    print(f"⏱️ Response time: {(end_time - start_time)*1000:.2f}ms")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Response: {json.dumps(result, indent=2)}")
        
        # Validate Cohere format
        assert "results" in result
        assert "meta" in result
        assert len(result["results"]) == 3
        
        for i, res in enumerate(result["results"]):
            assert "index" in res
            assert "relevance_score" in res
            print(f"   📄 Result {i+1}: Document {res['index']} - Score: {res['relevance_score']:.4f}")
            
        print("✅ Cohere v1 format validation passed!")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def test_cohere_v2_rerank():
    """Test Cohere v2 rerank endpoint."""
    print("\n🧪 Testing Cohere v2 rerank endpoint...")
    
    url = f"{BASE_URL}/v2/rerank"
    payload = {
        "query": "Apple Silicon performance",
        "documents": [
            "Apple Silicon chips offer exceptional performance per watt.",
            "MLX framework is optimized for Apple Silicon.",
            "Embedding models run efficiently on M1 and M2 chips.",
            "Traditional x86 processors consume more power.",
            "GPU acceleration is important for machine learning."
        ],
        "top_n": 2,
        "return_documents": False
    }
    
    print(f"📤 Request: POST {url}")
    print(f"📝 Payload: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    response = requests.post(url, json=payload)
    end_time = time.time()
    
    print(f"⏱️ Response time: {(end_time - start_time)*1000:.2f}ms")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Response: {json.dumps(result, indent=2)}")
        
        # Validate Cohere format
        assert "results" in result
        assert "meta" in result
        assert len(result["results"]) == 2
        
        for i, res in enumerate(result["results"]):
            assert "index" in res
            assert "relevance_score" in res
            # Should not have document field when return_documents=False
            assert "document" not in res
            print(f"   📄 Result {i+1}: Document {res['index']} - Score: {res['relevance_score']:.4f}")
            
        print("✅ Cohere v2 format validation passed!")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def test_performance_comparison():
    """Compare performance across different API formats."""
    print("\n⚡ Performance Comparison Test...")
    
    query = "Natural language processing and machine learning"
    documents = [
        "Natural language processing (NLP) is a branch of AI that helps computers understand human language.",
        "Machine learning algorithms can be trained on large datasets to make predictions.",
        "Deep learning is a subset of machine learning that uses neural networks.",
        "Computer vision enables machines to interpret and understand visual information.",
        "Reinforcement learning involves training agents through rewards and penalties.",
        "Statistical methods form the foundation of many machine learning techniques.",
        "Python is widely used for machine learning and data science applications.",
        "The cat sat on the mat in the sunny garden.",
        "Today is a beautiful day for going to the beach.",
        "Quantum computing could revolutionize certain computational problems."
    ]
    
    # Test different endpoints
    endpoints = [
        ("/api/v1/rerank/", {
            "query": query,
            "passages": documents,
            "top_k": 5
        }),
        ("/v1/rerank", {
            "query": query,
            "documents": documents,
            "top_n": 5
        }),
        ("/v2/rerank", {
            "query": query,
            "documents": documents,
            "top_n": 5
        })
    ]
    
    for endpoint, payload in endpoints:
        url = f"{BASE_URL}{endpoint}"
        times = []
        
        # Warm up
        requests.post(url, json=payload)
        
        # Measure performance
        for _ in range(3):
            start_time = time.time()
            response = requests.post(url, json=payload)
            end_time = time.time()
            
            if response.status_code == 200:
                times.append((end_time - start_time) * 1000)
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"   🚀 {endpoint}: {avg_time:.2f}ms average")
        else:
            print(f"   ❌ {endpoint}: Failed")


if __name__ == "__main__":
    print("🎯 Cohere API Compatibility Test Suite")
    print("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    # Test Cohere v1
    if test_cohere_v1_rerank():
        success_count += 1
    
    # Test Cohere v2  
    if test_cohere_v2_rerank():
        success_count += 1
    
    # Performance comparison
    test_performance_comparison()
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All Cohere compatibility tests passed! MLX + Cohere = ⚡")
    else:
        print("⚠️ Some tests failed. Check the server status.")
