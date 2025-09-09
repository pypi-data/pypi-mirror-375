"""Common models and enums for BasicOps entities."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    
    ON_TRACK = "On Track"
    AT_RISK = "At Risk"
    IN_TROUBLE = "In Trouble"
    ON_HOLD = "On Hold"
    COMPLETE = "Complete"


class TaskStatus(str, Enum):
    """Task status enumeration."""
    
    NEW = "New"
    ACCEPTED = "Accepted"
    IN_PROGRESS = "In Progress"
    UNDER_REVIEW = "Under Review"
    REVIEWED = "Reviewed"
    ON_HOLD = "On Hold"
    BLOCKED = "Blocked"
    COMPLETE = "Complete"


class SectionState(str, Enum):
    """Section state enumeration."""
    
    OPEN = "Open"
    COMPLETE = "Complete"


class CloudType(int, Enum):
    """Cloud storage type enumeration."""
    
    GOOGLE_DRIVE = 1
    BOX = 2
    DROPBOX = 3
    ONEDRIVE = 6


class BasicOpsBaseModel(BaseModel):
    """Base model for all BasicOps entities."""
    
    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "forbid"
    
    @validator("*", pre=True)
    def convert_datetime_strings(cls, v: Any) -> Any:
        """Convert datetime strings to datetime objects."""
        if isinstance(v, str) and v.endswith("Z"):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                pass
        return v


class Attachment(BasicOpsBaseModel):
    """File attachment model."""
    
    id: str = Field(alias="Id")
    filename: str = Field(alias="FileName")
    size: int = Field(alias="Size")
    created: datetime = Field(alias="Created")
    download_url: str = Field(alias="DownloadURL")
    thumbnail_url: Optional[str] = Field(None, alias="ThumbnailURL")
    width: Optional[int] = Field(None, alias="Width")
    height: Optional[int] = Field(None, alias="Height")
    content_type: Optional[str] = Field(None, alias="ContentType")


class CloudFile(BasicOpsBaseModel):
    """Cloud file model."""
    
    filename: str = Field(alias="fileName")
    content_type: str = Field(alias="contentType")
    cloud_type: CloudType = Field(alias="cloudType")
    cloud_id: str = Field(alias="cloudId")


class APIResponse(BasicOpsBaseModel):
    """Standard API response wrapper."""
    
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None


class ListResponse(BasicOpsBaseModel):
    """List response with pagination support."""
    
    success: bool
    data: List[Any]
    total: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
    has_more: Optional[bool] = None


class CreateResponse(BasicOpsBaseModel):
    """Response for create operations."""
    
    success: bool
    data: Dict[str, Any]
    
    @property
    def resource_id(self) -> Optional[int]:
        """Get the ID of the created resource."""
        return self.data.get("id")
    
    @property
    def view_url(self) -> Optional[str]:
        """Get the view URL of the created resource."""
        return self.data.get("viewUrl")
    
    @property
    def bounce_url(self) -> Optional[str]:
        """Get the bounce URL of the created resource."""
        return self.data.get("bounceUrl")


class DeleteResponse(BasicOpsBaseModel):
    """Response for delete operations."""
    
    success: bool
    data: Dict[str, Any]
    
    @property
    def status_message(self) -> Optional[str]:
        """Get the status message."""
        return self.data.get("status")
    
    @property
    def activities(self) -> List[int]:
        """Get the list of activity IDs."""
        return self.data.get("activities", [])


class FilterParams(BasicOpsBaseModel):
    """Base class for filter parameters."""
    
    created_after: Optional[datetime] = Field(None, description="Filter by creation date after")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date before")
    updated_after: Optional[datetime] = Field(None, description="Filter by update date after")
    updated_before: Optional[datetime] = Field(None, description="Filter by update date before")
    
    def to_query_params(self) -> Dict[str, str]:
        """Convert filter params to query parameters."""
        params = {}
        
        for field_name, field_value in self:
            if field_value is not None:
                if isinstance(field_value, datetime):
                    params[field_name] = field_value.isoformat()
                else:
                    params[field_name] = str(field_value)
        
        return params


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary."""
    return {k: v for k, v in data.items() if v is not None}


def serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Serialize datetime to ISO format string."""
    return dt.isoformat() if dt else None
