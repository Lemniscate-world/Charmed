---
description: Appliquer automatiquement la synchronisation EMPIRE_DOCS pour tous
  les projets. Assurer que chaque session de travail est sauvegardée dans le
  dossier central pour backup cloud et GitHub.
alwaysApply: true
---

TOUJOURS synchroniser les sessions de travail vers EMPIRE_DOCS central.

Pour chaque projet/repo:
1. Copier `sync_to_empire.py` depuis un projet existant ou créer le script
2. Après chaque session de travail significative, exécuter: `python sync_to_empire.py --project "NomProjet"`
3. Les fichiers suivants seront copiés vers `C:\Users\Utilisateur\Documents\EMPIRE_DOCS\{projet}\`:
   - SESSION_SUMMARY.md
   - {PROJET}_Session_{YYYYMMDD}.docx

Structure standardisée:
```
EMPIRE_DOCS/
├── README.md
├── empire_manager.py
└── {projet}/
    ├── README.md
    ├── SESSION_SUMMARY.md
    └── {PROJET}_Session_*.docx
```

Ce dossier est synchronisé avec Google Drive et a un repo GitHub dédié.

Les règles IA principales sont centralisées dans le repo: kuro-rules