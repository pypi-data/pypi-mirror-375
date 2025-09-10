#!/usr/bin/env python3
"""Basic test to verify SemWare functionality."""

import os
import tempfile
from pathlib import Path

# Set test environment
os.environ["API_KEY"] = "test-api-key-123"
os.environ["DEBUG"] = "true"
os.environ["EMBEDDING_MODEL_NAME"] = "all-MiniLM-L6-v2"
os.environ["EMBEDDING_DIMENSION"] = "384"

from fastapi.testclient import TestClient
from semware.main import create_app

def main():
    print("🚀 Testing SemWare...")
    
    # Create app with test environment
    app = create_app()
    client = TestClient(app)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200, f"Health check failed: {response.json()}"
    print("✅ Health check passed")
    
    # Test 2: Create table
    print("2. Testing table creation...")
    table_schema = {
        "name": "test_docs",
        "columns": {
            "id": "string",
            "title": "string",
            "content": "string"
        },
        "id_column": "id", 
        "embedding_column": "content"
    }
    
    response = client.post(
        "/tables",
        json={"schema": table_schema},
        headers={"X-API-Key": "test-api-key-123"}
    )
    
    if response.status_code != 201:
        print(f"❌ Table creation failed: {response.status_code} - {response.json()}")
        return
    
    print("✅ Table created successfully")
    
    # Test 3: Insert data
    print("3. Testing data insertion...")
    test_data = [
        {
            "data": {
                "id": "doc1",
                "title": "Machine Learning",
                "content": "Machine learning is a method of data analysis that automates analytical model building."
            }
        }
    ]
    
    response = client.post(
        "/tables/test_docs/data",
        json={"records": test_data},
        headers={"X-API-Key": "test-api-key-123"}
    )
    
    if response.status_code != 201:
        print(f"❌ Data insertion failed: {response.status_code} - {response.json()}")
        return
    
    print("✅ Data inserted successfully")
    
    # Test 4: Search
    print("4. Testing semantic search...")
    search_request = {
        "query": "artificial intelligence",
        "k": 5
    }
    
    response = client.post(
        "/tables/test_docs/search/top-k",
        json=search_request,
        headers={"X-API-Key": "test-api-key-123"}
    )
    
    if response.status_code != 200:
        print(f"❌ Search failed: {response.status_code} - {response.json()}")
        return
    
    data = response.json()
    print(f"✅ Search completed in {data['search_time_ms']:.2f}ms, found {data['total_results']} results")
    
    if data['results']:
        best_result = data['results'][0]
        print(f"   Best match: '{best_result['data']['title']}' (similarity: {best_result['similarity_score']:.3f})")
    
    print("🎉 All tests passed! SemWare is working correctly.")

if __name__ == "__main__":
    main()