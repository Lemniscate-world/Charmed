# AGENTS.md

## Setup Commands
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Commands
- **Run dev**: `python main.py`
- **Run tests**: `python -m pytest tests/ -v`
- **Build executable**: `python build_installer.py --skip-inno`
- **Build installer**: `python build_installer.py` (requires Inno Setup)
- **Build**: No build step required for development
- **Lint**: No linter configured
- **Version management**: `python version_manager.py --get|--set|--bump`

## Tech Stack
- **Language**: Python 3.10+
- **GUI**: PyQt5 (main window in `gui.py`, entry point in `main.py`)
- **API**: Spotipy for Spotify Web API (`spotify_api/spotify_api.py`)
- **Scheduling**: `schedule` library with daemon threads (`alarm.py`)
- **Environment**: python-dotenv for credentials (`.env` file gitignored)
- **Build**: PyInstaller for executable, Inno Setup for installer
- **CI/CD**: GitHub Actions (`.github/workflows/build.yml`)

## Architecture
- `main.py`: Entry point, launches PyQt5 app
- `gui.py`: All UI components (main window, dialogs, playlist widgets)
- `alarm.py`: Alarm scheduling and management with background thread
- `spotify_api/spotify_api.py`: Spotify API wrapper
- `tests/`: Pytest tests for alarm and API modules
- Virtual env: `.venv/` (per gitignore convention)

## Build System
- `alarmify.spec`: PyInstaller configuration (defines how executable is built)
- `installer.iss`: Inno Setup script (creates Windows installer with shortcuts, auto-start)
- `build_installer.py`: Orchestrates build process (PyInstaller → smoke tests → Inno Setup)
- `version_manager.py`: Manages version numbers across files
- `.github/workflows/build.yml`: CI/CD pipeline for automated builds and releases
- Build outputs: `dist/Alarmify.exe` (executable), `Output/AlarmifySetup-*.exe` (installer)

### Build Features
- Single-file executable with all dependencies bundled
- Windows installer with Start Menu shortcuts and optional auto-start
- Automated smoke tests for build verification
- Code signing placeholders (configure when certificate available)
- GitHub Actions for automated builds on push/tag
- Automated GitHub releases with version tags

### Build Requirements
- PyInstaller: `pip install pyinstaller` (for executable)
- Inno Setup 6: Install from https://jrsoftware.org/isdl.php (for installer)
- Code signing (optional): Windows SDK with SignTool

## Code Style
- Docstrings: Module-level and class-level docstrings with detailed inline comments
- Imports: Grouped by category (stdlib, third-party, local) with inline comments
- No strict linter configured; follow existing patterns in codebase
