#!/usr/bin/env python3
"""
sync_summary.py - Convertit SESSION_SUMMARY.md en .docx et synchronise

Ce script automatise la conversion du résumé de session en document Word
pour faciliter la copie vers WhatsApp et autres plateformes.

Usage:
    python sync_summary.py [--output OUTPUT_DIR]

Dépendances:
    pip install python-docx
"""

import argparse
import re
from pathlib import Path
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE


def parse_session_summary(content: str) -> dict:
    """Parse le contenu du SESSION_SUMMARY.md en structure dict"""
    sessions = []
    
    # Split par date (format: # Session Summary — YYYY-MM-DD)
    session_pattern = r'# Session Summary — (\d{4}-\d{2}-\d{2})'
    parts = re.split(session_pattern, content)
    
    # parts[0] est le header, puis alterne date/contenu
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            date = parts[i]
            body = parts[i + 1].strip()
            
            session = {
                'date': date,
                'editor': extract_field(body, r'\*\*Editor\*\*:\s*(.+)'),
                'fr': extract_section(body, '🇫🇷 Français'),
                'en': extract_section(body, '🇬🇧 English'),
                'tests': extract_field(body, r'\*\*Tests\*\*:\s*(.+)'),
                'blockers': extract_field(body, r'\*\*Blockers\*\*:\s*(.+)'),
            }
            sessions.append(session)
    
    return {'sessions': sessions}


def extract_field(text: str, pattern: str) -> str:
    """Extrait un champ spécifique du texte"""
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ''


def extract_section(text: str, header: str) -> dict:
    """Extrait une section (FR ou EN) du texte"""
    # Trouver le début de la section
    start_pattern = rf'## {header}\s*\n'
    start_match = re.search(start_pattern, text)
    
    if not start_match:
        return {}
    
    start_pos = start_match.end()
    
    # Trouver la fin (prochain ## ou fin de texte)
    end_match = re.search(r'\n## ', text[start_pos:])
    end_pos = start_pos + end_match.start() if end_match else len(text)
    
    section_text = text[start_pos:end_pos].strip()
    
    return {
        'what_done': extract_field(section_text, r'\*\*(?:Ce qui a été fait|What was done)\*\*\s*[:：]?\s*(.+?)(?=\n\*\*|\n\n|\Z)'),
        'files_changed': extract_field(section_text, r'\*\*(?:Fichiers modifiés|Files changed)\*\*\s*[:：]?\s*(.+?)(?=\n\*\*|\n\n|\Z)'),
        'next_steps': extract_field(section_text, r'\*\*(?:Étapes suivantes|Next steps)\*\*\s*[:：]?\s*(.+?)(?=\n\*\*|\n\n|\Z)'),
    }


def create_document(parsed_data: dict, output_path: Path):
    """Crée un document Word à partir des données parsées"""
    doc = Document()
    
    # Titre principal
    title = doc.add_heading('Charmed - Session Summaries', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Date de génération
    gen_date = doc.add_paragraph(f'Généré le: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    gen_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    for session in parsed_data['sessions']:
        # Séparateur
        doc.add_paragraph('─' * 50)
        
        # En-tête session
        doc.add_heading(f'Session — {session["date"]}', level=1)
        
        if session['editor']:
            p = doc.add_paragraph()
            p.add_run('Editor: ').bold = True
            p.add_run(session['editor'])
        
        # Section Française
        if session['fr']:
            doc.add_heading('🇫🇷 Français', level=2)
            add_session_content(doc, session['fr'])
        
        # Section Anglaise
        if session['en']:
            doc.add_heading('🇬🇧 English', level=2)
            add_session_content(doc, session['en'])
        
        # Tests et Blockers
        if session['tests']:
            p = doc.add_paragraph()
            p.add_run('Tests: ').bold = True
            p.add_run(session['tests'])
        
        if session['blockers']:
            p = doc.add_paragraph()
            p.add_run('Blockers: ').bold = True
            p.add_run(session['blockers'])
    
    # Sauvegarder
    doc.save(output_path)
    print(f"✓ Document créé: {output_path}")


def add_session_content(doc: Document, section: dict):
    """Ajoute le contenu d'une section au document"""
    if section.get('what_done'):
        p = doc.add_paragraph()
        p.add_run('Ce qui a été fait: ').bold = True
        p.add_run(section['what_done'])
    
    if section.get('files_changed'):
        p = doc.add_paragraph()
        p.add_run('Fichiers modifiés: ').bold = True
        p.add_run(section['files_changed'])
    
    if section.get('next_steps'):
        p = doc.add_paragraph()
        p.add_run('Étapes suivantes: ').bold = True
        p.add_run(section['next_steps'])


def main():
    parser = argparse.ArgumentParser(description='Sync SESSION_SUMMARY.md to .docx')
    parser.add_argument('--output', '-o', default='.', help='Output directory')
    args = parser.parse_args()
    
    # Lire SESSION_SUMMARY.md
    summary_path = Path(__file__).parent / 'SESSION_SUMMARY.md'
    
    if not summary_path.exists():
        print(f"❌ Fichier non trouvé: {summary_path}")
        return 1
    
    print(f"📖 Lecture de {summary_path}")
    content = summary_path.read_text(encoding='utf-8')
    
    # Parser
    print("🔄 Parsing...")
    parsed_data = parse_session_summary(content)
    print(f"   → {len(parsed_data['sessions'])} session(s) trouvée(s)")
    
    # Créer le document
    output_dir = Path(args.output)
    output_path = output_dir / f'Charmed_Session_{datetime.now().strftime("%Y%m%d")}.docx'
    
    create_document(parsed_data, output_path)
    
    print("\n✅ Synchronisation terminée!")
    return 0


if __name__ == '__main__':
    exit(main())