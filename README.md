# Alarmify

Alarmify lets you schedule Spotify playlists as alarms. Wake up to your favorite music by selecting a playlist, setting a time, and adjusting the volume.

## Features

- **Playlist Thumbnails**: View playlist cover images, track counts, and owner names
- **Authentication Status**: See your connection state and username in the UI header
- **Alarm Management**: View, track, and delete scheduled alarms via the Manage Alarms dialog
- **Volume Control**: Set playback volume (0-100%) for each alarm
- **Modern Dark Theme**: Spotify-inspired UI with dark background and green accents

## Quick Windows Setup

1. Install Python 3.10+ and ensure `python` is on the PATH.
2. Open PowerShell in the project folder `Alarmify`.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Spotify Developer Setup

1. Create an app at the Spotify Developer Dashboard: https://developer.spotify.com/dashboard/applications
2. Add a Redirect URI to your app settings. For local testing use `http://localhost:8888/callback`.

## Using the App

1. Run the app:

```powershell
python main.py
```

2. Click the gear icon in the header, enter your Spotify `Client ID`, `Client Secret`, and `Redirect URI`, then click Save.
3. Click `Login to Spotify`. Your browser will open to Spotify's consent screen. After authorizing, the app will capture the authorization code automatically.
4. Playlists will appear in the left pane with thumbnails and track counts. Select one.
5. Set the alarm time using the time picker and adjust volume with the slider.
6. Click `Set Alarm` to schedule playback.
7. Click `Manage Alarms` to view or delete scheduled alarms.

## Project Structure

```
Alarmify/
├── main.py              # Entry point
├── gui.py               # PyQt5 GUI with all UI components
├── alarm.py             # Alarm scheduling and management
├── spotify_api/
│   └── spotify_api.py   # Spotify Web API wrapper
├── tests/
│   ├── test_alarm.py    # Alarm module tests
│   └── test_spotify_api.py  # API module tests
├── requirements.txt     # Python dependencies
└── spotify_style.qss    # Qt stylesheet for dark theme
```

## Running Tests

```powershell
python -m pytest tests/ -v
```

## Notes

- The app starts a short-lived local HTTP server to capture the OAuth redirect; make sure the redirect URI host/port are free and match your Spotify app settings.
- Spotify Premium is required for playback control features.
- Instead of using the Settings dialog, you can set environment variables manually:

```powershell
$env:SPOTIPY_CLIENT_ID = 'your_client_id'
$env:SPOTIPY_CLIENT_SECRET = 'your_client_secret'
$env:SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Spotify credentials not set" | Open Settings and enter your API credentials |
| Playlist images not loading | Check internet connection; images load in background |
| "No active device" error | Open Spotify on a device first, then set the alarm |
| OAuth redirect fails | Ensure the redirect URI matches your Spotify app settings exactly |

## License

See LICENSE file for details.
