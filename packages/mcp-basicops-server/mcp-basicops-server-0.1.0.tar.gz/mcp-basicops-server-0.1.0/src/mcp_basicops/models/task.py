"""Task-related models for BasicOps API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field, validator

from .common import Attachment, BasicOpsBaseModel, FilterParams, TaskStatus, clean_dict


class TaskBase(BasicOpsBaseModel):
    """Base task model with common fields."""
    
    title: str = Field(description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    project: Optional[int] = Field(None, description="Project ID")
    section: Optional[int] = Field(None, description="Section ID")
    assignee: Optional[int] = Field(None, description="Assignee user ID")
    due_date: Optional[datetime] = Field(None, alias="dueDate", description="Task due date")
    status: Optional[TaskStatus] = Field(TaskStatus.NEW, description="Task status")


class Task(TaskBase):
    """Complete task model with read-only fields."""
    
    id: int = Field(description="Task ID")
    attachments: List[Attachment] = Field(default_factory=list, description="File attachments")
    project_info: Optional[Dict[str, Any]] = Field(None, alias="project", description="Project information")
    section_info: Optional[Dict[str, Any]] = Field(None, alias="section", description="Section information")
    assignee_info: Optional[Dict[str, Any]] = Field(None, alias="assignee", description="Assignee information")
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    updated: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        allow_population_by_field_name = True


class TaskCreate(TaskBase):
    """Model for creating a new task."""
    
    parent: Optional[int] = Field(None, description="Parent task ID for subtasks")
    
    @validator("title")
    def validate_title(cls, v: str) -> str:
        """Validate task title."""
        if not v or not v.strip():
            raise ValueError("Task title is required")
        return v.strip()
    
    def to_api_dict(self) -> dict:
        """Convert to API payload format."""
        data = self.dict(by_alias=True, exclude_none=True)
        return clean_dict(data)


class TaskUpdate(BasicOpsBaseModel):
    """Model for updating an existing task."""
    
    title: Optional[str] = Field(None, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    project: Optional[int] = Field(None, description="Project ID")
    section: Optional[int] = Field(None, description="Section ID")
    assignee: Optional[int] = Field(None, description="Assignee user ID")
    due_date: Optional[datetime] = Field(None, alias="dueDate", description="Task due date")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    
    @validator("title")
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate task title."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Task title cannot be empty")
        return v.strip() if v else v
    
    def to_api_dict(self) -> dict:
        """Convert to API payload format."""
        data = self.dict(by_alias=True, exclude_none=True)
        return clean_dict(data)


class TaskFilters(FilterParams):
    """Filter parameters for task queries."""
    
    project: Optional[int] = Field(None, description="Filter by project ID")
    section: Optional[int] = Field(None, description="Filter by section ID")
    assignee: Optional[int] = Field(None, description="Filter by assignee ID")
    due_date_after: Optional[datetime] = Field(None, description="Filter by due date after")
    due_date_before: Optional[datetime] = Field(None, description="Filter by due date before")
    status: Optional[TaskStatus] = Field(None, description="Filter by status")
    parent: Optional[int] = Field(None, description="Filter by parent task ID")


class TaskSummary(BasicOpsBaseModel):
    """Summary view of a task for list operations."""
    
    id: int
    title: str
    description: Optional[str] = None
    project: Optional[int] = None
    section: Optional[int] = None
    assignee: Optional[int] = None
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    status: Optional[TaskStatus] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class TaskWithDetails(Task):
    """Task with full nested details."""
    
    # Override the simple IDs with full objects
    project: Optional[Dict[str, Any]] = Field(None, description="Full project information")
    section: Optional[Dict[str, Any]] = Field(None, description="Full section information") 
    assignee: Optional[Dict[str, Any]] = Field(None, description="Full assignee information")


class FileUpload(BasicOpsBaseModel):
    """Model for file upload information."""
    
    filename: str = Field(description="Name of the file")
    content: bytes = Field(description="File content")
    content_type: Optional[str] = Field(None, description="MIME type of the file")


class CloudFileAttachment(BasicOpsBaseModel):
    """Model for cloud file attachment."""
    
    filename: str = Field(alias="fileName", description="Name of the file")
    content_type: str = Field(alias="contentType", description="Content type")
    cloud_type: int = Field(alias="cloudType", description="Cloud storage type")
    cloud_id: str = Field(alias="cloudId", description="Cloud file ID")
    
    def to_api_dict(self) -> dict:
        """Convert to API payload format."""
        return self.dict(by_alias=True)
