# Dette Technique — enterprise-rag

## Priorisation

| # | Item | Priorité | Statut |
|---|---|---|---|
| 1 | `from datasets import Dataset` eager dans `ragas_eval` | P1 | ✅ corrigé |
| 2 | Attribut `metadata` réservé sur le modèle `Document` | P1 | ✅ corrigé |
| 3 | Dépendance `alembic` déclarée mais aucune migration | P2 | à faire |
| 4 | Clients LLM/embeddings instanciés au niveau module | P2 | à faire |
| 5 | `settings = Settings()` au niveau module + champs requis | P2 | à faire |
| 6 | Fondations governance/gateway non câblées | P2 | à faire |
| 7 | `dict` non typés en signature | P3 | ✅ corrigé |
| 8 | Aucun seuil de couverture (`fail_under`) | P3 | à faire |

## 1. Import lourd eager dans `ragas_eval`

**Problème** — `app/evaluation/ragas_eval.py:3` fait `from datasets import Dataset` au niveau module.

**Impact** — Import lourd (et optionnel) exécuté dès l'import du module ; si `datasets` n'est pas installé, l'évaluation **et** la collecte des tests cassent (vérifié : `ModuleNotFoundError: datasets`).

**Action** — Import paresseux dans la fonction qui l'utilise, et déclarer `datasets`/`ragas` dans un extra optionnel `[project.optional-dependencies] eval`.

**Priorité** — P1

## 2. Alembic déclaré mais inutilisé

**Problème** — `alembic` est dans les dépendances mais il n'existe aucun dossier de migrations ni `alembic.ini`.

**Impact** — Le schéma DB n'est pas versionné/reproductible ; faux signal de maturité.

**Action** — Initialiser Alembic (`alembic init`) et générer la migration initiale, ou retirer la dépendance si non utilisée.

**Priorité** — P2

## 3. Clients LLM/embeddings au niveau module

**Problème** — `_llm = ChatOpenAI(...)` dans `rag/grader.py:18`, `rag/rewriter.py:10`, `rag/generator.py:18` ; `_embeddings = OpenAIEmbeddings(...)` dans `ingestion/store.py:7` et `rag/retriever/vector.py:9`.

**Impact** — Instanciation à l'import (clé requise tôt), init non paresseuse, mocking difficile, tests couplés au réseau.

**Action** — Factory paresseuse injectable / routage via `LLMGateway`.

**Priorité** — P2

## 4. `settings = Settings()` au niveau module

**Problème** — `app/config.py:33` construit le singleton à l'import (`# type: ignore[call-arg]`) ; `openai_api_key`, `database_url`, `database_url_sync` sans défaut.

**Impact** — Import dépendant de l'env ; échec en test/CI sans variables.

**Action** — `@lru_cache get_settings()` + défauts de test, injection par dépendance.

**Priorité** — P2

## 5. Fondations governance/gateway non câblées

**Problème** — `LLMGateway`, `RBACPolicy.authorize`, `mask_pii`, `IdempotencyGuard` ne sont pas appelés dans `app/rag/*` ni les routes.

**Impact** — Garanties (fallback LLM, RBAC, masquage PII) inactives.

**Action** — Router les appels LLM du pipeline via le gateway ; masquer les PII des réponses générées.

**Priorité** — P2

## 6. `dict` non typé en signature

**Problème** — `app/rag/retriever/vector.py:19` : `metadata: dict`.

**Impact** — Viole le typage strict.

**Action** — Typer `dict[str, object]` ou un modèle Pydantic.

**Priorité** — P3

## 7. Aucun seuil de couverture

**Problème** — Pas de `fail_under` dans `pyproject.toml` ; pas de workflow CI (`.github/`) non plus.

**Impact** — Aucune barrière automatique sur la couverture ni sur lint/tests.

**Action** — Ajouter un `ci.yml` (lint → typecheck → test) et `[tool.coverage.report] fail_under = <seuil>`.

**Priorité** — P3
