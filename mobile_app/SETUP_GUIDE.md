# Alarmify Mobile - Setup & Integration Guide

Complete guide to setting up and integrating the Alarmify mobile app with the desktop application.

## Prerequisites

### Development Environment

1. **Flutter SDK 3.0+**
   ```bash
   # Check installation
   flutter --version
   flutter doctor
   ```

2. **IDE Setup** (choose one)
   - Android Studio with Flutter plugin
   - VS Code with Flutter extension
   - IntelliJ IDEA with Flutter plugin

3. **Platform SDKs**
   - **Android**: Android SDK, Android Emulator
   - **iOS**: Xcode 14+ (macOS only), iOS Simulator
   - **Web**: Chrome browser (for testing)

### Desktop App Requirements

1. **Alarmify Desktop** running with cloud sync enabled
2. **Cloud sync configured** following `CLOUD_SYNC_IMPLEMENTATION.md`
3. **User account** created via desktop app

## Installation Steps

### 1. Clone and Setup

```bash
# Navigate to mobile app directory
cd mobile_app

# Install dependencies
flutter pub get

# Verify Flutter setup
flutter doctor
```

### 2. Generate Code

Generate JSON serialization code:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

This creates:
- `lib/models/alarm.g.dart`
- `lib/models/user.g.dart`
- `lib/models/device.g.dart`

### 3. Configure Backend URL

For local development, the default configuration should work:

**File**: `lib/services/cloud_sync_service.dart`

```dart
CloudSyncService({this.baseUrl = 'http://localhost:5000/api'});
```

For production deployment:

```dart
CloudSyncService({this.baseUrl = 'https://your-api-domain.com/api'});
```

### 4. Add Custom Fonts (Optional)

1. Download fonts:
   - Inter: https://fonts.google.com/specimen/Inter
   - JetBrains Mono: https://www.jetbrains.com/lp/mono/

2. Create font directories:
   ```bash
   mkdir -p assets/fonts
   ```

3. Copy font files to `assets/fonts/`:
   - Inter-Regular.ttf
   - Inter-Bold.ttf
   - JetBrainsMono-Regular.ttf
   - JetBrainsMono-Bold.ttf

4. Uncomment font configuration in `pubspec.yaml`

### 5. Run the App

**Android Emulator**:
```bash
# List available devices
flutter devices

# Run on Android
flutter run -d <device-id>
```

**iOS Simulator** (macOS only):
```bash
# Open iOS simulator
open -a Simulator

# Run on iOS
flutter run -d iPhone
```

**Web** (for testing):
```bash
flutter run -d chrome
```

## Integration with Desktop App

### Backend Integration Options

#### Option 1: Local File-Based Sync (Current)

The current implementation uses local file storage matching the desktop app structure:

1. **Desktop app** writes to `~/.alarmify/cloud_data/`
2. **Mobile app** reads from same location (requires network share or sync)
3. **No server** required for MVP

**Limitations**:
- Same device only or manual file sync
- No real-time updates

#### Option 2: REST API Server (Recommended)

Create a simple REST API server to bridge desktop and mobile:

**Tech Stack Options**:
- Flask (Python) - matches desktop tech stack
- Node.js + Express
- FastAPI (Python, modern)

**Example Flask Server**:

```python
# cloud_sync_server.py
from flask import Flask, request, jsonify
from cloud_sync.cloud_auth import CloudAuthManager
from cloud_sync.cloud_sync_api import CloudSyncAPI

app = Flask(__name__)
auth_manager = CloudAuthManager()
sync_api = CloudSyncAPI()

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    success, message, user_id = auth_manager.register(
        data['email'], 
        data['password'], 
        data.get('display_name')
    )
    return jsonify({
        'success': success,
        'message': message,
        'user_id': user_id
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    success, message, access_token, refresh_token = auth_manager.login(
        data['email'],
        data['password']
    )
    
    if success:
        user = auth_manager.get_current_user()
        return jsonify({
            'success': True,
            'message': message,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user
        })
    return jsonify({'success': False, 'message': message})

@app.route('/api/sync/alarms/backup', methods=['POST'])
def backup_alarms():
    data = request.json
    success, message = sync_api.backup_alarms(
        data['user_id'],
        data['alarms'],
        data['device_id']
    )
    return jsonify({'success': success, 'message': message})

@app.route('/api/sync/alarms/restore', methods=['GET'])
def restore_alarms():
    user_id = request.args.get('user_id')
    success, message, alarms = sync_api.restore_alarms(user_id)
    return jsonify({
        'success': success,
        'message': message,
        'alarms': alarms or []
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Run Server**:
```bash
python cloud_sync_server.py
```

**Update Mobile App**:
- iOS Simulator: Use `http://localhost:5000/api`
- Android Emulator: Use `http://10.0.2.2:5000/api`
- Real Device: Use your computer's IP (e.g., `http://192.168.1.100:5000/api`)

#### Option 3: Cloud Service (Production)

For production deployment:

1. **Deploy API** to:
   - AWS Lambda + API Gateway
   - Google Cloud Functions
   - Heroku
   - DigitalOcean App Platform

2. **Database**:
   - PostgreSQL (structured data)
   - MongoDB (flexible schema)
   - Firebase (real-time)

