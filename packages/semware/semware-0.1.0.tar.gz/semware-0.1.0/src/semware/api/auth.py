"""API Key authentication for SemWare."""

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger

from ..config import settings


class APIKeyBearer(HTTPBearer):
    """Custom HTTPBearer for API key authentication."""

    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        """Authenticate API key from Authorization header or X-API-Key header.

        Args:
            request: FastAPI request object

        Returns:
            API key if valid

        Raises:
            HTTPException: If authentication fails
        """
        # Try Authorization header first
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials and credentials.scheme == "Bearer":
            api_key = credentials.credentials
        else:
            # Try X-API-Key header
            api_key = request.headers.get("X-API-Key")

        if not api_key:
            logger.warning("No API key provided in request")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required. Provide it via 'Authorization: Bearer <key>' or 'X-API-Key: <key>' header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not self.verify_api_key(api_key):
            logger.warning(f"Invalid API key provided: {api_key[:8]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug("API key authentication successful")
        return api_key

    def verify_api_key(self, api_key: str) -> bool:
        """Verify if the provided API key is valid.

        Args:
            api_key: API key to verify

        Returns:
            True if valid, False otherwise
        """
        return api_key == settings.api_key


# Global API key authentication instance
api_key_auth = APIKeyBearer()


# Alternative header-based authentication for convenience
async def get_api_key_from_header(request: Request) -> str:
    """Get API key from X-API-Key header.

    Args:
        request: FastAPI request object

    Returns:
        API key if valid

    Raises:
        HTTPException: If authentication fails
    """
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        logger.warning("No X-API-Key header provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required in X-API-Key header",
        )

    if api_key != settings.api_key:
        logger.warning(f"Invalid API key in X-API-Key header: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    logger.debug("X-API-Key authentication successful")
    return api_key
