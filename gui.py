"""
gui.py - Main GUI module for Alarmify

This module provides the main application window and all UI components:
- AlarmApp: Main window with playlist browser, alarm controls
- PlaylistItemWidget: Custom widget for playlist items with thumbnails
- SettingsDialog: Dialog for Spotify API credentials
- AlarmManagerDialog: Dialog to view/delete scheduled alarms

Dependencies:
- PyQt5: Qt bindings for Python GUI
- requests: HTTP library for downloading playlist images
"""

# PyQt5 imports for GUI components
from PyQt5 import QtWidgets, uic  # Base widgets and UI loader
from PyQt5.QtWidgets import (
    QWidget,           # Base widget class
    QVBoxLayout,       # Vertical layout manager
    QHBoxLayout,       # Horizontal layout manager
    QPushButton,       # Clickable button
    QTimeEdit,         # Time input spinner
    QListWidget,       # List display widget
    QListWidgetItem,   # Item for QListWidget
    QMessageBox,       # Popup message dialogs
    QLabel,            # Text/image label
    QSpacerItem,       # Empty space in layouts
    QSizePolicy,       # Size policy for widgets
    QDialog,           # Modal dialog base
    QLineEdit,         # Single-line text input
    QFormLayout,       # Form-style layout (label + field)
    QSlider,           # Slider for volume control
    QFrame,            # Frame container with border
    QScrollArea,       # Scrollable container
    QTableWidget,      # Table display widget
    QTableWidgetItem,  # Item for QTableWidget
    QHeaderView,       # Table header control
    QAbstractItemView  # Item view constants
)
from PyQt5.QtGui import QFont, QPixmap, QIcon  # Font, images, icons
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QByteArray  # Core Qt utilities
from pathlib import Path  # Path manipulation
import os  # Operating system interface
import requests  # HTTP requests for image downloads
from dotenv import load_dotenv  # Environment variable loading

# Local module imports
from spotify_api.spotify_api import SpotifyAPI  # Spotify API wrapper
from alarm import Alarm  # Alarm scheduling


