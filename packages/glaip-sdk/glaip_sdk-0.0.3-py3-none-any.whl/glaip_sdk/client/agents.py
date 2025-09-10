#!/usr/bin/env python3
"""Agent client for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
import logging
from time import monotonic
from typing import Any, BinaryIO

from rich.console import Console as _Console

from glaip_sdk.client.base import BaseClient
from glaip_sdk.config.constants import (
    DEFAULT_AGENT_FRAMEWORK,
    DEFAULT_AGENT_PROVIDER,
    DEFAULT_AGENT_RUN_TIMEOUT,
    DEFAULT_AGENT_TYPE,
    DEFAULT_AGENT_VERSION,
    DEFAULT_MODEL,
)
from glaip_sdk.models import Agent
from glaip_sdk.utils.client_utils import (
    create_model_instances,
    extract_ids,
    find_by_name,
    iter_sse_events,
    prepare_multipart_data,
)
from glaip_sdk.utils.rendering.models import RunStats
from glaip_sdk.utils.rendering.renderer import RichStreamRenderer

# Set up module-level logger
logger = logging.getLogger("glaip_sdk.agents")


class AgentClient(BaseClient):
    """Client for agent operations."""

    def __init__(self, *, parent_client: BaseClient | None = None, **kwargs):
        """Initialize the agent client.

        Args:
            parent_client: Parent client to adopt session/config from
            **kwargs: Additional arguments for standalone initialization
        """
        super().__init__(parent_client=parent_client, **kwargs)

    def list_agents(self) -> list[Agent]:
        """List all agents."""
        data = self._request("GET", "/agents/")
        return create_model_instances(data, Agent, self)

    def get_agent_by_id(self, agent_id: str) -> Agent:
        """Get agent by ID."""
        data = self._request("GET", f"/agents/{agent_id}")
        return Agent(**data)._set_client(self)

    def find_agents(self, name: str | None = None) -> list[Agent]:
        """Find agents by name."""
        params = {}
        if name:
            params["name"] = name

        data = self._request("GET", "/agents/", params=params)
        agents = create_model_instances(data, Agent, self)
        if name is None:
            return agents
        return find_by_name(agents, name, case_sensitive=False)

    def create_agent(
        self,
        name: str,
        instruction: str,
        model: str = DEFAULT_MODEL,
        tools: list[str | Any] | None = None,
        agents: list[str | Any] | None = None,
        timeout: int = DEFAULT_AGENT_RUN_TIMEOUT,
        **kwargs,
    ) -> "Agent":
        """Create a new agent."""
        # Client-side validation
        if not name or not name.strip():
            raise ValueError("Agent name cannot be empty or whitespace")

        if not instruction or not instruction.strip():
            raise ValueError("Agent instruction cannot be empty or whitespace")

        if len(instruction.strip()) < 10:
            raise ValueError("Agent instruction must be at least 10 characters long")

        # Prepare the creation payload
        payload: dict[str, Any] = {
            "name": name.strip(),
            "instruction": instruction.strip(),
            "type": DEFAULT_AGENT_TYPE,
            "framework": DEFAULT_AGENT_FRAMEWORK,
            "version": DEFAULT_AGENT_VERSION,
            "provider": DEFAULT_AGENT_PROVIDER,
            "model_name": model or DEFAULT_MODEL,  # Ensure model_name is never None
        }

        # Include default execution timeout if provided
        if timeout is not None:
            payload["timeout"] = str(timeout)

        # Ensure minimum required metadata for visibility
        if "metadata" not in kwargs:
            kwargs["metadata"] = {}

        # Always include the minimum required metadata for visibility
        if "type" not in kwargs["metadata"]:
            kwargs["metadata"]["type"] = "custom"

        # Extract IDs from tool and agent objects
        tool_ids = extract_ids(tools)
        agent_ids = extract_ids(agents)

        # Add tools and agents if provided
        if tool_ids:
            payload["tools"] = tool_ids
        if agent_ids:
            payload["agents"] = agent_ids

        # Add any additional kwargs
        payload.update(kwargs)

        # Create the agent and fetch full details
        full_agent_data = self._post_then_fetch(
            id_key="id",
            post_endpoint="/agents/",
            get_endpoint_fmt="/agents/{id}",
            json=payload,
        )
        return Agent(**full_agent_data)._set_client(self)

    def update_agent(
        self,
        agent_id: str,
        name: str | None = None,
        instruction: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> "Agent":
        """Update an existing agent."""
        # First, get the current agent data
        current_agent = self.get_agent_by_id(agent_id)

        # Prepare the update payload with current values as defaults
        update_data = {
            "name": name if name is not None else current_agent.name,
            "instruction": instruction
            if instruction is not None
            else current_agent.instruction,
            "type": DEFAULT_AGENT_TYPE,  # Required by backend
            "framework": DEFAULT_AGENT_FRAMEWORK,  # Required by backend
            "version": DEFAULT_AGENT_VERSION,  # Required by backend
        }

        # Handle model specification
        if model is not None:
            update_data["provider"] = DEFAULT_AGENT_PROVIDER  # Default provider
            update_data["model_name"] = model
        else:
            # Use current model if available
            if hasattr(current_agent, "agent_config") and current_agent.agent_config:
                if "lm_provider" in current_agent.agent_config:
                    update_data["provider"] = current_agent.agent_config["lm_provider"]
                if "lm_name" in current_agent.agent_config:
                    update_data["model_name"] = current_agent.agent_config["lm_name"]
            else:
                # Default values
                update_data["provider"] = DEFAULT_AGENT_PROVIDER
                update_data["model_name"] = DEFAULT_MODEL

        # Handle tools and agents
        if "tools" in kwargs:
            tool_ids = extract_ids(kwargs["tools"])
            if tool_ids:
                update_data["tools"] = tool_ids
        elif current_agent.tools:
            update_data["tools"] = [
                tool["id"] if isinstance(tool, dict) else tool
                for tool in current_agent.tools
            ]

        if "agents" in kwargs:
            agent_ids = extract_ids(kwargs["agents"])
            if agent_ids:
                update_data["agents"] = agent_ids
        elif current_agent.agents:
            update_data["agents"] = [
                agent["id"] if isinstance(agent, dict) else agent
                for agent in current_agent.agents
            ]

        # Add any other kwargs
        for key, value in kwargs.items():
            if key not in ["tools", "agents"]:
                update_data[key] = value

        # Send the complete payload
        data = self._request("PUT", f"/agents/{agent_id}", json=update_data)
        return Agent(**data)._set_client(self)

    def delete_agent(self, agent_id: str) -> None:
        """Delete an agent."""
        self._request("DELETE", f"/agents/{agent_id}")

    def run_agent(
        self,
        agent_id: str,
        message: str,
        files: list[str | BinaryIO] | None = None,
        tty: bool = False,
        *,
        renderer: RichStreamRenderer | str | None = "auto",
        **kwargs,
    ) -> str:
        """Run an agent with a message, streaming via a renderer."""
        # Prepare multipart data if files are provided
        multipart_data = None
        headers = None  # None means "don't override client defaults"

        if files:
            multipart_data = prepare_multipart_data(message, files)
            # Inject optional multipart extras expected by backend
            if "chat_history" in kwargs and kwargs["chat_history"] is not None:
                multipart_data.data["chat_history"] = kwargs["chat_history"]
            if "pii_mapping" in kwargs and kwargs["pii_mapping"] is not None:
                multipart_data.data["pii_mapping"] = kwargs["pii_mapping"]
            headers = None  # Let httpx set proper multipart boundaries

        # When streaming, explicitly prefer SSE
        headers = {**(headers or {}), "Accept": "text/event-stream"}

        if files:
            payload = None
            # Use multipart data
            data_payload = multipart_data.data
            files_payload = multipart_data.files
        else:
            payload = {"input": message, **kwargs}
            if tty:
                payload["tty"] = True
            # Explicitly send stream intent both ways
            payload["stream"] = True
            data_payload = None
            files_payload = None

        # Choose renderer: use provided instance or create a default
        if isinstance(renderer, RichStreamRenderer):
            r = renderer
        else:
            # Default to a standard rich renderer
            r = RichStreamRenderer(console=_Console())

        # Try to set some meta early; refine as we receive events
        meta = {
            "agent_name": kwargs.get("agent_name", agent_id),
            "model": kwargs.get("model"),
            "run_id": None,
            "input_message": message,  # Add the original query for context
        }
        r.on_start(meta)

        final_text = ""
        stats_usage = {}
        started_monotonic = None
        finished_monotonic = None

        # MultipartData handles file cleanup automatically

        try:
            response = self.http_client.stream(
                "POST",
                f"/agents/{agent_id}/run",
                json=payload,
                data=data_payload,
                files=files_payload,
                headers=headers,
            )

            with response as stream_response:
                stream_response.raise_for_status()

                # capture request id if provided
                req_id = stream_response.headers.get(
                    "x-request-id"
                ) or stream_response.headers.get("x-run-id")
                if req_id:
                    meta["run_id"] = req_id
                    r.on_start(meta)  # refresh header with run_id

                # Get agent run timeout for execution control
                # Prefer CLI-provided timeout, otherwise use default
                timeout_seconds = kwargs.get("timeout", DEFAULT_AGENT_RUN_TIMEOUT)

                agent_name = kwargs.get("agent_name")

                for event in iter_sse_events(
                    stream_response, timeout_seconds, agent_name
                ):
                    try:
                        ev = json.loads(event["data"])
                    except json.JSONDecodeError:
                        logger.debug("Non-JSON SSE fragment skipped")
                        continue

                    # Start timer at first meaningful event
                    if started_monotonic is None and (
                        "content" in ev or "status" in ev or ev.get("metadata")
                    ):
                        started_monotonic = monotonic()

                    kind = (ev.get("metadata") or {}).get("kind")

                    # Pass event to the renderer (always, don't filter)
                    r.on_event(ev)

                    # Hide "artifact" chatter from content accumulation only
                    if kind == "artifact":
                        continue

                    # Accumulate assistant content, but do not print here
                    if "content" in ev and ev["content"]:
                        # Filter weird backend text like "Artifact received: ..."
                        if not ev["content"].startswith("Artifact received:"):
                            final_text = ev["content"]  # replace with latest
                        continue

                    # Also treat final_response like content for CLI return value
                    if kind == "final_response" and ev.get("content"):
                        final_text = ev["content"]  # ensure CLI non-empty
                        continue

                    # Usage/cost event (if your backend emits it)
                    if kind == "usage":
                        stats_usage.update(ev.get("usage") or {})
                        continue

                    # Model/run info (if emitted mid-stream)
                    if kind == "run_info":
                        if ev.get("model"):
                            meta["model"] = ev["model"]
                            r.on_start(meta)
                        if ev.get("run_id"):
                            meta["run_id"] = ev["run_id"]
                            r.on_start(meta)

            finished_monotonic = monotonic()
        except KeyboardInterrupt:
            try:
                r.close()
            finally:
                raise
        except Exception:
            try:
                r.close()
            finally:
                raise
        finally:
            # Ensure we close any opened file handles from multipart
            if multipart_data:
                multipart_data.close()

        # Finalize stats
        st = RunStats()
        # Ensure monotonic order (avoid negative -0.0s)
        if started_monotonic is None:
            started_monotonic = finished_monotonic

        st.started_at = started_monotonic or st.started_at
        st.finished_at = finished_monotonic or st.started_at
        st.usage = stats_usage

        # Prefer explicit content, otherwise fall back to what the renderer saw
        if hasattr(r, "state") and hasattr(r.state, "buffer"):
            rendered_text = "".join(r.state.buffer)
        else:
            rendered_text = ""
        final_payload = final_text or rendered_text or "No response content received."

        r.on_complete(st)
        return final_payload
