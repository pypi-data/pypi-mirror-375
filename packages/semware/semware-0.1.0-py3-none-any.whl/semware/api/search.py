"""API endpoints for semantic search operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from ..models.requests import SearchResponse, SimilaritySearchRequest, TopKSearchRequest
from ..services.search import search_service
from .auth import api_key_auth

router = APIRouter()


@router.post(
    "/{table_name}/search/similarity",
    response_model=SearchResponse,
    summary="Search by similarity threshold",
    description="Find all records with similarity score >= threshold. Results are sorted by similarity (descending).",
)
async def similarity_search(
    table_name: str,
    request: SimilaritySearchRequest,
    api_key: str = Depends(api_key_auth),
) -> SearchResponse:
    """Search for records by similarity threshold."""
    try:
        logger.info(f"Similarity search request for table '{table_name}'")

        result = search_service.similarity_search(table_name, request)
        return result

    except ValueError as e:
        logger.error(f"Similarity search validation error: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Similarity search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Similarity search failed",
        )


@router.post(
    "/{table_name}/search/top-k",
    response_model=SearchResponse,
    summary="Search for top-k most similar records",
    description="Find the k most similar records. Results are sorted by similarity (descending).",
)
async def top_k_search(
    table_name: str, request: TopKSearchRequest, api_key: str = Depends(api_key_auth)
) -> SearchResponse:
    """Search for top-k most similar records."""
    try:
        logger.info(f"Top-k search request for table '{table_name}'")

        result = search_service.top_k_search(table_name, request)
        return result

    except ValueError as e:
        logger.error(f"Top-k search validation error: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Top-k search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Top-k search failed",
        )
