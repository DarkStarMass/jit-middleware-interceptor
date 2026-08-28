"""Ontology & data structures — the clean foundation.

A Tool is a discrete capability. It never pollutes global session state.
A Payload is the ephemeral packet that travels through one turn and dies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class Tool:
    """Represents a discrete capability without polluting the global state."""

    name: str
    description: str
    schema: Dict[str, Any]
    executor: Callable[[str], str]


@dataclass
class Payload:
    """The standardized data packet traveling through the middleware.

    Lives for exactly one `process()` call. When the function returns, the
    payload is eligible for garbage collection — the pipeline stays unblocked.
    """

    user_prompt: str
    injected_tools: List[Dict[str, Any]] = field(default_factory=list)
    system_instruction: str = "Be simple, clear, and kind."
