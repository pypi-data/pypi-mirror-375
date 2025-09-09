"""User-related models for BasicOps API."""

from typing import List, Optional

from pydantic import Field, validator

from .common import BasicOpsBaseModel, FilterParams


class Role(BasicOpsBaseModel):
    """User role model."""
    
    id: int = Field(description="Role ID")
    name: str = Field(description="Role name")


class UserBase(BasicOpsBaseModel):
    """Base user model with common fields."""
    
    first_name: str = Field(alias="firstName", description="User's first name")
    last_name: Optional[str] = Field(None, alias="lastName", description="User's last name")
    email: Optional[str] = Field(None, description="User's email address")
    roles: List[Role] = Field(default_factory=list, description="User's roles")
    picture: Optional[str] = Field(None, description="User's profile picture URL")


class User(UserBase):
    """Complete user model with read-only fields."""
    
    id: int = Field(description="User ID")
    
    class Config:
        allow_population_by_field_name = True


class UserFilters(FilterParams):
    """Filter parameters for user queries."""
    
    name: Optional[str] = Field(None, description="Filter by name (first + last)")
    email: Optional[str] = Field(None, description="Filter by email address")
    role: Optional[int] = Field(None, description="Filter by role ID")


class UserSummary(BasicOpsBaseModel):
    """Summary view of a user for list operations."""
    
    id: int
    first_name: str = Field(alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    email: Optional[str] = None
    picture: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
