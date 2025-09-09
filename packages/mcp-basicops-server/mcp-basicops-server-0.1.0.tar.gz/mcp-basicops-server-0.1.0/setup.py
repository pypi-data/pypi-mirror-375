#!/usr/bin/env python3
"""Setup script for mcp-basicops-server."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from package
def get_version():
    """Get version from package."""
    version_file = os.path.join(this_directory, 'src', 'mcp_basicops', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="mcp-basicops-server",
    version=get_version(),
    author="MCP BasicOps Server",
    author_email="support@example.com",
    description="MCP server for BasicOps project management platform integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-basicops-server",
    project_urls={
        "Homepage": "https://github.com/yourusername/mcp-basicops-server",
        "Repository": "https://github.com/yourusername/mcp-basicops-server.git",
        "Issues": "https://github.com/yourusername/mcp-basicops-server/issues",
        "Documentation": "https://github.com/yourusername/mcp-basicops-server#readme",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Groupware",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "respx>=0.20.0",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcp-basicops-server=mcp_basicops.server:main",
        ],
    },
    keywords=["mcp", "basicops", "project-management", "llm", "ai"],
    include_package_data=True,
    package_data={
        "mcp_basicops": ["py.typed"],
    },
    zip_safe=False,
)
