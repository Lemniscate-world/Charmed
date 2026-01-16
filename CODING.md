# CODING.md - Development Guidelines

## 🎯 Purpose

This document provides comprehensive development guidelines for Alarmify, covering architecture patterns, code quality standards, testing strategies, and PyQt5-specific best practices.

---

## 📋 Table of Contents

1. [SOLID Principles](#solid-principles)
2. [Clean Code Practices](#clean-code-practices)
3. [PyQt5 Patterns](#pyqt5-patterns)
4. [Testing Strategies](#testing-strategies)
5. [Offline Development Setup](#offline-development-setup)
6. [Architecture Guidelines](#architecture-guidelines)
7. [Error Handling](#error-handling)
8. [Logging Standards](#logging-standards)
9. [Performance Best Practices](#performance-best-practices)
10. [Security Guidelines](#security-guidelines)

---

## 🏗️ SOLID Principles

### Single Responsibility Principle (SRP)

Each class should have one reason to change.

**Good Example:**
```python
# alarm.py - ONLY handles alarm scheduling
class Alarm:
    def set_alarm(self, time_str, playlist_uri, spotify_api, volume):
        """Schedule alarm - single responsibility"""
        pass

# spotify_api.py - ONLY handles Spotify API interactions
class SpotifyAPI:
    def play_playlist_by_uri(self, uri):
        """Play playlist - single responsibility"""
        pass
```

**Bad Example:**
```python
# DON'T mix responsibilities
class AlarmWithUI:
    def set_alarm(self):
        pass
    
    def show_dialog(self):  # ❌ UI logic in alarm class
        pass
    
    def save_to_database(self):  # ❌ Data persistence in alarm class
        pass
```

**Application in Alarmify:**
- `alarm.py`: Alarm scheduling logic only
- `gui.py`: UI components only
- `spotify_api/spotify_api.py`: API interactions only
- `logging_config.py`: Logging setup only

### Open/Closed Principle (OCP)

Open for extension, closed for modification.

**Good Example:**
```python
# Base API with extensibility
class SpotifyAPI:
    def authenticate(self):
        """Base authentication"""
        pass

# Extend without modifying
class MockSpotifyAPI(SpotifyAPI):
    """Test mode - extends base without modifying"""
    def authenticate(self):
        return True  # Mock authentication
```

**Application in Alarmify:**
- Use inheritance for test modes: `MockSpotifyAPI` extends `SpotifyAPI`
- Extend GUI components: Custom widgets inherit from Qt base classes
- Plugin architecture: Design for future extensions

### Liskov Substitution Principle (LSP)

Derived classes must be substitutable for base classes.

**Good Example:**
```python
# Both implementations can be used interchangeably
spotify_api = SpotifyAPI()  # Production
# OR
spotify_api = MockSpotifyAPI()  # Testing

# Both support same interface
playlists = spotify_api.get_playlists_detailed()
```

**Application in Alarmify:**
- `ThreadSafeSpotifyAPI` wraps `SpotifyAPI` transparently
- Mock implementations match real API interface
- Widget inheritance maintains Qt contracts

### Interface Segregation Principle (ISP)

Clients shouldn't depend on interfaces they don't use.

**Good Example:**
```python
# Split into focused interfaces
class PlaybackControl:
    def play(self): pass
    def pause(self): pass

class VolumeControl:
    def set_volume(self, level): pass
    def get_volume(self): pass

# Clients use only what they need
class Alarm:
    def __init__(self, playback: PlaybackControl):
        self.playback = playback  # Only needs playback
```

**Application in Alarmify:**
- Keep API methods focused and minimal
- Don't force dialogs to implement unnecessary methods
- Separate concerns in widget interfaces

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions.

**Good Example:**
```python
# Depend on abstract API, not concrete implementation
class Alarm:
    def __init__(self, api):  # Abstract: any API implementation
        self.api = api
    
    def play_playlist(self, uri):
        self.api.play_playlist_by_uri(uri)  # Works with any API

# Inject dependencies
alarm = Alarm(spotify_api)  # Production
alarm = Alarm(mock_api)     # Testing
```

**Application in Alarmify:**
- Pass `spotify_api` instance to `Alarm` (dependency injection)
- Pass `gui_app` reference for notifications (loose coupling)
- Use abstract logging interface (`get_logger`)

---

## ✨ Clean Code Practices

### Naming Conventions

**Follow PEP 8:**
```python
# Classes: PascalCase
class AlarmManagerDialog:
    pass

# Functions/methods: snake_case
def set_alarm(time_str, playlist_uri):
    pass

# Constants: UPPER_CASE
DEFAULT_VOLUME = 80
SPOTIFY_GREEN = '#1DB954'

# Private members: _leading_underscore
class Alarm:
    def __init__(self):
        self._alarms_lock = threading.Lock()
        self._is_running = False
```

**Use descriptive names:**
```python
# ✅ Good: Clear and descriptive
def validate_time_format(time_str):
    return re.match(r'^\d{2}:\d{2}$', time_str)

# ❌ Bad: Cryptic abbreviations
def vld_tm(ts):
    return re.match(r'^\d{2}:\d{2}$', ts)
```

### Function Design

**Keep functions small and focused:**
```python
# ✅ Good: Single responsibility, clear purpose
def load_playlists(self):
    """Load user playlists from Spotify API."""
    playlists = self.spotify_api.get_playlists_detailed()
    self.display_playlists(playlists)
    return playlists

def display_playlists(self, playlists):
    """Display playlists in UI list widget."""
    for playlist in playlists:
        self.add_playlist_item(playlist)

# ❌ Bad: Too many responsibilities
def load_and_display_and_save_playlists(self):
    playlists = self.spotify_api.get_playlists_detailed()
    for p in playlists:
        item = QListWidgetItem()
        # ... 50 lines of UI setup
        # ... database save logic
        # ... cache logic
```

**Limit parameters (ideally ≤ 3):**
```python
# ✅ Good: Grouped related parameters
def set_alarm(self, config: AlarmConfig):
    pass

# ❌ Bad: Too many parameters
def set_alarm(self, time, playlist_name, playlist_uri, 
              volume, device_id, fade_in, snooze_enabled):
    pass
```

### Code Comments

**Alarmify style: Module/class docstrings + inline comments for complex logic:**

```python
"""
alarm.py - Alarm scheduling module for Alarmify

This module provides the Alarm class for scheduling playlist alarms.
Uses the 'schedule' library for daily recurring tasks.
"""

import schedule  # Job scheduling library
import threading  # Background thread execution

class Alarm:
    """
    Alarm manager for scheduling Spotify playlist playback.
    
    Maintains a list of scheduled alarms and runs a background
    scheduler thread to trigger them at the specified times.
    """
    
    def set_alarm(self, time_str, playlist_uri, spotify_api, volume=80):
        """
        Schedule a new alarm.
        
        Args:
            time_str: Time in 'HH:MM' format (24-hour).
            playlist_uri: Spotify URI of playlist to play.
            spotify_api: SpotifyAPI instance for playback.
            volume: Volume level 0-100 (default 80).
        """
        # Validate time format before scheduling
        if not self._validate_time_format(time_str):
            raise ValueError(f'Invalid time format: {time_str}')
        
        # Schedule daily recurring job
        job = schedule.every().day.at(time_str).do(
            self.play_playlist, playlist_uri, spotify_api, volume
        )
```

**When NOT to comment:**
```python
# ❌ Bad: Obvious comments
i = i + 1  # Increment i
return True  # Return True

# ✅ Good: Self-documenting code
alarm_count += 1
return is_valid_time_format
```

### DRY (Don't Repeat Yourself)

**Extract repeated logic:**
```python
# ✅ Good: Reusable function
def show_error_message(title, message):
    """Show standardized error dialog."""
    QMessageBox.critical(None, title, message)
    logger.error(f"{title}: {message}")

# Use it everywhere
show_error_message('API Error', 'Failed to load playlists')
show_error_message('Network Error', 'Connection timeout')

# ❌ Bad: Repeated code
QMessageBox.critical(None, 'API Error', 'Failed to load playlists')
logger.error('API Error: Failed to load playlists')
# ... same code 10 more times
```

### Code Organization

**Group imports by category:**
```python
# Standard library
import os
import threading
from pathlib import Path

# Third-party packages
from PyQt5.QtWidgets import QWidget, QDialog
import spotipy
from dotenv import load_dotenv

# Local modules
from spotify_api.spotify_api import ThreadSafeSpotifyAPI
from alarm import Alarm
from logging_config import get_logger
```

**Logical class structure:**
```python
class AlarmApp(QWidget):
    # 1. Class constants
    DEFAULT_VOLUME = 80
    
    # 2. Initialization
    def __init__(self):
        pass
    
    # 3. Public methods (alphabetically or by feature)
    def load_playlists(self):
        pass
    
    def set_alarm(self):
        pass
    
    # 4. Private methods
    def _validate_credentials(self):
        pass
    
    def _setup_ui(self):
        pass
    
    # 5. Event handlers
    def on_alarm_button_clicked(self):
        pass
    
    # 6. Qt slots
    @pyqtSlot()
    def on_login_complete(self):
        pass
```

---

## 🖼️ PyQt5 Patterns

### Widget Lifecycle

**Proper widget initialization:**
```python
class CustomWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Initialize instance variables
        self.data = []
        self._is_loading = False
        
        # 2. Set up UI
        self._init_ui()
        
        # 3. Connect signals
        self._connect_signals()
        
        # 4. Load initial data (if needed)
        self._load_initial_data()
    
    def _init_ui(self):
        """Set up user interface components."""
        self.setWindowTitle('My Widget')
        layout = QVBoxLayout()
        self.setLayout(layout)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.button.clicked.connect(self.on_button_clicked)
    
    def closeEvent(self, event):
        """Clean up before closing."""
        self.cleanup()
        event.accept()
```

### Thread Safety

**Background tasks with QThread:**
```python
class ImageLoaderThread(QThread):
    """Background image loading to prevent UI freezing."""
    image_loaded = pyqtSignal(str, QPixmap)  # Signal to communicate with main thread
    
    def __init__(self, playlist_id, image_url):
        super().__init__()
        self.playlist_id = playlist_id
        self.image_url = image_url
    
    def run(self):
        """Execute in background thread."""
        try:
            # Long-running operation
            response = requests.get(self.image_url, timeout=5)
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            
            # Emit signal (thread-safe communication)
            self.image_loaded.emit(self.playlist_id, pixmap)
        except Exception as e:
            logger.error(f"Failed to load image: {e}")

# Usage in main thread
class MainWindow(QWidget):
    def load_image(self, playlist_id, url):
        thread = ImageLoaderThread(playlist_id, url)
        thread.image_loaded.connect(self.on_image_loaded)
        thread.start()
        # Store reference to prevent garbage collection
        self._image_threads.append(thread)
    
    def on_image_loaded(self, playlist_id, pixmap):
        """Slot called in main thread when image is ready."""
        self.update_playlist_image(playlist_id, pixmap)
```

**Thread-safe API calls:**
```python
# Use locks for shared resources
class ThreadSafeSpotifyAPI:
    def __init__(self):
        self._api = SpotifyAPI()
        self._lock = threading.RLock()  # Reentrant lock
    
    def get_playlists(self):
        """Thread-safe method."""
        with self._lock:
            return self._api.get_playlists_detailed()
```

### Signal-Slot Pattern

**Custom signals for communication:**
```python
class LoginDialog(QDialog):
    # Define custom signals
    login_successful = pyqtSignal(dict)  # Emits user data
    login_failed = pyqtSignal(str)       # Emits error message
    
    def attempt_login(self):
        """Attempt to authenticate user."""
        try:
            user_data = self.spotify_api.authenticate()
            self.login_successful.emit(user_data)  # Emit success
            self.accept()
        except Exception as e:
            self.login_failed.emit(str(e))  # Emit failure

# Connect in parent
class MainWindow(QWidget):
    def show_login_dialog(self):
        dialog = LoginDialog(self)
        dialog.login_successful.connect(self.on_login_success)
        dialog.login_failed.connect(self.on_login_failure)
        dialog.exec_()
    
    def on_login_success(self, user_data):
        """Handle successful login."""
        self.statusBar().showMessage(f"Logged in as {user_data['name']}")
    
    def on_login_failure(self, error):
        """Handle login failure."""
        QMessageBox.warning(self, 'Login Failed', error)
```

### Resource Management

**Proper cleanup:**
```python
class AlarmApp(QWidget):
    def __init__(self):
        super().__init__()
        self._threads = []
        self._timers = []
    
    def start_background_task(self):
        """Start a background thread."""
        thread = QThread()
        self._threads.append(thread)  # Keep reference
        thread.start()
    
    def closeEvent(self, event):
        """Clean up resources before closing."""
        # Stop all threads
        for thread in self._threads:
            thread.quit()
            thread.wait()
        
        # Stop all timers
        for timer in self._timers:
            timer.stop()
        
        # Close connections
        if hasattr(self, 'spotify_api'):
            self.spotify_api.cleanup()
        
        event.accept()
```

### UI Updates from Threads

**Always use signals or QTimer:**
```python
# ✅ Good: Use signal from thread
class WorkerThread(QThread):
    update_ui = pyqtSignal(str)
    
    def run(self):
        result = self.do_work()
        self.update_ui.emit(result)  # Thread-safe

# ✅ Good: Use QTimer.singleShot
def background_task_complete(result):
    QTimer.singleShot(0, lambda: update_ui(result))

# ❌ Bad: Direct UI update from thread
def run(self):
    result = self.do_work()
    self.label.setText(result)  # NOT thread-safe! Will crash
```

---

## 🧪 Testing Strategies

### Test Structure

**Organize tests by module:**
```
tests/
├── __init__.py
├── test_alarm.py           # Alarm scheduling tests
├── test_spotify_api.py     # API wrapper tests
├── test_gui.py             # GUI component tests
├── test_integration.py     # End-to-end tests
├── test_thread_safety.py   # Concurrency tests
└── test_build.py           # Build verification tests
```

### Unit Tests

**Test individual functions:**
```python
# test_alarm.py
import pytest
from alarm import Alarm

def test_validate_time_format():
    """Test time format validation."""
    alarm = Alarm()
    
    # Valid formats
    assert alarm._validate_time_format('09:30')
    assert alarm._validate_time_format('23:59')
    
    # Invalid formats
    assert not alarm._validate_time_format('9:30')    # Missing leading zero
    assert not alarm._validate_time_format('25:00')   # Invalid hour
    assert not alarm._validate_time_format('12:60')   # Invalid minute
    assert not alarm._validate_time_format('12:30:00') # Seconds included

def test_set_alarm_invalid_time():
    """Test that invalid time raises ValueError."""
    alarm = Alarm()
    
    with pytest.raises(ValueError):
        alarm.set_alarm('25:00', 'Test', 'uri', None)
```

### Mock Objects

**Use mocks for external dependencies:**
```python
# test_spotify_api.py
from unittest.mock import Mock, patch
import pytest

class MockSpotify:
    """Mock Spotify API for testing."""
    def current_user_playlists(self):
        return {
            'items': [
                {'name': 'Test Playlist', 'uri': 'spotify:test:123'}
            ]
        }

def test_get_playlists_with_mock():
    """Test playlist retrieval with mocked API."""
    api = SpotifyAPI()
    api.sp = MockSpotify()  # Inject mock
    
    playlists = api.get_playlists_detailed()
    
    assert len(playlists) == 1
    assert playlists[0]['name'] == 'Test Playlist'

@patch('spotipy.Spotify')
def test_authentication(mock_spotify):
    """Test authentication with patched Spotify."""
    mock_spotify.return_value.current_user.return_value = {'id': 'test_user'}
    
    api = SpotifyAPI()
    user = api.get_current_user()
    
    assert user['id'] == 'test_user'
```

### GUI Testing

**Test GUI components:**
```python
# test_gui.py
import pytest
from PyQt5.QtWidgets import QApplication
from gui import AlarmApp

@pytest.fixture
def app(qtbot):
    """Create application instance for testing."""
    test_app = AlarmApp()
    qtbot.addWidget(test_app)
    return test_app

def test_alarm_button_click(app, qtbot):
    """Test alarm button functionality."""
    # Set up test data
    app.playlist_list.addItem('Test Playlist')
    app.time_picker.setTime(QTime(9, 30))
    
    # Click button
    qtbot.mouseClick(app.set_alarm_btn, Qt.LeftButton)
    
    # Verify alarm was set
    assert len(app.alarm_manager.alarms) == 1
    assert app.alarm_manager.alarms[0]['time'] == '09:30'
```

### Integration Tests

**Test component interactions:**
```python
# test_integration.py
def test_alarm_triggers_playback():
    """Test complete alarm flow from scheduling to playback."""
    # Set up
    mock_api = MockSpotifyAPI()
    alarm = Alarm()
    
    # Schedule alarm for immediate trigger
    current_time = datetime.now().strftime('%H:%M')
    alarm.set_alarm(current_time, 'Test', 'spotify:playlist:test', mock_api)
    
    # Trigger scheduler
    schedule.run_pending()
    
    # Verify playback was called
    assert mock_api.play_called
    assert mock_api.last_played_uri == 'spotify:playlist:test'
```

### Test Coverage

**Aim for high coverage on critical paths:**
```bash
# Run tests with coverage
pytest --cov=. --cov-report=html tests/

# Target coverage:
# - Core logic (alarm, API): 90%+
# - GUI components: 70%+
# - Integration: 80%+
```

### Test-Driven Development (TDD)

**Write tests first for new features:**
```python
# 1. Write failing test
def test_fade_in_volume():
    """Test gradual volume increase."""
    alarm = Alarm()
    alarm.set_fade_in_alarm('09:00', 'uri', api, start_vol=20, end_vol=80)
    # ... assertions

# 2. Implement feature
class Alarm:
    def set_fade_in_alarm(self, time_str, uri, api, start_vol, end_vol):
        # Implementation

# 3. Test passes
pytest test_alarm.py::test_fade_in_volume
```

---

## 💻 Offline Development Setup

### Test Mode for Non-Premium Users

**Enable mock mode for development without Spotify Premium:**

```python
# Set environment variable
# Windows PowerShell:
$env:ALARMIFY_TEST_MODE="true"
python main.py

# Linux/Mac:
export ALARMIFY_TEST_MODE=true
python main.py
```

**Mock implementation:**
```python
# spotify_api/mock_spotify.py
class MockSpotifyAPI:
    """
    Mock Spotify API for testing without Premium account.
    
    Simulates all API responses with realistic test data.
    """
    
    def __init__(self):
        self.authenticated = True
        self.play_called = False
        self.last_played_uri = None
    
    def is_authenticated(self):
        """Always return authenticated in test mode."""
        return True
    
    def is_premium_user(self):
        """Simulate Premium for testing."""
        return True
    
    def get_playlists_detailed(self):
        """Return mock playlists."""
        return [
            {
                'name': 'Morning Energy',
                'id': 'mock_morning',
                'uri': 'spotify:playlist:mock_morning',
                'track_count': 45,
                'image_url': 'https://via.placeholder.com/300/1DB954/ffffff?text=Morning',
                'owner': 'Test User'
            },
            {
                'name': 'Chill Vibes',
                'id': 'mock_chill',
                'uri': 'spotify:playlist:mock_chill',
                'track_count': 120,
                'image_url': 'https://via.placeholder.com/300/FF6B6B/ffffff?text=Chill',
                'owner': 'Test User'
            }
        ]
    
    def get_devices(self):
        """Return mock devices."""
        return [
            {
                'id': 'mock_device_1',
                'name': 'Test Computer',
                'type': 'Computer',
                'is_active': True,
                'volume_percent': 50
            }
        ]
    
    def play_playlist_by_uri(self, uri, device_id=None):
        """Simulate playlist playback."""
        self.play_called = True
        self.last_played_uri = uri
        logger.info(f"[MOCK] Would play playlist: {uri}")
        return True
    
    def set_volume(self, volume):
        """Simulate volume control."""
        logger.info(f"[MOCK] Would set volume to: {volume}%")
        return True
```

**Use mock in application:**
```python
# main.py or gui.py
import os

TEST_MODE = os.getenv('ALARMIFY_TEST_MODE', 'False').lower() == 'true'

class AlarmApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Use mock API in test mode
        if TEST_MODE:
            from spotify_api.mock_spotify import MockSpotifyAPI
            self.spotify_api = MockSpotifyAPI()
            logger.info("Running in TEST MODE with mock API")
        else:
            self.spotify_api = ThreadSafeSpotifyAPI()
            logger.info("Running in PRODUCTION MODE with real API")
```

### Local Development Without Spotify Credentials

**Work on UI without API:**
```python
# gui.py - Design UI components independently
class PlaylistItemWidget(QWidget):
    """Playlist widget - can be developed without API."""
    
    def __init__(self, playlist_data):
        super().__init__()
        self.playlist_data = playlist_data
        self._init_ui()
    
    def _init_ui(self):
        """Set up UI - no API required."""
        layout = QHBoxLayout()
        # ... UI setup

# Test with dummy data
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    dummy_playlist = {
        'name': 'Test Playlist',
        'track_count': 50,
        'owner': 'Test User'
    }
    
    widget = PlaylistItemWidget(dummy_playlist)
    widget.show()
    sys.exit(app.exec_())
```

### Offline Testing Checklist

**What you can test offline:**
- ✅ UI layout and styling
- ✅ Alarm scheduling logic
- ✅ Time validation
- ✅ Settings dialogs
- ✅ Playlist list rendering (with mock data)
- ✅ Device selection UI
- ✅ Error handling flows
- ✅ Threading behavior
- ✅ Logging functionality

**What requires Spotify API:**
- ❌ Real authentication flow
- ❌ Actual playlist data from user account
- ❌ Real playback control
- ❌ Active device detection
- ❌ Premium status verification

---

## 🏛️ Architecture Guidelines

### Separation of Concerns

**Alarmify architecture:**
```
┌─────────────────────────────────────────┐
│              main.py                     │  Entry point
│         (Application bootstrap)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│              gui.py                      │  Presentation layer
│         (UI components, dialogs)         │
└──┬──────────┬──────────┬────────────────┘
   │          │          │
   │   ┌──────▼──────┐  │
   │   │   alarm.py  │  │  Business logic
   │   │  (Scheduler)│  │
   │   └─────────────┘  │
   │                    │
┌──▼─────────────────┐  │
│ spotify_api.py     │◄─┘  Data access layer
│   (API wrapper)    │
└────────────────────┘
```

**Layer responsibilities:**
- **Presentation (GUI)**: User interaction, display, input validation
- **Business Logic (Alarm)**: Scheduling, alarm management, core functionality
- **Data Access (API)**: External service communication, data fetching

### Module Independence

**Design for testability:**
```python
# ✅ Good: Modules can be tested independently
def test_alarm_without_gui():
    alarm = Alarm()  # No GUI dependency
    alarm.set_alarm('09:00', 'Test', 'uri', mock_api)
    assert len(alarm.alarms) == 1

def test_api_without_alarm():
    api = SpotifyAPI()  # No alarm dependency
    playlists = api.get_playlists_detailed()
    assert isinstance(playlists, list)

# ❌ Bad: Tight coupling
class AlarmWithGUI:
    def __init__(self):
        self.window = QMainWindow()  # Can't test without GUI
```

### Configuration Management

**Centralize configuration:**
```python
# config.py
from pathlib import Path

class Config:
    """Application configuration."""
    
    # Paths
    APP_DIR = Path.home() / '.alarmify'
    LOG_DIR = APP_DIR / 'logs'
    CACHE_DIR = APP_DIR / 'cache'
    
    # Defaults
    DEFAULT_VOLUME = 80
    DEFAULT_REDIRECT_URI = 'http://127.0.0.1:8888/callback'
    
    # API settings
    SPOTIFY_SCOPES = [
        'user-library-read',
        'user-read-playback-state',
        'user-modify-playback-state',
        'playlist-read-private'
    ]
    
    # UI settings
    SPOTIFY_GREEN = '#1DB954'
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories."""
        cls.APP_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)
        cls.CACHE_DIR.mkdir(exist_ok=True)
```

---

## 🚨 Error Handling

### Exception Hierarchy

**Use appropriate exception types:**
```python
# Define custom exceptions
class AlarmifyException(Exception):
    """Base exception for Alarmify."""
    pass

class SpotifyAuthenticationError(AlarmifyException):
    """Raised when Spotify authentication fails."""
    pass

class InvalidTimeFormatError(AlarmifyException):
    """Raised when time format is invalid."""
    pass

# Usage
def set_alarm(self, time_str):
    if not self._validate_time_format(time_str):
        raise InvalidTimeFormatError(
            f"Invalid time format: {time_str}. Expected HH:MM"
        )
```

### Error Recovery

**Implement retry logic for transient failures:**
```python
def play_playlist_with_retry(self, uri, max_retries=3):
    """
    Play playlist with exponential backoff retry.
    
    Args:
        uri: Spotify playlist URI
        max_retries: Maximum retry attempts
    
    Returns:
        bool: True if successful, False otherwise
    """
    for attempt in range(max_retries):
        try:
            self.spotify_api.play_playlist_by_uri(uri)
            logger.info(f"Playback started successfully on attempt {attempt + 1}")
            return True
            
        except SpotifyException as e:
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                logger.warning(
                    f"Playback failed (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
            else:
                logger.error(f"Playback failed after {max_retries} attempts")
                return False
    
    return False
```

### User-Friendly Error Messages

**Provide actionable error messages:**
```python
def show_error_dialog(self, error_type, technical_details):
    """
    Show user-friendly error dialog.
    
    Args:
        error_type: Type of error (auth, network, api, etc.)
        technical_details: Technical error message for logs
    """
    # Map technical errors to user-friendly messages
    user_messages = {
        'auth': (
            "Authentication Failed",
            "Could not connect to Spotify. Please check your credentials "
            "in Settings and try again."
        ),
        'network': (
            "Network Error",
            "Could not connect to Spotify servers. Please check your "
            "internet connection and try again."
        ),
        'premium': (
            "Premium Required",
            "This feature requires Spotify Premium. Please upgrade your "
            "account at spotify.com/premium"
        ),
        'device': (
            "No Active Device",
            "Could not find an active Spotify device. Please open Spotify "
            "on any device and try again."
        )
    }
    
    title, message = user_messages.get(error_type, (
        "An Error Occurred",
        "Something went wrong. Please try again or contact support."
    ))
    
    # Log technical details
    logger.error(f"{error_type.upper()}_ERROR: {technical_details}")
    
    # Show user-friendly message
    QMessageBox.critical(self, title, message)
```

---

## 📝 Logging Standards

### Logging Levels

**Use appropriate log levels:**
```python
# DEBUG: Detailed diagnostic information
logger.debug(f"Playlist data: {playlist}")

# INFO: General informational messages
logger.info("User logged in successfully")
logger.info(f"Alarm scheduled for {time_str}")

# WARNING: Something unexpected but not critical
logger.warning("Playlist has no cover image, using default")
logger.warning(f"Retry attempt {retry_count}/{max_retries}")

# ERROR: Error that prevented an operation
logger.error(f"Failed to load playlists: {e}")
logger.error("Authentication failed - invalid credentials")

# CRITICAL: Severe error that may cause shutdown
logger.critical("Cannot initialize Spotify API - shutting down")
```

### Structured Logging

**Include context in log messages:**
```python
# ✅ Good: Includes context
logger.info(
    f"Alarm triggered - Time: {alarm['time']}, "
    f"Playlist: {alarm['playlist']}, Volume: {alarm['volume']}%"
)

# ❌ Bad: Missing context
logger.info("Alarm triggered")
```

### Sensitive Data

**Never log credentials or tokens:**
```python
# ✅ Good: Mask sensitive data
logger.info(f"Client ID: {client_id[:8]}...")
logger.info("Access token refreshed")

# ❌ Bad: Logs sensitive data
logger.info(f"Client Secret: {client_secret}")  # Security risk!
logger.info(f"Access Token: {token}")  # Security risk!
```

---

## ⚡ Performance Best Practices

### Lazy Loading

**Load resources only when needed:**
```python
class AlarmApp(QWidget):
    def __init__(self):
        super().__init__()
        self._playlists = None  # Not loaded yet
    
    @property
    def playlists(self):
        """Lazy load playlists on first access."""
        if self._playlists is None:
            self._playlists = self.spotify_api.get_playlists_detailed()
        return self._playlists
```

### Caching

**Cache expensive operations:**
```python
from functools import lru_cache

class SpotifyAPI:
    @lru_cache(maxsize=100)
    def get_playlist_details(self, playlist_id):
        """Cache playlist details to avoid repeated API calls."""
        return self.sp.playlist(playlist_id)
    
    def clear_cache(self):
        """Clear cache when needed (e.g., after playlist update)."""
        self.get_playlist_details.cache_clear()
```

### Background Processing

**Offload heavy operations to threads:**
```python
# ✅ Good: Load images in background
for playlist in playlists:
    if playlist['image_url']:
        thread = ImageLoaderThread(playlist['id'], playlist['image_url'])
        thread.image_loaded.connect(self.on_image_loaded)
        thread.start()
        self._image_threads.append(thread)

# ❌ Bad: Block UI while loading images
for playlist in playlists:
    if playlist['image_url']:
        response = requests.get(playlist['image_url'])  # Blocks UI!
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
```

### Memory Management

**Clean up resources:**
```python
class AlarmApp(QWidget):
    def load_playlists(self):
        """Load playlists and clean up old threads."""
        # Clean up completed threads
        self._image_threads = [t for t in self._image_threads if t.isRunning()]
        
        # Load new playlists
        playlists = self.spotify_api.get_playlists_detailed()
        
        # Limit cache size
        if len(self._playlist_cache) > 1000:
            self._playlist_cache.clear()
```

---

## 🔒 Security Guidelines

### Credential Storage

**Never commit credentials to repository:**
```python
# ✅ Good: Use .env file (gitignored)
# .env
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret

# Load in application
load_dotenv()
client_id = os.getenv('SPOTIPY_CLIENT_ID')

# ❌ Bad: Hardcoded credentials
CLIENT_ID = 'abc123...'  # Never do this!
```

### Token Security

**Handle tokens securely:**
```python
# ✅ Good: Clear tokens on logout
def logout(self):
    """Securely log out user."""
    # Clear in-memory tokens
    self.spotify_api.sp = None
    
    # Remove cached tokens
    cache_file = Path('.cache')
    if cache_file.exists():
        cache_file.unlink()
    
    logger.info("User logged out, tokens cleared")

# ❌ Bad: Leave tokens in memory
def logout(self):
    pass  # Tokens still accessible
```

### Input Validation

**Always validate user input:**
```python
def set_alarm(self, time_str, volume):
    """Set alarm with validated input."""
    # Validate time format
    if not re.match(r'^\d{2}:\d{2}$', time_str):
        raise ValueError("Invalid time format")
    
    # Validate time range
    hour, minute = map(int, time_str.split(':'))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("Time out of range")
    
    # Validate volume range
    if not (0 <= volume <= 100):
        raise ValueError("Volume must be 0-100")
    
    # Safe to proceed
    self._schedule_alarm(time_str, volume)
```

---

## 🎯 Summary

### Key Takeaways

1. **SOLID Principles**: Single responsibility, open for extension, dependency injection
2. **Clean Code**: Descriptive names, small functions, DRY principle
3. **PyQt5 Patterns**: Proper threading, signal-slot communication, resource cleanup
4. **Testing**: Unit tests, mocks, integration tests, high coverage
5. **Offline Development**: Test mode, mock API, dummy data
6. **Architecture**: Separation of concerns, module independence
7. **Error Handling**: Retry logic, user-friendly messages, proper logging
8. **Performance**: Lazy loading, caching, background processing
9. **Security**: No hardcoded credentials, token management, input validation

### Before Writing Code

1. ✅ Read existing code to understand patterns
2. ✅ Check for existing utilities/helpers
3. ✅ Plan architecture (which layer/module?)
4. ✅ Consider testability
5. ✅ Think about error cases
6. ✅ Review SOLID principles

### Code Review Checklist

- [ ] Follows SOLID principles
- [ ] Uses descriptive names
- [ ] Functions are small and focused
- [ ] Proper error handling
- [ ] Thread-safe if multi-threaded
- [ ] Includes docstrings
- [ ] Has unit tests
- [ ] No security issues
- [ ] No performance bottlenecks
- [ ] Follows existing patterns

---

**Last Updated:** December 23, 2024  
**Version:** 1.0  
**Maintainer:** Development Team
