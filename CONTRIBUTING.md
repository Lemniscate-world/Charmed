# Contributing to Charmed

Thank you for your interest in contributing to Charmed! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Project Architecture](#project-architecture)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Documentation](#documentation)
- [Build System](#build-system)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and constructive in all interactions
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what's best for the project and community
- Show empathy towards other contributors

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting comments, or personal attacks
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.10 or higher installed
- Git for version control
- A Spotify Premium account for testing
- Spotify Developer App credentials ([create one here](https://developer.spotify.com/dashboard))
- Basic understanding of Python, PyQt5, and async programming

### Finding Issues to Work On

1. Check the [Issues](../../issues) page for open tasks
2. Look for issues labeled `good first issue` for beginner-friendly tasks
3. Issues labeled `help wanted` need community assistance
4. Comment on an issue to indicate you're working on it

### Communication

- **Issues**: For bug reports and feature requests
- **Discussions**: For questions, ideas, and general conversation
- **Pull Requests**: For code contributions with clear descriptions

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/charmed.git
cd charmed

# Add upstream remote for staying updated
git remote add upstream https://github.com/ORIGINAL_OWNER/charmed.git
```

### 2. Create Virtual Environment

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Install development dependencies (if you add a requirements-dev.txt)
pip install pytest pytest-cov pytest-qt
```

### 4. Configure Spotify Credentials

Create a `.env` file in the project root:

```env
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

**Important**: Never commit the `.env` file. It's already in `.gitignore`.

### 5. Verify Setup

```bash
# Run the application
python main.py

# Run tests to ensure everything works
python -m pytest tests/ -v
```

### 6. Create Feature Branch

```bash
# Create a new branch for your feature/fix
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

## Coding Standards

### Python Style Guide

Charmed follows **PEP 8** conventions with some project-specific guidelines:

#### General Principles

- **Readability First**: Code should be easy to understand
- **Explicit Over Implicit**: Clear variable names and logic flow
- **DRY (Don't Repeat Yourself)**: Extract common logic into functions
- **Keep It Simple**: Avoid over-engineering solutions

#### Code Conventions

**Import Organization**:
```python
# Standard library imports (alphabetically sorted)
import os
import sys
import threading

# Third-party imports (alphabetically sorted)
from PyQt5.QtWidgets import QWidget, QLabel
import spotipy

# Local imports (alphabetically sorted)
from alarm import Alarm
from spotify_api.spotify_api import SpotifyAPI
```

**Docstrings**:
- Use triple-quoted docstrings for all modules, classes, and functions
- Follow Google or NumPy docstring format
- Include type hints in function signatures when beneficial

```python
def set_alarm(self, time_str, playlist_name, playlist_uri, spotify_api, volume=80):
    """
    Schedule a new alarm.

    Creates a daily recurring job that plays the specified playlist
    at the given time with the specified volume.

    Args:
        time_str: Time in 'HH:MM' format (24-hour).
        playlist_name: Name of the Spotify playlist (for display).
        playlist_uri: Spotify URI of the playlist to play.
        spotify_api: SpotifyAPI instance for playback control.
        volume: Volume level 0-100 (default 80).
    """
```

**Naming Conventions**:
- `snake_case` for functions, variables, and module names
- `PascalCase` for class names
- `UPPER_CASE` for constants
- Private methods/attributes: prefix with single underscore `_`

**Comments**:
- Use inline comments sparingly - code should be self-documenting
- Complex logic should have explanatory comments
- Don't state the obvious
- Update comments when code changes

```python
# Good: Explains WHY
# Use RLock to allow nested calls from same thread
self._api_lock = threading.RLock()

# Bad: States WHAT (already obvious from code)
# Create a lock
self._api_lock = threading.RLock()
```

**Line Length**:
- Maximum 100 characters per line (soft limit)
- Break long lines logically at function arguments or operators

**Whitespace**:
- 4 spaces for indentation (no tabs)
- Blank lines to separate logical sections
- No trailing whitespace

### PyQt5 Specific Guidelines

**Widget Naming**:
```python
# Use descriptive names with widget type suffix
self.playlist_list = QListWidget()
self.login_button = QPushButton()
self.time_input = QTimeEdit()
self.volume_slider = QSlider()
```

**Signal Connections**:
```python
# Connect signals explicitly, preferably in __init__ or dedicated method
self.login_button.clicked.connect(self.login_to_spotify)
self.volume_slider.valueChanged.connect(self._on_volume_changed)
```

**Layout Building**:
```python
# Build layouts in dedicated methods for clarity
def _build_ui(self):
    """Build the complete UI layout."""
    root_layout = QVBoxLayout(self.central_widget)
    # ... layout construction
```

**Thread Safety in Qt**:
- Never update GUI from background threads
- Use signals/slots for cross-thread communication
- Or use `QMetaObject.invokeMethod()` with `Qt.QueuedConnection`

### Thread Safety Guidelines

**Always Protect Shared State**:
```python
# Use locks for any data accessed by multiple threads
with self._alarms_lock:
    self.alarms.append(alarm_info)
```

**Use Decorators for Consistency**:
```python
@thread_safe_api_call
def get_playlists(self):
    # Lock automatically acquired by decorator
    pass
```

**Avoid Deadlocks**:
- Acquire locks in consistent order
- Keep critical sections short
- Don't call external code while holding locks
- Use timeout parameters when possible

**Test Concurrent Access**:
- Write tests that exercise multiple threads
- Test edge cases like rapid consecutive calls
- Verify no data corruption or crashes occur

### Error Handling

**Use Specific Exceptions**:
```python
# Good: Specific exception with helpful message
raise RuntimeError('Spotify client not authenticated')

# Bad: Generic exception
raise Exception('Error')
```

**Handle Expected Failures**:
```python
try:
    spotify_api.set_volume(volume)
except Exception:
    # Volume control may fail if no active device
    pass  # Continue with playback attempt
```

**Log Useful Information**:
```python
except Exception as e:
    print(f"Alarm playback failed: {e}")
    # In production, use proper logging
```

## Project Architecture

### Module Overview

```
charmed/
├── main.py              # Entry point: creates QApplication and AlarmApp
├── gui.py               # All UI components and PyQt5 widgets
│   ├── AlarmApp         # Main window with playlist browser and controls
│   ├── PlaylistItemWidget  # Custom widget for playlist display
│   ├── SettingsDialog   # Spotify credentials configuration
│   ├── AlarmManagerDialog  # View/manage scheduled alarms
│   └── ImageLoaderThread   # Background image loading
├── alarm.py             # Alarm scheduling and management
│   └── Alarm            # Schedule jobs, trigger playback
├── spotify_api/
│   └── spotify_api.py   # Thread-safe Spotify Web API wrapper
│       └── SpotifyAPI   # OAuth, playlist fetching, playback control
└── tests/               # Test suite
    ├── test_alarm.py
    ├── test_spotify_api.py
    └── test_thread_safety.py
```

### Key Design Patterns

**Separation of Concerns**:
- `gui.py`: UI logic only, delegates to API and alarm modules
- `alarm.py`: Scheduling logic, no UI dependencies
- `spotify_api.py`: API access, no business logic

**Thread Safety Pattern**:
- Locks protect shared state
- Decorators ensure consistent lock usage
- Background daemon threads for long-running tasks

**Qt Patterns**:
- Signals/slots for event handling
- Custom widgets for reusable UI components
- Background threads for network operations

### Data Flow

1. **Authentication Flow**:
   ```
   User clicks "Login" → SpotifyAPI.authenticate() → 
   Browser OAuth → Token cached → GUI updates
   ```

2. **Playlist Loading**:
   ```
   Authentication success → get_playlists_detailed() →
   Create PlaylistItemWidget → Start ImageLoaderThread →
   Image loads → Signal emitted → Widget updated
   ```

3. **Alarm Scheduling**:
   ```
   User sets alarm → Alarm.set_alarm() → schedule.every().day.at() →
   Background thread checks schedule → Time matches → play_playlist()
   ```

4. **Playback Trigger**:
   ```
   Scheduler triggers → SpotifyAPI.set_volume() →
   SpotifyAPI.play_playlist_by_uri() → Spotify device plays
   ```

### Thread Model

**Main Thread** (Qt GUI thread):
- All UI updates and user interactions
- Event loop processing
- Signal/slot execution

**Alarm Scheduler Thread** (daemon):
- Runs `schedule.run_pending()` every second
- Triggers alarm callbacks at scheduled times
- Calls SpotifyAPI methods (thread-safe)

**Image Loader Threads** (multiple, short-lived):
- Download playlist cover images
- Emit signal when complete
- GUI thread updates widget

## Testing Guidelines

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_alarm.py -v

# Run with coverage report
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test
python -m pytest tests/test_alarm.py::test_set_alarm -v
```

### Writing Tests

**Test Structure**:
```python
import pytest

def test_feature_description():
    """
    Test that feature works correctly.
    
    Arrange: Set up test data and mocks
    Act: Execute the functionality
    Assert: Verify expected results
    """
    # Arrange
    alarm = Alarm()
    
    # Act
    alarm.set_alarm("08:00", "Morning Playlist", "uri", mock_api, 80)
    
    # Assert
    alarms = alarm.get_alarms()
    assert len(alarms) == 1
    assert alarms[0]['time'] == "08:00"
```

**Use Fixtures for Common Setup**:
```python
@pytest.fixture
def spotify_api_mock():
    """Mock SpotifyAPI for testing."""
    api = Mock(spec=SpotifyAPI)
    api.is_authenticated.return_value = True
    return api
```

**Test Thread Safety**:
```python
def test_concurrent_access():
    """Test multiple threads accessing API simultaneously."""
    api = SpotifyAPI()
    threads = []
    
    for _ in range(10):
        t = threading.Thread(target=api.get_playlists)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # No crashes = success
```

### Test Coverage Goals

- Aim for >80% code coverage
- All critical paths must be tested
- Edge cases and error conditions
- Thread safety scenarios

## Pull Request Process

### Before Submitting

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**:
   ```bash
   python -m pytest tests/ -v
   ```

3. **Check code style**:
   - Follow PEP 8 conventions
   - Run linter if available
   - Remove debugging code

4. **Update documentation**:
   - Update docstrings for new functions
   - Update README.md if adding features
   - Add comments for complex logic

5. **Commit with clear messages**:
   ```bash
   git commit -m "Add playlist shuffle feature"
   
   # Or more detailed:
   git commit -m "Add playlist shuffle feature
   
   - Implement random track selection in Alarm.play_playlist()
   - Add shuffle toggle to AlarmManagerDialog
   - Update tests to cover shuffle behavior
   - Closes #123"
   ```

### Submitting the PR

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request on GitHub**:
   - Click "New Pull Request" on your fork
   - Select your feature branch
   - Fill out the PR template

3. **PR Description Should Include**:
   - **What**: Brief description of changes
   - **Why**: Motivation and context
   - **How**: Technical approach taken
   - **Testing**: How you tested the changes
   - **Screenshots**: For UI changes (use `docs/screenshots/` folder)
   - **Related Issues**: "Closes #123" or "Related to #456"

### Example PR Description

```markdown
## Add Fade-in Volume Feature

### What
Adds gradual volume fade-in when alarms trigger, making wake-up more gentle.

### Why
Abrupt full-volume alarms can be jarring. A fade-in provides a more pleasant wake-up experience.

### How
- Modified `Alarm.play_playlist()` to accept `fade_seconds` parameter
- Implemented volume ramping from 10% to target volume over specified duration
- Added fade duration slider to AlarmManagerDialog
- Used threading.Timer for volume increments

### Testing
- Manual testing with various fade durations (5s, 10s, 30s)
- Verified no conflicts with existing volume control
- Tested multiple alarms triggering with different fade settings
- All existing tests pass

### Screenshots
![Fade-in controls](docs/screenshots/fade-in-controls.png)

Closes #42
```

### Review Process

1. **Automated Checks**: CI will run tests automatically
2. **Code Review**: Maintainers will review your code
3. **Feedback**: Address review comments with new commits
4. **Approval**: Once approved, PR will be merged

### After Merge

1. **Delete your branch** (optional):
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. **Update your fork**:
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

## Issue Guidelines

### Reporting Bugs

**Before Submitting**:
- Check if issue already exists
- Try the latest version
- Verify it's not a configuration problem

**Bug Report Template**:
```markdown
**Description**
Clear description of what went wrong

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should have happened

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g., Windows 10]
- Python Version: [e.g., 3.10.5]
- Charmed Version: [e.g., commit hash]

**Screenshots/Logs**
Any relevant screenshots or console output

**Additional Context**
Any other information that might be helpful
```

### Feature Requests

**Feature Request Template**:
```markdown
**Is your feature request related to a problem?**
Clear description of the problem or use case

**Describe the solution you'd like**
What you want to happen

**Describe alternatives you've considered**
Other approaches you thought about

**Additional context**
Mockups, examples, or links to similar features
```

### Security Issues

**Do not** create public issues for security vulnerabilities.

Instead, email security issues privately to the maintainers.

## Documentation

### Updating Documentation

When adding features or changing behavior:

1. **Update README.md**:
   - Add to feature list if significant
   - Update usage instructions
   - Add troubleshooting entries if needed

2. **Update USER_GUIDE.md**:
   - Add step-by-step instructions
   - Include screenshots
   - Explain common pitfalls

3. **Update AGENTS.md**:
   - Technical architecture changes
   - New commands or build steps
   - Dependency updates

4. **Update Docstrings**:
   - Keep code documentation current
   - Add examples for complex functions
   - Document parameters and return values

### Documentation Style

- **Clear and Concise**: Get to the point quickly
- **Use Examples**: Show, don't just tell
- **Assume Beginner Friendly**: Explain technical terms
- **Keep Updated**: Documentation drift is worse than no docs
- **Screenshots**: Use annotated images for UI features

### Adding Screenshots

Place screenshots in `docs/screenshots/` with descriptive names:
```
docs/screenshots/
├── main-window.png
├── settings-dialog.png
├── alarm-manager.png
└── feature-xyz.png
```

Reference in markdown:
```markdown
![Feature Description](docs/screenshots/feature-xyz.png)
```

## Build System

### Architecture

The build system consists of:

1. **charmed.spec** - PyInstaller configuration
2. **installer.iss** - Inno Setup script
3. **build_installer.py** - Build orchestration
4. **version_manager.py** - Version management
5. **.github/workflows/build.yml** - CI/CD pipeline

### Building

#### Build Executable Only

```powershell
# Quick build (executable only)
python build_installer.py --skip-inno

# Output: dist/Charmed.exe
```

#### Build Full Installer

Requires [Inno Setup 6](https://jrsoftware.org/isdl.php):

```powershell
# Full build with installer
python build_installer.py

# Outputs:
# - dist/Charmed.exe
# - Output/CharmedSetup-1.0.0.exe
```

#### Build Options

```powershell
# Skip tests (faster)
python build_installer.py --skip-tests

# Skip Inno Setup (executable only)
python build_installer.py --skip-inno

# Both options
python build_installer.py --skip-tests --skip-inno
```

### Modifying Build

#### Add Data Files

Edit `charmed.spec`:
```python
datas=[
    ('spotify_style.qss', '.'),
    ('new_file.txt', '.'),  # Add here
],
```

#### Add Dependencies

Edit `charmed.spec`:
```python
hiddenimports=[
    'PyQt5.sip',
    'new_package',  # Add here
],
```

#### Change Installer Options

Edit `installer.iss`:
- App information: `[Setup]` section
- Files to install: `[Files]` section
- Shortcuts: `[Icons]` section
- Registry keys: `[Registry]` section

#### Modify Build Process

Edit `build_installer.py`:
- Add new build stages
- Add custom verification
- Integrate additional tools

### CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/build.yml`):

**Runs on:**
- Push to main/develop
- Pull requests
- Version tags (v*.*.*)

**Jobs:**
1. **build** - Build executable and installer
2. **smoke-test** - Verify build quality
3. **release** - Create GitHub release (tags only)

**Testing your changes:**
1. Push to your fork
2. Check Actions tab
3. Verify build succeeds

## Development Tips

### Debugging

**Console Logging**:
```python
# Temporary debugging (remove before commit)
print(f"Debug: playlist_uri = {playlist_uri}")

# Use proper logging for production
import logging
logging.debug(f"Triggering alarm at {time_str}")
```

**Qt Debugging**:
```python
# Check if widget is visible
print(f"Widget visible: {self.playlist_list.isVisible()}")

# Inspect layout
print(f"Layout count: {layout.count()}")
```

**Thread Debugging**:
```python
# Identify which thread is running
print(f"Thread: {threading.current_thread().name}")
```

### Common Pitfalls

**Qt GUI Updates from Background Threads**:
```python
# DON'T: Update GUI from background thread
def background_task():
    self.label.setText("Done")  # CRASH!

# DO: Use signals
class Worker(QThread):
    finished = pyqtSignal(str)
    
    def run(self):
        result = do_work()
        self.finished.emit(result)  # Safe!
```

**Forgetting to Hold Locks**:
```python
# DON'T: Access shared data without lock
self.alarms.append(alarm)  # Race condition!

# DO: Protect with lock
with self._alarms_lock:
    self.alarms.append(alarm)
```

**Resource Cleanup**:
```python
# Always clean up in closeEvent
def closeEvent(self, event):
    self._cleanup_resources()
    event.accept()
```

## Questions?

If you have questions about contributing:

1. Check existing documentation first
2. Search closed issues for similar questions
3. Ask in [Discussions](../../discussions)
4. Reach out to maintainers

Thank you for contributing to Charmed! 🎵⏰
