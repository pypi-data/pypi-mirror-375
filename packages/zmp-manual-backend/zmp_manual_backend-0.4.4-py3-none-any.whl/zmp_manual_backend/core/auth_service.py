import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from zmp_manual_backend.models.auth import TokenData

logger = logging.getLogger("appLogger")

# JWT token URL for auth flows (used by OAuth2PasswordBearer)
TOKEN_URL = "/api/manual/v1/auth/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)


class AuthService:
    """Authentication service for handling user operations."""

    def __init__(self):
        """Initialize the auth service."""
        pass

    async def get_current_active_user(
        self, token: str = Depends(oauth2_scheme)
    ) -> TokenData:
        """
        Get the current active user from a token.
        This is a placeholder - actual token verification is handled by Keycloak.
        """
        # This method is kept for backward compatibility
        # Actual implementation is now in oauth2_keycloak.py
        logger.warning(
            "Using deprecated get_current_active_user method in auth_service.py"
        )
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Legacy JWT authentication is no longer supported. Use Keycloak OAuth2 instead.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Create a singleton instance of the auth service
auth_service = AuthService()
