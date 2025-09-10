"""Tests for search API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestSearchAPI:
    """Test cases for search endpoints."""

    @pytest.fixture(autouse=True)
    def setup_table_with_data(
        self,
        client: TestClient,
        api_headers: dict,
        sample_table_schema,
        sample_data_records,
    ):
        """Setup a test table with sample data."""
        # Create table
        client.post(
            "/tables",
            json={"schema": sample_table_schema.model_dump()},
            headers=api_headers,
        )

        # Insert sample data
        records = [{"data": record} for record in sample_data_records]
        client.post(
            f"/tables/{sample_table_schema.name}/data",
            json={"records": records},
            headers=api_headers,
        )

        self.table_name = sample_table_schema.name
        self.api_headers = api_headers

    def test_similarity_search_success(self, client: TestClient):
        """Test successful similarity search."""
        search_request = {
            "query": "artificial intelligence and machine learning",
            "threshold": 0.1,
            "limit": 10,
        }

        response = client.post(
            f"/tables/{self.table_name}/search/similarity",
            json=search_request,
            headers=self.api_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == search_request["query"]
        assert isinstance(data["results"], list)
        assert isinstance(data["total_results"], int)
        assert isinstance(data["search_time_ms"], float)
        assert data["search_time_ms"] > 0

        # Check result structure if any results
        if data["results"]:
            result = data["results"][0]
            assert "id" in result
            assert "data" in result
            assert "similarity_score" in result
            assert 0 <= result["similarity_score"] <= 1

    def test_similarity_search_invalid_threshold(self, client: TestClient):
        """Test similarity search with invalid threshold."""
        search_request = {
            "query": "test query",
            "threshold": 1.5,  # Invalid threshold > 1
        }

        response = client.post(
            f"/tables/{self.table_name}/search/similarity",
            json=search_request,
            headers=self.api_headers,
        )

        assert response.status_code == 422

    def test_similarity_search_invalid_table(self, client: TestClient):
        """Test similarity search on non-existent table."""
        search_request = {"query": "test query", "threshold": 0.5}

        response = client.post(
            "/tables/nonexistent/search/similarity",
            json=search_request,
            headers=self.api_headers,
        )

        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]

    def test_top_k_search_success(self, client: TestClient):
        """Test successful top-k search."""
        search_request = {"query": "programming and software development", "k": 2}

        response = client.post(
            f"/tables/{self.table_name}/search/top-k",
            json=search_request,
            headers=self.api_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == search_request["query"]
        assert isinstance(data["results"], list)
        assert len(data["results"]) <= search_request["k"]
        assert isinstance(data["total_results"], int)
        assert isinstance(data["search_time_ms"], float)
        assert data["search_time_ms"] > 0

        # Results should be sorted by similarity (descending)
        if len(data["results"]) > 1:
            scores = [r["similarity_score"] for r in data["results"]]
            assert scores == sorted(scores, reverse=True)

    def test_top_k_search_invalid_k(self, client: TestClient):
        """Test top-k search with invalid k value."""
        search_request = {"query": "test query", "k": 0}  # Invalid k <= 0

        response = client.post(
            f"/tables/{self.table_name}/search/top-k",
            json=search_request,
            headers=self.api_headers,
        )

        assert response.status_code == 422

    def test_top_k_search_large_k(self, client: TestClient):
        """Test top-k search with k larger than available records."""
        search_request = {
            "query": "test query",
            "k": 100,  # Larger than number of records
        }

        response = client.post(
            f"/tables/{self.table_name}/search/top-k",
            json=search_request,
            headers=self.api_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Should return all available records
        assert len(data["results"]) <= 3  # We only have 3 sample records

    def test_search_no_auth(self, client: TestClient):
        """Test search without authentication."""
        search_request = {"query": "test query", "threshold": 0.5}

        response = client.post(
            f"/tables/{self.table_name}/search/similarity", json=search_request
        )

        assert response.status_code == 401

    def test_search_empty_query(self, client: TestClient):
        """Test search with empty query."""
        search_request = {"query": "", "threshold": 0.5}

        response = client.post(
            f"/tables/{self.table_name}/search/similarity",
            json=search_request,
            headers=self.api_headers,
        )

        # Should still work but may return no results
        assert response.status_code == 200
