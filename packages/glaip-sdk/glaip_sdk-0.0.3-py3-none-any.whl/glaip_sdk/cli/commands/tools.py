"""Tool management commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
import re

import click
from rich.console import Console
from rich.panel import Panel

from ..utils import (
    coerce_to_row,
    get_client,
    output_flags,
    output_list,
    output_result,
    resolve_resource,
)

console = Console()


@click.group(name="tools", no_args_is_help=True)
def tools_group():
    """Tool management operations."""
    pass


def _resolve_tool(ctx, client, ref, select=None):
    """Resolve tool reference (ID or name) with ambiguity handling."""
    return resolve_resource(
        ctx,
        ref,
        get_by_id=client.get_tool,
        find_by_name=client.find_tools,
        label="Tool",
        select=select,
    )


# ----------------------------- Helpers --------------------------------- #


def _extract_internal_name(code: str) -> str:
    """Extract plugin class name attribute from tool code."""
    m = re.search(r'^\s*name\s*:\s*str\s*=\s*"([^"]+)"', code, re.M)
    if not m:
        m = re.search(r'^\s*name\s*=\s*"([^"]+)"', code, re.M)
    if not m:
        raise click.ClickException(
            "Could not find plugin 'name' attribute in the tool file. "
            'Ensure your plugin class defines e.g. name: str = "my_tool".'
        )
    return m.group(1)


def _validate_name_match(provided: str | None, internal: str) -> str:
    """Validate provided --name against internal name; return effective name."""
    if provided and provided != internal:
        raise click.ClickException(
            f"--name '{provided}' does not match plugin internal name '{internal}'. "
            "Either update the code or pass a matching --name."
        )
    return provided or internal


def _check_duplicate_name(client, tool_name: str) -> None:
    """Raise if a tool with the same name already exists."""
    try:
        existing = client.find_tools(name=tool_name)
        if existing:
            raise click.ClickException(
                f"A tool named '{tool_name}' already exists. "
                "Please change your plugin's 'name' to a unique value, then re-run."
            )
    except click.ClickException:
        # Re-raise ClickException (intended error)
        raise
    except Exception:
        # Non-fatal: best-effort duplicate check for other errors
        pass


def _parse_tags(tags: str | None) -> list[str]:
    return [t.strip() for t in (tags.split(",") if tags else []) if t.strip()]


@tools_group.command(name="list")
@output_flags()
@click.pass_context
def list_tools(ctx):
    """List all tools."""
    try:
        client = get_client(ctx)
        tools = client.list_tools()

        # Define table columns: (data_key, header, style, width)
        columns = [
            ("id", "ID", "dim", 36),
            ("name", "Name", "cyan", None),
            ("framework", "Framework", "blue", None),
        ]

        # Transform function for safe dictionary access
        def transform_tool(tool):
            row = coerce_to_row(tool, ["id", "name", "framework"])
            # Ensure id is always a string
            row["id"] = str(row["id"])
            return row

        output_list(ctx, tools, "🔧 Available Tools", columns, transform_tool)

    except Exception as e:
        raise click.ClickException(str(e))


@tools_group.command()
@click.argument("file_arg", required=False, type=click.Path(exists=True))
@click.option(
    "--file",
    type=click.Path(exists=True),
    help="Tool file to upload (optional for metadata-only tools)",
)
@click.option(
    "--name",
    help="Tool name (required for metadata-only tools, extracted from script if file provided)",
)
@click.option(
    "--description",
    help="Tool description (optional - extracted from script if file provided)",
)
@click.option(
    "--tags",
    help="Comma-separated tags for the tool",
)
@output_flags()
@click.pass_context
def create(ctx, file_arg, file, name, description, tags):
    """Create a new tool."""
    try:
        client = get_client(ctx)

        # Allow positional file argument for better DX (matches examples)
        if not file and file_arg:
            file = file_arg

        # Validate required parameters based on creation method
        if not file:
            # Metadata-only tool creation
            if not name:
                raise click.ClickException(
                    "--name is required when creating metadata-only tools"
                )

        # Create tool based on whether file is provided
        if file:
            # File-based tool creation — validate internal plugin name, no rewriting
            with open(file, encoding="utf-8") as f:
                code_content = f.read()

            internal_name = _extract_internal_name(code_content)
            tool_name = _validate_name_match(name, internal_name)
            _check_duplicate_name(client, tool_name)

            # Upload the plugin code as-is (no rewrite)
            tool = client.create_tool_from_code(
                tool_name,
                code_content,
                framework="langchain",  # Always langchain
                description=description,
                tags=_parse_tags(tags),
            )
        else:
            # Metadata-only tool creation
            tool_kwargs = {}
            if name:
                tool_kwargs["name"] = name
            tool_kwargs["tool_type"] = "custom"  # Always custom
            tool_kwargs["framework"] = "langchain"  # Always langchain
            if description:
                tool_kwargs["description"] = description
            if tags:
                tool_kwargs["tags"] = _parse_tags(tags)

            tool = client.create_tool(**tool_kwargs)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(tool.model_dump(), indent=2))
        else:
            # Rich output
            creation_method = (
                "file upload (custom)" if file else "metadata only (native)"
            )
            panel = Panel(
                f"[green]✅ Tool '{tool.name}' created successfully via {creation_method}![/green]\n\n"
                f"ID: {tool.id}\n"
                f"Framework: {getattr(tool, 'framework', 'N/A')} (default)\n"
                f"Type: {getattr(tool, 'tool_type', 'N/A')} (auto-detected)\n"
                f"Description: {getattr(tool, 'description', 'No description')}",
                title="🔧 Tool Created",
                border_style="green",
            )
            console.print(panel)

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error creating tool: {e}[/red]")
        raise click.ClickException(str(e))


@tools_group.command()
@click.argument("tool_ref")
@click.option("--select", type=int, help="Choose among ambiguous matches (1-based)")
@output_flags()
@click.pass_context
def get(ctx, tool_ref, select):
    """Get tool details."""
    try:
        client = get_client(ctx)

        # Resolve tool with ambiguity handling
        tool = _resolve_tool(ctx, client, tool_ref, select)

        # Create result data with all available fields from backend
        result_data = {
            "id": str(getattr(tool, "id", "N/A")),
            "name": getattr(tool, "name", "N/A"),
            "tool_type": getattr(tool, "tool_type", "N/A"),
            "framework": getattr(tool, "framework", "N/A"),
            "version": getattr(tool, "version", "N/A"),
            "description": getattr(tool, "description", "N/A"),
        }

        output_result(
            ctx, result_data, title="Tool Details", panel_title=f"🔧 {tool.name}"
        )

    except Exception as e:
        raise click.ClickException(str(e))


@tools_group.command()
@click.argument("tool_id")
@click.option(
    "--file", type=click.Path(exists=True), help="New tool file for code update"
)
@click.option("--description", help="New description")
@click.option("--tags", help="Comma-separated tags")
@output_flags()
@click.pass_context
def update(ctx, tool_id, file, description, tags):
    """Update a tool (code or metadata)."""
    try:
        client = get_client(ctx)

        # Get tool by ID (no ambiguity handling needed)
        try:
            tool = client.get_tool_by_id(tool_id)
        except Exception as e:
            raise click.ClickException(f"Tool with ID '{tool_id}' not found: {e}")

        update_data = {}

        if description:
            update_data["description"] = description

        if tags:
            update_data["tags"] = [tag.strip() for tag in tags.split(",")]

        if file:
            # Update code
            updated_tool = tool.update(file_path=file)
            if ctx.obj.get("view") != "json":
                console.print(f"[green]✓[/green] Tool code updated from {file}")
        elif update_data:
            # Update metadata
            updated_tool = tool.update(**update_data)
            if ctx.obj.get("view") != "json":
                console.print("[green]✓[/green] Tool metadata updated")
        else:
            if ctx.obj.get("view") != "json":
                console.print("[yellow]No updates specified[/yellow]")
            return

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(updated_tool.model_dump(), indent=2))
        else:
            console.print(
                f"[green]✅ Tool '{updated_tool.name}' updated successfully[/green]"
            )

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error updating tool: {e}[/red]")
        raise click.ClickException(str(e))


@tools_group.command()
@click.argument("tool_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
@output_flags()
@click.pass_context
def delete(ctx, tool_id, yes):
    """Delete a tool."""
    try:
        client = get_client(ctx)

        # Get tool by ID (no ambiguity handling needed)
        try:
            tool = client.get_tool_by_id(tool_id)
        except Exception as e:
            raise click.ClickException(f"Tool with ID '{tool_id}' not found: {e}")

        # Confirm deletion
        if not yes and not click.confirm(
            f"Are you sure you want to delete tool '{tool.name}'?"
        ):
            if ctx.obj.get("view") != "json":
                console.print("Deletion cancelled.")
            return

        tool.delete()

        if ctx.obj.get("view") == "json":
            click.echo(
                json.dumps(
                    {"success": True, "message": f"Tool '{tool.name}' deleted"},
                    indent=2,
                )
            )
        else:
            console.print(f"[green]✅ Tool '{tool.name}' deleted successfully[/green]")

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error deleting tool: {e}[/red]")
        raise click.ClickException(str(e))


@tools_group.command()
@click.argument("tool_id")
@output_flags()
@click.pass_context
def script(ctx, tool_id):
    """Get tool script content."""
    try:
        client = get_client(ctx)

        # Get tool by ID (no ambiguity handling needed)
        try:
            tool = client.get_tool_by_id(tool_id)
        except Exception as e:
            raise click.ClickException(f"Tool with ID '{tool_id}' not found: {e}")

        # Get tool script content
        script_content = client.tools.get_tool_script(tool_id)

        if ctx.obj.get("view") == "json":
            click.echo(
                json.dumps(
                    {
                        "tool_id": tool_id,
                        "tool_name": tool.name,
                        "script": script_content,
                    },
                    indent=2,
                )
            )
        elif ctx.obj.get("output"):
            # Save to file
            output_file = ctx.obj.get("output")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(script_content)
            console.print(f"[green]✅ Tool script saved to {output_file}[/green]")
        else:
            # Display in terminal
            console.print(
                Panel(
                    script_content,
                    title=f"🔧 Tool Script: {tool.name}",
                    border_style="cyan",
                )
            )

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error getting tool script: {e}[/red]")
        raise click.ClickException(str(e))


@tools_group.command()
@click.argument("tool_id")
@click.option(
    "--file",
    type=click.Path(exists=True),
    required=True,
    help="New tool file for code update",
)
@click.option("--name", help="New tool name")
@click.option("--description", help="New description")
@click.option("--tags", help="Comma-separated tags")
@output_flags()
@click.pass_context
def upload_update(ctx, tool_id, file, name, description, tags):
    """Update a tool plugin via file upload."""
    try:
        client = get_client(ctx)

        # Prepare update data
        update_data = {}
        if name:
            update_data["name"] = name
        if description:
            update_data["description"] = description
        if tags:
            update_data["tags"] = [tag.strip() for tag in tags.split(",")]

        # Update tool via file upload
        updated_tool = client.tools.update_tool_via_file(tool_id, file, **update_data)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(updated_tool.model_dump(), indent=2))
        else:
            console.print(
                f"[green]✅ Tool '{updated_tool.name}' updated successfully via file upload[/green]"
            )
            console.print(f"[blue]📁 File: {file}[/blue]")

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error updating tool: {e}[/red]")
        raise click.ClickException(str(e))
