import ollama

MODEL = "qwen2.5:1.5b"
SYSTEM_PROMPT = 'You are a concise and helpful AI agent.'

# Initialize the conversation with a system prompt
messages = [
    {'role': 'system', 'content': SYSTEM_PROMPT}
]

print("Agent initialized. Type 'exit' or 'quit' to stop.")

# minimal read–eval–print loop (REPL)
while True:
    # 1. Get user input
    user_input = input("\nYou: ")
    if user_input.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break

    # 2. Add user message to history
    messages.append({'role': 'user', 'content': user_input})

    # 3. Call the model
    response = ollama.chat(
        model=MODEL,
        messages=messages)
    
    # 4. Extract and print the model's response
    agent_message = response['message']
    print(f"\nAgent: {agent_message['content']}")

    # 5. Add the model's response to the history to maintain context
    messages.append(agent_message)
