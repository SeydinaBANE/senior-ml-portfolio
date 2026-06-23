---
name: prod-serverless-aws
description: Patterns d'un backend GenAI serverless AWS prêt pour la production — Lambda (clients boto3 lazy, garde MAX_TOOL_TURNS + timeout, actions à confirmed=True idempotentes, auth JWT/JWKS + fallback guest), dual pyproject (racine mypy-only + lambda complet), et squelette CDK (VPC/Lambda Docker/API Gateway/WAF). À utiliser pour un agent déployé sur AWS Lambda.
---

# prod-serverless-aws

Reproduit l'ossature d'un agent conversationnel déployé en Lambda Docker, avec son infra CDK.
Points clés non négociables : **jamais de client boto3 au niveau module** (instanciation lazy pour
des tests mockables et un cold-start propre), garde de boucle d'outils, et écritures idempotentes
exigeant une confirmation explicite.

## Quand l'utiliser

- Agent/chatbot déployé sur AWS Lambda (Bedrock) plutôt qu'un service FastAPI long-running.
- Besoin d'infra reproductible (CDK) et de tests sans appel AWS réel.

## Fichiers générés

| Asset | Destination |
|---|---|
| `Makefile.serverless.tmpl` | `Makefile` |
| `pyproject.root.toml.tmpl` | `pyproject.toml` (racine, mypy-only) |
| `pyproject.lambda.toml.tmpl` | `lambda/pyproject.toml` (config réelle : ruff/mypy strict/pytest) |
| `handler.py.tmpl` | `lambda/handler.py` |
| `auth.py.tmpl` | `lambda/auth.py` |
| `cdk_app.py.tmpl` | `infra/cdk/app.py` |
| `cdk.json.tmpl` | `infra/cdk/cdk.json` |

## Patterns imposés

- **Clients boto3 lazy** : `_bedrock_client()`/`_ssm_client()`/`_cw_client()` retournent un
  `boto3.client(...)` à l'appel — jamais de client défini au niveau module (sinon les tests
  cassent et le cold-start importe AWS inutilement).
- **Garde de boucle** : `MAX_TOOL_TURNS` + garde de timeout (marge avant le timeout Lambda).
- **Idempotence** : les actions mutatives (`ajouter_panier`, `passer_commande`…) exigent
  `confirmed=True` ; refuser les URLs non-HTTPS quand une `base_url` est configurée.
- **Auth** : JWT RS256 validé via JWKS ; fallback invité `mode=limited` (jamais un échec dur silencieux
  non journalisé).
- **Métriques** : `_emit_metric` ne doit pas masquer une vraie erreur applicative (logger l'exception).
- **Dual pyproject** : racine mypy-only (évite les conflits d'outils) ; `lambda/pyproject.toml`
  porte ruff + mypy strict + pytest. **Pas de `[build-system]`** : Lambda déploie en image Docker.

## Testing

- `tests/conftest.py` ajoute `../lambda` au `sys.path` → lancer pytest **depuis la racine** (`make test`).
- Tous les services AWS (SSM, Bedrock, OpenSearch) sont mockés ; les clients lazy rendent ça sûr.

## Checklist de validation

- `make lint typecheck test` verts depuis la racine.
- Aucun `boto3.client(...)` au niveau module (grep).
- Une action mutative sans `confirmed=True` est refusée ; URL non-HTTPS rejetée.
- `cdk synth` réussit dans `infra/cdk/`.
