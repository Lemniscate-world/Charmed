# Screenshots Directory

This directory contains screenshots referenced in the user documentation.

## How to Create Screenshots

To complete the documentation, capture the following screenshots of the Alarmify application:

### Required Screenshots

#### 1. Main Window (`main-window.png`)
**What to capture**: The main Alarmify window after successful authentication
- Show authenticated status ("Connected as [Name]") in top-right
- Display several playlists with cover art loaded
- Highlight one playlist as selected
- Show the time picker and volume slider in right panel
- Include both "Login to Spotify" and "Set Alarm" buttons

**How to capture**:
1. Launch Alarmify and authenticate with Spotify
2. Wait for playlists and cover art to load
3. Click on a playlist to select it
4. Take a full window screenshot

**Recommended size**: 1280x800 or actual window size

---

#### 2. Main Window - Full View (`main-window-full.png`)
**What to capture**: Identical to main-window.png but ensure full detail is visible

---

#### 3. Settings Dialog (`settings-dialog.png`)
**What to capture**: The Spotify Settings dialog
- Show all three input fields (Client ID, Client Secret, Redirect URI)
- Leave fields empty or with placeholder text
- Show both "Cancel" and "Save" buttons

**How to capture**:
1. Launch Alarmify
2. Click the gear icon (⚙) in top-right
3. Take screenshot of the dialog

**Recommended size**: 500x400

---

#### 4. Settings Dialog - Filled (`settings-filled.png`)
**What to capture**: Settings dialog with credentials entered
- Client ID field with example value (not real credentials)
- Client Secret showing dots/asterisks (masked)
- Redirect URI with `http://localhost:8888/callback`

**How to capture**:
1. Open Settings dialog
2. Enter example credentials (or use test values)
3. Take screenshot

---

#### 5. Spotify Dashboard (`spotify-dashboard.png`)
**What to capture**: Spotify Developer Dashboard showing app details
- Browser view of developer.spotify.com/dashboard
- Show an example app created for Alarmify
- Display Client ID (you can blur actual values)
- Show "Show Client Secret" button
- Display Redirect URIs section with callback URL

**How to capture**:
1. Visit https://developer.spotify.com/dashboard
2. Create or select an app
3. Capture the app details page
4. (Optional) Blur sensitive information

---

#### 6. Spotify Authorization Page (`spotify-auth-browser.png`)
**What to capture**: Browser showing Spotify OAuth consent page
- Spotify authorization screen asking for permissions
- Show list of scopes being requested
- Display "Agree" or "Cancel" buttons
- Include Spotify branding

**How to capture**:
1. Open Settings dialog and enter credentials
2. Click "Login to Spotify"
3. Browser opens to Spotify authorization
4. Take screenshot before clicking "Agree"

---

#### 7. Authentication Flow (`auth-flow.png`)
**What to capture**: Same as spotify-auth-browser.png or a composite showing the flow

---

#### 8. Authentication Success (`auth-success.png`)
**What to capture**: Browser showing successful auth callback
- Page with "Authentication successful!" message
- Message saying "You can close this window and return to Alarmify"
- URL showing localhost:8888/callback with code parameter

**How to capture**:
1. Complete OAuth flow by clicking "Agree"
2. Browser redirects to localhost callback
3. Quickly capture the success page

---

#### 9. Alarm Manager Dialog (`alarm-manager.png`)
**What to capture**: The Manage Alarms dialog window
- Table with at least 2-3 scheduled alarms
- Columns: Time, Playlist, Volume, Actions
- Each row showing different playlist and volume settings
- Delete buttons in Actions column
- Close button at bottom

**How to capture**:
1. Set 2-3 different alarms with different playlists and volumes
2. Click "Manage Alarms" button
3. Take screenshot of the dialog

**Recommended size**: 600x400

---

#### 10. Alarm Manager - Multiple Alarms (`alarm-manager-multiple.png`)
**What to capture**: Same as alarm-manager.png but with 4-5 alarms to show capacity

---

#### 11. Set Alarm Confirmation (`alarm-confirmation.png` or `set-alarm-dialog.png`)
**What to capture**: Confirmation dialog after clicking "Set Alarm"
- Dialog title "Alarm Set"
- Text showing:
  - "Alarm set for [HH:MM]"
  - "Playlist: [playlist name]"
  - "Volume: [X]%"
- OK button

