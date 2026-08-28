"""Trace sinks — optional observers for the interceptor lifecycle.

The original demonstration printed emoji-tagged lines to stdout. That
behavior is preserved via PrintTracer. Tests and UIs inject their own
sink so the pipeline remains inspectable without polluting stdout.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol


@dataclass(frozen=True)
class TraceEvent:
    channel: str
    message: str


class Tracer(Protocol):
    def emit(self, channel: str, message: str) -> None: ...


class PrintTracer:
    """Faithful recreation of the original demonstration log format."""

    _PREFIX = {
        "REGISTRY": "[REGISTRY]",
        "IN": "📥 [MIDDLEWARE IN]",
        "INJECT": "💉 [MIDDLEWARE INJECT]",
        "ROUTE": "🛡️ [MIDDLEWARE ROUTE]",
        "NETWORK": "🌐 [NETWORK]",
        "EXECUTE": "⚙️ [MIDDLEWARE EXECUTE]",
        "CLEANUP": "🧹 [MIDDLEWARE CLEANUP]",
    }

    def emit(self, channel: str, message: str) -> None:
        prefix = self._PREFIX.get(channel, f"[{channel}]")
        if channel == "IN":
            print()
            print("[" + ("-" * 60) + "]")
            print(f"{prefix} Raw Request: '{message}'")
        elif channel == "CLEANUP":
            print(f"{prefix} {message}")
            print("[" + ("-" * 60) + "]")
            print()
        else:
            print(f"{prefix} {message}")


class RecordingTracer:
    """Collects events for tests and interactive playgrounds."""

    def __init__(self) -> None:
        self.events: List[TraceEvent] = []

    def emit(self, channel: str, message: str) -> None:
        self.events.append(TraceEvent(channel=channel, message=message))


class FanoutTracer:
    def __init__(self, *sinks: Tracer) -> None:
        self._sinks = sinks

    def emit(self, channel: str, message: str) -> None:
        for sink in self._sinks:
            sink.emit(channel, message)


def optional_emit(tracer: Optional[Tracer], channel: str, message: str) -> None:
    if tracer is not None:
        tracer.emit(channel, message)
