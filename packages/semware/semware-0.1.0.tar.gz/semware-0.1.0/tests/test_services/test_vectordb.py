"""Tests for VectorDB service."""


import numpy as np
import pytest

from semware.models.schemas import DataRecord, TableSchema
from semware.services.vectordb import VectorDBService


class TestVectorDBService:
    """Test cases for VectorDB service."""

    def test_create_table(
        self, test_vectordb: VectorDBService, sample_table_schema: TableSchema
    ):
        """Test table creation."""
        test_vectordb.create_table(sample_table_schema)

        assert sample_table_schema.name in test_vectordb.get_table_names()
        schema = test_vectordb.get_table_schema(sample_table_schema.name)
        assert schema.name == sample_table_schema.name
        assert schema.columns == sample_table_schema.columns

    def test_create_duplicate_table(
        self, test_vectordb: VectorDBService, sample_table_schema: TableSchema
    ):
        """Test creating duplicate table raises error."""
        test_vectordb.create_table(sample_table_schema)

        with pytest.raises(ValueError, match="already exists"):
            test_vectordb.create_table(sample_table_schema)

    def test_delete_table(
        self, test_vectordb: VectorDBService, sample_table_schema: TableSchema
    ):
        """Test table deletion."""
        test_vectordb.create_table(sample_table_schema)
        assert sample_table_schema.name in test_vectordb.get_table_names()

        test_vectordb.delete_table(sample_table_schema.name)
        assert sample_table_schema.name not in test_vectordb.get_table_names()

    def test_delete_nonexistent_table(self, test_vectordb: VectorDBService):
        """Test deleting non-existent table raises error."""
        with pytest.raises(ValueError, match="does not exist"):
            test_vectordb.delete_table("nonexistent")

    def test_get_table_schema_nonexistent(self, test_vectordb: VectorDBService):
        """Test getting schema for non-existent table raises error."""
        with pytest.raises(ValueError, match="does not exist"):
            test_vectordb.get_table_schema("nonexistent")

    def test_upsert_records(
        self,
        test_vectordb: VectorDBService,
        sample_table_schema: TableSchema,
        sample_data_records: list,
    ):
        """Test record upsert operation."""
        # Create table
        test_vectordb.create_table(sample_table_schema)

        # Prepare records and embeddings
        records = [DataRecord(data=record) for record in sample_data_records[:2]]
        embeddings = [np.random.rand(384).astype(np.float32) for _ in records]

        # Upsert records
        inserted, updated = test_vectordb.upsert_records(
            sample_table_schema.name, records, embeddings
        )

        assert inserted == 2
        assert updated == 0
        assert test_vectordb.get_table_record_count(sample_table_schema.name) >= 2

    def test_upsert_records_invalid_table(
        self, test_vectordb: VectorDBService, sample_data_records: list
    ):
        """Test upserting to non-existent table raises error."""
        records = [DataRecord(data=sample_data_records[0])]
        embeddings = [np.random.rand(384).astype(np.float32)]

        with pytest.raises(ValueError, match="does not exist"):
            test_vectordb.upsert_records("nonexistent", records, embeddings)

    def test_upsert_records_mismatched_lengths(
        self,
        test_vectordb: VectorDBService,
        sample_table_schema: TableSchema,
        sample_data_records: list,
    ):
        """Test upserting with mismatched record/embedding counts raises error."""
        test_vectordb.create_table(sample_table_schema)

        records = [DataRecord(data=sample_data_records[0])]
        embeddings = [
            np.random.rand(384).astype(np.float32),
            np.random.rand(384).astype(np.float32),
        ]

        with pytest.raises(ValueError, match="must match"):
            test_vectordb.upsert_records(sample_table_schema.name, records, embeddings)

    def test_get_record(
        self,
        test_vectordb: VectorDBService,
        sample_table_schema: TableSchema,
        sample_data_records: list,
    ):
        """Test getting a specific record."""
        # Create table and insert record
        test_vectordb.create_table(sample_table_schema)

        record = DataRecord(data=sample_data_records[0])
        embedding = np.random.rand(384).astype(np.float32)
        test_vectordb.upsert_records(sample_table_schema.name, [record], [embedding])

        # Get the record
        retrieved = test_vectordb.get_record(
            sample_table_schema.name, record.data["id"]
        )

        assert retrieved is not None
        assert retrieved["title"] == record.data["title"]
        assert retrieved["content"] == record.data["content"]

    def test_get_nonexistent_record(
        self, test_vectordb: VectorDBService, sample_table_schema: TableSchema
    ):
        """Test getting non-existent record returns None."""
        test_vectordb.create_table(sample_table_schema)

        retrieved = test_vectordb.get_record(sample_table_schema.name, "nonexistent")
        assert retrieved is None

    def test_delete_record(
        self,
        test_vectordb: VectorDBService,
        sample_table_schema: TableSchema,
        sample_data_records: list,
    ):
        """Test deleting a specific record."""
        # Create table and insert record
        test_vectordb.create_table(sample_table_schema)

        record = DataRecord(data=sample_data_records[0])
        embedding = np.random.rand(384).astype(np.float32)
        test_vectordb.upsert_records(sample_table_schema.name, [record], [embedding])

        # Verify record exists
        retrieved = test_vectordb.get_record(
            sample_table_schema.name, record.data["id"]
        )
        assert retrieved is not None

        # Delete the record
        test_vectordb.delete_record(sample_table_schema.name, record.data["id"])

        # Verify record is gone
        retrieved = test_vectordb.get_record(
            sample_table_schema.name, record.data["id"]
        )
        assert retrieved is None

    def test_validate_record_missing_column(
        self, test_vectordb: VectorDBService, sample_table_schema: TableSchema
    ):
        """Test record validation with missing column."""
        invalid_data = {"id": "test", "title": "Test"}  # Missing required columns
        record = DataRecord(data=invalid_data)

        with pytest.raises(ValueError, match="Missing required column"):
            test_vectordb._validate_record(record, sample_table_schema)

    def test_validate_record_extra_column(
        self, test_vectordb: VectorDBService, sample_table_schema: TableSchema
    ):
        """Test record validation with extra column."""
        invalid_data = {
            "id": "test",
            "title": "Test",
            "content": "Test content",
            "author": "Test author",
            "category": "Test",
            "extra_field": "Should not be here",
        }
        record = DataRecord(data=invalid_data)

        with pytest.raises(ValueError, match="Unknown column"):
            test_vectordb._validate_record(record, sample_table_schema)
