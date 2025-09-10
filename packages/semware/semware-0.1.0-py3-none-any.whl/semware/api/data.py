"""API endpoints for data operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from ..models.requests import DeleteDataResponse, UpsertDataRequest, UpsertDataResponse
from ..services.embedding import embedding_service
from ..services.vectordb import vectordb
from .auth import api_key_auth

router = APIRouter()


@router.post(
    "/{table_name}/data",
    response_model=UpsertDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Insert or update data records",
    description="Insert new records or update existing ones in the specified table. Embeddings are automatically generated.",
)
async def upsert_data(
    table_name: str, request: UpsertDataRequest, api_key: str = Depends(api_key_auth)
) -> UpsertDataResponse:
    """Insert or update data records in a table."""
    try:
        logger.info(f"Upserting {len(request.records)} records in table: {table_name}")

        # Get table schema
        try:
            schema = vectordb.get_table_schema(table_name)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        # Validate all records first
        texts_for_embedding = []
        for i, record in enumerate(request.records):
            try:
                # Validate record structure
                vectordb._validate_record(record, schema)

                # Extract text for embedding
                text = record.get_text_for_embedding(schema.embedding_column)
                texts_for_embedding.append(text)

            except ValueError as e:
                logger.error(f"Record {i} validation failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Record {i}: {str(e)}",
                )

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts_for_embedding)} records")
        embeddings = embedding_service.generate_embeddings(texts_for_embedding)

        # Upsert records with embeddings
        inserted_count, updated_count = vectordb.upsert_records(
            table_name, request.records, embeddings
        )

        return UpsertDataResponse(
            message=f"Successfully processed {len(request.records)} records",
            inserted_count=inserted_count,
            updated_count=updated_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error upserting data in table '{table_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upsert data",
        )


@router.delete(
    "/{table_name}/data/{record_id}",
    response_model=DeleteDataResponse,
    summary="Delete a data record",
    description="Delete a specific record from the table by its ID.",
)
async def delete_data(
    table_name: str, record_id: str, api_key: str = Depends(api_key_auth)
) -> DeleteDataResponse:
    """Delete a data record from a table."""
    try:
        logger.info(f"Deleting record '{record_id}' from table: {table_name}")

        # Check if table exists
        try:
            vectordb.get_table_schema(table_name)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        # Check if record exists
        existing_record = vectordb.get_record(table_name, record_id)
        if existing_record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Record with ID '{record_id}' not found in table '{table_name}'",
            )

        # Delete the record
        vectordb.delete_record(table_name, record_id)

        return DeleteDataResponse(
            message="Record deleted successfully", deleted_id=record_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"Error deleting record '{record_id}' from table '{table_name}': {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete record",
        )


@router.get(
    "/{table_name}/data/{record_id}",
    summary="Get a data record",
    description="Retrieve a specific record from the table by its ID.",
)
async def get_data(
    table_name: str, record_id: str, api_key: str = Depends(api_key_auth)
) -> dict:
    """Get a data record from a table."""
    try:
        logger.debug(f"Getting record '{record_id}' from table: {table_name}")

        # Check if table exists
        try:
            vectordb.get_table_schema(table_name)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        # Get the record
        record = vectordb.get_record(table_name, record_id)

        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Record with ID '{record_id}' not found in table '{table_name}'",
            )

        return {"table_name": table_name, "record_id": record_id, "data": record}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"Error getting record '{record_id}' from table '{table_name}': {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get record",
        )
