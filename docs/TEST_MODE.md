# Test Mode for Non-Premium Users

## 🧪 Testing Without Spotify Premium

Since you don't have Premium yet, here's how to test Alarmify features.

---

## ✅ Current Test Options

### 1. **Mock Mode** (Recommended)
Test all features without real Spotify API calls.

### 2. **Free Account Testing**
Test authentication and UI with free account.

### 3. **Premium Trial**
Use Spotify's 1-month free trial.

---

## 🔧 Implementation: Mock Mode

### What It Does
- Simulates Spotify API responses
- Tests all UI features
- No real API calls
- No Premium required

### Features Testable
- ✅ UI/UX
- ✅ Alarm scheduling
- ✅ Playlist browsing (mock data)
- ✅ Device selection (mock)
- ✅ Volume control (mock)
- ✅ Error handling
- ✅ All workflows

### Features NOT Testable
- ❌ Real playback
- ❌ Real device control
- ❌ Real authentication

---

## 🚀 Quick Implementation

### Step 1: Add Test Mode Flag

```python
# In main.py or config
TEST_MODE = os.getenv('ALARMIFY_TEST_MODE', 'False').lower() == 'true'
```

### Step 2: Mock Spotify API

```python
# spotify_api/mock_spotify.py
class MockSpotifyAPI:
    def is_authenticated(self):
        return True
    
    def is_premium_user(self):
        return False  # or True for testing
    
    def get_playlists_detailed(self):
        return [
            {
                'name': 'Test Playlist 1',
                'id': 'test1',
                'uri': 'spotify:playlist:test1',
                'track_count': 50,
                'image_url': 'https://via.placeholder.com/300',
                'owner': 'Test User'
            },
            # ... more mock playlists
        ]
    
    def get_devices(self):
        return [
            {
                'id': 'device1',
                'name': 'Test Device',
                'type': 'Computer',
                'is_active': True
            }
        ]
    
    def play_playlist_by_uri(self, uri):
        print(f"[MOCK] Would play: {uri}")
        return True
```

### Step 3: Use Mock in Test Mode

```python
# In gui.py
if TEST_MODE:
    from spotify_api.mock_spotify import MockSpotifyAPI
    self.spotify_api = MockSpotifyAPI()
else:
    self.spotify_api = ThreadSafeSpotifyAPI()
```

---

## 📋 Test Scenarios

### Scenario 1: UI Testing
```bash
# Set test mode
export ALARMIFY_TEST_MODE=true
python main.py

# Test:
- Login flow (mock)
- Playlist browsing
- Alarm setting
- Device selection
- All UI interactions
```

### Scenario 2: Free Account Testing
```bash
# Use real Spotify (free account)
# Test:
- Authentication works
- Playlist loading
- UI features
- Error messages (Premium required)
```

### Scenario 3: Premium Trial
```bash
# Sign up for 1-month free trial
# Test:
- Full functionality
- Real playback
- All features
```

---

## 🎯 Recommended Approach

### For Development (Now)
1. **Use Mock Mode**
   - Fast iteration
   - No API limits
   - Test all features
   - No cost

2. **Add Mock Data**
   - Realistic playlists
   - Multiple devices
   - Various scenarios

### For Testing (Before Launch)
1. **Get Premium Trial**
   - 1 month free
   - Test real features
   - Verify everything works

2. **Test with Free Account**
   - Verify error handling
   - Test Premium detection
   - Check user experience

---

## 🔧 Quick Start: Test Mode

### Enable Test Mode
```bash
# Windows PowerShell
$env:ALARMIFY_TEST_MODE="true"
python main.py

# Linux/Mac
export ALARMIFY_TEST_MODE=true
python main.py
```

### Or in Code
```python
# main.py
import os
os.environ['ALARMIFY_TEST_MODE'] = 'true'
```

---

## 📝 Mock Data Examples

### Mock Playlists
```python
MOCK_PLAYLISTS = [
    {
        'name': 'Morning Energy',
        'id': 'morning1',
        'uri': 'spotify:playlist:morning1',
        'track_count': 45,
        'image_url': 'https://via.placeholder.com/300/1DB954/ffffff?text=Morning',
        'owner': 'You'
    },
    {
        'name': 'Chill Vibes',
        'id': 'chill1',
        'uri': 'spotify:playlist:chill1',
        'track_count': 120,
        'image_url': 'https://via.placeholder.com/300/FF6B6B/ffffff?text=Chill',
        'owner': 'You'
    },
    # ... more
]
```

### Mock Devices
```python
MOCK_DEVICES = [
    {
        'id': 'desktop1',
        'name': 'Your Computer',
        'type': 'Computer',
        'is_active': True,
        'volume_percent': 50
    },
    {
        'id': 'phone1',
        'name': 'Your Phone',
        'type': 'Smartphone',
        'is_active': False,
        'volume_percent': 80
    }
]
```

---

## ✅ Testing Checklist

### UI/UX Testing (Mock Mode)
- [ ] Login flow
- [ ] Playlist browsing
- [ ] Alarm setting
- [ ] Device selection
- [ ] Volume control
- [ ] Alarm management
- [ ] Settings dialog
- [ ] Error messages
- [ ] Responsive design
- [ ] Animations

### Functional Testing (Free Account)
- [ ] Authentication
- [ ] Playlist loading
- [ ] Premium detection
- [ ] Error handling
- [ ] Device detection

### Full Testing (Premium Trial)
- [ ] Real playback
- [ ] Volume control
- [ ] Device switching
- [ ] Alarm triggering
- [ ] All features

---

## 🎯 Action Plan

**Now (2025 Start):**
1. [ ] Implement mock mode
2. [ ] Add mock data
3. [ ] Test all UI features
4. [ ] Iterate quickly

**Before Launch:**
1. [ ] Get Premium trial
2. [ ] Test real features
3. [ ] Verify everything works
4. [ ] Fix any issues

**At Launch:**
1. [ ] Premium required (clear messaging)
2. [ ] Free account: Show upgrade prompt
3. [ ] Premium account: Full features

---

**Last Updated:** December 23, 2024
**Status:** Implementation Guide
**Priority:** High (for development)

