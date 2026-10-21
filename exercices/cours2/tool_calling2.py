import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from ollama import chat

MODEL = "qwen2.5:1.5b"

NUM_RUNS_TIMES = 1


# ==========================
# Available tools 
# ==========================
def add(a: int, b: int) -> int:
    """Add two integers and return the sum."""
    return a + b


def greet(name: str) -> str:
    """Return a friendly greeting for the given name."""
    return f"Hello, {name}!"


# Tool registry for dynamic execution by name
TOOL_REGISTRY: Dict[str, Any] = {
    "add": add,
    "greet": greet,
}


# ==========================
# Prompt
# ==========================

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """
"""


def run_model_for_tool_call(system_prompt: str) -> List[Any]:
    # TODO: Fill this in!
    return []


def execute_tool_call(call: Any) -> str:
    name = call.function.name
    if not isinstance(name, str):
        raise ValueError("Tool call missing 'name' string")
    func = TOOL_REGISTRY.get(name)
    if func is None:
        raise ValueError(f"Unknown tool: {name}")
    args = call.function.arguments or {}
    if not isinstance(args, dict):
        raise ValueError("Tool call arguments must be an object")
    return func(**args)


def test_your_prompt(system_prompt: str) -> bool:
    """Run up to NUM_RUNS_TIMES: require the model to produce a valid tool call."""
    for _ in range(NUM_RUNS_TIMES):
        try:
            tool_calls = run_model_for_tool_call(system_prompt)
        except Exception as exc:
            print(f"Failed to get tool calls: {exc}")
            continue

        if not tool_calls:
            print("Model returned no tool calls")
            continue

        ok = True
        for call in tool_calls:
            try:
                actual = execute_tool_call(call)
            except Exception as exc:
                print(f"Tool execution failed: {exc}")
                ok = False
                continue
            print(f"Generated tool call: {call}")
            print(f"Generated output: {actual}")
        if ok:
            return True
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
