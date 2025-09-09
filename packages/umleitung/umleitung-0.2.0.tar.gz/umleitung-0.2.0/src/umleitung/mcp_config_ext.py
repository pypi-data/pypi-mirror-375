from typing import Optional
from fastmcp.mcp_config import (
    StdioMCPServer as BaseStdioMCPServer,
    RemoteMCPServer as BaseRemoteMCPServer,
    MCPConfig as BaseMCPConfig,
)
from pydantic import Field, model_validator


class StdioMCPServer(BaseStdioMCPServer):
    allowed_tools: Optional[list[str]] = Field(
        default=None,
        alias="allowedTools",
        serialization_alias="allowedTools",
        description="List of allowed tools for this MCP server",
    )
    blocked_tools: Optional[list[str]] = Field(
        default=None,
        alias="blockedTools",
        serialization_alias="blockedTools",
        description="List of blocked tools for this MCP server",
    )

    @model_validator(mode="after")
    def only_one_of_allowed_or_blocked(cls, self):
        if self.allowed_tools and self.blocked_tools:
            raise ValueError(
                "Specify only one of allowedTools or blockedTools on a server, not both."
            )
        return self


class RemoteMCPServer(BaseRemoteMCPServer):
    allowed_tools: Optional[list[str]] = Field(
        default=None,
        alias="allowedTools",
        serialization_alias="allowedTools",
        description="List of allowed tools for this MCP server",
    )
    blocked_tools: Optional[list[str]] = Field(
        default=None,
        alias="blockedTools",
        serialization_alias="blockedTools",
        description="List of blocked tools for this MCP server",
    )

    @model_validator(mode="after")
    def only_one_of_allowed_or_blocked(cls, self):
        if self.allowed_tools and self.blocked_tools:
            raise ValueError(
                "Specify only one of allowedTools or blockedTools on a server, not both."
            )
        return self


class MCPConfig(BaseMCPConfig):
    mcpServers: dict[str, StdioMCPServer | RemoteMCPServer]
