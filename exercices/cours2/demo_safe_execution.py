import json
import os
import subprocess

from ollama import chat

MODEL = "qwen2.5:1.5b"

# The only folder the tool may write to
SANDBOX = "/tmp/demo_safe_execution"


def write_file(path: str, content: str) -> str:
    """Write content to a file, with bash.

    Args:
        path: Path of the file, e.g. palindrome.py.
        content: Text to write in the file.
    """
    # bash runs in the sandbox: a relative path stays inside it
    subprocess.run(["bash", "-c", 'cat > "$1"', "bash", path],
                   input=content, text=True, cwd=SANDBOX, check=True)
    return f"écrit : {SANDBOX}/{path}"


def check_path(path: str) -> str | None:
    """Return why the harness refuses the path, or None if it is safe."""
    if os.path.isabs(path) or path.startswith("~"):
        return "chemin absolu"
    if ".." in path.split("/"):
        return "le chemin sort du bac à sable"
    return None


def harness(call) -> str:
    """Check the declared call, and run it only if its path is safe."""
    reason = check_path(call.arguments.get("path", ""))
    if reason:
        return f"REFUSÉ : {reason}"
    return write_file(**call.arguments)


os.makedirs(SANDBOX, exist_ok=True)

# The same request, with a path inside the sandbox, then two outside of it
for path in ["palindrome.py", "/home/etudiant/palindrome.py", "../../etc/palindrome.py"]:
    prompt = (f"Crée le fichier {path} contenant une fonction Python "
              "qui renvoie True si un mot est un palindrome.")
    print(f"\n=== Prompt ===\n{prompt}")
    # temperature 0: the same output at every run of the demo
    response = chat(model=MODEL, messages=[{"role": "user", "content": prompt}],
                    tools=[write_file], options={"temperature": 0})
    for tool_call in response.message.tool_calls or []:
        call = tool_call.function
        print(f"=== Appel déclaré par le modèle ===\n{call.name}({json.dumps(call.arguments, ensure_ascii=False)})")
        print(f"=== Le harness ===\n{harness(call)}")

with open(os.path.join(SANDBOX, "palindrome.py")) as f:
    print(f"\n=== {SANDBOX}/palindrome.py ===\n{f.read()}")
