"""Automated test harness for JMI-v2.0.

Covers the three canonical demonstration turns plus isolation, dormant
routing, unknown-tool fail-closed, and sequential non-leakage.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jmi import (
    JITMiddleware,
    LocalIntentAnalyzer,
    MiddlewareToolRegistry,
    Payload,
    Tool,
)
from jmi.runtime import mock_llm_operator, select_mode
from jmi.trace import RecordingTracer


def _tool(name: str, output: str) -> Tool:
    return Tool(
        name=name,
        description=name,
        schema={"type": "function", "function": {"name": name}},
        executor=lambda args, _output=output: _output,
    )


def _stack(*names: str):
    tracer = RecordingTracer()
    registry = MiddlewareToolRegistry(tracer=tracer)
    outputs = {
        "veo_video_generation": "Rendered a beautiful 15s MP4 via Veo 3.1.",
        "lyria_music_generation": "Synthesized a clean cinematic audio track.",
        "file_system_manager": "Wrote the document to the logbook.",
    }
    for name in names:
        registry.register(_tool(name, outputs[name]))
    middleware = JITMiddleware(registry, tracer=tracer)
    return middleware, registry, tracer


class CanonicalDemoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mw, self.registry, self.tracer = _stack(
            "veo_video_generation",
            "lyria_music_generation",
        )

    def test_1_philosophy_keeps_pipeline_clean(self) -> None:
        result = self.mw.run(
            "Erkläre mir die Philosophie des kleinsten Nenners.",
            mock_llm_operator,
        )
        self.assertEqual(result.mode, "text")
        self.assertEqual(result.injected_tool_names, [])
        self.assertIn("reine Textantwort", result.output)
        channels = [e.channel for e in self.tracer.events]
        self.assertIn("ROUTE", channels)
        self.assertNotIn("INJECT", channels)
        self.assertNotIn("EXECUTE", channels)
        self.assertEqual(channels[-1], "CLEANUP")

    def test_2_video_injects_veo_executes_and_cleans(self) -> None:
        result = self.mw.run(
            "Ich brauche ein Video von einer Protein-Faltung.",
            mock_llm_operator,
        )
        self.assertEqual(result.mode, "tool")
        self.assertEqual(result.injected_tool_names, ["veo_video_generation"])
        self.assertIn("Veo 3.1", result.output)
        channels = [e.channel for e in self.tracer.events]
        self.assertIn("INJECT", channels)
        self.assertIn("EXECUTE", channels)
        self.assertEqual(channels[-1], "CLEANUP")

    def test_3_music_loads_lyria_on_clear_pipeline(self) -> None:
        result = self.mw.run(
            "Mach mir eine entspannte Musik für den Feierabend.",
            mock_llm_operator,
        )
        self.assertEqual(result.mode, "tool")
        self.assertEqual(result.injected_tool_names, ["lyria_music_generation"])
        self.assertIn("cinematic audio", result.output)


class IsolationTests(unittest.TestCase):
    def test_sequential_turns_do_not_leak_schemas(self) -> None:
        mw, _, _ = _stack("veo_video_generation", "lyria_music_generation")
        video = mw.run("render a video of rain", mock_llm_operator)
        text = mw.run("What is entropy?", mock_llm_operator)
        music = mw.run("compose a melody", mock_llm_operator)

        self.assertEqual(video.injected_tool_names, ["veo_video_generation"])
        self.assertEqual(text.injected_tool_names, [])
        self.assertEqual(text.mode, "text")
        self.assertEqual(music.injected_tool_names, ["lyria_music_generation"])

    def test_dormant_file_tool_is_not_injected_until_registered(self) -> None:
        mw, registry, _ = _stack("veo_video_generation")
        # file_system_manager lives in the routing matrix but is not registered
        result = mw.run("Please save this document as a pdf logbook.", mock_llm_operator)
        self.assertEqual(result.injected_tool_names, [])
        self.assertEqual(result.mode, "text")

        registry.register(_tool("file_system_manager", "Wrote the document to the logbook."))
        result2 = mw.run("Please save this document as a pdf logbook.", mock_llm_operator)
        self.assertEqual(result2.injected_tool_names, ["file_system_manager"])
        self.assertEqual(result2.mode, "tool")

    def test_unknown_tool_call_fails_closed(self) -> None:
        mw, _, _ = _stack("veo_video_generation")

        def hostile_llm(_payload: Payload):
            return {"tool_call": {"name": "not_a_real_tool", "arguments": "x"}}

        result = mw.run("make a video", hostile_llm)
        self.assertEqual(result.mode, "error")
        self.assertIn("unknown tool", result.output)

    def test_mode_selection_follows_injected_schemas(self) -> None:
        self.assertEqual(select_mode(Payload(user_prompt="hi")), "B")
        self.assertEqual(
            select_mode(
                Payload(
                    user_prompt="hi",
                    injected_tools=[{"function": {"name": "veo_video_generation"}}],
                )
            ),
            "A",
        )

    def test_custom_routing_matrix_is_honored(self) -> None:
        registry = MiddlewareToolRegistry()
        registry.register(_tool("veo_video_generation", "ok"))
        analyzer = LocalIntentAnalyzer(
            registry,
            routing_matrix={"veo_video_generation": ["protein"]},
        )
        mw = JITMiddleware(registry, analyzer=analyzer)
        hit = mw.run("protein folding please", mock_llm_operator)
        miss = mw.run("I need a video", mock_llm_operator)
        self.assertEqual(hit.injected_tool_names, ["veo_video_generation"])
        self.assertEqual(miss.injected_tool_names, [])

    def test_payload_system_instruction_is_kind(self) -> None:
        payload = Payload(user_prompt="hello")
        self.assertEqual(payload.system_instruction, "Be simple, clear, and kind.")


if __name__ == "__main__":
    unittest.main()
