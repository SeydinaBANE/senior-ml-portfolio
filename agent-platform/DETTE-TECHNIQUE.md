# Dette Technique — agent-platform

## Priorisation

| # | Item | Priorité | Statut |
|---|---|---|---|
| 1 | `settings = Settings()` au niveau module + champs requis | P2 | à faire |
| 2 | `dict` non typé pour l'utilisateur courant dans `deps.py` | P2 | à faire |
| 3 | Client LLM au niveau module + `except Exception` dans le router | P2 | à faire |
| 4 | Fondations governance/gateway non câblées | P2 | à faire |
| 5 | `ruff` ignore largement S105/S106/B008 | P3 | à faire |
| 6 | Aucun seuil de couverture (`fail_under`) | P3 | à faire |

## 1. `settings = Settings()` au niveau module

**Problème** — `app/config.py:36` construit le singleton à l'import (`# type: ignore[call-arg]`) ; `secret_key`, `openai_api_key`, `database_url`, `database_url_sync` sans défaut.

**Impact** — Import de `app.config` dépendant de l'env ; échec en test/CI sans variables (vérifié : `Field required`).

**Action** — `@lru_cache get_settings()` + défauts de test, injection par dépendance.

**Priorité** — P2

## 2. `dict` non typé pour l'utilisateur courant

**Problème** — `app/api/deps.py:28,32,36` : `get_tenant_id/get_user_id/get_role(user: dict = Depends(get_current_user))`.

**Impact** — Le claim JWT circule en `dict` non typé ; aucune validation de structure, erreurs de clés silencieuses, typage strict contourné.

**Action** — Introduire un modèle Pydantic `CurrentUser` (sub, tenant_id, role) renvoyé par `get_current_user`.

**Priorité** — P2

## 3. Client LLM au niveau module + `except Exception`

**Problème** — `app/core/router/classifier.py:23` instancie `_llm = ChatOpenAI(...)` au niveau module ; `app/core/router/dispatcher.py:50` capture `Exception` largement.

**Impact** — Init non paresseuse (clé requise tôt, mocking difficile) ; les erreurs de dispatch sont avalées.

**Action** — Factory paresseuse / `LLMGateway` ; restreindre l'`except` et journaliser + `METRICS`.

**Priorité** — P2

## 4. Fondations governance/gateway non câblées

**Problème** — `LLMGateway`, `RBACPolicy.authorize`, `mask_pii`, `IdempotencyGuard` ne sont pas appelés dans le router/les routes.

**Impact** — Garanties (fallback LLM, RBAC applicatif, idempotence) inactives. La matrice `_ROLE_PERMISSIONS` (admin/developer/user) est définie mais jamais évaluée.

**Action** — Brancher `authorize` aux endpoints sensibles et router les appels LLM via le gateway.

**Priorité** — P2

## 5. `ruff` ignore largement S105/S106/B008

**Problème** — La config `ruff` ignore S105, S106 (secrets en dur) et B008 (appels dans les défauts d'arguments).

**Impact** — Masque de vrais risques (secrets, `Depends()` mal placés) sur l'ensemble du projet.

**Action** — Remplacer les ignores globaux par des `# noqa` ciblés et réactiver les règles.

**Priorité** — P3

## 6. Aucun seuil de couverture

**Problème** — Pas de `fail_under` dans `pyproject.toml`.

**Impact** — Une régression de couverture passe inaperçue en CI.

**Action** — Ajouter `[tool.coverage.report] fail_under = <seuil>` et le gater dans `ci.yml`.

**Priorité** — P3
