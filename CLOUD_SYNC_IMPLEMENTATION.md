# Cloud Sync Implementation

## Overview

Alarmify now includes a comprehensive cloud synchronization system that allows users to:
- Create accounts and securely authenticate
- Backup and restore alarms across devices
- Synchronize settings between devices
- Manage multiple devices
- Resolve conflicts intelligently
- Enable automatic synchronization

## Architecture

### Components

1. **CloudAuthManager** (`cloud_sync/cloud_auth.py`)
   - User registration and login
   - JWT-based token authentication
   - Password hashing with bcrypt
   - Token refresh mechanism
   - Session management

2. **CloudSyncAPI** (`cloud_sync/cloud_sync_api.py`)
   - Alarm backup and restore
   - Settings synchronization
   - Device registration and management
   - Sync history tracking
   - Data integrity with checksums

3. **SyncConflictResolver** (`cloud_sync/sync_conflict_resolver.py`)
   - Conflict detection between local and remote data
   - Multiple resolution strategies:
     - Newest wins (default)
     - Local wins
     - Remote wins
     - Intelligent merge
     - Manual resolution
   - Conflict reporting

4. **CloudSyncManager** (`cloud_sync/cloud_sync_manager.py`)
   - Main coordinator for all sync operations
   - Automatic synchronization scheduling
   - Device identification
   - Callback system for sync events

5. **Cloud Sync GUI** (`cloud_sync_gui.py`)
   - CloudLoginDialog: User authentication UI
   - CloudSyncDialog: Main sync management interface
   - Background sync with progress indicators
   - Device management interface

## Features

### Authentication System

- **Secure Registration**: 
  - Email validation
  - Password strength requirements (min 8 characters)
  - bcrypt password hashing (12 rounds)
  - Optional display name

- **JWT Authentication**:
  - Access tokens (24-hour expiration)
  - Refresh tokens (30-day expiration)
  - Automatic token refresh
  - Secure token storage

- **Account Management**:
  - Password changes
  - Account deletion
  - Session persistence

### Data Synchronization

#### Alarm Sync
- Backup all alarm configurations to cloud
- Restore alarms from cloud to any device
- Preserve alarm metadata:
  - Time and playlist
  - Volume settings
  - Fade-in configuration
  - Active days
  - Device ID and timestamps

#### Settings Sync
- Synchronize app settings across devices
- Theme preferences
- Notification settings
- Auto-sync configuration

#### Conflict Resolution
When multiple devices have different data:
1. **Detect** conflicts by comparing timestamps and content
2. **Resolve** using configured strategy:
   - Newest wins: Use most recently modified version
   - Merge: Intelligently combine non-conflicting changes
   - Manual: Prompt user to choose
3. **Apply** resolved data to local storage

### Multi-Device Management

- **Device Registration**:
  - Automatic device ID generation
  - Device name and type detection
  - Registration timestamp tracking

- **Device Monitoring**:
  - View all registered devices
  - Last sync time for each device
  - Current device identification

### Automatic Synchronization

- **Configurable Intervals**:
  - 15 minutes
  - 30 minutes (default)
  - 1 hour
  - 2 hours

- **Background Operation**:
  - Non-blocking sync in separate thread
  - Progress indicators
  - Error handling and retry logic

- **Smart Sync**:
  - Only sync when logged in
  - Automatic conflict resolution
  - Sync history tracking

## Usage

### Getting Started

1. **First Time Setup**:
   ```python
   # Click "☁ Cloud Sync" button in main window
   # Select "Create Account"
   # Enter email, password, and optional display name
   # Click "Create Account"
   ```

2. **Login on Another Device**:
   ```python
   # Click "☁ Cloud Sync" button
   # Enter your email and password
   # Click "Sign In"
   ```

3. **Sync Your Data**:
   ```python
   # In Cloud Sync dialog, click "Sync Now"
   # Or enable automatic sync with desired interval
   ```

### Sync Directions

- **Upload Only**: Send local data to cloud (backup)
- **Download Only**: Get data from cloud (restore)
- **Both** (default): Merge local and cloud data intelligently

### Manual Sync Operations

```python
# Through GUI
cloud_sync_button.click()  # Opens dialog
sync_now_button.click()     # Performs sync

# Programmatic
sync_manager = CloudSyncManager(alarm_manager)
success, message = sync_manager.login(email, password)
success, message, details = sync_manager.sync_all('both')
```

### Automatic Sync

```python
# Enable auto-sync
sync_manager.start_auto_sync(interval_minutes=30)

# Disable auto-sync
sync_manager.stop_auto_sync()
```

