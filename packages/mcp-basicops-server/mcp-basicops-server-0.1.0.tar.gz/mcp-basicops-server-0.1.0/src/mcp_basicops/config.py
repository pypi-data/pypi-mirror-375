"""Configuration management for the BasicOps MCP server."""

import os
from typing import Optional
from pydantic import BaseSettings, Field, validator


class Config(BaseSettings):
    """Configuration settings for the BasicOps MCP server."""
    
    # BasicOps API settings
    basicops_api_url: str = Field(
        default="https://api.basicops.com/v1",
        description="Base URL for the BasicOps API"
    )
    basicops_api_token: str = Field(
        description="Bearer token for BasicOps API authentication"
    )
    
    # HTTP client settings
    basicops_timeout: float = Field(
        default=30.0,
        description="Request timeout in seconds"
    )
    basicops_max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts"
    )
    basicops_retry_delay: float = Field(
        default=1.0,
        description="Base delay between retries in seconds"
    )
    
    # Logging settings
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_format: str = Field(
        default="text",
        description="Log format: 'text' or 'json'"
    )
    
    # Environment settings
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator("basicops_api_url")
    def validate_api_url(cls, v: str) -> str:
        """Ensure API URL ends without trailing slash."""
        return v.rstrip("/")
    
    @validator("basicops_api_token")
    def validate_api_token(cls, v: str) -> str:
        """Ensure API token is provided."""
        if not v.strip():
            raise ValueError("BasicOps API token is required")
        return v.strip()
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v_upper
    
    @validator("log_format")
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        valid_formats = {"text", "json"}
        v_lower = v.lower()
        if v_lower not in valid_formats:
            raise ValueError(f"Log format must be one of: {', '.join(valid_formats)}")
        return v_lower
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_envs = {"development", "staging", "production"}
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"Environment must be one of: {', '.join(valid_envs)}")
        return v_lower
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    @property
    def auth_header(self) -> dict[str, str]:
        """Get authorization header for API requests."""
        return {"Authorization": f"Bearer {self.basicops_api_token}"}


# Global configuration instance
config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global config
    if config is None:
        config = Config()
    return config


def set_config(new_config: Config) -> None:
    """Set the global configuration instance."""
    global config
    config = new_config
