# Alarmify Mobile - Flutter Companion App

Mobile companion app for Alarmify desktop alarm clock. Wake up to your Spotify music with seamless cloud sync across all your devices.

## Features

- **Alarm Management**: Create, edit, and delete alarms with full control
- **Cloud Sync**: Seamlessly sync alarms with desktop app via cloud
- **Charm-Inspired Design**: Beautiful, minimal UI following the Charm design system
- **Spotify Integration**: Set your favorite playlists as alarm sounds (via desktop)
- **Smart Scheduling**: Set recurring alarms for specific days
- **Volume Control**: Adjust alarm volume with optional fade-in
- **Multi-Device**: Manage alarms across Windows, Mac, Linux, iOS, and Android

## Design System

The app implements a Charm-inspired design aesthetic:

- **Deep Black Background** (#0A0A0A): Minimal, distraction-free interface
- **Spotify Green Accent** (#1DB954): Vibrant, recognizable branding
- **Glassmorphism**: Subtle frosted glass effects on cards
- **Smooth Animations**: 250ms transitions with spring physics
- **Typography**: Inter for UI, JetBrains Mono for time display

## Project Structure

```
mobile_app/
├── lib/
│   ├── main.dart                    # App entry point
│   ├── models/                      # Data models
│   │   ├── alarm.dart              # Alarm model
│   │   ├── user.dart               # User & auth models
│   │   └── device.dart             # Device model
│   ├── services/                    # Business logic
│   │   ├── cloud_sync_service.dart # Cloud API integration
│   │   └── storage_service.dart    # Local persistence
│   ├── providers/                   # State management
│   │   ├── auth_provider.dart      # Authentication state
│   │   └── alarm_provider.dart     # Alarm list state
│   ├── screens/                     # UI screens
│   │   ├── login_screen.dart       # Login/register
│   │   ├── home_screen.dart        # Alarm list
│   │   ├── alarm_edit_screen.dart  # Create/edit alarm
│   │   └── settings_screen.dart    # Settings & sync
│   ├── widgets/                     # Reusable widgets
│   │   ├── glass_card.dart         # Glassmorphism card
│   │   ├── gradient_button.dart    # Primary action button
│   │   ├── alarm_card.dart         # Alarm display card
│   │   ├── day_selector.dart       # Day of week picker
│   │   └── sync_indicator.dart     # Sync status banner
│   └── theme/                       # Design system
│       ├── app_colors.dart         # Color palette
│       └── app_theme.dart          # Theme configuration
├── assets/                          # Static assets
│   ├── fonts/                       # Custom fonts
│   └── images/                      # Images & icons
├── pubspec.yaml                     # Dependencies
└── README.md                        # This file
```

## Getting Started

### Prerequisites

- Flutter SDK 3.0.0 or higher
- Dart SDK 3.0.0 or higher
- Android Studio / Xcode (for mobile development)
- Alarmify desktop app running with cloud sync enabled

### Installation

1. **Install Flutter dependencies**:
   ```bash
   cd mobile_app
   flutter pub get
   ```

2. **Generate JSON serialization code**:
   ```bash
   flutter pub run build_runner build --delete-conflicting-outputs
   ```

3. **Run the app**:
   ```bash
   # iOS
   flutter run -d ios
   
   # Android
   flutter run -d android
   
   # Web (for testing)
   flutter run -d chrome
   ```

### Configuration

The app connects to the Alarmify cloud sync backend. By default, it uses `http://localhost:5000/api` for development. For production:

1. Update `baseUrl` in `lib/services/cloud_sync_service.dart`
2. Ensure desktop app is running with cloud sync enabled
3. Use the same account credentials on both apps

## Usage

### First Time Setup

1. **Create Account**:
   - Open the app
   - Tap "Don't have an account? Sign up"
   - Enter email, password, and optional display name
   - Tap "Create Account"

2. **Sync Alarms**:
   - The app automatically syncs with cloud on first login
   - Any alarms from desktop app will appear in the mobile app
   - New alarms created on mobile sync back to desktop

### Creating Alarms

1. Tap the **+** button on home screen
2. Set alarm time by tapping the time display
3. Select days for recurring alarms
4. Choose playlist (requires Spotify integration on desktop)
5. Adjust volume and fade-in settings
6. Tap **Save**

### Editing Alarms

1. Tap any alarm card on home screen
2. Modify settings as needed
3. Tap **Save** to sync changes

### Managing Sync

1. Open **Settings** from home screen
2. Toggle **Auto Sync** to enable/disable automatic syncing
3. Set **Sync Interval** (15, 30, 60, or 120 minutes)
4. Manually sync anytime with **Sync Now** button

## Cloud Sync API

The mobile app integrates with the desktop cloud sync system:

### Authentication Endpoints

- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - User authentication
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/user` - Get current user info

### Sync Endpoints

- `POST /api/sync/alarms/backup` - Upload alarms to cloud
- `GET /api/sync/alarms/restore` - Download alarms from cloud
- `POST /api/sync/alarms/sync` - Bi-directional sync with conflict resolution

### Device Endpoints

- `POST /api/devices/register` - Register new device
- `GET /api/devices` - List all registered devices

## State Management

The app uses **Provider** for state management:

### AuthProvider

Manages user authentication state:
- Login/logout
- Token management
- User session persistence

### AlarmProvider

Manages alarm list state:
- CRUD operations
- Cloud sync
- Auto-sync scheduling

## Data Models

### Alarm

```dart
{
  id: String,
  time: String,              // HH:MM format
  playlistName: String,
  playlistUri: String,       // Spotify URI
  volume: int,               // 0-100
  fadeInEnabled: bool,
  fadeInDuration: int,       // minutes
  days: List<String>,        // Active days
  isActive: bool,
  deviceId: String?,
  lastModified: DateTime?,
  createdAt: DateTime?
}
```

### User

```dart
{
  userId: String,
  email: String,
  displayName: String,
  createdAt: DateTime?,
  lastLogin: DateTime?
}
```

## Customization

### Changing Colors

Edit `lib/theme/app_colors.dart`:

```dart
static const Color accent = Color(0xFF1DB954);  // Your color
```

### Adjusting Animations

Edit `lib/theme/app_theme.dart`:

```dart
static const Duration animationNormal = Duration(milliseconds: 250);
```

### Custom Fonts

1. Add font files to `assets/fonts/`
2. Update `pubspec.yaml`:
   ```yaml
   fonts:
     - family: YourFont
       fonts:
         - asset: assets/fonts/YourFont-Regular.ttf
   ```
3. Update theme in `lib/theme/app_theme.dart`

## Building for Production

### Android

```bash
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk

# Or build app bundle for Play Store
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

### iOS

```bash
flutter build ios --release
# Open Xcode to sign and archive
```

## Testing

```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Run specific test
flutter test test/widget_test.dart
```

## Troubleshooting

### Sync Not Working

1. Check network connectivity
2. Verify desktop app is running with cloud sync enabled
3. Ensure using same account on both apps
4. Check Settings > Sync Status

### Build Errors

1. Clean build: `flutter clean`
2. Regenerate code: `flutter pub run build_runner build --delete-conflicting-outputs`
3. Get dependencies: `flutter pub get`

### JSON Serialization Errors

Run code generation:
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

## Dependencies

Key packages used:

- **provider** (^6.1.1) - State management
- **http** (^1.1.2) - Network requests
- **shared_preferences** (^2.2.2) - Local storage
- **flutter_secure_storage** (^9.0.0) - Secure token storage
- **json_annotation** (^4.8.1) - JSON serialization
- **intl** (^0.19.0) - Date/time formatting
- **uuid** (^4.3.3) - UUID generation

## Roadmap

### Near Term

- [ ] Spotify playlist browser integration
- [ ] Push notifications for alarm triggers
- [ ] Alarm preview/test
- [ ] Dark/light theme toggle

### Future

- [ ] Widget support for quick alarm toggle
- [ ] Smart wake-up with sleep cycle detection
- [ ] Statistics and insights
- [ ] Calendar integration
- [ ] Wearable support

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

See main Alarmify LICENSE file.

## Credits

- **Design Inspiration**: Charm CLI design system
- **Icons**: Material Design Icons
- **Fonts**: Inter, JetBrains Mono (when configured)

## Support

For issues and questions:
- Check desktop app CLOUD_SYNC_IMPLEMENTATION.md
- Review PRODUCT_ROADMAP.md for planned features
- Open issue on GitHub repository

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Status**: MVP Complete
