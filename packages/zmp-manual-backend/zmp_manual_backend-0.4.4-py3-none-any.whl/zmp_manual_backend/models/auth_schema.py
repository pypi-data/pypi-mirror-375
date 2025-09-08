from typing import Dict, Optional, Any

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Request model for user login."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Response model for login token."""

    access_token: str
    token_type: str = "bearer"


class ResponseModel(BaseModel):
    """Generic response model with data field."""

    result: str = "success"
    data: Optional[Dict[str, Any]] = None
