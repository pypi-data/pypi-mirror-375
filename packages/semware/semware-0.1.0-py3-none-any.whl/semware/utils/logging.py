"""Logging configuration using Loguru."""

import sys
from pathlib import Path

from loguru import logger


def setup_logging(
    level: str = "INFO",
    log_file: str | None = None,
    rotation: str = "10 MB",
    retention: str = "1 month",
    compression: str = "zip",
) -> None:
    """Setup logging configuration with Loguru.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file, if None only console logging
        rotation: Log file rotation policy
        retention: Log file retention policy
        compression: Compression for rotated files
    """
    # Remove default handler
    logger.remove()

    # Add console handler with colors
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        colorize=True,
    )

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            str(log_path),
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=True,  # For thread safety
        )

    logger.info(f"Logging configured with level: {level}")
    if log_file:
        logger.info(f"Log file: {log_file}")


def get_logger(name: str):
    """Get a logger instance for the given name.

    Args:
        name: Logger name, typically __name__

    Returns:
        Logger instance
    """
    return logger.bind(name=name)
