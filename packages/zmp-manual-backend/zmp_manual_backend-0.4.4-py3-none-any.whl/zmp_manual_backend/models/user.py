from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base model for user data."""

    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserRead(UserBase):
    """Model for user data returned from API."""

    id: Optional[str] = Field(None, description="User ID (subject identifier)")
    roles: Optional[List[str]] = Field(default_factory=list, description="User roles")

    class Config:
        from_attributes = True
