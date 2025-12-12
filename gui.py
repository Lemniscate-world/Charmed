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

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTimeEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QDialog,
    QLineEdit,
    QFormLayout,
    QSlider,
    QFrame,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QSystemTrayIcon
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QByteArray, QTimer
from pathlib import Path
import os
import requests
from dotenv import load_dotenv
import re

from spotify_api.spotify_api import SpotifyAPI
from alarm import Alarm
from logging_config import get_logger, get_log_files, read_log_file, get_current_log_file

logger = get_logger(__name__)


class ImageLoaderThread(QThread):
    """
    Background thread for downloading playlist cover images.

    Prevents UI freezing while fetching images from Spotify CDN.
    Emits a signal with the image data when download completes.
    """
    image_loaded = pyqtSignal(str, QPixmap)

    def __init__(self, playlist_id, image_url):
        """
        Initialize the image loader thread.

        Args:
            playlist_id: Unique ID to identify which playlist this image belongs to.
            image_url: URL of the image to download.
        """
        super().__init__()
        self.playlist_id = playlist_id
        self.image_url = image_url
        self._is_running = True

    def run(self):
        """
        Execute the download in background thread.

        Downloads image from URL, converts to QPixmap, and emits signal.
        On failure, emits an empty pixmap.
        """
        if not self._is_running:
            return
        
        try:
            response = requests.get(self.image_url, timeout=10)
            response.raise_for_status()

            if not self._is_running:
                return

            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(response.content))

            if self._is_running:
                self.image_loaded.emit(self.playlist_id, pixmap)
        except Exception as e:
            if self._is_running:
                logger.warning(f'Failed to load playlist image from {self.image_url}: {e}')
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

        self.playlist_data = playlist_data

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        self.image_label = QLabel()
        self.image_label.setFixedSize(64, 64)
        self.image_label.setStyleSheet(
            "background-color: #282828; border-radius: 4px;"
        )
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.name_label = QLabel(playlist_data.get('name', 'Unknown'))
        self.name_label.setFont(QFont('Arial', 11, QFont.Bold))
        self.name_label.setStyleSheet("color: #FFFFFF;")
        text_layout.addWidget(self.name_label)

        track_count = playlist_data.get('track_count', 0)
        owner = playlist_data.get('owner', 'Unknown')
        info_text = f"{track_count} tracks - by {owner}"
        self.info_label = QLabel(info_text)
        self.info_label.setFont(QFont('Arial', 9))
        self.info_label.setStyleSheet("color: #B3B3B3;")
        text_layout.addWidget(self.info_label)

        text_layout.addStretch()

        layout.addLayout(text_layout)
        layout.addStretch()

    def set_image(self, pixmap):
        """
        Set the playlist cover image.

        Args:
            pixmap: QPixmap of the cover image.
        """
        if not pixmap.isNull():
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
        
        logger.info('Initializing Alarmify main window')

        self.image_loaders = []
        self.playlist_widgets = {}

        self._build_ui()

        style_path = Path(__file__).resolve().parent / 'spotify_style.qss'
        if style_path.exists():
            try:
                with open(style_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
                logger.debug('Applied Spotify stylesheet')
            except Exception as e:
                logger.warning(f'Failed to load stylesheet: {e}')

        try:
            self.spotify_api = SpotifyAPI()
        except RuntimeError as e:
            logger.warning('Spotify credentials not configured')
            QMessageBox.warning(
                self,
                'Spotify Credentials Required',
                f'{e}\n\nPlease click the Settings button (⚙) to configure your Spotify API credentials.'
            )
            self.spotify_api = None

        self.alarm = Alarm(self)

        self.login_button.clicked.connect(self.login_to_spotify)
        self.set_alarm_button.clicked.connect(self.set_alarm)
        self.settings_button.clicked.connect(self.open_settings)
        self.manage_alarms_button.clicked.connect(self.open_alarm_manager)
        self.view_logs_button.clicked.connect(self.open_log_viewer)

        if not self.spotify_api:
            self.login_button.setEnabled(False)
            self.set_alarm_button.setEnabled(False)

        self._setup_system_tray()
        self._update_auth_status()
        self._start_device_status_monitor()

        if self.spotify_api and self.spotify_api.is_authenticated():
            logger.info('Auto-loading playlists (cached authentication)')
            self._load_playlists()

    def _setup_system_tray(self):
        """Setup system tray icon for notifications."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = None
            return

        self.tray_icon = QSystemTrayIcon(self)
        
        icon_path = Path(__file__).resolve().parent / 'icon.png'
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        
        self.tray_icon.setToolTip('Alarmify')
        self.tray_icon.show()

    def show_tray_notification(self, title, message, icon_type=QSystemTrayIcon.Information):
        """
        Show a system tray notification.

        Args:
            title: Notification title.
            message: Notification message.
            icon_type: QSystemTrayIcon icon type (Information, Warning, Critical).
        """
        if self.tray_icon and self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(title, message, icon_type, 5000)

    def _start_device_status_monitor(self):
        """Start periodic monitoring of active Spotify device."""
        self.device_status_timer = QTimer(self)
        self.device_status_timer.timeout.connect(self._update_device_status)
        self.device_status_timer.start(10000)
        self._update_device_status()

    def _update_device_status(self):
        """Update the device status indicator in the UI header."""
        if not self.spotify_api or not self.spotify_api.is_authenticated():
            self.device_status_label.setText('No active device')
            self.device_status_label.setStyleSheet("color: #B3B3B3;")
            return

        try:
            device = self.spotify_api.get_active_device()
            if device:
                device_name = device.get('name', 'Unknown Device')
                device_type = device.get('type', 'Device')
                self.device_status_label.setText(f'🔊 {device_name} ({device_type})')
                self.device_status_label.setStyleSheet("color: #1DB954;")
            else:
                self.device_status_label.setText('No active device')
                self.device_status_label.setStyleSheet("color: #FFA500;")
        except Exception:
            self.device_status_label.setText('Device check failed')
            self.device_status_label.setStyleSheet("color: #B3B3B3;")

    def _build_ui(self):
        """Build the complete UI layout programmatically."""
        self.setWindowTitle('Alarmify')
        self.setMinimumSize(700, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        root_layout = QVBoxLayout(self.central_widget)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(16)

        header = QHBoxLayout()

        logo = QLabel('Alarmify')
        logo.setObjectName('appLogo')
        logo.setFont(QFont('Arial', 24, QFont.Bold))
        logo.setStyleSheet("color: #1DB954;")
        header.addWidget(logo)

        header.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        status_layout = QVBoxLayout()
        status_layout.setSpacing(4)

        self.auth_status_label = QLabel('Not connected')
        self.auth_status_label.setObjectName('authStatus')
        self.auth_status_label.setStyleSheet("color: #B3B3B3;")
        status_layout.addWidget(self.auth_status_label)

        self.device_status_label = QLabel('No active device')
        self.device_status_label.setObjectName('deviceStatus')
        self.device_status_label.setStyleSheet("color: #B3B3B3; font-size: 10px;")
        status_layout.addWidget(self.device_status_label)

        header.addLayout(status_layout)

        self.settings_button = QPushButton('\u2699')
        self.settings_button.setFixedSize(36, 36)
        self.settings_button.setToolTip('Settings')
        header.addWidget(self.settings_button)

        root_layout.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(20)

        left_panel = QVBoxLayout()

        playlist_header = QLabel('Your Playlists')
        playlist_header.setFont(QFont('Arial', 14, QFont.Bold))
        playlist_header.setStyleSheet("color: #FFFFFF;")
        left_panel.addWidget(playlist_header)

        self.playlist_list = QListWidget()
        self.playlist_list.setObjectName('playlistList')
        self.playlist_list.setMinimumWidth(350)
        self.playlist_list.setSpacing(2)
        left_panel.addWidget(self.playlist_list)

        btn_layout = QHBoxLayout()

        self.login_button = QPushButton('Login to Spotify')
        self.login_button.setObjectName('loginButton')
        btn_layout.addWidget(self.login_button)

        self.set_alarm_button = QPushButton('Set Alarm')
        self.set_alarm_button.setObjectName('setAlarmButton')
        btn_layout.addWidget(self.set_alarm_button)

        left_panel.addLayout(btn_layout)
        content.addLayout(left_panel, stretch=2)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(16)

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

        volume_label = QLabel('Alarm Volume')
        volume_label.setFont(QFont('Arial', 14, QFont.Bold))
        volume_label.setStyleSheet("color: #FFFFFF;")
        right_panel.addWidget(volume_label)

        volume_row = QHBoxLayout()

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(80)
        self.volume_slider.setObjectName('volumeSlider')
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_row.addWidget(self.volume_slider)

        self.volume_value_label = QLabel('80%')
        self.volume_value_label.setFixedWidth(45)
        self.volume_value_label.setStyleSheet("color: #B3B3B3;")
        volume_row.addWidget(self.volume_value_label)

        right_panel.addLayout(volume_row)

        self.manage_alarms_button = QPushButton('Manage Alarms')
        self.manage_alarms_button.setObjectName('manageAlarmsButton')
        right_panel.addWidget(self.manage_alarms_button)

        self.view_logs_button = QPushButton('View Logs')
        self.view_logs_button.setObjectName('viewLogsButton')
        right_panel.addWidget(self.view_logs_button)

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
                self.auth_status_label.setStyleSheet("color: #1DB954;")
            else:
                self.auth_status_label.setText('Connected')
                self.auth_status_label.setStyleSheet("color: #1DB954;")
            self._update_device_status()
        else:
            self.auth_status_label.setText('Not connected')
            self.auth_status_label.setStyleSheet("color: #B3B3B3;")
            self.device_status_label.setText('')

    def login_to_spotify(self):
        """Handle login button click - authenticate with Spotify."""
        if not self.spotify_api:
            QMessageBox.warning(
                self,
                'Missing Credentials',
                'Spotify credentials are not configured.\n\n'
                'Please click the Settings button (⚙) to enter your Spotify API credentials.'
            )
            return

        logger.info('User initiated Spotify login')
        try:
            self.spotify_api.authenticate()
            self._update_auth_status()
            self._load_playlists()
            self._update_device_status()
            logger.info('Spotify login successful')

        except Exception as e:
            error_msg = str(e)
            actionable_msg = 'Could not login to Spotify.'
            
            if 'redirect_uri' in error_msg.lower():
                actionable_msg += '\n\n⚠ Check that your Redirect URI matches the one configured in your Spotify Developer Dashboard.'
            elif 'client' in error_msg.lower():
                actionable_msg += '\n\n⚠ Verify your Client ID and Client Secret are correct in Settings.'
            elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                actionable_msg += '\n\n⚠ Check your internet connection and try again.'
            else:
                actionable_msg += f'\n\n⚠ Error: {error_msg}'
            
            logger.error(f'Spotify login failed: {e}', exc_info=True)
            QMessageBox.critical(self, 'Login Failed', actionable_msg)

    def _load_playlists(self):
        """Load user's playlists with thumbnails and metadata."""
        if not self.spotify_api:
            return

        logger.info('Loading user playlists')
        try:
            playlists = self.spotify_api.get_playlists_detailed()

            self.playlist_list.clear()
            self.playlist_widgets.clear()

            for playlist in playlists:
                widget = PlaylistItemWidget(playlist)

                item = QListWidgetItem(self.playlist_list)
                item.setSizeHint(QSize(340, 76))

                item.setData(Qt.UserRole, playlist)

                self.playlist_list.setItemWidget(item, widget)

                playlist_id = playlist.get('id', '')
                self.playlist_widgets[playlist_id] = widget

                image_url = playlist.get('image_url')
                if image_url:
                    self._load_playlist_image(playlist_id, image_url)

            logger.info(f'Loaded {len(playlists)} playlists into UI')

        except RuntimeError as e:
            logger.error(f'Failed to load playlists: {e}', exc_info=True)
            QMessageBox.warning(self, 'Failed to Load Playlists', str(e))
        except Exception as e:
            error_msg = f'Could not load playlists: {str(e)}\n\n'
            error_msg += '⚠ Make sure you are logged into Spotify and try clicking "Login to Spotify" again.'
            logger.error(f'Unexpected error loading playlists: {e}', exc_info=True)
            QMessageBox.warning(self, 'Error Loading Playlists', error_msg)

    def _load_playlist_image(self, playlist_id, image_url):
        """Start background thread to load playlist cover image."""
        loader = ImageLoaderThread(playlist_id, image_url)
        loader.image_loaded.connect(self._on_image_loaded)
        self.image_loaders.append(loader)
        loader.start()

    def _on_image_loaded(self, playlist_id, pixmap):
        """Handle loaded image - update the playlist widget."""
        widget = self.playlist_widgets.get(playlist_id)
        if widget and not pixmap.isNull():
            widget.set_image(pixmap)

    def open_settings(self):
        """Open the settings dialog for Spotify credentials."""
        logger.info('Opening settings dialog')
        dlg = SettingsDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            load_dotenv(override=True)
            try:
                self.spotify_api = SpotifyAPI()
                self.login_button.setEnabled(True)
                self.set_alarm_button.setEnabled(True)
                self._update_auth_status()
                logger.info('Spotify credentials updated successfully')
                QMessageBox.information(
                    self,
                    'Settings Saved',
                    'Spotify credentials saved successfully.\n\nPlease click "Login to Spotify" to authenticate.'
                )
            except Exception as e:
                logger.error(f'Failed to reload Spotify API after settings update: {e}', exc_info=True)
                QMessageBox.warning(
                    self,
                    'Configuration Error',
                    f'Could not load Spotify API with the provided credentials:\n\n{str(e)}'
                )

    def open_alarm_manager(self):
        """Open the alarm manager dialog."""
        logger.info('Opening alarm manager')
        dlg = AlarmManagerDialog(self.alarm, self)
        dlg.exec_()

    def open_log_viewer(self):
        """Open the log viewer dialog."""
        logger.info('Opening log viewer')
        dlg = LogViewerDialog(self)
        dlg.exec_()

    def set_alarm(self):
        """Set an alarm for the selected playlist."""
        time_str = self.time_input.time().toString('HH:mm')

        if not self._validate_alarm_time(time_str):
            return

        current = self.playlist_list.currentItem()
        if current is None:
            logger.warning('User attempted to set alarm without selecting a playlist')
            QMessageBox.warning(
                self,
                'No Playlist Selected',
                'Please select a playlist from the list before setting an alarm.'
            )
            return

        playlist_data = current.data(Qt.UserRole)
        if not playlist_data:
            QMessageBox.warning(
                self,
                'Invalid Playlist',
                'Could not retrieve playlist information. Please try selecting the playlist again.'
            )
            return

        playlist_name = playlist_data.get('name', 'Unknown')
        playlist_uri = playlist_data.get('uri')
        
        if not playlist_uri:
            QMessageBox.warning(
                self,
                'Invalid Playlist',
                'Playlist URI is missing. Please try reloading your playlists by logging in again.'
            )
            return

        if not self.spotify_api:
            logger.error('User attempted to set alarm without Spotify credentials')
            QMessageBox.warning(
                self,
                'Not Authenticated',
                'Spotify credentials are not configured.\n\n'
                'Please click Settings (⚙) to configure your credentials.'
            )
            return

        if not self.spotify_api.is_authenticated():
            QMessageBox.warning(
                self,
                'Not Logged In',
                'You are not logged into Spotify.\n\n'
                'Please click "Login to Spotify" to authenticate.'
            )
            return

        volume = self.volume_slider.value()

        logger.info(f'User setting alarm: time={time_str}, playlist={playlist_name}, volume={volume}%')

        try:
            self.alarm.set_alarm(time_str, playlist_name, playlist_uri, self.spotify_api, volume)

            message = f'Alarm scheduled for {time_str}\n\nPlaylist: {playlist_name}\nVolume: {volume}%\n\nMake sure a Spotify device is active when the alarm triggers.'
            QMessageBox.information(self, 'Alarm Set Successfully', message)
            logger.info('Alarm set successfully by user')

        except ValueError as e:
            logger.error(f'Invalid time format for alarm: {e}')
            QMessageBox.warning(
                self,
                'Invalid Alarm Time',
                f'{str(e)}\n\n'
                'Please enter a valid time in HH:MM format (24-hour).'
            )
        except Exception as e:
            logger.error(f'Failed to set alarm: {e}', exc_info=True)
            QMessageBox.critical(
                self,
                'Failed to Set Alarm',
                f'Could not set alarm: {str(e)}\n\n'
                'Please check your settings and try again.'
            )

    def _validate_alarm_time(self, time_str):
        """
        Validate alarm time format and value.

        Args:
            time_str: Time string in HH:MM format.

        Returns:
            bool: True if valid, False otherwise (displays error message).
        """
        if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', time_str):
            QMessageBox.warning(
                self,
                'Invalid Time Format',
                f'Invalid time format: {time_str}\n\n'
                'Please use HH:MM format (24-hour), e.g., 07:30 or 14:45'
            )
            return False

        try:
            hours, minutes = map(int, time_str.split(':'))
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                raise ValueError('Time out of range')
        except ValueError:
            QMessageBox.warning(
                self,
                'Invalid Time',
                f'Invalid time: {time_str}\n\n'
                'Hours must be 00-23 and minutes must be 00-59'
            )
            return False

        return True

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
        logger.info('Application closing - cleaning up resources')
        self._cleanup_resources()
        event.accept()

    def _cleanup_resources(self):
        """Clean up all background threads and resources."""
        if hasattr(self, 'device_status_timer'):
            self.device_status_timer.stop()

        for loader in self.image_loaders:
            if loader.isRunning():
                loader.stop()
                loader.wait(1000)
        
        self.image_loaders.clear()
        
        if self.alarm:
            self.alarm.shutdown()
        
        logger.info('Resource cleanup complete')

        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.hide()


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

        header = QLabel('Scheduled Alarms')
        header.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(header)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Time', 'Playlist', 'Volume', 'Actions'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        btn_close = QPushButton('Close')
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _load_alarms(self):
        """Load and display all scheduled alarms."""
        alarms = self.alarm_manager.get_alarms()
        self.table.setRowCount(len(alarms))

        for row, alarm_info in enumerate(alarms):
            self.table.setItem(row, 0, QTableWidgetItem(alarm_info.get('time', '')))
            self.table.setItem(row, 1, QTableWidgetItem(alarm_info.get('playlist', '')))
            self.table.setItem(row, 2, QTableWidgetItem(f"{alarm_info.get('volume', 80)}%"))

            btn_delete = QPushButton('Delete')
            btn_delete.clicked.connect(lambda checked, r=row: self._delete_alarm(r))
            self.table.setCellWidget(row, 3, btn_delete)

    def _delete_alarm(self, row):
        """Delete the alarm at the specified row."""
        alarms = self.alarm_manager.get_alarms()
        if 0 <= row < len(alarms):
            alarm_info = alarms[row]
            self.alarm_manager.remove_alarm(alarm_info.get('time', ''))
            self._load_alarms()


class SettingsDialog(QDialog):
    """
    Dialog for configuring Spotify API credentials.

    Allows user to enter Client ID, Client Secret, and Redirect URI.
    Saves credentials to .env file in project directory.
    Provides help button to guide users through getting credentials.
    """

    def __init__(self, parent=None):
        """Initialize the settings dialog with current credentials."""
        super().__init__(parent)
        self.setWindowTitle('Spotify Settings')
        self.setMinimumWidth(450)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        instructions = QLabel(
            "To use Alarmify, you need Spotify API credentials.\n"
            "Click 'Get Credentials' to create them (takes 2 minutes)."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #b3b3b3; margin-bottom: 10px;")
        layout.addWidget(instructions)

        btn_get_creds = QPushButton('Get Credentials (Open Spotify Developer)', self)
        btn_get_creds.setStyleSheet(
            "background-color: #1DB954; color: white; padding: 10px; "
            "font-weight: bold; border-radius: 5px;"
        )
        btn_get_creds.clicked.connect(self._open_spotify_dashboard)
        layout.addWidget(btn_get_creds)

        separator = QLabel("— Then paste your credentials below —")
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("color: #666; margin: 10px 0;")
        layout.addWidget(separator)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.client_id = QLineEdit(self)
        self.client_id.setPlaceholderText('Paste your Client ID here')

        self.client_secret = QLineEdit(self)
        self.client_secret.setPlaceholderText('Paste your Client Secret here')
        self.client_secret.setEchoMode(QLineEdit.Password)

        self.redirect_uri = QLineEdit(self)
        self.redirect_uri.setText('http://localhost:8888/callback')
        self.redirect_uri.setStyleSheet("color: #888;")

        load_dotenv()
        if os.getenv('SPOTIPY_CLIENT_ID'):
            self.client_id.setText(os.getenv('SPOTIPY_CLIENT_ID', ''))
        if os.getenv('SPOTIPY_CLIENT_SECRET'):
            self.client_secret.setText(os.getenv('SPOTIPY_CLIENT_SECRET', ''))
        if os.getenv('SPOTIPY_REDIRECT_URI'):
            self.redirect_uri.setText(os.getenv('SPOTIPY_REDIRECT_URI'))

        form_layout.addRow('Client ID:', self.client_id)
        form_layout.addRow('Client Secret:', self.client_secret)
        form_layout.addRow('Redirect URI:', self.redirect_uri)

        layout.addLayout(form_layout)

        uri_note = QLabel(
            "Note: Add this exact Redirect URI in your Spotify app settings."
        )
        uri_note.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(uri_note)

        btn_layout = QHBoxLayout()

        btn_cancel = QPushButton('Cancel', self)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton('Save & Connect', self)
        btn_save.clicked.connect(self.save)
        btn_save.setDefault(True)
        btn_save.setStyleSheet(
            "background-color: #1DB954; color: white; padding: 8px 16px;"
        )
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def _open_spotify_dashboard(self):
        """Open Spotify Developer Dashboard in browser with instructions."""
        import webbrowser
        QMessageBox.information(
            self,
            'How to Get Credentials',
            "1. Log in with your Spotify account\n"
            "2. Click 'Create app'\n"
            "3. Enter any name (e.g., 'Alarmify')\n"
            "4. Enter any description\n"
            "5. Set Redirect URI to:\n"
            "   http://localhost:8888/callback\n"
            "6. Check 'Web API'\n"
            "7. Click 'Save'\n"
            "8. Copy Client ID and Client Secret\n"
            "9. Paste them in this dialog"
        )
        webbrowser.open('https://developer.spotify.com/dashboard')

    def save(self):
        """Validate and save credentials to .env file."""
        root = Path(__file__).resolve().parent
        env_path = root / '.env'

        try:
            cid = self.client_id.text().strip()
            csec = self.client_secret.text().strip()
            ruri = self.redirect_uri.text().strip()

            if not cid or not csec:
                QMessageBox.warning(
                    self,
                    'Validation Error',
                    'Client ID and Client Secret are required.\n\n'
                    'Get these from your Spotify Developer Dashboard:\n'
                    'https://developer.spotify.com/dashboard'
                )
                return

            if not ruri:
                QMessageBox.warning(
                    self,
                    'Validation Error',
                    'Redirect URI is required.\n\nDefault: http://localhost:8888/callback'
                )
                return

            if not (ruri.startswith('http://') or ruri.startswith('https://')):
                QMessageBox.warning(
                    self,
                    'Validation Error',
                    'Redirect URI must start with http:// or https://\n\n'
                    'This must match the Redirect URI configured in your Spotify app settings.'
                )
                return

            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(f"SPOTIPY_CLIENT_ID={cid}\n")
                f.write(f"SPOTIPY_CLIENT_SECRET={csec}\n")
                f.write(f"SPOTIPY_REDIRECT_URI={ruri}\n")

            load_dotenv(override=True)

            self.accept()

        except PermissionError:
            QMessageBox.critical(
                self, 
                'Permission Denied', 
                'Could not save credentials. Please check file permissions.'
            )
        except Exception as e:
            logger.error(f'Failed to save settings: {e}', exc_info=True)
            QMessageBox.critical(
                self,
                'Save Error',
                f'Could not save credentials: {str(e)}\n\n'
                'Check that you have write permissions in the application directory.'
            )


class LogViewerDialog(QDialog):
    """
    Dialog for viewing and exporting application logs.
    
    Displays log entries in a text area with automatic refresh capability.
    Provides export functionality to save logs to a file.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the log viewer dialog.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle('Log Viewer')
        self.setMinimumSize(800, 600)
        self.setModal(False)
        
        self._build_ui()
        self._load_logs()
    
    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        
        title = QLabel('Application Logs')
        title.setFont(QFont('Arial', 14, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.log_file_combo = QtWidgets.QComboBox()
        self.log_file_combo.setMinimumWidth(300)
        self.log_file_combo.currentIndexChanged.connect(self._on_log_file_changed)
        header_layout.addWidget(QLabel('Log File:'))
        header_layout.addWidget(self.log_file_combo)
        
        layout.addLayout(header_layout)
        
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Courier New', 9))
        self.log_text.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        layout.addWidget(self.log_text)
        
        btn_layout = QHBoxLayout()
        
        btn_refresh = QPushButton('Refresh')
        btn_refresh.clicked.connect(self._load_logs)
        btn_layout.addWidget(btn_refresh)
        
        btn_export = QPushButton('Export Logs...')
        btn_export.clicked.connect(self._export_logs)
        btn_layout.addWidget(btn_export)
        
        btn_open_folder = QPushButton('Open Log Folder')
        btn_open_folder.clicked.connect(self._open_log_folder)
        btn_layout.addWidget(btn_open_folder)
        
        btn_layout.addStretch()
        
        btn_close = QPushButton('Close')
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
    
    def _load_logs(self):
        """Load and display logs from the current log file."""
        log_files = get_log_files()
        current_text = self.log_file_combo.currentText()
        
        self.log_file_combo.clear()
        if not log_files:
            self.log_text.setPlainText('No log files found.')
            return
        
        for log_file in log_files:
            self.log_file_combo.addItem(log_file.name, log_file)
        
        if current_text:
            index = self.log_file_combo.findText(current_text)
            if index >= 0:
                self.log_file_combo.setCurrentIndex(index)
        
        self._display_current_log()
    
    def _on_log_file_changed(self, index):
        """Handle log file selection change."""
        self._display_current_log()
    
    def _display_current_log(self):
        """Display the currently selected log file."""
        log_file = self.log_file_combo.currentData()
        if not log_file:
            self.log_text.setPlainText('No log file selected.')
            return
        
        try:
            content = read_log_file(log_file, max_lines=10000)
            self.log_text.setPlainText(content)
            self.log_text.verticalScrollBar().setValue(
                self.log_text.verticalScrollBar().maximum()
            )
        except Exception as e:
            self.log_text.setPlainText(f'Error loading log file: {e}')
    
    def _export_logs(self):
        """Export current log to a user-selected file."""
        log_file = self.log_file_combo.currentData()
        if not log_file:
            QMessageBox.warning(self, 'No Log File', 'No log file selected.')
            return
        
        export_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            'Export Logs',
            f'alarmify_logs_export.log',
            'Log Files (*.log);;Text Files (*.txt);;All Files (*.*)'
        )
        
        if export_path:
            try:
                import shutil
                shutil.copy2(log_file, export_path)
                logger.info(f'Logs exported to: {export_path}')
                QMessageBox.information(
                    self,
                    'Export Successful',
                    f'Logs exported to:\n{export_path}'
                )
            except Exception as e:
                logger.error(f'Failed to export logs: {e}', exc_info=True)
                QMessageBox.critical(
                    self,
                    'Export Failed',
                    f'Could not export logs: {e}'
                )
    
    def _open_log_folder(self):
        """Open the logs folder in the file explorer."""
        from logging_config import LOG_DIR
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Windows':
                os.startfile(LOG_DIR)
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', LOG_DIR])
            else:
                subprocess.Popen(['xdg-open', LOG_DIR])
            logger.info('Opened logs folder in file explorer')
        except Exception as e:
            logger.error(f'Failed to open log folder: {e}', exc_info=True)
            QMessageBox.warning(
                self,
                'Error',
                f'Could not open log folder: {e}'
            )
