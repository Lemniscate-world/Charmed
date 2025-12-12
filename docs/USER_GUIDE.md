# Alarmify User Guide

Welcome to Alarmify! This comprehensive guide will walk you through everything you need to know to set up and use Alarmify as your personal Spotify alarm clock.

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Initial Setup](#initial-setup)
5. [Getting Started](#getting-started)
6. [Features Guide](#features-guide)
7. [Advanced Usage](#advanced-usage)
8. [Tips and Best Practices](#tips-and-best-practices)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

## Introduction

### What is Alarmify?

Alarmify is a desktop application that integrates with your Spotify account to wake you up with your favorite music. Instead of harsh beeps or buzzes, you can wake up to any playlist in your Spotify library at a custom volume level.

### Key Features

- 🎵 **Spotify Integration** - Access all your playlists directly
- ⏰ **Multiple Alarms** - Schedule as many alarms as you need
- 🔊 **Volume Control** - Set individual volume levels for each alarm
- 🎨 **Beautiful Interface** - Spotify-themed dark UI with playlist artwork
- 🔐 **Secure** - Uses official Spotify OAuth for authentication
- 💻 **Cross-Platform** - Works on Windows, macOS, and Linux

### How It Works

1. You authenticate with your Spotify account
2. Your playlists are loaded into the app
3. You select a playlist and set an alarm time
4. When the alarm triggers, Alarmify plays your chosen playlist on your active Spotify device

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **Python**: Version 3.10 or higher
- **RAM**: 512 MB minimum
- **Disk Space**: 100 MB for application and dependencies
- **Internet**: Required for Spotify API access
- **Spotify**: Premium subscription (required for playback control API)

### Recommended Setup

- **Internet**: Stable broadband connection
- **Spotify Device**: Desktop app, mobile app, or smart speaker for playback
- **Screen Resolution**: 1280x720 or higher for optimal UI experience

### Spotify Account Requirements

⚠️ **Important**: You must have a **Spotify Premium** account. The free tier does not support playback control via the Spotify API.

## Installation

### Step 1: Install Python

If you don't have Python installed:

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. ✅ Check "Add Python to PATH" during installation
4. Complete the installation

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python@3.10

# Or download from python.org
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

### Step 2: Download Alarmify

**Option A: Clone with Git** (recommended for developers)
```bash
git clone <repository-url>
cd alarmify
```

**Option B: Download ZIP**
1. Download the ZIP file from the repository
2. Extract to your desired location
3. Open terminal/command prompt in the extracted folder

### Step 3: Set Up Virtual Environment

Virtual environments keep Alarmify's dependencies isolated from your system Python.

**Windows PowerShell:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt when activated.

### Step 4: Install Dependencies

With your virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs:
- PyQt5 (GUI framework)
- spotipy (Spotify API wrapper)
- schedule (alarm scheduling)
- python-dotenv (environment variables)

### Step 5: Verify Installation

```bash
python main.py
```

If successful, the Alarmify window should open. If you see an error about Spotify credentials, that's expected - we'll set those up next!

## Initial Setup

### Step 1: Create Spotify Developer App

Before using Alarmify, you need to register an application with Spotify:

1. **Go to Spotify Developer Dashboard**
   - Visit [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
   - Log in with your Spotify account

2. **Create an App**
   - Click "Create app" button
   - Fill in the form:
     - **App name**: `Alarmify` (or your choice)
     - **App description**: `Personal alarm clock app`
     - **Redirect URI**: `http://localhost:8888/callback` ⚠️ **Must be exact**
     - **APIs used**: Check "Web API"
   - Accept terms and click "Save"

3. **Get Your Credentials**
   - Click on your new app in the dashboard
   - You'll see:
     - **Client ID**: A long alphanumeric string
     - **Client Secret**: Click "Show Client Secret" to reveal
   - Keep this page open - you'll need these values next

![Spotify Dashboard](screenshots/spotify-dashboard.png)
*Screenshot placeholder: Spotify Developer Dashboard with app details*

### Step 2: Configure Alarmify

1. **Launch Alarmify**
   ```bash
   python main.py
   ```

2. **Open Settings**
   - Click the gear icon (⚙) in the top-right corner of the window
   - The Settings dialog will open

3. **Enter Your Credentials**
   - **Client ID**: Paste from Spotify Dashboard
   - **Client Secret**: Paste from Spotify Dashboard  
   - **Redirect URI**: Should be `http://localhost:8888/callback`
     - This must match exactly what you entered in the Spotify Dashboard
   - Click "Save"

![Settings Dialog](screenshots/settings-dialog.png)
*Screenshot placeholder: Settings dialog with credential fields*

4. **Confirmation**
   - You'll see "Spotify credentials saved"
   - The "Login to Spotify" button is now enabled

### Step 3: Authenticate with Spotify

1. **Click "Login to Spotify"**
   - Your default browser will open
   - You'll see the Spotify authorization page

2. **Grant Permissions**
   - Review the permissions Alarmify requests:
     - Access your playlists
     - Control playback
     - Read playback state
   - Click "Agree" or "Accept"

3. **Return to Alarmify**
   - The browser will show "Authentication successful!"
   - You can close that tab
   - Alarmify will automatically load your playlists

![Authentication Flow](screenshots/auth-flow.png)
*Screenshot placeholder: Browser showing Spotify authorization page*

4. **Verify Success**
   - Top-right corner should show "Connected as [Your Name]"
   - Playlist list should populate with your playlists and cover art

## Getting Started

### Your First Alarm

Let's set up your first alarm step-by-step:

#### Step 1: Select a Playlist

1. Browse your playlists in the left panel
2. Playlists show:
   - Cover artwork (loading in background)
   - Playlist name
   - Number of tracks
   - Owner name
3. Click on the playlist you want to wake up to
4. The playlist will be highlighted

![Main Window](screenshots/main-window.png)
*Screenshot placeholder: Main window with playlist selected*

💡 **Tip**: Choose playlists with gradually increasing energy for a gentler wake-up experience.

#### Step 2: Set the Time

1. Look at the right panel for "Alarm Time"
2. Click the time display to edit
3. Use the spinner or type directly:
   - Hours: 00-23 (24-hour format)
   - Minutes: 00-59
4. Examples:
   - 7:00 AM = `07:00`
   - 2:30 PM = `14:30`
   - Midnight = `00:00`

![Time Picker](screenshots/time-picker.png)
*Screenshot placeholder: Time picker showing 07:00*

#### Step 3: Adjust Volume

1. Use the "Alarm Volume" slider
2. Drag left (quieter) or right (louder)
3. Percentage displays next to the slider
4. Recommended: Start with 60-80%

⚠️ **Warning**: Test your volume before setting a real alarm! What sounds reasonable might be too loud for sleeping.

#### Step 4: Set the Alarm

1. Click the "Set Alarm" button
2. Confirmation dialog appears with:
   - Alarm time
   - Selected playlist
   - Volume level
3. Click "OK" to confirm

![Alarm Confirmation](screenshots/alarm-confirmation.png)
*Screenshot placeholder: Confirmation dialog*

✅ **Success!** Your alarm is now scheduled and will trigger daily at the specified time.

#### Step 5: Keep Alarmify Running

⚠️ **Important**: Alarmify must be running for alarms to trigger!

- Don't close the application window
- Minimize it instead (keeps running in background)
- Make sure your computer isn't set to sleep/hibernate during alarm time

### Testing Your Alarm

Before relying on Alarmify for waking up:

1. **Set a Test Alarm**
   - Set for 2-3 minutes from now
   - Use a low volume (30-40%)

2. **Ensure Spotify is Ready**
   - Open Spotify desktop or mobile app
   - Play any song briefly (activates device)
   - Can pause after a few seconds

3. **Wait for the Alarm**
   - Keep Alarmify running
   - Watch the clock approach your test time
   - Playlist should start playing automatically

4. **Adjust as Needed**
   - Too loud? Lower the volume
   - Too quiet? Increase it
   - Wrong playlist? Delete and recreate

## Features Guide

### Managing Alarms

#### View All Alarms

1. Click "Manage Alarms" button (right panel)
2. Table shows all scheduled alarms:
   - Time (24-hour format)
   - Playlist name
   - Volume percentage
   - Delete button for each alarm

![Alarm Manager](screenshots/alarm-manager.png)
*Screenshot placeholder: Alarm Manager dialog showing multiple alarms*

#### Delete an Alarm

1. Open "Manage Alarms"
2. Find the alarm you want to remove
3. Click the "Delete" button in that row
4. Alarm is immediately removed (no confirmation)

#### Multiple Alarms

- Set as many alarms as you need
- Each can have different:
  - Times
  - Playlists
  - Volume levels
- Useful for:
  - Weekday vs. weekend wake-ups
  - Multiple people in household
  - Backup alarms

### Playlist Browser

#### Features

- **Cover Art**: Thumbnails load asynchronously
- **Metadata**: Track count and owner displayed
- **Scrolling**: Smooth scrolling for large libraries
- **Search**: (Planned feature - use Spotify app to organize playlists)

#### Tips

- Create dedicated "Morning" or "Alarm" playlists in Spotify
- Keep alarm playlists relatively long (30+ minutes)
- Mix of calm and energetic songs works well
- Update playlists in Spotify app, then restart Alarmify to see changes

### Volume Control

#### How It Works

- Volume is set on your **Spotify device**, not system volume
- Applies when alarm triggers, before playback starts
- Each alarm can have different volume

#### Device Compatibility

Not all devices support volume control via API:

✅ **Supported**:
- Spotify Desktop App (Windows, Mac, Linux)
- Spotify Mobile App (iOS, Android)
- Many smart speakers

❌ **Limited/Unsupported**:
- Web Player (some browsers)
- Some third-party devices
- Spotify Connect devices (varies)

💡 **Tip**: If volume control doesn't work, manually set your device volume before sleeping.

### Authentication Status

Top-right corner shows current status:

- **"Not connected"** (gray): Need to log in
- **"Connected"** (green): Authenticated, no user info
- **"Connected as [Name]"** (green): Fully authenticated

Clicking the status doesn't do anything - use "Login to Spotify" button to re-authenticate if needed.

### Settings

Click the gear icon (⚙) to access settings:

#### Current Settings

- Spotify Client ID
- Spotify Client Secret
- Redirect URI

#### When to Update

- Credentials expired or changed
- Switched to different Spotify app
- Authentication fails repeatedly

⚠️ **Security**: Client Secret is masked (shows dots). Your credentials are stored in `.env` file which is **not** committed to version control.

## Advanced Usage

### Running on Startup (Windows)

To ensure Alarmify starts when you boot your computer:

1. **Create Batch File**

Create `start-alarmify.bat` in the Alarmify folder:
```batch
@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
pythonw main.py
```

2. **Add to Startup**
   - Press `Win + R`
   - Type `shell:startup`
   - Press Enter
   - Create shortcut to your `.bat` file in this folder

3. **Test**
   - Restart your computer
   - Alarmify should start automatically

### Running on Startup (macOS)

1. **Create Launch Agent**

Create `~/Library/LaunchAgents/com.alarmify.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.alarmify</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/alarmify/.venv/bin/python</string>
        <string>/path/to/alarmify/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

2. **Load the Agent**
```bash
launchctl load ~/Library/LaunchAgents/com.alarmify.plist
```

### Running on Startup (Linux)

1. **Create Desktop Entry**

Create `~/.config/autostart/alarmify.desktop`:
```ini
[Desktop Entry]
Type=Application
Name=Alarmify
Exec=/path/to/alarmify/.venv/bin/python /path/to/alarmify/main.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

2. **Make Executable**
```bash
chmod +x ~/.config/autostart/alarmify.desktop
```

### Using Different Spotify Devices

You can control which device plays your alarm:

1. **Open Spotify** on your desired device
2. **Play any song** briefly (activates the device)
3. **Set your alarm** in Alarmify
4. Alarm will play on the most recently active device

💡 **Multi-Room Audio**: Use Spotify Connect to group devices before setting your alarm.

### Command Line Options

Currently, Alarmify doesn't support command-line arguments, but you can:

- Set environment variables before launching
- Edit `.env` file to change credentials
- Run in headless mode (planned feature)

### Integration with Smart Home

While Alarmify doesn't have direct smart home integration, you can:

1. **Trigger on Wake-Up**:
   - Use alarm to start Spotify on smart speaker
   - Configure smart lights to turn on at same time (via their apps)

2. **IFTTT Integration** (indirect):
   - Alarmify plays Spotify → Spotify triggers IFTTT webhook → Actions occur

## Tips and Best Practices

### Creating the Perfect Wake-Up Playlist

1. **Start Gentle**:
   - Begin with softer, slower songs
   - Acoustic or ambient tracks work well
   - Avoid starting with aggressive music

2. **Build Energy**:
   - Gradually increase tempo and volume
   - Mix in more upbeat songs after 10-15 minutes
   - End with motivational tracks

3. **Length Matters**:
   - At least 30 minutes long
   - Prevents awkward silence if you snooze
   - Gives variety throughout wake-up period

4. **Avoid Shuffle**:
   - Keep a deliberate song order
   - Spotify plays in order when triggered by API
   - You can predict what's playing when

### Optimal Volume Settings

| Volume % | Description | Best For |
|----------|-------------|----------|
| 20-40% | Very quiet | Light sleepers, shared rooms |
| 50-70% | Moderate | Most people, normal sleep |
| 80-90% | Loud | Heavy sleepers, need strong wake-up |
| 100% | Maximum | Emergency only, may be jarring |

💡 **Pro Tip**: Start at 60% and adjust based on experience. Can always increase later.

### Device Management

**Best Practices**:
- Keep one device (desktop app) as primary alarm device
- Leave Spotify desktop app open overnight
- Don't let computer sleep during alarm times
- Check device is active before bed

**Power Settings** (Windows):
```
Settings → System → Power & Sleep
Set "Sleep after" to "Never" during alarm times
```

**Energy Saver** (macOS):
```
System Preferences → Energy Saver
Uncheck "Put hard disks to sleep when possible"
```

### Backup Strategies

Don't rely solely on Alarmify:

1. **Phone Alarm**: Set phone alarm 5-10 minutes after Alarmify
2. **Multiple Alarms**: Set 2-3 Alarmify alarms at different times
3. **Test Regularly**: Verify alarm works every week
4. **Monitor App**: Check Alarmify is running before sleeping

### Troubleshooting Connectivity

**Spotty Internet**:
- Spotify credentials cached (works offline after initial login)
- Playlist data cached
- But playback **requires** internet

**Spotify Connection Lost**:
- Re-authenticate: Click "Login to Spotify" again
- Delete `.cache` file and restart
- Check [Spotify Status](https://status.spotify.com/)

## Troubleshooting

### Quick Diagnosis Checklist

Before diving into specific issues, check these common points:

- [ ] Alarmify application is running (not closed)
- [ ] Computer is not in sleep/hibernate mode
- [ ] Internet connection is active
- [ ] Spotify Premium account is active
- [ ] At least one Spotify device is active
- [ ] Credentials are correctly entered in Settings
- [ ] Alarm appears in "Manage Alarms" list

### Common Issues & Solutions

#### Issue: Alarm Doesn't Trigger

**Symptoms**: Scheduled alarm time passes but nothing happens.

**Solutions**:

1. **Check Application Status**:
   ```
   - Is Alarmify window open? (Check taskbar/dock)
   - Not minimized to tray (current version doesn't support tray)
   - Check Task Manager/Activity Monitor for `python` process
   ```

2. **Verify Alarm is Scheduled**:
   - Click "Manage Alarms"
   - Confirm alarm appears in list with correct time
   - Time format is HH:MM (24-hour)

3. **Active Device Required**:
   - Open Spotify on any device
   - Play and pause a song
   - Device shows as "active" in Spotify app

4. **Check Console for Errors**:
   - Terminal/PowerShell window shows Alarmify output
   - Look for error messages at alarm time
   - Common: "No active device available"

#### Issue: "No active device" Error

**Symptoms**: Error message appears in console or alarm fails silently.

**Solutions**:

1. **Activate a Device**:
   ```
   Open Spotify → Play any song → Pause after 2 seconds
   Device remains active for ~15-30 minutes
   ```

2. **Use Desktop App**:
   - Mobile devices may go inactive when locked
   - Desktop app stays active longer
   - Keep Spotify running in background

3. **Check Spotify Connect**:
   - Open Spotify → Click Devices icon (bottom-right)
   - Should show available devices
   - Select the one you want alarm to use

4. **Restart Spotify**:
   - Completely quit Spotify app
   - Reopen and play a song
   - Try alarm again

#### Issue: Volume Control Doesn't Work

**Symptoms**: Alarm plays but at wrong volume, ignoring slider setting.

**Solutions**:

1. **Check Device Compatibility**:
   - Not all devices support API volume control
   - Test: Manually change volume in Spotify app
   - If that works, device should support API control

2. **Use System Volume**:
   - Set your computer/device volume manually before bed
   - Disable any volume normalization in Spotify settings

3. **Try Different Device**:
   - Desktop apps have better volume API support
   - Mobile apps usually work
   - Web players may not support it

#### Issue: Playlists Don't Load

**Symptoms**: Empty playlist list after authentication.

**Solutions**:

1. **Re-Authenticate**:
   ```
   Click "Login to Spotify" button
   Complete OAuth flow again
   Playlists should load automatically
   ```

2. **Check Permissions**:
   - During OAuth, ensure all permissions granted
   - Specifically: `playlist-read-private`
   - Re-authenticate and carefully review permissions

3. **Verify Playlists Exist**:
   - Open Spotify app/web player
   - Confirm you actually have playlists
   - Created playlists vs. followed playlists both work

4. **Clear Cache**:
   ```bash
   # In Alarmify directory
   rm .cache  # Linux/Mac
   del .cache  # Windows
   # Then re-authenticate
   ```

#### Issue: Images Not Loading

**Symptoms**: Playlists show but cover art is missing (gray boxes).

**Solutions**:

1. **Wait**: Images load asynchronously in background (5-10 seconds)

2. **Check Internet**: Slow connection delays image downloads

3. **Firewall/Antivirus**: May block image downloads from Spotify CDN
   - Add exception for Alarmify
   - Allow Python through firewall

4. **Some Playlists Have No Images**: This is normal
   - User-created playlists without custom artwork
   - Shows gray placeholder

#### Issue: Authentication Fails

**Symptoms**: Browser opens but callback fails, or error during login.

**Solutions**:

1. **Check Redirect URI**:
   ```
   Settings: http://localhost:8888/callback
   Dashboard: http://localhost:8888/callback
   Must match EXACTLY (including port)
   ```

2. **Port in Use**:
   ```powershell
   # Windows: Check what's using port 8888
   netstat -ano | findstr :8888
   # Kill process or use different port
   ```

3. **Firewall Blocking**:
   - Temporarily disable firewall to test
   - Add exception for Python on port 8888

4. **Browser Issues**:
   - Try different browser (Chrome, Firefox, Edge)
   - Clear browser cache and cookies
   - Disable browser extensions temporarily

#### Issue: Application Crashes

**Symptoms**: Alarmify window closes unexpectedly or freezes.

**Solutions**:

1. **Check Console Output**:
   - Look for Python stack trace
   - Note error message for reporting

2. **Update Dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Python Version**:
   ```bash
   python --version  # Should be 3.10+
   ```

4. **Corrupted Installation**:
   ```bash
   # Recreate virtual environment
   rm -rf .venv  # or rmdir /s .venv on Windows
   python -m venv .venv
   # Activate and reinstall
   pip install -r requirements.txt
   ```

### Getting Help

If issues persist after trying troubleshooting steps:

1. **Gather Information**:
   - Error messages from console
   - Steps to reproduce the issue
   - OS and Python version
   - Screenshots if relevant

2. **Check Existing Issues**:
   - Search repository issues
   - Might already be reported/solved

3. **Create New Issue**:
   - Use bug report template
   - Include all gathered information
   - Be specific and detailed

4. **Community Help**:
   - Ask in discussions section
   - Other users may have solutions
   - Maintainers monitor regularly

## FAQ

### General Questions

**Q: Do I need Spotify Premium?**
A: Yes, absolutely. Spotify's playback control API only works with Premium accounts. Free accounts cannot be controlled programmatically.

**Q: Can I use Alarmify without internet?**
A: Partially. After initial authentication, credentials are cached. But playback requires internet since it streams from Spotify.

**Q: Does Alarmify work on mobile devices?**
A: Not directly. Alarmify is a desktop application. However, it can trigger playback on mobile devices via Spotify Connect.

**Q: Is my Spotify data secure?**
A: Yes. Alarmify uses official OAuth 2.0 authentication. Your password is never stored. Credentials are saved locally in `.env` file only.

**Q: Can multiple people use one installation?**
A: Not simultaneously. Alarmify authenticates with one Spotify account at a time. Each user needs their own installation or account switching.

### Feature Questions

**Q: Can I set different alarms for different days?**
A: Currently, alarms repeat daily. Day-specific alarms are a planned feature. Workaround: Enable/disable alarms manually.

**Q: Does Alarmify support snooze?**
A: Not yet. This is a planned feature. Current workaround: Set multiple alarms 10 minutes apart.

**Q: Can I fade in the volume gradually?**
A: Not currently. Fade-in is a planned enhancement. Volume is set immediately when alarm triggers.

**Q: Will Alarmify run in system tray?**
A: Not in the current version. System tray support is planned for future release.

**Q: Can I use local music files instead of Spotify?**
A: No. Alarmify is specifically designed for Spotify integration. For local files, consider alternative alarm clock applications.

**Q: Does it work with Spotify Family accounts?**
A: Yes, as long as your specific account has Premium. Each family member would set up their own Alarmify installation.

### Technical Questions

**Q: How do I update Alarmify?**
A: 
```bash
git pull origin main  # If using git
pip install --upgrade -r requirements.txt
```

**Q: Can I run Alarmify as a service/daemon?**
A: Not officially supported yet. It requires the GUI to run. Headless mode is planned.

**Q: What data does Alarmify collect?**
A: None. Everything runs locally. No telemetry, analytics, or data collection. Your credentials never leave your computer.

**Q: Why does Alarmify need so many Spotify permissions?**
A:
- `user-library-read`: Access your playlists
- `user-read-playback-state`: Check active device
- `user-modify-playback-state`: Play music, set volume
- `playlist-read-private`: Access private playlists

All necessary for core functionality.

**Q: Can I contribute to Alarmify development?**
A: Absolutely! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines. Contributions welcome!

**Q: Is Alarmify open source?**
A: Check the repository license. If open source, you can view, modify, and distribute the code per license terms.

### Comparison Questions

**Q: How is this different from Spotify's built-in alarm?**
A: Spotify mobile app has sleep timer and car mode, but no desktop alarm clock feature. Alarmify fills this gap with:
- Desktop support
- Multiple alarms
- Custom volume per alarm
- Always-on scheduling

**Q: Why not just use my phone alarm?**
A: You can! Alarmify is for people who:
- Want to wake up to Spotify playlists
- Prefer desktop control
- Need multiple simultaneous alarms
- Like customization options

**Q: Alternatives to Alarmify?**
A:
- **Phone alarms**: Simple but limited Spotify integration
- **Smart speakers**: "Alexa, wake me at 7am with playlist X"
- **cron + spotify-cli**: Technical, requires scripting knowledge
- **Commercial apps**: Often paid, closed source

Alarmify is free, open source, and Spotify-focused.

## Screenshots

### Main Application Window

![Main Window - Authenticated](screenshots/main-window-full.png)
*Main interface showing authenticated status, playlist browser with cover art, time picker, volume control, and management buttons*

### Authentication Flow

![Settings Configuration](screenshots/settings-filled.png)
*Settings dialog with Spotify credentials entered (Client Secret masked for security)*

![Spotify Authorization Page](screenshots/spotify-auth-browser.png)
*Browser showing Spotify's permission request page during OAuth flow*

![Authentication Success](screenshots/auth-success.png)
*Browser confirmation that authentication completed successfully*

### Alarm Management

![Alarm Confirmation](screenshots/set-alarm-dialog.png)
*Confirmation dialog showing alarm details: time, playlist, and volume*

![Alarm Manager Window](screenshots/alarm-manager-multiple.png)
*Alarm Manager displaying multiple scheduled alarms with different settings*

### Playlist Features

![Playlist Browser](screenshots/playlist-list-scrolling.png)
*Scrollable playlist list with cover art thumbnails and metadata*

![Loading State](screenshots/playlist-loading.png)
*Playlists loading with placeholder images (before thumbnails download)*

## Appendix

### Keyboard Shortcuts

Currently, Alarmify doesn't have custom keyboard shortcuts. Standard Qt shortcuts apply:

- `Tab`: Navigate between fields
- `Enter`: Activate focused button
- `Escape`: Close dialog windows
- `Arrow Keys`: Navigate lists

### Configuration Files

**`.env`** (Project root)
```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

**`.cache`** (Project root)
- Created automatically by Spotipy
- Contains OAuth tokens
- Deleted to force re-authentication

### File Structure for Users

```
alarmify/
├── main.py                 # Launch this to start app
├── gui.py                  # GUI code (don't modify)
├── alarm.py                # Alarm logic (don't modify)
├── spotify_api/            # API wrapper (don't modify)
├── .env                    # Your credentials (YOU configure)
├── .cache                  # OAuth tokens (auto-generated)
├── requirements.txt        # Dependencies list
└── docs/                   # Documentation you're reading
```

### Environment Variables

You can override settings with environment variables:

```bash
# Example: Different redirect port
export SPOTIPY_REDIRECT_URI=http://localhost:9999/callback

# Custom scope (advanced)
export SPOTIPY_SCOPE=user-library-read,user-modify-playback-state
```

### Spotify API Rate Limits

Spotify imposes rate limits on API calls:
- ~180 calls per minute typical limit
- Alarmify uses minimal calls:
  - 1 call to authenticate
  - 1-2 calls to load playlists
  - 2 calls per alarm trigger (set volume + play)

Normal usage won't hit rate limits. If you do:
- Error messages will indicate rate limiting
- Wait 60 seconds and retry
- Don't set hundreds of alarms simultaneously

### Logs and Debugging

**Console Output**:
- Launch from terminal to see logs
- Errors print to console in real-time
- Useful for troubleshooting

**Enable Debug Mode** (future feature):
```bash
export ALARMIFY_DEBUG=1
python main.py
```

### Privacy and Security

**What's Stored Locally**:
- Spotify API credentials (`.env`)
- OAuth access/refresh tokens (`.cache`)
- No browsing history, playback data, or personal info

**What's Sent to Spotify**:
- API calls for playlists, devices, playback control
- Standard OAuth authentication
- Same as using Spotify app

**Security Best Practices**:
- Don't share `.env` file
- Don't commit credentials to version control
- Revoke app access in Spotify settings if compromised
- Keep Python and dependencies updated

### Resources

**Official Documentation**:
- [Spotify Web API Docs](https://developer.spotify.com/documentation/web-api/)
- [Spotipy Library Docs](https://spotipy.readthedocs.io/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)

**Community**:
- [Alarmify Repository](../../)
- [Issue Tracker](../../issues)
- [Discussions](../../discussions)

**Related Projects**
- [Spotipy](https://github.com/plamere/spotipy) - Spotify API wrapper
- [spotify-player](https://github.com/aome510/spotify-player) - Terminal Spotify client
- [spotifyd](https://github.com/Spotifyd/spotifyd) - Lightweight Spotify daemon

---

**Thank you for using Alarmify!** 🎵⏰

If you find this guide helpful, please star the repository. For issues or suggestions, open an issue on GitHub.

*Last Updated: December 2024*
