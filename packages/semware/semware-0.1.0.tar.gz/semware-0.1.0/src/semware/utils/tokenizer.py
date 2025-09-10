"""Text tokenization utilities for handling context length limits."""


import tiktoken
from loguru import logger


class TextTokenizer:
    """Handles text tokenization and batching for embedding generation."""

    def __init__(self, encoding_name: str = "cl100k_base"):
        """Initialize tokenizer.

        Args:
            encoding_name: Name of the tokenizer encoding to use
        """
        self.encoding = tiktoken.get_encoding(encoding_name)
        logger.info(f"Initialized tokenizer with encoding: {encoding_name}")

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in the text.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))

    def batch_text(self, text: str, max_tokens: int = 2000) -> list[str]:
        """Split text into batches based on token count.

        Args:
            text: Input text to batch
            max_tokens: Maximum tokens per batch

        Returns:
            List of text batches
        """
        if not text.strip():
            return []

        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)

        if total_tokens <= max_tokens:
            return [text]

        # Split tokens into batches
        batches = []
        for i in range(0, total_tokens, max_tokens):
            batch_tokens = tokens[i : i + max_tokens]
            batch_text = self.encoding.decode(batch_tokens)
            batches.append(batch_text)

        logger.debug(
            f"Split text into {len(batches)} batches ({total_tokens} total tokens)"
        )
        return batches

    def batch_texts(self, texts: list[str], max_tokens: int = 2000) -> list[list[str]]:
        """Batch multiple texts.

        Args:
            texts: List of texts to batch
            max_tokens: Maximum tokens per batch

        Returns:
            List of batches for each text
        """
        return [self.batch_text(text, max_tokens) for text in texts]


# Global tokenizer instance
tokenizer = TextTokenizer()
