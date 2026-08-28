"""The Core Middleware — the interceptor.

Lifecycle of one turn, and only one turn:

    Intercept → Inject → Forward → Execute → Clean

The payload is a local variable. When `process()` returns, the frame is
gone. No session lock, no dangling tool schema, no restart button.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .analyzer import LocalIntentAnalyzer
from .models import Payload
from .registry import MiddlewareToolRegistry
from .trace import Tracer, optional_emit

LLMCall = Callable[[Payload], Dict[str, Any]]


@dataclass
class ProcessResult:
    """Structured outcome of a single interceptor turn."""

    output: str
    injected_tool_names: List[str] = field(default_factory=list)
    mode: str = "text"  # "text" | "tool" | "error"
    raw_llm_response: Dict[str, Any] = field(default_factory=dict)


class JITMiddleware:
    def __init__(
        self,
        registry: MiddlewareToolRegistry,
        tracer: Optional[Tracer] = None,
        analyzer: Optional[LocalIntentAnalyzer] = None,
    ) -> None:
        self.registry = registry
        self.tracer = tracer
        self.analyzer = analyzer or LocalIntentAnalyzer(registry)

    def process(self, user_text: str, llm_api_call: LLMCall) -> str:
        """Intercept → Inject → Forward → Execute → Clean. Returns the user-facing string."""
        return self.run(user_text, llm_api_call).output

    def run(self, user_text: str, llm_api_call: LLMCall) -> ProcessResult:
        optional_emit(self.tracer, "IN", user_text)

        # Step 1: Intercept & Analyze locally (zero cost, high privacy)
        required_tool_names = self.analyzer.evaluate(user_text)
        payload = Payload(user_prompt=user_text)

        # Step 2: Inject precisely what is needed (Just-in-Time)
        for name in required_tool_names:
            tool = self.registry.get_tool(name)
            if tool:
                payload.injected_tools.append(tool.schema)
                optional_emit(
                    self.tracer,
                    "INJECT",
                    f"dynamically loaded schema: {name}",
                )

        if not payload.injected_tools:
            optional_emit(
                self.tracer,
                "ROUTE",
                "Clean text pipeline. No tools injected.",
            )

        # Step 3: Forward optimized payload to the LLM
        optional_emit(self.tracer, "NETWORK", "Forwarding payload to LLM...")
        llm_response = llm_api_call(payload)

        # Step 4: Intercept LLM response & execute tool if requested
        result = self._handle_llm_response(llm_response)
        result.injected_tool_names = list(required_tool_names)
        result.raw_llm_response = llm_response

        # Step 5: Garbage collection is implicit — `payload` dies with the frame.
        optional_emit(
            self.tracer,
            "CLEANUP",
            "Pipeline flushed. Ready for next prompt.",
        )
        return result

    def _handle_llm_response(self, llm_response: Dict[str, Any]) -> ProcessResult:
        if "tool_call" in llm_response:
            tool_name = llm_response["tool_call"]["name"]
            arguments = llm_response["tool_call"]["arguments"]

            optional_emit(
                self.tracer,
                "EXECUTE",
                f"LLM requested local tool: {tool_name}",
            )
            tool = self.registry.get_tool(tool_name)

            if tool:
                result = tool.executor(arguments)
                return ProcessResult(
                    output=f"✅ Tool Output: {result}",
                    mode="tool",
                )
            return ProcessResult(
                output=f"❌ Error: LLM requested unknown tool {tool_name}",
                mode="error",
            )

        return ProcessResult(
            output=f"💬 LLM Output: {llm_response.get('text', '')}",
            mode="text",
        )
