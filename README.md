# Suno Song Builder (Web App)

Application web autonome pour structurer des paroles et sections de chanson pour Suno, avec focus sur la compatibilite multi-voix, l'export propre et la rapidite de workflow.

## Fichier unique

Le projet est volontairement minimal:

- `index.html` : app complete (HTML + CSS + JavaScript)

Aucune dependance, aucun build, aucune installation.

## Fonctionnalites principales

- Gestion des chanteurs:
  - nom
  - type de voix (male/female)
  - notation phonetique pour la prononciation Suno
- Construction de chanson par sections:
  - Intro, Verse, Chorus, Bridge, Hook, Drop, Outro, etc.
  - assignation de voix par section (solo, all, instrumental, public, mixed)
  - tags d'ambiance + performance vocale
- Drag & drop des sections
- Templates (genres + multi-voix)
- Editeur de paroles par section
- Apercu Suno colore en temps reel
- Export `.txt` pour Suno
- Export `Pack Suno` (`*_suno_pack.txt`) avec style, lyrics strict/balanced, plan extend et check
- Export `Plan Extend` (`*_suno_extend_plan.md`) bloc par bloc pour generation iterative Suno
- Export `Styles Suno` (`*_suno_styles.txt`) avec 3 variantes prêtes a tester: safe, creative, aggressive
- Export HTML de partage (`*_share.html`) avec toutes les informations de la chanson
- Export Markdown Discord (`*_discord.md`) avec prompts, stats et diagnostic
- Sauvegarde / ouverture projet `.json`
- Import `.txt` existant
- Auto-save localStorage
- Undo / Redo

## Fonctions avancees (compatibilite Suno)

- Deux modes d'export:
  - `Equilibre` : conserve les tags creatifs
  - `Compatibilite stricte` : normalise les tags pour robustesse
- En-tetes instrumentaux explicites a l'export
- Onglet `Qualite`:
  - score de qualite (0-100)
  - liste des erreurs / avertissements
  - auto-fix sur incoherences courantes
- Onglet `Studio`:
  - workflow presets preconfigures (duo pop, rap battle, epic choir, ballade acoustique)
  - snapshots de versions (sauvegarde / chargement / suppression)
  - operations batch (assignation et tags d'ambiance par type de section)
  - nettoyage global des paroles
  - normalisation des sections instrumentales
  - statistiques vocales par chanteur (sections / lignes / mots)
- Diagnostic compatibilite manuel
- Diagnostic compatibilite Suno renforce:
  - style manquant
  - style trop long ou trop generique
  - lyrics trop longs
  - trop de sections pour une generation unique
  - section trop longue (>16 lignes)
  - absence de chorus
  - cohesion de rimes faible sur sections vocales
  - metrique syllabique trop irreguliere

- Outils de rimes (dans l'editeur de section):
  - templates de rimes (AABB, ABAB, ABBA, AAAA, etc.)
  - detecteur de rimes (score + groupes de finales + details ligne par ligne)
- Compteur de syllabes (dans l'editeur de section):
  - analyse locale heuristique FR (sans API)
  - syllabes moyennes par ligne
  - regularite metrique (ecart-type + barres visuelles par ligne)

- Personnalisation de lisibilite (onglet Studio):
  - ajustement largeur panneau gauche
  - ajustement largeur panneau droite
  - sauvegarde automatique des preferences de layout
- Estimation de duree de morceau
- Optimiseur de style prompt (`Wand Style`)
- Correctif responsive de l'onglet `Apercu Suno` (plus de debordement horizontal)

## Demarrage

1. Ouvrir `index.html` dans un navigateur.
2. Ajouter les chanteurs.
3. Appliquer un template (optionnel).
4. Ecrire/assigner les sections.
5. Verifier `Apercu Suno` et `Qualite`.
6. Utiliser `Studio` pour snapshots, batch edits et nettoyage.
7. Exporter en `.txt` pour Suno ou en `.html` pour partage Discord.

## Raccourcis clavier

- `Ctrl+S` : sauvegarder le projet JSON
- `Ctrl+O` : ouvrir un projet
- `Ctrl+E` : exporter pour Suno
- `Ctrl+Shift+S` : sauvegarder un snapshot Studio
- `Ctrl+Z` : annuler
- `Ctrl+Y` : retablir
- `Delete` : supprimer la section selectionnee

## Conseils d'utilisation Suno

- Pour du multi-voix stable, utilisez des noms de chanteurs clairs et constants.
- Pour la prononciation, remplissez le champ phonetique (ex: `Fenn-riss`).
- Avant export final, viser un score `Qualite >= 85`.
- En cas de comportements incoherents de Suno, utiliser l'export `Compatibilite stricte`.

## Publication

Ce depot est maintenu volontairement simple pour edition rapide:

- code principal: `index.html`
- documentation: `README.md`