3. **Authentication**:
   - JWT tokens (current)
   - OAuth 2.0
   - Firebase Auth

## Testing the Integration

### 1. Create Account on Desktop

1. Launch desktop Alarmify app
2. Click "☁ Cloud Sync" button
3. Create new account with email/password
4. Create some test alarms

### 2. Login on Mobile

1. Launch mobile app
2. Enter same email/password
3. App should sync and display alarms from desktop

### 3. Test Sync

**Desktop → Mobile**:
1. Add alarm on desktop
2. Click "Sync Now" on desktop
3. Pull to refresh or wait for auto-sync on mobile
4. Alarm should appear on mobile

**Mobile → Desktop**:
1. Add alarm on mobile
2. Auto-sync happens automatically (or tap sync button)
3. Check desktop app - alarm should appear

### 4. Test Conflict Resolution

1. Modify same alarm on both devices while offline
2. Trigger sync
3. System should resolve using "newest wins" strategy

## Network Configuration

### Android Emulator

To connect to localhost on host machine:

```dart
// Use 10.0.2.2 instead of localhost
CloudSyncService({this.baseUrl = 'http://10.0.2.2:5000/api'});
```

### iOS Simulator

Localhost works directly:

```dart
CloudSyncService({this.baseUrl = 'http://localhost:5000/api'});
```

### Real Device

Use your computer's local IP:

```bash
# Find your IP
# macOS/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

```dart
CloudSyncService({this.baseUrl = 'http://192.168.1.100:5000/api'});
```

### Firewall Configuration

Ensure firewall allows incoming connections on port 5000:

**macOS**:
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /usr/local/bin/python3
```

**Windows**:
- Open Windows Defender Firewall
- Add inbound rule for port 5000

**Linux**:
```bash
sudo ufw allow 5000/tcp
```

## Build Configuration

### Android

**File**: `android/app/build.gradle`

```gradle
android {
    defaultConfig {
        applicationId "com.alarmify.mobile"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "1.0.0"
    }
}
```

### iOS

**File**: `ios/Runner/Info.plist`

Add network permissions:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

## Troubleshooting

### Common Issues

#### 1. Cannot Connect to Server

**Error**: Network unreachable

**Solutions**:
- Check server is running: `curl http://localhost:5000/api/health`
- Verify correct URL for your platform (localhost vs 10.0.2.2)
- Check firewall settings
- Use real device IP for physical devices

#### 2. JSON Serialization Errors

**Error**: `type 'Null' is not a subtype of type 'String'`

**Solution**:
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

#### 3. State Not Updating

**Error**: UI doesn't reflect changes

**Solution**:
- Ensure `notifyListeners()` is called in providers
- Check Provider is properly configured in widget tree
- Rebuild app: `flutter run --hot-restart`

#### 4. Build Errors

**Error**: Various build failures

**Solution**:
```bash
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
flutter run
```

### Debug Mode

Enable verbose logging:

**File**: `lib/services/cloud_sync_service.dart`

```dart
// Add debug prints
print('API Request: $url');
print('Response: ${response.body}');
```

## Performance Optimization

### 1. Reduce Network Calls

- Cache responses locally
- Implement smart sync (only changed data)
- Use delta sync for large datasets

### 2. Optimize Build Size

```bash
# Analyze app size
flutter build apk --analyze-size

# Build with optimization
flutter build apk --split-per-abi
```

### 3. Improve Startup Time

- Lazy load providers
- Defer non-critical initialization
- Use splash screen strategically

## Security Considerations

### 1. HTTPS in Production

Always use HTTPS for production:

```dart
CloudSyncService({this.baseUrl = 'https://api.alarmify.com'});
```

### 2. Token Security

Tokens are stored in Flutter Secure Storage:
- Android: KeyStore
- iOS: Keychain

### 3. API Key Management

Never commit API keys to repository:

```dart
// Use environment variables
const apiKey = String.fromEnvironment('API_KEY');
```

## Deployment

### Android Play Store

1. Update version in `pubspec.yaml`
2. Generate signing key
3. Build release:
   ```bash
   flutter build appbundle --release
   ```
4. Upload to Play Console

### iOS App Store

1. Update version in `pubspec.yaml`
2. Build release:
   ```bash
   flutter build ios --release
   ```
3. Open Xcode, archive, and upload

## Monitoring

### Crash Reporting

Integrate Firebase Crashlytics:

```yaml
# pubspec.yaml
dependencies:
  firebase_crashlytics: ^3.4.0
```

### Analytics

Track user behavior:

```yaml
dependencies:
  firebase_analytics: ^10.7.0
```

## Next Steps

1. **Complete Spotify Integration**: Add playlist browser
2. **Push Notifications**: Alert users when alarms trigger
3. **Widget Support**: Quick alarm toggle from home screen
4. **Offline Mode**: Queue sync operations when offline
5. **Real-time Sync**: WebSocket for instant updates

## Support

- Desktop app docs: `CLOUD_SYNC_IMPLEMENTATION.md`
- Roadmap: `docs/PRODUCT_ROADMAP.md`
- Issues: GitHub repository

---

**Last Updated**: December 2024  
**Version**: 1.0.0
