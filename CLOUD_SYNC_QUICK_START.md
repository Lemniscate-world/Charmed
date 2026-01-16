# Cloud Sync Quick Start Guide

## What is Cloud Sync?

Cloud Sync allows you to backup your alarms and settings to the cloud and synchronize them across multiple devices. Never lose your alarm configurations again!

## Getting Started (5 Minutes)

### Step 1: Create Your Account

1. Open Alarmify
2. Click the **☁ Cloud Sync** button in the main window
3. Click **Create Account**
4. Enter your email and password (min 8 characters)
5. Optionally add a display name
6. Click **Create Account**

### Step 2: First Sync

1. After creating your account, you'll automatically be logged in
2. In the Cloud Sync dialog, click **Sync Now**
3. Your current alarms will be uploaded to the cloud
4. Done! Your data is now backed up

### Step 3: Sync to Another Device

1. Install Alarmify on your second device
2. Click **☁ Cloud Sync**
3. Click **Sign In**
4. Enter the same email and password
5. Click **Sync Now**
6. Your alarms are now on both devices!

## Key Features

### 🔄 Automatic Sync
- Enable "Enable automatic synchronization"
- Choose your preferred interval (15 min - 2 hours)
- Your data syncs automatically in the background

### 🔐 Secure & Private
- Your password is hashed and never stored in plain text
- All data is stored locally with encryption
- JWT tokens for secure authentication

### 📱 Multi-Device Support
- View all your registered devices
- See when each device last synced
- Sync works seamlessly across Windows, Mac, and Linux

### ⚔️ Smart Conflict Resolution
- If you change alarms on multiple devices, Cloud Sync intelligently merges them
- Newest changes win by default
- No data loss!

## Common Use Cases

### Backup Your Alarms
```
1. Click "☁ Cloud Sync"
2. Click "Upload Only"
3. Your alarms are backed up!
```

### Restore from Backup
```
1. Click "☁ Cloud Sync"
2. Click "Download Only"
3. Your alarms are restored!
```

### Keep Devices in Sync
```
1. Enable "Enable automatic synchronization"
2. Your devices stay in sync automatically
```

## Sync Options

- **Sync Now** - Upload and download (merge changes)
- **Upload Only** - Send your local data to cloud (backup)
- **Download Only** - Get data from cloud (restore)

## Tips

✅ **DO:**
- Enable auto-sync for automatic backups
- Sync before making major changes to avoid conflicts
- Check the Devices tab to see all your devices

❌ **DON'T:**
- Share your password with others
- Forget to sync after setting up new alarms on one device

## Troubleshooting

### "Not logged in" error
- Click **☁ Cloud Sync** and sign in again

### Alarms not syncing
- Check that you're logged in
- Try clicking **Sync Now** manually
- Check the sync status in the Status tab

### Forgot password
- Currently no password reset (v1.0)
- Create a new account if needed
- Your old data will remain in your local backup

## Data Privacy

Your data is stored:
- Locally on your computer in `~/.alarmify/`
- In cloud storage (simulated locally in v1.0)
- Never shared with third parties
- You can delete all cloud data anytime in Settings tab

## Need Help?

1. Check the Status tab for sync information
2. View the Devices tab to see registered devices
3. Check the main app logs: **View Logs** button
4. Read the full documentation: `CLOUD_SYNC_IMPLEMENTATION.md`

## What Gets Synced?

✓ Alarm times and playlists
✓ Volume settings
✓ Fade-in configurations
✓ Active days (weekday/weekend settings)
✓ Alarm templates
✓ App settings (theme, notifications)

✗ Spotify authentication (login separately on each device)
✗ Log files
✗ Cache data

## Security

- Passwords hashed with bcrypt (industry standard)
- JWT tokens with expiration
- Local file permissions set to owner-only
- Data integrity verification with checksums

---

**Ready to sync?** Click the **☁ Cloud Sync** button and get started! 🚀
