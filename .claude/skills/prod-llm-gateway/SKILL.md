---
name: prod-llm-gateway
description: Ajoute un gateway LLM asynchrone abstrait par Protocol, avec bascule primaire→fallback, providers Local/Failing/Http (compatible chat completions LiteLLM/OpenAI) et streaming. À utiliser dès qu'un projet appelle un LLM et doit rester testable hors-ligne et résilient aux pannes de fournisseur.
---

# prod-llm-gateway

Découple le code métier du fournisseur LLM concret : il manipule un `LLMProvider` (Protocol).
Un `LocalProvider` déterministe permet de tourner hors-ligne et en tests ; en production on
injecte un `HttpLLMProvider` (Bedrock/LiteLLM/OpenAI) respectant le même contrat. Le `LLMGateway`
tente le primaire, journalise et bascule sur le fallback en cas d'échec.

## Quand l'utiliser

- Tout projet qui appelle un LLM (synthèse, agent, RAG).
- Besoin de tests déterministes sans réseau et de résilience multi-modèle.

## Fichiers générés

| Asset | Destination |
|---|---|
| `gateway.py.tmpl` | `src/__PKG__/gateway.py` |
| `schemas.py.tmpl` | `src/__PKG__/schemas.py` (ou fusionner dans un schemas existant) |

Dépend de `prod-config` (`Settings`, `get_settings`) et `prod-observability` (`METRICS`,
`record_span`). Si `prod-observability` n'est pas appliqué, retirer les appels `METRICS`/`record_span`.

## Étapes d'adaptation

1. Substituer `__PKG__`.
2. Vérifier que `schemas.py` expose `Message`, `Role`, `LLMRequest`, `LLMResponse`.
3. En production, renseigner `llm_api_base`/`llm_api_key` : `build_default_gateway()` bascule
   automatiquement de `LocalProvider` vers `HttpLLMProvider`.
4. Pour un autre protocole d'API (ex. Bedrock natif), créer une classe respectant le `Protocol`
   `LLMProvider` (méthodes `complete` et `stream`) — ne pas modifier `LLMGateway`.

## Checklist de validation

- Test du fallback : `LLMGateway(primary=FailingProvider(...), fallback=LocalProvider(...))`
  retourne bien la réponse du fallback avec `used_fallback=True`.
- Streaming testé via `make_gateway` (voir `prod-test-harness`).
- `mypy --strict` passe (les providers concrets satisfont le `Protocol`).
