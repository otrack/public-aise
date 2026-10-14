import os
from dotenv import load_dotenv
from ollama import chat

MODEL="ministral-3:3b"

NUM_RUNS_TIMES = 1

SYSTEM_PROMPT = """Tu es un assistant serviable qui adore programmer, au niveau d'un développeur senior, et tu es très détaillé et pédant dans tes réponses."""
# SYSTEM_PROMPT = """Tu es le BFF numérique d'une personne de la génération Z. Écris toujours comme si tu envoyais un message sur Snapchat à 2 h du matin."""

USER_PROMPT = """Écris une fonction Python qui renvoie \texttt{True} si un mot est un palindrome."""

response = chat(
    model=MODEL,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT},
    ],
    options={"temperature": 0.1},
)
output_text = response.message.content.strip()

print(f"Model output: '{output_text}'")