**How to capture**:
1. Select a playlist
2. Set a time
3. Adjust volume
4. Click "Set Alarm"
5. Capture the confirmation dialog

---

#### 12. Time Picker (`time-picker.png`)
**What to capture**: Close-up of the time input widget
- QTimeEdit showing time like "07:00"
- Up/down spinner arrows visible
- Focus on the time picker in right panel

**How to capture**:
1. Zoom in or crop to show just the "Alarm Time" section
2. Click on time picker to show it's active

---

#### 13. Playlist List - Scrolling (`playlist-list-scrolling.png`)
**What to capture**: The playlist browser with many playlists
- Show scrollbar if list is long
- Multiple playlists visible with varying cover art
- Demonstrates the scrollable nature

**How to capture**:
1. Ensure you have 10+ playlists
2. Capture the left panel showing multiple items

---

#### 14. Playlist Loading State (`playlist-loading.png`)
**What to capture**: Playlists displayed before images fully load
- Show playlists with gray placeholder boxes instead of cover art
- Or capture during the brief loading period

**How to capture**:
1. Clear browser cache if needed
2. Fresh login and immediately capture before images load
3. Or use slow network simulation

---

### Screenshot Guidelines

**Technical Requirements**:
- **Format**: PNG (preferred) or JPG
- **Resolution**: Minimum 1280px width for main window shots
- **Color**: RGB color space
- **Compression**: Moderate (balance quality and file size)

**Content Guidelines**:
- Use example data (not personal playlists if privacy is a concern)
- Ensure text is readable
- Show realistic usage scenarios
- Avoid showing actual Spotify credentials (use placeholders or blur)
- Consistent window styling (same OS, same theme)

**Naming Convention**:
- Use lowercase with hyphens
- Descriptive names matching documentation references
- Example: `main-window.png`, `alarm-manager.png`

**Editing**:
- Crop to remove unnecessary desktop background
- Add subtle drop shadows if desired (optional)
- Annotate with arrows or text if helpful (optional)
- Maintain aspect ratio

### Tools for Capturing

**Windows**:
- Snipping Tool (Win + Shift + S)
- Game Bar (Win + G)
- Greenshot (third-party)

**macOS**:
- Screenshot tool (Cmd + Shift + 4)
- Preview for editing
- CleanShot X (third-party)

**Linux**:
- GNOME Screenshot (PrtSc)
- Flameshot
- Spectacle (KDE)

### After Capturing

1. **Save** screenshots to `docs/screenshots/` directory
2. **Verify** file names match documentation references
3. **Check** that all images are readable and clear
4. **Commit** to repository:
   ```bash
   git add docs/screenshots/*.png
   git commit -m "Add application screenshots to documentation"
   ```

### Optional Enhancements

For professional documentation, consider:

- **Annotations**: Add arrows or text overlays to highlight features
- **Composites**: Create multi-panel images showing workflow steps
- **Animated GIFs**: Show interactions like setting an alarm (use tools like ScreenToGif, LICEcap)
- **Consistent styling**: Use same window theme across all shots

### Example Screenshot Workflow

```bash
# 1. Set up clean environment
python main.py

# 2. Go through each scenario and capture
# - Main window (after auth)
# - Settings dialog
# - Alarm manager
# - etc.

# 3. Edit if needed
# - Crop, resize, annotate

# 4. Save to docs/screenshots/
# - Verify naming matches docs

# 5. Test documentation links
# - Open README.md and USER_GUIDE.md
# - Check that images display correctly
```

## Current Status

⚠️ **Placeholder images referenced in documentation need to be created**

The following screenshots are referenced but not yet captured:
- [ ] main-window.png
- [ ] main-window-full.png
- [ ] settings-dialog.png
- [ ] settings-filled.png
- [ ] spotify-dashboard.png
- [ ] spotify-auth-browser.png
- [ ] auth-flow.png
- [ ] auth-success.png
- [ ] alarm-manager.png
- [ ] alarm-manager-multiple.png
- [ ] set-alarm-dialog.png
- [ ] alarm-confirmation.png
- [ ] time-picker.png
- [ ] playlist-list-scrolling.png
- [ ] playlist-loading.png

To complete the documentation, follow the instructions above to capture each screenshot.

## Questions?

If you're creating screenshots for the project:
- Follow the guidelines above for consistency
- Ask maintainers if you need clarification on what to show
- Submit screenshots via pull request with descriptive commit message

Thank you for contributing to Alarmify documentation! 📸
