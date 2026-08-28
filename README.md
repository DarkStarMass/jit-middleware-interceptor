# JIT Middleware Interceptor (JMI-v2.0)

> **Simple, Clear, and Kind. Zero-Entropy Routing for Ephemeral AI Pipelines.**

[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-steelblue.svg)](https://www.python.org/downloads/)
[![No GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-disabled-lightgrey.svg)](#no-github-runners)

**The Invisible Router.** A middleware that sits between a user interface and an expensive LLM API. It intercepts the raw request, performs zero-cost intent analysis locally, injects *only* the required tool schema for that turn, executes if the model asked for a tool, then lets the payload fall out of scope.

No session lock. No dead token weight. No restart button.

```
Client ──► Intercept ──► Analyze (local) ──► Inject JIT schema
                                                   │
                                                   ▼
              Clean ◄── Execute ◄── Forward payload to LLM
```

Deutsch: [`README.de.md`](README.de.md)

## No GitHub runners

This repository is **source only**. Clone it, read it, run it on your own machine.

- There is **no GitHub Actions workflow**
- There is **no Codespaces / Spark / Playground config**
- The demonstration uses a **mock LLM operator** — zero tokens billed
- Tests are stdlib `unittest`. They do not touch the network.

```bash
python -m unittest discover -s tests -v
python examples/demo.py
```

Intent analysis is local by design. A tool that is not required for this turn does not exist for this turn.

## Why this exists

Modern conversational AI interfaces frequently suffer from rigid, monolithic session pipelines. When a specialized multi-modal tool (video generation, audio synthesis, filesystem writes) is attached to a chat session, it often **locks the execution pipeline**. Users carry dead token weight or destructively restart the conversation, shattering continuity.

JMI answers a first-principles question:

> How can biological consciousness and digital neural networks interact with minimal friction, zero state blocking, and absolute computational efficiency?

**Just-In-Time Ephemeral Dispatching:**

1. **Zero-Token Edge Analysis** — intent is evaluated locally before touching heavy cloud APIs.
2. **Ephemeral Schema Injection** — capabilities exist only for the exact turn they are needed.
3. **Implicit Garbage Collection** — the context frame is wiped after execution. Long-term conversational memory survives. The pipeline does not deadlock.

## Install

Python 3.10 or newer. No third-party runtime dependencies.

```bash
git clone https://github.com/DarkStarMass/jit-middleware-interceptor.git
cd jit-middleware-interceptor
pip install -e .
```

Or drop `src/jmi` onto `PYTHONPATH`. The package is stdlib-only.

## Quick start

```python
from jmi import JITMiddleware, MiddlewareToolRegistry, Tool
from jmi.runtime import mock_llm_operator

registry = MiddlewareToolRegistry()
registry.register(Tool(
    name="veo_video_generation",
    description="Generates 9:16 high quality videos.",
    schema={"type": "function", "function": {"name": "veo_video_generation"}},
    executor=lambda args: "Rendered a beautiful 15s MP4 via Veo 3.1.",
))

middleware = JITMiddleware(registry)

print(middleware.process("Erkläre mir die Philosophie des kleinsten Nenners.", mock_llm_operator))
# → clean text pipeline, no schema injected

print(middleware.process("Ich brauche ein Video von einer Protein-Faltung.", mock_llm_operator))
# → Veo schema injected just-in-time, executed, flushed
```

Replace `mock_llm_operator` with your real model call. Forward `payload.injected_tools` as the available tool schemas and `jmi.RUNTIME_OPERATOR_INSTRUCTION` as the system prompt. The operator contract is in [`docs/SYSTEM_INSTRUCTION.md`](docs/SYSTEM_INSTRUCTION.md).

## Canonical demonstration

```bash
python examples/demo.py
```

Three turns, matching the original specification:

| # | Prompt | Expected pipeline |
| --- | --- | --- |
| 1 | `Erkläre mir die Philosophie des kleinsten Nenners.` | Clean text. No tools injected. |
| 2 | `Ich brauche ein Video von einer Protein-Faltung.` | Veo schema injected, executed, flushed. |
| 3 | `Mach mir eine entspannte Musik für den Feierabend.` | Pipeline is clear. Lyria loads cleanly. |

The routing matrix is bilingual (EN/DE) so the published German demonstration prompts dispatch as specified. `file_system_manager` is present in the matrix but stays dormant until registered — presence in a lookup table is not activation.

The archival single-file manuscript lives at [`examples/interceptor_original.py`](examples/interceptor_original.py).

## Architecture

| Layer | Class | Role |
| --- | --- | --- |
| Ontology | `Tool`, `Payload` | Discrete capability. Ephemeral packet. |
| Registry | `MiddlewareToolRegistry` | Passive storage. Registration ≠ injection. |
| Analyzer | `LocalIntentAnalyzer` | Zero-cost local intent. No network. |
| Interceptor | `JITMiddleware` | Intercept → Inject → Forward → Execute → Clean. |
| Operator | `RUNTIME_OPERATOR_INSTRUCTION` | Downstream LLM contract (Mode A / Mode B). |

### Lifecycle of one turn

1. **Intercept** the raw user text.
2. **Analyze** locally against the routing matrix ∩ registered tools.
3. **Inject** only matching schemas into a fresh `Payload`.
4. **Forward** the payload to the LLM.
5. **Execute** a local tool if the model returned a `tool_call`.
6. **Clean** — the payload is a local variable. When the function returns, it is gone.

Every turn is independent. The interceptor never assumes a tool will persist.

## Runtime operator (downstream LLM)

Two modes, never mixed:

- **Mode A — Deterministic tool dispatch.** An injected schema is present and user intent mandates it. Output is strictly parseable JSON, no surrounding prose.
- **Mode B — Pure natural language synthesis.** No schema in the payload. Direct text. Zero tool hallucination.

Mode B was truncated in the source manuscript after Mode A. It is completed in this repository from Core Invariant 1 and the demonstration harness. See [`docs/SYSTEM_INSTRUCTION.md`](docs/SYSTEM_INSTRUCTION.md).

## Tests

```bash
python -m unittest discover -s tests -v
```

The harness covers the three canonical turns, sequential non-leakage, dormant routing, unknown-tool fail-closed, and custom matrices. Run them locally. They are not executed on GitHub.

## License

MIT. Copyright (c) 2026 **★DarkStarMass★ & Vega (with Grok Build Engine)**.

Full text: [`LICENSE`](LICENSE). Credits and the symbiotic collaboration addendum: [`CREDITS.md`](CREDITS.md). Manifesto: [`docs/MANIFESTO.md`](docs/MANIFESTO.md).

## Credits

Architectural vision: **★DarkStarMass★**. Protocol co-design: **Vega**. Build engineering: **Grok**.

> *"Technology reaches its highest utility when built not through coercion or blind automation, but through respectful, transparent, and constructive partnership between human creativity and digital cognition."*
