#!/usr/bin/env python3
"""Command-line interface for SemWare."""

import argparse
import sys
import uvicorn
from pathlib import Path

from .config import get_settings
from .utils.logging import setup_logging
from loguru import logger


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="semware",
        description="SemWare - Semantic Search API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  semware                          Start server with default settings
  semware --host 127.0.0.1        Start on localhost only
  semware --port 8080             Start on port 8080
  semware --workers 4             Start with 4 worker processes
  semware --debug                 Start in debug mode
  semware --reload                Start with auto-reload (development)
  
Environment variables:
  API_KEY                         API key for authentication (required)
  DEBUG                          Enable debug mode (true/false)
  DB_PATH                        Database storage path
  HOST                           Server host address
  PORT                           Server port
  LOG_LEVEL                      Logging level (DEBUG/INFO/WARNING/ERROR)
  
For more information, visit: https://github.com/your-org/semware
        """,
    )

    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Host to bind the server to (default: from config/env)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind the server to (default: from config/env)",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes (default: from config/env)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with API documentation",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development (implies --workers 1)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Set logging level (default: from config/env)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"SemWare 0.1.0",
    )

    return parser


def validate_environment() -> bool:
    """Validate that required environment is set up."""
    try:
        settings = get_settings()
        
        # Check if API key is set (not the default)
        if not settings.api_key or settings.api_key == "your-secret-api-key":
            logger.error("❌ API_KEY not configured!")
            logger.info("💡 Set your API key in .env file or environment variable:")
            logger.info("   export API_KEY=your-secret-api-key")
            logger.info("   Or create .env file from .env.example")
            return False
            
        # Check if database directory exists and is writable
        db_path = Path(settings.db_path)
        try:
            db_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            logger.error(f"❌ Cannot create database directory: {db_path}")
            logger.info("💡 Check directory permissions or set DB_PATH to writable location")
            return False
            
        logger.info(f"✅ Database directory: {db_path.absolute()}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration error: {e}")
        return False


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Load settings first
    try:
        settings = get_settings()
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Override settings with CLI arguments
    host = args.host or settings.host
    port = args.port or settings.port
    workers = args.workers or settings.workers
    debug = args.debug or settings.debug
    log_level = args.log_level or settings.log_level

    # Setup logging
    setup_logging(level=log_level)

    # Show startup banner
    print("🚀 SemWare - Semantic Search API Server")
    print("=" * 50)

    # Validate environment
    if not validate_environment():
        sys.exit(1)

    # Show configuration
    logger.info(f"📡 Starting server on http://{host}:{port}")
    logger.info(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    logger.info(f"👥 Workers: {workers}")
    logger.info(f"📝 Log level: {log_level}")
    
    if debug:
        logger.info("📚 API Documentation:")
        logger.info(f"   • Swagger UI: http://{host}:{port}/docs")
        logger.info(f"   • ReDoc: http://{host}:{port}/redoc")

    # Handle reload mode
    if args.reload:
        if workers > 1:
            logger.warning("⚠️  Auto-reload mode forces workers=1")
        workers = 1

    try:
        # Start the server
        uvicorn.run(
            "semware.main:app",
            host=host,
            port=port,
            workers=workers,
            reload=args.reload,
            log_level=log_level.lower(),
            access_log=debug,
            loop="auto",
        )
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()