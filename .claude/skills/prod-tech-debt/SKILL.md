---
name: prod-tech-debt
description: Génère ou met à jour DETTE-TECHNIQUE.md — un registre priorisé de la dette technique (zones peu couvertes, Any généralisé, exceptions avalées, validation manquante, clients au niveau module, absence de cache/request-id…). À utiliser après une revue de code ou avant de planifier un sprint de durcissement.
---

# prod-tech-debt

Rend la dette visible et priorisée plutôt que diffuse. Chaque item décrit le problème, son impact,
et l'action corrective, classés par priorité. Sert de backlog de durcissement entre deux features.

## Quand l'utiliser

- Après `/code-review`, `/review` ou une revue manuelle.
- Avant de planifier un sprint « qualité/dette ».
- Pour documenter une décision de raccourci assumée (avec son coût).

## Fichier généré

| Asset | Destination |
|---|---|
| `DETTE-TECHNIQUE.md.tmpl` | `DETTE-TECHNIQUE.md` (racine du projet) |

## Méthode (à suivre par Claude)

1. Recenser : modules sous le seuil de couverture, branches jamais testées, `Any`/`type: ignore`,
   `except Exception` qui avalent, clients (boto3/httpx/DB) instanciés au niveau module, entrées non
   validées (pydantic absent), absence de request-id, duplication, gardes de timeout manquantes,
   absence de cache.
2. Pour chaque item : **Problème**, **Impact**, **Action** (concrète, fichier:ligne si possible),
   **Priorité** (P1 critique → P3 cosmétique).
3. Maintenir une section **Priorisation** en tête (tableau récapitulatif).

## Signaux fréquents à chasser

- Couverture < seuil sur un module clé · `Any` en signature · `_emit_metric` qui swallow ·
  validation d'entrée absente · clients au module level (cassent les tests/lazy init) · pas de
  request-id · `MAX_*` sans timeout dynamique · pas de cache RAG.

## Checklist de validation

- Chaque item a Problème / Impact / Action / Priorité.
- La section Priorisation reflète l'ordre réel de traitement.
- Les items renvoient à du code précis quand c'est possible.
