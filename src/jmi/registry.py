"""The Registry — passive storage, zero overhead.

Tools sit dormant until the analyzer names them. Registration is not
activation. Presence in the registry does not leak schemas into the LLM
payload.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .models import Tool
from .trace import Tracer


class MiddlewareToolRegistry:
    def __init__(self, tracer: Optional[Tracer] = None) -> None:
        self._tools: Dict[str, Tool] = {}
        self._tracer = tracer

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool
        if self._tracer is not None:
            self._tracer.emit(
                "REGISTRY",
                f"Tool registered and dormant: {tool.name}",
            )

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def get_all_names(self) -> List[str]:
        return list(self._tools.keys())
