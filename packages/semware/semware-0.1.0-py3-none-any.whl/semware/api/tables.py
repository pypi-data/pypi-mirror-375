"""API endpoints for table management."""

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from ..models.requests import (
    CreateTableRequest,
    CreateTableResponse,
    GetTableResponse,
    ListTablesResponse,
)
from ..models.schemas import SuccessResponse
from ..services.vectordb import vectordb
from .auth import api_key_auth

router = APIRouter()


@router.post(
    "",
    response_model=CreateTableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new table",
    description="Create a new table with the specified schema for storing documents and embeddings.",
)
async def create_table(
    request: CreateTableRequest, api_key: str = Depends(api_key_auth)
) -> CreateTableResponse:
    """Create a new table with the specified schema."""
    try:
        logger.info(f"Creating table: {request.table_schema.name}")
        vectordb.create_table(request.table_schema)

        return CreateTableResponse(
            message=f"Table '{request.table_schema.name}' created successfully",
            table_name=request.table_schema.name,
        )

    except ValueError as e:
        logger.error(f"Table creation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error creating table: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create table",
        )


@router.get(
    "",
    response_model=ListTablesResponse,
    summary="List all tables",
    description="Get a list of all available tables in the database.",
)
async def list_tables(api_key: str = Depends(api_key_auth)) -> ListTablesResponse:
    """List all available tables."""
    try:
        logger.debug("Listing all tables")
        table_names = vectordb.get_table_names()

        return ListTablesResponse(tables=table_names, count=len(table_names))

    except Exception as e:
        logger.exception(f"Error listing tables: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list tables",
        )


@router.get(
    "/{table_name}",
    response_model=GetTableResponse,
    summary="Get table information",
    description="Get detailed information about a specific table including its schema and record count.",
)
async def get_table(
    table_name: str, api_key: str = Depends(api_key_auth)
) -> GetTableResponse:
    """Get information about a specific table."""
    try:
        logger.debug(f"Getting table info: {table_name}")

        # Get table schema
        schema = vectordb.get_table_schema(table_name)

        # Get record count
        record_count = vectordb.get_table_record_count(table_name)

        return GetTableResponse(
            table_name=table_name, table_schema=schema, record_count=record_count
        )

    except ValueError as e:
        logger.error(f"Table not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Error getting table info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get table information",
        )


@router.delete(
    "/{table_name}",
    response_model=SuccessResponse,
    summary="Delete a table",
    description="Delete a table and all its data permanently. This operation cannot be undone.",
)
async def delete_table(
    table_name: str, api_key: str = Depends(api_key_auth)
) -> SuccessResponse:
    """Delete a table and all its data."""
    try:
        logger.info(f"Deleting table: {table_name}")
        vectordb.delete_table(table_name)

        return SuccessResponse(message=f"Table '{table_name}' deleted successfully")

    except ValueError as e:
        logger.error(f"Table deletion failed: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Error deleting table: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete table",
        )
