#!/usr/bin/env python3
"""MCP client for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import logging
from typing import Any

from glaip_sdk.client.base import BaseClient
from glaip_sdk.models import MCP
from glaip_sdk.utils.client_utils import create_model_instances, find_by_name

# Set up module-level logger
logger = logging.getLogger("glaip_sdk.mcps")


class MCPClient(BaseClient):
    """Client for MCP operations."""

    def __init__(self, *, parent_client: BaseClient | None = None, **kwargs):
        """Initialize the MCP client.

        Args:
            parent_client: Parent client to adopt session/config from
            **kwargs: Additional arguments for standalone initialization
        """
        super().__init__(parent_client=parent_client, **kwargs)

    def list_mcps(self) -> list[MCP]:
        """List all MCPs."""
        data = self._request("GET", "/mcps/")
        return create_model_instances(data, MCP, self)

    def get_mcp_by_id(self, mcp_id: str) -> MCP:
        """Get MCP by ID."""
        data = self._request("GET", f"/mcps/{mcp_id}")
        return MCP(**data)._set_client(self)

    def find_mcps(self, name: str | None = None) -> list[MCP]:
        """Find MCPs by name."""
        # Backend doesn't support name query parameter, so we fetch all and filter client-side
        data = self._request("GET", "/mcps/")
        mcps = create_model_instances(data, MCP, self)
        return find_by_name(mcps, name, case_sensitive=False)

    def create_mcp(
        self,
        name: str,
        description: str,
        config: dict[str, Any] | None = None,
        **kwargs,
    ) -> MCP:
        """Create a new MCP."""
        payload = {
            "name": name,
            "description": description,
            **kwargs,
        }

        if config:
            payload["config"] = config

        # Create the MCP and fetch full details
        full_mcp_data = self._post_then_fetch(
            id_key="id",
            post_endpoint="/mcps/",
            get_endpoint_fmt="/mcps/{id}",
            json=payload,
        )
        return MCP(**full_mcp_data)._set_client(self)

    def update_mcp(self, mcp_id: str, **kwargs) -> MCP:
        """Update an existing MCP."""
        data = self._request("PUT", f"/mcps/{mcp_id}", json=kwargs)
        return MCP(**data)._set_client(self)

    def delete_mcp(self, mcp_id: str) -> None:
        """Delete an MCP."""
        self._request("DELETE", f"/mcps/{mcp_id}")

    def get_mcp_tools(self, mcp_id: str) -> list[dict[str, Any]]:
        """Get tools available from an MCP."""
        data = self._request("GET", f"/mcps/{mcp_id}/tools")
        return data or []

    def test_mcp_connection(self, config: dict[str, Any]) -> dict[str, Any]:
        """Test MCP connection using configuration.

        Args:
            config: MCP configuration dictionary

        Returns:
            dict: Connection test result

        Raises:
            Exception: If connection test fails
        """
        try:
            response = self._request("POST", "/mcps/connect", json=config)
            return response
        except Exception as e:
            logger.error(f"Failed to test MCP connection: {e}")
            raise

    def test_mcp_connection_from_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Test MCP connection using configuration (alias for test_mcp_connection).

        Args:
            config: MCP configuration dictionary

        Returns:
            dict: Connection test result
        """
        return self.test_mcp_connection(config)

    def get_mcp_tools_from_config(self, config: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch tools from MCP configuration without saving.

        Args:
            config: MCP configuration dictionary

        Returns:
            list: List of available tools from the MCP

        Raises:
            Exception: If tool fetching fails
        """
        try:
            response = self._request("POST", "/mcps/connect/tools", json=config)
            if response is None:
                return []
            return response.get("tools", []) or []
        except Exception as e:
            logger.error(f"Failed to get MCP tools from config: {e}")
            raise