## Security

### Password Security
- Passwords never stored in plain text
- bcrypt hashing with 12 rounds (highly secure)
- Fallback to SHA-256 with salt if bcrypt unavailable
- Password verification without exposure
- Email validation with proper regex pattern

### Token Security
- JWT tokens with expiration
- Refresh token rotation
- Secure token storage with file permissions (0600)
- Token verification on each request

### Data Integrity
- MD5 checksums for all synced data
- Verification on restore
- Corruption detection and reporting

### Storage Security
- Local storage in user home directory (`~/.alarmify/`)
- File permissions set to owner-only (Unix systems)
- Separate storage per user ID

## Data Storage

### Local Files
```
~/.alarmify/
├── cloud_auth.json          # User accounts and sessions
├── cloud_data/              # Per-user cloud data
│   └── {user_id}/
│       ├── alarms_backup.json
│       ├── settings_backup.json
│       ├── devices.json
│       └── sync_history.json
├── .jwt_secret              # JWT signing secret
└── .device_id               # Unique device identifier
```

### Data Formats

#### Alarm Backup
```json
{
  "user_id": "abc123",
  "device_id": "device-uuid",
  "timestamp": "2024-01-16T12:00:00",
  "version": "1.0",
  "alarm_count": 3,
  "alarms": [
    {
      "time": "07:00",
      "playlist": "Morning Vibes",
      "playlist_uri": "spotify:playlist:...",
      "volume": 80,
      "fade_in_enabled": true,
      "fade_in_duration": 10,
      "days": ["Monday", "Tuesday", "Wednesday"],
      "last_modified": "2024-01-16T11:00:00"
    }
  ],
  "checksum": "md5-hash"
}
```

#### Device Registration
```json
{
  "device-uuid": {
    "device_id": "device-uuid",
    "device_name": "My-PC",
    "device_type": "windows",
    "registered_at": "2024-01-16T10:00:00",
    "last_sync": "2024-01-16T12:00:00"
  }
}
```

## API Reference

### CloudAuthManager

```python
# Registration
success, message, user_id = auth.register(email, password, display_name)

# Login
success, message, access_token, refresh_token = auth.login(email, password)

# Check login status
is_logged_in = auth.is_logged_in()

# Get current user
user = auth.get_current_user()

# Logout
auth.logout()

# Change password
success, message = auth.change_password(old_password, new_password)

# Delete account
success, message = auth.delete_account(password)
```

### CloudSyncAPI

```python
# Backup alarms
success, message = api.backup_alarms(user_id, alarms, device_id)

# Restore alarms
success, message, alarms = api.restore_alarms(user_id)

# Backup settings
success, message = api.backup_settings(user_id, settings, device_id)

# Restore settings
success, message, settings = api.restore_settings(user_id)

# Register device
success, message = api.register_device(user_id, device_id, device_name, device_type)

# Get devices
success, message, devices = api.get_devices(user_id)
```

### CloudSyncManager

```python
# Initialize
manager = CloudSyncManager(alarm_manager, settings_manager)

# Login
success, message = manager.login(email, password)

# Sync operations
success, message = manager.sync_alarms(direction='both')
success, message = manager.sync_settings(direction='both')
success, message, details = manager.sync_all(direction='both')

# Auto-sync
manager.start_auto_sync(interval_minutes=30)
manager.stop_auto_sync()

# Device management
devices = manager.get_devices()
status = manager.get_sync_status()
```

## Configuration

### Conflict Resolution Strategy

```python
# Set default strategy
resolver = SyncConflictResolver(default_strategy='newest_wins')

# Available strategies
STRATEGY_NEWEST_WINS = 'newest_wins'  # Use most recent version
STRATEGY_LOCAL_WINS = 'local_wins'    # Keep local version
STRATEGY_REMOTE_WINS = 'remote_wins'  # Use remote version
STRATEGY_MERGE = 'merge'              # Merge non-conflicting changes
STRATEGY_MANUAL = 'manual'            # Prompt user
```

### Sync Intervals

```python
# Configure auto-sync interval
manager.start_auto_sync(interval_minutes=15)  # 15 minutes
manager.start_auto_sync(interval_minutes=30)  # 30 minutes (default)
manager.start_auto_sync(interval_minutes=60)  # 1 hour
manager.start_auto_sync(interval_minutes=120) # 2 hours
```

### Callbacks

```python
# Set sync completion callback
manager.on_sync_complete = lambda results: print(f"Sync complete: {results}")

# Set sync error callback
manager.on_sync_error = lambda message, results: print(f"Sync error: {message}")
```

