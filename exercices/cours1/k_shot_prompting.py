import os
from dotenv import load_dotenv
from ollama import chat

MODEL="ministral-3:3b"

NUM_RUNS_TIMES = 1

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """
"""

USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

slimmer
"""

EXPECTED_OUTPUT = "remmils"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0},
        )
        output_text = response.message.content.strip()
        
        if output_text == EXPECTED_OUTPUT:
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: '{EXPECTED_OUTPUT}'")
            print(f"Actual output: '{output_text}'")
            
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)

    
