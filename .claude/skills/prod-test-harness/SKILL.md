---
name: prod-test-harness
description: Met en place les conventions de tests « sans service externe » — fixtures SQLite in-memory, provider LLM scripté déterministe (ScriptedProvider/make_gateway), reset des métriques, injection httpx.MockTransport/ASGITransport, asyncio_mode=auto et seuil de couverture. À utiliser pour rendre la suite de tests rapide, déterministe et offline.
---

# prod-test-harness

Codifie la règle d'or : **aucun service externe pour les tests unitaires**. Les stores sont
substitués par du SQLite en mémoire, les LLM par des providers scriptés, et le réseau par
`httpx.MockTransport`/`ASGITransport`. Garantit des tests rapides, déterministes, et une
couverture ≥ 80 % en CI.

## Quand l'utiliser

- Juste après avoir généré le code métier (gateway, governance…).
- Pour remplacer des tests qui touchent un vrai réseau/DB/LLM.

## Fichiers générés

| Asset | Destination |
|---|---|
| `conftest.py.tmpl` | `tests/conftest.py` |
| `test_example.py.tmpl` | `tests/test_example.py` (modèle à dupliquer/supprimer) |

## Outils fournis

- `ScriptedProvider(model, reply)` — provider LLM qui renvoie toujours `reply`.
- `make_gateway(reply)` — `LLMGateway` dont le primaire renvoie `reply`.
- `business_engine` (fixture) — Engine SQLite in-memory seedé (`StaticPool`).
- `reset_metrics` (fixture autouse) — `METRICS.reset()` entre chaque test.

## Conventions

- `asyncio_mode = "auto"` (défini dans `pyproject.toml`) : pas de `@pytest.mark.asyncio`.
- Nommage : `test_<fonction>_<cas>` ; au minimum 1 cas nominal + 1 cas d'erreur par fonction.
- Tests nécessitant la stack Docker : marqueur `@pytest.mark.integration` (lancés via `pytest -m integration`).
- Réseau : injecter `httpx.MockTransport(handler)` ou `ASGITransport(app=...)`, jamais d'appel réel.

## Checklist de validation

- `make test` vert, `--cov-fail-under=80` respecté.
- Aucun test n'ouvre de socket réseau ni ne dépend d'un service local.
- `make_gateway`/`ScriptedProvider` couvrent les chemins LLM sans appel externe.
