"""Pydantic schemas for data validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TableSchema(BaseModel):
    """Schema definition for a table."""

    name: str = Field(..., description="Name of the table")
    columns: dict[str, str] = Field(..., description="Column name to data type mapping")
    id_column: str = Field(..., description="Name of the unique identifier column")
    embedding_column: str = Field(
        ..., description="Name of the column used for embeddings"
    )

    @field_validator("embedding_column")
    @classmethod
    def validate_embedding_column(cls, v: str, info) -> str:
        """Validate that embedding column exists and is string type."""
        if hasattr(info, "data") and "columns" in info.data:
            columns = info.data["columns"]
            if v not in columns:
                raise ValueError(f"Embedding column '{v}' not found in columns")
            if columns[v] != "string":
                raise ValueError(f"Embedding column '{v}' must be of type 'string'")
        return v

    @field_validator("id_column")
    @classmethod
    def validate_id_column(cls, v: str, info) -> str:
        """Validate that ID column exists in columns."""
        if hasattr(info, "data") and "columns" in info.data:
            columns = info.data["columns"]
            if v not in columns:
                raise ValueError(f"ID column '{v}' not found in columns")
        return v


class TableInfo(BaseModel):
    """Information about a table."""

    name: str
    table_schema: TableSchema = Field(..., alias="schema")
    created_at: datetime
    record_count: int = 0
    
    model_config = {"populate_by_name": True}


class DataRecord(BaseModel):
    """A data record to be inserted/updated."""

    data: dict[str, Any] = Field(..., description="The actual data record")

    def get_id(self, id_column: str) -> str | int:
        """Get the ID value from the data record."""
        if id_column not in self.data:
            raise ValueError(f"ID column '{id_column}' not found in data")
        return self.data[id_column]

    def get_text_for_embedding(self, embedding_column: str) -> str:
        """Get the text content for embedding generation."""
        if embedding_column not in self.data:
            raise ValueError(f"Embedding column '{embedding_column}' not found in data")

        value = self.data[embedding_column]
        if not isinstance(value, str):
            raise ValueError(
                f"Embedding column '{embedding_column}' must contain string data"
            )

        return value


class SearchResult(BaseModel):
    """A search result record."""

    id: str | int
    data: dict[str, Any]
    similarity_score: float = Field(
        ..., ge=0.0, le=1.0, description="Similarity score between 0 and 1"
    )


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
    error_code: str | None = Field(
        None, description="Error code for programmatic handling"
    )


class SuccessResponse(BaseModel):
    """Standard success response."""

    message: str = Field(..., description="Success message")
    data: dict[str, Any] | None = Field(None, description="Additional response data")
