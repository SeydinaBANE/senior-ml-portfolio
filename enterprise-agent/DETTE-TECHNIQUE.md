# Dette Technique — enterprise-agent

## Priorisation

| # | Item | Priorité | Statut |
|---|---|---|---|
| 1 | Attribut `metadata` réservé sur un modèle SQLAlchemy | P1 | ✅ corrigé |
| 2 | `settings = Settings()` au niveau module (`# type: ignore`) | P2 | à faire |
| 3 | Clients LLM/embeddings instanciés au niveau module | P2 | à faire |
| 4 | `dependencies.py` annote `RBACPolicy`/`AuditLog` sans les importer | P2 | ✅ corrigé |
| 5 | Fondations governance/gateway non câblées | P2 | à faire |
| 6 | `except Exception` qui avale dans `tool_agent` | P3 | à faire |
| 7 | `Any` dans `memory/cache.py` | P3 | à faire |
| 8 | Aucun seuil de couverture (`fail_under`) | P3 | à faire |

## 1. Attribut `metadata` réservé sur un modèle SQLAlchemy

**Problème** — `app/db/models.py:28` déclare `metadata: Mapped[dict] = mapped_column(JSON, ...)`. `metadata` est un nom réservé par l'API Declarative de SQLAlchemy.

**Impact** — `InvalidRequestError` à l'import du module ; la suite de tests ne peut même pas être collectée (vérifié : `pytest` échoue immédiatement). Bloque tout le projet.

**Action** — Renommer la colonne (ex. `meta`/`payload`) avec `mapped_column("metadata", JSON)` si le nom SQL doit rester, et typer `Mapped[dict[str, object]]`. Ajouter un test d'import du modèle.

**Priorité** — P1

## 2. `settings = Settings()` au niveau module

**Problème** — `app/config.py:47` construit le singleton au moment de l'import, avec `# type: ignore[call-arg]`.

**Impact** — Toute importation de `app.config` exige l'environnement complet ; casse l'import en test/CI quand une variable manque, et masque l'erreur de typage.

**Action** — Exposer `@lru_cache get_settings()` et injecter via dépendance ; supprimer le `type: ignore` en typant les champs requis ou en fournissant des défauts de test.

**Priorité** — P2

## 3. Clients LLM/embeddings instanciés au niveau module

**Problème** — `_llm = ChatOpenAI(...)` dans `agents/supervisor.py:24`, `agents/specialized/{rag,memory,tool}_agent.py`, et `_embeddings = OpenAIEmbeddings(...)` dans `rag/retriever.py:9`.

**Impact** — Instanciation à l'import (clé API requise tôt), pas d'init paresseuse, difficile à mocker → tests fragiles et couplés au réseau.

**Action** — Passer par `build_default_gateway()` / une factory paresseuse injectable ; supprimer les singletons module-level.

**Priorité** — P2

## 4. `dependencies.py` annote des types non importés

**Problème** — `app/dependencies.py` annote `get_rbac_policy() -> RBACPolicy` et `get_audit_log() -> AuditLog` mais n'importe que `Principal, audit_log, rbac_policy`.

**Impact** — `mypy --strict` échoue (noms non définis), même si `from __future__ import annotations` masque l'erreur au runtime.

**Action** — Importer `RBACPolicy, AuditLog` depuis `app.governance`.

**Priorité** — P2

## 5. Fondations governance/gateway non câblées

**Problème** — `RBACPolicy.authorize`, `mask_pii`, `IdempotencyGuard` et `LLMGateway` sont fournis et injectables mais jamais appelés dans les routes/agents.

**Impact** — Code mort apparent ; les garanties (RBAC, masquage PII, idempotence, fallback LLM) ne s'appliquent pas réellement.

**Action** — Brancher `authorize` au point d'entrée des outils, `mask_pii` sur les réponses, `IdempotencyGuard` sur les écritures, et router les appels LLM via le gateway.

**Priorité** — P2

## 6. `except Exception` qui avale

**Problème** — `app/agents/specialized/tool_agent.py:28` capture `Exception` largement.

**Impact** — Masque les erreurs réelles, complique le debug et l'observabilité.

**Action** — Restreindre au type attendu, journaliser via `get_logger`, et incrémenter un compteur `METRICS`.

**Priorité** — P3

## 7. `Any` dans `memory/cache.py`

**Problème** — `cache_get(...) -> Any | None` et `cache_set(key, value: Any, ...)` (`app/memory/cache.py:18,23`).

**Impact** — Perte de garanties de typage sur une primitive très utilisée.

**Action** — Introduire un type générique borné ou (dé)sérialiser un modèle Pydantic typé.

**Priorité** — P3

## 8. Aucun seuil de couverture

**Problème** — La couverture est mesurée mais aucun `fail_under` n'est configuré dans `pyproject.toml`.

**Impact** — Une baisse de couverture passe inaperçue en CI.

**Action** — Ajouter `[tool.coverage.report] fail_under = <seuil>` et l'appliquer en CI.

**Priorité** — P3
