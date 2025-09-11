"""Renderer package for modular streaming output.

This package provides modular components for rendering agent execution streams,
with clean separation of concerns between configuration, console handling,
debug output, panel rendering, progress tracking, and event routing.
"""

from .base import RichStreamRenderer
from .config import RendererConfig
from .console import CapturingConsole
from .debug import render_debug_event
from .panels import (
    create_context_panel,
    create_final_panel,
    create_main_panel,
    create_tool_panel,
)
from .progress import (
    format_tool_title,
    is_delegation_tool,
)
from .stream import StreamProcessor

__all__ = [
    # Main classes
    "RichStreamRenderer",
    "RendererConfig",
    "CapturingConsole",
    "StreamProcessor",
    # Key functions
    "render_debug_event",
    "create_main_panel",
    "create_tool_panel",
    "create_context_panel",
    "create_final_panel",
    "format_tool_title",
    "is_delegation_tool",
]
