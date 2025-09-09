"""Project-related models for BasicOps API."""

from datetime import datetime
from typing import List, Optional

from pydantic import Field, validator

from .common import BasicOpsBaseModel, FilterParams, ProjectStatus, clean_dict


class ProjectBase(BasicOpsBaseModel):
    """Base project model with common fields."""
    
    title: str = Field(description="Project title")
    description: Optional[str] = Field(None, description="Project description")
    owner: Optional[int] = Field(None, description="ID of the project owner")
    team: Optional[List[int]] = Field(None, description="List of team member IDs")
    due_date: Optional[datetime] = Field(None, alias="dueDate", description="Project due date")
    start_date: Optional[datetime] = Field(None, alias="startDate", description="Project start date")
    status: Optional[ProjectStatus] = Field(ProjectStatus.ON_TRACK, description="Project status")
    folder: Optional[int] = Field(None, description="Project group/folder ID")


class Project(ProjectBase):
    """Complete project model with read-only fields."""
    
    id: int = Field(description="Project ID")
    is_template: Optional[bool] = Field(None, alias="isTemplate", description="Whether this is a template")
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    updated: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        allow_population_by_field_name = True


class ProjectCreate(ProjectBase):
    """Model for creating a new project."""
    
    template: Optional[int] = Field(None, description="ID of project template to use")
    
    @validator("title")
    def validate_title(cls, v: str) -> str:
        """Validate project title."""
        if not v or not v.strip():
            raise ValueError("Project title is required")
        return v.strip()
    
    def to_api_dict(self) -> dict:
        """Convert to API payload format."""
        data = self.dict(by_alias=True, exclude_none=True)
        return clean_dict(data)


class ProjectUpdate(BasicOpsBaseModel):
    """Model for updating an existing project."""
    
    title: Optional[str] = Field(None, description="Project title")
    description: Optional[str] = Field(None, description="Project description")
    owner: Optional[int] = Field(None, description="ID of the project owner")
    team: Optional[List[int]] = Field(None, description="List of team member IDs")
    due_date: Optional[datetime] = Field(None, alias="dueDate", description="Project due date")
    start_date: Optional[datetime] = Field(None, alias="startDate", description="Project start date")
    status: Optional[ProjectStatus] = Field(None, description="Project status")
    folder: Optional[int] = Field(None, description="Project group/folder ID")
    
    @validator("title")
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate project title."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Project title cannot be empty")
        return v.strip() if v else v
    
    def to_api_dict(self) -> dict:
        """Convert to API payload format."""
        data = self.dict(by_alias=True, exclude_none=True)
        return clean_dict(data)


class ProjectFilters(FilterParams):
    """Filter parameters for project queries."""
    
    is_template: Optional[bool] = Field(None, description="Filter by template status")
    owner: Optional[int] = Field(None, description="Filter by owner ID")
    due_date_after: Optional[datetime] = Field(None, description="Filter by due date after")
    due_date_before: Optional[datetime] = Field(None, description="Filter by due date before")
    start_date_after: Optional[datetime] = Field(None, description="Filter by start date after")
    start_date_before: Optional[datetime] = Field(None, description="Filter by start date before")
    status: Optional[ProjectStatus] = Field(None, description="Filter by status")
    folder: Optional[int] = Field(None, description="Filter by folder ID")


class ProjectSummary(BasicOpsBaseModel):
    """Summary view of a project for list operations."""
    
    id: int
    title: str
    description: Optional[str] = None
    owner: Optional[int] = None
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    status: Optional[ProjectStatus] = None
    is_template: Optional[bool] = Field(None, alias="isTemplate")
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
