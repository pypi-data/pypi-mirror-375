"""Basic tests for the MCP BasicOps server."""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from mcp_basicops.models import ProjectCreate, ProjectStatus
from mcp_basicops.services.project import ProjectService
from mcp_basicops.client import BasicOpsClient


@pytest.fixture
def mock_client():
    """Create a mock BasicOps client."""
    client = Mock(spec=BasicOpsClient)
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
def project_service(mock_client):
    """Create a project service with mock client."""
    return ProjectService(mock_client)


@pytest.mark.asyncio
async def test_create_project(project_service, mock_client):
    """Test project creation."""
    # Arrange
    project_data = ProjectCreate(
        title="Test Project",
        description="A test project",
        status=ProjectStatus.ON_TRACK
    )
    
    mock_response = {
        "success": True,
        "data": {
            "id": 123,
            "viewUrl": "https://example.com/project/123",
            "bounceUrl": "https://example.com/bounce/123"
        }
    }
    mock_client.post.return_value = mock_response
    
    # Act
    result = await project_service.create_project(project_data)
    
    # Assert
    assert result.success is True
    assert result.resource_id == 123
    assert "https://example.com/project/123" in result.view_url
    mock_client.post.assert_called_once_with("project", data=project_data.to_api_dict())


@pytest.mark.asyncio
async def test_get_project(project_service, mock_client):
    """Test getting a project."""
    # Arrange
    project_id = 123
    mock_response = {
        "success": True,
        "data": {
            "id": 123,
            "title": "Test Project",
            "description": "A test project",
            "status": "On Track",
            "owner": 456,
            "created": "2024-01-15T10:30:00Z",
            "updated": "2024-01-16T14:20:00Z"
        }
    }
    mock_client.get.return_value = mock_response
    
    # Act
    project = await project_service.get_project(project_id)
    
    # Assert
    assert project.id == 123
    assert project.title == "Test Project"
    assert project.description == "A test project"
    assert project.status == ProjectStatus.ON_TRACK
    assert project.owner == 456
    mock_client.get.assert_called_once_with("project/123")


@pytest.mark.asyncio 
async def test_list_projects(project_service, mock_client):
    """Test listing projects."""
    # Arrange
    mock_response = {
        "success": True,
        "data": [
            {
                "id": 123,
                "title": "Project 1",
                "status": "On Track",
                "owner": 456
            },
            {
                "id": 124,
                "title": "Project 2", 
                "status": "At Risk",
                "owner": 457
            }
        ]
    }
    mock_client.get.return_value = mock_response
    
    # Act
    projects = await project_service.list_projects(limit=10)
    
    # Assert
    assert len(projects) == 2
    assert projects[0].id == 123
    assert projects[0].title == "Project 1"
    assert projects[1].id == 124
    assert projects[1].title == "Project 2"
    mock_client.get.assert_called_once_with("project", params={"limit": "10"})


def test_project_create_validation():
    """Test project creation validation."""
    # Valid project
    project = ProjectCreate(
        title="Valid Project",
        description="A valid project"
    )
    assert project.title == "Valid Project"
    
    # Invalid project (empty title)
    with pytest.raises(ValueError, match="Project title is required"):
        ProjectCreate(title="")
    
    # Invalid project (whitespace only title)
    with pytest.raises(ValueError, match="Project title is required"):
        ProjectCreate(title="   ")


def test_project_api_dict():
    """Test project to_api_dict method."""
    project = ProjectCreate(
        title="Test Project",
        description="A test project",
        status=ProjectStatus.ON_TRACK,
        due_date=datetime(2024, 12, 31, 23, 59, 59)
    )
    
    api_dict = project.to_api_dict()
    
    assert api_dict["title"] == "Test Project"
    assert api_dict["description"] == "A test project"
    assert api_dict["status"] == "On Track"
    assert "dueDate" in api_dict
    assert api_dict["dueDate"] == "2024-12-31T23:59:59"
