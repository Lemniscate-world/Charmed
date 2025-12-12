# Logging System - Quick Usage Guide

## For End Users

### Viewing Logs in the Application

1. **Open Log Viewer**
   - Launch Alarmify
   - Click the "View Logs" button (located in the right panel below "Manage Alarms")

2. **Navigate Logs**
   - Use the dropdown menu at the top to switch between different log files
   - The newest log file is shown by default
   - Logs are displayed in chronological order (oldest to newest)
   - The view automatically scrolls to show the latest entries

3. **Refresh Logs**
   - Click the "Refresh" button to reload the current log file
   - Useful to see the latest entries while the app is running

4. **Export Logs**
   - Click "Export Logs..." button
   - Choose a location to save the log file
   - Useful for sharing logs when reporting issues

5. **Open Log Folder**
   - Click "Open Log Folder" to open the logs directory in your file explorer
   - Access all historical log files

### Log File Location
- **Windows**: `<Alarmify folder>/logs/`
- Log files are named: `alarmify_YYYYMMDD_HHMMSS.log`
- Example: `alarmify_20240115_143045.log`

### When to Check Logs

Check logs when:
- An alarm doesn't trigger as expected
- Spotify playback fails
- Authentication issues occur
- You want to verify alarm scheduling
- Reporting a bug to support

### Interpreting Log Levels

- **[INFO]**: Normal operation (e.g., "Alarm scheduled successfully")
- **[WARNING]**: Minor issues that don't stop operation (e.g., "Failed to set volume")
- **[ERROR]**: Problems that need attention (e.g., "Alarm playback failed")
- **[DEBUG]**: Detailed technical information

## For Developers

### Adding Logging to New Code

1. **Import the logger**
   ```python
   from logging_config import get_logger
   
   logger = get_logger(__name__)
   ```

2. **Basic logging**
   ```python
   # Information
   logger.info('User action completed')
   
   # Warning
   logger.warning('Non-critical issue occurred')
   
   # Error
   logger.error('Operation failed')
   
   # Debug (detailed info)
   logger.debug('Variable value: %s', some_var)
   ```

3. **Exception logging**
   ```python
   try:
       risky_operation()
   except Exception as e:
       logger.error(f'Operation failed: {e}', exc_info=True)
       # exc_info=True includes full stack trace
   ```

4. **Structured logging**
   ```python
   # Include relevant context
   logger.info(f'Alarm scheduled: time={time}, playlist={playlist}, volume={volume}%')
   ```

### Best Practices

1. **Use appropriate log levels**
   - DEBUG: Detailed diagnostic info
   - INFO: General informational messages
   - WARNING: Non-critical issues
   - ERROR: Error events
   - CRITICAL: Severe errors

2. **Include context**
   - Log function parameters for operations
   - Include user actions
   - Add timing for long operations

3. **Don't log sensitive data**
   - Never log passwords, tokens, or API keys
   - Be careful with user data

4. **Use f-strings for readability**
   ```python
   logger.info(f'Processing {count} items for user {username}')
   ```

### Configuration

Default configuration in `logging_config.py`:
- Log level: INFO (can be changed to DEBUG for more detail)
- Max file size: 5MB before rotation
- Backup count: 5 files kept
- Format: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`

To change log level globally:
```python
from logging_config import setup_logging
import logging

setup_logging(log_level=logging.DEBUG)  # More verbose
```

### Testing with Logs

When testing:
1. Check console output for immediate feedback
2. Review log files for complete history
3. Look for ERROR or WARNING messages
4. Verify structured logging includes all expected fields

### Debugging

To debug issues:
1. Set log level to DEBUG in `logging_config.py`
2. Reproduce the issue
3. Open log file and search for ERROR/WARNING
4. Check timestamps to trace execution flow
5. Look at surrounding INFO messages for context
