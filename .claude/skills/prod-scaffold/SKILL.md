---
name: prod-scaffold
description: Bootstrap un projet Python GenAI prêt pour la production (FastAPI + pydantic strict). Génère Makefile, pyproject (ruff/mypy strict/pytest/coverage), pre-commit, CI GitHub Actions, Dockerfile multi-stage, docker-compose, .env.example et les docs AGENTS/PROJET/POC/MVP. À utiliser au démarrage d'un nouveau projet ou pour aligner un projet existant sur le socle.
---

# prod-scaffold

Crée l'ossature d'outillage commune à tous les projets GenAI « production-grade » : un seul
workflow `make`, mypy strict, ruff, pre-commit, CI reproduisant `make build`, et un seuil de
couverture. C'est la première skill à appliquer ; les autres (`prod-config`, `prod-llm-gateway`,
…) viennent remplir `src/__PKG__/`.

## Quand l'utiliser

- Nouveau projet GenAI backend Python (FastAPI).
- Projet existant à mettre au standard (importer les fichiers manquants, ne pas écraser à l'aveugle).

## Fichiers générés

Depuis `assets/`, en remplaçant les placeholders, écrire à la racine du projet cible :

| Asset | Destination |
|---|---|
| `Makefile.tmpl` | `Makefile` |
| `pyproject.toml.tmpl` | `pyproject.toml` |
| `pre-commit-config.yaml.tmpl` | `.pre-commit-config.yaml` |
| `ci.yml.tmpl` | `.github/workflows/ci.yml` |
| `dependabot.yml.tmpl` | `.github/dependabot.yml` |
| `PULL_REQUEST_TEMPLATE.md.tmpl` | `.github/PULL_REQUEST_TEMPLATE.md` |
| `Dockerfile.tmpl` | `Dockerfile` |
| `docker-compose.yml.tmpl` | `docker-compose.yml` |
| `env.example.tmpl` | `.env.example` |
| `AGENTS.md.tmpl` | `AGENTS.md` |
| `PROJET.md.tmpl` | `PROJET.md` |

Créer aussi le layout : `src/__PKG__/__init__.py`, `tests/__init__.py`.

## Étapes d'adaptation

1. Choisir les valeurs : `__PROJECT__` (nom lisible, ex. *Liaison*), `__PKG__` (package importable,
   ex. `liaison`), `__PREFIX__` (préfixe env majuscule, ex. `LIAISON_`).
2. Substituer les placeholders dans chaque fichier copié (`sed` ou édition).
3. Ajuster les dépendances métier dans `pyproject.toml` (Qdrant, SQLAlchemy… selon le projet) ;
   garder le bloc `[dev]`/`[test]` tel quel.
4. Adapter `docker-compose.yml` aux services réellement nécessaires (Postgres/Qdrant/Redis…).
5. Renseigner `AGENTS.md`/`PROJET.md` avec l'architecture réelle.

## Checklist de validation

- `make init` installe l'env et les hooks sans erreur.
- `make build` (= `lint typecheck test`) est vert.
- `ruff format --check src/ tests/` passe (la CI l'exige).
- La couverture atteint le seuil `--cov-fail-under` défini dans `pyproject.toml`.
