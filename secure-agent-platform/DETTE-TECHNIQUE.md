# Dette Technique — secure-agent-platform

## Priorisation

| # | Item | Priorité | Statut |
|---|---|---|---|
| 1 | Import circulaire `guardrails.engine` ↔ `guardrails.llamaguard` | P1 | ✅ corrigé |
| 2 | `settings = Settings()` au niveau module + champs requis sans défaut | P2 | à faire |
| 3 | Client LLM instancié au niveau module | P2 | à faire |
| 4 | Fondations governance/gateway non câblées | P2 | à faire |
| 5 | `dependencies.py` annote `RBACPolicy`/`AuditLog` sans les importer | P3 | ✅ corrigé |
| 6 | `dict` non typés en signature | P3 | ✅ corrigé |
| 7 | Aucun seuil de couverture (`fail_under`) | P3 | à faire |

## 1. Import circulaire des guardrails

**Problème** — `app/core/guardrails/engine.py:5` importe `LlamaGuardClient` depuis `llamaguard.py`, qui importe en retour `GuardrailResult, GuardrailVerdict` depuis `engine.py` (`llamaguard.py:6`).

**Impact** — `ImportError: cannot import name 'GuardrailResult' ... partially initialized module` ; casse la collecte des tests (vérifié).

**Action** — Extraire `GuardrailResult`/`GuardrailVerdict` dans un module neutre (ex. `guardrails/types.py`) importé par les deux.

**Priorité** — P1

## 2. `settings = Settings()` au niveau module

**Problème** — `app/config.py:34` construit le singleton à l'import (`# type: ignore[call-arg]`) ; `secret_key`, `openai_api_key`, `database_url`, `database_url_sync` n'ont pas de défaut.

**Impact** — Tout import de `app.config` exige l'env complet ; échec d'import en test/CI sans variables (vérifié : `Field required`).

**Action** — `@lru_cache get_settings()` + défauts sûrs en mode test, injection par dépendance.

**Priorité** — P2

## 3. Client LLM au niveau module

**Problème** — `app/agents/runner.py:21` : `_llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)`.

**Impact** — Instanciation à l'import (clé requise tôt), difficile à mocker, tests couplés au réseau.

**Action** — Factory paresseuse injectable / routage via `LLMGateway`.

**Priorité** — P2

## 4. Fondations governance/gateway non câblées

**Problème** — `LLMGateway`, `RBACPolicy.authorize`, `mask_pii`, `IdempotencyGuard` ne sont pas appelés dans `agents/runner.py` ni les routes.

**Impact** — Les garanties annoncées (fallback LLM, RBAC applicatif, masquage PII) ne s'exécutent pas. Note : l'autorisation principale passe par OPA (`policy/evaluator.py`), à articuler avec la couche RBAC.

**Action** — Décider de la frontière OPA vs RBAC applicatif et câbler le gateway/mask_pii dans le runner.

**Priorité** — P2

## 5. `dependencies.py` annote des types non importés

**Problème** — `app/dependencies.py` annote `-> RBACPolicy` / `-> AuditLog` mais n'importe que `Principal, audit_log, rbac_policy`.

**Impact** — `mypy --strict` échoue (noms non définis).

**Action** — Importer `RBACPolicy, AuditLog` depuis `app.governance`.

**Priorité** — P3

## 6. `dict` non typés en signature

**Problème** — `app/core/audit/logger.py:14` (`payload: dict`), `app/schemas/admin.py:25` (`config: dict`).

**Impact** — Viole le typage strict, perd la validation Pydantic des charges utiles.

**Action** — Typer `dict[str, object]` ou un modèle Pydantic dédié.

**Priorité** — P3

## 7. Aucun seuil de couverture

**Problème** — Pas de `fail_under` dans `pyproject.toml`.

**Impact** — Une régression de couverture passe inaperçue.

**Action** — Ajouter `[tool.coverage.report] fail_under = <seuil>` et l'appliquer en CI.

**Priorité** — P3
