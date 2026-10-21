# Cours 2 — Appel d'outils et ancrage

## Installation

Les modèles sont ceux du cours 1 (voir `cours1/README.md`).

### uv (serveurs MCP)

`demo_time.py` lance son serveur MCP avec `uvx`, fourni avec [uv](https://docs.astral.sh/uv/).
uv fait partie de `requirements.txt` : il est installé avec les autres dépendances (voir
`cours1/README.md`). Si votre environnement a été créé avant, mettez-le à jour, puis vérifiez :

```sh
pip install -r requirements.txt
uvx --version
```

`uvx` n'est trouvé que si l'environnement virtuel est activé.

Le premier lancement télécharge le serveur MCP : il faut une connexion à Internet.

## Les fichiers

### Démos

| Fichier | Ce qu'il montre |
|---|---|
| `demo_tool_calling.py` | un premier outil, `search_flights` : le schéma que reçoit le modèle, l'appel qu'il déclare, le résultat exécuté |
| `demo_rag.py` | un RAG sur une base SQLite embarquée : le modèle cherche des vols, puis répond à partir des résultats |
| `demo_time.py` | un client MCP minimal : il découvre les outils du serveur `mcp-server-time` et appelle l'un d'eux |
| `demo_safe_execution.py` | le *harness* vérifie le chemin d'un appel d'outil, et n'écrit que dans un dossier de `/tmp` |

### Exercices

| Fichier | À écrire | Ce qui est vérifié |
|---|---|---|
| `memory.py` | la liste des messages envoyés au modèle, avec ou sans l'historique | le modèle se souvient de votre nom seulement avec l'historique ; le script affiche les *tokens* envoyés à chaque tour |
| `tool_calling.py` | un *system prompt* qui fait écrire au modèle un appel d'outil en JSON (l'ancienne méthode) | l'appel est analysé et exécuté |
| `tool_calling2.py` | un *system prompt* et l'appel à `chat()` avec l'argument `tools=` (la méthode actuelle) | le modèle déclare un appel structuré, qui est exécuté |

`demo_rag.py` et `demo_time.py` utilisent `ministral-3:3b` ; les autres, `qwen2.5:1.5b`.
