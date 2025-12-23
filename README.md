# Alarmify - Spotify Alarm Clock

![Alarmify Logo](Logo%20First%20Draft.png)

A PyQt5-based desktop application that wakes you up with your favorite Spotify playlists. Set alarms to automatically play specific playlists at scheduled times with customizable volume control.

## Features

- 🎵 **Playlist Browser** - Browse and select from your Spotify playlists with cover art thumbnails
- ⏰ **Smart Alarms** - Schedule daily recurring alarms for specific times
- 🔊 **Volume Control** - Set custom volume levels for each alarm
- 🎨 **Spotify-Themed UI** - Dark theme matching Spotify's visual design
- 🔐 **Secure Authentication** - OAuth 2.0 integration with Spotify
- 🧵 **Thread-Safe** - Concurrent alarm scheduling and GUI operations
- 🖥️ **Device Management** - Automatic playback on your active Spotify device
- 📊 **Alarm Manager** - View, edit, and delete scheduled alarms

## Screenshots

### Main Window
![Main Window](docs/screenshots/main-window.png)
*The main Alarmify interface showing playlist browser, alarm controls, and volume settings*

### Settings Dialog
![Settings Dialog](docs/screenshots/settings-dialog.png)
*Configure your Spotify API credentials*

### Alarm Manager
![Alarm Manager](docs/screenshots/alarm-manager.png)
*View and manage all scheduled alarms*

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Spotify Premium account (required for playback control)
- Spotify Developer App credentials ([Get them here](https://developer.spotify.com/dashboard))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd alarmify
   ```

2. **Create and activate virtual environment**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   source .venv/bin/activate   # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Spotify API credentials**
   - Create a [Spotify Developer App](https://developer.spotify.com/dashboard)
   - Add `http://localhost:8888/callback` to your app's Redirect URIs
   - Launch Alarmify and click the settings gear icon (⚙)
   - Enter your Client ID, Client Secret, and Redirect URI

5. **Run the application**
   ```bash
   python main.py
   ```

## Usage

### Setting Up Your First Alarm

1. **Authenticate with Spotify**
   - Click "Login to Spotify" button
   - Browser will open for authorization
   - Grant permissions and return to the app

2. **Browse Your Playlists**
   - Your playlists will load automatically with cover art
   - Select the playlist you want to wake up to

3. **Configure Alarm**
   - Set the desired wake-up time using the time picker
   - Adjust the alarm volume with the slider (0-100%)
   - Click "Set Alarm" to schedule

4. **Manage Alarms**
   - Click "Manage Alarms" to view all scheduled alarms
   - Delete alarms you no longer need
   - Multiple alarms can be active simultaneously

### Tips for Best Experience

- **Keep Spotify Open**: Leave Spotify desktop/mobile app open on a device
- **Active Device**: Ensure you have an active Spotify device (computer, phone, speaker)
- **Volume Testing**: Test alarm volume before your actual wake-up time
- **Playlist Length**: Use playlists with multiple songs for gradual wake-up
- **Premium Account**: Spotify Premium is required for playback API access

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive step-by-step guide with screenshots
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute to Alarmify
- **[Planning & Strategy](docs/PLANNING.md)** - Product roadmap, features, design system
- **[Architecture Overview](AGENTS.md)** - Technical details for developers

## Troubleshooting

### Common Issues

#### "Spotify credentials not set" Error

**Problem**: The application can't find your Spotify API credentials.

**Solution**:
1. Click the settings gear icon (⚙) in the top-right corner
2. Enter your Spotify Developer App credentials:
   - Client ID
   - Client Secret
   - Redirect URI (default: `http://localhost:8888/callback`)
3. Make sure the Redirect URI matches exactly what's configured in your Spotify Developer Dashboard
4. Click "Save" and restart the authentication process

#### Authentication Browser Window Doesn't Open

**Problem**: Clicking "Login to Spotify" doesn't open a browser window.

**Solution**:
1. Copy the authorization URL from the console/terminal
2. Manually paste it into your browser
3. Complete the authorization
4. The callback should still work automatically

**Alternative**:
- Check if your default browser is set correctly
- Try running the app with administrator privileges
- Temporarily disable firewall/antivirus that might block port 8888

#### "No active device" Error When Alarm Triggers

**Problem**: Alarm is scheduled but can't play because no Spotify device is active.

**Solution**:
1. Open Spotify on any device (desktop, mobile, web player, smart speaker)
2. Play any song briefly to activate the device
3. Your device will remain active for future alarms
4. Consider keeping Spotify desktop app running in background

**Pro Tip**: Use Spotify Connect to select specific playback devices in advance.

#### Alarm Doesn't Trigger

**Problem**: You set an alarm but nothing happens at the scheduled time.

**Checklist**:
- ✓ Application must be running (don't close the window)
- ✓ Computer must not be in sleep/hibernation mode
- ✓ At least one Spotify device must be active
- ✓ Spotify Premium account is required
- ✓ Check "Manage Alarms" to confirm alarm is scheduled
- ✓ System time is correct (alarms use 24-hour format)

**Debug Steps**:
1. Open "Manage Alarms" to verify the alarm is listed
2. Check the console/terminal for error messages
3. Set a test alarm for 1-2 minutes from now
4. Ensure Spotify is open and a device is active

#### Playlists Don't Load

**Problem**: After authentication, playlist list remains empty.

**Solution**:
1. Check your internet connection
2. Verify you've granted all requested permissions during OAuth
3. Re-authenticate by clicking "Login to Spotify" again
4. Check if you have any playlists in your Spotify account
5. Try refreshing by logging out and back in

**API Permissions**: Ensure your Spotify app has these scopes enabled:
- `user-library-read`
- `user-read-playback-state`
- `user-modify-playback-state`
- `playlist-read-private`

#### Playlist Images Not Showing

**Problem**: Playlists load but thumbnails are missing.

**Solution**:
- Wait a few seconds - images load asynchronously in background
- Check internet connection stability
- Some playlists may not have cover art (default placeholder shows)
- Restart the application to retry image downloads

#### Volume Control Not Working

**Problem**: Slider changes but Spotify volume doesn't adjust during alarm.

**Solution**:
1. Verify the device supports volume control (not all Spotify devices do)
2. Try manually adjusting volume in Spotify to test device capability
3. Some devices (e.g., browsers, some smart speakers) don't support API volume control
4. Use desktop Spotify app or mobile app for best volume control support

#### Application Crashes or Freezes

**Problem**: App becomes unresponsive or crashes unexpectedly.

**Solution**:
1. Check terminal/console for error messages
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Update PyQt5: `pip install --upgrade PyQt5`
4. Delete `.cache` file in app directory and re-authenticate
5. Try removing and re-adding your Spotify credentials

**Report Issues**: If crashes persist, please [open an issue](issues) with:
- Error messages from console
- Python version (`python --version`)
- OS version
- Steps to reproduce

#### Port 8888 Already in Use

**Problem**: Error message about port 8888 being unavailable during authentication.

**Solution**:
1. Close any other applications using port 8888
2. Change the Redirect URI in both:
   - Spotify Developer Dashboard (e.g., to `http://localhost:8889/callback`)
   - Alarmify settings dialog
3. Restart the application

**Check Port Usage** (Windows):
```powershell
netstat -ano | findstr :8888
```

#### Thread Safety Issues (Rare)

**Problem**: Unusual behavior when setting alarms while browsing playlists.

**Solution**:
- All API calls are thread-safe by design
- If you experience issues, try:
  1. Setting alarms one at a time
  2. Waiting for playlist loading to complete before scheduling alarms
  3. Checking for application updates
  4. Reporting the issue with reproduction steps

### Error Messages Explained

| Error Message | Meaning | Solution |
|--------------|---------|----------|
| `Spotify credentials not set` | Missing API credentials | Configure credentials in Settings dialog |
| `Failed to receive authorization code` | OAuth callback failed | Check Redirect URI matches dashboard settings |
| `Spotify client not authenticated` | Not logged in | Click "Login to Spotify" button |
| `No active device` | No Spotify device available | Open Spotify on any device |
| `Playlist not found` | Playlist was deleted/renamed | Select a different playlist |
| `Could not load playlists` | API request failed | Check internet connection, re-authenticate |
| `Could not save credentials` | File system error | Check directory permissions |

### Getting Help

- **Issues**: [Report bugs or request features](issues)
- **Discussions**: [Ask questions and share tips](discussions)
- **Documentation**: See [User Guide](docs/USER_GUIDE.md) for detailed instructions
- **Development**: See [Contributing Guide](CONTRIBUTING.md) for developer info

## Technical Architecture

### Thread Safety Implementation

Alarmify implements comprehensive thread safety to prevent race conditions:

- **SpotifyAPI Thread Safety** (`spotify_api/spotify_api.py`)
  - Reentrant lock (RLock) protects all API calls
  - `@thread_safe_api_call` decorator ensures synchronized access
  - Command queue pattern available for advanced serialization

- **Alarm Manager Thread Safety** (`alarm.py`)
  - Threading Lock guards alarm list modifications
  - Protected operations: add, remove, clear, list alarms
  - Background daemon thread for scheduler execution

### Concurrency Scenarios Handled

1. GUI + Alarm Scheduler: User browsing playlists while alarm triggers
2. Multiple Alarms: Multiple alarms triggering simultaneously
3. Manual Playback + Alarm: User interaction during alarm trigger
4. Settings Changes: Credential updates during active scheduling

### Testing Thread Safety

Run comprehensive thread safety tests:
```bash
python -m pytest tests/test_thread_safety.py -v
```

## Technology Stack

- **Language**: Python 3.10+
- **GUI Framework**: PyQt5
- **API Library**: Spotipy (Spotify Web API wrapper)
- **Scheduler**: schedule library with threading
- **Environment**: python-dotenv for configuration

## Project Structure

```
alarmify/
├── main.py                 # Application entry point
├── gui.py                  # Main window and UI components
├── alarm.py                # Alarm scheduling and management
├── spotify_api/
│   └── spotify_api.py     # Thread-safe Spotify API wrapper
├── tests/                  # Test suite
├── docs/                   # Documentation and screenshots
├── requirements.txt        # Python dependencies
├── spotify_style.qss       # Qt stylesheet for Spotify theme
└── .env                    # Spotify credentials (not in git)
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Setting up development environment
- Coding standards and style guide
- Testing guidelines
- Pull request process
- Architecture decisions

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_alarm.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## Building Executable

PyInstaller spec file included for creating standalone executable:

```bash
pyinstaller alarmify.spec
```

The built application will be in `dist/alarmify/`.

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) for music control
- [Spotipy](https://spotipy.readthedocs.io/) for Python API wrapper
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for GUI framework
- [schedule](https://schedule.readthedocs.io/) for alarm scheduling

## Future Enhancements

- [ ] System tray integration for background running
- [ ] Multiple alarm profiles with different settings
- [ ] Fade-in volume animation
- [ ] Snooze functionality
- [ ] Alarm history and statistics
- [ ] Custom notification sounds
- [ ] Integration with calendar apps
- [ ] Smart alarm (play based on sleep cycle)

## Support

If you find Alarmify useful, please ⭐ star the repository!

For issues, feature requests, or contributions, see [CONTRIBUTING.md](CONTRIBUTING.md).
