---
name: commit-propre
description: Prépare un commit propre au format Conventional Commits. À utiliser quand je demande de commiter.
disable-model-invocation: true
allowed-tools: Bash(git status *), Bash(git diff *)
---

# Préparer un commit propre

Réponds en français et explique simplement chaque étape.

## 1. Montrer l'état du dépôt

- Lance `git status` et affiche le résultat.
- Lance `git diff` (et `git diff --staged` si des fichiers sont déjà indexés).
- Résume les changements en quelques phrases simples : quels fichiers, et ce qui a changé dans chacun.
- S'il n'y a aucun changement, dis-le et arrête-toi.

## 2. Proposer un message de commit

Propose un message en français au format Conventional Commits : `<préfixe>: <description courte>`.

Choisis un seul préfixe parmi :

| Préfixe    | Quand l'utiliser |
|------------|------------------|
| `feat`     | Nouvelle fonctionnalité visible |
| `fix`      | Correction d'un bug |
| `docs`     | Documentation uniquement (README, CLAUDE.md, commentaires) |
| `chore`    | Maintenance : configuration, dépendances, outils |
| `refactor` | Réorganisation du code sans changer son comportement |
| `test`     | Ajout ou modification de tests |

Explique en une ou deux phrases pourquoi ce préfixe convient mieux que les autres.
Si les changements mélangent plusieurs sujets, propose plutôt de les séparer en plusieurs commits.

## 3. Attendre mon accord

- Ne lance pas `git add` ni `git commit` avant que j'aie validé le message.
- Si je demande une modification, propose un nouveau message et attends de nouveau mon accord.

## 4. Ne jamais pousser

- Ne lance jamais `git push`, même après le commit.
- À la fin, rappelle que le push reste à faire par moi, si je le souhaite.
