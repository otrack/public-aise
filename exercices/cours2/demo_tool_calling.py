import json

from ollama import chat
from ollama._utils import convert_function_to_tool

MODEL = "qwen2.5:1.5b"

def search_flights(from_city: str, to_city: str, date: str) -> str:
    """Return available flights for a route on a date (mock).

    Args:
        from_city: City of departure.
        to_city: City of arrival.
        date: Date of the flight, as YYYY-MM-DD.
    """
    return f"{from_city} -> {to_city} on {date}: TAP 1702 at 45€, Iberia 894 at 62€"


def show(title: str, data) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))


messages = [{"role": "user", "content": "Find me a flight Paris to Lisbon on 2026-06-12."}]
tools = [search_flights]

# 1. What the model receives: the messages, and each tool as a JSON schema
show("Sent to the model", {
    "messages": messages,
    "tools": [convert_function_to_tool(t).model_dump(exclude_none=True) for t in tools],
})

# temperature 0: the same output at every run of the demo
response = chat(
    model=MODEL,
    messages=messages,
    tools=tools,
    options={"temperature": 0})

# 2. What the model emits: no answer in plain text, but a structured tool call
show("Emitted by the model", response.message.model_dump(exclude_none=True))

# 3. The harness executes the declared call; the model never runs it itself
call = response.message.tool_calls[0].function
result = search_flights(**call.arguments)
print("\n=== Executed by the harness ===")
print(f"{call.name}(**{call.arguments}) -> {result}")

# 4. The harness sends the result back: the call is an "assistant" message,
#    its result a "tool" message; then the model answers in plain text
messages.append(response.message)
messages.append({"role": "tool", "content": result, "tool_name": call.name})
show("Sent back to the model", messages[-1])

final = chat(
    model=MODEL,
    messages=messages,
    tools=tools,
    options={"temperature": 0})

show("Final answer of the model", final.message.model_dump(exclude_none=True))
