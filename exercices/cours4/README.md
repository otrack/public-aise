# Cours 4 — D'un agent à plusieurs, et l'avenir du développement logiciel

## Installation

### Le projet du cours

Le projet de ce cours est une équipe d'agents opencode (un *lead*, un product-manager, un coder,
un qa-tester et un reviewer) qui ne communique que par un dépôt git : chaque agent travaille sur sa
propre branche, et les agents s'échangent leur travail par `main`. Ce dépôt est le projet lui-même :
clonez-le dans ce répertoire, sous le nom `project` :

```sh
cd exercices/cours4
git clone https://github.com/otrack/projet-aise-cours4.git project
```

Ce dépôt est indépendant de celui du cours : les commits de l'équipe restent dans `project/`, et un
`git pull` du dépôt du cours ne les touche pas. La suite (le modèle, l'équipe, et les tâches) est
dans `project/README.md`.

## Les fichiers

### Démos

| Fichier | Ce qu'il montre |
|---|---|
| `demo_parallel.py` | une recherche d'information séquentielle, puis parallèle, avec opencode |
| `demo_delegate.py` | un agent opencode délègue une recherche sur Wikipédia à un sous-agent |

Les deux démos lancent opencode (version 2.2.5 ou plus récente) en mode non interactif
(`opencode run`), et demandent une connexion à Internet. Il leur faut un modèle : par défaut
*Ministral 3 14B*, avec une clé d'API Mistral (l'option A du projet du cours 3) ; un autre modèle se
choisit avec `--model`, par exemple :

```sh
python3 demo_parallel.py --model opencode/deepseek-v4.1-flash-free
python3 demo_delegate.py --model opencode/deepseek-v4.1-flash-free
```

### Exercices

Les exercices de ce cours sont les tâches du projet : voir `project/README.md`.
