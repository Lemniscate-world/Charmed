# Logging System Implementation

## Overview
This document describes the comprehensive logging system that has been implemented in Alarmify.

## Features Implemented

### 1. Centralized Logging Configuration (`logging_config.py`)
- **Structured Logging**: Timestamped log entries with log level, module name, and message
- **Dual Output**: 
  - Console output (stdout) for development/debugging
  - File output to `logs/` directory with rotation
- **Log Rotation**: Automatic rotation at 5MB per file, keeps 5 backup files
- **Timestamped Files**: Each application run creates a new log file named `alarmify_YYYYMMDD_HHMMSS.log`

### 2. Log Format
```
YYYY-MM-DD HH:MM:SS [LEVEL] module_name: message
```
Example:
```
2024-01-15 14:30:45 [INFO] alarm: Alarm triggered: playlist=Morning Vibes, volume=80%
2024-01-15 14:30:46 [ERROR] alarm: Alarm playback failed for playlist "Morning Vibes": No active device found
```

### 3. Logging Coverage

#### main.py
- Application startup
- Main window display
- Fatal errors in main application

#### alarm.py
- Alarm scheduling events
- Alarm triggers (when alarm goes off)
- Playback success/failure
- Volume control attempts
- Alarm removal/clearing
- Scheduler thread lifecycle

#### spotify_api/spotify_api.py
- Spotify API initialization
- OAuth authentication flow (start, completion, failures)
- Playlist fetching
- Playback commands
- Volume control
- API errors and exceptions

#### gui.py
- GUI initialization
- User actions (login, setting alarms, opening dialogs)
- Playlist loading
- Settings updates
- Image loading failures
- All user interactions

#### build_installer.py
- Build process steps
- Build success/failure

### 4. Log Levels Used

- **DEBUG**: Detailed information for troubleshooting (e.g., OAuth URLs, volume settings)
- **INFO**: General informational messages (e.g., alarm scheduled, login successful)
- **WARNING**: Non-critical issues (e.g., failed to load image, volume control failed)
- **ERROR**: Error events (e.g., authentication failure, playlist not found)
- **EXCEPTION**: Full stack traces for exceptions

### 5. GUI Log Viewer (`LogViewerDialog`)

A complete log viewer has been added to the GUI with the following features:

#### Features:
- **View Logs**: Read-only text view of log files with monospace font
- **Log File Selection**: Dropdown to switch between different log files
- **Refresh**: Reload current log file to see latest entries
- **Export**: Save current log file to a user-specified location
- **Open Log Folder**: Opens the logs directory in file explorer
- **Auto-scroll**: Automatically scrolls to bottom to show latest entries
- **Large File Support**: Displays last 10,000 lines for performance

#### Access:
- New "View Logs" button added to main window (right panel)
- Opens in a non-modal dialog (can stay open while using the app)

### 6. Structured Logging for Key Events

#### Alarm Triggers
```python
logger.info(f'Alarm triggered: playlist={playlist}, volume={volume}%')
# ... attempt playback ...
logger.info(f'Successfully started playback: {playlist}')
# OR
logger.error(f'Alarm playback failed for playlist "{playlist}": {e}', exc_info=True)
```

#### Scheduling Events
```python
logger.info(f'Scheduling alarm: time={time_str}, playlist={playlist}, volume={volume}%')
logger.info(f'Alarm scheduled successfully: {time_str}')
logger.info('Scheduler background thread initialized')
```

#### Authentication
```python
logger.info('Starting Spotify OAuth authentication')
logger.info('Opening browser for user authorization')
logger.info(f'Starting OAuth callback server on {host}:{port}')
logger.info('Spotify authentication completed successfully')
```

### 7. Files Modified

1. **logging_config.py** (NEW)
   - Core logging configuration
   - Helper functions for log file management

2. **main.py**
   - Initialize logging system
   - Log application lifecycle

3. **alarm.py**
   - Replaced print() with logger calls
   - Added structured logging for all alarm operations

4. **spotify_api/spotify_api.py**
   - Added logging for all API operations
   - Detailed OAuth flow logging

5. **gui.py**
   - Added LogViewerDialog class
   - Logging for all user interactions
   - "View Logs" button

6. **build_installer.py**
   - Replaced print() with logger calls

7. **.gitignore**
   - Added `logs/` directory to ignore list

### 8. Log File Management

#### Location
- All logs stored in `logs/` directory at project root
- Directory created automatically on first run

#### Naming Convention
- Format: `alarmify_YYYYMMDD_HHMMSS.log`
- Example: `alarmify_20240115_143045.log`

#### Rotation
- Current log file grows up to 5MB
- When limit reached, rotates to `.log.1`, `.log.2`, etc.
- Keeps up to 5 backup files
- Oldest backups deleted automatically

### 9. Benefits

1. **Debugging**: Full visibility into application behavior
2. **User Support**: Users can export logs to share when reporting issues
3. **Monitoring**: Track alarm execution and failures over time
4. **Audit Trail**: Complete record of user actions and system events
5. **Performance**: Rotating logs prevent disk space issues
6. **Development**: Console output for immediate feedback

### 10. Usage Examples

#### For Developers
```python
from logging_config import get_logger

logger = get_logger(__name__)

# Info logging
logger.info('User logged in successfully')

# Error with exception
try:
    risky_operation()
except Exception as e:
    logger.error(f'Operation failed: {e}', exc_info=True)

# Debug for detailed info
logger.debug(f'Processing {len(items)} items')
```

#### For Users
1. Click "View Logs" button in main window
2. Select log file from dropdown
3. Click "Refresh" to update view
4. Click "Export Logs..." to save a copy
5. Click "Open Log Folder" to access all logs

## Technical Details

### Thread Safety
- Python's logging module is thread-safe
- Safe to log from alarm scheduler thread and GUI thread

### Performance
- Logging is asynchronous and non-blocking
- Minimal performance impact on application

### Error Handling
- Logging system never throws exceptions
- If log file cannot be written, falls back to console only

## Future Enhancements (Not Implemented)

- Log level configuration in settings
- Log filtering in viewer by level/module
- Real-time log streaming in viewer
- Log compression for old files
- Email alerts for critical errors
