"""Agent CLI commands for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from glaip_sdk.config.constants import DEFAULT_AGENT_RUN_TIMEOUT, DEFAULT_MODEL
from glaip_sdk.exceptions import AgentTimeoutError
from glaip_sdk.utils import is_uuid

from ..utils import (
    _fuzzy_pick_for_resources,
    build_renderer,
    coerce_to_row,
    get_client,
    output_flags,
    output_list,
    output_result,
    resolve_resource,
)

console = Console()


def _display_run_suggestions(agent):
    """Display helpful suggestions for running the agent."""
    console.print()
    console.print(
        Panel(
            f"[bold blue]💡 Next Steps:[/bold blue]\n\n"
            f"🚀 Run this agent:\n"
            f'   [green]aip agents run {agent.id} "Your message here"[/green]\n\n'
            f"📋 Or use the agent name:\n"
            f'   [green]aip agents run "{agent.name}" "Your message here"[/green]\n\n'
            f"🔧 Available options:\n"
            f"   [dim]--chat-history[/dim]  Include previous conversation\n"
            f"   [dim]--file[/dim]          Attach files\n"
            f"   [dim]--input[/dim]         Alternative input method\n"
            f"   [dim]--timeout[/dim]       Set execution timeout\n"
            f"   [dim]--save[/dim]          Save transcript to file\n"
            f"   [dim]--verbose[/dim]       Show detailed execution\n\n"
            f"💡 [dim]Input text can be positional OR use --input flag (both work!)[/dim]",
            title="🤖 Ready to Run Agent",
            border_style="blue",
            padding=(0, 1),
        )
    )


def _format_datetime(dt):
    """Format datetime object to readable string."""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    elif dt is None:
        return "N/A"
    return dt


def _fetch_full_agent_details(client, agent):
    """Fetch full agent details by ID to ensure all fields are populated."""
    try:
        agent_id = str(getattr(agent, "id", "")).strip()
        if agent_id:
            return client.agents.get_agent_by_id(agent_id)
    except Exception:
        # If fetching full details fails, continue with the resolved object
        pass
    return agent


def _build_agent_result_data(agent):
    """Build standardized result data for agent display."""
    return {
        "id": str(getattr(agent, "id", "N/A")),
        "name": getattr(agent, "name", "N/A"),
        "type": getattr(agent, "type", "N/A"),
        "framework": getattr(agent, "framework", "N/A"),
        "version": getattr(agent, "version", "N/A"),
        "description": getattr(agent, "description", "N/A"),
        "instruction": getattr(agent, "instruction", "") or "-",
        "created_at": _format_datetime(getattr(agent, "created_at", "N/A")),
        "updated_at": _format_datetime(getattr(agent, "updated_at", "N/A")),
        "metadata": getattr(agent, "metadata", "N/A"),
        "language_model_id": getattr(agent, "language_model_id", "N/A"),
        "agent_config": getattr(agent, "agent_config", "N/A"),
        "tool_configs": getattr(agent, "tool_configs", {}),
        "tools": getattr(agent, "tools", []),
        "agents": getattr(agent, "agents", []),
        "mcps": getattr(agent, "mcps", []),
        "a2a_profile": getattr(agent, "a2a_profile", "N/A"),
    }


def _get_agent_attributes(agent):
    """Dynamically get all relevant agent attributes for export."""
    # Exclude these attributes from export (methods, private attrs, computed properties)
    exclude_attrs = {
        "id",
        "created_at",
        "updated_at",  # System-managed fields
        "_client",
        "_raw_data",  # Internal fields
    }

    # Methods and callable attributes to exclude
    exclude_callables = {
        "model_dump",
        "dict",
        "json",  # Pydantic methods
        "get",
        "post",
        "put",
        "delete",  # HTTP methods
        "save",
        "refresh",
        "update",  # ORM methods
    }

    export_data = {}

    # Method 1: Try Pydantic model_dump() if available (best for structured data)
    if hasattr(agent, "model_dump") and callable(agent.model_dump):
        try:
            # Get all model fields
            all_data = agent.model_dump()
            # Filter out excluded attributes
            for key, value in all_data.items():
                if key not in exclude_attrs and key not in exclude_callables:
                    export_data[key] = value
            return export_data
        except Exception:
            # Fall back to manual attribute detection
            pass

    # Method 2: Manual attribute inspection with filtering
    # Get all non-private, non-method attributes
    all_attrs = []
    if hasattr(agent, "__dict__"):
        all_attrs.extend(agent.__dict__.keys())
    if hasattr(agent, "__annotations__"):
        all_attrs.extend(agent.__annotations__.keys())

    # Remove duplicates and filter
    all_attrs = list(set(all_attrs))

    for attr in all_attrs:
        # Skip excluded attributes
        if (
            attr in exclude_attrs
            or attr.startswith("_")  # Private attributes
            or attr in exclude_callables
        ):
            continue

        # Skip callable attributes (methods, functions)
        attr_value = getattr(agent, attr, None)
        if callable(attr_value):
            continue

        # Add the attribute to export data
        export_data[attr] = attr_value

    return export_data


def _build_agent_export_data(agent):
    """Build comprehensive export data for agent (always includes all fields)."""
    # Get all available agent attributes dynamically
    all_agent_data = _get_agent_attributes(agent)

    # Always include all detected attributes for comprehensive export
    # Add default timeout if not present
    if "timeout" not in all_agent_data:
        all_agent_data["timeout"] = DEFAULT_AGENT_RUN_TIMEOUT
    return all_agent_data


def _get_agent_model_name(agent):
    """Extract model name from agent configuration."""
    # Try different possible locations for model name
    if hasattr(agent, "agent_config") and agent.agent_config:
        if isinstance(agent.agent_config, dict):
            return agent.agent_config.get("lm_name") or agent.agent_config.get("model")

    if hasattr(agent, "model") and agent.model:
        return agent.model

    # Default fallback
    return DEFAULT_MODEL


def _extract_tool_ids(agent):
    """Extract tool IDs from agent tools list for import compatibility."""
    tools = getattr(agent, "tools", [])
    if not tools:
        return []

    ids = []
    for tool in tools:
        if isinstance(tool, dict):
            tool_id = tool.get("id")
            if tool_id:
                ids.append(tool_id)
            else:
                # Fallback to name if ID not available
                name = tool.get("name", "")
                if name:
                    ids.append(name)
        elif hasattr(tool, "id"):
            ids.append(tool.id)
        elif hasattr(tool, "name"):
            ids.append(tool.name)
        else:
            ids.append(str(tool))
    return ids


def _extract_agent_ids(agent):
    """Extract agent IDs from agent agents list for import compatibility."""
    agents = getattr(agent, "agents", [])
    if not agents:
        return []

    ids = []
    for sub_agent in agents:
        if isinstance(sub_agent, dict):
            agent_id = sub_agent.get("id")
            if agent_id:
                ids.append(agent_id)
            else:
                # Fallback to name if ID not available
                name = sub_agent.get("name", "")
                if name:
                    ids.append(name)
        elif hasattr(sub_agent, "id"):
            ids.append(sub_agent.id)
        elif hasattr(sub_agent, "name"):
            ids.append(sub_agent.name)
        else:
            ids.append(str(sub_agent))
    return ids


def _export_agent_to_file(agent, file_path: Path, format: str = "json"):
    """Export agent to file (JSON or YAML) with comprehensive data."""
    export_data = _build_agent_export_data(agent)

    if format.lower() == "yaml" or file_path.suffix.lower() in [".yaml", ".yml"]:
        _write_yaml_to_file(file_path, export_data)
    else:
        _write_json_to_file(file_path, export_data)


def _load_agent_from_file(file_path: Path) -> dict[str, Any]:
    """Load agent data from JSON or YAML file."""
    if file_path.suffix.lower() in [".yaml", ".yml"]:
        return _read_yaml_from_file(file_path)
    else:
        return _read_json_from_file(file_path)


def _read_yaml_from_file(file_path: Path) -> dict[str, Any]:
    """Read YAML data from file."""
    try:
        import yaml
    except ImportError:
        raise click.ClickException(
            "PyYAML is required for YAML import. Install with: pip install PyYAML"
        )

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Handle instruction_lines array format for user-friendly YAML
    if "instruction_lines" in data and isinstance(data["instruction_lines"], list):
        data["instruction"] = "\n\n".join(data["instruction_lines"])
        del data["instruction_lines"]

    # Handle instruction as list from YAML export (convert back to string)
    if "instruction" in data and isinstance(data["instruction"], list):
        data["instruction"] = "\n\n".join(data["instruction"])

    return data


def _extract_ids_from_export(items: list) -> list[str]:
    """Extract IDs from export format (list of dicts with id/name fields)."""
    ids = []
    for item in items:
        if isinstance(item, dict):
            item_id = item.get("id")
            if item_id:
                ids.append(item_id)
        elif isinstance(item, str):
            ids.append(item)
    return ids


def _convert_export_to_import_format(data: dict[str, Any]) -> dict[str, Any]:
    """Convert export format to import-compatible format (extract IDs from objects)."""
    import_data = data.copy()

    # Convert tools from dicts to IDs
    if "tools" in import_data and isinstance(import_data["tools"], list):
        import_data["tools"] = _extract_ids_from_export(import_data["tools"])

    # Convert agents from dicts to IDs
    if "agents" in import_data and isinstance(import_data["agents"], list):
        import_data["agents"] = _extract_ids_from_export(import_data["agents"])

    return import_data


def _write_json_to_file(file_path: Path, data: dict[str, Any], indent: int = 2) -> None:
    """Write data to JSON file with consistent formatting."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)


