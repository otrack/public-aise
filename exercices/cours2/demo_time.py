import asyncio
import os
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = "ministral-3:3b"

def stream_chat(**kwargs) -> ollama.Message:
    """Call the model, printing its text as it is generated; return the whole message."""
    content, tool_calls = "", []
    for chunk in ollama.chat(**kwargs, stream=True):
        if chunk.message.content and not content:
            print("\nAssistant: ", end="")
        print(chunk.message.content, end="", flush=True)
        content += chunk.message.content
        # a tool call is not streamed: it comes whole, in one chunk
        tool_calls += chunk.message.tool_calls or []
    if content:
        print()
    return ollama.Message(role="assistant", content=content, tool_calls=tool_calls or None)

async def main():
    # 1. Define the MCP server to connect to. 
    # We use 'uvx' to run the official Python-based time server on the fly.
    server_params = StdioServerParameters(
        command="uvx",
        args=["mcp-server-time"],
        env=None
    )

    print("Starting MCP Client and connecting to server...")
    
    # 2. Connect to the MCP Server
    # uvx writes "Installed N packages" on the server's stderr, which stdio_client forwards to the
    # terminal by default: send it to /dev/null so that it does not pollute the output
    with open(os.devnull, "w") as server_log:
        async with stdio_client(server_params, errlog=server_log) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 3. Fetch available tools from the MCP server
                mcp_tools = await session.list_tools()
            
                # 4. Convert MCP tool schemas into Ollama's expected format
                ollama_tools = [{"type": "function", "function":
                                 {"name": t.name, "description": t.description, "parameters": t.input_schema}}
                                for t in mcp_tools.tools]

                print(f"Loaded {len(ollama_tools)} tools from MCP server.")

                # 5. Set up the chat with Ollama
                messages = [
                    {"role": "system", "content": "You are an helpful assistant. Always answer in a concise and informative manner."},
                    {"role": "user", "content": "What is the exact current time in Paris?"}
                ]
                print(f"\nSystem: {messages[0]['content']}")
                print(f"\nUser: {messages[1]['content']}")

                # First LLM call: providing the prompt and the available tools
                # (a plain answer, if the model calls no tool, is printed as it is generated)
                message = stream_chat(
                    model=MODEL,
                    messages=messages,
                    tools=ollama_tools,
                    options={"temperature": 0}
                )

                # Append the model's response (which contains the tool call) to the history
                messages.append(message)

                # 6. Check if the model decided to call a tool
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_name = tool_call['function']['name']
                        tool_args = tool_call['function']['arguments']
                        print(f"\n[Tool Execution] Model called '{tool_name}' with arguments: {tool_args}")

                        # Execute the tool on the MCP server
                        mcp_result = await session.call_tool(tool_name, tool_args)

                        # Extract the text content from the MCP response
                        tool_content = "\n".join(
                            [c.text for c in mcp_result.content if c.type == "text"]
                        )
                        print(f"[Tool Result] {tool_content}")

                        # Append the tool's result to the message history
                        messages.append({
                            "role": "tool",
                            "name": tool_name,
                            "content": tool_content
                        })

                    # Second LLM call: generating the final human-readable response, printed as it is generated
                    stream_chat(
                        model=MODEL,
                        messages=messages
                    )

if __name__ == "__main__":
    asyncio.run(main())
