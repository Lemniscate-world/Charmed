# Charmed - The Magical Spotify Alarm Ecosystem

A premium, cross-platform Spotify alarm ecosystem that makes mornings magical. Built on the Charmed design system with glassmorphism and smooth spring physics.

## Features

- 🎵 **Playlist Browser** - Browse and select from your Spotify playlists with cover art thumbnails
- ⏰ **Smart Alarms** - Schedule daily recurring alarms for specific times
- 🔊 **Volume Control** - Set custom volume levels for each alarm
- 🌅 **Gradual Wake-Up** - Fade-in volume from 0% to target over 5-30 minutes for gentle awakening
- 🎧 **Preview Mode** - Test your fade-in settings with a 30-second preview before setting the alarm
- 🎨 **Spotify-Themed UI** - Dark theme matching Spotify's visual design
- 🔐 **Secure Authentication** - OAuth 2.0 integration with Spotify
- 🧵 **Thread-Safe** - Concurrent alarm scheduling and GUI operations
- 🖥️ **Device Management** - Automatic playback on your active Spotify device
- 📊 **Alarm Manager** - View, edit, and delete scheduled alarms
- 😴 **Snooze Functionality** - Configurable snooze intervals (5/10/15 minutes) with persistent state
- 🔄 **Local Fallback Alarm** - Built-in alarm sound using QMediaPlayer when Spotify is unavailable

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Spotify Premium account (required for playback control)
- Spotify Developer App credentials ([Get them here](https://developer.spotify.com/dashboard))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd charmed
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
   - Launch Charmed and click the settings gear icon (⚙)
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
   - **Optional**: Enable gradual volume fade-in
     - Check "Enable gradual volume fade-in" in the alarm setup dialog
     - Choose fade-in duration (5-30 minutes) using the slider
     - Click "Preview Fade-In (30s)" to test with current playback
   - Click "Set Alarm" to schedule

4. **Manage Alarms**
   - Click "Manage Alarms" to view all scheduled alarms
   - Delete alarms you no longer need
   - Multiple alarms can be active simultaneously

### Snooze Functionality

When an alarm triggers, you have flexible snooze options:

**Snooze Methods:**
1. **Snooze Dialog** - Popup with three snooze duration buttons (5/10/15 min) or dismiss
2. **System Tray Menu** - Right-click tray icon during active alarm for quick snooze access

**Features:**
- Configurable intervals: 5, 10, or 15 minutes
- Persistent snooze state (survives app restarts)
- Multiple simultaneous snoozed alarms supported
- Fade-in settings preserved when snoozing
- Visual indicators in system tray when alarm is snoozable
- Snoozed alarms shown in Alarm Manager dialog

**Persistent State:**
- Snooze data saved to `~/.charmed/snooze_state.json`
- Automatically restored on app restart
- Expired snoozes cleaned up automatically

### Using the Gradual Wake-Up Feature

The fade-in feature gradually increases volume from 0% to your target volume over a configurable duration, providing a gentle and natural wake-up experience.

**How to Enable Fade-In:**

1. Click "Set Alarm" after selecting your playlist and time
2. In the Alarm Setup dialog, check "Enable gradual volume fade-in"
3. Use the slider to set fade-in duration (5-30 minutes)
4. **Preview your settings**: Click "Preview Fade-In (30s)" to hear a 30-second compressed version
   - Make sure Spotify is playing before previewing
   - The preview will fade from 0% to your target volume over 30 seconds
   - You can stop the preview at any time
5. Click "Set Alarm" to save your alarm with fade-in enabled

**Fade-In Technical Details:**

- Volume increases in smooth steps every 5 seconds
- For a 10-minute fade-in: 120 volume adjustments over 600 seconds
- Algorithm ensures linear volume progression
- Thread-safe implementation prevents conflicts with other alarms
- Fade-in state is persisted with each alarm

**Recommended Durations:**

- **5-10 minutes**: Light sleepers or quick wake-ups
- **15-20 minutes**: Most users, natural wake-up
- **25-30 minutes**: Deep sleepers or gentle meditation wake-up

### Local Fallback Alarm

Charmed includes a built-in local alarm that plays when Spotify is unavailable. This ensures you'll never miss an alarm even if:

- No Spotify device is active
- Spotify Premium has expired
- Network connectivity issues occur

The fallback alarm uses the system's default sound or a bundled alarm tone via QMediaPlayer.

**Features:**
- Automatic activation when Spotify playback fails
- Configurable fallback volume
- Persistent until dismissed
- Works completely offline

### Tips for Best Experience

- **Keep Spotify Open**: Leave Spotify desktop/mobile app open on a device
- **Active Device**: Ensure you have an active Spotify device (computer, phone, speaker)
- **Volume Testing**: Test alarm volume before your actual wake-up time
- **Fade-In Preview**: Use the 30-second preview to test your fade-in settings
- **Gentle Wake-Up**: Enable 15-20 minute fade-in for the most natural wake-up experience
- **Playlist Length**: Use playlists with multiple songs for gradual wake-up
- **Premium Account**: Spotify Premium is required for playback API access
- **Fallback Ready**: The local fallback alarm has your back if Spotify fails

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive step-by-step guide with screenshots
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute to Charmed
- **[Planning & Strategy](docs/PLANNING.md)** - Product roadmap, features, design system
- **[Architecture Overview](AGENTS.md)** - Technical details for developers
- **[AI Guidelines](AI_GUIDELINES.md)** - Development methodology and coding standards
- **[Security Policy](security.md)** - Security practices and vulnerability reporting

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
5. **Don't worry**: The local fallback alarm will play if Spotify fails

**Pro Tip**: Use Spotify Connect to select specific playback devices in advance.

#### Alarm Doesn't Trigger

**Problem**: You set an alarm but nothing happens at the scheduled time.

**Checklist**:
- ✓ Application must be running (don't close the window)
- ✓ Computer must not be in sleep/hibernation mode
- ✓ At least one Spotify device must be active (or fallback alarm will play)
- ✓ Spotify Premium account is required for Spotify playback
- ✓ Check "Manage Alarms" to confirm alarm is scheduled
- ✓ System time is correct (alarms use 24-hour format)

**Debug Steps**:
1. Open "Manage Alarms" to verify the alarm is listed
2. Check the console/terminal for error messages
3. Set a test alarm for 1-2 minutes from now
4. Ensure Spotify is open and a device is active (or test the fallback alarm)

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
5. The fallback alarm has its own volume control independent of Spotify

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
   - Charmed settings dialog
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
| `No active device` | No Spotify device available | Open Spotify on any device, or fallback alarm will play |
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

Charmed implements comprehensive thread safety to prevent race conditions:

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
5. Local Fallback: Fallback alarm plays independently of Spotify

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
- **Local Audio**: QMediaPlayer for fallback alarm

## Project Structure

```
charmed/
├── main.py                 # Application entry point
├── gui.py                  # Main window and UI components
├── alarm.py                # Alarm scheduling and management
├── spotify_api/
│   └── spotify_api.py     # Thread-safe Spotify API wrapper
├── tests/                  # Test suite
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── spotify_style.qss       # Qt stylesheet for Spotify theme
├── .env                    # Spotify credentials (not in git)
├── security.md             # Security policies
├── AI_GUIDELINES.md        # Development methodology
└── SESSION_SUMMARY.md      # Session history
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Setting up development environment
- Coding standards and style guide
- Testing guidelines
- Pull request process
- Architecture decisions

### Security Development

This project follows strict security practices:

- **Static Analysis**: CodeQL, SonarQube, and Codacy integration
- **Security Scanning**: bandit and safety before every commit
- **Advanced Testing**: Fuzzing (AFL), Load Testing (Locust), Mutation Testing (Stryker)
- **Policy as Code**: Automated security compliance

See [security.md](security.md) for full security policies and [AI_GUIDELINES.md](AI_GUIDELINES.md) for development methodology.

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_alarm.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

**Test Results**: 24 passing tests (Spotify + Local Fallback)

## Building Executable

PyInstaller spec file included for creating standalone executable:

```bash
pyinstaller charmed.spec
```

The built application will be in `dist/charmed/`.

### Version Management

Manage versions with the built-in tool:

```bash
# Get current version
python version_manager.py --get

# Set version
python version_manager.py --set 1.2.3

# Bump version
python version_manager.py --bump major  # 1.0.0 -> 2.0.0
python version_manager.py --bump minor  # 1.0.0 -> 1.1.0
python version_manager.py --bump patch  # 1.0.0 -> 1.0.1
```

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
- [ ] Alarm history and statistics
- [ ] Custom notification sounds
- [ ] Integration with calendar apps
- [ ] Smart alarm (play based on sleep cycle)
- [ ] Weekend vs weekday alarm profiles
- [ ] Weather-based playlist selection

## Support

If you find Charmed useful, please ⭐ star the repository!

For issues, feature requests, or contributions, see [CONTRIBUTING.md](CONTRIBUTING.md).

