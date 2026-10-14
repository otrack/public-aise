from ollama import chat

MODEL="ministral-3:3b"

SYSTEM_PROMPT = """Réponds uniquement par du code, sans explication."""

VAGUE_PROMPT = "Donne-moi la commande pour trouver les fichiers Python modifiés récemment."

EXPLICIT_PROMPT = """Commande bash (Linux, GNU find) qui liste les fichiers .py du dossier src/ et de ses sous-dossiers modifiés il y a moins de 24 heures. Un fichier par ligne."""

# What the explicit prompt asks for, checked on the answer.
CHECKS = {
    "dossier src/": lambda text: "src" in text,
    "fichiers .py": lambda text: '"*.py"' in text or "'*.py'" in text,
    "moins de 24 heures": lambda text: "-mtime -1" in text,
    "pas de ls ni awk": lambda text: "ls " not in text and "awk" not in text,
}

for name, prompt in [("PROMPT VAGUE", VAGUE_PROMPT), ("PROMPT EXPLICITE", EXPLICIT_PROMPT)]:
    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0},
    )
    text = response.message.content.strip()
    print(f"=== {name} ===\n{prompt}\n--- Réponse du modèle ---\n{text}\n")
    print("--- Contraintes respectées ---")
    for label, check in CHECKS.items():
        print(f"[{'x' if check(text) else ' '}] {label}")
    print()
