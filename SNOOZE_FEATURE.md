# Snooze Functionality - Complete Documentation

## Overview

The snooze functionality allows users to delay alarms with configurable intervals, providing a familiar alarm clock experience with persistent state management and multiple access methods.

## Features

### 1. Configurable Snooze Intervals

Three preset intervals available:
- **5 minutes** - Quick snooze for brief delay
- **10 minutes** - Standard snooze duration
- **15 minutes** - Extended snooze for more sleep

Intervals can be customized in `alarm.py`:
```python
SNOOZE_INTERVALS = [5, 10, 15]  # Modify these values as needed
DEFAULT_SNOOZE_DURATION = 5
```

### 2. Multiple Access Methods

#### A. Snooze Notification Dialog
- Appears automatically when alarm triggers
- Large, centered buttons for each snooze duration
- Dismiss button to cancel alarm without snoozing
- Spotify green (🎵) color scheme
- Always-on-top window for visibility

#### B. System Tray Menu
- Right-click tray icon to access snooze options
- Only visible when alarm is active
- Quick access without switching windows
- Emoji icons for visual clarity (⏰ for snooze, ❌ for dismiss)
- Confirmation notifications

### 3. Persistent State Management

#### Storage Location
- **Windows:** `C:\Users\<username>\.alarmify\snooze_state.json`
- **Linux/Mac:** `~/.alarmify/snooze_state.json`

#### JSON Structure
```json
[
  {
    "snooze_time": "2024-01-15T08:15:00",
    "original_playlist": "Morning Vibes",
    "snooze_duration": 10,
    "playlist_uri": "spotify:playlist:abc123",
    "volume": 80,
    "fade_in_enabled": true,
    "fade_in_duration": 15
  }
]
```

#### Features
- Automatic save on every snooze
- Automatic restore on app startup
- Expired snoozes cleaned automatically
- Thread-safe operations with locking
- Survives app crashes and restarts

### 4. System Tray Integration

#### Dynamic Menu
The system tray context menu dynamically shows/hides snooze options:

**Normal State:**
```
├── Show
├── Hide
├── ───────────
└── Quit
```

**Active Alarm State:**
```
├── Show
├── Hide
├── ───────────
├── ⏰ Snooze 5 minutes
├── ⏰ Snooze 10 minutes
├── ⏰ Snooze 15 minutes
├── ❌ Dismiss Alarm
├── ───────────
└── Quit
```

#### Behavior
- Snooze section appears when alarm triggers
- Automatically hidden after action (snooze/dismiss)
- Stored alarm data ensures correct playlist on snooze
- Tray notifications confirm actions

### 5. Alarm Manager Integration

The Alarm Manager dialog shows two sections:

#### Scheduled Alarms Table
- Regular recurring alarms
- Time, playlist, volume, days, actions

#### Snoozed Alarms Table
- Currently snoozed alarms
- Will Trigger At (exact time)
- Original playlist name
- Snooze duration (in minutes)
- Auto-refresh to remove expired snoozes

### 6. Fade-in Preservation

When an alarm with fade-in is snoozed:
- Fade-in enabled/disabled state preserved
- Fade-in duration preserved
- Volume target preserved
- Smooth wake-up experience maintained

## User Workflow

### Setting an Alarm
1. Select playlist
2. Set time
3. Configure volume and optional fade-in
4. Click "Set Alarm"

### When Alarm Triggers
1. Spotify playlist starts playing
2. SnoozeNotificationDialog appears
3. System tray shows snooze options
4. User chooses:
   - Snooze 5/10/15 minutes (dialog or tray)
   - Dismiss alarm

### If Snoozed
1. Alarm rescheduled for selected duration
2. State saved to JSON file
3. Confirmation notification shown
4. Snooze visible in Alarm Manager
5. Tray menu options hidden

### When Snooze Triggers
1. Same playlist plays
2. Same volume and fade-in settings
3. Can snooze again or dismiss
4. Process repeats

### After App Restart
1. App loads snooze state from JSON
2. Snoozed alarms restored to memory
3. After Spotify login, alarms rescheduled
4. Expired snoozes automatically removed

## Implementation Details

### Core Components

#### alarm.py
**Snooze Management:**
```python
class Alarm:
    def snooze_alarm(self, alarm_data, snooze_minutes=5):
        """Schedule snooze and save state"""
    
    def _save_snooze_state(self):
        """Persist to JSON"""
    
    def _load_snooze_state(self):
        """Restore from JSON"""
    
    def reschedule_snoozed_alarms(self, spotify_api):
        """Reschedule after login"""
    
    def get_snoozed_alarms(self):
        """Get active snoozes, clean expired"""
```

#### gui.py
**System Tray Integration:**
```python
class AlarmApp:
    def _setup_system_tray(self):
        """Setup tray with snooze actions"""
    
    def _show_snooze_in_tray(self, alarm_data):
        """Show snooze options"""
    
    def _hide_snooze_from_tray(self):
        """Hide snooze options"""
    
    def _snooze_from_tray(self, minutes):
        """Handle tray snooze"""
    
    def _dismiss_alarm_from_tray(self):
        """Handle tray dismiss"""
```

