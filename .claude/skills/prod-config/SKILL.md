---
name: prod-config
description: Ajoute le pattern de configuration 12-factor (pydantic-settings chargé depuis .env, préfixe d'env, get_settings caché) et le logging structuré JSON (structlog, get_logger). À utiliser juste après prod-scaffold, avant tout code métier, pour que config et logs soient disponibles partout.
---

# prod-config

Fournit deux fondations transverses : `config.py` (paramètres typés chargés de l'environnement,
12-factor) et `logging.py` (logs JSON structurés). Tout le reste du code dépend de
`get_settings()` et `get_logger(__name__)`.

## Quand l'utiliser

- Immédiatement après `prod-scaffold`.
- Pour remplacer une config ad hoc (os.environ épars) ou des `print` par du logging structuré.

## Fichiers générés

| Asset | Destination |
|---|---|
| `config.py.tmpl` | `src/__PKG__/config.py` |
| `logging.py.tmpl` | `src/__PKG__/logging.py` |

## Étapes d'adaptation

1. Substituer `__PKG__` (package) et `__PREFIX__` (préfixe env, ex. `LIAISON_`).
2. Dans `config.py`, ajouter les champs propres au projet (DSN, URLs de services, clés) avec des
   types concrets et des valeurs par défaut sûres pour le mode local/démo.
3. Exposer toute logique dérivée via des `@property` (ex. `api_key_mapping`), jamais en dur.
4. Appeler `configure_logging()` une fois au démarrage (lifespan FastAPI).

## Règles

- `get_settings()` est `@lru_cache(maxsize=1)` : une seule instance, surchargeable en tests via
  `get_settings.cache_clear()`.
- Aucun secret en dur : tout vient de `.env` / variables d'environnement.
- Logs en JSON uniquement (`JSONRenderer`), niveau piloté par `__PREFIX__LOG_LEVEL`.

## Checklist de validation

- `mypy src/` strict passe (pydantic plugin actif).
- Importer `get_settings()` ne lève pas et lit bien `.env`.
- Les logs sortent en JSON avec `request_id` quand le middleware de corrélation est branché.