class ImageLoaderThread(QThread):
    """
    Background thread for downloading playlist cover images.

    Prevents UI freezing while fetching images from Spotify CDN.
    Emits a signal with the image data when download completes.
    """
    # Signal emitted when image is loaded: (playlist_id, QPixmap)
    image_loaded = pyqtSignal(str, QPixmap)

    def __init__(self, playlist_id, image_url):
        """
        Initialize the image loader thread.

        Args:
            playlist_id: Unique ID to identify which playlist this image belongs to.
            image_url: URL of the image to download.
        """
        super().__init__()
        self.playlist_id = playlist_id  # Store playlist ID for signal
        self.image_url = image_url      # URL to download
        self._is_running = True         # Flag for graceful shutdown

    def run(self):
        """
        Execute the download in background thread.

        Downloads image from URL, converts to QPixmap, and emits signal.
        On failure, emits an empty pixmap.
        """
        if not self._is_running:
            return
        
        try:
            # Download image data from URL
            response = requests.get(self.image_url, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors

            if not self._is_running:
                return

            # Convert raw bytes to QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(response.content))

            # Emit signal with playlist ID and loaded pixmap
            if self._is_running:
                self.image_loaded.emit(self.playlist_id, pixmap)
        except Exception:
            # On error, emit empty pixmap
            if self._is_running:
                self.image_loaded.emit(self.playlist_id, QPixmap())

    def stop(self):
        """Request the thread to stop gracefully."""
        self._is_running = False


class PlaylistItemWidget(QWidget):
    """
    Custom widget for displaying a playlist item with thumbnail.

    Shows:
    - Playlist cover image (64x64 pixels)
    - Playlist name (bold)
    - Track count and owner info

    Used as custom widget in QListWidget items.
    """

    def __init__(self, playlist_data, parent=None):
        """
        Initialize the playlist item widget.

        Args:
            playlist_data: Dict with 'name', 'track_count', 'owner', 'image_url', 'uri'
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        # Store playlist data for later retrieval
        self.playlist_data = playlist_data

        # Main horizontal layout: [Image] [Text Info]
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)  # Small margins
        layout.setSpacing(12)  # Space between image and text

        # Playlist cover image label (64x64 placeholder)
        self.image_label = QLabel()
        self.image_label.setFixedSize(64, 64)  # Fixed size for consistency
        self.image_label.setStyleSheet(
            "background-color: #282828; border-radius: 4px;"  # Dark placeholder
        )
        self.image_label.setAlignment(Qt.AlignCenter)  # Center any content
        layout.addWidget(self.image_label)

        # Vertical layout for text info
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)  # Tight spacing between lines

        # Playlist name (bold, larger font)
        self.name_label = QLabel(playlist_data.get('name', 'Unknown'))
        self.name_label.setFont(QFont('Arial', 11, QFont.Bold))
        self.name_label.setStyleSheet("color: #FFFFFF;")  # White text
        text_layout.addWidget(self.name_label)

        # Track count and owner (smaller, gray text)
        track_count = playlist_data.get('track_count', 0)
        owner = playlist_data.get('owner', 'Unknown')
        info_text = f"{track_count} tracks - by {owner}"
        self.info_label = QLabel(info_text)
        self.info_label.setFont(QFont('Arial', 9))
        self.info_label.setStyleSheet("color: #B3B3B3;")  # Gray text
        text_layout.addWidget(self.info_label)

        # Add stretch to push text to top
        text_layout.addStretch()

        layout.addLayout(text_layout)
        layout.addStretch()  # Push content to left

    def set_image(self, pixmap):
        """
        Set the playlist cover image.

        Args:
            pixmap: QPixmap of the cover image.
        """
        if not pixmap.isNull():
            # Scale to fit while maintaining aspect ratio
            scaled = pixmap.scaled(
                64, 64,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)


class AlarmApp(QtWidgets.QMainWindow):
    """
    Main application window for Alarmify.

    Provides:
    - Playlist browser with thumbnails and metadata
    - Authentication status display
    - Alarm time picker and scheduling
    - Volume control slider
    - Alarm management (view/delete)
    - Settings dialog for credentials
    """

    def __init__(self):
        """Initialize the main window and all UI components."""
        super(AlarmApp, self).__init__()

        # Track active image loader threads to prevent garbage collection
        self.image_loaders = []

        # Map playlist IDs to their widget items for image updates
        self.playlist_widgets = {}

        # Build the UI programmatically (no .ui file needed)
        self._build_ui()

        # Apply Spotify-style stylesheet if available
        style_path = Path(__file__).resolve().parent / 'spotify_style.qss'
        if style_path.exists():
            try:
                with open(style_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
            except Exception:
                pass  # Continue without stylesheet

        # Try to initialize Spotify API with existing credentials
        try:
            self.spotify_api = SpotifyAPI()
        except RuntimeError as e:
            # No credentials configured yet - show warning
            QMessageBox.warning(self, 'Spotify credentials', str(e))
            self.spotify_api = None

        # Initialize alarm manager
        self.alarm = Alarm()

        # Connect button signals to handlers
        self.login_button.clicked.connect(self.login_to_spotify)
        self.set_alarm_button.clicked.connect(self.set_alarm)
        self.settings_button.clicked.connect(self.open_settings)
        self.manage_alarms_button.clicked.connect(self.open_alarm_manager)

        # Disable buttons if no credentials
        if not self.spotify_api:
            self.login_button.setEnabled(False)
            self.set_alarm_button.setEnabled(False)

        # Update auth status display
        self._update_auth_status()

        # Auto-connect: If already authenticated, load playlists automatically
        if self.spotify_api and self.spotify_api.is_authenticated():
            self._load_playlists()

    def _build_ui(self):
        """Build the complete UI layout programmatically."""
        # Window configuration
        self.setWindowTitle('Alarmify')
        self.setMinimumSize(700, 500)  # Minimum window size

        # Central widget container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Root vertical layout
        root_layout = QVBoxLayout(self.central_widget)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(16)

        # === HEADER SECTION ===
        header = QHBoxLayout()

        # App logo/title
        logo = QLabel('Alarmify')
        logo.setObjectName('appLogo')
        logo.setFont(QFont('Arial', 24, QFont.Bold))
        logo.setStyleSheet("color: #1DB954;")  # Spotify green
        header.addWidget(logo)

        # Spacer to push auth status and settings to right
        header.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Authentication status label
        self.auth_status_label = QLabel('Not connected')
        self.auth_status_label.setObjectName('authStatus')
        self.auth_status_label.setStyleSheet("color: #B3B3B3;")
        header.addWidget(self.auth_status_label)

        # Settings button (gear icon)
        self.settings_button = QPushButton('\u2699')  # Unicode gear
        self.settings_button.setFixedSize(36, 36)
        self.settings_button.setToolTip('Settings')
        header.addWidget(self.settings_button)

        root_layout.addLayout(header)

        # === MAIN CONTENT SECTION ===
        content = QHBoxLayout()
        content.setSpacing(20)

        # --- LEFT PANEL: Playlist Browser ---
        left_panel = QVBoxLayout()

        # Playlist header
        playlist_header = QLabel('Your Playlists')
        playlist_header.setFont(QFont('Arial', 14, QFont.Bold))
        playlist_header.setStyleSheet("color: #FFFFFF;")
        left_panel.addWidget(playlist_header)

        # Playlist list widget with custom items
        self.playlist_list = QListWidget()
        self.playlist_list.setObjectName('playlistList')
        self.playlist_list.setMinimumWidth(350)
        self.playlist_list.setSpacing(2)  # Space between items
        left_panel.addWidget(self.playlist_list)

        # Buttons row
        btn_layout = QHBoxLayout()

        self.login_button = QPushButton('Login to Spotify')
        self.login_button.setObjectName('loginButton')
        btn_layout.addWidget(self.login_button)

        self.set_alarm_button = QPushButton('Set Alarm')
        self.set_alarm_button.setObjectName('setAlarmButton')
        btn_layout.addWidget(self.set_alarm_button)

        left_panel.addLayout(btn_layout)
        content.addLayout(left_panel, stretch=2)

        # --- RIGHT PANEL: Alarm Controls ---
        right_panel = QVBoxLayout()
        right_panel.setSpacing(16)

        # Alarm Time section
        time_label = QLabel('Alarm Time')
        time_label.setFont(QFont('Arial', 14, QFont.Bold))
        time_label.setStyleSheet("color: #FFFFFF;")
        right_panel.addWidget(time_label)

        self.time_input = QTimeEdit(self)
        self.time_input.setDisplayFormat('HH:mm')
        self.time_input.setObjectName('timeInput')
        self.time_input.setFont(QFont('Arial', 18))
        self.time_input.setMinimumHeight(50)
        right_panel.addWidget(self.time_input)

        # Volume Control section
        volume_label = QLabel('Alarm Volume')
        volume_label.setFont(QFont('Arial', 14, QFont.Bold))
        volume_label.setStyleSheet("color: #FFFFFF;")
        right_panel.addWidget(volume_label)

        # Volume slider with value display
        volume_row = QHBoxLayout()

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(80)  # Default 80%
        self.volume_slider.setObjectName('volumeSlider')
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_row.addWidget(self.volume_slider)

        self.volume_value_label = QLabel('80%')
        self.volume_value_label.setFixedWidth(45)
        self.volume_value_label.setStyleSheet("color: #B3B3B3;")
        volume_row.addWidget(self.volume_value_label)

        right_panel.addLayout(volume_row)

        # Manage Alarms button
        self.manage_alarms_button = QPushButton('Manage Alarms')
        self.manage_alarms_button.setObjectName('manageAlarmsButton')
        right_panel.addWidget(self.manage_alarms_button)

        # Push everything up
        right_panel.addStretch()

        content.addLayout(right_panel, stretch=1)
        root_layout.addLayout(content)

    def _on_volume_changed(self, value):
        """Update volume label when slider moves."""
        self.volume_value_label.setText(f'{value}%')

    def _update_auth_status(self):
        """Update the authentication status display."""
        if self.spotify_api and self.spotify_api.is_authenticated():
            user = self.spotify_api.get_current_user()
            if user:
                name = user.get('display_name', 'User')
                self.auth_status_label.setText(f'Connected as {name}')
                self.auth_status_label.setStyleSheet("color: #1DB954;")  # Green
            else:
                self.auth_status_label.setText('Connected')
                self.auth_status_label.setStyleSheet("color: #1DB954;")
        else:
            self.auth_status_label.setText('Not connected')
            self.auth_status_label.setStyleSheet("color: #B3B3B3;")  # Gray

    def login_to_spotify(self):
        """Handle login button click - authenticate with Spotify."""
        if not self.spotify_api:
            QMessageBox.warning(self, 'Missing', 'Spotify credentials are not configured.')
            return

        try:
            # Perform OAuth authentication
            self.spotify_api.authenticate()

            # Update auth status display
            self._update_auth_status()

            # Load playlists with detailed info
            self._load_playlists()

        except Exception as e:
            QMessageBox.critical(self, 'Login Failed', f'Could not login to Spotify: {e}')

    def _load_playlists(self):
        """Load user's playlists with thumbnails and metadata."""
        if not self.spotify_api:
            return

        try:
            # Get detailed playlist info
            playlists = self.spotify_api.get_playlists_detailed()

            # Clear existing items
            self.playlist_list.clear()
            self.playlist_widgets.clear()

            for playlist in playlists:
                # Create custom widget for this playlist
                widget = PlaylistItemWidget(playlist)

                # Create list item with appropriate size
                item = QListWidgetItem(self.playlist_list)
                item.setSizeHint(QSize(340, 76))  # Height for image + padding

                # Store playlist data in item for retrieval
                item.setData(Qt.UserRole, playlist)

                # Set the custom widget
                self.playlist_list.setItemWidget(item, widget)

                # Store reference for image updates
                playlist_id = playlist.get('id', '')
                self.playlist_widgets[playlist_id] = widget

                # Load image in background if URL exists
                image_url = playlist.get('image_url')
                if image_url:
                    self._load_playlist_image(playlist_id, image_url)

        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not load playlists: {e}')

    def _load_playlist_image(self, playlist_id, image_url):
        """Start background thread to load playlist cover image."""
        # Create loader thread
        loader = ImageLoaderThread(playlist_id, image_url)

        # Connect signal to update handler
        loader.image_loaded.connect(self._on_image_loaded)

        # Keep reference to prevent garbage collection
        self.image_loaders.append(loader)

        # Start the download
        loader.start()

    def _on_image_loaded(self, playlist_id, pixmap):
        """Handle loaded image - update the playlist widget."""
        # Find the widget for this playlist
        widget = self.playlist_widgets.get(playlist_id)
        if widget and not pixmap.isNull():
            widget.set_image(pixmap)

    def open_settings(self):
        """Open the settings dialog for Spotify credentials."""
        dlg = SettingsDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            # Reload environment and recreate SpotifyAPI
            load_dotenv(override=True)
            try:
                self.spotify_api = SpotifyAPI()
                self.login_button.setEnabled(True)
                self.set_alarm_button.setEnabled(True)
                self._update_auth_status()
                QMessageBox.information(self, 'Saved', 'Spotify credentials saved.')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Could not load Spotify API: {e}')

    def open_alarm_manager(self):
        """Open the alarm manager dialog."""
        dlg = AlarmManagerDialog(self.alarm, self)
        dlg.exec_()

    def set_alarm(self):
        """Set an alarm for the selected playlist."""
        # Get selected time
        time_str = self.time_input.time().toString('HH:mm')

        # Get selected playlist
        current = self.playlist_list.currentItem()
        if current is None:
            QMessageBox.warning(self, 'No playlist', 'Please select a playlist first.')
            return

        # Get playlist data from item
        playlist_data = current.data(Qt.UserRole)
        if not playlist_data:
            QMessageBox.warning(self, 'Error', 'Could not retrieve playlist information.')
            return

        playlist_name = playlist_data.get('name', 'Unknown')
        playlist_uri = playlist_data.get('uri')
        
        if not playlist_uri:
            QMessageBox.warning(self, 'Error', 'Playlist URI is missing.')
            return

        if not self.spotify_api:
            QMessageBox.warning(self, 'Missing', 'Spotify credentials are not configured.')
            return

        # Get volume setting
        volume = self.volume_slider.value()

        # Set the alarm with both name and URI
        self.alarm.set_alarm(time_str, playlist_name, playlist_uri, self.spotify_api, volume)

        QMessageBox.information(
            self,
            'Alarm Set',
            f'Alarm set for {time_str}\nPlaylist: {playlist_name}\nVolume: {volume}%'
        )

    def closeEvent(self, event):
        """
        Handle window close event - cleanup resources before exit.

        Ensures all background threads are stopped and resources are released:
        - Stops all image loader threads
        - Shuts down the alarm scheduler thread
        - Cleans up scheduled jobs

        Args:
            event: QCloseEvent from Qt framework
        """
        self._cleanup_resources()
        event.accept()

    def _cleanup_resources(self):
        """Clean up all background threads and resources."""
        for loader in self.image_loaders:
            if loader.isRunning():
                loader.stop()
                loader.wait(1000)
        
        self.image_loaders.clear()
        
        if self.alarm:
            self.alarm.shutdown()


class AlarmManagerDialog(QDialog):
    """
    Dialog to view and manage scheduled alarms.

    Shows a table of all active alarms with time, playlist, and volume.
    Allows deleting individual alarms.
    """

    def __init__(self, alarm_manager, parent=None):
        """
        Initialize the alarm manager dialog.

        Args:
            alarm_manager: Alarm instance containing scheduled alarms.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.alarm_manager = alarm_manager
        self.setWindowTitle('Manage Alarms')
        self.setMinimumSize(500, 300)
        self.setModal(True)

        self._build_ui()
        self._load_alarms()

    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel('Scheduled Alarms')
        header.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(header)

        # Alarms table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Time', 'Playlist', 'Volume', 'Actions'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        # Close button
        btn_close = QPushButton('Close')
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _load_alarms(self):
        """Load and display all scheduled alarms."""
        alarms = self.alarm_manager.get_alarms()
        self.table.setRowCount(len(alarms))

        for row, alarm_info in enumerate(alarms):
            # Time column
            self.table.setItem(row, 0, QTableWidgetItem(alarm_info.get('time', '')))

            # Playlist column
            self.table.setItem(row, 1, QTableWidgetItem(alarm_info.get('playlist', '')))

            # Volume column
            self.table.setItem(row, 2, QTableWidgetItem(f"{alarm_info.get('volume', 80)}%"))

            # Delete button
            btn_delete = QPushButton('Delete')
            btn_delete.clicked.connect(lambda checked, r=row: self._delete_alarm(r))
            self.table.setCellWidget(row, 3, btn_delete)

    def _delete_alarm(self, row):
        """Delete the alarm at the specified row."""
        alarms = self.alarm_manager.get_alarms()
        if 0 <= row < len(alarms):
            alarm_info = alarms[row]
            self.alarm_manager.remove_alarm(alarm_info.get('time', ''))
            self._load_alarms()  # Refresh table


class SettingsDialog(QDialog):
    """
    Dialog for configuring Spotify API credentials.

    Allows user to enter Client ID, Client Secret, and Redirect URI.
    Saves credentials to .env file in project directory.
    """

    def __init__(self, parent=None):
        """Initialize the settings dialog with current credentials."""
        super().__init__(parent)
        self.setWindowTitle('Spotify Settings')
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QFormLayout(self)
        layout.setSpacing(12)

        # Client ID input
        self.client_id = QLineEdit(self)
        self.client_id.setPlaceholderText('Enter your Spotify Client ID')

        # Client Secret input (masked)
        self.client_secret = QLineEdit(self)
        self.client_secret.setPlaceholderText('Enter your Spotify Client Secret')
        self.client_secret.setEchoMode(QLineEdit.Password)  # Hide secret

        # Redirect URI input
        self.redirect_uri = QLineEdit(self)
        self.redirect_uri.setPlaceholderText('http://localhost:8888/callback')

        # Pre-fill with existing values from environment
        load_dotenv()
        self.client_id.setText(os.getenv('SPOTIPY_CLIENT_ID', ''))
        self.client_secret.setText(os.getenv('SPOTIPY_CLIENT_SECRET', ''))
        self.redirect_uri.setText(
            os.getenv('SPOTIPY_REDIRECT_URI', 'http://localhost:8888/callback')
        )

        # Add rows to form
        layout.addRow('Client ID:', self.client_id)
        layout.addRow('Client Secret:', self.client_secret)
        layout.addRow('Redirect URI:', self.redirect_uri)

        # Buttons row
        btn_layout = QHBoxLayout()

        btn_cancel = QPushButton('Cancel', self)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton('Save', self)
        btn_save.clicked.connect(self.save)
        btn_save.setDefault(True)  # Enter key triggers save
        btn_layout.addWidget(btn_save)

        layout.addRow(btn_layout)

    def save(self):
        """Validate and save credentials to .env file."""
        # Get project root directory (where this file is located)
        root = Path(__file__).resolve().parent
        env_path = root / '.env'

        try:
            # Extract and clean input values
            cid = self.client_id.text().strip()
            csec = self.client_secret.text().strip()
            ruri = self.redirect_uri.text().strip()

            # Validation: required fields
            if not cid or not csec:
                QMessageBox.warning(
                    self,
                    'Validation Error',
                    'Client ID and Client Secret are required.'
                )
                return

            # Validation: redirect URI format
            if not (ruri.startswith('http://') or ruri.startswith('https://')):
                QMessageBox.warning(
                    self,
                    'Validation Error',
                    'Redirect URI must start with http:// or https://'
                )
                return

            # Write credentials to .env file
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(f"SPOTIPY_CLIENT_ID={cid}\n")
                f.write(f"SPOTIPY_CLIENT_SECRET={csec}\n")
                f.write(f"SPOTIPY_REDIRECT_URI={ruri}\n")

            # Reload environment with new values
            load_dotenv(override=True)

            # Close dialog with success
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, 'Save Error', f'Could not save credentials: {e}')
