"""Tests for tokenizer utility."""

from semware.utils.tokenizer import TextTokenizer


class TestTextTokenizer:
    """Test cases for TextTokenizer."""

    def test_count_tokens(self):
        """Test token counting."""
        tokenizer = TextTokenizer()

        # Simple text
        text = "Hello world"
        count = tokenizer.count_tokens(text)
        assert count > 0
        assert isinstance(count, int)

        # Empty text
        empty_count = tokenizer.count_tokens("")
        assert empty_count == 0

    def test_batch_text_short(self):
        """Test batching short text."""
        tokenizer = TextTokenizer()

        short_text = "This is a short text that should not be batched."
        batches = tokenizer.batch_text(short_text, max_tokens=1000)

        assert len(batches) == 1
        assert batches[0] == short_text

    def test_batch_text_long(self):
        """Test batching long text."""
        tokenizer = TextTokenizer()

        # Create a long text by repeating
        long_text = "This is a sentence that will be repeated many times. " * 100
        batches = tokenizer.batch_text(long_text, max_tokens=50)

        # Should create multiple batches
        assert len(batches) > 1

        # Each batch should be a string
        for batch in batches:
            assert isinstance(batch, str)
            assert len(batch) > 0

    def test_batch_text_empty(self):
        """Test batching empty text."""
        tokenizer = TextTokenizer()

        batches = tokenizer.batch_text("", max_tokens=100)
        assert batches == []

        batches = tokenizer.batch_text("   ", max_tokens=100)
        assert batches == []

    def test_batch_texts_multiple(self):
        """Test batching multiple texts."""
        tokenizer = TextTokenizer()

        texts = ["First text", "Second text that is a bit longer", "Third text"]

        batches_list = tokenizer.batch_texts(texts, max_tokens=100)

        assert len(batches_list) == 3
        for batches in batches_list:
            assert isinstance(batches, list)
            assert len(batches) >= 1

    def test_token_count_consistency(self):
        """Test that token counting is consistent."""
        tokenizer = TextTokenizer()

        text = "Machine learning is a subset of artificial intelligence."

        # Count tokens directly
        direct_count = tokenizer.count_tokens(text)

        # Count tokens through batching
        batches = tokenizer.batch_text(text, max_tokens=1000)
        batch_tokens = sum(tokenizer.count_tokens(batch) for batch in batches)

        # Should be approximately equal (some variance due to tokenizer behavior)
        assert abs(direct_count - batch_tokens) <= 2
