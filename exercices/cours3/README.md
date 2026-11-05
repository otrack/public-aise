# Cours 3 — Le développement agentique

## Installation

### Le projet du cours

Les exercices de ce cours se font sur un petit projet, `wikidiff`, qui a son propre dépôt git :
vous y travaillerez avec un agent de code, et chaque tâche s'y termine par un commit. Clonez-le
dans ce répertoire, sous le nom `project` :

```sh
cd exercices/cours3
git clone https://github.com/otrack/projet-aise-cours3.git project
```

Ce dépôt est indépendant de celui du cours : vos commits restent dans `project/`, et un
`git pull` du dépôt du cours ne les touche pas. La suite (l'installation de l'agent, puis les
quatre tâches) est dans `project/README.md`.

## Les fichiers

### Démos

| Fichier | Ce qu'il montre |
|---|---|
| `demo_agent1.py` | la boucle minimale d'un assistant (*REPL*) : lire la demande, appeler le modèle, afficher sa réponse, garder l'historique |
| `demo_agent2.py` | un agent de code : la même boucle, avec une boucle interne d'appels d'outils (lire, écrire et exécuter un fichier, chercher sur Wikipédia), affichée sous forme de trace ReAct (*Thought*, *Action*, *Obs.*) |

`demo_agent2.py` ne lit, n'écrit et n'exécute que dans `/tmp/agent`, vidé à chaque lancement, et
demande votre accord avant d'exécuter un fichier. Sa recherche sur Wikipédia demande une connexion
à Internet.

`demo_agent1.py` utilise `qwen2.5:1.5b` ; `demo_agent2.py`, `ministral-3:3b`.

### Exercices

Comme indiqué ci-dessus, les exercices de ce cours sont les tâches du projet `wikidiff` : voir `project/README.md`.