def _write_yaml_to_file(file_path: Path, data: dict[str, Any]) -> None:
    """Write data to YAML file with user-friendly formatting."""
    try:
        import yaml
    except ImportError:
        raise click.ClickException(
            "PyYAML is required for YAML export. Install with: pip install PyYAML"
        )

    # Custom YAML dumper for user-friendly instruction formatting
    class LiteralString(str):
        pass

    def literal_string_representer(dumper, data):
        # Use literal block scalar (|) for multiline strings to preserve formatting
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    # Add custom representer to the YAML dumper
    yaml.add_representer(LiteralString, literal_string_representer)

    # Convert instruction to LiteralString for proper formatting
    if "instruction" in data and data["instruction"]:
        data["instruction"] = LiteralString(data["instruction"])

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )


def _read_json_from_file(file_path: Path) -> dict[str, Any]:
    """Read JSON data from file with validation."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() != ".json":
        raise ValueError(
            f"Unsupported file format: {file_path.suffix}. Only JSON files are supported."
        )

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def _merge_import_with_cli_args(
    import_data: dict[str, Any],
    cli_args: dict[str, Any],
    array_fields: list[str] = None,
) -> dict[str, Any]:
    """Merge imported data with CLI arguments, preferring CLI args.

    Args:
        import_data: Data loaded from import file
        cli_args: Arguments passed via CLI
        array_fields: Fields that should be combined (merged) rather than replaced

    Returns:
        Merged data dictionary
    """
    if array_fields is None:
        array_fields = ["tools", "agents"]

    merged = {}

    for key, cli_value in cli_args.items():
        if cli_value is not None and (
            not isinstance(cli_value, list | tuple) or len(cli_value) > 0
        ):
            # CLI value takes precedence (for non-empty values)
            if key in array_fields and key in import_data:
                # For array fields, combine CLI and imported values
                import_value = import_data[key]
                if isinstance(import_value, list):
                    merged[key] = list(cli_value) + import_value
                else:
                    merged[key] = cli_value
            else:
                merged[key] = cli_value
        elif key in import_data:
            # Use imported value if no CLI value
            merged[key] = import_data[key]

    # Add any import-only fields
    for key, import_value in import_data.items():
        if key not in merged:
            merged[key] = import_value

    return merged


def _resolve_resources_by_name(
    client, items: tuple[str, ...], resource_type: str, find_func, label: str
) -> list[str]:
    """Resolve resource names/IDs to IDs, handling ambiguity.

    Args:
        client: API client
        items: Tuple of resource names/IDs
        resource_type: Type of resource ("tool" or "agent")
        find_func: Function to find resources by name
        label: Label for error messages

    Returns:
        List of resolved resource IDs
    """
    out = []
    for ref in list(items or ()):
        if is_uuid(ref):
            out.append(ref)
            continue

        matches = find_func(name=ref)
        if not matches:
            raise click.ClickException(f"{label} not found: {ref}")
        if len(matches) > 1:
            raise click.ClickException(
                f"Multiple {resource_type}s named '{ref}'. Use ID instead."
            )
        out.append(str(matches[0].id))
    return out


def _display_agent_creation_success(agent, model=None, default_model=DEFAULT_MODEL):
    """Display success message for agent creation/update."""
    lm = getattr(agent, "model", None)
    if not lm:
        cfg = getattr(agent, "agent_config", {}) or {}
        lm = (
            cfg.get("lm_name")
            or cfg.get("model")
            or model  # Use provided model if specified
            or f"{default_model} (backend default)"
        )

    panel = Panel(
        f"[green]✅ Agent '{agent.name}' created successfully![/green]\n\n"
        f"ID: {agent.id}\n"
        f"Model: {lm}\n"
        f"Type: {getattr(agent, 'type', 'config')}\n"
        f"Framework: {getattr(agent, 'framework', 'langchain')}\n"
        f"Version: {getattr(agent, 'version', '1.0')}",
        title="🤖 Agent Created",
        border_style="green",
        padding=(0, 1),
    )
    console.print(panel)


def _display_agent_update_success(agent):
    """Display success message for agent update."""
    console.print(Text(f"[green]✅ Agent '{agent.name}' updated successfully[/green]"))


def _display_agent_details(ctx, client, agent):
    """Display full agent details in a standardized format."""
    # Fetch full details to ensure all fields are populated
    full_agent = _fetch_full_agent_details(client, agent)

    # Build result data
    result_data = _build_agent_result_data(full_agent)

    # Display using output_result
    output_result(
        ctx,
        result_data,
        title="Agent Details",
        panel_title=f"🤖 {full_agent.name}",
    )


@click.group(name="agents", no_args_is_help=True)
def agents_group():
    """Agent management operations."""
    pass


def _resolve_agent(ctx, client, ref, select=None, interface_preference="fuzzy"):
    """Resolve agent reference (ID or name) with ambiguity handling.

    Args:
        interface_preference: "fuzzy" for fuzzy picker, "questionary" for up/down list
    """
    return resolve_resource(
        ctx,
        ref,
        get_by_id=client.agents.get_agent_by_id,
        find_by_name=client.agents.find_agents,
        label="Agent",
        select=select,
        interface_preference=interface_preference,
    )


@agents_group.command(name="list")
@click.option(
    "--simple", is_flag=True, help="Show simple table without interactive picker"
)
@output_flags()
@click.pass_context
def list_agents(ctx, simple):
    """List all agents."""
    try:
        client = get_client(ctx)
        agents = client.agents.list_agents()

        # Define table columns: (data_key, header, style, width)
        columns = [
            ("id", "ID", "dim", 36),
            ("name", "Name", "cyan", None),
            ("type", "Type", "yellow", None),
            ("framework", "Framework", "blue", None),
            ("version", "Version", "green", None),
        ]

        # Transform function for safe attribute access
        def transform_agent(agent):
            row = coerce_to_row(agent, ["id", "name", "type", "framework", "version"])
            # Ensure id is always a string
            row["id"] = str(row["id"])
            return row

        # Use fuzzy picker for interactive agent selection and details (default behavior)
        # Skip if --simple flag is used
        if not simple and console.is_terminal and os.isatty(1) and len(agents) > 0:
            picked_agent = _fuzzy_pick_for_resources(agents, "agent", "")
            if picked_agent:
                _display_agent_details(ctx, client, picked_agent)
                return

        # Show simple table (either --simple flag or non-interactive)
        output_list(ctx, agents, "🤖 Available Agents", columns, transform_agent)

    except Exception as e:
        raise click.ClickException(str(e))


@agents_group.command()
@click.argument("agent_ref")
@click.option("--select", type=int, help="Choose among ambiguous matches (1-based)")
@click.option(
    "--export",
    type=click.Path(dir_okay=False, writable=True),
    help="Export complete agent configuration to file (format auto-detected from .json/.yaml extension)",
)
@output_flags()
@click.pass_context
def get(ctx, agent_ref, select, export):
    """Get agent details.

    Examples:
        aip agents get my-agent
        aip agents get my-agent --export agent.json    # Exports complete configuration as JSON
        aip agents get my-agent --export agent.yaml    # Exports complete configuration as YAML
    """
    try:
        client = get_client(ctx)

        # Resolve agent with ambiguity handling - use questionary interface for traditional UX
        agent = _resolve_agent(
            ctx, client, agent_ref, select, interface_preference="questionary"
        )

        # Handle export option
        if export:
            export_path = Path(export)
            # Auto-detect format from file extension
            if export_path.suffix.lower() in [".yaml", ".yml"]:
                detected_format = "yaml"
            else:
                detected_format = "json"

            # Always export comprehensive data - re-fetch agent with full details
            try:
                agent = client.agents.get_agent_by_id(agent.id)
            except Exception as e:
                console.print(
                    Text(f"[yellow]⚠️  Could not fetch full agent details: {e}[/yellow]")
                )
                console.print(
                    Text("[yellow]⚠️  Proceeding with available data[/yellow]")
                )

            _export_agent_to_file(agent, export_path, detected_format)
            console.print(
                Text(
                    f"[green]✅ Complete agent configuration exported to: {export_path} (format: {detected_format})[/green]"
                )
            )

        # Display full agent details using the standardized helper
        _display_agent_details(ctx, client, agent)

        # Show run suggestions (only in rich mode, not JSON)
        if ctx.obj.get("view") != "json":
            _display_run_suggestions(agent)

    except Exception as e:
        raise click.ClickException(str(e))


@agents_group.command()
@click.argument("agent_ref")
@click.argument("input_text", required=False)
@click.option("--select", type=int, help="Choose among ambiguous matches (1-based)")
@click.option("--input", "input_option", help="Input text for the agent")
@click.option("--chat-history", help="JSON string of chat history")
@click.option(
    "--timeout",
    default=DEFAULT_AGENT_RUN_TIMEOUT,
    type=int,
    help="Agent execution timeout in seconds (default: 300s)",
)
@click.option(
    "--save",
    type=click.Path(dir_okay=False, writable=True),
    help="Save transcript to file (md or json)",
)
@click.option(
    "--file",
    "files",
    multiple=True,
    type=click.Path(exists=True),
    help="Attach file(s)",
)
@click.option(
    "--verbose/--no-verbose",
    default=False,
    help="Show detailed SSE events during streaming",
)
@output_flags()
@click.pass_context
def run(
    ctx,
    agent_ref,
    select,
    input_text,
    input_option,
    chat_history,
    timeout,
    save,
    files,
    verbose,
):
    """Run an agent with input text.

    Usage: aip agents run <agent_ref> <input_text> [OPTIONS]

    Examples:
        aip agents run my-agent "Hello world"
        aip agents run agent-123 "Process this data" --timeout 600
        aip agents run my-agent --input "Hello world"  # Legacy style
    """
    # Handle input precedence: --input option overrides positional argument
    final_input_text = input_option if input_option else input_text

    # Validate that we have input text from either positional argument or --input option
    if not final_input_text:
        raise click.ClickException(
            "Input text is required. Use either positional argument or --input option."
        )

    try:
        client = get_client(ctx)

        # Resolve agent by ID or name (align with other commands) - use fuzzy interface
        agent = _resolve_agent(
            ctx, client, agent_ref, select, interface_preference="fuzzy"
        )

        # Parse chat history if provided
        parsed_chat_history = None
        if chat_history:
            try:
                parsed_chat_history = json.loads(chat_history)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON in chat history")

        # Create custom renderer with CLI flags
        tty_enabled = bool((ctx.obj or {}).get("tty", True))

        # Build renderer and capturing console
        renderer, working_console = build_renderer(
            ctx,
            save_path=save,
            verbose=verbose,
            tty_enabled=tty_enabled,
        )

        # Set HTTP timeout to match agent timeout exactly
        # This ensures the agent timeout controls the HTTP timeout
        try:
            client.timeout = float(timeout)
        except Exception:
            pass

        # Ensure timeout is applied to the root client and subclients share its session
        run_kwargs = {
            "agent_id": agent.id,
            "message": final_input_text,
            "files": list(files),
            "agent_name": agent.name,  # Pass agent name for better display
            "tty": tty_enabled,
        }

        # Add optional parameters
        if parsed_chat_history:
            run_kwargs["chat_history"] = parsed_chat_history

        # Pass custom renderer if available
        if renderer is not None:
            run_kwargs["renderer"] = renderer

        # Pass timeout to client (verbose mode is handled by the renderer)
        result = client.agents.run_agent(**run_kwargs, timeout=timeout)

        # Check if renderer already printed output (for streaming renderers)
        # Note: Auto-paging is handled by the renderer when view=="rich"
        printed_by_renderer = bool(renderer)

        # Resolve selected view from context (output_flags() stores it here)
        selected_view = (ctx.obj or {}).get("view", "rich")

        # Handle output format for fallback
        # Only print here if nothing was printed by the renderer
        if not printed_by_renderer:
            if selected_view == "json":
                click.echo(json.dumps({"output": result}, indent=2))
            elif selected_view == "md":
                click.echo(f"# Assistant\n\n{result}")
            elif selected_view == "plain":
                click.echo(result)

        # Save transcript if requested
        if save:
            ext = (save.rsplit(".", 1)[-1] or "").lower()
            if ext == "json":
                # Save both the result and captured output
                save_data = {
                    "output": result or "",
                    "full_debug_output": getattr(
                        working_console, "get_captured_output", lambda: ""
                    )(),
                    "timestamp": "captured during agent execution",
                }
                content = json.dumps(save_data, indent=2)
            else:
                # For markdown/text files, save the full captured output if available
                # Get the full captured output including all tool panels and debug info (if available)
                full_output = getattr(
                    working_console, "get_captured_output", lambda: ""
                )()
                if full_output:
                    content = f"# Agent Debug Log\n\n{full_output}\n\n---\n\n## Final Result\n\n{result or ''}\n"
                else:
                    # Fallback to simple format
                    content = f"# Assistant\n\n{result or ''}\n"

            with open(save, "w", encoding="utf-8") as f:
                f.write(content)
            console.print(Text(f"[green]Full debug output saved to: {save}[/green]"))

    except AgentTimeoutError as e:
        # Handle agent timeout errors with specific messages
        error_msg = str(e)
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": error_msg}, indent=2))
        # Don't print the error message here - Click.ClickException will handle it
        raise click.ClickException(error_msg)
    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        # Don't print the error message here - Click.ClickException will handle it
        raise click.ClickException(str(e))


@agents_group.command()
@click.option("--name", help="Agent name")
@click.option("--instruction", help="Agent instruction (prompt)")
@click.option(
    "--model",
    help=f"Language model to use (e.g., {DEFAULT_MODEL}, default: {DEFAULT_MODEL})",
)
@click.option("--tools", multiple=True, help="Tool names or IDs to attach")
@click.option("--agents", multiple=True, help="Sub-agent names or IDs to attach")
@click.option(
    "--timeout",
    default=DEFAULT_AGENT_RUN_TIMEOUT,
    type=int,
    help="Agent execution timeout in seconds (default: 300s)",
)
@click.option(
    "--import",
    "import_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Import agent configuration from JSON file",
)
@output_flags()
@click.pass_context
def create(
    ctx,
    name,
    instruction,
    model,
    tools,
    agents,
    timeout,
    import_file,
):
    """Create a new agent.

    Examples:
        aip agents create --name "My Agent" --instruction "You are a helpful assistant"
        aip agents create --import agent.json
    """
    try:
        client = get_client(ctx)

        # Handle import from file
        if import_file:
            import_data = _load_agent_from_file(Path(import_file))

            # Convert export format to import-compatible format
            import_data = _convert_export_to_import_format(import_data)

            # Merge CLI args with imported data
            cli_args = {
                "name": name,
                "instruction": instruction,
                "model": model,
                "tools": tools or (),
                "agents": agents or (),
                "timeout": timeout if timeout != DEFAULT_AGENT_RUN_TIMEOUT else None,
            }

            merged_data = _merge_import_with_cli_args(import_data, cli_args)

            # Extract merged values
            name = merged_data.get("name")
            instruction = merged_data.get("instruction")
            model = merged_data.get("model")
            tools = tuple(merged_data.get("tools", ()))
            agents = tuple(merged_data.get("agents", ()))
            timeout = merged_data.get("timeout", DEFAULT_AGENT_RUN_TIMEOUT)

        # Validate required fields
        if not name:
            raise click.ClickException("Agent name is required (--name or --import)")
        if not instruction:
            raise click.ClickException(
                "Agent instruction is required (--instruction or --import)"
            )

        # Resolve tool and agent references: accept names or IDs
        resolved_tools = _resolve_resources_by_name(
            client, tools, "tool", client.find_tools, "Tool"
        )
        resolved_agents = _resolve_resources_by_name(
            client, agents, "agent", client.find_agents, "Agent"
        )

        # Create agent with comprehensive attribute support
        create_kwargs = {
            "name": name,
            "instruction": instruction,
            "tools": resolved_tools or None,
            "agents": resolved_agents or None,
            "timeout": timeout,
        }

        # Add model if specified (prioritize CLI model over imported model)
        if model:
            create_kwargs["model"] = model
        elif (
            import_file
            and "agent_config" in merged_data
            and merged_data["agent_config"]
        ):
            # Use lm_name from agent_config for cloning
            agent_config = merged_data["agent_config"]
            if isinstance(agent_config, dict) and "lm_name" in agent_config:
                create_kwargs["model"] = agent_config["lm_name"]

        # If importing from file, include all other detected attributes
        if import_file:
            # Add all other attributes from import data (excluding already handled ones and system-only fields)
            excluded_fields = {
                "name",
                "instruction",
                "model",
                "tools",
                "agents",
                "timeout",
                # System-only fields that shouldn't be passed to create_agent
                "id",
                "created_at",
                "updated_at",
                "agent_config",
                "language_model_id",
                "type",
                "framework",
                "version",
                "tool_configs",
                "mcps",
                "a2a_profile",
            }
            for key, value in merged_data.items():
                if key not in excluded_fields and value is not None:
                    create_kwargs[key] = value

        agent = client.agents.create_agent(**create_kwargs)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(agent.model_dump(), indent=2))
        else:
            # Rich output
            _display_agent_creation_success(agent, model)

            # Show run suggestions (only in rich mode, not JSON)
            if ctx.obj.get("view") != "json":
                _display_run_suggestions(agent)

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(Text(f"[red]Error creating agent: {e}[/red]"))
        raise click.ClickException(str(e))


@agents_group.command()
@click.argument("agent_id")
@click.option("--name", help="New agent name")
@click.option("--instruction", help="New instruction")
@click.option("--tools", multiple=True, help="New tool names or IDs")
@click.option("--agents", multiple=True, help="New sub-agent names")
@click.option("--timeout", type=int, help="New timeout value")
@click.option(
    "--import",
    "import_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Import agent configuration from JSON file",
)
@output_flags()
@click.pass_context
def update(ctx, agent_id, name, instruction, tools, agents, timeout, import_file):
    """Update an existing agent.

    Examples:
        aip agents update my-agent --instruction "New instruction"
        aip agents update my-agent --import agent.json
    """
    try:
        client = get_client(ctx)

        # Get agent by ID (no ambiguity handling needed)
        try:
            agent = client.agents.get_agent_by_id(agent_id)
        except Exception as e:
            raise click.ClickException(f"Agent with ID '{agent_id}' not found: {e}")

        # Handle import from file
        if import_file:
            import_data = _load_agent_from_file(Path(import_file))

            # Convert export format to import-compatible format
            import_data = _convert_export_to_import_format(import_data)

            # Merge CLI args with imported data
            cli_args = {
                "name": name,
                "instruction": instruction,
                "tools": tools or (),
                "agents": agents or (),
                "timeout": timeout,
            }

            merged_data = _merge_import_with_cli_args(import_data, cli_args)

            # Extract merged values
            name = merged_data.get("name")
            instruction = merged_data.get("instruction")
            tools = tuple(merged_data.get("tools", ()))
            agents = tuple(merged_data.get("agents", ()))
            timeout = merged_data.get("timeout")

        # Build update data with comprehensive attribute support
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if instruction is not None:
            update_data["instruction"] = instruction
        if tools:
            update_data["tools"] = list(tools)
        if agents:
            update_data["agents"] = list(agents)
        if timeout is not None:
            update_data["timeout"] = timeout

        # If importing from file, include all other detected attributes
        if import_file:
            # Add all other attributes from import data (excluding already handled ones and system-only fields)
            excluded_fields = {
                "name",
                "instruction",
                "tools",
                "agents",
                "timeout",
                # System-only fields that shouldn't be passed to update_agent
                "id",
                "created_at",
                "updated_at",
                "agent_config",
                "type",
                "framework",
                "version",
                "tool_configs",
                "mcps",
                "a2a_profile",
            }
            for key, value in merged_data.items():
                if key not in excluded_fields and value is not None:
                    update_data[key] = value

        if not update_data:
            raise click.ClickException("No update fields specified")

        # Update agent
        updated_agent = client.agents.update_agent(agent.id, **update_data)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(updated_agent.model_dump(), indent=2))
        else:
            _display_agent_update_success(updated_agent)

            # Show run suggestions (only in rich mode, not JSON)
            if ctx.obj.get("view") != "json":
                _display_run_suggestions(updated_agent)

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(Text(f"[red]Error updating agent: {e}[/red]"))
        raise click.ClickException(str(e))


@agents_group.command()
@click.argument("agent_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
@output_flags()
@click.pass_context
def delete(ctx, agent_id, yes):
    """Delete an agent."""
    try:
        client = get_client(ctx)

        # Get agent by ID (no ambiguity handling needed)
        try:
            agent = client.agents.get_agent_by_id(agent_id)
        except Exception as e:
            raise click.ClickException(f"Agent with ID '{agent_id}' not found: {e}")

        # Confirm deletion
        if not yes and not click.confirm(
            f"Are you sure you want to delete agent '{agent.name}'?"
        ):
            if ctx.obj.get("view") != "json":
                console.print(Text("Deletion cancelled."))
            return

        client.agents.delete_agent(agent.id)

        if ctx.obj.get("view") == "json":
            click.echo(
                json.dumps(
                    {"success": True, "message": f"Agent '{agent.name}' deleted"},
                    indent=2,
                )
            )
        else:
            console.print(
                Text(f"[green]✅ Agent '{agent.name}' deleted successfully[/green]")
            )

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(Text(f"[red]Error deleting agent: {e}[/red]"))
        raise click.ClickException(str(e))
