"""MCP BasicOps Server - A Model Context Protocol server for BasicOps integration."""

__version__ = "0.1.0"
__author__ = "MCP BasicOps Server Team"
__email__ = "your.email@example.com"
__description__ = "MCP server for BasicOps project management platform integration"
__url__ = "https://github.com/yourusername/mcp-basicops-server"

from . import models
from .client import BasicOpsClient
from .config import Config, get_config, set_config
from .exceptions import (
    BasicOpsError,
    BasicOpsAPIError,
    BasicOpsAuthenticationError,
    BasicOpsNotFoundError,
    BasicOpsValidationError,
    BasicOpsRateLimitError,
    BasicOpsNetworkError,
    BasicOpsConfigurationError,
)

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__description__",
    "__url__",
    "models",
    "BasicOpsClient",
    "Config",
    "get_config",
    "set_config",
    "BasicOpsError",
    "BasicOpsAPIError", 
    "BasicOpsAuthenticationError",
    "BasicOpsNotFoundError",
    "BasicOpsValidationError",
    "BasicOpsRateLimitError",
    "BasicOpsNetworkError",
    "BasicOpsConfigurationError",
]
