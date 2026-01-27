"""
User schemas for DomainSentry API.
"""
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    """Base schema for user data."""
    username: str
    email: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user."""
    email: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user data stored in database."""
    id: str
    hashed_password: str
    
    class Config:
        from_attributes = True


class User(UserBase):
    """Schema for user API response."""
    id: str
    
    class Config:
        from_attributes = True