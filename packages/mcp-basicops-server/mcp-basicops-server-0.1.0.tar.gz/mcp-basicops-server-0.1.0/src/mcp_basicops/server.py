"""MCP BasicOps Server - Main server implementation."""

import asyncio
import sys
from typing import Any, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest, 
    ListToolsResult,
    Tool,
    TextContent,
)
from loguru import logger

from .client import BasicOpsClient
from .config import get_config
from .exceptions import BasicOpsError
from .models import ProjectCreate, ProjectUpdate, ProjectFilters
from .services.project import ProjectService


# Initialize server
server = Server("basicops")


@server.list_tools()
async def list_tools(request: ListToolsRequest) -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="create_project",
                description="Create a new project in BasicOps",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Project title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Project description"
                        },
                        "owner": {
                            "type": "integer", 
                            "description": "Owner user ID"
                        },
                        "due_date": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Project due date (ISO format)"
                        },
                        "start_date": {
                            "type": "string", 
                            "format": "date-time",
                            "description": "Project start date (ISO format)"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["On Track", "At Risk", "In Trouble", "On Hold", "Complete"],
                            "description": "Project status"
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="get_project",
                description="Retrieve a specific project by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "integer",
                            "description": "Project ID to retrieve"
                        }
                    },
                    "required": ["project_id"]
                }
            ),
            Tool(
                name="list_projects", 
                description="List projects with optional filtering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "is_template": {
                            "type": "boolean",
                            "description": "Filter by template status"
                        },
                        "owner": {
                            "type": "integer",
                            "description": "Filter by owner ID" 
                        },
                        "status": {
                            "type": "string",
                            "enum": ["On Track", "At Risk", "In Trouble", "On Hold", "Complete"],
                            "description": "Filter by status"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of projects to return"
                        }
                    }
                }
            ),
            Tool(
                name="update_project",
                description="Update an existing project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "integer",
                            "description": "Project ID to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "Project title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Project description"
                        },
                        "owner": {
                            "type": "integer",
                            "description": "Owner user ID"
                        },
                        "due_date": {
                            "type": "string",
                            "format": "date-time", 
                            "description": "Project due date (ISO format)"
                        },
                        "start_date": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Project start date (ISO format)" 
                        },
                        "status": {
                            "type": "string",
                            "enum": ["On Track", "At Risk", "In Trouble", "On Hold", "Complete"],
                            "description": "Project status"
                        }
                    },
                    "required": ["project_id"]
                }
            ),
            Tool(
                name="delete_project",
                description="Delete a project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "integer",
                            "description": "Project ID to delete"
                        }
                    },
                    "required": ["project_id"]
                }
            )
        ]
    )


@server.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    
    try:
        # Initialize client and service
        config = get_config()
        async with BasicOpsClient(config) as client:
            project_service = ProjectService(client)
            
            if request.name == "create_project":
                # Create project
                project_data = ProjectCreate(**request.arguments)
                result = await project_service.create_project(project_data)
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully created project with ID {result.resource_id}. "
                                f"View URL: {result.view_url or 'N/A'}"
                        )
                    ]
                )
            
            elif request.name == "get_project":
                # Get project
                project_id = request.arguments["project_id"]
                project = await project_service.get_project(project_id)
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", 
                            text=f"Project Details:\n"
                                f"ID: {project.id}\n"
                                f"Title: {project.title}\n"
                                f"Description: {project.description or 'N/A'}\n"
                                f"Owner: {project.owner or 'N/A'}\n"
                                f"Status: {project.status or 'N/A'}\n"
                                f"Due Date: {project.due_date or 'N/A'}\n"
                                f"Start Date: {project.start_date or 'N/A'}\n"
                                f"Created: {project.created or 'N/A'}\n"
                                f"Updated: {project.updated or 'N/A'}"
                        )
                    ]
                )
            
            elif request.name == "list_projects":
                # List projects
                filters = ProjectFilters(**{k: v for k, v in request.arguments.items() 
                                         if k in ["is_template", "owner", "status"]})
                limit = request.arguments.get("limit")
                
                projects = await project_service.list_projects(filters=filters, limit=limit)
                
                if not projects:
                    return CallToolResult(
                        content=[TextContent(type="text", text="No projects found.")]
                    )
                
                project_list = []
                for project in projects:
                    project_list.append(
                        f"• {project.title} (ID: {project.id}) - {project.status or 'Unknown'}"
                    )
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Found {len(projects)} project(s):\n" + "\n".join(project_list)
                        )
                    ]
                )
            
            elif request.name == "update_project":
                # Update project
                project_id = request.arguments.pop("project_id")
                update_data = ProjectUpdate(**request.arguments)
                
                success = await project_service.update_project(project_id, update_data)
                
                if success:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Successfully updated project {project_id}"
                            )
                        ]
                    )
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text", 
                                text=f"Failed to update project {project_id}"
                            )
                        ]
                    )
            
            elif request.name == "delete_project":
                # Delete project
                project_id = request.arguments["project_id"]
                result = await project_service.delete_project(project_id)
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Successfully deleted project {project_id}. "
                                f"Status: {result.status_message or 'Deleted'}"
                        )
                    ]
                )
            
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Unknown tool: {request.name}"
                        )
                    ]
                )
    
    except BasicOpsError as e:
        logger.error(f"BasicOps error in tool {request.name}: {str(e)}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in tool {request.name}: {str(e)}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text", 
                    text=f"An unexpected error occurred: {str(e)}"
                )
            ]
        )


async def run_server() -> None:
    """Run the MCP server."""
    
    # Configure logging
    config = get_config()
    logger.remove()
    
    if config.log_format == "json":
        logger.add(
            sys.stderr,
            level=config.log_level,
            serialize=True,
            format="{time} | {level} | {name} | {message}"
        )
    else:
        logger.add(
            sys.stderr,
            level=config.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                  "<level>{level: <8}</level> | "
                  "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                  "<level>{message}</level>"
        )
    
    logger.info(f"Starting MCP BasicOps Server v{getattr(__import__('mcp_basicops'), '__version__', '0.1.0')}")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"API URL: {config.basicops_api_url}")
    
    # Run the server
    async with server.run_stdio() as streams:
        await streams.forward()


def main() -> None:
    """Main entry point for the MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
