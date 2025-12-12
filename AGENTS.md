1→# AGENTS.md
2→
3→## Setup Commands
4→```powershell
5→python -m venv .venv
6→.venv\Scripts\Activate.ps1
7→pip install -r requirements.txt
8→```
9→
10→## Commands
11→- **Run dev**: `python main.py`
12→- **Run tests**: `python -m pytest tests/ -v`
13→- **Build**: No build step (PyInstaller config exists but not automated)
14→- **Lint**: No linter configured
15→
16→## Tech Stack
17→- **Language**: Python 3.10+
18→- **GUI**: PyQt5 (main window in `gui.py`, entry point in `main.py`)
19→- **API**: Spotipy for Spotify Web API (`spotify_api/spotify_api.py`)
20→- **Scheduling**: `schedule` library with daemon threads (`alarm.py`)
21→- **Environment**: python-dotenv for credentials (`.env` file gitignored)
22→
23→## Architecture
24→- `main.py`: Entry point, launches PyQt5 app
25→- `gui.py`: All UI components (main window, dialogs, playlist widgets)
26→- `alarm.py`: Alarm scheduling and management with background thread
27→- `spotify_api/spotify_api.py`: Spotify API wrapper
28→- `tests/`: Pytest tests for alarm and API modules
29→- Virtual env: `.venv/` (per gitignore convention)
30→
31→## Code Style
32→- Docstrings: Module-level and class-level docstrings with detailed inline comments
33→- Imports: Grouped by category (stdlib, third-party, local) with inline comments
34→- No strict linter configured; follow existing patterns in codebase
35→