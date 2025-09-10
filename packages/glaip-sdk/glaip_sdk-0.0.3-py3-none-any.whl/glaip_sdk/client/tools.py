#!/usr/bin/env python3
"""Tool client for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import logging
import os
import tempfile

from glaip_sdk.client.base import BaseClient
from glaip_sdk.models import Tool
from glaip_sdk.utils.client_utils import (
    create_model_instances,
    find_by_name,
)

# Set up module-level logger
logger = logging.getLogger("glaip_sdk.tools")


class ToolClient(BaseClient):
    """Client for tool operations."""

    def __init__(self, *, parent_client: BaseClient | None = None, **kwargs):
        """Initialize the tool client.

        Args:
            parent_client: Parent client to adopt session/config from
            **kwargs: Additional arguments for standalone initialization
        """
        super().__init__(parent_client=parent_client, **kwargs)

    def list_tools(self) -> list[Tool]:
        """List all tools."""
        data = self._request("GET", "/tools/")
        return create_model_instances(data, Tool, self)

    def get_tool_by_id(self, tool_id: str) -> Tool:
        """Get tool by ID."""
        data = self._request("GET", f"/tools/{tool_id}")
        return Tool(**data)._set_client(self)

    def find_tools(self, name: str | None = None) -> list[Tool]:
        """Find tools by name."""
        # Backend doesn't support name query parameter, so we fetch all and filter client-side
        data = self._request("GET", "/tools/")
        tools = create_model_instances(data, Tool, self)
        return find_by_name(tools, name, case_sensitive=False)

    def create_tool(
        self,
        name: str | None = None,
        tool_type: str = "custom",
        description: str | None = None,
        tool_script: str | None = None,
        tool_file: str | None = None,
        file_path: str | None = None,
        code: str | None = None,
        framework: str = "langchain",
        **kwargs,
    ) -> Tool:
        """Create a new tool.

        Args:
            name: Tool name (required if not provided via file)
            tool_type: Tool type (defaults to "custom")
            description: Tool description (optional)
            tool_script: Tool script content (optional)
            tool_file: Tool file path (optional)
            file_path: Alternative to tool_file (for compatibility)
            code: Alternative to tool_script (for compatibility)
            framework: Tool framework (defaults to "langchain")
            **kwargs: Additional tool parameters
        """
        # Handle compatibility parameters
        if file_path and not tool_file:
            tool_file = file_path
        if code and not tool_script:
            tool_script = code

        # Auto-detect name from file if not provided
        if not name and tool_file:
            import os

            name = os.path.splitext(os.path.basename(tool_file))[0]

        if not name:
            raise ValueError(
                "Tool name is required (either explicitly or via file path)"
            )

        # Auto-detect description if not provided
        if not description:
            description = f"A {tool_type} tool"

        payload = {
            "name": name,
            "tool_type": tool_type,
            "description": description,
            "framework": framework,
            **kwargs,
        }

        if tool_script:
            payload["tool_script"] = tool_script
        if tool_file:
            payload["tool_file"] = tool_file

        data = self._request("POST", "/tools/", json=payload)
        return Tool(**data)._set_client(self)

    def create_tool_from_code(
        self,
        name: str,
        code: str,
        framework: str = "langchain",
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> Tool:
        """Create a new tool plugin from code string.

        This method uses the /tools/upload endpoint which properly processes
        and registers tool plugins, unlike the regular create_tool method
        which only creates metadata.

        Args:
            name: Name for the tool (used for temporary file naming)
            code: Python code containing the tool plugin
            framework: Tool framework (defaults to "langchain")

        Returns:
            Tool: The created tool object
        """
        # Create a temporary file with the tool code
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", prefix=f"{name}_", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            # Prepare multipart upload
            filename = os.path.basename(temp_file_path)
            with open(temp_file_path, "rb") as fb:
                files = {
                    "file": (filename, fb, "application/octet-stream"),
                }
                data = {
                    "name": name,
                    "framework": framework,
                }
                if description:
                    data["description"] = description
                if tags:
                    # Backend might expect comma-separated or JSON; start with comma-separated
                    data["tags"] = ",".join(tags)

                response = self._request(
                    "POST",
                    "/tools/upload",
                    files=files,
                    data=data,
                )
            return Tool(**response)._set_client(self)
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass  # Ignore cleanup errors

    def update_tool(self, tool_id: str, **kwargs) -> Tool:
        """Update an existing tool."""
        data = self._request("PUT", f"/tools/{tool_id}", json=kwargs)
        return Tool(**data)._set_client(self)

    def delete_tool(self, tool_id: str) -> None:
        """Delete a tool."""
        self._request("DELETE", f"/tools/{tool_id}")

    def install_tool(self, tool_id: str) -> bool:
        """Install a tool."""
        try:
            self._request("POST", f"/tools/{tool_id}/install")
            return True
        except Exception as e:
            logger.error(f"Failed to install tool {tool_id}: {e}")
            return False

    def uninstall_tool(self, tool_id: str) -> bool:
        """Uninstall a tool."""
        try:
            self._request("POST", f"/tools/{tool_id}/uninstall")
            return True
        except Exception as e:
            logger.error(f"Failed to install tool {tool_id}: {e}")
            return False

    def get_tool_script(self, tool_id: str) -> str:
        """Get the tool script content.

        Args:
            tool_id: The ID of the tool

        Returns:
            str: The tool script content

        Raises:
            Exception: If the tool script cannot be retrieved
        """
        try:
            response = self._request("GET", f"/tools/{tool_id}/script")
            return response.get("script", "") or response.get("content", "")
        except Exception as e:
            logger.error(f"Failed to get tool script for {tool_id}: {e}")
            raise

    def update_tool_via_file(self, tool_id: str, file_path: str, **kwargs) -> Tool:
        """Update a tool plugin via file upload.

        Args:
            tool_id: The ID of the tool to update
            file_path: Path to the new tool file
            **kwargs: Additional metadata to update (name, description, tags, etc.)

        Returns:
            Tool: The updated tool object

        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: If the update fails
        """
        import os

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Tool file not found: {file_path}")

        try:
            # Prepare multipart upload
            filename = os.path.basename(file_path)
            with open(file_path, "rb") as fb:
                files = {
                    "file": (filename, fb, "application/octet-stream"),
                }

                # Add any additional metadata
                data = kwargs.copy()

                response = self._request(
                    "PUT",
                    f"/tools/{tool_id}/upload",
                    files=files,
                    data=data,
                )
            return Tool(**response)._set_client(self)
        except Exception as e:
            logger.error(f"Failed to update tool {tool_id} via file: {e}")
            raise
