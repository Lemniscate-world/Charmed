"#!/usr/bin/env python3
\"\"\"EMPIRE_DOCS Manager - Gestionnaire central pour tous les projets\"\"\"

import os
import sys
from pathlib import Path
from datetime import datetime

EMPIRE_DOCS_PATH = Path.home() / \"Documents\" / \"EMPIRE_DOCS\"

def list_projects():
    \"\"\"Liste tous les projets dans EMPIRE_DOCS\"\"\"
    if not EMPIRE_DOCS_PATH.exists():
        print(\"EMPIRE_DOCS folder does not exist!\")
        return
    
    print(\"EMPIRE_DOCS Projects:\")
    print(\"-\" * 40)
    
    for project in sorted(EMPIRE_DOCS_PATH.iterdir()):
        if project.is_dir():
            docx_count = len(list(project.glob(\"*_Session_*.docx\")))
            has_summary = (project / \"SESSION_SUMMARY.md\").exists()
            print(f\"  {project.name}\")
            print(f\"    - Sessions Word: {docx_count}\")
            print(f\"    - SESSION_SUMMARY.md: {'Yes' if has_summary else 'No'}\")

def init_project(project_name: str):
    \"\"\"Initialise un nouveau projet\"\"\"
    project_folder = EMPIRE_DOCS_PATH / project_name.lower().replace(\" \", \"-\")
    project_folder.mkdir(parents=True, exist_ok=True)
    
    readme = project_folder / \"README.md\"
    if not readme.exists():
        project_upper = project_name.upper().replace(\" \", \"_\")
        content = f\"\"\"# {project_name}

Documentation du projet **{project_name}**.

## Fichiers

- `SESSION_SUMMARY.md` - Resume de session
- `{project_upper}_Session_YYYYMMDD.docx` - Sessions Word
\"\"\"
        readme.write_text(content, encoding=\"utf-8\")
        print(f\"Created: {project_folder}\")
    else:
        print(f\"Project already exists: {project_folder}\")

def main():
    if len(sys.argv) < 2:
        print(\"Usage: python empire_manager.py [list|init]\")
        print(\"  list          - Liste tous les projets\")
        print(\"  init NAME     - Cree un nouveau projet\")
        return
    
    cmd = sys.argv[1]
    
    if cmd == \"list\":
        list_projects()
    elif cmd == \"init\":
        if len(sys.argv) < 3:
            print(\"Usage: python empire_manager.py init \\\"NomProjet\\\"\")
            return
        init_project(sys.argv[2])
    else:
        print(f\"Unknown command: {cmd}\")

if __name__ == \"__main__\":
    main()
"