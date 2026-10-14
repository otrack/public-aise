# Cours 1 — Les assistants IA : bases des LLM et du prompting

## Installation

Cette installation sert à tous les cours.

### Python

Il faut Python 3.10 ou plus récent.

```sh
python3 --version
```

Créez un environnement virtuel dans le répertoire `exercices/`, puis installez les dépendances :

```sh
cd exercices
python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

### Ollama (modèles locaux)

Les scripts dialoguent avec un modèle de langage qui tourne en local grâce à
[Ollama](https://ollama.com). Installez-le en suivant les instructions de
<https://ollama.com/download>. Sous Linux :

```sh
curl -fsSL https://ollama.com/install.sh | sh
```

Vérifiez que le serveur tourne (l'application de bureau le lance d'elle-même ; sinon, lancez `ollama serve`),
puis téléchargez les deux modèles utilisés par les cours 1 et 2 :

```sh
ollama pull qwen2.5:1.5b        # la plupart des scripts (environ 1 Go)
ollama pull ministral-3:3b      # les scripts qui demandent un modèle plus fort (environ 3 Go)
```

Vérifiez que tout fonctionne :

```sh
ollama run qwen2.5:1.5b "Say hello"
```

## Les fichiers

### Démos

| Fichier | Ce qu'il montre |
|---|---|
| `demo_personna.py` | la persona : un *system prompt* qui fixe le ton de la réponse (un second, en commentaire, à essayer) |
| `demo_be_explicit.py` | un *prompt* vague, puis un *prompt* explicite ; le script vérifie ce que la réponse respecte |
| `demo_good_prompt.py` | « pourquoi ma fonction ne marche pas ? », puis la même question avec le code, le but et l'erreur |

### Exercices

| Fichier | À écrire | Ce qui est vérifié |
|---|---|---|
| `k_shot_prompting.py` | un *system prompt* avec des exemples (*few-shot*) | le modèle écrit un mot à l'envers |
| `chain_of_thought.py` | un *system prompt* qui fait raisonner étape par étape | le bon résultat d'un petit problème, sur plusieurs essais |
| `self_consistency_prompting.py` | un *system prompt* pour un problème de distances | le vote majoritaire sur plusieurs réponses |
| `reflexion.py` | le *prompt* de *reflexion* et le message qui renvoie les tests échoués au modèle | la fonction `is_valid_password` générée passe la suite de tests |

`demo_be_explicit.py`, `demo_personna.py`, `k_shot_prompting.py` et `reflexion.py` utilisent
`ministral-3:3b` ; les autres, `qwen2.5:1.5b`.
