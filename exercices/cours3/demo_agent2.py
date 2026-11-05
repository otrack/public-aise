import html
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from ollama import ResponseError, chat

MODEL = "ministral-3:3b"
WORKDIR = Path("/tmp/agent")  # the only directory the agent's tools may touch, re-created at each run
MAX_STEPS = 20  # cap on tool calls per user turn, so a confused model can't loop forever

SYSTEM_PROMPT = (
    "You are a _concise_ and helpful Python coding agent. "
    "Use your tools to carry out the tasks the user asks for: "
    "do not just explain how to do them, or give code for the user to run, do them yourself. "
    f"You may only read, write and run files inside {WORKDIR}; "
    "access to any other location will be refused. "
    f"Use paths relative to {WORKDIR} (for example 'hello.py'). "
    "After writing code, run it to check that it works, and fix any errors you see. "
    "To find a fact you do not know, search Wikipedia instead of guessing. "
    # ReAct: the model writes its Thought as plain text next to each tool call (its Action)
    "Before each tool call, say in one short sentence what you are going to do and why."
)

# The ReAct trace (Thought / Action / Obs.), with the labels and the colours of the slides:
# thoughts in pale green, actions in pale blue, observations in pale violet, the answer as is
GREEN, BLUE, VIOLET, RESET = "\033[38;5;151m", "\033[38;5;153m", "\033[38;5;183m", "\033[0m"
MAX_SHOWN = 1500  # characters of a tool result printed as an observation


def show(label: str, text: str, colour: str) -> None:
    """Print one step of the trace: a label, then the text, indented under it."""
    body = text.strip().replace("\n", "\n         ")
    print(f"{colour}{label:<8} {body}{RESET}")


# --- Path guard --------------------------------------------------------------

def _safe_path(path: str) -> Path:
    """Resolve path inside WORKDIR, or raise if it points anywhere else."""
    root = WORKDIR.resolve()
    # Relative paths are taken from WORKDIR; resolve() collapses '..' and
    # follows symlinks, so neither can be used to escape.
    p = (root / path).resolve()
    if not p.is_relative_to(root):
        raise PermissionError(f"Access denied: '{path}' is outside {WORKDIR}")
    return p


# --- Tools -------------------------------------------------------------------
# Ollama builds the tool schema from each function's signature and docstring.

def read_file(path: str) -> str:
    """Read a text file and return its contents.

    Args:
        path: Path to the file to read, relative to the working directory.
    """
    return _safe_path(path).read_text()


def write_file(path: str, content: str) -> str:
    """Create or overwrite a file with the given content.

    Args:
        path: Path to the file to write, relative to the working directory.
        content: The complete text of the file.
    """
    p = _safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Wrote {len(content)} characters to {p}"


def run_python(path: str) -> str:
    """Run a Python file and return its exit code, stdout and stderr.

    Args:
        path: Path to the .py file to run, relative to the working directory.
    """
    p = _safe_path(path)
    # The model can write arbitrary code, so ask before executing it.
    if input(f"\n[Run {p}? y/N] ").strip().lower() != "y":
        return "The user declined to run the file."
    try:
        r = subprocess.run([sys.executable, str(p)], cwd=WORKDIR,
                           capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return "Error: execution timed out after 30 seconds."
    output = f"exit code: {r.returncode}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    return output[-4000:]  # keep the tail so tracebacks survive, context stays small


def _extract_to_text(extract: str) -> str:
    """Turn the HTML introduction of an article into plain text, each formula written in LaTeX."""
    def latex(match: re.Match) -> str:
        # The MathML of a formula is unreadable as text, but its alttext attribute is its LaTeX source
        tex = html.unescape(match.group(1)).strip()
        tex = re.sub(r"^\{\\displaystyle (.*)\}$", r"\1", tex, flags=re.S)  # drop the display wrapper
        return f" ${tex}$ "
    text = re.sub(r'<math[^>]*alttext="([^"]*)"[^>]*>.*?</math>', latex, extract, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))  # the other tags: keep their text only
    return re.sub(r"\s*\n\s*", "\n", re.sub(r"[ \t]+", " ", text)).strip()


