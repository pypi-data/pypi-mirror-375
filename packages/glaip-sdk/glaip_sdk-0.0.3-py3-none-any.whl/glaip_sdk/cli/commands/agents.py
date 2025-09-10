"""Agent CLI commands for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel

from glaip_sdk.config.constants import DEFAULT_AGENT_RUN_TIMEOUT, DEFAULT_MODEL
from glaip_sdk.exceptions import AgentTimeoutError
from glaip_sdk.utils import is_uuid

from ..utils import (
    build_renderer,
    coerce_to_row,
    get_client,
    output_flags,
    output_list,
    output_result,
    resolve_resource,
)

console = Console()


def _format_datetime(dt):
    """Format datetime object to readable string."""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    elif dt is None:
        return "N/A"
    return dt


@click.group(name="agents", no_args_is_help=True)
def agents_group():
    """Agent management operations."""
    pass


def _resolve_agent(ctx, client, ref, select=None):
    """Resolve agent reference (ID or name) with ambiguity handling."""
    return resolve_resource(
        ctx,
        ref,
        get_by_id=client.agents.get_agent_by_id,
        find_by_name=client.agents.find_agents,
        label="Agent",
        select=select,
    )


@agents_group.command(name="list")
@output_flags()
@click.pass_context
def list_agents(ctx):
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

        output_list(ctx, agents, "🤖 Available Agents", columns, transform_agent)

    except Exception as e:
        raise click.ClickException(str(e))


@agents_group.command()
@click.argument("agent_ref")
@click.option("--select", type=int, help="Choose among ambiguous matches (1-based)")
@output_flags()
@click.pass_context
def get(ctx, agent_ref, select):
    """Get agent details."""
    try:
        client = get_client(ctx)

        # Resolve agent with ambiguity handling
        agent = _resolve_agent(ctx, client, agent_ref, select)

        # If resolved by name, it may be a shallow object from list endpoint.
        # Fetch full details by ID to ensure instruction/tools are populated.
        try:
            agent_id = str(getattr(agent, "id", "")).strip()
            if agent_id:
                agent = client.agents.get_agent_by_id(agent_id)
        except Exception:
            # If fetching full details fails, continue with the resolved object.
            pass

        # Create result data with all available fields from backend
        result_data = {
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
            "tool_configs": agent.tool_configs or {},
            "tools": getattr(agent, "tools", []),
            "agents": getattr(agent, "agents", []),
            "mcps": getattr(agent, "mcps", []),
            "a2a_profile": getattr(agent, "a2a_profile", "N/A"),
        }

        output_result(
            ctx, result_data, title="Agent Details", panel_title=f"🤖 {agent.name}"
        )

    except Exception as e:
        raise click.ClickException(str(e))


@agents_group.command()
@click.argument("agent_ref")
@click.option("--select", type=int, help="Choose among ambiguous matches (1-based)")
@click.option("--input", "input_text", required=True, help="Input text for the agent")
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
    chat_history,
    timeout,
    save,
    files,
    verbose,
):
    """Run an agent with input text (ID or name)."""
    try:
        client = get_client(ctx)

        # Resolve agent by ID or name (align with other commands)
        agent = _resolve_agent(ctx, client, agent_ref, select)

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
            "message": input_text,
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
            console.print(f"[green]Full debug output saved to: {save}[/green]")

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
@click.option("--name", required=True, help="Agent name")
@click.option("--instruction", required=True, help="Agent instruction (prompt)")
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
):
    """Create a new agent."""
    try:
        client = get_client(ctx)

        # Resolve tool and agent references: accept names or IDs
        def _resolve_tools(items: tuple[str, ...]) -> list[str]:
            out: list[str] = []
            for ref in list(items or ()):  # tuple -> list
                if is_uuid(ref):
                    out.append(ref)
                    continue
                matches = client.find_tools(name=ref)
                if not matches:
                    raise click.ClickException(f"Tool not found: {ref}")
                if len(matches) > 1:
                    raise click.ClickException(
                        f"Multiple tools named '{ref}'. Use ID instead."
                    )
                out.append(str(matches[0].id))
            return out

        def _resolve_agents(items: tuple[str, ...]) -> list[str]:
            out: list[str] = []
            for ref in list(items or ()):  # tuple -> list
                if is_uuid(ref):
                    out.append(ref)
                    continue
                matches = client.find_agents(name=ref)
                if not matches:
                    raise click.ClickException(f"Agent not found: {ref}")
                if len(matches) > 1:
                    raise click.ClickException(
                        f"Multiple agents named '{ref}'. Use ID instead."
                    )
                out.append(str(matches[0].id))
            return out

        resolved_tools = _resolve_tools(tools)
        resolved_agents = _resolve_agents(agents)

        # Create agent with optional model specification
        create_kwargs = {
            "name": name,
            "instruction": instruction,
            "tools": resolved_tools or None,
            "agents": resolved_agents or None,
            "timeout": timeout,
        }

        # Add model if specified
        if model:
            create_kwargs["model"] = model

        agent = client.agents.create_agent(**create_kwargs)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(agent.model_dump(), indent=2))
        else:
            # Rich output
            lm = getattr(agent, "model", None)
            if not lm:
                cfg = getattr(agent, "agent_config", {}) or {}
                lm = (
                    cfg.get("lm_name")
                    or cfg.get("model")
                    or model  # Use CLI model if specified
                    or f"{DEFAULT_MODEL} (backend default)"
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
            )
            console.print(panel)

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error creating agent: {e}[/red]")
        raise click.ClickException(str(e))


@agents_group.command()
@click.argument("agent_id")
@click.option("--name", help="New agent name")
@click.option("--instruction", help="New instruction")
@click.option("--tools", multiple=True, help="New tool names or IDs")
@click.option("--agents", multiple=True, help="New sub-agent names")
@click.option("--timeout", type=int, help="New timeout value")
@output_flags()
@click.pass_context
def update(ctx, agent_id, name, instruction, tools, agents, timeout):
    """Update an existing agent."""
    try:
        client = get_client(ctx)

        # Get agent by ID (no ambiguity handling needed)
        try:
            agent = client.agents.get_agent_by_id(agent_id)
        except Exception as e:
            raise click.ClickException(f"Agent with ID '{agent_id}' not found: {e}")

        # Build update data
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

        if not update_data:
            raise click.ClickException("No update fields specified")

        # Update agent
        updated_agent = client.agents.update_agent(agent.id, **update_data)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(updated_agent.model_dump(), indent=2))
        else:
            console.print(
                f"[green]✅ Agent '{updated_agent.name}' updated successfully[/green]"
            )

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error updating agent: {e}[/red]")
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
                console.print("Deletion cancelled.")
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
                f"[green]✅ Agent '{agent.name}' deleted successfully[/green]"
            )

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error deleting agent: {e}[/red]")
        raise click.ClickException(str(e))
