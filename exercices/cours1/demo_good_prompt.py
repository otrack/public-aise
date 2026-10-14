from ollama import chat

MODEL = "qwen2.5:1.5b"

CODE = '''def map_users_by_id(users):
    result = {}
    for i in range(len(users) + 1):
        result[users[i]["id"]] = users[i]
    return result'''

SYSTEM_PROMPT = """Tu es un assistant serviable qui adore programmer au niveau d'un développeur senior. Réponds toujours de manière succinte. Si tu ne sais pas répondre car il te manque du contexte, indique le clairement."""

BAD_PROMPT = "Pourquoi ma fonction map_users_by_id ne marche pas ?"

GOOD_PROMPT = f"""Ma fonction Python map_users_by_id doit transformer une liste d'utilisateurs en dictionnaire indexé par id.
Elle plante : IndexError: list index out of range.

Exemple : map_users_by_id([{{"id": 1, "name": "Alice"}}])
Attendu : {{1: {{"id": 1, "name": "Alice"}}}}

Voici le code :
{CODE}

Quel est le bug, et comment le corriger ?"""

for name, prompt in [("MAUVAIS PROMPT", BAD_PROMPT), ("BON PROMPT", GOOD_PROMPT)]:
    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        options={"temperature": 0},
    )
    print(f"=== {name} ===\n{prompt}\n--- Réponse du modèle ---\n{response.message.content.strip()}\n")
