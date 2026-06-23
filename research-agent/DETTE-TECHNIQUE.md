# Dette Technique — research-agent

## Priorisation

| # | Item | Priorité | Statut |
|---|---|---|---|
| 1 | `from tavily import TavilyClient` eager dans `tools/search` | P1 | ✅ corrigé |
| 2 | Fonctions non typées (`# type: ignore[no-untyped-def]`) | P2 | à faire |
| 3 | Clients LLM instanciés au niveau module | P2 | à faire |
| 4 | `settings = Settings()` au niveau module + `openai_api_key` requis | P2 | à faire |
| 5 | Fondations governance/gateway non câblées | P2 | à faire |
| 6 | `except Exception` qui avale dans `verifier` | P3 | à faire |
| 7 | Aucun workflow CI ni seuil de couverture | P3 | à faire |

## 1. Import lourd eager dans `tools/search`

**Problème** — `app/tools/search.py:4` fait `from tavily import TavilyClient` au niveau module.

**Impact** — L'import casse tout le graphe (`app/agent/graph.py` importe `web_search`) si `tavily` est absent (vérifié : `ModuleNotFoundError: tavily`) ; collecte des tests bloquée.

**Action** — Import paresseux dans la fonction d'appel et/ou client injectable ; s'assurer que `tavily` est bien une dépendance déclarée.

**Priorité** — P1

## 2. Fonctions non typées

**Problème** — `# type: ignore[no-untyped-def]` sur `_get_calendar_service` (`tools/calendar.py:14`), `_get_gmail_service` (`tools/gmail.py:17`), `build_research_graph` (`agent/graph.py:116`).

**Impact** — Trous de typage sur des fonctions structurantes ; `mypy --strict` contourné.

**Action** — Annoter les retours (clients Google typés via `Resource`, type du graphe compilé) et retirer les `type: ignore`.

**Priorité** — P2

## 3. Clients LLM au niveau module

**Problème** — `_llm = ChatOpenAI(...)` dans `app/agent/graph.py:13` et `app/tools/verifier.py:22`.

**Impact** — Instanciation à l'import (clé requise tôt), init non paresseuse, mocking difficile, tests couplés au réseau.

**Action** — Factory paresseuse injectable / routage via `LLMGateway`.

**Priorité** — P2

## 4. `settings = Settings()` au niveau module

**Problème** — `app/config.py:37` construit le singleton à l'import (`# type: ignore[call-arg]`) ; `openai_api_key` sans défaut.

**Impact** — Import dépendant de l'env ; échec en test/CI sans variables.

**Action** — `@lru_cache get_settings()` + défaut de test, injection par dépendance.

**Priorité** — P2

## 5. Fondations governance/gateway non câblées

**Problème** — `LLMGateway`, `RBACPolicy.authorize`, `mask_pii`, `IdempotencyGuard` ne sont pas appelés dans `app/agent/*`, `app/tools/*` ni les routes.

**Impact** — Garanties (fallback LLM, RBAC, masquage PII) inactives — sensible vu les connecteurs (Gmail, Calendar, Notion, Slack) qui manipulent des données personnelles.

**Action** — Brancher `mask_pii` sur les sorties des connecteurs et router les appels LLM via le gateway.

**Priorité** — P2

## 6. `except Exception` qui avale

**Problème** — `app/tools/verifier.py:48` capture `Exception` largement.

**Impact** — Masque les erreurs de vérification de sources ; observabilité dégradée.

**Action** — Restreindre au type attendu, journaliser, incrémenter un compteur `METRICS`.

**Priorité** — P3

## 7. Aucun workflow CI ni seuil de couverture

**Problème** — Pas de `.github/workflows/` ni de `fail_under` dans `pyproject.toml`.

**Impact** — Aucune barrière automatique (lint/typecheck/tests/couverture).

**Action** — Ajouter `ci.yml` (lint → typecheck → test) et `[tool.coverage.report] fail_under = <seuil>`.

**Priorité** — P3
