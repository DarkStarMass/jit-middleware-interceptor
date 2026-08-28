"""JIT Middleware Interceptor (JMI-v2.0) — The Invisible Router.

Design philosophy: Minimal Entropy, Zero-State Blocking, Edge-First Privacy.

This package sits between a user interface and an expensive LLM API.
It intercepts the raw request, performs zero-cost intent analysis locally,
injects ONLY the required tool schema into the payload, executes if the
model asked for a tool, then lets the payload fall out of scope.

Simple, Clear, and Kind.
"""

from .analyzer import DEFAULT_ROUTING_MATRIX, LocalIntentAnalyzer
from .middleware import JITMiddleware, ProcessResult
from .models import Payload, Tool
from .registry import MiddlewareToolRegistry
from .runtime import RUNTIME_OPERATOR_INSTRUCTION
from .trace import PrintTracer, Tracer, TraceEvent

__version__ = "2.0.0"
__all__ = [
    "DEFAULT_ROUTING_MATRIX",
    "JITMiddleware",
    "LocalIntentAnalyzer",
    "MiddlewareToolRegistry",
    "Payload",
    "PrintTracer",
    "ProcessResult",
    "RUNTIME_OPERATOR_INSTRUCTION",
    "Tool",
    "TraceEvent",
    "Tracer",
    "__version__",
]