**Snooze Dialog:**
```python
class SnoozeNotificationDialog(QDialog):
    def __init__(self, parent, title, message, alarm_data):
        """Create dialog with snooze buttons"""
    
    def _snooze(self, minutes):
        """Handle snooze button click"""
```

### Thread Safety

All snooze operations use `self._alarms_lock`:
```python
with self._alarms_lock:
    self.snoozed_alarms.append(snooze_info)
    # ... safe access to shared state
```

### Error Handling

- JSON load errors logged, non-fatal
- Invalid snooze data skipped with warning
- Failed reschedule logged, doesn't crash app
- Expired snoozes cleaned automatically

## Configuration Options

### Customizing Intervals

Edit `alarm.py`:
```python
# Change default intervals (in minutes)
SNOOZE_INTERVALS = [5, 10, 15]

# Change default snooze duration
DEFAULT_SNOOZE_DURATION = 5

# To add a 20-minute option:
SNOOZE_INTERVALS = [5, 10, 15, 20]
```

Then update `gui.py` to add UI elements for new intervals.

### Disabling Persistent State

To disable state persistence (snoozes won't survive restart):
```python
# In alarm.py, comment out:
# self._save_snooze_state()
```

### Changing Storage Location

```python
# In Alarm.__init__():
self.snooze_state_file = Path('/custom/path/snooze_state.json')
```

## Testing

Tests in `tests/test_alarm.py`:

```python
class TestSnoozeAlarm:
    def test_snooze_alarm_creates_scheduled_job()
    def test_snooze_alarm_starts_scheduler()
    def test_snooze_alarm_multiple_snoozes()
    def test_snooze_alarm_default_duration()

class TestGetSnoozedAlarms:
    def test_get_snoozed_alarms_empty()
    def test_get_snoozed_alarms_returns_info()
    def test_get_snoozed_alarms_excludes_job()

class TestShutdownWithSnooze:
    def test_shutdown_clears_snoozed_alarms()

class TestFadeInFeature:
    def test_snooze_with_fade_in()
```

Run tests:
```bash
python -m pytest tests/test_alarm.py::TestSnoozeAlarm -v
```

## API Reference

### Alarm.snooze_alarm(alarm_data, snooze_minutes=5)

Schedule an alarm snooze.

**Parameters:**
- `alarm_data` (dict): Alarm information
  - `playlist_uri` (str): Spotify playlist URI
  - `playlist_name` (str): Playlist display name
  - `volume` (int): Volume 0-100
  - `fade_in_enabled` (bool): Fade-in enabled
  - `fade_in_duration` (int): Fade-in duration in minutes
  - `spotify_api` (SpotifyAPI): API instance
- `snooze_minutes` (int): Snooze duration in minutes (default: 5)

**Returns:** None

**Side Effects:**
- Creates scheduled job for snooze time
- Adds to `snoozed_alarms` list
- Saves state to JSON file
- Starts scheduler if not running

### Alarm.get_snoozed_alarms()

Get active snoozed alarms.

**Returns:** list[dict]
- `snooze_time` (datetime): When alarm will trigger
- `original_playlist` (str): Playlist name
- `snooze_duration` (int): Duration in minutes

**Side Effects:**
- Removes expired snoozes
- Saves updated state to JSON

### Alarm.reschedule_snoozed_alarms(spotify_api)

Reschedule snoozed alarms after login.

**Parameters:**
- `spotify_api` (SpotifyAPI): Authenticated API instance

**Returns:** None

**Side Effects:**
- Creates jobs for unscheduled snoozes
- Starts scheduler if not running

## Troubleshooting

### Snooze Not Persisting

**Problem:** Snoozes don't survive app restart

**Solutions:**
1. Check file permissions on `~/.alarmify/`
2. Check logs for JSON save errors
3. Verify `_save_snooze_state()` is called

### Snoozed Alarm Not Triggering

**Problem:** Snoozed alarm doesn't play

**Solutions:**
1. Check Spotify authentication (log in after restart)
2. Call `reschedule_snoozed_alarms()` after login
3. Verify snooze time hasn't passed
4. Check scheduler is running

### System Tray Options Not Showing

**Problem:** Can't see snooze options in tray

**Solutions:**
1. Verify alarm triggered (check logs)
2. Check `_show_snooze_in_tray()` is called
3. Verify `current_alarm_data` is set
4. Restart app if menu state is stuck

## Future Enhancements

Potential improvements:
- Custom snooze durations via settings dialog
- Snooze history/statistics
- Maximum snooze count per alarm
- Progressive snooze intervals (5, 10, 15, 20...)
- Smart snooze (adjusts based on sleep patterns)
- Calendar integration for snooze scheduling

## Related Documentation

- `README.md` - User-facing snooze documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation summary
- `alarm.py` - Core snooze implementation
- `gui.py` - UI and system tray integration
- `tests/test_alarm.py` - Snooze test suite
