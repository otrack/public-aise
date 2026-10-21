"""Context stacking: the model is stateless, its "memory" is what the harness re-sends.

Run it twice and tell the model your name, then ask it back:
    python memoire.py                    # the whole conversation is re-sent at each call
    python memoire.py --without-history  # only the last message is sent

Watch the number of prompt tokens: with the history, it grows at every turn.
"""
import sys

from ollama import chat

MODEL = "qwen2.5:1.5b"
WITHOUT_HISTORY = "--without-history" not in sys.argv

history = []  # the conversation so far, kept by the harness (this script), not by the model

print(f"History {'ON' if WITHOUT_HISTORY else 'OFF'}. Type 'exit' to stop.")
while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ("exit", "quit"):
        break
    history.append({"role": "user", "content": user_input})

    # TODO: Fill this in! Build the list of messages sent to the model.
    sent = []

    response = chat(model=MODEL, messages=sent, options={"temperature": 0})
    answer = response.message.content
    history.append({"role": "assistant", "content": answer})

    print(f"\nModel: {answer}")
    print(f"  [sent {len(sent)} message(s), {response.prompt_eval_count} prompt tokens]"
)
