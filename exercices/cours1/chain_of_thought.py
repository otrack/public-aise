import os
import re
from dotenv import load_dotenv
from ollama import chat

MODEL = "qwen2.5:1.5b"

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT="""
"""

USER_PROMPT = """
Solve the problem below.
The last line of your reply must be EXACTLY:
Answer: <number>

A bakery bakes 192 muffins each morning.
On Monday it sold 137 muffins.
On Tuesday it baked the usual amount and sold 168.
Muffins left at the end of a day are kept for the next day.
How many are left at the end of Tuesday?
"""

# For this simple example, we expect the final numeric answer only
EXPECTED_OUTPUT = "Answer: 79"

def extract_final_answer(text: str) -> str:
    """Extract the final 'Answer: ...' line from a verbose reasoning trace.

    - Finds the LAST line that starts with 'Answer:' (case-insensitive)
    - Normalizes to 'Answer: <number>' when a number is present
    - Falls back to returning the matched content if no number is detected
    """
    clean = text.replace(",", "")
    m = re.findall(r"(?mi)^[\s*_#>-]*answer\s*[:=]?\s*[\$\\(\[{]*\s*(-?\d+(?:\.\d+)?)", clean)
    if m:
        return f"Answer: {m[-1]}"
    m = re.findall(r"\\boxed\{\s*(-?\d+(?:\.\d+)?)\s*\}", clean)
    if m:
        return f"Answer: {m[-1]}"
    tail = clean[-200:]
    m = re.findall(r"(-?\d+(?:\.\d+)?)[^\d]*$", tail)
    if m:
        return f"Answer: {m[-1]}"
    return "Answer: <none>"

def test_your_prompt(system_prompt: str, verbose: bool) -> None:
    """Run up to NUM_RUNS_TIMES and return how many times the model was right.

    Prints the success ratio.
    """
    successes = 0
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={
                "temperature": 0.3
            },
        )
        output_text = response.message.content
        reasoning, _, _ = output_text.rpartition("Answer:")

        # full model output
        if verbose:
            print(response.done_reason, response.eval_count)
            print(repr(output_text))

        final_answer = extract_final_answer(output_text)
        if final_answer.strip() == EXPECTED_OUTPUT.strip():
            successes += 1            
    print(f"{successes}/{NUM_RUNS_TIMES}")

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT, True)


