"""
======================================================================
JIT MIDDLEWARE INTERCEPTOR v2.0 - "THE INVISIBLE ROUTER"
Design Philosophy: Minimal Entropy, Zero-State Blocking, Edge-First Privacy.
======================================================================
This middleware sits seamlessly between a User Interface (Client) and an
expensive LLM API (Server). It intercepts the raw user request, performs a
zero-cost intent analysis locally, dynamically injects ONLY the required tool
schema into the payload, and sanitizes the pipeline immediately after execution.
======================================================================

Archival single-file form of the original specification, kept so the
published package can be compared against the source manuscript.
The installable library lives in `src/jmi/`.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Callable, List, Optional

# ------------------------------------------------------------------------------
# 1. ONTOLOGY & DATA STRUCTURES (The Clean Foundation)
# ------------------------------------------------------------------------------

@dataclass
class Tool:
    """Represents a discrete capability without polluting the global state."""
    name: str
    description: str
    schema: Dict[str, Any]
    executor: Callable[[str], str]

@dataclass
class Payload:
    """The standardized data packet traveling through the middleware."""
    user_prompt: str
    injected_tools: List[Dict[str, Any]] = field(default_factory=list)
    system_instruction: str = "Be simple, clear, and kind."

# ------------------------------------------------------------------------------
# 2. THE REGISTRY (Passive Storage, Zero Overhead)
# ------------------------------------------------------------------------------

class MiddlewareToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool
        print(f"[REGISTRY] Tool registered and dormant: {tool.name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def get_all_names(self) -> List[str]:
        return list(self._tools.keys())

# ------------------------------------------------------------------------------
# 3. THE ANALYZER (Local Edge-Computing for Privacy & Cost Avoidance)
# ------------------------------------------------------------------------------

class LocalIntentAnalyzer:
    """
    Acts as a zero-cost gatekeeper. Instead of asking the expensive LLM
    which tool to use, we analyze intent locally before the network call.
    """
    def __init__(self, registry: MiddlewareToolRegistry):
        self.registry = registry

    def evaluate(self, prompt: str) -> List[str]:
        """
        In a production environment, this could be a tiny, lightning-fast
        local model (like a quantized BERT or simple semantic keyword mapper).
        """
        prompt_lower = prompt.lower()
        active_tools = []

        # Heuristic routing matrix
        routing_matrix = {
            "veo_video_generation": ["video", "render", "animation", "shot", "mp4"],
            "lyria_music_generation": ["music", "audio", "song", "track", "melody", "musik"],
            "file_system_manager": ["save", "file", "document", "pdf", "logbook"]
        }

        for tool_name, keywords in routing_matrix.items():
            if any(kw in prompt_lower for kw in keywords) and self.registry.get_tool(tool_name):
                active_tools.append(tool_name)

        return active_tools

# ------------------------------------------------------------------------------
# 4. THE CORE MIDDLEWARE (The Interceptor)
# ------------------------------------------------------------------------------

class JITMiddleware:
    def __init__(self, registry: MiddlewareToolRegistry):
        self.registry = registry
        self.analyzer = LocalIntentAnalyzer(registry)

    def process(self, user_text: str, mock_llm_api_call: Callable) -> str:
        """
        The main lifecycle: Intercept -> Inject -> Forward -> Execute -> Clean.
        """
        print(f"\n[{'-'*60}]")
        print(f"📥 [MIDDLEWARE IN] Raw Request: '{user_text}'")

        # Step 1: Intercept & Analyze locally (Zero cost, high privacy)
        required_tool_names = self.analyzer.evaluate(user_text)
        payload = Payload(user_prompt=user_text)

        # Step 2: Inject precisely what is needed (Just-in-Time)
        for name in required_tool_names:
            tool = self.registry.get_tool(name)
            if tool:
                payload.injected_tools.append(tool.schema)
                print(f"💉 [MIDDLEWARE INJECT] dynamically loaded schema: {name}")

        if not payload.injected_tools:
            print("🛡️ [MIDDLEWARE ROUTE] Clean text pipeline. No tools injected.")

        # Step 3: Forward optimized payload to the LLM
        print("🌐 [NETWORK] Forwarding payload to LLM...")
        llm_response = mock_llm_api_call(payload)

        # Step 4: Intercept LLM Response & Execute Tool if requested
        final_output = self._handle_llm_response(llm_response)

        # Step 5: Garbage Collection is implicit since 'payload' is destroyed
        # when the function exits. The pipeline remains completely unblocked.
        print(f"🧹 [MIDDLEWARE CLEANUP] Pipeline flushed. Ready for next prompt.")
        print(f"[{'-'*60}]\n")

        return final_output

    def _handle_llm_response(self, llm_response: Dict[str, Any]) -> str:
        """Parses the LLM's return. Executes local tools if the LLM called them."""
        if "tool_call" in llm_response:
            tool_name = llm_response["tool_call"]["name"]
            arguments = llm_response["tool_call"]["arguments"]

            print(f"⚙️ [MIDDLEWARE EXECUTE] LLM requested local tool: {tool_name}")
            tool = self.registry.get_tool(tool_name)

            if tool:
                result = tool.executor(arguments)
                return f"✅ Tool Output: {result}"
            else:
                return f"❌ Error: LLM requested unknown tool {tool_name}"
        else:
            return f"💬 LLM Output: {llm_response.get('text', '')}"

# ------------------------------------------------------------------------------
# 5. DEMONSTRATION & DEPLOYMENT
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    registry = MiddlewareToolRegistry()

    registry.register(Tool(
        name="veo_video_generation",
        description="Generates 9:16 high quality videos.",
        schema={"type": "function", "function": {"name": "veo_video_generation"}},
        executor=lambda args: "Rendered a beautiful 15s MP4 via Veo 3.1."
    ))

    registry.register(Tool(
        name="lyria_music_generation",
        description="Generates audio tracks and soundscapes.",
        schema={"type": "function", "function": {"name": "lyria_music_generation"}},
        executor=lambda args: "Synthesized a clean cinematic audio track."
    ))

    middleware = JITMiddleware(registry)

    def mock_google_gemini_api(payload: Payload) -> Dict[str, Any]:
        """Simulates what the LLM does when it receives the payload."""
        if payload.injected_tools:
            tool_to_call = payload.injected_tools[0]["function"]["name"]
            return {"tool_call": {"name": tool_to_call, "arguments": payload.user_prompt}}
        return {"text": "Das ist eine reine Textantwort basierend auf purer Logik."}

    middleware.process("Erkläre mir die Philosophie des kleinsten Nenners.", mock_google_gemini_api)
    middleware.process("Ich brauche ein Video von einer Protein-Faltung.", mock_google_gemini_api)
    middleware.process("Mach mir eine entspannte Musik für den Feierabend.", mock_google_gemini_api)