def wikipedia_search(query: str, lang: str = "en") -> str:
    """Search Wikipedia and return the title and the introduction of the best matching articles.

    Args:
        query: What to search for, e.g. 'Lisbon' or 'population of Lisbon'.
        lang: Language code of the Wikipedia to search, e.g. 'en' or 'fr'.
    """
    # One call to the MediaWiki API: search (generator=search), then the HTML introduction of each
    # result (prop=extracts), kept in HTML for its formulas. No API key; Wikimedia asks for a User-Agent.
    params = urllib.parse.urlencode({
        "action": "query", "format": "json", "formatversion": 2,
        "generator": "search", "gsrsearch": query, "gsrlimit": 3,
        "prop": "extracts", "exintro": 1,
    })
    request = urllib.request.Request(
        f"https://{lang}.wikipedia.org/w/api.php?{params}",
        headers={"User-Agent": "aise-course-demo/1.0 (teaching demo)"})
    with urllib.request.urlopen(request, timeout=10) as r:
        pages = json.load(r).get("query", {}).get("pages", [])
    if not pages:
        return f"No Wikipedia article found for '{query}'."
    pages.sort(key=lambda page: page["index"])  # the search rank
    # Introductions only, cut short: the result goes back into the context of a small model
    return "\n\n".join(f"# {page['title']}\n{_extract_to_text(page.get('extract', ''))[:1000]}"
                       for page in pages)


TOOLS = {f.__name__: f for f in (read_file, write_file, run_python, wikipedia_search)}


# --- Agent loop --------------------------------------------------------------

# A fresh, empty working directory: nothing left from a previous run
shutil.rmtree(WORKDIR, ignore_errors=True)
WORKDIR.mkdir(parents=True)

messages = [
    {'role': 'system', 'content': SYSTEM_PROMPT}
]

print(f"Agent initialized (working directory: {WORKDIR}). Type 'exit' or 'quit' to stop.")

while True:
    # 1. Get user input
    user_input = input("\nYou: ")
    if user_input.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break

    # 2. Add user message to history
    messages.append({'role': 'user', 'content': user_input})

    # 3. Inner loop: let the model call tools until it gives a plain answer
    agent_message = None
    for _ in range(MAX_STEPS):
        try:
            response = chat(
                model=MODEL,
                messages=messages,
                options={"temperature": 0},
                tools=list(TOOLS.values()))
        except ResponseError as e:
            # Ollama parses the tool call the model generated; if its JSON is malformed (common when
            # the model writes a long file), the call fails. Nothing to run: tell the model, and retry.
            error = f"Error: your tool call was not valid JSON ({e.error}). Call the tool again, with valid JSON arguments."
            show("Obs.", error, VIOLET)
            messages.append({'role': 'user', 'content': error})
            continue
        agent_message = response.message
        messages.append(agent_message)

        if not agent_message.tool_calls:
            break  # no tool requested: this is the final answer

        # 4. Show the model's reasoning, then execute each requested tool and feed the result back
        if (agent_message.content or "").strip():
            show("Thought", agent_message.content, GREEN)
        for call in agent_message.tool_calls:
            name, args = call.function.name, call.function.arguments
            # the arguments in full: the code the model writes is part of its reasoning
            shown_args = "\n".join(f"{k} = {v}" for k, v in args.items())
            show("Action", f"{name}\n{shown_args}", BLUE)
            fn = TOOLS.get(name)
            try:
                result = fn(**args) if fn else f"Error: unknown tool '{name}'"
            except Exception as e:
                result = f"Error: {type(e).__name__}: {e}"
            shown = str(result)
            if len(shown) > MAX_SHOWN:
                shown = shown[:MAX_SHOWN] + "\n[...]"
            show("Obs.", shown, VIOLET)
            messages.append({'role': 'tool', 'content': str(result), 'tool_name': name})
    else:
        print("\n(Stopped after reaching the step limit.)")

    # 5. Print the agent's final response
    show("Answer", (agent_message.content if agent_message else "") or "", RESET)
