"""The Analyzer — local edge-computing for privacy and cost avoidance.

Acts as a zero-cost gatekeeper. Instead of asking the expensive LLM which
tool to use, intent is evaluated locally before the network call.

The original v2.0 routing matrix used English tokens. The canonical
demonstration prompts are German, so the matrix is bilingual (EN/DE) —
otherwise Test 3 ("Musik") would silently fall through to a clean text
pipeline, contradicting the spec's own expected outcome.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence

from .registry import MiddlewareToolRegistry

# Canonical heuristic routing matrix (v2.0).
# English tokens: original specification.
# German tokens: required so the published demonstration prompts dispatch.
DEFAULT_ROUTING_MATRIX: Dict[str, List[str]] = {
    "veo_video_generation": [
        "video",
        "render",
        "animation",
        "shot",
        "mp4",
        "film",
        "clip",
    ],
    "lyria_music_generation": [
        "music",
        "audio",
        "song",
        "track",
        "melody",
        "musik",
        "lied",
        "klang",
        "tonspur",
    ],
    "file_system_manager": [
        "save",
        "file",
        "document",
        "pdf",
        "logbook",
        "speichern",
        "datei",
        "dokument",
    ],
}


class LocalIntentAnalyzer:
    """Zero-cost local intent gatekeeper.

    In production this can be swapped for a tiny local model (quantized
    BERT, embedding kNN, etc.). The default is a deterministic keyword
    mapper — no network, no tokens billed, no prompt leakage.
    """

    def __init__(
        self,
        registry: MiddlewareToolRegistry,
        routing_matrix: Optional[Mapping[str, Sequence[str]]] = None,
    ) -> None:
        self.registry = registry
        self.routing_matrix: Dict[str, List[str]] = {
            name: list(keywords)
            for name, keywords in (routing_matrix or DEFAULT_ROUTING_MATRIX).items()
        }

    def evaluate(self, prompt: str) -> List[str]:
        prompt_lower = prompt.lower()
        active_tools: List[str] = []

        for tool_name, keywords in self.routing_matrix.items():
            if any(kw in prompt_lower for kw in keywords) and self.registry.get_tool(
                tool_name
            ):
                active_tools.append(tool_name)

        return active_tools
