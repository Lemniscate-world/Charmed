"""
gui_setup_wizard.py - First-run setup wizard for Alarmify

Provides a guided setup experience for new users, reducing friction
and making the initial configuration as smooth as possible.

Features:
- Welcome screen
- Spotify Premium check
- Credentials setup (with help)
- OAuth authentication
- Test alarm setup
"""

from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFormLayout, QMessageBox, QCheckBox,
    QTextEdit, QProgressBar, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from pathlib import Path
import os
import webbrowser
from dotenv import load_dotenv
from logging_config import get_logger

logger = get_logger(__name__)


class WelcomePage(QWizardPage):
    """Welcome page - first screen of the wizard."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Welcome to Alarmify")
        self.setSubTitle("Let's get you set up in just a few steps")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Welcome message
        welcome_text = QLabel(
            "Alarmify wakes you up with your favorite Spotify playlists.\n\n"
            "This wizard will help you:\n"
            "• Set up your Spotify credentials\n"
            "• Connect your account\n"
            "• Create your first alarm\n\n"
            "This should only take 2-3 minutes!"
        )
        welcome_text.setWordWrap(True)
        welcome_text.setStyleSheet("font-size: 14px; color: #b3b3b3; padding: 20px;")
        layout.addWidget(welcome_text)
        
        layout.addStretch()


class PremiumCheckPage(QWizardPage):
    """Check if user has Spotify Premium."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Spotify Premium Check")
        self.setSubTitle("Alarmify requires Spotify Premium for playback control")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        info_text = QLabel(
            "To use Alarmify, you need a Spotify Premium account.\n\n"
            "Premium allows Alarmify to:\n"
            "• Control playback on your devices\n"
            "• Set volume levels\n"
            "• Start playlists automatically\n\n"
            "Do you have Spotify Premium?\n\n"
            "💡 Tip: You can continue setup now and test with mock mode, "
            "then upgrade to Premium when ready!"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("font-size: 14px; color: #b3b3b3; padding: 20px;")
        layout.addWidget(info_text)
        
        self.has_premium = QCheckBox("Yes, I have Spotify Premium")
        self.has_premium.setStyleSheet("font-size: 14px; padding: 10px; color: #ffffff;")
        layout.addWidget(self.has_premium)
        
        no_premium_layout = QHBoxLayout()
        no_premium_label = QLabel("No Premium?")
        no_premium_label.setStyleSheet("color: #727272;")
        no_premium_layout.addWidget(no_premium_label)
        
        upgrade_button = QPushButton("Get Premium (1 Month Free Trial)")
        upgrade_button.setStyleSheet(
            "background-color: #1DB954; color: #000000; padding: 10px 20px; "
            "border-radius: 6px; font-weight: 600;"
        )
        upgrade_button.clicked.connect(self._open_premium_page)
        no_premium_layout.addWidget(upgrade_button)
        no_premium_layout.addStretch()
        
        layout.addLayout(no_premium_layout)
        
        # Note about continuing without Premium
        continue_note = QLabel(
            "You can continue setup without Premium to test the app interface. "
            "You'll need Premium for actual alarm playback."
        )
        continue_note.setWordWrap(True)
        continue_note.setStyleSheet("color: #888; font-size: 12px; font-style: italic; padding: 10px;")
        layout.addWidget(continue_note)
        
        layout.addStretch()
        
        # Register field
        self.registerField("has_premium", self.has_premium)
    
    def _open_premium_page(self):
        """Open Spotify Premium signup page."""
        webbrowser.open('https://www.spotify.com/premium')
    
    def validatePage(self):
        """Validate that user has Premium or is getting it."""
        if not self.has_premium.isChecked():
            reply = QMessageBox.question(
                self,
                'Continue Without Premium?',
                'Alarmify requires Spotify Premium for playback control.\n\n'
                'You can continue setup now to:\n'
                '• Test the app interface\n'
                '• Set up credentials\n'
                '• Use test mode (mock data)\n\n'
                'You\'ll need Premium for actual alarm playback.\n\n'
                'Would you like to continue?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes  # Default to Yes - allow them to continue
            )
            return reply == QMessageBox.Yes
        return True


class CredentialsPage(QWizardPage):
    """Setup Spotify API credentials."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Spotify Credentials")
        self.setSubTitle("We'll help you get your Spotify API credentials")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Instructions
        instructions = QLabel(
            "You need to create a Spotify Developer App to use Alarmify.\n"
            "Don't worry - it's free and takes 2 minutes!"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 14px; color: #b3b3b3; padding: 10px;")
        layout.addWidget(instructions)
        
        # Get credentials button
        get_creds_button = QPushButton("Get Credentials (Open Spotify Developer Dashboard)")
        get_creds_button.setStyleSheet(
            "background-color: #1DB954; color: #000000; padding: 12px 24px; "
            "border-radius: 6px; font-weight: 700; font-size: 14px;"
        )
        get_creds_button.clicked.connect(self._open_dashboard)
        layout.addWidget(get_creds_button)
        
        # Separator
        separator = QLabel("— Then paste your credentials below —")
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("color: #666; margin: 10px 0;")
        layout.addWidget(separator)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.client_id = QLineEdit()
        self.client_id.setPlaceholderText('Paste your Client ID here')
        self.client_id.setMinimumHeight(40)
        
        self.client_secret = QLineEdit()
        self.client_secret.setPlaceholderText('Paste your Client Secret here')
        self.client_secret.setEchoMode(QLineEdit.Password)
        self.client_secret.setMinimumHeight(40)
        
        self.redirect_uri = QLineEdit()
        self.redirect_uri.setText('http://127.0.0.1:8888/callback')
        self.redirect_uri.setReadOnly(True)
        self.redirect_uri.setStyleSheet("color: #888; background: #1a1a1a;")
        self.redirect_uri.setMinimumHeight(40)
        
        form_layout.addRow('Client ID:', self.client_id)
        form_layout.addRow('Client Secret:', self.client_secret)
        form_layout.addRow('Redirect URI:', self.redirect_uri)
        
        layout.addLayout(form_layout)
        
        # Help note
        help_note = QLabel(
            "Note: Add this exact Redirect URI in your Spotify app settings.\n"
            "Spotify requires 127.0.0.1 (not localhost) for security."
        )
        help_note.setWordWrap(True)
        help_note.setStyleSheet("color: #888; font-size: 11px; margin-top: 10px;")
        layout.addWidget(help_note)
        
        layout.addStretch()
        
        # Register fields
        self.registerField("client_id*", self.client_id)
        self.registerField("client_secret*", self.client_secret)
        self.registerField("redirect_uri", self.redirect_uri)
    
    def _open_dashboard(self):
        """Open Spotify Developer Dashboard with instructions."""
        QMessageBox.information(
            self,
            'How to Get Credentials',
            "1. Log in with your Spotify account\n"
            "2. Click 'Create app'\n"
            "3. Enter any name (e.g., 'Alarmify')\n"
            "4. Enter any description\n"
            "5. Set Redirect URI to:\n"
            "   http://127.0.0.1:8888/callback\n"
            "   (Important: Use 127.0.0.1, not localhost)\n"
            "6. Check 'Web API'\n"
            "7. Click 'Save'\n"
            "8. Copy Client ID and Client Secret\n"
            "9. Paste them in this dialog"
        )
        webbrowser.open('https://developer.spotify.com/dashboard')
    
    def validatePage(self):
        """Validate credentials are entered."""
        if not self.client_id.text().strip():
            QMessageBox.warning(self, 'Missing Field', 'Please enter your Client ID.')
            return False
        if not self.client_secret.text().strip():
            QMessageBox.warning(self, 'Missing Field', 'Please enter your Client Secret.')
            return False
        return True


class AuthenticationPage(QWizardPage):
    """Authenticate with Spotify."""
    
    authenticated = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Connect to Spotify")
        self.setSubTitle("Let's connect your Spotify account")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        info_text = QLabel(
            "Now we'll authenticate with Spotify.\n\n"
            "Click the button below to open your browser and authorize Alarmify."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("font-size: 14px; color: #b3b3b3; padding: 20px;")
        layout.addWidget(info_text)
        
        self.login_button = QPushButton("Login to Spotify")
        self.login_button.setStyleSheet(
            "background-color: #1DB954; color: #000000; padding: 12px 32px; "
            "border-radius: 500px; font-weight: 700; font-size: 14px; min-height: 40px;"
        )
        self.login_button.clicked.connect(self._authenticate)
        layout.addWidget(self.login_button)
        
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #b3b3b3; padding: 10px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        self._authenticated = False
    
    def _authenticate(self):
        """Start authentication process."""
        self.login_button.setEnabled(False)
        self.status_label.setText("Opening browser for authentication...")
        
        try:
            # Save credentials first
            self._save_credentials()
            
            # Try to authenticate
            from spotify_api.spotify_api import ThreadSafeSpotifyAPI
            api = ThreadSafeSpotifyAPI()
            api.authenticate()
            
            self.status_label.setText("✅ Authentication successful!")
            self.status_label.setStyleSheet("color: #1DB954; padding: 10px;")
            self._authenticated = True
            self.authenticated.emit(True)
            
        except Exception as e:
            self.status_label.setText(f"❌ Authentication failed: {str(e)}")
            self.status_label.setStyleSheet("color: #FF6B6B; padding: 10px;")
            self.login_button.setEnabled(True)
            self._authenticated = False
            self.authenticated.emit(False)
    
    def _save_credentials(self):
        """Save credentials to .env file."""
        root = Path(__file__).resolve().parent
        env_path = root / '.env'
        
        client_id = self.field("client_id")
        client_secret = self.field("client_secret")
        redirect_uri = self.field("redirect_uri") or 'http://127.0.0.1:8888/callback'
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f"SPOTIPY_CLIENT_ID={client_id}\n")
            f.write(f"SPOTIPY_CLIENT_SECRET={client_secret}\n")
            f.write(f"SPOTIPY_REDIRECT_URI={redirect_uri}\n")
        
        load_dotenv(override=True)
    
    def isComplete(self):
        """Page is complete when authenticated."""
        return self._authenticated
    
    def validatePage(self):
        """Validate authentication."""
        if not self._authenticated:
            QMessageBox.warning(
                self,
                'Not Authenticated',
                'Please complete the authentication process before continuing.'
            )
            return False
        return True


class CompletionPage(QWizardPage):
    """Final page - setup complete."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Setup Complete!")
        self.setSubTitle("You're all set to use Alarmify")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        success_text = QLabel(
            "🎉 Congratulations! Alarmify is ready to use.\n\n"
            "You can now:\n"
            "• Browse your Spotify playlists\n"
            "• Set alarms for any time\n"
            "• Wake up to your favorite music\n\n"
            "Click 'Finish' to start using Alarmify!"
        )
        success_text.setWordWrap(True)
        success_text.setStyleSheet("font-size: 14px; color: #b3b3b3; padding: 20px;")
        layout.addWidget(success_text)
        
        layout.addStretch()


