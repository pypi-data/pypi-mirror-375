"""Debug rendering utilities for verbose SSE event display.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
from datetime import datetime
from time import monotonic
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel


def render_debug_event(
    event: dict[str, Any], console: Console, started_ts: float | None = None
) -> None:
    """Render a debug panel for an SSE event.

    Args:
        event: The SSE event data
        console: Rich console to print to
        started_ts: Monotonic timestamp when streaming started
    """
    try:
        # Add relative time since first meaningful event and wall-clock stamp
        now_mono = monotonic()
        rel = 0.0
        if started_ts is not None:
            rel = max(0.0, now_mono - started_ts)
        ts_full = datetime.now().strftime("%H:%M:%S.%f")
        ts_ms = ts_full[:-3]  # trim to milliseconds

        # Compose a descriptive title with kind/status
        sse_kind = (event.get("metadata") or {}).get("kind") or "event"
        status_str = event.get("status") or (event.get("metadata") or {}).get("status")
        title = (
            f"SSE: {sse_kind} — {status_str} @ {ts_ms} (+{rel:.2f}s)"
            if status_str
            else f"SSE: {sse_kind} @ {ts_ms} (+{rel:.2f}s)"
        )

        # Deep-pretty the event by parsing nested JSON strings
        def _dejson(obj):
            if isinstance(obj, dict):
                return {k: _dejson(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_dejson(x) for x in obj]
            if isinstance(obj, str):
                s = obj.strip()
                if (s.startswith("{") and s.endswith("}")) or (
                    s.startswith("[") and s.endswith("]")
                ):
                    try:
                        return _dejson(json.loads(s))
                    except Exception:
                        return obj
                return obj
            return obj

        try:
            event_json = json.dumps(_dejson(event), indent=2, ensure_ascii=False)
        except Exception:
            event_json = str(event)

        # Choose border color by kind for readability
        border = {
            "agent_step": "blue",
            "content": "green",
            "final_response": "green",
            "status": "yellow",
            "artifact": "grey42",
        }.get(sse_kind, "grey42")

        # Render using Markdown with JSON code block (consistent with tool panels)
        md = Markdown(f"```json\n{event_json}\n```", code_theme="monokai")
        console.print(Panel(md, title=title, border_style=border))
    except Exception as e:
        # Debug helpers must not break streaming
        print(f"Debug error: {e}")  # Fallback debug output
