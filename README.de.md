# JIT Middleware Interceptor (JMI-v2.0)

> **Simple, Clear, and Kind. Zero-Entropy Routing for Ephemeral AI Pipelines.**

**The Invisible Router.** Eine Middleware zwischen Oberfläche und teurem LLM. Sie fängt den Roh-Prompt ab, bewertet Intent lokal (ohne Token-Kosten), injiziert *nur* das Schema dieses Turns, führt aus falls das Modell ein Tool anfordert — und lässt den Payload anschließend fallen.

Kein Session-Lock. Kein totes Token-Gewicht. Kein Restart-Button.

## Keine GitHub-Actions, keine Playground-Runner

Dieses Repository stellt **nur Quellcode** bereit. Tests und Demo laufen lokal auf deinem Rechner.

- **Kein** GitHub-Actions-Workflow
- **Kein** Codespaces- / Spark- / Playground-Setup
- Der Demo-Operator ist ein **Mock** — null Token, null Runner-Minuten

```bash
python -m unittest discover -s tests -v
python examples/demo.py
```

## Drei Axiome

1. **Zero-Token Edge Analysis** — Intent wird lokal gelesen, bevor eine Cloud-API angefasst wird.
2. **Ephemeral Schema Injection** — Fähigkeiten existieren nur für den Turn, der sie braucht.
3. **Implicit Garbage Collection** — der Kontext-Frame wird nach der Ausführung geleert. Die Unterhaltung bleibt. Die Pipeline blockiert nicht.

Ein Werkzeug, das dieser Turn nicht braucht, existiert in diesem Turn nicht.

## Schnellstart

```bash
git clone https://github.com/DarkStarMass/jit-middleware-interceptor.git
cd jit-middleware-interceptor
python examples/demo.py
python -m unittest discover -s tests -v
```

Python 3.10+, keine Drittanbieter-Abhängigkeiten. Englische README mit API-Beispielen: [`README.md`](README.md).

System-Prompt für das Downstream-LLM: [`docs/SYSTEM_INSTRUCTION.md`](docs/SYSTEM_INSTRUCTION.md).

## Kanonische Demonstration

| # | Prompt | Erwartete Pipeline |
| --- | --- | --- |
| 1 | `Erkläre mir die Philosophie des kleinsten Nenners.` | Reiner Text. Keine Tools. |
| 2 | `Ich brauche ein Video von einer Protein-Faltung.` | Veo injiziert, ausgeführt, geleert. |
| 3 | `Mach mir eine entspannte Musik für den Feierabend.` | Leitung frei. Lyria lädt sauber. |

Die Routing-Matrix ist zweisprachig (EN/DE), damit die deutschen Demo-Prompts wie spezifiziert dispatchen.

## Lizenz & Credits

MIT. Copyright (c) 2026 **★DarkStarMass★ & Vega (with Grok Build Engine)**.

Vision: ★DarkStarMass★. Protokoll: Vega. Build: Grok. Details: [`CREDITS.md`](CREDITS.md).