class SetupWizard(QWizard):
    """
    First-run setup wizard for Alarmify.
    
    Guides new users through:
    1. Welcome
    2. Premium check
    3. Credentials setup
    4. Authentication
    5. Completion
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alarmify Setup Wizard")
        self.setMinimumSize(600, 500)
        
        # Apply Spotify theme
        self._apply_theme()
        
        # Add pages
        self.addPage(WelcomePage())
        self.addPage(PremiumCheckPage())
        self.addPage(CredentialsPage())
        self.addPage(AuthenticationPage())
        self.addPage(CompletionPage())
        
        # Wizard settings
        self.setButtonText(QWizard.NextButton, "Next")
        self.setButtonText(QWizard.BackButton, "Back")
        self.setButtonText(QWizard.FinishButton, "Finish")
        self.setButtonText(QWizard.CancelButton, "Cancel")
        
        logger.info('Setup wizard initialized')
    
    def _apply_theme(self):
        """Apply Spotify-inspired theme to wizard."""
        style = """
        QWizard {
            background: #121212;
            color: #ffffff;
        }
        QWizardPage {
            background: #121212;
            color: #ffffff;
        }
        QLabel {
            color: #b3b3b3;
        }
        QPushButton {
            background: #1DB954;
            color: #000000;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #1ed760;
        }
        QPushButton:disabled {
            background: #2a2a2a;
            color: #777777;
        }
        QLineEdit {
            background: #181818;
            color: #ffffff;
            border: 1px solid #2a2a2a;
            border-radius: 6px;
            padding: 8px;
        }
        QLineEdit:focus {
            border: 2px solid #1DB954;
        }
        QCheckBox {
            color: #ffffff;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #727272;
            border-radius: 9px;
            background: #181818;
        }
        QCheckBox::indicator:checked {
            background: #1DB954;
            border: 2px solid #1DB954;
        }
        QCheckBox::indicator:hover {
            border: 2px solid #b3b3b3;
        }
        QCheckBox::indicator:checked:hover {
            border: 2px solid #1ed760;
            background: #1ed760;
        }
        """
        self.setStyleSheet(style)
    
    def get_credentials(self):
        """Get credentials from wizard."""
        return {
            'client_id': self.field("client_id"),
            'client_secret': self.field("client_secret"),
            'redirect_uri': self.field("redirect_uri") or 'http://127.0.0.1:8888/callback'
        }

