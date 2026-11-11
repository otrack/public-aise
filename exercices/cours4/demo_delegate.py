"""An opencode agent delegates a Wikipedia lookup to a subagent (lecture 4,
"Superviseur et ouvriers, en pratique : les sous-agents").

The primary agent (build) does not look the fact up itself: it calls its subagent tool with a task
for wiki-searcher, a subagent declared in a Markdown file, .opencode/agents/wiki-searcher.md: a
description (so that the primary agent knows when to call it), permissions (webfetch allowed, edit
and shell denied), then its prompt. The subagent starts with a fresh context (its prompt and the
task, not the conversation of the primary agent), reads Wikipedia with its webfetch tool, and
returns a short report: the pages it read stay in its own context. The primary agent writes its
final answer from that report.

The script writes the subagent in a new temporary directory and runs opencode there in headless
mode (opencode run --format json: one event per line). Only the events of the primary agent are
printed by opencode run; the session of the subagent is read afterwards (opencode session export).

Usage: python3 demo_delegate.py [--model provider/model] [--question "..."] [--timeout 600]
Needs: opencode v2, with a model it can use (by default Mistral, with its API key), and the network.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

QUESTION = "En quelle année Carl Hewitt a-t-il proposé le modèle d'acteur ?"

# The subagent: a frontmatter (description, mode, permissions), then its prompt. The permissions
# are an ordered list of rules, and the last one that matches wins; they are enforced by opencode,
# whatever the model writes.
SUBAGENT = """\
---
description: Cherche un fait sur Wikipédia et rend une réponse d'une phrase, avec l'URL de l'article. À utiliser pour toute question factuelle.
mode: subagent
permissions:
  - action: webfetch
    resource: "*"
    effect: allow
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
  - action: subagent
    resource: "*"
    effect: deny
---
Cherche la réponse sur Wikipédia avec l'outil webfetch, ne réponds pas de mémoire : d'abord
la recherche, https://fr.wikipedia.org/w/index.php?search=<mots-clés>, puis l'article trouvé.
Réponds en une phrase, et donne l'URL de l'article que tu as lu.
"""

PROMPT = ("Ne cherche pas toi-même : confie la question suivante au sous-agent wiki-searcher, "
          "puis donne la réponse finale en une phrase, avec la source qu'il t'indique.\n"
          "Question : {question}")


def show(label: str, text: str) -> None:
    """Print one step of the trace: a label, then the text, indented under it."""
    print(f"\n{label} :\n  " + text.strip().replace("\n", "\n  "), flush=True)


def characters(n: int) -> str:
    """A number of characters, the French way: 60 918 caractères."""
    return f"{n:,} caractères".replace(",", " ")


def opencode(arguments: list[str], directory: str, timeout: float) -> subprocess.CompletedProcess:
    """Run an opencode command in directory."""
    # opencode run takes its directory from $PWD, which cwd alone does not change
    return subprocess.run(["opencode", *arguments], cwd=directory,
                          env={**os.environ, "PWD": directory},
                          capture_output=True, text=True, timeout=timeout)


def run_agent(directory: str, prompt: str, model: str, timeout: float) -> list[dict]:
    """Run the primary agent of opencode in headless mode, in directory; return its events."""
    # --standalone: a private server; --auto: with no terminal to answer a permission request,
    # approve it, unless a rule denies it
    run = opencode(["run", "--standalone", "--auto", "--format", "json", "--model", model, prompt],
                   directory, timeout)
    events = [json.loads(line) for line in run.stdout.splitlines() if line.startswith("{")]
    if not events and run.returncode != 0:
        sys.exit(f"opencode s'est arrêté avec le code {run.returncode} : {run.stderr.strip()}")
    return events


def subagent_messages(call: dict, directory: str) -> list[dict]:
    """The messages of the subagent's session, which opencode run does not print."""
    session_id = call.get("metadata", {}).get("metadata", {}).get("sessionID")
    if session_id is None:  # the call failed before the subagent started
        return []
    run = opencode(["session", "export", "--standalone", session_id], directory, timeout=60)
    return json.loads(run.stdout)["messages"] if run.returncode == 0 else []


def show_subagent(call: dict, directory: str) -> None:
    """Print a call of the subagent tool: the task, what the subagent did, and its report."""
    show(f"l'agent principal délègue à {call['input']['agent']}", call["input"]["prompt"])
    read = 0  # characters the subagent read with its tools
    for message in subagent_messages(call, directory):
        if message["type"] == "user":  # the first message of its fresh context: the task, nothing else
            show("le sous-agent part d'un contexte neuf, avec ce seul message", message["text"])
        for part in message.get("content", []):
            if part["type"] == "tool":
                state = part["state"]
                if state["status"] == "completed":
                    pages = sum(len(c.get("text", "")) for c in state.get("content", []))
                    read += pages
                    result = characters(pages) + " lus"
                else:  # e.g. a page that does not exist, or a tool the subagent is denied
                    error = state.get("error")
                    result = "erreur : " + (error["message"] if isinstance(error, dict) else str(error))
                show(f"le sous-agent appelle {part['name']}",
                     f"{json.dumps(state['input'], ensure_ascii=False)}\n-> {result}")
    # the tool result is the report, between <subagent ...> and </subagent>
    report = re.sub(r"</?subagent[^>]*>", "", call.get("output") or call.get("error", "")).strip()
    show("rapport du sous-agent", report)
    print(f"  (le sous-agent a lu {characters(read)} ; "
          f"l'agent principal ne reçoit que le rapport, {characters(len(report))})")


def trace(events: list[dict], directory: str) -> None:
    """Print the events of the primary agent, in order; its last text is the final answer."""
    last = max((i for i, event in enumerate(events) if event["type"] == "text"), default=None)
    for i, event in enumerate(events):
        part = event.get("part", {})
        if event["type"] == "tool_use" and part["tool"] == "subagent":
            show_subagent(part["state"], directory)
        elif event["type"] == "tool_use":
            show(f"l'agent principal appelle {part['tool']}",
                 json.dumps(part["state"]["input"], ensure_ascii=False))
        elif event["type"] == "text":
            show("réponse finale" if i == last else "l'agent principal", part["text"])
        elif event["type"] == "error":
            show("erreur", event["error"]["message"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", default="mistral/ministral-14b-2512",
                        help="model of both agents, as provider/model (default: %(default)s)")
    parser.add_argument("--question", default=QUESTION,
                        help="question to delegate (default: %(default)s)")
    parser.add_argument("--timeout", type=float, default=600,
                        help="seconds allowed to the opencode run (default: %(default)s)")
    args = parser.parse_args()
    if shutil.which("opencode") is None:
        sys.exit("opencode est introuvable : installez-le (https://opencode.ai) et ajoutez-le au PATH.")

    with tempfile.TemporaryDirectory(prefix="demo-delegate-") as directory:
        agent_file = Path(directory, ".opencode", "agents", "wiki-searcher.md")
        agent_file.parent.mkdir(parents=True)
        agent_file.write_text(SUBAGENT)
        show(f"le sous-agent, déclaré dans {agent_file.relative_to(directory)}", SUBAGENT)
        prompt = PROMPT.format(question=args.question)
        show(f"prompt de l'agent principal (build, {args.model})", prompt)
        print("\n(opencode travaille : l'agent principal, puis le sous-agent...)", flush=True)
        try:
            events = run_agent(directory, prompt, args.model, args.timeout)
        except subprocess.TimeoutExpired:
            sys.exit(f"opencode n'a pas répondu en {args.timeout:.0f} s (voir --timeout).")
        trace(events, directory)
