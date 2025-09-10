"""Tests for data management API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestDataAPI:
    """Test cases for data management endpoints."""

    @pytest.fixture(autouse=True)
    def setup_table(self, client: TestClient, api_headers: dict, sample_table_schema):
        """Setup a test table for data operations."""
        response = client.post(
            "/tables",
            json={"schema": sample_table_schema.model_dump()},
            headers=api_headers,
        )
        print(f"Table creation response: {response.status_code} - {response.json()}")
        assert response.status_code == 201, f"Failed to create table: {response.json()}"
        
        self.table_name = sample_table_schema.name
        self.api_headers = api_headers

    def test_upsert_data_success(self, client: TestClient, sample_data_records):
        """Test successful data upsert."""
        records = [{"data": record} for record in sample_data_records[:2]]

        response = client.post(
            f"/tables/{self.table_name}/data",
            json={"records": records},
            headers=self.api_headers,
        )

        if response.status_code != 201:
            print(f"Response: {response.status_code} - {response.json()}")
        
        assert response.status_code == 201
        data = response.json()
        assert "Successfully processed" in data["message"]
        assert data["inserted_count"] == 2
        assert data["updated_count"] == 0

    def test_upsert_data_invalid_table(self, client: TestClient, sample_data_records):
        """Test upserting data to non-existent table."""
        records = [{"data": record} for record in sample_data_records[:1]]

        response = client.post(
            "/tables/nonexistent/data",
            json={"records": records},
            headers=self.api_headers,
        )

        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]

    def test_upsert_data_invalid_record(self, client: TestClient):
        """Test upserting invalid data record."""
        invalid_record = {"data": {"id": "test", "missing_required_fields": "value"}}

        response = client.post(
            f"/tables/{self.table_name}/data",
            json={"records": [invalid_record]},
            headers=self.api_headers,
        )

        assert response.status_code == 422

    def test_upsert_data_no_auth(self, client: TestClient, sample_data_records):
        """Test upserting data without authentication."""
        records = [{"data": record} for record in sample_data_records[:1]]

        response = client.post(
            f"/tables/{self.table_name}/data", json={"records": records}
        )

        assert response.status_code == 401

    def test_get_data_success(self, client: TestClient, sample_data_records):
        """Test getting data record."""
        # First insert a record
        record = sample_data_records[0]
        records = [{"data": record}]

        client.post(
            f"/tables/{self.table_name}/data",
            json={"records": records},
            headers=self.api_headers,
        )

        # Then get it
        response = client.get(
            f"/tables/{self.table_name}/data/{record['id']}", headers=self.api_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["record_id"] == record["id"]
        assert data["table_name"] == self.table_name
        assert data["data"]["title"] == record["title"]

    def test_get_data_not_found(self, client: TestClient):
        """Test getting non-existent data record."""
        response = client.get(
            f"/tables/{self.table_name}/data/nonexistent", headers=self.api_headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_delete_data_success(self, client: TestClient, sample_data_records):
        """Test deleting data record."""
        # First insert a record
        record = sample_data_records[0]
        records = [{"data": record}]

        client.post(
            f"/tables/{self.table_name}/data",
            json={"records": records},
            headers=self.api_headers,
        )

        # Then delete it
        response = client.delete(
            f"/tables/{self.table_name}/data/{record['id']}", headers=self.api_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]
        assert data["deleted_id"] == record["id"]

        # Verify it's gone
        response = client.get(
            f"/tables/{self.table_name}/data/{record['id']}", headers=self.api_headers
        )
        assert response.status_code == 404

    def test_delete_data_not_found(self, client: TestClient):
        """Test deleting non-existent data record."""
        response = client.delete(
            f"/tables/{self.table_name}/data/nonexistent", headers=self.api_headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_delete_data_invalid_table(self, client: TestClient):
        """Test deleting data from non-existent table."""
        response = client.delete(
            "/tables/nonexistent/data/some_id", headers=self.api_headers
        )

        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]
