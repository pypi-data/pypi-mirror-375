"""Project service for BasicOps API interactions."""

from typing import List, Optional

from loguru import logger

from ..client import BasicOpsClient
from ..exceptions import BasicOpsError
from ..models import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectFilters,
    CreateResponse,
    DeleteResponse,
    ListResponse,
)


class ProjectService:
    """Service for managing BasicOps projects."""
    
    def __init__(self, client: BasicOpsClient):
        """Initialize the project service."""
        self.client = client
    
    async def get_project(self, project_id: int) -> Project:
        """Retrieve a specific project by ID."""
        logger.debug(f"Retrieving project {project_id}")
        
        try:
            response_data = await self.client.get(f"project/{project_id}")
            
            if not response_data.get("success"):
                raise BasicOpsError(f"Failed to retrieve project {project_id}")
            
            return Project.parse_obj(response_data["data"])
            
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {str(e)}")
            raise
    
    async def list_projects(
        self,
        filters: Optional[ProjectFilters] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Project]:
        """List projects with optional filtering."""
        logger.debug("Listing projects")
        
        try:
            params = {}
            
            if filters:
                params.update(filters.to_query_params())
            
            if limit is not None:
                params["limit"] = str(limit)
            
            if offset is not None:
                params["offset"] = str(offset)
            
            response_data = await self.client.get("project", params=params)
            
            if not response_data.get("success"):
                raise BasicOpsError("Failed to list projects")
            
            # Handle both single item and list responses
            data = response_data["data"]
            if not isinstance(data, list):
                data = [data] if data else []
            
            return [Project.parse_obj(item) for item in data]
            
        except Exception as e:
            logger.error(f"Failed to list projects: {str(e)}")
            raise
    
    async def create_project(self, project_data: ProjectCreate) -> CreateResponse:
        """Create a new project."""
        logger.debug(f"Creating project: {project_data.title}")
        
        try:
            payload = project_data.to_api_dict()
            response_data = await self.client.post("project", data=payload)
            
            return CreateResponse.parse_obj(response_data)
            
        except Exception as e:
            logger.error(f"Failed to create project: {str(e)}")
            raise
    
    async def update_project(self, project_id: int, project_data: ProjectUpdate) -> bool:
        """Update an existing project."""
        logger.debug(f"Updating project {project_id}")
        
        try:
            payload = project_data.to_api_dict()
            if not payload:  # No fields to update
                return True
            
            response_data = await self.client.put(f"project/{project_id}", data=payload)
            
            return response_data.get("success", False)
            
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {str(e)}")
            raise
    
    async def delete_project(self, project_id: int) -> DeleteResponse:
        """Delete a project."""
        logger.debug(f"Deleting project {project_id}")
        
        try:
            response_data = await self.client.delete(f"project/{project_id}")
            
            return DeleteResponse.parse_obj(response_data)
            
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {str(e)}")
            raise
    
    async def list_project_sections(self, project_id: int) -> List[dict]:
        """List sections for a specific project."""
        logger.debug(f"Listing sections for project {project_id}")
        
        try:
            response_data = await self.client.get(f"project/{project_id}/sections")
            
            if not response_data.get("success"):
                raise BasicOpsError(f"Failed to list sections for project {project_id}")
            
            # Handle both single item and list responses
            data = response_data["data"]
            if not isinstance(data, list):
                data = [data] if data else []
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to list sections for project {project_id}: {str(e)}")
            raise
    
    async def list_project_tasks(self, project_id: int) -> List[dict]:
        """List tasks for a specific project."""
        logger.debug(f"Listing tasks for project {project_id}")
        
        try:
            response_data = await self.client.get(f"project/{project_id}/tasks")
            
            if not response_data.get("success"):
                raise BasicOpsError(f"Failed to list tasks for project {project_id}")
            
            # Handle both single item and list responses
            data = response_data["data"]
            if not isinstance(data, list):
                data = [data] if data else []
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to list tasks for project {project_id}: {str(e)}")
            raise
    
    async def list_project_notes(self, project_id: int) -> List[dict]:
        """List notes for a specific project."""
        logger.debug(f"Listing notes for project {project_id}")
        
        try:
            response_data = await self.client.get(f"project/{project_id}/notes")
            
            if not response_data.get("success"):
                raise BasicOpsError(f"Failed to list notes for project {project_id}")
            
            # Handle both single item and list responses
            data = response_data["data"]
            if not isinstance(data, list):
                data = [data] if data else []
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to list notes for project {project_id}: {str(e)}")
            raise
