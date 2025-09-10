"""Utility modules for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import re
from uuid import UUID

import click

from .rendering.models import RunStats, Step
from .rendering.steps import StepManager
from .run_renderer import RichStreamRenderer

# Rich imports with availability check
try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Functions are defined below in this file


def is_uuid(value: str) -> bool:
    """Check if a string is a valid UUID.

    Args:
        value: String to check

    Returns:
        True if value is a valid UUID, False otherwise
    """
    try:
        UUID(value)
        return True
    except (ValueError, TypeError):
        return False


def sanitize_name(name: str) -> str:
    """Sanitize a name for resource creation.

    Args:
        name: Raw name input

    Returns:
        Sanitized name suitable for resource creation
    """
    # Remove special characters and normalize
    sanitized = re.sub(r"[^a-zA-Z0-9\-_]", "-", name.strip())
    sanitized = re.sub(r"-+", "-", sanitized)  # Collapse multiple dashes
    return sanitized.lower().strip("-")


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human readable size string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def progress_bar(iterable, description: str = "Processing"):
    """Simple progress bar using click.

    Args:
        iterable: Iterable to process
        description: Progress description

    Yields:
        Items from iterable with progress display
    """
    try:
        with click.progressbar(iterable, label=description) as bar:
            for item in bar:
                yield item
    except ImportError:
        # Fallback if click not available
        for item in iterable:
            yield item


# Rich display utilities for enhanced output
# RICH_AVAILABLE is determined by the try/except block above


def print_agent_output(output: str, title: str = "Agent Output") -> None:
    """Print agent output with rich formatting.

    Args:
        output: The agent's response text
        title: Title for the output panel
    """
    if RICH_AVAILABLE:
        console = Console()
        panel = Panel(
            Text(output, style="green"),
            title=title,
            border_style="green",
            box=box.ROUNDED,
        )
        console.print(panel)
    else:
        print(f"\n=== {title} ===")
        print(output)
        print("=" * (len(title) + 8))


def print_agent_created(agent, title: str = "🤖 Agent Created") -> None:
    """Print agent creation success with rich formatting.

    Args:
        agent: The created agent object
        title: Title for the output panel
    """
    if RICH_AVAILABLE:
        console = Console()
        panel = Panel(
            f"[green]✅ Agent '{agent.name}' created successfully![/green]\n\n"
            f"ID: {agent.id}\n"
            f"Model: {getattr(agent, 'model', 'N/A')}\n"
            f"Type: {getattr(agent, 'type', 'config')}\n"
            f"Framework: {getattr(agent, 'framework', 'langchain')}\n"
            f"Version: {getattr(agent, 'version', '1.0')}",
            title=title,
            border_style="green",
            box=box.ROUNDED,
        )
        console.print(panel)
    else:
        print(f"✅ Agent '{agent.name}' created successfully!")
        print(f"ID: {agent.id}")
        print(f"Model: {getattr(agent, 'model', 'N/A')}")
        print(f"Type: {getattr(agent, 'type', 'config')}")
        print(f"Framework: {getattr(agent, 'framework', 'langchain')}")
        print(f"Version: {getattr(agent, 'version', '1.0')}")


def print_agent_updated(agent) -> None:
    """Print agent update success with rich formatting.

    Args:
        agent: The updated agent object
    """
    if RICH_AVAILABLE:
        console = Console()
        console.print(f"[green]✅ Agent '{agent.name}' updated successfully[/green]")
    else:
        print(f"✅ Agent '{agent.name}' updated successfully")


def print_agent_deleted(agent_id: str) -> None:
    """Print agent deletion success with rich formatting.

    Args:
        agent_id: The deleted agent's ID
    """
    if RICH_AVAILABLE:
        console = Console()
        console.print(f"[green]✅ Agent deleted successfully (ID: {agent_id})[/green]")
    else:
        print(f"✅ Agent deleted successfully (ID: {agent_id})")


__all__ = [
    "RichStreamRenderer",
    "RunStats",
    "Step",
    "StepManager",
    "RICH_AVAILABLE",
    "is_uuid",
    "sanitize_name",
    "format_file_size",
    "progress_bar",
    "print_agent_output",
    "print_agent_created",
    "print_agent_updated",
    "print_agent_deleted",
]
