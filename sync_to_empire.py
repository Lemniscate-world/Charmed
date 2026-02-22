#!/usr/bin/env python3
"""
Sync to EMPIRE_DOCS - Script pour synchroniser les sessions vers le dossier central EMPIRE_DOCS

Usage:
    python sync_to_empire.py --project "NomProjet"
    python sync_to_empire.py --project "NomProjet" --init

Ce script copie les fichiers de session du projet courant vers:
    C:/Users/Utilisateur/Documents/EMPIRE_DOCS/{projet}/
"""

import os
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path

# Chemin vers EMPIRE_DOCS (dans Documents Windows)
EMPIRE_DOCS_PATH = Path.home() / "Documents" / "EMPIRE_DOCS"

def get_project_name():
    """Detecte le nom du projet depuis le dossier courant"""
    return Path.cwd().name

def ensure_project_folder(project_name: str) -> Path:
    """Cree le dossier du projet dans EMPIRE_DOCS si necessaire"""
    project_folder = EMPIRE_DOCS_PATH / project_name.lower().replace(" ", "-")
    project_folder.mkdir(parents=True, exist_ok=True)
    return project_folder

def copy_session_files(project_name: str, source_dir: Path = None):
    """Copie les fichiers de session vers EMPIRE_DOCS"""
    if source_dir is None:
        source_dir = Path.cwd()
    
    project_folder = ensure_project_folder(project_name)
    
    files_to_copy = []
    
    # SESSION_SUMMARY.md
    session_md = source_dir / "SESSION_SUMMARY.md"
    if session_md.exists():
        shutil.copy2(session_md, project_folder / "SESSION_SUMMARY.md")
        files_to_copy.append("SESSION_SUMMARY.md")
    
    # Fichiers Word de session: {PROJECT}_Session_{YYYYMMDD}.docx
    today = datetime.now().strftime("%Y%m%d")
    project_upper = project_name.upper().replace(" ", "_").replace("-", "_")
    session_docx = source_dir / f"{project_upper}_Session_{today}.docx"
    
    if session_docx.exists():
        shutil.copy2(session_docx, project_folder / session_docx.name)
        files_to_copy.append(session_docx.name)
    
    # Chercher tous les fichiers *_Session_*.docx
    for docx_file in source_dir.glob("*_Session_*.docx"):
        if docx_file.name not in [f.name for f in [Path(f) for f in files_to_copy if f.endswith('.docx')]]:
            shutil.copy2(docx_file, project_folder / docx_file.name)
            files_to_copy.append(docx_file.name)
    
    return files_to_copy

def create_project_readme(project_name: str):
    """Cree un README.md pour le projet dans EMPIRE_DOCS"""
    project_folder = ensure_project_folder(project_name)
    readme_path = project_folder / "README.md"
    
    if readme_path.exists():
        return False
    
    content = f"""# {project_name}

Documentation du projet **{project_name}**.

## Fichiers

- `SESSION_SUMMARY.md` - Resume de session en Markdown
- `{project_name.upper().replace(' ', '_')}_Session_YYYYMMDD.docx` - Resumes de session Word

## Synchronisation

Ce dossier est automatiquement synchronise avec:
- Google Drive
- GitHub (empire-docs)
"""
    readme_path.write_text(content, encoding="utf-8")
    return True

def main():
    parser = argparse.ArgumentParser(description="Synchroniser les sessions vers EMPIRE_DOCS")
    parser.add_argument("--project", "-p", type=str, help="Nom du projet (defaut: dossier courant)")
    parser.add_argument("--init", action="store_true", help="Initialiser le dossier projet et creer README")
    parser.add_argument("--status", "-s", action="store_true", help="Afficher le statut de EMPIRE_DOCS")
    
    args = parser.parse_args()
    
    project_name = args.project or get_project_name()
    
    if args.status:
        print(f"EMPIRE_DOCS path: {EMPIRE_DOCS_PATH}")
        print(f"Project: {project_name}")
        print(f"Project folder: {EMPIRE_DOCS_PATH / project_name.lower().replace(' ', '-')}")
        if EMPIRE_DOCS_PATH.exists():
            print("EMPIRE_DOCS exists: YES")
            print("\nProjects:")
            for p in EMPIRE_DOCS_PATH.iterdir():
                if p.is_dir():
                    print(f"  - {p.name}")
        else:
            print("EMPIRE_DOCS exists: NO")
        return
    
    print(f"Sync project: {project_name}")
    print(f"Target: {EMPIRE_DOCS_PATH / project_name.lower().replace(' ', '-')}")
    
    if args.init:
        print("Initializing project folder...")
        create_project_readme(project_name)
    
    files = copy_session_files(project_name)
    
    if files:
        print(f"Copied {len(files)} file(s):")
        for f in files:
            print(f"  - {f}")
    else:
        print("No session files found to copy.")
    
    print("Done!")

if __name__ == "__main__":
    main()