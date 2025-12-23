# Zero-Friction Setup Plan

## 🎯 Goal
Reduce setup time from 5-10 minutes to < 2 minutes. Make it as easy as possible for users.

---

## 🔧 Current Friction Points

### 1. Manual API Credential Setup
**Problem:** Users must:
- Go to Spotify Developer Dashboard
- Create an app
- Copy Client ID and Secret
- Paste into Alarmify

**Friction Score:** 8/10 (Very High)

### 2. Redirect URI Configuration
**Problem:** Users must:
- Understand what redirect URI means
- Add exact URI to Spotify dashboard
- Match it in Alarmify

**Friction Score:** 7/10 (High)

### 3. OAuth Flow
**Problem:** Users must:
- Click login
- Authorize in browser
- Return to app

**Friction Score:** 3/10 (Low - this is necessary)

---

## ✅ Solutions

### Solution 1: Embedded OAuth Flow (Recommended)

#### Implementation
1. **Embedded WebView** for OAuth
   - No browser popup
   - Seamless experience
   - Auto-capture callback

2. **Auto-configure Redirect URI**
   - Use `http://127.0.0.1:8888/callback` automatically
   - Pre-fill in settings
   - Show instructions only if needed

3. **One-Click Setup Wizard**
   - First-run tutorial
   - Step-by-step guidance
   - Visual indicators

#### Code Changes Needed
```python
# Use QWebEngineView for embedded OAuth
from PyQt5.QtWebEngineWidgets import QWebEngineView

class OAuthWebView(QWebEngineView):
    def __init__(self, redirect_uri, parent=None):
        super().__init__(parent)
        self.redirect_uri = redirect_uri
        # Monitor URL changes for callback
```

### Solution 2: Browser Extension (Advanced)

#### Implementation
1. **Chrome/Firefox Extension**
   - Extract credentials from browser
   - Auto-fill in Alarmify
   - One-click setup

2. **Benefits**
   - Zero manual entry
   - Most secure
   - Best UX

3. **Drawbacks**
   - Requires extension installation
   - More complex
   - Browser-specific

### Solution 3: Smart Defaults + Wizard

#### Implementation
1. **First-Run Wizard**
   ```
   Step 1: Welcome screen
   Step 2: "Do you have Spotify Premium?" (Yes/No)
   Step 3: "Let's set up your credentials"
      - Option A: "I'll set it up myself" (current flow)
      - Option B: "Guide me through it" (wizard)
   Step 4: OAuth flow
   Step 5: Test alarm setup
   ```

2. **Smart Defaults**
   - Auto-detect redirect URI
   - Pre-fill common values
   - Show help tooltips

3. **Visual Guidance**
   - Screenshots in wizard
   - Highlighted fields
   - Progress indicator

---

## 🚀 Implementation Plan

### Phase 1: Quick Wins (Week 1)

#### 1.1 Auto-Configure Redirect URI
- [ ] Pre-fill `http://127.0.0.1:8888/callback` in settings
- [ ] Show clear instructions in UI
- [ ] Validate format automatically

**Code:**
```python
# In SettingsDialog.__init__
self.redirect_uri.setText('http://127.0.0.1:8888/callback')
self.redirect_uri.setReadOnly(True)  # Or make it editable but pre-filled
```

#### 1.2 Better Instructions
- [ ] Add screenshots to settings dialog
- [ ] Step-by-step guide
- [ ] Link to Spotify dashboard with pre-filled redirect URI

#### 1.3 First-Run Wizard
- [ ] Detect first run
- [ ] Show welcome screen
- [ ] Guide through setup
- [ ] Skip option for advanced users

### Phase 2: Embedded OAuth (Week 2)

#### 2.1 WebView Integration
- [ ] Install QWebEngineWidgets
- [ ] Create embedded OAuth view
- [ ] Handle callback in-app
- [ ] Remove browser popup

#### 2.2 Auto-Detection
- [ ] Try to detect existing credentials
- [ ] Check for cached tokens
- [ ] Auto-login if possible

### Phase 3: Advanced (Future)

#### 3.1 Browser Extension
- [ ] Create Chrome extension
- [ ] Create Firefox extension
- [ ] Auto-extract credentials
- [ ] One-click setup

#### 3.2 Cloud Setup
- [ ] Optional cloud account
- [ ] Sync credentials (encrypted)
- [ ] Multi-device setup

---

## 📋 Detailed Implementation

### Step 1: First-Run Detection

```python
# In main.py or gui.py
def is_first_run():
    """Check if this is the first time running the app."""
    config_path = Path.home() / '.alarmify' / 'config.json'
    return not config_path.exists()

def create_first_run_wizard():
    """Show first-run setup wizard."""
    wizard = SetupWizard()
    if wizard.exec_() == QDialog.Accepted:
        # Save config
        save_config(wizard.get_credentials())
```

### Step 2: Setup Wizard

```python
class SetupWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Welcome to Alarmify')
        self.addPage(WelcomePage())
        self.addPage(CredentialsPage())
        self.addPage(OAuthPage())
        self.addPage(TestPage())
```

### Step 3: Embedded OAuth

```python
class OAuthWebView(QWebEngineView):
    urlChanged = pyqtSignal(str)
    
    def __init__(self, auth_url, redirect_uri, parent=None):
        super().__init__(parent)
        self.redirect_uri = redirect_uri
        self.load(QUrl(auth_url))
        
    def urlChanged(self, url):
        if url.toString().startswith(self.redirect_uri):
            # Extract code from URL
            code = self.extract_code(url)
            self.code_received.emit(code)
```

### Step 4: Auto-Detection

```python
def try_auto_detect_credentials():
    """Try to detect Spotify credentials from common locations."""
    # Check browser cookies (requires extension)
    # Check environment variables
    # Check previous installations
    # Return credentials if found, None otherwise
```

---

## 🎯 Success Metrics

### Target Metrics
- **Setup Time:** < 2 minutes (from 5-10 minutes)
- **Completion Rate:** > 90% (from ~60%)
- **Error Rate:** < 5% (from ~20%)
- **User Satisfaction:** > 4.5/5

### Measurement
- Track setup time
- Track completion rate
- Track error frequency
- User feedback surveys

---

## 📚 Resources

- [Qt WebEngine](https://doc.qt.io/qt-5/qtwebengine-index.html)
- [OAuth 2.0 Best Practices](https://oauth.net/2/)
- [Browser Extension Development](https://developer.chrome.com/docs/extensions/)

---

## 🚨 Risks & Mitigation

### Risk 1: WebView Not Available
**Mitigation:** Fallback to browser popup

### Risk 2: Security Concerns
**Mitigation:** 
- Encrypt stored credentials
- Use secure token storage
- Clear sensitive data

### Risk 3: Complexity
**Mitigation:**
- Start simple
- Iterate based on feedback
- Keep fallback options

---

**Last Updated:** December 23, 2024
**Status:** Planning
**Priority:** High (MVP)