## Error Handling

### Common Errors

1. **Not Logged In**
   - Error: "Not logged in"
   - Solution: Call `manager.login()` first

2. **Sync In Progress**
   - Error: "Sync already in progress"
   - Solution: Wait for current sync to complete

3. **Network/Connection Issues**
   - Error: "Failed to sync: [network error]"
   - Solution: Check connectivity, retry

4. **Data Corruption**
   - Error: "Backup data corrupted"
   - Solution: Checksum mismatch detected, data rejected

5. **Invalid Credentials**
   - Error: "Invalid email or password"
   - Solution: Verify credentials, reset if needed

### Error Recovery

```python
# Graceful error handling
success, message, details = manager.sync_all('both')
if not success:
    logger.error(f"Sync failed: {message}")
    # Check details for partial success
    if details.get('alarms_success'):
        print("Alarms synced successfully")
    if details.get('settings_success'):
        print("Settings synced successfully")
```

## Testing

### Manual Testing

1. **Create Account**: Register new user
2. **Login**: Authenticate on Device 1
3. **Create Alarms**: Set up test alarms
4. **Sync Upload**: Upload alarms to cloud
5. **Login Device 2**: Login on second device
6. **Sync Download**: Download alarms to Device 2
7. **Verify**: Check alarms match on both devices
8. **Modify & Sync**: Change alarms, sync both ways
9. **Conflict Test**: Modify same alarm on both devices, sync
10. **Auto-Sync**: Enable auto-sync, verify periodic updates

### Unit Testing

```python
# Test authentication
def test_registration():
    auth = CloudAuthManager()
    success, message, user_id = auth.register('test@example.com', 'password123')
    assert success
    assert user_id

# Test sync
def test_alarm_sync():
    manager = CloudSyncManager()
    manager.login('test@example.com', 'password123')
    success, message = manager.sync_alarms('upload')
    assert success
```

## Dependencies

New dependencies added to `requirements.txt`:
- `PyJWT>=2.8.0` - JWT token encoding/decoding
- `bcrypt>=4.0.1` - Secure password hashing

## Limitations

### Current Version
- Local file-based storage (production would use database)
- No actual network API (simulated with local files)
- Single-user per device (no user switching in GUI)
- Manual conflict resolution UI not implemented

### Future Enhancements
- Cloud database backend (PostgreSQL, MongoDB)
- REST API with HTTPS
- WebSocket for real-time sync
- Conflict resolution UI
- File encryption at rest
- Two-factor authentication (2FA)
- Social login (Google, Microsoft, Apple)
- Sync status notifications
- Bandwidth optimization
- Delta sync (only changes)

## Troubleshooting

### Sync Not Working
1. Check login status: `manager.is_logged_in()`
2. Verify credentials in `~/.alarmify/cloud_auth.json`
3. Check logs for error messages
4. Try manual sync first before enabling auto-sync

### Conflicts Not Resolving
1. Check conflict resolver strategy
2. Review sync history for conflict details
3. Try different resolution strategy
4. Manually backup/restore if needed

### Authentication Issues
1. Verify email format
2. Check password length (min 8 characters)
3. Clear auth cache: Delete `~/.alarmify/cloud_auth.json`
4. Re-register if account corrupted

### Performance Issues
1. Reduce auto-sync frequency
2. Check alarm/settings count
3. Review sync history for patterns
4. Consider manual sync instead

## Migration Guide

### From Non-Sync Version
1. Update Alarmify to cloud sync version
2. Install new dependencies: `pip install -r requirements.txt`
3. Click "☁ Cloud Sync" button
4. Create account or login
5. Click "Sync Now" to upload existing alarms
6. Repeat on other devices

### Backing Up Before Migration
```bash
# Backup alarm data
cp ~/.alarmify/alarm_templates.json ~/alarm_backup.json
cp -r ~/.alarmify ~/alarmify_backup/
```

## Best Practices

1. **Regular Sync**: Enable auto-sync for automatic backups
2. **Multiple Devices**: Register all devices for seamless experience
3. **Conflict Prevention**: Sync before making major changes
4. **Password Security**: Use strong, unique password
5. **Backup**: Periodically export alarms locally
6. **Review History**: Check sync history for issues
7. **Update Regularly**: Keep Alarmify updated for latest features

## Support

For issues or questions:
1. Check logs: `View Logs` button in main window
2. Review sync history in Cloud Sync dialog
3. Check this documentation
4. Report bugs with log files attached
