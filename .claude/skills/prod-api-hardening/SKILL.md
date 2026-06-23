---
name: prod-api-hardening
description: Durcit une API FastAPI — rate limiting sliding-window par IP, traçage par correlation-ID (X-Request-ID lié aux logs structlog), et authentification par clé API mappée à un rôle (422 header manquant, 401 clé invalide, 403 rôle insuffisant). À utiliser avant d'exposer publiquement une API.
---

# prod-api-hardening

Ajoute les protections transverses au niveau ASGI/FastAPI : limite de débit par IP en fenêtre
glissante, identifiant de corrélation propagé dans tous les logs et renvoyé au client, et
dépendances d'authentification par `X-API-Key` → rôle (pour brancher la RBAC de `prod-governance`).

## Quand l'utiliser

- Toute API exposée (interne ou publique) nécessitant auth + rate limit + traçabilité.
- Dépend de `prod-config` (`get_settings`) et idéalement `prod-governance` (`Principal`, `RBACPolicy`).

## Fichiers générés

| Asset | Destination |
|---|---|
| `middleware.py.tmpl` | `src/__PKG__/middleware.py` |
| `dependencies.py.tmpl` | `src/__PKG__/dependencies.py` |

## Câblage

```python
from __PKG__.middleware import setup_middlewares
setup_middlewares(app, max_requests=cfg.rate_limit_max_requests, window_sec=cfg.rate_limit_window_sec)
```
Protéger un endpoint : `principal: Principal = Depends(get_principal)`.

## Règles d'auth (à respecter)

- Header `X-API-Key` **obligatoire** (`Header(...)`) → manquant = `422` automatique.
- Clé absente du mapping `__PREFIX__API_KEYS` (`key:role,...`) → `401`.
- Permission insuffisante (via `RBACPolicy.authorize`) → `403`.
- `/health` reste public.

## Étapes d'adaptation

1. Substituer `__PKG__`.
2. Ajuster `_CHAT_PATHS` aux routes à limiter (ou limiter toutes les routes hors `/health`).
3. Adapter `get_principal` au schéma de rôle réel ; brancher `get_rbac_policy`/`get_audit_log`.

## Checklist de validation

- Sans header → 422 ; clé invalide → 401 ; rôle insuffisant → 403 ; `/health` → 200.
- Au-delà de `max_requests` dans la fenêtre → 429.
- Chaque réponse renvoie un `X-Request-ID` présent aussi dans les logs JSON.
