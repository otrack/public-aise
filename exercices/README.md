# Exercices

Ce répertoire contient les scripts Python qui accompagnent le cours, un sous-répertoire par cours :

```
exercices/
├── README.md            ce fichier
├── requirements.txt     les dépendances Python, communes à tous les cours
├── cours1/            cours 1 : les assistants IA, bases des LLM et du prompting
├── cours2/            cours 2 : appel d'outils et ancrage
├── cours3/            cours 3 : le développement agentique
└── cours4/            cours 4 : plusieurs agents
```

Chaque `coursN/` a son propre `README.md` : il donne d'abord l'installation propre à ce cours,
s'il y en a une, puis présente chacun de ses fichiers. Commencez par celui de `cours1/` : il
installe Python, les dépendances et Ollama, qui servent à tous les cours.

## Démos et exercices

Il y a deux sortes de fichiers dans un répertoire de cours :

- les **démos**, `demo_*.py` : ce sont les démonstrations montrées pendant le cours ; elles
  fonctionnent telles quelles, il suffit de les lancer et de lire ce qu'elles affichent ;
- les **exercices**, tous les autres fichiers `.py` : il vous reste à écrire une partie du code
  (un *prompt*, le corps d'une fonction…). Chaque partie à écrire est signalée par le commentaire

  ```python
  # TODO: Fill this in!
  ```

  Le script vérifie ensuite votre réponse, en général en appelant le modèle plusieurs fois.

## Lancer un script

Depuis le répertoire `exercices/`, avec l'environnement virtuel activé (voir `cours1/README.md`) :

```sh
python cours1/chain_of_thought.py
```
