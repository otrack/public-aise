"""A web search done by one agent, then by several agents in parallel (lecture 4, "Des réussites").

Anthropic's multi-agent research system: a lead agent splits the question, subagents search in
parallel, and the lead gathers their findings; it beats a single agent doing all the searches.
Here, the split is done by hand, one question per agent:

- sequential: ONE agent gets all the questions, and looks them up one after the other;
- parallel: one agent per question, all launched at once, then their answers are gathered.

Each agent is opencode in headless mode (opencode run), with the plan agent (it reads, it does not
edit), which reads Wikipedia with its webfetch tool.

Usage: python3 demo_parallel.py [--model provider/model] [--mode les-deux] [--timeout 300]
Needs: opencode, with a model it can use (by default Mistral, with its API key), and the network.
"""
import argparse
import json
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

QUESTIONS = [
    "En quelle année est sortie la version 3.0 du langage Python ?",
    "Quelle est la hauteur de la tour Eiffel ?",
    "Quelle est la longueur de la Seine ?",
    "Quel jour a eu lieu le premier vol de l'Airbus A380 ?",
]

SEARCH = "Cherche sur Wikipédia avec l'outil webfetch, ne réponds pas de mémoire."


def seconds(duration: float) -> str:
    """A duration, the French way: 42,3 s."""
    return f"{duration:.1f} s".replace(".", ",")


def ask(prompt: str, model: str, timeout: float, live: bool = False) -> tuple[str, list[str], float]:
    """Run one opencode agent on the prompt.

    Return its answer (or the error), the pages it read, and how long it took.
    With live=True, print each step of the agent (the pages it reads, its texts) as it happens.
    """
    command = ["opencode", "run", "--standalone", "--auto", "--format", "json",
               "--model", model, "--agent", "plan", prompt]
    start = time.perf_counter()
    run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    timer = threading.Timer(timeout, run.kill)  # stop the agent if it takes too long
    timer.start()
    # --format json: one event per line (the agent's texts, its tool calls, its errors), read as they come
    answer, pages, error = "", [], ""
    for line in run.stdout:
        if not line.startswith("{"):  # not an event (e.g. a warning)
            continue
        event = json.loads(line)
        if event["type"] == "text":
            answer = event["part"]["text"].strip()  # the last text is the final answer
            if live:
                first = answer.splitlines()[0] if answer else ""  # the full answer is printed at the end
                print(f"   [{seconds(time.perf_counter() - start)}] l'agent écrit : {first[:100]}", flush=True)
        elif event["type"] == "tool_use" and event["part"]["tool"] == "webfetch":
            url = event["part"]["state"]["input"]["url"]
            pages.append(url)
            if live:
                print(f"   [{seconds(time.perf_counter() - start)}] l'agent lit {url}", flush=True)
        elif event["type"] == "error":
            error = event["error"]["message"]
    run.wait()
    timed_out = not timer.is_alive()  # the timer fired: the agent was killed
    timer.cancel()
    duration = time.perf_counter() - start
    if timed_out:
        return f"[erreur : pas de réponse en {seconds(timeout)}]", pages, duration
    if error:
        return f"[erreur : {error}]", pages, duration
    if run.returncode != 0:
        answer += f"\n[erreur : opencode s'est arrêté avec le code {run.returncode}] {run.stderr.read().strip()}"
    return answer.strip(), pages, duration


def sequential(model: str, timeout: float) -> None:
    """One agent, all the questions in one prompt, looked up one after the other."""
    numbered = "\n".join(f"{i}. {q}" for i, q in enumerate(QUESTIONS, 1))
    prompt = (f"Réponds aux questions suivantes, l'une après l'autre. {SEARCH}\n{numbered}\n"
              "Termine par une réponse courte (une phrase) par question, numérotée comme la question.")
    answer, pages, _ = ask(prompt, model, timeout, live=True)  # its progress, step by step
    print("\nRéponse de l'agent :")
    print(answer)
    print(f"(pages lues : {', '.join(pages) or 'aucune'})")


def parallel(model: str, timeout: float) -> None:
    """One agent per question, all launched at once; their answers are gathered."""
    prompts = [f"{q} {SEARCH} Réponds en une phrase." for q in QUESTIONS]
    with ThreadPoolExecutor(max_workers=len(prompts)) as pool:
        results = list(pool.map(lambda prompt: ask(prompt, model, timeout), prompts))
    # all the agents are done: gather their answers
    for i, (question, (answer, pages, duration)) in enumerate(zip(QUESTIONS, results), 1):
        answer = answer.replace("\n", "\n   ")  # indented under its question
        print(f"{i}. {question}\n   {answer}")
        print(f"   (agent {i} : {seconds(duration)} ; pages lues : {', '.join(pages) or 'aucune'})")


def timed(label: str, search, model: str, timeout: float) -> float:
    """Print the label, run the search, print and return its wall-clock duration."""
    print(f"\n== {label} ==", flush=True)
    start = time.perf_counter()
    search(model, timeout)
    duration = time.perf_counter() - start
    print(f"durée : {seconds(duration)}")
    return duration


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", default="mistral/ministral-14b-2512",
                        help="model of the agents, as provider/model (default: %(default)s)")
    parser.add_argument("--mode", choices=["sequentiel", "parallele", "les-deux"], default="les-deux")
    parser.add_argument("--timeout", type=float, default=300,
                        help="seconds allowed to each opencode run (default: %(default)s)")
    args = parser.parse_args()
    if shutil.which("opencode") is None:
        sys.exit("opencode est introuvable : installez-le (https://opencode.ai) et ajoutez-le au PATH.")

    durations = []
    if args.mode in ("sequentiel", "les-deux"):
        durations.append(timed("Recherche séquentielle : un agent, les questions l'une après l'autre",
                               sequential, args.model, args.timeout))
    if args.mode in ("parallele", "les-deux"):
        durations.append(timed("Recherche parallèle : un agent par question",
                               parallel, args.model, args.timeout))
    if len(durations) == 2:
        speedup = durations[0] / durations[1]
        print(f"\nAccélération (durée séquentielle / durée parallèle) : {speedup:.1f}".replace(".", ","))
