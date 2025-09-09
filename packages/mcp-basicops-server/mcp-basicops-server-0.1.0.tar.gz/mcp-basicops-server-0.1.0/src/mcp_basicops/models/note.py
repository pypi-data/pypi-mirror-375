"""Note-related models for BasicOps API."""

from datetime import datetime
from typing import List, Optional

from pydantic import Field, validator

from .common import Attachment, BasicOpsBaseModel, FilterParams, clean_dict


class Participant(BasicOpsBaseModel):
    """Meeting participant model."""
    
    first_name: str = Field(alias="firstName", description="Participant's first name")
    last_name: str = Field(alias="lastName", description="Participant's last name")
    email: str = Field(description="Participant's email address")


class ActionItem(BasicOpsBaseModel):
    """Action item model for meeting notes."""
    
    title: str = Field(description="Action item title/description")
    add_as_task: bool = Field(False, alias="addAsTask", description="Whether to create a task")


class NoteBase(BasicOpsBaseModel):
    """Base note model with common fields."""
    
    name: str = Field(description="Note name/title")
    content: Optional[str] = Field(None, description="Note content")
    project: Optional[int] = Field(None, description="Project ID")


class Note(NoteBase):
    """Complete note model with read-only fields."""
    
    id: int = Field(description="Note ID")
    attachments: List[Attachment] = Field(default_factory=list, description="File attachments")
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    updated: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        allow_population_by_field_name = True


class NoteCreate(NoteBase):
    """Model for creating a new note."""
    
    # Meeting-specific fields
    start_time: Optional[datetime] = Field(None, alias="startTime", description="Meeting start time")
    end_time: Optional[datetime] = Field(None, alias="endTime", description="Meeting end time")
    summary: Optional[str] = Field(None, description="Meeting summary")
    action_items: Optional[List[ActionItem]] = Field(None, alias="actionItems", description="Action items")
    participants: Optional[List[Participant]] = Field(None, description="Meeting participants")
    
    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate note name."""
        if not v or not v.strip():
            raise ValueError("Note name is required")
        return v.strip()
    
    def to_api_dict(self) -> dict:
        """Convert to API payload format."""
        data = self.dict(by_alias=True, exclude_none=True)
        return clean_dict(data)


class NoteUpdate(BasicOpsBaseModel):
    """Model for updating an existing note."""
    
    name: Optional[str] = Field(None, description="Note name/title")
    content: Optional[str] = Field(None, description="Note content")
    project: Optional[int] = Field(None, description="Project ID")
    
    @validator("name")
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate note name."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Note name cannot be empty")
        return v.strip() if v else v
    
    def to_api_dict(self) -> dict:
        """Convert to API payload format."""
        data = self.dict(by_alias=True, exclude_none=True)
        return clean_dict(data)


class NoteFilters(FilterParams):
    """Filter parameters for note queries."""
    
    project: Optional[int] = Field(None, description="Filter by project ID")
    name: Optional[str] = Field(None, description="Filter by note name")
    content: Optional[str] = Field(None, description="Search in note content")


class NoteSummary(BasicOpsBaseModel):
    """Summary view of a note for list operations."""
    
    id: int
    name: str
    content: Optional[str] = None
    project: Optional[int] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
