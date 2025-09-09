"""Webhook-related models for BasicOps API."""

from typing import List, Optional

from pydantic import Field, validator

from .common import BasicOpsBaseModel, FilterParams, clean_dict


class WebhookBase(BasicOpsBaseModel):
    """Base webhook model with common fields."""
    
    name: str = Field(description="Webhook name")
    url: str = Field(description="Webhook URL endpoint")
    events: str = Field(description="Comma-separated list of events to subscribe to")
    project: Optional[int] = Field(None, description="Project ID to filter events")
    section: Optional[int] = Field(None, description="Section ID to filter events")
    exclude_details: Optional[bool] = Field(False, alias="excludeDetails", description="Whether to exclude event details")


class Webhook(WebhookBase):
    """Complete webhook model with read-only fields."""
    
    id: int = Field(alias="Id", description="Webhook internal ID")
    company_id: int = Field(alias="CompanyId", description="Company ID")
    user_id: int = Field(alias="UserId", description="User ID who created the webhook")
    eid: str = Field(alias="EId", description="External webhook ID")
    
    class Config:
        allow_population_by_field_name = True


class WebhookCreate(WebhookBase):
    """Model for creating a new webhook."""
    
    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate webhook name."""
        if not v or not v.strip():
            raise ValueError("Webhook name is required")
        return v.strip()
    
    @validator("url")
    def validate_url(cls, v: str) -> str:
        """Validate webhook URL."""
        if not v or not v.strip():
            raise ValueError("Webhook URL is required")
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("Webhook URL must start with http:// or https://")
        return v
    
    @validator("events")
    def validate_events(cls, v: str) -> str:
        """Validate events string."""
        if not v or not v.strip():
            raise ValueError("At least one event is required")
        
        events = [event.strip() for event in v.split(",")]
        valid_patterns = [
            "basicops:project:",
            "basicops:section:",
            "basicops:task:",
            "basicops:note:",
            "basicops:user:"
        ]
        valid_actions = ["created", "updated", "deleted"]
        
        for event in events:
            if not event:
                continue
            
            # Check if event follows the correct pattern
            if not any(event.startswith(pattern) for pattern in valid_patterns):
                raise ValueError(f"Invalid event format: {event}")
            
            # Check if it ends with a valid action
            if not any(event.endswith(action) for action in valid_actions):
                raise ValueError(f"Invalid event action in: {event}")
        
        return v.strip()
    
    def to_api_dict(self) -> dict:
        """Convert to API payload format."""
        data = self.dict(by_alias=True, exclude_none=True)
        return clean_dict(data)


class WebhookUpdate(BasicOpsBaseModel):
    """Model for updating an existing webhook."""
    
    name: Optional[str] = Field(None, description="Webhook name")
    url: Optional[str] = Field(None, description="Webhook URL endpoint")
    events: Optional[str] = Field(None, description="Comma-separated list of events")
    project: Optional[int] = Field(None, description="Project ID to filter events")
    section: Optional[int] = Field(None, description="Section ID to filter events")
    exclude_details: Optional[bool] = Field(None, alias="excludeDetails", description="Whether to exclude event details")
    
    @validator("name")
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate webhook name."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Webhook name cannot be empty")
        return v.strip() if v else v
    
    @validator("url")
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate webhook URL."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Webhook URL cannot be empty")
            v = v.strip()
            if not v.startswith(("http://", "https://")):
                raise ValueError("Webhook URL must start with http:// or https://")
        return v
    
    @validator("events")
    def validate_events(cls, v: Optional[str]) -> Optional[str]:
        """Validate events string."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("At least one event is required")
            
            events = [event.strip() for event in v.split(",")]
            valid_patterns = [
                "basicops:project:",
                "basicops:section:",
                "basicops:task:",
                "basicops:note:",
                "basicops:user:"
            ]
            valid_actions = ["created", "updated", "deleted"]
            
            for event in events:
                if not event:
                    continue
                
                if not any(event.startswith(pattern) for pattern in valid_patterns):
                    raise ValueError(f"Invalid event format: {event}")
                
                if not any(event.endswith(action) for action in valid_actions):
                    raise ValueError(f"Invalid event action in: {event}")
        
        return v.strip() if v else v
    
    def to_api_dict(self) -> dict:
        """Convert to API payload format."""
        data = self.dict(by_alias=True, exclude_none=True)
        return clean_dict(data)


class WebhookFilters(FilterParams):
    """Filter parameters for webhook queries."""
    
    name: Optional[str] = Field(None, description="Filter by webhook name")
    url: Optional[str] = Field(None, description="Filter by webhook URL")
    project: Optional[int] = Field(None, description="Filter by project ID")


class WebhookEvent(BasicOpsBaseModel):
    """Model for webhook event payloads."""
    
    timestamp: str = Field(description="Event timestamp")
    event: str = Field(description="Event type")
    user: dict = Field(description="User who triggered the event")
    records: List[dict] = Field(description="Affected records")


class WebhookPayload(BasicOpsBaseModel):
    """Model for incoming webhook payloads."""
    
    events: List[WebhookEvent] = Field(description="List of events")
