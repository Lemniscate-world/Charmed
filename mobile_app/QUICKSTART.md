# Alarmify Mobile - Quick Start Guide

Get the mobile app running in 5 minutes.

## Prerequisites

- Flutter SDK 3.0+ installed
- Android Studio or VS Code with Flutter extension
- Alarmify desktop app (optional for full sync testing)

## Quick Setup

### 1. Install Dependencies

```bash
cd mobile_app
flutter pub get
```

### 2. Generate Code

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### 3. Run the App

**Option A: Android Emulator**
```bash
# Start emulator from Android Studio, then:
flutter run
```

**Option B: iOS Simulator** (macOS only)
```bash
open -a Simulator
flutter run
```

**Option C: Web** (for quick testing)
```bash
flutter run -d chrome
```

## First Run

1. **Create Account**:
   - App opens to login screen
   - Tap "Don't have an account? Sign up"
   - Enter email: `test@example.com`
   - Password: `password123`
   - Tap "Create Account"

2. **Explore**:
   - Tap **+** button to create alarm
   - Set time, days, volume
   - Tap **Save**
   - Toggle alarm on/off with switch

## Testing Cloud Sync

### Option 1: Desktop Integration (Full Feature)

1. **Setup Desktop App**:
   ```bash
   # In main Alarmify directory
   python main.py
   ```

2. **Create Account on Desktop**:
   - Click "☁ Cloud Sync"
   - Register with same credentials as mobile
   - Create some test alarms

3. **Start Local API Server**:
   ```bash
   # Create simple Flask server (see SETUP_GUIDE.md)
   python cloud_sync_server.py
   ```

4. **Mobile App**:
   - Login with same credentials
   - Alarms should sync from desktop
   - Changes on either device sync automatically

### Option 2: Standalone (Mock Data)

Without desktop app, the mobile app works standalone:
- Creates alarms locally
- Stores in device storage
- Syncs when API available

## Common Commands

```bash
# Clean build
flutter clean && flutter pub get

# Hot reload (during development)
# Press 'r' in terminal while app running

# Hot restart
# Press 'R' in terminal

# Run tests
flutter test

# Analyze code
flutter analyze

# Build release
flutter build apk --release    # Android
flutter build ios --release    # iOS
```

## Project Structure Overview

```
lib/
├── main.dart              # Entry point
├── models/                # Data models
├── services/              # API & storage
├── providers/             # State management
├── screens/               # UI screens
├── widgets/               # Reusable widgets
└── theme/                 # Design system
```

## Key Files to Know

- **main.dart**: App initialization and navigation
- **cloud_sync_service.dart**: API integration (change baseUrl here)
- **app_theme.dart**: Customize colors and styles
- **pubspec.yaml**: Dependencies and assets

## Troubleshooting

### "Cannot connect to server"

**For Android Emulator**:
```dart
// In lib/services/cloud_sync_service.dart
baseUrl: 'http://10.0.2.2:5000/api'
```

**For iOS Simulator**:
```dart
baseUrl: 'http://localhost:5000/api'
```

**For Real Device**:
```dart
baseUrl: 'http://YOUR_COMPUTER_IP:5000/api'
```

### "JSON serialization error"

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### "Build errors"

```bash
flutter clean
flutter pub get
flutter run
```

## Next Steps

1. **Customize Design**: Edit `lib/theme/app_colors.dart`
2. **Add Features**: See `README.md` for roadmap
3. **Deploy**: Follow `SETUP_GUIDE.md` deployment section
4. **Integrate Desktop**: See `SETUP_GUIDE.md` integration section

## Resources

- **Full Documentation**: See `README.md`
- **Setup Guide**: See `SETUP_GUIDE.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Desktop Integration**: See `CLOUD_SYNC_IMPLEMENTATION.md` in parent directory

## Development Tips

### VS Code Extensions

- Flutter
- Dart
- Flutter Widget Snippets
- Pubspec Assist

### Android Studio Plugins

- Flutter
- Dart

### Useful Shortcuts

**VS Code/Android Studio**:
- `Ctrl/Cmd + .` - Show code actions
- `Alt + Enter` - Quick fixes
- `Shift + F10` - Run
- `Ctrl + F9` - Build

### Debug Tools

```dart
// Add debug prints
print('Debug: $variable');

// Use debugger
debugger();

// Flutter DevTools
flutter pub global activate devtools
flutter pub global run devtools
```

## Sample Test Account

For quick testing without desktop:

```
Email: test@alarmify.com
Password: testpassword123
```

(Creates local-only account, no cloud sync)

## Quick Demo

```bash
# Complete demo in one go:
cd mobile_app
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
flutter run -d chrome

# Then in app:
# 1. Sign up with test credentials
# 2. Create alarm for 2 minutes from now
# 3. Enable alarm
# 4. Explore settings
```

## Support

Questions? Check:
1. `README.md` - Full documentation
2. `SETUP_GUIDE.md` - Detailed setup
3. GitHub Issues - Report bugs

---

**Quick Start Version**: 1.0  
**Last Updated**: December 2024

Happy coding! 🚀
