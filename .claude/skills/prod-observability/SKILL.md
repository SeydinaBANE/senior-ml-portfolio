---
name: prod-observability
description: Ajoute une observabilité légère — compteurs de métriques et traces de spans en mémoire, via un context manager record_span et un singleton METRICS. Abstrait Langfuse/Prometheus pour rester exécutable hors-ligne et testable. À utiliser pour instrumenter durées, succès/échecs et appels LLM.
---

# prod-observability

Fournit `METRICS` (compteurs) et `record_span(...)` (chronométrage d'un bloc) sans dépendance
externe : tout est agrégé en mémoire et loggé en JSON. En production, on rebranche `record_span`
sur Langfuse et `METRICS` sur un exporter Prometheus — l'API ne change pas.

## Quand l'utiliser

- Dès `prod-llm-gateway` ou `prod-governance` (ils référencent `METRICS`/`record_span`).
- Pour mesurer durées d'opérations et taux de succès/échec sans stack de monitoring locale.

## Fichiers générés

| Asset | Destination |
|---|---|
| `observability.py.tmpl` | `src/__PKG__/observability.py` |

## API

- `METRICS.incr("name")` — incrémente un compteur.
- `METRICS.reset()` — vide compteurs et spans (à appeler en `fixture` de test).
- `with record_span("op", key="val"): ...` — enregistre la durée du bloc.

## Étapes d'adaptation

1. Substituer `__PKG__`.
2. Nommer les compteurs/spans de façon hiérarchique (`llm.primary.success`, `connector.sql.query`).
3. En production, remplacer le corps de `record_span` par un span Langfuse et exporter
   `METRICS.counters` vers Prometheus — garder la même signature.

## Checklist de validation

- `record_span` enregistre bien une durée > 0 et un log `span`.
- `METRICS.reset()` remet les compteurs à zéro entre deux tests.
- `mypy --strict` passe.
