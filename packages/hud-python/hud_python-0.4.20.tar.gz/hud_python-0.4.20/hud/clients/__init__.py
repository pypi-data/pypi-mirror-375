"""HUD MCP client implementations."""

from __future__ import annotations

from .base import AgentMCPClient, BaseHUDClient
from .fastmcp import FastMCPHUDClient

# Default to FastMCP for new features
MCPClient = FastMCPHUDClient

__all__ = [
    "AgentMCPClient",
    "BaseHUDClient",
    "FastMCPHUDClient",
    "MCPClient",
]
