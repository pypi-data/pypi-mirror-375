"""Embedding generation service using Google's EmbeddingGemma model."""


import numpy as np
from loguru import logger
from sentence_transformers import SentenceTransformer

from ..config import settings
from ..utils.tokenizer import tokenizer


class EmbeddingService:
    """Service for generating text embeddings using EmbeddingGemma."""

    def __init__(self, model_name: str | None = None):
        """Initialize the embedding service.

        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name or settings.embedding_model_name
        self.max_tokens_per_batch = settings.max_tokens_per_batch
        self.embedding_dimension = settings.embedding_dimension

        logger.info(f"Loading embedding model: {self.model_name}")
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            Normalized embedding vector
        """
        if not text.strip():
            logger.warning("Empty text provided for embedding")
            return np.zeros(self.embedding_dimension, dtype=np.float32)

        # Tokenize and batch the text if necessary
        batches = tokenizer.batch_text(text, self.max_tokens_per_batch)

        if not batches:
            logger.warning("No valid batches created from text")
            return np.zeros(self.embedding_dimension, dtype=np.float32)

        try:
            # Generate embeddings for each batch
            batch_embeddings = []
            for batch in batches:
                # Use encode_document for document embedding
                embedding = self.model.encode(
                    batch, convert_to_numpy=True, normalize_embeddings=False
                )
                batch_embeddings.append(embedding)

            # Combine embeddings if multiple batches
            if len(batch_embeddings) == 1:
                combined_embedding = batch_embeddings[0]
            else:
                # Average pooling for combining embeddings
                combined_embedding = np.mean(batch_embeddings, axis=0)

            # Normalize the final embedding for cosine similarity
            norm = np.linalg.norm(combined_embedding)
            if norm > 0:
                combined_embedding = combined_embedding / norm
            else:
                logger.warning("Zero norm embedding, returning zeros")
                combined_embedding = np.zeros_like(combined_embedding)

            logger.debug(f"Generated embedding with {len(batches)} batches")
            return combined_embedding.astype(np.float32)

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return np.zeros(self.embedding_dimension, dtype=np.float32)

    def generate_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of normalized embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)

        logger.info(f"Generated embeddings for {len(texts)} texts")
        return embeddings

    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for a query text.

        This method is optimized for query embeddings and uses the same
        batching strategy as document embeddings for consistency.

        Args:
            query: Query text

        Returns:
            Normalized query embedding vector
        """
        # Use the same logic as generate_embedding for consistency
        return self.generate_embedding(query)

    def compute_similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Normalize vectors if not already normalized
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            normalized1 = embedding1 / norm1
            normalized2 = embedding2 / norm2

            # Compute cosine similarity
            similarity = np.dot(normalized1, normalized2)

            # Clamp to [0, 1] range (cosine can be negative)
            similarity = max(0.0, min(1.0, (similarity + 1.0) / 2.0))

            return float(similarity)

        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            return 0.0

    def get_model_info(self) -> dict:
        """Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "max_tokens_per_batch": self.max_tokens_per_batch,
            "model_max_seq_length": getattr(self.model, "max_seq_length", "unknown"),
        }


# Global embedding service instance
embedding_service = EmbeddingService()
