# Dette Technique — intel-agent

## Priorisation

| # | Item | Priorité | Statut |
|---|---|---|---|
| 1 | `settings = Settings()` au niveau module + `openai_api_key` requis | P2 | à faire |
| 2 | Clients LLM instanciés au niveau module | P2 | à faire |
| 3 | Fondations governance/gateway non câblées | P2 | à faire |
| 4 | `except Exception` qui avale dans `intelligence` | P3 | à faire |
| 5 | `# type: ignore` sur l'instrumentation OTel | P3 | à faire |
| 6 | Aucun seuil de couverture (`fail_under`) | P3 | à faire |

## 1. `settings = Settings()` au niveau module

**Problème** — `app/config.py:31` construit le singleton à l'import (`# type: ignore[call-arg]`) ; `openai_api_key` n'a pas de défaut.

**Impact** — Import de `app.config` dépendant de l'env ; échec possible en test/CI ; `type: ignore` masquant.

**Action** — `@lru_cache get_settings()` + défaut de test, injection par dépendance.

**Priorité** — P2

## 2. Clients LLM au niveau module

**Problème** — `_llm = ChatOpenAI(...)` dans `app/agent/summarizer.py:14` et `app/agent/intelligence.py:14`.

**Impact** — Instanciation à l'import, init non paresseuse, mocking difficile, tests couplés au réseau.

**Action** — Factory paresseuse injectable / routage via `LLMGateway`.

**Priorité** — P2

## 3. Fondations governance/gateway non câblées

**Problème** — `LLMGateway`, `RBACPolicy.authorize`, `mask_pii`, `IdempotencyGuard` ne sont pas appelés dans `app/agent/*` ni les routes.

**Impact** — Garanties (fallback LLM, RBAC, masquage PII) inactives.

**Action** — Router les appels LLM via le gateway et brancher l'autorisation/masquage aux points d'entrée.

**Priorité** — P2

## 4. `except Exception` qui avale

**Problème** — `app/agent/intelligence.py:36` capture `Exception` largement.

**Impact** — Masque les erreurs réelles ; observabilité dégradée.

**Action** — Restreindre au type attendu, journaliser, incrémenter un compteur `METRICS`.

**Priorité** — P3

## 5. `# type: ignore` sur l'instrumentation OTel

**Problème** — `app/observability/tracing.py:24` : `FastAPIInstrumentor.instrument_app(...)  # type: ignore[arg-type]`.

**Impact** — Dette de typage tolérée ; peut masquer une incompatibilité de version.

**Action** — Vérifier la signature de la lib et retirer le `type: ignore`, ou documenter la raison.

**Priorité** — P3

## 6. Aucun seuil de couverture

**Problème** — Pas de `fail_under` dans `pyproject.toml`.

**Impact** — Une régression de couverture passe inaperçue en CI (alors que le projet est la référence CI/CD).

**Action** — Ajouter `[tool.coverage.report] fail_under = <seuil>` et le gater dans `ci.yml`.

**Priorité** — P3
