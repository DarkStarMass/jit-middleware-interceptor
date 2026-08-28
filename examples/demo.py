#!/usr/bin/env python3
"""Demonstration & deployment harness — JMI-v2.0

Canonical three-turn proof from the original specification:

  1. Normal conversation  → clean text pipeline, no tools injected
  2. Video request        → Veo schema injected, executed, flushed
  3. Music request        → pipeline is clear, Lyria loads cleanly
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running this file directly from a source checkout.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jmi import (  # noqa: E402
    JITMiddleware,
    MiddlewareToolRegistry,
    PrintTracer,
    Tool,
)
from jmi.runtime import mock_llm_operator  # noqa: E402
from jmi.trace import FanoutTracer, RecordingTracer  # noqa: E402


def build_demo_stack():
    tracer = PrintTracer()
    registry = MiddlewareToolRegistry(tracer=tracer)

    registry.register(
        Tool(
            name="veo_video_generation",
            description="Generates 9:16 high quality videos.",
            schema={
                "type": "function",
                "function": {"name": "veo_video_generation"},
            },
            executor=lambda args: "Rendered a beautiful 15s MP4 via Veo 3.1.",
        )
    )

    registry.register(
        Tool(
            name="lyria_music_generation",
            description="Generates audio tracks and soundscapes.",
            schema={
                "type": "function",
                "function": {"name": "lyria_music_generation"},
            },
            executor=lambda args: "Synthesized a clean cinematic audio track.",
        )
    )

    recorder = RecordingTracer()
    middleware = JITMiddleware(
        registry,
        tracer=FanoutTracer(tracer, recorder),
    )
    return middleware, recorder


def main() -> None:
    middleware, _recorder = build_demo_stack()

    print("Test 1: Normal Conversation (Should keep pipeline clean)")
    out1 = middleware.process(
        "Erkläre mir die Philosophie des kleinsten Nenners.",
        mock_llm_operator,
    )
    print(out1)

    print("Test 2: Video Request (Should inject Veo, execute, and clean up)")
    out2 = middleware.process(
        "Ich brauche ein Video von einer Protein-Faltung.",
        mock_llm_operator,
    )
    print(out2)

    print("Test 3: Music Request (Pipeline is clear, Lyria loads cleanly)")
    out3 = middleware.process(
        "Mach mir eine entspannte Musik für den Feierabend.",
        mock_llm_operator,
    )
    print(out3)


if __name__ == "__main__":
    main()
