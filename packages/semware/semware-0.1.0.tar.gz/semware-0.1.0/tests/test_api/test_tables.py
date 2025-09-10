"""Tests for table management API endpoints."""

from fastapi.testclient import TestClient


class TestTablesAPI:
    """Test cases for table management endpoints."""

    def test_create_table_success(
        self, client: TestClient, api_headers: dict, sample_table_schema
    ):
        """Test successful table creation."""
        response = client.post(
            "/tables",
            json={"schema": sample_table_schema.model_dump()},
            headers=api_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert (
            data["message"]
            == f"Table '{sample_table_schema.name}' created successfully"
        )
        assert data["table_name"] == sample_table_schema.name

    def test_create_table_duplicate(
        self, client: TestClient, api_headers: dict, sample_table_schema
    ):
        """Test creating duplicate table fails."""
        # Create table first time
        client.post(
            "/tables",
            json={"schema": sample_table_schema.model_dump()},
            headers=api_headers,
        )

        # Try to create same table again
        response = client.post(
            "/tables",
            json={"schema": sample_table_schema.model_dump()},
            headers=api_headers,
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_table_invalid_schema(self, client: TestClient, api_headers: dict):
        """Test creating table with invalid schema."""
        invalid_schema = {
            "name": "invalid_table",
            "columns": {"id": "string", "content": "string"},
            "id_column": "missing_column",  # Column doesn't exist
            "embedding_column": "content",
        }

        response = client.post(
            "/tables", json={"schema": invalid_schema}, headers=api_headers
        )

        assert response.status_code == 422

    def test_create_table_no_auth(self, client: TestClient, sample_table_schema):
        """Test creating table without authentication fails."""
        response = client.post(
            "/tables", json={"schema": sample_table_schema.model_dump()}
        )

        assert response.status_code == 401

    def test_list_tables_empty(self, client: TestClient, api_headers: dict):
        """Test listing tables when none exist."""
        response = client.get("/tables", headers=api_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["tables"] == []
        assert data["count"] == 0

    def test_list_tables_with_data(
        self, client: TestClient, api_headers: dict, sample_table_schema
    ):
        """Test listing tables with existing tables."""
        # Create a table first
        client.post(
            "/tables",
            json={"schema": sample_table_schema.model_dump()},
            headers=api_headers,
        )

        response = client.get("/tables", headers=api_headers)

        assert response.status_code == 200
        data = response.json()
        assert sample_table_schema.name in data["tables"]
        assert data["count"] == 1

    def test_get_table_success(
        self, client: TestClient, api_headers: dict, sample_table_schema
    ):
        """Test getting table information."""
        # Create table first
        client.post(
            "/tables",
            json={"schema": sample_table_schema.model_dump()},
            headers=api_headers,
        )

        response = client.get(
            f"/tables/{sample_table_schema.name}", headers=api_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["table_name"] == sample_table_schema.name
        assert data["schema"]["name"] == sample_table_schema.name
        assert data["record_count"] == 0

    def test_get_table_not_found(self, client: TestClient, api_headers: dict):
        """Test getting non-existent table."""
        response = client.get("/tables/nonexistent", headers=api_headers)

        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]

    def test_delete_table_success(
        self, client: TestClient, api_headers: dict, sample_table_schema
    ):
        """Test successful table deletion."""
        # Create table first
        client.post(
            "/tables",
            json={"schema": sample_table_schema.model_dump()},
            headers=api_headers,
        )

        response = client.delete(
            f"/tables/{sample_table_schema.name}", headers=api_headers
        )

        assert response.status_code == 200
        assert (
            f"Table '{sample_table_schema.name}' deleted successfully"
            in response.json()["message"]
        )

        # Verify table is gone
        response = client.get(
            f"/tables/{sample_table_schema.name}", headers=api_headers
        )
        assert response.status_code == 404

    def test_delete_table_not_found(self, client: TestClient, api_headers: dict):
        """Test deleting non-existent table."""
        response = client.delete("/tables/nonexistent", headers=api_headers)

        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]
