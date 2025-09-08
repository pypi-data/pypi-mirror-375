from typing import List, Optional

from pydantic import BaseModel


class TokenData(BaseModel):
    """Model for representing token data."""

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    roles: List[str] = []
    preferred_username: Optional[str] = None
    exp: Optional[int] = None
