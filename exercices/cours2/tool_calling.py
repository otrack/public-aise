import ast
import json
import os
from typing import Any, Dict, List, Optional, Tuple, Callable

from dotenv import load_dotenv
from ollama import chat

MODEL = "qwen2.5:1.5b"

NUM_RUNS_TIMES = 3

# ==========================
# Tool implementation (the "executor")
# ==========================
def add(a: int, b: int) -> int:
    return a + b


def greet(name: str) -> str:
    return f"Hello, {name}!"

# Tool registry for dynamic execution by name
TOOL_REGISTRY: Dict[str, function] = {
    "add": add,
    "greet": greet
}

# ==========================
# Prompt
# ==========================

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """
"""

def resolve_path(p: str) -> str:
    if os.path.isabs(p):
        return p
    here = os.path.dirname(__file__)
    c1 = os.path.join(here, p)
    if os.path.exists(c1):
        return c1
    # Try sibling of project root if needed
    return p


def extract_tool_call(text: str) -> Dict[str, Any]:
    """Parse a single JSON object from the model output."""
    text = text.strip()
    # Some models wrap JSON in code fences; attempt to strip
    if text.startswith("```") and text.endswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json\n"):
            text = text[5:]
    try:
        obj = json.loads(text)
        print(obj)
        return obj
    except json.JSONDecodeError:
        raise ValueError("Model did not return valid JSON for the tool call")


def run_model_for_tool_call(system_prompt: str) -> Dict[str, Any]:
    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Call the 'greet' tool with argument name set to 'Alice'."},
        ],
        options={"temperature": 0.1},
    )
    content = response.message.content
    print("CONTENT\n"+ content+"\n"+"END CONTENT")
    return extract_tool_call(content)


def execute_tool_call(call: Dict[str, Any]) -> str:
    name = call.get("tool")
    if not isinstance(name, str):
        raise ValueError("Tool call JSON missing 'tool' string")
    print(name)
    func = TOOL_REGISTRY.get(name)
    if func is None:
        raise ValueError(f"Unknown tool: {name}")
    args = call.get("args", {})
    if not isinstance(args, dict):
        raise ValueError("Tool call JSON 'args' must be an object")
    return func(**args)

def test_your_prompt(system_prompt: str) -> bool:
    """Run once: require the model to produce a valid tool call."""
    for _ in range(NUM_RUNS_TIMES):
        try:
            call = run_model_for_tool_call(system_prompt)
        except Exception as exc:
            print(f"Failed to parse tool call: {exc}")
            continue
        print(call)
        try:
            actual = execute_tool_call(call)
        except Exception as exc:
            print(f"Tool execution failed: {exc}")
            continue
        print(f"Generated tool call: {call}")
        print(f"Generated output: {actual}")

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
