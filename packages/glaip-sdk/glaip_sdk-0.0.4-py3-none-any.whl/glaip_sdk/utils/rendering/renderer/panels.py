"""Panel rendering utilities for the renderer package.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text


def create_main_panel(content: str, title: str, theme: str = "dark") -> Panel:
    """Create a main content panel.

    Args:
        content: The content to display
        title: Panel title
        theme: Color theme ("dark" or "light")

    Returns:
        Rich Panel instance
    """
    if content.strip():
        return Panel(
            Markdown(content, code_theme=("monokai" if theme == "dark" else "github")),
            title=title,
            border_style="green",
        )
    else:
        # Placeholder panel
        placeholder = Text("Processing...", style="dim")
        return Panel(
            placeholder,
            title=title,
            border_style="green",
        )


def create_tool_panel(
    title: str,
    content: str,
    status: str = "running",
    theme: str = "dark",
    is_delegation: bool = False,
) -> Panel:
    """Create a tool execution panel.

    Args:
        title: Tool name/title
        content: Tool output content
        status: Tool execution status
        theme: Color theme
        is_delegation: Whether this is a delegation tool

    Returns:
        Rich Panel instance
    """
    mark = "✓" if status == "finished" else "⟳"
    border_style = "magenta" if is_delegation else "blue"

    return Panel(
        Markdown(
            content or "Processing...",
            code_theme=("monokai" if theme == "dark" else "github"),
        ),
        title=f"{title}  {mark}",
        border_style=border_style,
    )


def create_context_panel(
    title: str,
    content: str,
    status: str = "running",
    theme: str = "dark",
    is_delegation: bool = False,
) -> Panel:
    """Create a context/sub-agent panel.

    Args:
        title: Context title
        content: Context content
        status: Execution status
        theme: Color theme
        is_delegation: Whether this is a delegation context

    Returns:
        Rich Panel instance
    """
    mark = "✓" if status == "finished" else "⟳"
    border_style = "magenta" if is_delegation else "cyan"

    return Panel(
        Markdown(
            content,
            code_theme=("monokai" if theme == "dark" else "github"),
        ),
        title=f"{title}  {mark}",
        border_style=border_style,
    )


def create_final_panel(
    content: str, title: str = "Final Result", theme: str = "dark"
) -> Panel:
    """Create a final result panel.

    Args:
        content: Final result content
        title: Panel title
        theme: Color theme

    Returns:
        Rich Panel instance
    """
    return Panel(
        Markdown(content, code_theme=("monokai" if theme == "dark" else "github")),
        title=title,
        border_style="green",
        padding=(0, 1),
    )
