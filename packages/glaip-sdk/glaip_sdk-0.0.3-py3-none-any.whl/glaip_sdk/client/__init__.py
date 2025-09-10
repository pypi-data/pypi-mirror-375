#!/usr/bin/env python3
"""Main client for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from typing import Any

from glaip_sdk.client.agents import AgentClient
from glaip_sdk.client.base import BaseClient
from glaip_sdk.client.mcps import MCPClient
from glaip_sdk.client.tools import ToolClient
from glaip_sdk.models import MCP, Agent, Tool


class Client(BaseClient):
    """Main client that composes all specialized clients and shares one HTTP session."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Share the single httpx.Client + config with sub-clients
        shared_config = {
            "parent_client": self,
            "api_url": self.api_url,
            "api_key": self.api_key,
            "timeout": self._timeout,
        }
        self.agents = AgentClient(**shared_config)
        self.tools = ToolClient(**shared_config)
        self.mcps = MCPClient(**shared_config)

    # ---- Agents
    def list_agents(self) -> list[Agent]:
        agents = self.agents.list_agents()
        for agent in agents:
            agent._set_client(self)
        return agents

    def get_agent_by_id(self, agent_id: str) -> Agent:
        agent = self.agents.get_agent_by_id(agent_id)
        agent._set_client(self)
        return agent

    def find_agents(self, name: str | None = None) -> list[Agent]:
        agents = self.agents.find_agents(name)
        for agent in agents:
            agent._set_client(self)
        return agents

    def create_agent(
        self,
        name: str | None = None,
        model: str | None = None,
        instruction: str | None = None,
        tools: list[str | Tool] | None = None,
        agents: list[str | Agent] | None = None,
        timeout: int = 300,
        **kwargs,
    ) -> Agent:
        agent = self.agents.create_agent(
            name=name,
            model=model,
            instruction=instruction,
            tools=tools,
            agents=agents,
            timeout=timeout,
            **kwargs,
        )
        agent._set_client(self)
        return agent

    def delete_agent(self, agent_id: str) -> None:
        """Delete an agent by ID."""
        return self.agents.delete_agent(agent_id)

    def update_agent(
        self, agent_id: str, update_data: dict | None = None, **kwargs
    ) -> Agent:
        """Update an agent by ID."""
        if update_data:
            kwargs.update(update_data)
        return self.agents.update_agent(agent_id, **kwargs)

    # ---- Tools
    def list_tools(self) -> list[Tool]:
        tools = self.tools.list_tools()
        for tool in tools:
            tool._set_client(self)
        return tools

    def get_tool_by_id(self, tool_id: str) -> Tool:
        tool = self.tools.get_tool_by_id(tool_id)
        tool._set_client(self)
        return tool

    def find_tools(self, name: str | None = None) -> list[Tool]:
        tools = self.tools.find_tools(name)
        for tool in tools:
            tool._set_client(self)
        return tools

    def create_tool(self, **kwargs) -> Tool:
        tool = self.tools.create_tool(**kwargs)
        tool._set_client(self)
        return tool

    def create_tool_from_code(
        self,
        name: str,
        code: str,
        framework: str = "langchain",
        *,
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> Tool:
        """Create a new tool plugin from code string."""
        tool = self.tools.create_tool_from_code(
            name, code, framework, description=description, tags=tags
        )
        tool._set_client(self)
        return tool

    def update_tool(self, tool_id: str, **kwargs) -> Tool:
        """Update an existing tool."""
        return self.tools.update_tool(tool_id, **kwargs)

    def delete_tool(self, tool_id: str) -> None:
        """Delete a tool by ID."""
        return self.tools.delete_tool(tool_id)

    def get_tool_script(self, tool_id: str) -> str:
        """Get tool script content."""
        return self.tools.get_tool_script(tool_id)

    def update_tool_via_file(self, tool_id: str, file_path: str, **kwargs) -> Tool:
        """Update a tool plugin via file upload."""
        tool = self.tools.update_tool_via_file(tool_id, file_path, **kwargs)
        tool._set_client(self)
        return tool

    # ---- MCPs
    def list_mcps(self) -> list[MCP]:
        mcps = self.mcps.list_mcps()
        for mcp in mcps:
            mcp._set_client(self)
        return mcps

    def get_mcp_by_id(self, mcp_id: str) -> MCP:
        mcp = self.mcps.get_mcp_by_id(mcp_id)
        mcp._set_client(self)
        return mcp

    def find_mcps(self, name: str | None = None) -> list[MCP]:
        mcps = self.mcps.find_mcps(name)
        for mcp in mcps:
            mcp._set_client(self)
        return mcps

    def create_mcp(self, **kwargs) -> MCP:
        mcp = self.mcps.create_mcp(**kwargs)
        mcp._set_client(self)
        return mcp

    def delete_mcp(self, mcp_id: str) -> None:
        """Delete an MCP by ID."""
        return self.mcps.delete_mcp(mcp_id)

    def update_mcp(self, mcp_id: str, **kwargs) -> MCP:
        """Update an MCP by ID."""
        return self.mcps.update_mcp(mcp_id, **kwargs)

    def test_mcp_connection(self, config: dict[str, Any]) -> dict[str, Any]:
        """Test MCP connection using configuration."""
        return self.mcps.test_mcp_connection(config)

    def test_mcp_connection_from_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Test MCP connection using configuration (alias)."""
        return self.mcps.test_mcp_connection_from_config(config)

    def get_mcp_tools_from_config(self, config: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch tools from MCP configuration without saving."""
        return self.mcps.get_mcp_tools_from_config(config)

    def run_agent(self, agent_id: str, message: str, **kwargs) -> str:
        """Run an agent with a message."""
        return self.agents.run_agent(agent_id, message, **kwargs)

    # ---- Language Models
    def list_language_models(self) -> list[dict]:
        """List available language models."""
        data = self._request("GET", "/language-models")
        return data or []

    # ---- Timeout propagation ----
    @property
    def timeout(self) -> float:  # type: ignore[override]
        return super().timeout

    @timeout.setter
    def timeout(self, value: float) -> None:  # type: ignore[override]
        # Rebuild the root http client
        BaseClient.timeout.fset(self, value)  # call parent setter
        # Propagate the new session to sub-clients so they don't hold a closed client
        try:
            if hasattr(self, "agents"):
                self.agents.http_client = self.http_client
            if hasattr(self, "tools"):
                self.tools.http_client = self.http_client
            if hasattr(self, "mcps"):
                self.mcps.http_client = self.http_client
        except Exception:
            pass

    # ---- Aliases (back-compat)
    def get_agent(self, agent_id: str) -> Agent:
        return self.get_agent_by_id(agent_id)

    def get_tool(self, tool_id: str) -> Tool:
        return self.get_tool_by_id(tool_id)

    def get_mcp(self, mcp_id: str) -> MCP:
        return self.get_mcp_by_id(mcp_id)

    # ---- Health
    def ping(self) -> bool:
        try:
            self._request("GET", "/health-check")
            return True
        except Exception:
            return False
