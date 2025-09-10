"""LanceDB integration for vector storage and retrieval."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import lancedb
import numpy as np
import pyarrow as pa
from loguru import logger

from ..config import settings
from ..models.schemas import DataRecord, SearchResult, TableSchema


class VectorDBService:
    """Service for managing LanceDB operations."""

    def __init__(self, db_path: Path | None = None):
        """Initialize the vector database service.

        Args:
            db_path: Path to the database directory
        """
        self.db_path = db_path or settings.db_path
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Connect to LanceDB
        self.db = lancedb.connect(str(self.db_path))
        self.table_schemas: dict[str, TableSchema] = {}

        # Load existing table schemas
        self._load_table_schemas()

        logger.info(f"VectorDB initialized at: {self.db_path}")

    def _load_table_schemas(self) -> None:
        """Load table schemas from metadata."""
        schema_file = self.db_path / "table_schemas.json"
        if schema_file.exists():
            try:
                with open(schema_file) as f:
                    schemas_data = json.load(f)
                    for table_name, schema_data in schemas_data.items():
                        self.table_schemas[table_name] = TableSchema(**schema_data)
                logger.info(f"Loaded {len(self.table_schemas)} table schemas")
            except Exception as e:
                logger.error(f"Failed to load table schemas: {e}")

    def _save_table_schemas(self) -> None:
        """Save table schemas to metadata."""
        schema_file = self.db_path / "table_schemas.json"
        try:
            schemas_data = {
                name: schema.model_dump() for name, schema in self.table_schemas.items()
            }
            with open(schema_file, "w") as f:
                json.dump(schemas_data, f, indent=2)
            logger.debug("Table schemas saved")
        except Exception as e:
            logger.error(f"Failed to save table schemas: {e}")

    def _create_arrow_schema(self, table_schema: TableSchema) -> pa.Schema:
        """Create PyArrow schema from table schema.

        Args:
            table_schema: Table schema definition

        Returns:
            PyArrow schema
        """
        fields = []

        # Add all columns from schema
        for col_name, col_type in table_schema.columns.items():
            if col_type == "string":
                arrow_type = pa.string()
            elif col_type == "int":
                arrow_type = pa.int64()
            elif col_type == "float":
                arrow_type = pa.float64()
            elif col_type == "bool":
                arrow_type = pa.bool_()
            else:
                logger.warning(
                    f"Unknown column type '{col_type}', defaulting to string"
                )
                arrow_type = pa.string()

            fields.append(pa.field(col_name, arrow_type))

        # Add embedding vector column (fixed size for LanceDB vector indexing)
        fields.append(pa.field("_embedding", pa.list_(pa.float32(), settings.embedding_dimension)))

        # Add metadata columns
        fields.append(pa.field("_created_at", pa.timestamp("ms")))
        fields.append(pa.field("_updated_at", pa.timestamp("ms")))

        return pa.schema(fields)

    def _create_dummy_record(self, table_schema: TableSchema, arrow_schema: pa.Schema) -> pa.Table:
        """Create a dummy record for table initialization.
        
        Args:
            table_schema: Table schema definition
            arrow_schema: PyArrow schema
            
        Returns:
            PyArrow table with one dummy record
        """
        data = {}
        current_time = datetime.now()
        
        # Add dummy values for all columns
        for col_name, col_type in table_schema.columns.items():
            if col_type == "string":
                data[col_name] = ["dummy"]
            elif col_type == "int":
                data[col_name] = [0]
            elif col_type == "float":
                data[col_name] = [0.0]
            elif col_type == "bool":
                data[col_name] = [False]
            else:
                data[col_name] = ["dummy"]
        
        # Add dummy embedding (384 dimensions for MiniLM)
        data["_embedding"] = [[0.0] * settings.embedding_dimension]
        
        # Add metadata
        data["_created_at"] = [current_time]
        data["_updated_at"] = [current_time]
        
        return pa.table(data, schema=arrow_schema)

    def create_table(self, schema: TableSchema) -> None:
        """Create a new table with the given schema.

        Args:
            schema: Table schema definition

        Raises:
            ValueError: If table already exists
        """
        if schema.name in self.table_schemas:
            raise ValueError(f"Table '{schema.name}' already exists")

        if schema.name in self.db.table_names():
            raise ValueError(f"Table '{schema.name}' already exists in database")

        # Create arrow schema
        arrow_schema = self._create_arrow_schema(schema)

        # Create table using schema only (LanceDB will handle empty table creation)
        try:
            table = self.db.create_table(schema.name, schema=arrow_schema, mode="create")
        except Exception as e:
            logger.error(f"Failed to create table with schema-only approach: {e}")
            # Fallback: create with one dummy record then delete it
            dummy_data = self._create_dummy_record(schema, arrow_schema)
            table = self.db.create_table(schema.name, dummy_data, mode="create")
            # Delete the dummy record
            table.delete("_rowid = 0")

        # Store schema
        self.table_schemas[schema.name] = schema
        self._save_table_schemas()

        logger.info(f"Created table '{schema.name}' with {len(schema.columns)} columns")

    def delete_table(self, table_name: str) -> None:
        """Delete a table.

        Args:
            table_name: Name of the table to delete

        Raises:
            ValueError: If table doesn't exist
        """
        if table_name not in self.table_schemas:
            raise ValueError(f"Table '{table_name}' does not exist")

        # Drop the table
        self.db.drop_table(table_name)

        # Remove from schemas
        del self.table_schemas[table_name]
        self._save_table_schemas()

        logger.info(f"Deleted table '{table_name}'")

    def get_table_names(self) -> list[str]:
        """Get list of all table names.

        Returns:
            List of table names
        """
        return list(self.table_schemas.keys())

    def get_table_schema(self, table_name: str) -> TableSchema:
        """Get schema for a specific table.

        Args:
            table_name: Name of the table

        Returns:
            Table schema

        Raises:
            ValueError: If table doesn't exist
        """
        if table_name not in self.table_schemas:
            raise ValueError(f"Table '{table_name}' does not exist")

        return self.table_schemas[table_name]

    def get_table_record_count(self, table_name: str) -> int:
        """Get the number of records in a table.

        Args:
            table_name: Name of the table

        Returns:
            Number of records
        """
        if table_name not in self.table_schemas:
            raise ValueError(f"Table '{table_name}' does not exist")

        try:
            table = self.db.open_table(table_name)
            return table.count_rows()
        except Exception as e:
            logger.error(f"Failed to count rows in table '{table_name}': {e}")
            return 0

    def upsert_records(
        self, table_name: str, records: list[DataRecord], embeddings: list[np.ndarray]
    ) -> tuple[int, int]:
        """Insert or update records in a table.

        Args:
            table_name: Name of the table
            records: List of data records
            embeddings: List of embedding vectors (one per record)

        Returns:
            Tuple of (inserted_count, updated_count)

        Raises:
            ValueError: If table doesn't exist or data validation fails
        """
        if table_name not in self.table_schemas:
            raise ValueError(f"Table '{table_name}' does not exist")

        if len(records) != len(embeddings):
            raise ValueError("Number of records and embeddings must match")

        schema = self.table_schemas[table_name]
        table = self.db.open_table(table_name)

        # Prepare data for insertion
        insert_data = []
        now = datetime.now()

        for record, embedding in zip(records, embeddings, strict=False):
            # Validate record against schema
            self._validate_record(record, schema)

            # Prepare row data
            row = record.data.copy()
            row["_embedding"] = embedding.tolist()
            row["_created_at"] = now
            row["_updated_at"] = now

            insert_data.append(row)

        # Convert to PyArrow table with proper schema
        arrow_schema = self._create_arrow_schema(schema)
        
        # Convert dict data to column format
        columns_data = {}
        for field in arrow_schema:
            column_name = field.name
            if column_name == "_embedding":
                columns_data[column_name] = [row[column_name] for row in insert_data]
            else:
                columns_data[column_name] = [row[column_name] for row in insert_data]
        
        arrow_table = pa.table(columns_data, schema=arrow_schema)

        # Upsert data (merge on ID column)
        table.merge_insert(
            f"{schema.id_column}"
        ).when_matched_update_all().when_not_matched_insert_all().execute(arrow_table)

        # For now, assume all are inserts (Lance doesn't return update counts easily)
        inserted_count = len(records)
        updated_count = 0

        logger.info(f"Upserted {len(records)} records in table '{table_name}'")
        return inserted_count, updated_count

    def delete_record(self, table_name: str, record_id: str | int) -> None:
        """Delete a record from a table.

        Args:
            table_name: Name of the table
            record_id: ID of the record to delete

        Raises:
            ValueError: If table doesn't exist
        """
        if table_name not in self.table_schemas:
            raise ValueError(f"Table '{table_name}' does not exist")

        schema = self.table_schemas[table_name]
        table = self.db.open_table(table_name)

        # Delete the record
        table.delete(f"{schema.id_column} = '{record_id}'")

        logger.info(f"Deleted record with ID '{record_id}' from table '{table_name}'")

    def get_record(
        self, table_name: str, record_id: str | int
    ) -> dict[str, Any] | None:
        """Get a specific record by ID.

        Args:
            table_name: Name of the table
            record_id: ID of the record

        Returns:
            Record data or None if not found
        """
        if table_name not in self.table_schemas:
            raise ValueError(f"Table '{table_name}' does not exist")

        schema = self.table_schemas[table_name]
        table = self.db.open_table(table_name)

        try:
            result = (
                table.search().where(f"{schema.id_column} = '{record_id}'").to_pandas()
            )
            if len(result) == 0:
                return None

            # Convert first row to dict and remove internal columns
            record = result.iloc[0].to_dict()
            return {k: v for k, v in record.items() if not k.startswith("_")}
        except Exception as e:
            logger.error(
                f"Failed to get record '{record_id}' from table '{table_name}': {e}"
            )
            return None

    def similarity_search(
        self,
        table_name: str,
        query_embedding: np.ndarray,
        threshold: float,
        limit: int | None = None,
    ) -> list[SearchResult]:
        """Search for records by similarity threshold.

        Args:
            table_name: Name of the table
            query_embedding: Query embedding vector
            threshold: Minimum similarity threshold
            limit: Maximum number of results

        Returns:
            List of search results
        """
        if table_name not in self.table_schemas:
            raise ValueError(f"Table '{table_name}' does not exist")

        schema = self.table_schemas[table_name]
        table = self.db.open_table(table_name)

        try:
            # Perform vector search with explicit vector column
            search_query = table.search(query_embedding.tolist(), vector_column_name="_embedding")

            if limit:
                search_query = search_query.limit(limit)

            results = search_query.to_pandas()

            # Filter by threshold and convert to SearchResult
            search_results = []
            for _, row in results.iterrows():
                # LanceDB returns distance, convert to similarity (1 - normalized distance)
                similarity = max(0.0, min(1.0, 1.0 - row["_distance"]))

                if similarity >= threshold:
                    # Extract original data (exclude internal columns)
                    data = {k: v for k, v in row.items() if not k.startswith("_")}

                    search_results.append(
                        SearchResult(
                            id=row[schema.id_column],
                            data=data,
                            similarity_score=similarity,
                        )
                    )

            logger.info(f"Similarity search returned {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Similarity search failed for table '{table_name}': {e}")
            return []

    def top_k_search(
        self, table_name: str, query_embedding: np.ndarray, k: int
    ) -> list[SearchResult]:
        """Search for top-k most similar records.

        Args:
            table_name: Name of the table
            query_embedding: Query embedding vector
            k: Number of top results to return

        Returns:
            List of search results
        """
        if table_name not in self.table_schemas:
            raise ValueError(f"Table '{table_name}' does not exist")

        schema = self.table_schemas[table_name]
        table = self.db.open_table(table_name)

        try:
            # Perform vector search with explicit vector column
            results = table.search(query_embedding.tolist(), vector_column_name="_embedding").limit(k).to_pandas()

            # Convert to SearchResult
            search_results = []
            for _, row in results.iterrows():
                # LanceDB returns distance, convert to similarity
                similarity = max(0.0, min(1.0, 1.0 - row["_distance"]))

                # Extract original data (exclude internal columns)
                data = {k: v for k, v in row.items() if not k.startswith("_")}

                search_results.append(
                    SearchResult(
                        id=row[schema.id_column], data=data, similarity_score=similarity
                    )
                )

            logger.info(f"Top-k search returned {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Top-k search failed for table '{table_name}': {e}")
            return []

    def _validate_record(self, record: DataRecord, schema: TableSchema) -> None:
        """Validate a record against the table schema.

        Args:
            record: Data record to validate
            schema: Table schema

        Raises:
            ValueError: If validation fails
        """
        # Check if all required columns are present
        for col_name in schema.columns.keys():
            if col_name not in record.data:
                raise ValueError(f"Missing required column: {col_name}")

        # Check for extra columns
        for col_name in record.data.keys():
            if col_name not in schema.columns:
                raise ValueError(f"Unknown column: {col_name}")

        # Validate ID column
        try:
            record.get_id(schema.id_column)
        except ValueError as e:
            raise ValueError(f"Invalid ID: {e}")

        # Validate embedding column
        try:
            text = record.get_text_for_embedding(schema.embedding_column)
            if not text.strip():
                raise ValueError("Embedding column cannot be empty")
        except ValueError as e:
            raise ValueError(f"Invalid embedding column: {e}")


# Global vector database instance
vectordb = VectorDBService()
