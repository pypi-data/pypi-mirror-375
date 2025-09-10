"""Test configuration and fixtures for SemWare."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from semware.config import Settings, get_settings
from semware.main import create_app
from semware.models.schemas import TableSchema
from semware.services.vectordb import VectorDBService


@pytest.fixture(scope="function")
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        api_key="test-api-key-123",
        debug=True,
        db_path=Path(tempfile.mkdtemp()) / "test_db",
        log_level="DEBUG",
        embedding_model_name="all-MiniLM-L6-v2",
        max_tokens_per_batch=2000,
        embedding_dimension=384,
    )


@pytest.fixture(scope="function")
def client(test_settings: Settings) -> Generator[TestClient, None, None]:
    """Create test client with test settings."""
    # Create temporary directory for test database
    temp_dir = Path(tempfile.mkdtemp())
    test_settings.db_path = temp_dir / "test_db"
    
    # Monkey patch the global settings object in all modules
    import semware.config
    import semware.api.auth
    import semware.main
    import semware.services.vectordb
    import semware.services.embedding
    
    original_settings = semware.config.settings
    
    # Patch settings in all modules that import it
    semware.config.settings = test_settings
    semware.api.auth.settings = test_settings
    semware.main.settings = test_settings
    semware.services.vectordb.settings = test_settings
    semware.services.embedding.settings = test_settings
    
    # Patch the global service instances with test-specific instances
    import semware.services.vectordb
    import semware.services.embedding
    import semware.services.search
    import semware.api.data
    import semware.api.tables
    import semware.api.search
    from semware.services.vectordb import VectorDBService
    from semware.services.embedding import EmbeddingService
    from semware.services.search import SearchService
    
    original_vectordb = semware.services.vectordb.vectordb
    original_embedding_service = semware.services.embedding.embedding_service
    original_search_service = semware.services.search.search_service
    original_api_data_vectordb = semware.api.data.vectordb
    original_api_data_embedding_service = semware.api.data.embedding_service
    original_api_tables_vectordb = semware.api.tables.vectordb
    original_api_search_search_service = semware.api.search.search_service
    
    # Create new instances with test settings
    test_vectordb = VectorDBService(test_settings.db_path)
    test_embedding_service = EmbeddingService(test_settings.embedding_model_name)
    test_search_service = SearchService()
    
    # Patch the global instances in all locations
    semware.services.vectordb.vectordb = test_vectordb
    semware.services.embedding.embedding_service = test_embedding_service
    semware.services.search.search_service = test_search_service
    
    # Patch vectordb and embedding_service in the search service module
    semware.services.search.vectordb = test_vectordb
    semware.services.search.embedding_service = test_embedding_service
    
    semware.api.data.vectordb = test_vectordb
    semware.api.data.embedding_service = test_embedding_service
    semware.api.tables.vectordb = test_vectordb
    semware.api.search.search_service = test_search_service
    
    # Now import and create app with patched settings
    from semware.main import create_app
    app = create_app()
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Restore original settings in all modules
    semware.config.settings = original_settings
    semware.api.auth.settings = original_settings
    semware.main.settings = original_settings
    semware.services.vectordb.settings = original_settings
    semware.services.embedding.settings = original_settings
    
    # Restore original global service instances
    semware.services.vectordb.vectordb = original_vectordb
    semware.services.embedding.embedding_service = original_embedding_service
    semware.services.search.search_service = original_search_service
    
    # Restore original instances in search service module
    semware.services.search.vectordb = original_vectordb
    semware.services.search.embedding_service = original_embedding_service
    
    semware.api.data.vectordb = original_api_data_vectordb
    semware.api.data.embedding_service = original_api_data_embedding_service
    semware.api.tables.vectordb = original_api_tables_vectordb
    semware.api.search.search_service = original_api_search_search_service


@pytest.fixture(scope="function")
def test_vectordb(test_settings: Settings) -> Generator[VectorDBService, None, None]:
    """Create a test vector database instance."""
    # Create temporary database
    temp_dir = Path(tempfile.mkdtemp())
    db = VectorDBService(db_path=temp_dir)

    yield db

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_table_schema() -> TableSchema:
    """Create a sample table schema for testing."""
    return TableSchema(
        name="test_documents",
        columns={
            "id": "string",
            "title": "string",
            "content": "string",
            "author": "string",
            "category": "string",
        },
        id_column="id",
        embedding_column="content",
    )


@pytest.fixture
def api_headers() -> dict:
    """Get API headers with authentication."""
    return {"X-API-Key": "test-api-key-123", "Content-Type": "application/json"}


@pytest.fixture
def sample_data_records() -> list:
    """Create sample data records for testing."""
    return [
        {
            "id": "doc1",
            "title": "Introduction to Machine Learning",
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn without explicit programming.",
            "author": "John Doe",
            "category": "AI",
        },
        {
            "id": "doc2",
            "title": "Python Programming Basics",
            "content": "Python is a high-level programming language known for its simplicity and readability.",
            "author": "Jane Smith",
            "category": "Programming",
        },
        {
            "id": "doc3",
            "title": "Data Science Fundamentals",
            "content": "Data science combines statistics, computer science, and domain expertise to extract insights from data.",
            "author": "Bob Johnson",
            "category": "Data Science",
        },
    ]
