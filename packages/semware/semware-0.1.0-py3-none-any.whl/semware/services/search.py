"""Search service for semantic search operations."""

import time

from loguru import logger

from ..models.requests import SearchResponse, SimilaritySearchRequest, TopKSearchRequest
from .embedding import embedding_service
from .vectordb import vectordb


class SearchService:
    """Service for performing semantic search operations."""

    def __init__(self):
        """Initialize the search service."""
        pass

    def similarity_search(
        self, table_name: str, request: SimilaritySearchRequest
    ) -> SearchResponse:
        """Perform similarity-based search.

        Args:
            table_name: Name of the table to search
            request: Search request parameters

        Returns:
            Search response with results
        """
        start_time = time.time()

        try:
            logger.info(
                f"Similarity search in table '{table_name}' with threshold {request.threshold}"
            )

            # Validate table exists
            vectordb.get_table_schema(table_name)

            # Generate query embedding
            logger.debug("Generating query embedding")
            query_embedding = embedding_service.generate_query_embedding(request.query)

            # Perform search
            results = vectordb.similarity_search(
                table_name=table_name,
                query_embedding=query_embedding,
                threshold=request.threshold,
                limit=request.limit,
            )

            # Sort results by similarity score (descending)
            results.sort(key=lambda x: x.similarity_score, reverse=True)

            search_time_ms = (time.time() - start_time) * 1000

            logger.info(
                f"Similarity search completed in {search_time_ms:.2f}ms, found {len(results)} results"
            )

            return SearchResponse(
                query=request.query,
                results=results,
                total_results=len(results),
                search_time_ms=search_time_ms,
            )

        except ValueError as e:
            logger.error(f"Similarity search validation error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Similarity search failed: {e}")
            raise

    def top_k_search(
        self, table_name: str, request: TopKSearchRequest
    ) -> SearchResponse:
        """Perform top-k search.

        Args:
            table_name: Name of the table to search
            request: Search request parameters

        Returns:
            Search response with results
        """
        start_time = time.time()

        try:
            logger.info(f"Top-k search in table '{table_name}' for k={request.k}")

            # Validate table exists
            vectordb.get_table_schema(table_name)

            # Generate query embedding
            logger.debug("Generating query embedding")
            query_embedding = embedding_service.generate_query_embedding(request.query)

            # Perform search
            results = vectordb.top_k_search(
                table_name=table_name, query_embedding=query_embedding, k=request.k
            )

            # Results are already sorted by similarity (descending) from LanceDB

            search_time_ms = (time.time() - start_time) * 1000

            logger.info(
                f"Top-k search completed in {search_time_ms:.2f}ms, found {len(results)} results"
            )

            return SearchResponse(
                query=request.query,
                results=results,
                total_results=len(results),
                search_time_ms=search_time_ms,
            )

        except ValueError as e:
            logger.error(f"Top-k search validation error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Top-k search failed: {e}")
            raise


# Global search service instance
search_service = SearchService()
