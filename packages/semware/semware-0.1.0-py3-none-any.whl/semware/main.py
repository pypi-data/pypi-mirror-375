"""Main FastAPI application for SemWare."""

from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from .config import settings
from .models.requests import HealthResponse
from .models.schemas import ErrorResponse
from .utils.logging import setup_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Setup logging
    setup_logging(
        level=settings.log_level,
        log_file=settings.log_file,
    )

    # Create data directory if it doesn't exist
    settings.db_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Data directory: {settings.db_path}")

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Semantic search API server using vector databases and ML embeddings",
        debug=settings.debug,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Add middleware and exception handlers
    setup_exception_handlers(app)

    # Add routes
    setup_routes(app)

    logger.info(f"FastAPI app created: {settings.app_name} v{settings.app_version}")
    return app


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup custom exception handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle request validation errors."""
        logger.warning(f"Validation error for {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="Validation Error", detail=str(exc), error_code="VALIDATION_ERROR"
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.exception(f"Unhandled exception for {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal Server Error",
                detail="An unexpected error occurred",
                error_code="INTERNAL_ERROR",
            ).model_dump(),
        )


def setup_routes(app: FastAPI) -> None:
    """Setup API routes."""

    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            app_name=settings.app_name,
            version=settings.app_version,
            timestamp=datetime.now().isoformat(),
        )

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name} v{settings.app_version}",
            "docs_url": (
                "/docs" if settings.debug else "Documentation disabled in production"
            ),
        }

    # Import and include routers
    from .api.data import router as data_router
    from .api.search import router as search_router
    from .api.tables import router as tables_router

    app.include_router(tables_router, prefix="/tables", tags=["Tables"])
    app.include_router(data_router, prefix="/tables", tags=["Data"])
    app.include_router(search_router, prefix="/tables", tags=["Search"])


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting SemWare server on {settings.host}:{settings.port}")
    uvicorn.run(
        "semware.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
