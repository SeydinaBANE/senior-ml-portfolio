---
name: prod-governance
description: Ajoute la couche de gouvernance transverse — RBAC (rôles/permissions), masquage PII (emails, téléphones), garde d'idempotence pour les écritures, et journal d'audit append-only. À utiliser dès qu'un système expose des actions de lecture/écriture sensibles ou doit tracer qui a fait quoi.
---

# prod-governance

Enveloppe les actions métier (connecteurs, outils, endpoints) : autorise/refuse selon le rôle,
masque les données personnelles en sortie, garantit l'idempotence des écritures et journalise
chaque décision pour traçabilité.

## Quand l'utiliser

- Système multi-rôles (viewer/operator…) avec actions de lecture ET d'écriture.
- Sorties LLM pouvant contenir des PII à masquer.
- Écritures (création de ticket, commande…) devant être idempotentes.

## Fichiers générés

| Asset | Destination |
|---|---|
| `governance.py.tmpl` | `src/__PKG__/governance.py` |

Dépend de `prod-config`/`prod-observability` (`get_logger`, `METRICS`). Si `prod-observability`
n'est pas appliqué, retirer l'appel `METRICS.incr` dans `authorize`.

## Composants

- `Permission(StrEnum)` + `_ROLE_PERMISSIONS` : matrice rôle → permissions (à adapter au domaine).
- `Principal` (frozen) : appelant authentifié (`user_id`, `roles`).
- `RBACPolicy.authorize(principal, permission)` : lève `AccessDeniedError` si non autorisé.
- `mask_pii(text)` : remplace emails/téléphones par `[email]`/`[phone]`.
- `IdempotencyGuard.is_new(key)` : True une seule fois par clé.
- `AuditLog.record(...)` : journal append-only + log structuré.

## Étapes d'adaptation

1. Substituer `__PKG__`.
2. Redéfinir `Permission` et `_ROLE_PERMISSIONS` selon les actions réelles du projet.
3. Brancher `authorize` au point d'entrée des outils/connecteurs ; appeler `mask_pii` sur les
   textes renvoyés à l'utilisateur ; passer `IdempotencyGuard` aux écritures.
4. En production, persister `AuditLog` (DB/SIEM) plutôt que la liste en mémoire.

## Checklist de validation

- Test nominal : un `operator` peut écrire ; test d'erreur : un `viewer` reçoit `AccessDeniedError`.
- `mask_pii("a@b.com 06 12 34 56 78")` ne laisse fuir ni email ni numéro.
- Deux appels avec la même clé d'idempotence ne produisent qu'une écriture.
