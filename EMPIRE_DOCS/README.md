# EMPIRE DOCS

Dossier de documentation centralise pour synchronisation cloud.

## Structure

Les fichiers generes sont nommes selon le format :
- `{PROJECT}_Session_{YYYYMMDD}.docx` - Resume de session du jour

## Utilisation

### Generer un document Word
```bash
python ../sync_summary.py
```

### Generer et envoyer sur WhatsApp
```bash
python ../sync_summary.py --whatsapp
```

### Specifier un projet
```bash
python ../sync_summary.py --project "Mon Projet"
```

## Configuration WhatsApp

Voir `../.env.example` pour la configuration.

### Option 1: CallMeBot (Gratuit)
1. Ajouter +34 644 71 49 47 a vos contacts WhatsApp
2. Envoyer "I allow callmebot to send me messages"
3. Vous recevrez votre API key par message
4. Configurer `.env` avec votre numero et API key

### Option 2: Twilio (Payant)
1. Creer un compte Twilio
2. Activer WhatsApp Sandbox
3. Configurer les identifiants dans `.env`

## Synchronisation Cloud

Ce dossier est destine a etre synchronise avec :
- Google Drive
- Dropbox
- OneDrive
- Ou tout autre service cloud

Les liens partageables peuvent etre envoyes a l'equipe via WhatsApp.

## Automatisation

Pour automatiser la generation a chaque commit, ajouter un hook git :

```bash
# .git/hooks/post-commit
#!/bin/bash
python sync_summary.py