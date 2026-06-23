---
name: prod-web-component
description: Génère un widget de chat embarquable en Web Component vanilla (Shadow DOM, zéro dépendance runtime, build esbuild ~40KB). Configurable par attributs (tenant-id, api-url, primary-color, position, lang, token, stream), encapsulé du CSS hôte, prêt à poser sur n'importe quel site. À utiliser pour le frontend d'un agent conversationnel.
---

# prod-web-component

Frontend autonome et embarquable : un `<custom-element>` isolé par Shadow DOM, sans framework ni
dépendance runtime, buildé par esbuild. S'intègre par une seule balise script + élément, sans
polluer les styles de la page hôte.

## Quand l'utiliser

- Exposer un agent (ex. `prod-serverless-aws`) sur un site tiers via un widget léger.
- Besoin d'isolation CSS (Shadow DOM) et de personnalisation par attributs.

## Fichiers générés

| Asset | Destination |
|---|---|
| `web-component.js.tmpl` | `widget/__PKG__.js` |
| `package.json.tmpl` | `widget/package.json` |

## Patterns imposés

- **Shadow DOM** (`attachShadow({ mode: 'open' })`) : styles encapsulés, zéro fuite vers/depuis l'hôte.
- **Zéro dépendance runtime** : aucune lib chargée chez le client ; build esbuild minifié vers
  `dist/`.
- **Config par attributs** via `observedAttributes` (tenant, api-url, couleur, position, langue,
  token, stream) — réactif à `attributeChangedCallback`.
- **Confirmation explicite** côté UI pour les actions mutatives (`pendingConfirmation`).
- **i18n minimal** (au moins fr) et support RTL via `direction`.

## Étapes d'adaptation

1. Substituer `__PROJECT__`/`__PKG__` et le tag de l'élément (`<__PKG__-chat>`).
2. Brancher `apiUrl` sur l'endpoint de l'agent ; gérer le mode `stream` (SSE/fetch streaming).
3. Adapter la palette via `--primary` et les libellés i18n.
4. `npm install && npm run build` → `dist/__PKG__.min.js`.

## Checklist de validation

- `npm run build` produit un bundle minifié sans dépendance runtime.
- Le widget s'affiche correctement quelle que soit la CSS de la page hôte (Shadow DOM).
- Une action mutative demande confirmation avant envoi.
