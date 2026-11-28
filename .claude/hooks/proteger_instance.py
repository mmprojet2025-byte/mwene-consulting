#!/usr/bin/env python3
"""Hook PreToolUse de Claude Code : protège la base et les CV (dossier instance/).

Claude Code lance ce script avant chaque commande Bash et lui envoie, sur
l'entrée standard, un JSON qui décrit la commande :
    {"tool_name": "Bash", "tool_input": {"command": "ls instance/"}, ...}

Réponse par le code de sortie :
    0 -> la commande peut continuer ;
    2 -> la commande est bloquée, et le texte écrit sur stderr est renvoyé à Claude.

Voir la règle correspondante dans CLAUDE.md (section « Règles »).
"""

import json
import sys

# Morceaux de texte interdits dans une commande Bash (comparés en minuscules).
MOTIFS_INTERDITS = ("instance/", ".db")

MESSAGE = """Commande bloquée par le hook .claude/hooks/proteger_instance.py.

Elle contient {motifs}. Le dossier instance/ contient la base de données
et les CV des candidats : ce sont des données personnelles.
Règle du projet (CLAUDE.md) : ne jamais lire, ouvrir ni inspecter ces fichiers
sans l'accord explicite de l'utilisateur, demandé à chaque fois.

Si cette commande est vraiment nécessaire, explique pourquoi à l'utilisateur :
c'est à lui de la lancer lui-même (par exemple avec « ! » dans le prompt).
"""


def main():
    try:
        donnees = json.load(sys.stdin)
        commande = donnees["tool_input"]["command"].lower()
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
        # Entrée illisible : on bloque par prudence plutôt que de laisser passer.
        print("Hook proteger_instance : description de la commande illisible, "
              "commande bloquée par prudence.", file=sys.stderr)
        return 2

    trouves = [motif for motif in MOTIFS_INTERDITS if motif in commande]
    if trouves:
        motifs = " et ".join(f"« {motif} »" for motif in trouves)
        print(MESSAGE.format(motifs=motifs), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
