"""Request and response models for API endpoints."""


from pydantic import BaseModel, Field

from .schemas import DataRecord, SearchResult, TableSchema


# Table Management Requests
class CreateTableRequest(BaseModel):
    """Request to create a new table."""

    table_schema: TableSchema = Field(..., alias="schema", description="Table schema definition")
    
    model_config = {"populate_by_name": True}


class DeleteTableRequest(BaseModel):
    """Request to delete a table (path parameter only)."""

    pass


# Data Management Requests
class UpsertDataRequest(BaseModel):
    """Request to insert or update data records."""

    records: list[DataRecord] = Field(..., description="List of data records to upsert")


class DeleteDataRequest(BaseModel):
    """Request to delete a data record (path parameter only)."""

    pass


# Search Requests
class SimilaritySearchRequest(BaseModel):
    """Request for similarity-based search."""

    query: str = Field(..., description="Query text for semantic search")
    threshold: float = Field(
        ..., ge=0.0, le=1.0, description="Minimum similarity threshold (0.0 to 1.0)"
    )
    limit: int | None = Field(
        None, gt=0, le=1000, description="Maximum number of results to return"
    )


class TopKSearchRequest(BaseModel):
    """Request for top-k search."""

    query: str = Field(..., description="Query text for semantic search")
    k: int = Field(..., gt=0, le=1000, description="Number of top results to return")


# Response Models
class CreateTableResponse(BaseModel):
    """Response for table creation."""

    message: str = Field(..., description="Success message")
    table_name: str = Field(..., description="Name of the created table")


class ListTablesResponse(BaseModel):
    """Response for listing tables."""

    tables: list[str] = Field(..., description="List of table names")
    count: int = Field(..., description="Number of tables")


class GetTableResponse(BaseModel):
    """Response for getting table schema."""

    table_name: str = Field(..., description="Name of the table")
    table_schema: TableSchema = Field(..., alias="schema", description="Table schema")
    record_count: int = Field(..., description="Number of records in the table")
    
    model_config = {"populate_by_name": True}


class UpsertDataResponse(BaseModel):
    """Response for data upsert operation."""

    message: str = Field(..., description="Success message")
    inserted_count: int = Field(..., description="Number of new records inserted")
    updated_count: int = Field(..., description="Number of existing records updated")


class DeleteDataResponse(BaseModel):
    """Response for data deletion."""

    message: str = Field(..., description="Success message")
    deleted_id: str = Field(..., description="ID of the deleted record")


class SearchResponse(BaseModel):
    """Response for search operations."""

    query: str = Field(..., description="Original query text")
    results: list[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results returned")
    search_time_ms: float = Field(
        ..., description="Search execution time in milliseconds"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="Current timestamp")
