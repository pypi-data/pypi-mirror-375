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

    def _validate_and_read_file(self, file_path: str) -> str:
        """Validate file exists and read its content.

        Args:
            file_path: Path to the file to read

        Returns:
            str: File content

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Tool file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            return f.read()

    def _extract_name_from_file(self, file_path: str) -> str:
        """Extract tool name from file path.

        Args:
            file_path: Path to the file

        Returns:
            str: Extracted name (filename without extension)
        """
        return os.path.splitext(os.path.basename(file_path))[0]

    def _prepare_upload_data(
        self, name: str, framework: str, description: str | None = None, **kwargs
    ) -> dict:
        """Prepare upload data dictionary.

        Args:
            name: Tool name
            framework: Tool framework
            description: Optional description
            **kwargs: Additional parameters

        Returns:
            dict: Upload data dictionary
        """
        data = {
            "name": name,
            "framework": framework,
        }

        if description:
            data["description"] = description

        # Handle tags if provided in kwargs
        if "tags" in kwargs and kwargs["tags"]:
            if isinstance(kwargs["tags"], list):
                data["tags"] = ",".join(kwargs["tags"])
            else:
                data["tags"] = kwargs["tags"]

        # Include any other kwargs in the upload data
        for key, value in kwargs.items():
            if key not in ["tags"]:  # tags already handled above
                data[key] = value

        return data

    def _upload_tool_file(self, file_path: str, upload_data: dict) -> Tool:
        """Upload tool file to server.

        Args:
            file_path: Path to temporary file to upload
            upload_data: Dictionary with upload metadata

        Returns:
            Tool: Created tool object
        """
        with open(file_path, "rb") as fb:
            files = {
                "file": (os.path.basename(file_path), fb, "application/octet-stream"),
            }

            response = self._request(
                "POST",
                "/tools/upload",
                files=files,
                data=upload_data,
            )

        return Tool(**response)._set_client(self)

    def _create_tool_from_file(
        self,
        file_path: str,
        name: str | None = None,
        description: str | None = None,
        framework: str = "langchain",
        **kwargs,
    ) -> Tool:
        """Create tool from file content using upload endpoint.

        Args:
            file_path: Path to tool file
            name: Optional tool name (auto-detected if not provided)
            description: Optional tool description
            framework: Tool framework
            **kwargs: Additional parameters

        Returns:
            Tool: Created tool object
        """
        # Read and validate file
        file_content = self._validate_and_read_file(file_path)

        # Auto-detect name if not provided
        if not name:
            name = self._extract_name_from_file(file_path)

        # Handle description - generate default if not provided or empty
        if description is None or description == "":
            # Generate default description based on tool_type if available
            tool_type = kwargs.get("tool_type", "custom")
            description = f"A {tool_type} tool"

        # Create temporary file for upload
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            prefix=f"{name}_",
            delete=False,
            encoding="utf-8",
        ) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # Prepare upload data
            upload_data = self._prepare_upload_data(
                name=name, framework=framework, description=description, **kwargs
            )

            # Upload file
            return self._upload_tool_file(temp_file_path, upload_data)

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass  # Ignore cleanup errors

    def create_tool(
        self,
        file_path: str,
        name: str | None = None,
        description: str | None = None,
        framework: str = "langchain",
        **kwargs,
    ) -> Tool:
        """Create a new tool from a file.

        Args:
            file_path: File path to tool script (required) - file content will be read and processed as plugin
            name: Tool name (auto-detected from file if not provided)
            description: Tool description (auto-generated if not provided)
            framework: Tool framework (defaults to "langchain")
            **kwargs: Additional tool parameters
        """
        return self._create_tool_from_file(
            file_path=file_path,
            name=name,
            description=description,
            framework=framework,
            **kwargs,
        )

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
            description: Optional tool description
            tags: Optional list of tags

        Returns:
            Tool: The created tool object
        """
        # Create a temporary file with the tool code
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            prefix=f"{name}_",
            delete=False,
            encoding="utf-8",
        ) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            # Prepare upload data using shared helper
            upload_data = self._prepare_upload_data(
                name=name,
                framework=framework,
                description=description,
                tags=tags if tags else None,
            )

            # Upload file using shared helper
            return self._upload_tool_file(temp_file_path, upload_data)

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
        # Validate file exists
        self._validate_and_read_file(file_path)

        try:
            # Prepare multipart upload
            with open(file_path, "rb") as fb:
                files = {
                    "file": (
                        os.path.basename(file_path),
                        fb,
                        "application/octet-stream",
                    ),
                }

                response = self._request(
                    "PUT",
                    f"/tools/{tool_id}/upload",
                    files=files,
                    data=kwargs,  # Pass kwargs directly as data
                )

            return Tool(**response)._set_client(self)

        except Exception as e:
            logger.error(f"Failed to update tool {tool_id} via file: {e}")
            raise
