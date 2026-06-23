---
name: prod-threat-model
description: Génère ou met à jour FAILLE.md — le modèle de menaces du projet : vulnérabilités numérotées (Description / Mitigation actuelle / Fix), analyse des risques acceptés et procédure de signalement. À utiliser avant une mise en production ou une revue de sécurité pour documenter la surface d'attaque et les décisions.
---

# prod-threat-model

Produit un document de sécurité honnête et actionnable. Pour chaque faille identifiée : ce que
c'est, ce qui la limite déjà, et le correctif prévu. Couvre aussi les risques sciemment acceptés
et comment signaler une faille.

## Quand l'utiliser

- Avant mise en production ou audit (`/security-review`, `/cso`).
- Après tout changement élargissant la surface d'attaque (nouvel endpoint, intégration, upload).

## Fichier généré

| Asset | Destination |
|---|---|
| `FAILLE.md.tmpl` | `FAILLE.md` (racine du projet) |

## Méthode (à suivre par Claude)

1. Cartographier les entrées : endpoints, webhooks sortants (SSRF), uploads, paramètres
   utilisateur, dépendances, permissions IAM/cloud, en-têtes de réponse.
2. Pour chaque vecteur réel, créer une section numérotée : **Description**, **Mitigation actuelle**,
   **Fix** (concret, avec fichier/ligne quand possible).
3. Lister les **risques acceptés** avec justification explicite (pourquoi on ne corrige pas maintenant).
4. Renseigner la **procédure de signalement** (contact, délai de réponse).
5. Trier par gravité décroissante ; rester factuel, pas de faux positifs.

## Catégories à vérifier systématiquement

- SSRF (appels HTTP sortants pilotés par l'entrée), XSS/injection, validation/limites de taille
  des entrées, fallback d'auth silencieux, permissions cloud trop larges (`*`), en-têtes de
  sécurité manquants (COOP/COEP, CSP), fuite de secrets.

## Checklist de validation

- Chaque faille a les 3 sous-sections (Description / Mitigation / Fix).
- Les risques acceptés sont justifiés, pas seulement listés.
- Aucun secret réel dans le document.
