"""Section-related models for BasicOps API."""

from datetime import datetime
from typing import Optional

from pydantic import Field, validator

from .common import BasicOpsBaseModel, FilterParams, SectionState, clean_dict


class SectionBase(BasicOpsBaseModel):
    """Base section model with common fields."""
    
    name: str = Field(description="Section name")
    project: int = Field(description="Project ID")
    end_date: Optional[datetime] = Field(None, alias="endDate", description="Section end date")
    state: Optional[SectionState] = Field(SectionState.OPEN, description="Section state")


class Section(SectionBase):
    """Complete section model with read-only fields."""
    
    id: int = Field(description="Section ID")
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    updated: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        allow_population_by_field_name = True


class SectionCreate(SectionBase):
    """Model for creating a new section."""
    
    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate section name."""
        if not v or not v.strip():
            raise ValueError("Section name is required")
        return v.strip()
    
    @validator("project")
    def validate_project(cls, v: int) -> int:
        """Validate project ID."""
        if v <= 0:
            raise ValueError("Valid project ID is required")
        return v
    
    def to_api_dict(self) -> dict:
        """Convert to API payload format."""
        data = self.dict(by_alias=True, exclude_none=True)
        return clean_dict(data)


class SectionUpdate(BasicOpsBaseModel):
    """Model for updating an existing section."""
    
    name: Optional[str] = Field(None, description="Section name")
    project: Optional[int] = Field(None, description="Project ID")
    end_date: Optional[datetime] = Field(None, alias="endDate", description="Section end date")
    state: Optional[SectionState] = Field(None, description="Section state")
    
    @validator("name")
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate section name."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Section name cannot be empty")
        return v.strip() if v else v
    
    @validator("project")
    def validate_project(cls, v: Optional[int]) -> Optional[int]:
        """Validate project ID."""
        if v is not None and v <= 0:
            raise ValueError("Valid project ID is required")
        return v
    
    def to_api_dict(self) -> dict:
        """Convert to API payload format."""
        data = self.dict(by_alias=True, exclude_none=True)
        return clean_dict(data)


class SectionFilters(FilterParams):
    """Filter parameters for section queries."""
    
    project: Optional[int] = Field(None, description="Filter by project ID")
    state: Optional[SectionState] = Field(None, description="Filter by state")
    end_date_after: Optional[datetime] = Field(None, description="Filter by end date after")
    end_date_before: Optional[datetime] = Field(None, description="Filter by end date before")


class SectionSummary(BasicOpsBaseModel):
    """Summary view of a section for list operations."""
    
    id: int
    name: str
    project: int
    end_date: Optional[datetime] = Field(None, alias="endDate")
    state: Optional[SectionState] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
