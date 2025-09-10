#!/usr/bin/env python3
"""Utility functions for AIP SDK clients.

This module contains generic utility functions that can be reused across
different client types (agents, tools, etc.).

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import logging
from contextlib import ExitStack
from pathlib import Path
from typing import Any, BinaryIO

import httpx

from glaip_sdk.exceptions import AgentTimeoutError

# Set up module-level logger
logger = logging.getLogger("glaip_sdk.client_utils")


class MultipartData:
    """Container for multipart form data with automatic file handle cleanup."""

    def __init__(self, data: dict[str, Any], files: list[tuple[str, Any]]):
        """Initialize multipart data container.

        Args:
            data: Form data dictionary
            files: List of file tuples for multipart form
        """
        self.data = data
        self.files = files
        self._exit_stack = ExitStack()

    def close(self):
        """Close all opened file handles."""
        self._exit_stack.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def extract_ids(items: list[str | Any] | None) -> list[str] | None:
    """Extract IDs from a list of objects or strings.

    Args:
        items: List of items that may be strings, objects with .id, or other types

    Returns:
        List of extracted IDs, or None if items is empty/None
    """
    if not items:
        return None

    ids = []
    for item in items:
        if isinstance(item, str):
            ids.append(item)
        elif hasattr(item, "id"):
            ids.append(item.id)
        else:
            # Fallback: convert to string
            ids.append(str(item))

    return ids


def create_model_instances(
    data: list[dict] | None, model_class: type, client: Any
) -> list[Any]:
    """Create model instances from API data with client association.

    This is a common pattern used across different clients (agents, tools, mcps)
    to create model instances and associate them with the client.

    Args:
        data: List of dictionaries from API response
        model_class: The model class to instantiate
        client: The client instance to associate with models

    Returns:
        List of model instances with client association
    """
    if not data:
        return []

    return [model_class(**item_data)._set_client(client) for item_data in data]


def find_by_name(
    items: list[Any], name: str, case_sensitive: bool = False
) -> list[Any]:
    """Filter items by name with optional case sensitivity.

    This is a common pattern used across different clients for client-side
    filtering when the backend doesn't support name query parameters.

    Args:
        items: List of items to filter
        name: Name to search for
        case_sensitive: Whether the search should be case sensitive

    Returns:
        Filtered list of items matching the name
    """
    if not name:
        return items

    if case_sensitive:
        return [item for item in items if name in item.name]
    else:
        return [item for item in items if name.lower() in item.name.lower()]


def iter_sse_events(
    response: httpx.Response, timeout_seconds: float = None, agent_name: str = None
):
    """Iterate over Server-Sent Events with proper parsing.

    Args:
        response: HTTP response object with streaming content
        timeout_seconds: Timeout duration in seconds (for error messages)
        agent_name: Agent name (for error messages)

    Yields:
        Dictionary with event data, type, and ID

    Raises:
        AgentTimeoutError: When agent execution times out
        httpx.TimeoutException: When general timeout occurs
        Exception: For other unexpected errors
    """
    buf = []
    event_type = None
    event_id = None

    try:
        for raw in response.iter_lines():
            line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            if line is None:
                continue

            # Normalize CRLF and treat whitespace-only as blank
            line = line.rstrip("\r")

            if not line.strip():  # instead of: if line == ""
                if buf:
                    data = "\n".join(buf)
                    yield {
                        "event": event_type or "message",
                        "id": event_id,
                        "data": data,
                    }
                    buf, event_type, event_id = [], None, None
                continue

            if line.startswith(":"):  # comment
                continue
            if line.startswith("data:"):
                data_line = line[5:].lstrip()

                # Optional: handle sentinel end markers gracefully
                if data_line.strip() == "[DONE]":
                    if buf:
                        data = "\n".join(buf)
                        yield {
                            "event": event_type or "message",
                            "id": event_id,
                            "data": data,
                        }
                    return

                buf.append(data_line)
            elif line.startswith("event:"):
                event_type = line[6:].strip() or None
            elif line.startswith("id:"):
                event_id = line[3:].strip() or None

        # Flush any remaining data
        if buf:
            yield {
                "event": event_type or "message",
                "id": event_id,
                "data": "\n".join(buf),
            }
    except httpx.ReadTimeout as e:
        logger.error(f"Read timeout during streaming: {e}")
        logger.error("This usually indicates the backend is taking too long to respond")
        logger.error(
            "Consider increasing the timeout value or checking backend performance"
        )
        # Raise a more user-friendly timeout error
        raise AgentTimeoutError(
            timeout_seconds or 30.0,  # Default to 30s if not provided
            agent_name,
        )
    except httpx.TimeoutException as e:
        logger.error(f"General timeout during streaming: {e}")
        # Also convert general timeout to agent timeout for consistency
        raise AgentTimeoutError(timeout_seconds or 30.0, agent_name)
    except httpx.StreamClosed as e:
        logger.error(f"Stream closed unexpectedly during streaming: {e}")
        logger.error("This may indicate a backend issue or network problem")
        logger.error("The response stream was closed before all data could be read")
        raise
    except httpx.ConnectError as e:
        logger.error(f"Connection error during streaming: {e}")
        logger.error("Check your network connection and backend availability")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during streaming: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        # Log additional context if available
        if hasattr(e, "__cause__") and e.__cause__:
            logger.error(f"Caused by: {e.__cause__}")
        raise


def prepare_multipart_data(message: str, files: list[str | BinaryIO]) -> MultipartData:
    """Prepare multipart form data for file uploads.

    Args:
        message: Text message to include with the upload
        files: List of file paths or file-like objects

    Returns:
        MultipartData object with automatic file handle cleanup

    Raises:
        FileNotFoundError: When a file path doesn't exist
        ValueError: When a file object is invalid
    """
    # Backend expects 'input' for the main prompt. Keep 'message' for
    # backward-compatibility with any legacy handlers.
    form_data = {"input": message, "message": message, "stream": True}
    file_list = []

    with ExitStack() as stack:
        multipart_data = MultipartData(form_data, [])
        multipart_data._exit_stack = stack

        for file_item in files:
            if isinstance(file_item, str):
                # File path - let httpx stream the file handle
                file_path = Path(file_item)
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_item}")

                # Open file and register for cleanup
                fh = stack.enter_context(open(file_path, "rb"))
                file_list.append(
                    (
                        "files",
                        (
                            file_path.name,
                            fh,
                            "application/octet-stream",
                        ),
                    )
                )
            else:
                # File-like object
                if hasattr(file_item, "name"):
                    filename = getattr(file_item, "name", "file")
                else:
                    filename = "file"

                if hasattr(file_item, "read"):
                    # For file-like objects, we need to read them since httpx expects bytes
                    file_content = file_item.read()
                    file_list.append(
                        ("files", (filename, file_content, "application/octet-stream"))
                    )
                else:
                    raise ValueError(f"Invalid file object: {file_item}")

        multipart_data.files = file_list
        return multipart_data
