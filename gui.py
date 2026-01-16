"""
gui.py - Main GUI module for Alarmify

This module provides the main application window and all UI components:
- AlarmApp: Main window with playlist browser, alarm controls
- PlaylistItemWidget: Custom widget for playlist items with thumbnails
- SettingsDialog: Dialog for Spotify API credentials
- AlarmManagerDialog: Dialog to view/delete scheduled alarms
- LogViewerDialog: Dialog to view and export application logs
- CrashReportDialog: Dialog to display crash details and save crash logs

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
    QSystemTrayIcon,
    QMenu,
    QAction,
    QComboBox,
    QStatusBar,
    QCheckBox,
    QButtonGroup,
    QRadioButton,
    QTextEdit,
    QFileDialog
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QFontDatabase
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QByteArray, QTimer, QPropertyAnimation, QEasingCurve
from pathlib import Path
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import re
import traceback
import sys

# Local module imports
from spotify_api.spotify_api import ThreadSafeSpotifyAPI  # Thread-safe Spotify API wrapper
from alarm import Alarm, AlarmTemplate, TemplateManager, AlarmHistory  # Alarm scheduling and templates
from logging_config import get_logger, get_log_files, read_log_file, get_current_log_file
from charm_stylesheet import get_stylesheet
from charm_animations import AnimationBuilder, apply_entrance_animations
from icon_generator import generate_icon_image, generate_tray_icon

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
        self._is_hovered = False
        self.hover_animation = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(16)

        self.image_label = QLabel()
        self.image_label.setFixedSize(72, 72)
        self.image_label.setStyleSheet(
            "background: rgba(40, 40, 40, 0.7); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);"
        )
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        self.name_label = QLabel(playlist_data.get('name', 'Unknown'))
        self.name_label.setFont(QFont('Inter', 14, QFont.Bold))
        self.name_label.setStyleSheet("color: #FFFFFF;")
        text_layout.addWidget(self.name_label)

        track_count = playlist_data.get('track_count', 0)
        owner = playlist_data.get('owner', 'Unknown')
        info_text = f"{track_count} tracks • {owner}"
        self.info_label = QLabel(info_text)
        self.info_label.setFont(QFont('Inter', 11))
        self.info_label.setStyleSheet("color: #b3b3b3;")
        text_layout.addWidget(self.info_label)

        text_layout.addStretch()

        layout.addLayout(text_layout)
        layout.addStretch()

        self.setMouseTracking(True)
        
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                border-radius: 8px;
            }
        """)

    def set_image(self, pixmap):
        """
        Set the playlist cover image.

        Args:
            pixmap: QPixmap of the cover image.
        """
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                72, 72,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

    def enterEvent(self, event):
        """Handle mouse enter event for hover effect with animation."""
        self._is_hovered = True
        
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(42, 42, 42, 0.9),
                    stop:1 rgba(29, 185, 84, 0.1));
                border-radius: 8px;
                border-left: 3px solid rgba(29, 185, 84, 0.5);
            }
        """)
        
        if not self.hover_animation:
            self.hover_animation = AnimationBuilder.create_fade_in(self, 150)
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event to remove hover effect."""
        self._is_hovered = False
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                border-radius: 8px;
            }
        """)
        super().leaveEvent(event)

    def contextMenuEvent(self, event):
        """Show context menu for playlist actions."""
        menu = QMenu(self)
        
        play_action = QAction("Play Now", self)
        play_action.triggered.connect(self._play_playlist)
        menu.addAction(play_action)
        
        menu.exec_(event.globalPos())

    def _play_playlist(self):
        """Play this playlist immediately for testing."""
        parent = self.parent()
        while parent and not isinstance(parent, AlarmApp):
            parent = parent.parent()
        
        if parent and isinstance(parent, AlarmApp):
            parent.play_playlist_now(self.playlist_data.get('uri'))


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
    - System tray icon support
    - Device selector
    - Theme toggle
    """

    def __init__(self):
        """Initialize the main window and all UI components."""
        super(AlarmApp, self).__init__()
        
        logger.info('Initializing Alarmify main window with Charm design')

        self.image_loaders = []
        self.playlist_widgets = {}
        self.current_theme = 'dark'
        self.last_sync_time = None
        
        self._load_custom_fonts()
        
        self._build_ui()
        self._apply_theme()
        
        self._setup_entrance_animations()

        # Check for test mode
        test_mode = os.getenv('ALARMIFY_TEST_MODE', 'False').lower() == 'true'
        
        if test_mode:
            logger.info('TEST MODE: Using Mock Spotify API')
            from spotify_api.mock_spotify import MockThreadSafeSpotifyAPI
            self.spotify_api = MockThreadSafeSpotifyAPI()
        else:
            try:
                self.spotify_api = ThreadSafeSpotifyAPI()
            except RuntimeError as e:
                logger.warning('Spotify credentials not configured')
                QMessageBox.warning(
                    self,
                    'Spotify Credentials Required',
                    f'{e}\n\nPlease click the Settings button (⚙) to configure your Spotify API credentials.'
                )
                self.spotify_api = None

        self.alarm = Alarm(self)
        self.template_manager = TemplateManager()

        self.login_button.clicked.connect(self.login_to_spotify)
        self.set_alarm_button.clicked.connect(self.set_alarm)
        self.settings_button.clicked.connect(self.open_settings)
        self.manage_alarms_button.clicked.connect(self.open_alarm_manager)
        self.view_logs_button.clicked.connect(self.open_log_viewer)
        self.manage_templates_button.clicked.connect(self.open_template_manager)
        self.view_history_button.clicked.connect(self.open_history_stats)
        self.quick_setup_button.clicked.connect(self.quick_setup_from_template)
        self.device_selector.currentIndexChanged.connect(self._on_device_changed)
        self.refresh_devices_button.clicked.connect(self._refresh_devices)
        self.playlist_search.textChanged.connect(self._filter_playlists)

        if not self.spotify_api:
            self.login_button.setEnabled(False)
            self.set_alarm_button.setEnabled(False)

        self._setup_system_tray()
        self._update_auth_status()
        self._start_device_status_monitor()
        
        self.alarm_countdown_timer = QTimer(self)
        self.alarm_countdown_timer.timeout.connect(self._update_next_alarm_display)
        self.alarm_countdown_timer.start(1000)
        
        self._update_next_alarm_display()

        if self.spotify_api and self.spotify_api.is_authenticated():
            logger.info('Auto-loading playlists (cached authentication)')
            self._load_playlists()
            self._refresh_devices()
            self.alarm.reschedule_snoozed_alarms(self.spotify_api)

    def _load_custom_fonts(self):
        """Load custom fonts (Inter and JetBrains Mono)."""
        font_db = QFontDatabase()
        
        fonts_to_load = [
            'Inter',
            'JetBrains Mono'
        ]
        
        for font_name in fonts_to_load:
            font_id = font_db.addApplicationFont(font_name)
            if font_id >= 0:
                logger.info(f'Loaded custom font: {font_name}')
            else:
                logger.warning(f'Could not load custom font: {font_name}, using system fallback')
    
    def _setup_entrance_animations(self):
        """Apply entrance animations to UI elements."""
        widgets_to_animate = []
        
        if hasattr(self, 'playlist_list'):
            widgets_to_animate.append(self.playlist_list)
        
        if hasattr(self, 'time_input'):
            widgets_to_animate.append(self.time_input)
        
        apply_entrance_animations(widgets_to_animate, stagger_delay=100)

    def _build_ui(self):
        """Build the complete UI layout programmatically with Charm design."""
        self.setWindowTitle('Alarmify - Spotify Alarm Clock')
        self.setMinimumSize(1100, 750)
        
        app_icon = QIcon()
        icon_image = generate_icon_image(256)
        app_icon.addPixmap(QPixmap.fromImage(icon_image))
        self.setWindowIcon(app_icon)

        self.central_widget = QWidget()
        self.central_widget.setObjectName('centralWidget')
        self.setCentralWidget(self.central_widget)

        root_layout = QVBoxLayout(self.central_widget)
        root_layout.setContentsMargins(32, 32, 32, 32)
        root_layout.setSpacing(24)

        # Header with logo and status
        header = QHBoxLayout()
        header.setSpacing(20)

        header_container = QHBoxLayout()
        header_container.setSpacing(12)
        
        icon_label = QLabel()
        icon_pixmap = QPixmap.fromImage(generate_icon_image(48))
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(48, 48)
        header_container.addWidget(icon_label)
        
        logo = QLabel('Alarmify')
        logo.setObjectName('appLogo')
        logo.setFont(QFont('Inter', 32, QFont.Bold))
        header_container.addWidget(logo)
        
        header.addLayout(header_container)

        header.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        status_layout = QVBoxLayout()
        status_layout.setSpacing(6)
        status_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)

        self.auth_status_label = QLabel('Not connected')
        self.auth_status_label.setObjectName('authStatus')
        status_layout.addWidget(self.auth_status_label)

        self.device_status_label = QLabel('No active device')
        self.device_status_label.setObjectName('deviceStatus')
        status_layout.addWidget(self.device_status_label)

        header.addLayout(status_layout)

        self.settings_button = QPushButton('\u2699')
        self.settings_button.setObjectName('settingsButton')
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.setToolTip('Settings')
        header.addWidget(self.settings_button)

        root_layout.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(24)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)

        playlist_header = QLabel('Your Playlists')
        playlist_header.setObjectName('sectionHeader')
        playlist_header.setFont(QFont('Inter', 18, QFont.Bold))
        left_panel.addWidget(playlist_header)

        search_container = QHBoxLayout()
        search_container.setSpacing(8)
        
        search_icon = QLabel('🔍')
        search_icon.setStyleSheet("font-size: 18px; padding: 0 8px;")
        
        self.playlist_search = QLineEdit()
        self.playlist_search.setPlaceholderText('Search playlists...')
        self.playlist_search.setObjectName('playlistSearch')
        self.playlist_search.setMinimumHeight(48)
        
        search_container.addWidget(search_icon)
        search_container.addWidget(self.playlist_search)
        
        left_panel.addLayout(search_container)

        self.playlist_list = QListWidget()
        self.playlist_list.setObjectName('playlistList')
        self.playlist_list.setMinimumWidth(450)
        self.playlist_list.setSpacing(8)
        self.playlist_list.setContextMenuPolicy(Qt.CustomContextMenu)
        left_panel.addWidget(self.playlist_list)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.login_button = QPushButton('Login to Spotify')
        self.login_button.setObjectName('loginButton')
        btn_layout.addWidget(self.login_button)

        self.set_alarm_button = QPushButton('Set Alarm')
        self.set_alarm_button.setObjectName('setAlarmButton')
        btn_layout.addWidget(self.set_alarm_button)

        left_panel.addLayout(btn_layout)
        content.addLayout(left_panel, stretch=2)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)

        device_label = QLabel('Playback Device')
        device_label.setObjectName('sectionHeader')
        device_label.setFont(QFont('Inter', 18, QFont.Bold))
        right_panel.addWidget(device_label)

        device_row = QHBoxLayout()
        device_row.setSpacing(8)
        self.device_selector = QComboBox()
        self.device_selector.setObjectName('deviceSelector')
        self.device_selector.setMinimumHeight(44)
        device_row.addWidget(self.device_selector, stretch=1)

        self.refresh_devices_button = QPushButton('\u21bb')
        self.refresh_devices_button.setObjectName('refreshButton')
        self.refresh_devices_button.setFixedSize(44, 44)
        self.refresh_devices_button.setToolTip('Refresh devices')
        device_row.addWidget(self.refresh_devices_button)

        right_panel.addLayout(device_row)

        time_label = QLabel('Alarm Time')
        time_label.setObjectName('sectionHeader')
        time_label.setFont(QFont('Inter', 18, QFont.Bold))
        right_panel.addWidget(time_label)

        self.time_input = QTimeEdit(self)
        self.time_input.setDisplayFormat('HH:mm')
        self.time_input.setObjectName('timeInput')
        self.time_input.setFont(QFont('JetBrains Mono', 32, QFont.Bold))
        self.time_input.setMinimumHeight(80)
        self.time_input.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.time_input)

        next_alarm_container = QWidget()
        next_alarm_container.setObjectName('nextAlarmContainer')
        next_alarm_layout = QVBoxLayout(next_alarm_container)
        next_alarm_layout.setContentsMargins(16, 12, 16, 12)
        next_alarm_layout.setSpacing(8)
        
        next_alarm_header = QHBoxLayout()
        next_alarm_title = QLabel('Next Alarm')
        next_alarm_title.setFont(QFont('Inter', 12, QFont.Bold))
        next_alarm_title.setStyleSheet('color: #1DB954;')
        next_alarm_header.addWidget(next_alarm_title)
        next_alarm_header.addStretch()
        
        self.preview_button = QPushButton('View All')
        self.preview_button.setObjectName('previewButton')
        self.preview_button.setToolTip('View all upcoming alarms')
        self.preview_button.clicked.connect(self.open_alarm_preview)
        self.preview_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #1DB954;
                border: 1px solid #1DB954;
                border-radius: 4px;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1DB954;
                color: #000000;
            }
        """)
        next_alarm_header.addWidget(self.preview_button)
        
        next_alarm_layout.addLayout(next_alarm_header)
        
        self.next_alarm_time_label = QLabel('--:--')
        self.next_alarm_time_label.setFont(QFont('JetBrains Mono', 20, QFont.Bold))
        self.next_alarm_time_label.setStyleSheet('color: #ffffff;')
        next_alarm_layout.addWidget(self.next_alarm_time_label)
        
        self.next_alarm_countdown_label = QLabel('No alarms scheduled')
        self.next_alarm_countdown_label.setFont(QFont('Inter', 11))
        self.next_alarm_countdown_label.setStyleSheet('color: #888888;')
        next_alarm_layout.addWidget(self.next_alarm_countdown_label)
        
        next_alarm_container.setStyleSheet("""
            #nextAlarmContainer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(29, 185, 84, 0.15),
                    stop:1 rgba(29, 185, 84, 0.05));
                border: 1px solid rgba(29, 185, 84, 0.3);
                border-radius: 8px;
            }
        """)
        
        right_panel.addWidget(next_alarm_container)

        volume_label = QLabel('Alarm Volume')
        volume_label.setObjectName('sectionHeader')
        volume_label.setFont(QFont('Inter', 18, QFont.Bold))
        right_panel.addWidget(volume_label)

        volume_row = QHBoxLayout()
        volume_row.setSpacing(12)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(80)
        self.volume_slider.setObjectName('volumeSlider')
        self.volume_slider.setMinimumHeight(24)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_row.addWidget(self.volume_slider)

        self.volume_value_label = QLabel('80%')
        self.volume_value_label.setFixedWidth(50)
        self.volume_value_label.setStyleSheet("color: #b3b3b3; font-size: 14px; font-weight: 600;")
        self.volume_value_label.setAlignment(Qt.AlignCenter)
        volume_row.addWidget(self.volume_value_label)

        right_panel.addLayout(volume_row)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(12)

        self.quick_setup_button = QPushButton('⚡ Quick Setup from Template')
        self.quick_setup_button.setObjectName('quickSetupButton')
        self.quick_setup_button.setToolTip('Create alarm from saved template')
        button_layout.addWidget(self.quick_setup_button)

        self.manage_alarms_button = QPushButton('Manage Alarms')
        self.manage_alarms_button.setObjectName('manageAlarmsButton')
        button_layout.addWidget(self.manage_alarms_button)

        self.manage_templates_button = QPushButton('Manage Templates')
        self.manage_templates_button.setObjectName('manageTemplatesButton')
        button_layout.addWidget(self.manage_templates_button)

        self.view_history_button = QPushButton('History & Stats')
        self.view_history_button.setObjectName('viewHistoryButton')
        button_layout.addWidget(self.view_history_button)

        self.view_logs_button = QPushButton('View Logs')
        self.view_logs_button.setObjectName('viewLogsButton')
        button_layout.addWidget(self.view_logs_button)

        right_panel.addLayout(button_layout)

        right_panel.addStretch()

        content.addLayout(right_panel, stretch=1)
        root_layout.addLayout(content)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setObjectName('statusBar')
        
        self.connection_status_label = QLabel('Disconnected')
        self.sync_time_label = QLabel('Last sync: Never')
        
        self.status_bar.addPermanentWidget(self.connection_status_label)
        self.status_bar.addPermanentWidget(QLabel('  |  '))
        self.status_bar.addPermanentWidget(self.sync_time_label)

    def _setup_system_tray(self):
        """Setup system tray icon with menu."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray_icon = QSystemTrayIcon(self)
        
        tray_icon_image = generate_tray_icon(32)
        tray_icon_pixmap = QPixmap.fromImage(tray_icon_image)
        self.tray_icon.setIcon(QIcon(tray_icon_pixmap))

        self.tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self._show_window)
        self.tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        self.tray_menu.addAction(hide_action)
        
        self.tray_menu.addSeparator()
        
        # Snooze section (initially hidden, shown when alarm triggers)
        self.snooze_section_separator = self.tray_menu.addSeparator()
        self.snooze_section_separator.setVisible(False)
        
        self.snooze_5min_action = QAction("⏰ Snooze 5 minutes", self)
        self.snooze_5min_action.triggered.connect(lambda: self._snooze_from_tray(5))
        self.tray_menu.addAction(self.snooze_5min_action)
        self.snooze_5min_action.setVisible(False)
        
        self.snooze_10min_action = QAction("⏰ Snooze 10 minutes", self)
        self.snooze_10min_action.triggered.connect(lambda: self._snooze_from_tray(10))
        self.tray_menu.addAction(self.snooze_10min_action)
        self.snooze_10min_action.setVisible(False)
        
        self.snooze_15min_action = QAction("⏰ Snooze 15 minutes", self)
        self.snooze_15min_action.triggered.connect(lambda: self._snooze_from_tray(15))
        self.tray_menu.addAction(self.snooze_15min_action)
        self.snooze_15min_action.setVisible(False)
        
        self.dismiss_alarm_action = QAction("❌ Dismiss Alarm", self)
        self.dismiss_alarm_action.triggered.connect(self._dismiss_alarm_from_tray)
        self.tray_menu.addAction(self.dismiss_alarm_action)
        self.dismiss_alarm_action.setVisible(False)
        
        self.snooze_bottom_separator = self.tray_menu.addSeparator()
        self.snooze_bottom_separator.setVisible(False)
        
        self.tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_application)
        self.tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self._tray_icon_activated)
        self.tray_icon.show()
        
        # Store current alarm data for snooze
        self.current_alarm_data = None

    def _tray_icon_activated(self, reason):
        """Handle tray icon clicks."""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_window()
    
    def _show_snooze_in_tray(self, alarm_data):
        """
        Show snooze options in system tray menu.
        
        Args:
            alarm_data: Alarm data dictionary for snooze functionality.
        """
        self.current_alarm_data = alarm_data
        
        self.snooze_section_separator.setVisible(True)
        self.snooze_5min_action.setVisible(True)
        self.snooze_10min_action.setVisible(True)
        self.snooze_15min_action.setVisible(True)
        self.dismiss_alarm_action.setVisible(True)
        self.snooze_bottom_separator.setVisible(True)
        
        logger.info("Snooze options shown in system tray menu")
    
    def _hide_snooze_from_tray(self):
        """Hide snooze options from system tray menu."""
        self.snooze_section_separator.setVisible(False)
        self.snooze_5min_action.setVisible(False)
        self.snooze_10min_action.setVisible(False)
        self.snooze_15min_action.setVisible(False)
        self.dismiss_alarm_action.setVisible(False)
        self.snooze_bottom_separator.setVisible(False)
        
        self.current_alarm_data = None
        
        logger.info("Snooze options hidden from system tray menu")
    
    def _snooze_from_tray(self, minutes):
        """
        Snooze alarm from system tray.
        
        Args:
            minutes: Number of minutes to snooze.
        """
        if not self.current_alarm_data:
            logger.warning("No alarm data available for snooze")
            return
        
        logger.info(f"Snoozing alarm for {minutes} minutes from system tray")
        
        if self.alarm:
            self.alarm.snooze_alarm(self.current_alarm_data, minutes)
            self.tray_icon.showMessage(
                'Alarm Snoozed',
                f'Alarm snoozed for {minutes} minutes',
                QSystemTrayIcon.Information,
                3000
            )
        
        self._hide_snooze_from_tray()
    
    def _dismiss_alarm_from_tray(self):
        """Dismiss alarm from system tray."""
        logger.info("Dismissing alarm from system tray")
        
        # Record dismissal in history if current_alarm_data exists
        if self.current_alarm_data and hasattr(self, 'alarm'):
            self.alarm.history.record_dismiss(self.current_alarm_data)
        
        self._hide_snooze_from_tray()
        
        self.tray_icon.showMessage(
            'Alarm Dismissed',
            'Alarm dismissed',
            QSystemTrayIcon.Information,
            2000
        )

    def show_tray_notification(self, title, message, icon_type=QSystemTrayIcon.Information):
        """
        Show a system tray notification.
        
        Args:
            title: Notification title.
            message: Notification message.
            icon_type: QSystemTrayIcon icon type (Information, Warning, Critical).
        """
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.showMessage(title, message, icon_type, 5000)
    
    def show_snooze_notification(self, title, message, alarm_data, icon_type=QSystemTrayIcon.Information):
        """
        Show a snooze notification dialog when alarm triggers.
        
        Args:
            title: Notification title.
            message: Notification message.
            alarm_data: Alarm data dictionary for snooze functionality.
            icon_type: QSystemTrayIcon icon type.
        """
        logger.info('Showing snooze notification dialog')
        dlg = SnoozeNotificationDialog(self, title, message, alarm_data)
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()
        
        # Show snooze options in system tray
        self._show_snooze_in_tray(alarm_data)
        
        # Also show tray notification
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.showMessage(title, message, icon_type, 5000)

    def _show_window(self):
        """Show and activate the main window."""
        self.show()
        self.activateWindow()
        self.raise_()

    def _quit_application(self):
        """Quit the application completely."""
        self._cleanup_resources()
        QtWidgets.QApplication.quit()

    def _apply_theme(self):
        """Apply the current theme using the Charm design system."""
        stylesheet = get_stylesheet(self.current_theme)
        self.setStyleSheet(stylesheet)
        logger.info(f'Applied {self.current_theme} theme with Charm design system')

    def _toggle_theme(self):
        """Toggle between dark and light themes."""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self._apply_theme()

    def _on_volume_changed(self, value):
        """Update volume label when slider moves."""
        self.volume_value_label.setText(f'{value}%')

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

    def _update_auth_status(self):
        """Update the authentication status display."""
        if self.spotify_api and self.spotify_api.is_authenticated():
            user = self.spotify_api.get_current_user()
            is_premium = self.spotify_api.is_premium_user()
            
            if user:
                name = user.get('display_name', 'User')
                status_text = f'Connected as {name}'
                if is_premium:
                    status_text += ' ✓ Premium'
                elif is_premium is False:
                    status_text += ' (Free)'
                self.auth_status_label.setText(status_text)
                self.auth_status_label.setStyleSheet("color: #1DB954;")
                self.connection_status_label.setText('Connected')
            else:
                self.auth_status_label.setText('Connected')
                self.auth_status_label.setStyleSheet("color: #1DB954;")
                self.connection_status_label.setText('Connected')
            self._update_device_status()
        else:
            self.auth_status_label.setText('Not connected')
            self.auth_status_label.setStyleSheet("color: #B3B3B3;")
            self.connection_status_label.setText('Disconnected')
            self.device_status_label.setText('')

    def _update_next_alarm_display(self):
        """Update the next alarm display with time and countdown."""
        next_datetime = self.alarm.get_next_alarm_datetime()
        
        if next_datetime:
            time_str = next_datetime.strftime('%H:%M')
            self.next_alarm_time_label.setText(time_str)
            
            now = datetime.now()
            delta = next_datetime - now
            
            total_seconds = int(delta.total_seconds())
            if total_seconds < 0:
                self.next_alarm_countdown_label.setText('Alarm triggering...')
                return
            
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 48:
                days = hours // 24
                countdown_text = f'in {days} day{"s" if days != 1 else ""}'
            elif hours > 0:
                countdown_text = f'in {hours}h {minutes}m {seconds}s'
            elif minutes > 0:
                countdown_text = f'in {minutes}m {seconds}s'
            else:
                countdown_text = f'in {seconds}s'
            
            date_str = next_datetime.strftime('%a, %b %d')
            self.next_alarm_countdown_label.setText(f'{countdown_text} • {date_str}')
        else:
            self.next_alarm_time_label.setText('--:--')
            self.next_alarm_countdown_label.setText('No alarms scheduled')

    def _refresh_devices(self):
        """Refresh the device selector with available Spotify devices."""
        if not self.spotify_api or not self.spotify_api.is_authenticated():
            return

        devices = self.spotify_api.get_devices()
        
        self.device_selector.clear()
        self.device_selector.addItem('Auto (Use Active Device)', None)
        
        for device in devices:
            device_name = device.get('name', 'Unknown Device')
            device_type = device.get('type', '')
            is_active = device.get('is_active', False)
            
            if is_active:
                device_name += ' (Active)'
            
            display_text = f"{device_name} - {device_type}"
            self.device_selector.addItem(display_text, device.get('id'))

    def _on_device_changed(self, index):
        """Handle device selector change."""
        device_id = self.device_selector.itemData(index)
        if device_id and self.spotify_api:
            try:
                self.spotify_api.transfer_playback(device_id, force_play=False)
                QMessageBox.information(self, 'Device Changed', 'Playback device updated.')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Could not change device: {e}')

    def _filter_playlists(self, text):
        """Filter playlist list based on search text."""
        search_text = text.lower()
        
        for i in range(self.playlist_list.count()):
            item = self.playlist_list.item(i)
            widget = self.playlist_list.itemWidget(item)
            
            if widget:
                playlist_name = widget.playlist_data.get('name', '').lower()
                if search_text in playlist_name:
                    item.setHidden(False)
                else:
                    item.setHidden(True)

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
            self._refresh_devices()
            self._update_device_status()
            self.alarm.reschedule_snoozed_alarms(self.spotify_api)
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
                item.setSizeHint(QSize(380, 88))

                item.setData(Qt.UserRole, playlist)

                self.playlist_list.setItemWidget(item, widget)

                playlist_id = playlist.get('id', '')
                self.playlist_widgets[playlist_id] = widget

                image_url = playlist.get('image_url')
                if image_url:
                    self._load_playlist_image(playlist_id, image_url)

            self.last_sync_time = datetime.now()
            self.sync_time_label.setText(f'Last sync: {self.last_sync_time.strftime("%H:%M:%S")}')

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

    def play_playlist_now(self, playlist_uri):
        """Play a playlist immediately (for testing from context menu)."""
        if not self.spotify_api:
            QMessageBox.warning(self, 'Error', 'Not authenticated.')
            return

        try:
            self.spotify_api.play_playlist_by_uri(playlist_uri)
            QMessageBox.information(self, 'Playing', 'Playlist playback started.')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not play playlist: {e}')

    def open_settings(self):
        """Open the settings dialog for Spotify credentials."""
        logger.info('Opening settings dialog')
        dlg = SettingsDialog(self, self.current_theme)
        if dlg.exec_() == QDialog.Accepted:
            theme_changed = dlg.theme_changed
            if theme_changed:
                self._toggle_theme()
            
            # Reload environment and recreate ThreadSafeSpotifyAPI
            load_dotenv(override=True)
            try:
                self.spotify_api = ThreadSafeSpotifyAPI()
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
        self._update_next_alarm_display()
    
    def open_alarm_preview(self):
        """Open the alarm preview dialog showing upcoming alarms."""
        logger.info('Opening alarm preview dialog')
        dlg = AlarmPreviewDialog(self.alarm, self)
        dlg.exec_()

    def open_log_viewer(self):
        """Open the log viewer dialog."""
        logger.info('Opening log viewer')
        dlg = LogViewerDialog(self)
        dlg.exec_()

    def open_history_stats(self):
        """Open the alarm history and statistics dashboard."""
        logger.info('Opening alarm history and statistics dashboard')
        dlg = AlarmHistoryStatsDialog(self.alarm, self)
        dlg.exec_()

    def open_template_manager(self):
        """Open the template manager dialog."""
        logger.info('Opening template manager')
        dlg = TemplateManagerDialog(self.template_manager, self)
        dlg.exec_()

    def quick_setup_from_template(self):
        """Quick setup alarm from a saved template."""
        logger.info('Opening quick setup from template')
        templates = self.template_manager.load_templates()
        
        if not templates:
            QMessageBox.information(
                self,
                'No Templates',
                'No templates available.\n\nCreate templates in the Template Manager first.'
            )
            return
        
        dlg = QuickSetupDialog(templates, self)
        if dlg.exec_() == QDialog.Accepted:
            selected_template = dlg.selected_template
            if selected_template:
                self._apply_template(selected_template)

    def _apply_template(self, template: AlarmTemplate):
        """
        Apply a template to create a new alarm.
        
        Args:
            template: AlarmTemplate to apply.
        """
        if not self.spotify_api or not self.spotify_api.is_authenticated():
            QMessageBox.warning(
                self,
                'Not Logged In',
                'You are not logged into Spotify.\n\n'
                'Please click "Login to Spotify" to authenticate.'
            )
            return
        
        try:
            self.alarm.set_alarm(
                template.time,
                template.playlist_name,
                template.playlist_uri,
                self.spotify_api,
                template.volume,
                template.fade_in_enabled,
                template.fade_in_duration,
                template.days
            )
            
            message = f'Alarm created from template "{template.name}"\n\n'
            message += f'Time: {template.time}\n'
            message += f'Playlist: {template.playlist_name}\n'
            message += f'Volume: {template.volume}%'
            
            if template.fade_in_enabled:
                message += f'\nFade-in: {template.fade_in_duration} minutes'
            
            days_display = self._format_days_display(template.days)
            message += f'\nActive days: {days_display}'
            
            QMessageBox.information(self, 'Alarm Created', message)
            logger.info(f'Alarm created from template: {template.name}')
            self._update_alarm_preview()
        except Exception as e:
            logger.error(f'Failed to create alarm from template: {e}', exc_info=True)
            QMessageBox.critical(
                self,
                'Failed to Create Alarm',
                f'Could not create alarm from template: {str(e)}'
            )

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

        # Show alarm setup dialog with fade-in and day selection options
        dlg = AlarmSetupDialog(self, playlist_name, time_str, volume, playlist_uri)
        if dlg.exec_() != QDialog.Accepted:
            return
        
        fade_in_enabled = dlg.fade_in_enabled
        fade_in_duration = dlg.fade_in_duration
        selected_days = dlg.selected_days

        try:
            self.alarm.set_alarm(
                time_str, playlist_name, playlist_uri, self.spotify_api, volume,
                fade_in_enabled, fade_in_duration, selected_days
            )

            message = f'Alarm scheduled for {time_str}\n\nPlaylist: {playlist_name}\nVolume: {volume}%'
            if fade_in_enabled:
                message += f'\nFade-in: {fade_in_duration} minutes'
            
            # Display active days
            days_display = self._format_days_display(selected_days)
            message += f'\nActive days: {days_display}'
            
            message += '\n\nMake sure a Spotify device is active when the alarm triggers.'
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
        
        self._update_next_alarm_display()

    def _format_days_display(self, days):
        """
        Format days list for display.

        Args:
            days: List of weekday names or None.

        Returns:
            str: Formatted string for display.
        """
        if days is None:
            return 'Every day'
        
        if len(days) == 7:
            return 'Every day'
        
        if set(days) == {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}:
            return 'Weekdays'
        
        if set(days) == {'Saturday', 'Sunday'}:
            return 'Weekends'
        
        # Abbreviate day names
        abbrev = {
            'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
            'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'
        }
        
        return ', '.join([abbrev.get(day, day) for day in days])

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

    def changeEvent(self, event):
        """Handle window state changes for minimize to tray."""
        if event.type() == event.WindowStateChange:
            if self.isMinimized() and hasattr(self, 'tray_icon'):
                event.ignore()
                self.hide()
                self.tray_icon.showMessage(
                    'Alarmify',
                    'Application minimized to tray',
                    QSystemTrayIcon.Information,
                    2000
                )
        super().changeEvent(event)

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
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                'Alarmify',
                'Application is still running in the system tray',
                QSystemTrayIcon.Information,
                2000
            )
        else:
            logger.info('Application closing - cleaning up resources')
            self._cleanup_resources()
            event.accept()

    def _cleanup_resources(self):
        """Clean up all background threads and resources."""
        if hasattr(self, 'device_status_timer'):
            self.device_status_timer.stop()
        
        if hasattr(self, 'alarm_countdown_timer'):
            self.alarm_countdown_timer.stop()

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


class SnoozeNotificationDialog(QDialog):
    """
    Dialog shown when an alarm triggers, offering snooze options.
    
    Displays alarm information and provides buttons for:
    - Snooze 5 minutes
    - Snooze 10 minutes
    - Snooze 15 minutes
    - Dismiss alarm
    """
    
    def __init__(self, parent=None, title='', message='', alarm_data=None):
        """
        Initialize the snooze notification dialog.
        
        Args:
            parent: Parent widget (AlarmApp).
            title: Notification title.
            message: Notification message.
            alarm_data: Alarm data dictionary for snooze functionality.
        """
        super().__init__(parent)
        self.parent_app = parent
        self.alarm_data = alarm_data or {}
        
        self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.setModal(False)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        self._build_ui(title, message)
    
    def _build_ui(self, title, message):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Icon
        icon_label = QLabel('⏰')
        icon_label.setFont(QFont('Arial', 48))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet('color: #1DB954;')
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont('Inter', 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('color: #ffffff;')
        layout.addWidget(title_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setFont(QFont('Inter', 12))
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet('color: #b3b3b3; padding: 10px;')
        layout.addWidget(message_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet('background-color: #3a3a3a;')
        layout.addWidget(separator)
        
        # Snooze label
        snooze_label = QLabel('Snooze for:')
        snooze_label.setFont(QFont('Inter', 14, QFont.Bold))
        snooze_label.setStyleSheet('color: #ffffff;')
        layout.addWidget(snooze_label)
        
        # Snooze buttons
        snooze_button_layout = QHBoxLayout()
        snooze_button_layout.setSpacing(12)
        
        btn_5min = QPushButton('5 min')
        btn_5min.setMinimumHeight(50)
        btn_5min.setFont(QFont('Inter', 14, QFont.Bold))
        btn_5min.clicked.connect(lambda: self._snooze(5))
        btn_5min.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
        """)
        snooze_button_layout.addWidget(btn_5min)
        
        btn_10min = QPushButton('10 min')
        btn_10min.setMinimumHeight(50)
        btn_10min.setFont(QFont('Inter', 14, QFont.Bold))
        btn_10min.clicked.connect(lambda: self._snooze(10))
        btn_10min.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
        """)
        snooze_button_layout.addWidget(btn_10min)
        
        btn_15min = QPushButton('15 min')
        btn_15min.setMinimumHeight(50)
        btn_15min.setFont(QFont('Inter', 14, QFont.Bold))
        btn_15min.clicked.connect(lambda: self._snooze(15))
        btn_15min.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
        """)
        snooze_button_layout.addWidget(btn_15min)
        
        layout.addLayout(snooze_button_layout)
        
        # Dismiss button
        btn_dismiss = QPushButton('Dismiss')
        btn_dismiss.setMinimumHeight(50)
        btn_dismiss.setFont(QFont('Inter', 14))
        btn_dismiss.clicked.connect(self._dismiss)
        btn_dismiss.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 2px solid #5a5a5a;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 2px solid #6a6a6a;
            }
        """)
        layout.addWidget(btn_dismiss)
    
    def _snooze(self, minutes):
        """
        Snooze the alarm for the specified duration.
        
        Args:
            minutes: Number of minutes to snooze.
        """
        logger.info(f'User snoozed alarm for {minutes} minutes')
        
        if self.parent_app and hasattr(self.parent_app, 'alarm'):
            self.parent_app.alarm.snooze_alarm(self.alarm_data, minutes)
            
            # Hide snooze from tray since dialog handled it
            if hasattr(self.parent_app, '_hide_snooze_from_tray'):
                self.parent_app._hide_snooze_from_tray()
            
            snooze_msg = f'Alarm snoozed for {minutes} minutes'
            QMessageBox.information(self, 'Snoozed', snooze_msg)
            logger.info(f'Alarm successfully snoozed for {minutes} minutes')
        
        self.accept()
    
    def _dismiss(self):
        """Dismiss the alarm and record dismissal in history."""
        logger.info('User dismissed alarm from snooze dialog')
        
        if self.parent_app and hasattr(self.parent_app, 'alarm'):
            self.parent_app.alarm.history.record_dismiss(self.alarm_data)
            
            # Hide snooze from tray since dialog handled it
            if hasattr(self.parent_app, '_hide_snooze_from_tray'):
                self.parent_app._hide_snooze_from_tray()
        
        self.accept()


class AlarmSetupDialog(QDialog):
    """
    Dialog for configuring alarm settings including fade-in options and day selection.
    
    Allows user to configure:
    - Select specific days of the week for the alarm
    - Enable/disable gradual volume fade-in
    - Fade-in duration (5-30 minutes)
    - Preview fade-in with current playback
    """
    
    def __init__(self, parent=None, playlist_name='', time_str='', volume=80, playlist_uri=''):
        """
        Initialize the alarm setup dialog.
        
        Args:
            parent: Parent widget.
            playlist_name: Name of the playlist for the alarm.
            time_str: Time string for the alarm.
            volume: Target volume for the alarm.
            playlist_uri: Spotify URI of the playlist.
        """
        super().__init__(parent)
        self.setWindowTitle('Alarm Setup')
        self.setMinimumWidth(400)
        self.setModal(True)
        
        self.fade_in_enabled = False
        self.fade_in_duration = 10
        self.target_volume = volume
        self.preview_controller = None
        self.playlist_uri = playlist_uri
        
        self._build_ui(playlist_name, time_str, volume)
    
    def _build_ui(self, playlist_name, time_str, volume):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Header
        header = QLabel('Alarm Configuration')
        header.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(header)
        
        # Alarm info
        info_text = f'Playlist: {playlist_name}\nTime: {time_str}\nVolume: {volume}%'
        info_label = QLabel(info_text)
        info_label.setStyleSheet('color: #b3b3b3; padding: 10px; background: #1a1a1a; border-radius: 6px;')
        layout.addWidget(info_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Days section
        days_label = QLabel('Active Days')
        days_label.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(days_label)
        
        # Quick select buttons
        quick_select_layout = QHBoxLayout()
        
        btn_everyday = QPushButton('Every Day')
        btn_everyday.clicked.connect(self._select_every_day)
        quick_select_layout.addWidget(btn_everyday)
        
        btn_weekdays = QPushButton('Weekdays')
        btn_weekdays.clicked.connect(self._select_weekdays)
        quick_select_layout.addWidget(btn_weekdays)
        
        btn_weekends = QPushButton('Weekends')
        btn_weekends.clicked.connect(self._select_weekends)
        quick_select_layout.addWidget(btn_weekends)
        
        layout.addLayout(quick_select_layout)
        
        # Day checkboxes
        days_widget = QWidget()
        days_grid = QHBoxLayout(days_widget)
        days_grid.setContentsMargins(0, 8, 0, 8)
        days_grid.setSpacing(8)
        
        self.day_checkboxes = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_abbrev = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        for day, abbrev in zip(days, day_abbrev):
            checkbox = QCheckBox(abbrev)
            checkbox.setChecked(True)
            checkbox.setToolTip(day)
            self.day_checkboxes[day] = checkbox
            days_grid.addWidget(checkbox)
        
        layout.addWidget(days_widget)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator2)
        
        # Fade-in section
        fade_in_label = QLabel('Volume Fade-In')
        fade_in_label.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(fade_in_label)
        
        # Fade-in checkbox
        self.fade_in_checkbox = QCheckBox('Enable gradual volume fade-in')
        self.fade_in_checkbox.setChecked(False)
        self.fade_in_checkbox.toggled.connect(self._on_fade_in_toggled)
        layout.addWidget(self.fade_in_checkbox)
        
        # Fade-in description
        description = QLabel(
            'Gradually increase volume from 0% to target volume over a specified duration.\n'
            'Perfect for a gentle wake-up experience.'
        )
        description.setWordWrap(True)
        description.setStyleSheet('color: #888; font-size: 12px; margin-left: 24px;')
        layout.addWidget(description)
        
        # Fade-in duration controls
        duration_widget = QWidget()
        duration_layout = QHBoxLayout(duration_widget)
        duration_layout.setContentsMargins(24, 8, 0, 0)
        
        duration_label = QLabel('Fade-in duration:')
        duration_layout.addWidget(duration_label)
        
        self.duration_slider = QSlider(Qt.Horizontal)
        self.duration_slider.setMinimum(5)
        self.duration_slider.setMaximum(30)
        self.duration_slider.setValue(10)
        self.duration_slider.setTickPosition(QSlider.TicksBelow)
        self.duration_slider.setTickInterval(5)
        self.duration_slider.setEnabled(False)
        self.duration_slider.valueChanged.connect(self._on_duration_changed)
        duration_layout.addWidget(self.duration_slider, stretch=1)
        
        self.duration_value_label = QLabel('10 min')
        self.duration_value_label.setFixedWidth(60)
        self.duration_value_label.setStyleSheet('font-weight: 600;')
        duration_layout.addWidget(self.duration_value_label)
        
        layout.addWidget(duration_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        btn_save_template = QPushButton('Save as Template')
        btn_save_template.clicked.connect(self._save_as_template)
        btn_save_template.setStyleSheet('background-color: #3a3a3a; color: white; padding: 8px 16px;')
        button_layout.addWidget(btn_save_template)
        
        button_layout.addStretch()
        
        btn_cancel = QPushButton('Cancel')
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        btn_ok = QPushButton('Set Alarm')
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self._on_accept)
        btn_ok.setStyleSheet('background-color: #1DB954; color: white; padding: 8px 24px; font-weight: bold;')
        button_layout.addWidget(btn_ok)
        
        layout.addLayout(button_layout)
        
        self.playlist_name = playlist_name
        self.time_str = time_str
        self.volume = volume
    
    def _select_every_day(self):
        """Select all days."""
        for checkbox in self.day_checkboxes.values():
            checkbox.setChecked(True)
    
    def _select_weekdays(self):
        """Select weekdays (Mon-Fri)."""
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for day, checkbox in self.day_checkboxes.items():
            checkbox.setChecked(day in weekdays)
    
    def _select_weekends(self):
        """Select weekends (Sat-Sun)."""
        weekends = ['Saturday', 'Sunday']
        for day, checkbox in self.day_checkboxes.items():
            checkbox.setChecked(day in weekends)
    
    def _on_fade_in_toggled(self, checked):
        """Handle fade-in checkbox toggle."""
        self.duration_slider.setEnabled(checked)
        self.fade_in_enabled = checked
    
    def _on_duration_changed(self, value):
        """Handle duration slider change."""
        self.duration_value_label.setText(f'{value} min')
        self.fade_in_duration = value
    
    def _save_as_template(self):
        """Save current alarm configuration as a template."""
        name, ok = QtWidgets.QInputDialog.getText(
            self,
            'Save Template',
            'Enter template name:'
        )
        
        if not ok or not name.strip():
            return
        
        name = name.strip()
        
        selected_days = [day for day, checkbox in self.day_checkboxes.items() if checkbox.isChecked()]
        if len(selected_days) == 7:
            selected_days = None
        
        template = AlarmTemplate(
            name=name,
            time=self.time_str,
            playlist_name=self.playlist_name,
            playlist_uri=self.playlist_uri,
            volume=self.volume,
            fade_in_enabled=self.fade_in_enabled,
            fade_in_duration=self.fade_in_duration,
            days=selected_days
        )
        
        if hasattr(self.parent(), 'template_manager'):
            template_manager = self.parent().template_manager
            if template_manager.add_template(template):
                QMessageBox.information(
                    self,
                    'Template Saved',
                    f'Template "{name}" has been saved successfully.'
                )
                logger.info(f'Template "{name}" saved from alarm setup dialog')
            else:
                QMessageBox.warning(
                    self,
                    'Failed to Save',
                    f'A template with the name "{name}" already exists.\n\n'
                    'Please choose a different name.'
                )
        else:
            QMessageBox.warning(
                self,
                'Error',
                'Template manager not available.'
            )
    
    def _on_accept(self):
        """Handle OK button click - validate and collect selected days."""
        selected = [day for day, checkbox in self.day_checkboxes.items() if checkbox.isChecked()]
        
        if not selected:
            QMessageBox.warning(
                self,
                'No Days Selected',
                'Please select at least one day for the alarm.'
            )
            return
        
        # Store selected days (None if all 7 days are selected)
        self.selected_days = None if len(selected) == 7 else selected
        
        self.accept()


class TemplateManagerDialog(QDialog):
    """
    Dialog for managing alarm templates.
    
    Allows user to:
    - View all saved templates
    - Create new templates
    - Edit existing templates
    - Delete templates
    """
    
    def __init__(self, template_manager, parent=None):
        """
        Initialize the template manager dialog.
        
        Args:
            template_manager: TemplateManager instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.template_manager = template_manager
        self.setWindowTitle('Manage Alarm Templates')
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        self._build_ui()
        self._load_templates()
    
    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        header = QLabel('Alarm Templates')
        header.setFont(QFont('Inter', 16, QFont.Bold))
        layout.addWidget(header)
        
        description = QLabel(
            'Templates let you save alarm configurations for quick reuse. '
            'Create a template with your favorite settings and apply it instantly.'
        )
        description.setWordWrap(True)
        description.setStyleSheet('color: #b3b3b3; padding: 8px;')
        layout.addWidget(description)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'Name', 'Time', 'Playlist', 'Volume', 'Fade-in', 'Days', 'Actions'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)
        
        button_layout = QHBoxLayout()
        
        btn_create = QPushButton('Create Template')
        btn_create.clicked.connect(self._create_template)
        btn_create.setStyleSheet('background-color: #1DB954; color: white; padding: 8px 16px; font-weight: bold;')
        button_layout.addWidget(btn_create)
        
        button_layout.addStretch()
        
        btn_refresh = QPushButton('Refresh')
        btn_refresh.clicked.connect(self._load_templates)
        button_layout.addWidget(btn_refresh)
        
        btn_close = QPushButton('Close')
        btn_close.clicked.connect(self.accept)
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
    
    def _load_templates(self):
        """Load and display all templates."""
        templates = self.template_manager.load_templates()
        self.table.setRowCount(len(templates))
        
        for row, template in enumerate(templates):
            self.table.setItem(row, 0, QTableWidgetItem(template.name))
            self.table.setItem(row, 1, QTableWidgetItem(template.time))
            self.table.setItem(row, 2, QTableWidgetItem(template.playlist_name))
            self.table.setItem(row, 3, QTableWidgetItem(f'{template.volume}%'))
            
            fade_text = 'Yes' if template.fade_in_enabled else 'No'
            if template.fade_in_enabled:
                fade_text += f' ({template.fade_in_duration}min)'
            self.table.setItem(row, 4, QTableWidgetItem(fade_text))
            
            days_display = self._format_days_display(template.days)
            days_item = QTableWidgetItem(days_display)
            
            # Color code based on day pattern
            days = template.days
            if days is None or (days and len(days) == 7):
                days_item.setForeground(QColor('#1DB954'))  # Green for every day
            elif days and set(days) == {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}:
                days_item.setForeground(QColor('#1E90FF'))  # Blue for weekdays
            elif days and set(days) == {'Saturday', 'Sunday'}:
                days_item.setForeground(QColor('#FFA500'))  # Orange for weekends
            else:
                days_item.setForeground(QColor('#B3B3B3'))  # Gray for custom
            
            self.table.setItem(row, 5, days_item)
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            btn_edit = QPushButton('Edit')
            btn_edit.clicked.connect(lambda checked, t=template: self._edit_template(t))
            btn_edit.setStyleSheet('padding: 4px 12px;')
            actions_layout.addWidget(btn_edit)
            
            btn_delete = QPushButton('Delete')
            btn_delete.clicked.connect(lambda checked, t=template: self._delete_template(t))
            btn_delete.setStyleSheet('padding: 4px 12px; background-color: #c44; color: white;')
            actions_layout.addWidget(btn_delete)
            
            self.table.setCellWidget(row, 6, actions_widget)
    
    def _format_days_display(self, days):
        """Format days list for display."""
        if days is None:
            return 'Every day'
        
        if len(days) == 7:
            return 'Every day'
        
        if set(days) == {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}:
            return 'Weekdays'
        
        if set(days) == {'Saturday', 'Sunday'}:
            return 'Weekends'
        
        abbrev = {
            'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
            'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'
        }
        
        return ', '.join([abbrev.get(day, day) for day in days])
    
    def _create_template(self):
        """Create a new template."""
        dlg = TemplateEditDialog(None, self.parent(), self)
        if dlg.exec_() == QDialog.Accepted:
            template = dlg.get_template()
            if template and self.template_manager.add_template(template):
                QMessageBox.information(self, 'Success', f'Template "{template.name}" created.')
                self._load_templates()
            else:
                QMessageBox.warning(
                    self,
                    'Failed',
                    'Failed to create template. A template with this name may already exist.'
                )
    
    def _edit_template(self, template):
        """Edit an existing template."""
        dlg = TemplateEditDialog(template, self.parent(), self)
        if dlg.exec_() == QDialog.Accepted:
            new_template = dlg.get_template()
            if new_template and self.template_manager.update_template(template.name, new_template):
                QMessageBox.information(self, 'Success', f'Template "{new_template.name}" updated.')
                self._load_templates()
            else:
                QMessageBox.warning(self, 'Failed', 'Failed to update template.')
    
    def _delete_template(self, template):
        """Delete a template."""
        reply = QMessageBox.question(
            self,
            'Confirm Delete',
            f'Are you sure you want to delete the template "{template.name}"?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.template_manager.delete_template(template.name):
                QMessageBox.information(self, 'Deleted', f'Template "{template.name}" deleted.')
                self._load_templates()
            else:
                QMessageBox.warning(self, 'Failed', 'Failed to delete template.')


class TemplateEditDialog(QDialog):
    """
    Dialog for creating or editing a template.
    """
    
    def __init__(self, template=None, main_window=None, parent=None):
        """
        Initialize the template edit dialog.
        
        Args:
            template: AlarmTemplate to edit, or None to create new.
            main_window: Reference to AlarmApp for playlist selection.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.template = template
        self.main_window = main_window
        self.selected_playlist_uri = template.playlist_uri if template else None
        self.selected_playlist_name = template.playlist_name if template else None
        
        self.setWindowTitle('Edit Template' if template else 'Create Template')
        self.setMinimumWidth(500)
        self.setModal(True)
        
        self._build_ui()
        
        if template:
            self._populate_fields()
    
    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Enter template name')
        form_layout.addRow('Template Name:', self.name_input)
        
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat('HH:mm')
        self.time_input.setMinimumHeight(40)
        form_layout.addRow('Time:', self.time_input)
        
        playlist_row = QHBoxLayout()
        self.playlist_label = QLabel('No playlist selected')
        self.playlist_label.setStyleSheet('padding: 8px; background: #2a2a2a; border-radius: 4px;')
        playlist_row.addWidget(self.playlist_label, stretch=1)
        
        btn_select_playlist = QPushButton('Select Playlist')
        btn_select_playlist.clicked.connect(self._select_playlist)
        playlist_row.addWidget(btn_select_playlist)
        
        form_layout.addRow('Playlist:', playlist_row)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        
        volume_row = QHBoxLayout()
        volume_row.addWidget(self.volume_slider)
        self.volume_label = QLabel('80%')
        self.volume_label.setFixedWidth(50)
        volume_row.addWidget(self.volume_label)
        
        form_layout.addRow('Volume:', volume_row)
        
        layout.addLayout(form_layout)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        layout.addWidget(separator)
        
        days_label = QLabel('Active Days')
        days_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(days_label)
        
        # Quick select buttons
        quick_select_layout = QHBoxLayout()
        
        btn_everyday = QPushButton('Every Day')
        btn_everyday.clicked.connect(self._select_every_day)
        btn_everyday.setStyleSheet('padding: 4px 12px;')
        quick_select_layout.addWidget(btn_everyday)
        
        btn_weekdays = QPushButton('Weekdays')
        btn_weekdays.clicked.connect(self._select_weekdays)
        btn_weekdays.setStyleSheet('padding: 4px 12px;')
        quick_select_layout.addWidget(btn_weekdays)
        
        btn_weekends = QPushButton('Weekends')
        btn_weekends.clicked.connect(self._select_weekends)
        btn_weekends.setStyleSheet('padding: 4px 12px;')
        quick_select_layout.addWidget(btn_weekends)
        
        quick_select_layout.addStretch()
        
        layout.addLayout(quick_select_layout)
        
        days_widget = QWidget()
        days_layout = QHBoxLayout(days_widget)
        days_layout.setSpacing(8)
        
        self.day_checkboxes = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_abbrev = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        for day, abbrev in zip(days, day_abbrev):
            checkbox = QCheckBox(abbrev)
            checkbox.setChecked(True)
            checkbox.setToolTip(day)
            self.day_checkboxes[day] = checkbox
            days_layout.addWidget(checkbox)
        
        layout.addWidget(days_widget)
        
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        layout.addWidget(separator2)
        
        fade_label = QLabel('Fade-In Settings')
        fade_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(fade_label)
        
        self.fade_checkbox = QCheckBox('Enable gradual volume fade-in')
        self.fade_checkbox.toggled.connect(self._on_fade_toggled)
        layout.addWidget(self.fade_checkbox)
        
        duration_row = QHBoxLayout()
        duration_row.addWidget(QLabel('Duration:'))
        
        self.fade_duration_slider = QSlider(Qt.Horizontal)
        self.fade_duration_slider.setMinimum(5)
        self.fade_duration_slider.setMaximum(30)
        self.fade_duration_slider.setValue(10)
        self.fade_duration_slider.setEnabled(False)
        self.fade_duration_slider.valueChanged.connect(self._on_fade_duration_changed)
        duration_row.addWidget(self.fade_duration_slider)
        
        self.fade_duration_label = QLabel('10 min')
        self.fade_duration_label.setFixedWidth(60)
        duration_row.addWidget(self.fade_duration_label)
        
        layout.addLayout(duration_row)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_cancel = QPushButton('Cancel')
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton('Save Template')
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._save_template)
        btn_save.setStyleSheet('background-color: #1DB954; color: white; padding: 8px 24px; font-weight: bold;')
        button_layout.addWidget(btn_save)
        
        layout.addLayout(button_layout)
    
    def _populate_fields(self):
        """Populate fields when editing existing template."""
        if not self.template:
            return
        
        self.name_input.setText(self.template.name)
        
        time_parts = self.template.time.split(':')
        if len(time_parts) == 2:
            from PyQt5.QtCore import QTime
            self.time_input.setTime(QTime(int(time_parts[0]), int(time_parts[1])))
        
        self.playlist_label.setText(self.template.playlist_name)
        self.volume_slider.setValue(self.template.volume)
        
        if self.template.days:
            for day in self.day_checkboxes:
                self.day_checkboxes[day].setChecked(day in self.template.days)
        
        self.fade_checkbox.setChecked(self.template.fade_in_enabled)
        self.fade_duration_slider.setValue(self.template.fade_in_duration)
    
    def _select_playlist(self):
        """Open playlist selection dialog."""
        if not self.main_window or not hasattr(self.main_window, 'playlist_list'):
            QMessageBox.warning(self, 'Error', 'Cannot access playlists.')
            return
        
        playlist_list = self.main_window.playlist_list
        if playlist_list.count() == 0:
            QMessageBox.information(
                self,
                'No Playlists',
                'No playlists available. Please log in to Spotify first.'
            )
            return
        
        dlg = QDialog(self)
        dlg.setWindowTitle('Select Playlist')
        dlg.setMinimumSize(400, 500)
        
        layout = QVBoxLayout(dlg)
        
        list_widget = QListWidget()
        
        for i in range(playlist_list.count()):
            item = playlist_list.item(i)
            playlist_data = item.data(Qt.UserRole)
            if playlist_data:
                list_item = QListWidgetItem(playlist_data.get('name', 'Unknown'))
                list_item.setData(Qt.UserRole, playlist_data)
                list_widget.addItem(list_item)
        
        layout.addWidget(list_widget)
        
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton('Cancel')
        btn_cancel.clicked.connect(dlg.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_select = QPushButton('Select')
        btn_select.clicked.connect(dlg.accept)
        btn_layout.addWidget(btn_select)
        
        layout.addLayout(btn_layout)
        
        if dlg.exec_() == QDialog.Accepted:
            current = list_widget.currentItem()
            if current:
                playlist_data = current.data(Qt.UserRole)
                self.selected_playlist_uri = playlist_data.get('uri')
                self.selected_playlist_name = playlist_data.get('name')
                self.playlist_label.setText(self.selected_playlist_name)
    
    def _on_volume_changed(self, value):
        """Update volume label."""
        self.volume_label.setText(f'{value}%')
    
    def _on_fade_toggled(self, checked):
        """Handle fade-in checkbox toggle."""
        self.fade_duration_slider.setEnabled(checked)
    
    def _on_fade_duration_changed(self, value):
        """Update fade duration label."""
        self.fade_duration_label.setText(f'{value} min')
    
    def _select_every_day(self):
        """Select all days."""
        for checkbox in self.day_checkboxes.values():
            checkbox.setChecked(True)
    
    def _select_weekdays(self):
        """Select weekdays (Mon-Fri)."""
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for day, checkbox in self.day_checkboxes.items():
            checkbox.setChecked(day in weekdays)
    
    def _select_weekends(self):
        """Select weekends (Sat-Sun)."""
        weekends = ['Saturday', 'Sunday']
        for day, checkbox in self.day_checkboxes.items():
            checkbox.setChecked(day in weekends)
    
    def _save_template(self):
        """Validate and save the template."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, 'Validation Error', 'Please enter a template name.')
            return
        
        if not self.selected_playlist_uri or not self.selected_playlist_name:
            QMessageBox.warning(self, 'Validation Error', 'Please select a playlist.')
            return
        
        selected_days = [day for day, checkbox in self.day_checkboxes.items() if checkbox.isChecked()]
        if not selected_days:
            QMessageBox.warning(self, 'Validation Error', 'Please select at least one day.')
            return
        
        if len(selected_days) == 7:
            selected_days = None
        
        self.created_template = AlarmTemplate(
            name=name,
            time=self.time_input.time().toString('HH:mm'),
            playlist_name=self.selected_playlist_name,
            playlist_uri=self.selected_playlist_uri,
            volume=self.volume_slider.value(),
            fade_in_enabled=self.fade_checkbox.isChecked(),
            fade_in_duration=self.fade_duration_slider.value(),
            days=selected_days
        )
        
        self.accept()
    
    def get_template(self):
        """Get the created/edited template."""
        return getattr(self, 'created_template', None)


class QuickSetupDialog(QDialog):
    """
    Dialog for quick alarm setup from templates.
    
    Shows list of available templates and allows user to select one
    to quickly create an alarm.
    """
    
    def __init__(self, templates, parent=None):
        """
        Initialize the quick setup dialog.
        
        Args:
            templates: List of AlarmTemplate objects.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.templates = templates
        self.selected_template = None
        
        self.setWindowTitle('Quick Setup from Template')
        self.setMinimumSize(600, 400)
        self.setModal(True)
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        header = QLabel('Select a Template')
        header.setFont(QFont('Inter', 16, QFont.Bold))
        layout.addWidget(header)
        
        description = QLabel('Choose a template to quickly create an alarm with saved settings.')
        description.setStyleSheet('color: #b3b3b3;')
        layout.addWidget(description)
        
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_template_selected)
        
        for template in self.templates:
            days_display = self._format_days_display(template.days)
            fade_text = f", Fade: {template.fade_in_duration}min" if template.fade_in_enabled else ""
            
            item_text = (
                f"{template.name}\n"
                f"  Time: {template.time} | Playlist: {template.playlist_name}\n"
                f"  Volume: {template.volume}% | Days: {days_display}{fade_text}"
            )
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, template)
            self.list_widget.addItem(item)
        
        layout.addWidget(self.list_widget)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_cancel = QPushButton('Cancel')
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        btn_select = QPushButton('Create Alarm from Template')
        btn_select.setDefault(True)
        btn_select.clicked.connect(self._on_template_selected)
        btn_select.setStyleSheet('background-color: #1DB954; color: white; padding: 8px 24px; font-weight: bold;')
        button_layout.addWidget(btn_select)
        
        layout.addLayout(button_layout)
    
    def _format_days_display(self, days):
        """Format days list for display."""
        if days is None:
            return 'Every day'
        
        if len(days) == 7:
            return 'Every day'
        
        if set(days) == {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}:
            return 'Weekdays'
        
        if set(days) == {'Saturday', 'Sunday'}:
            return 'Weekends'
        
        abbrev = {
            'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
            'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'
        }
        
        return ', '.join([abbrev.get(day, day) for day in days])
    
    def _on_template_selected(self):
        """Handle template selection."""
        current = self.list_widget.currentItem()
        if current:
            self.selected_template = current.data(Qt.UserRole)
            self.accept()


class AlarmManagerDialog(QDialog):
    """
    Dialog to view and manage scheduled alarms and snoozed alarms.

    Shows tables of all active alarms and snoozed alarms with time, playlist, and volume.
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
        self.setMinimumSize(600, 500)
        self.setModal(True)

        self._build_ui()
        self._load_alarms()

    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)

        # Regular alarms section
        header = QLabel('Scheduled Alarms')
        header.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Time', 'Playlist', 'Volume', 'Days', 'Actions'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Snoozed alarms section
        snooze_header = QLabel('Snoozed Alarms')
        snooze_header.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(snooze_header)

        self.snooze_table = QTableWidget()
        self.snooze_table.setColumnCount(3)
        self.snooze_table.setHorizontalHeaderLabels(['Will Trigger At', 'Playlist', 'Snooze Duration'])
        self.snooze_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.snooze_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.snooze_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.snooze_table)

        # Buttons
        button_layout = QHBoxLayout()
        
        btn_refresh = QPushButton('Refresh')
        btn_refresh.clicked.connect(self._load_alarms)
        button_layout.addWidget(btn_refresh)
        
        button_layout.addStretch()
        
        btn_close = QPushButton('Close')
        btn_close.clicked.connect(self.accept)
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)

    def _load_alarms(self):
        """Load and display all scheduled alarms and snoozed alarms."""
        # Load regular alarms
        alarms = self.alarm_manager.get_alarms()
        self.table.setRowCount(len(alarms))

        for row, alarm_info in enumerate(alarms):
            # Time
            time_item = QTableWidgetItem(alarm_info.get('time', ''))
            time_item.setFont(QFont('JetBrains Mono', 11, QFont.Bold))
            self.table.setItem(row, 0, time_item)
            
            # Playlist
            self.table.setItem(row, 1, QTableWidgetItem(alarm_info.get('playlist', '')))
            
            # Volume with fade-in info
            volume_text = f"{alarm_info.get('volume', 80)}%"
            if alarm_info.get('fade_in_enabled', False):
                volume_text += f" (fade {alarm_info.get('fade_in_duration', 10)}min)"
            self.table.setItem(row, 2, QTableWidgetItem(volume_text))

            # Display active days with formatting
            days = alarm_info.get('days')
            days_display = self._format_days_display_static(days)
            days_item = QTableWidgetItem(days_display)
            
            # Color code based on day pattern
            if days is None or (days and len(days) == 7):
                days_item.setForeground(QColor('#1DB954'))  # Green for every day
            elif days and set(days) == {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}:
                days_item.setForeground(QColor('#1E90FF'))  # Blue for weekdays
            elif days and set(days) == {'Saturday', 'Sunday'}:
                days_item.setForeground(QColor('#FFA500'))  # Orange for weekends
            else:
                days_item.setForeground(QColor('#B3B3B3'))  # Gray for custom
            
            self.table.setItem(row, 3, days_item)

            # Delete button
            btn_delete = QPushButton('Delete')
            btn_delete.setStyleSheet('padding: 4px 12px; background-color: #c44; color: white; border-radius: 4px;')
            btn_delete.clicked.connect(lambda checked, r=row: self._delete_alarm(r))
            self.table.setCellWidget(row, 4, btn_delete)

        # Load snoozed alarms
        snoozed_alarms = self.alarm_manager.get_snoozed_alarms()
        self.snooze_table.setRowCount(len(snoozed_alarms))

        for row, snooze_info in enumerate(snoozed_alarms):
            snooze_time = snooze_info.get('snooze_time')
            time_str = snooze_time.strftime('%H:%M:%S') if snooze_time else 'Unknown'
            
            self.snooze_table.setItem(row, 0, QTableWidgetItem(time_str))
            self.snooze_table.setItem(row, 1, QTableWidgetItem(snooze_info.get('original_playlist', 'Unknown')))
            self.snooze_table.setItem(row, 2, QTableWidgetItem(f"{snooze_info.get('snooze_duration', 0)} min"))

    def _format_days_display_static(self, days):
        """
        Format days list for display (static helper).

        Args:
            days: List of weekday names or None.

        Returns:
            str: Formatted string for display.
        """
        if days is None:
            return 'Every day'
        
        if len(days) == 7:
            return 'Every day'
        
        if set(days) == {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}:
            return 'Weekdays'
        
        if set(days) == {'Saturday', 'Sunday'}:
            return 'Weekends'
        
        # Abbreviate day names
        abbrev = {
            'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
            'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'
        }
        
        return ', '.join([abbrev.get(day, day) for day in days])

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

    def __init__(self, parent=None, current_theme='dark'):
        """Initialize the settings dialog with current credentials."""
        super().__init__(parent)
        self.setWindowTitle('Spotify Settings')
        self.setMinimumWidth(450)
        self.setModal(True)
        self.theme_changed = False
        self.initial_theme = current_theme

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Theme selection
        theme_label = QLabel('Theme')
        theme_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(theme_label)

        theme_row = QHBoxLayout()
        self.theme_group = QButtonGroup(self)
        
        self.dark_radio = QRadioButton('Dark')
        self.light_radio = QRadioButton('Light')
        
        self.theme_group.addButton(self.dark_radio, 0)
        self.theme_group.addButton(self.light_radio, 1)
        
        if current_theme == 'dark':
            self.dark_radio.setChecked(True)
        else:
            self.light_radio.setChecked(True)
        
        theme_row.addWidget(self.dark_radio)
        theme_row.addWidget(self.light_radio)
        theme_row.addStretch()
        
        layout.addLayout(theme_row)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Instructions label at the top
        instructions = QLabel(
            "To use Alarmify, you need Spotify API credentials.\n"
            "Click 'Get Credentials' to create them (takes 2 minutes)."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #b3b3b3; margin-bottom: 10px;")
        layout.addWidget(instructions)

        # Button to open Spotify Developer Dashboard
        btn_get_creds = QPushButton('Get Credentials (Open Spotify Developer)', self)
        btn_get_creds.setStyleSheet(
            "background-color: #1DB954; color: white; padding: 10px; "
            "font-weight: bold; border-radius: 5px;"
        )
        btn_get_creds.clicked.connect(self._open_spotify_dashboard)
        layout.addWidget(btn_get_creds)

        # Separator
        separator2 = QLabel("— Then paste your credentials below —")
        separator2.setAlignment(Qt.AlignCenter)
        separator2.setStyleSheet("color: #666; margin: 10px 0;")
        layout.addWidget(separator2)

        # Form layout for inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Client ID input
        self.client_id = QLineEdit(self)
        self.client_id.setPlaceholderText('Paste your Client ID here')

        self.client_secret = QLineEdit(self)
        self.client_secret.setPlaceholderText('Paste your Client Secret here')
        self.client_secret.setEchoMode(QLineEdit.Password)  # Hide secret

        # Redirect URI input (pre-filled, user rarely needs to change)
        # Note: Spotify requires 127.0.0.1 instead of localhost for security
        self.redirect_uri = QLineEdit(self)
        self.redirect_uri.setText('http://127.0.0.1:8888/callback')
        self.redirect_uri.setStyleSheet("color: #888;")
        # Make it read-only by default (can be unlocked if needed)
        self.redirect_uri.setReadOnly(True)
        self.redirect_uri.setToolTip('This is the default redirect URI. Change only if you need a different port.')

        load_dotenv()
        if os.getenv('SPOTIPY_CLIENT_ID'):
            self.client_id.setText(os.getenv('SPOTIPY_CLIENT_ID', ''))
        if os.getenv('SPOTIPY_CLIENT_SECRET'):
            self.client_secret.setText(os.getenv('SPOTIPY_CLIENT_SECRET', ''))
        if os.getenv('SPOTIPY_REDIRECT_URI'):
            self.redirect_uri.setText(os.getenv('SPOTIPY_REDIRECT_URI'))
            self.redirect_uri.setReadOnly(False)  # Allow editing if from env

        form_layout.addRow('Client ID:', self.client_id)
        form_layout.addRow('Client Secret:', self.client_secret)
        
        # Redirect URI row with unlock button
        redirect_row = QHBoxLayout()
        redirect_row.addWidget(self.redirect_uri, stretch=1)
        
        self.unlock_uri_button = QPushButton('🔓')
        self.unlock_uri_button.setFixedSize(36, 40)
        self.unlock_uri_button.setToolTip('Unlock to edit redirect URI')
        self.unlock_uri_button.clicked.connect(self._toggle_redirect_uri_lock)
        redirect_row.addWidget(self.unlock_uri_button)
        
        form_layout.addRow('Redirect URI:', redirect_row)

        layout.addLayout(form_layout)
        # Help note about redirect URI
        uri_note = QLabel(
            "Note: Add this exact Redirect URI in your Spotify app settings.\n"
            "Spotify requires 127.0.0.1 (not localhost) for security."
        )
        uri_note.setStyleSheet("color: #888; font-size: 11px;")
        uri_note.setWordWrap(True)
        layout.addWidget(uri_note)

        # Buttons row
        btn_layout = QHBoxLayout()

        btn_cancel = QPushButton('Cancel', self)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton('Save & Connect', self)
        btn_save.clicked.connect(self.save)
        btn_save.setDefault(True)  # Enter key triggers save
        btn_save.setStyleSheet(
            "background-color: #1DB954; color: white; padding: 8px 16px;"
        )
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def _toggle_redirect_uri_lock(self):
        """Toggle redirect URI field between locked and unlocked."""
        if self.redirect_uri.isReadOnly():
            self.redirect_uri.setReadOnly(False)
            self.redirect_uri.setStyleSheet("color: #ffffff; background: #181818;")
            self.unlock_uri_button.setText('🔒')
            self.unlock_uri_button.setToolTip('Lock redirect URI')
        else:
            self.redirect_uri.setReadOnly(True)
            self.redirect_uri.setStyleSheet("color: #888; background: #1a1a1a;")
            self.unlock_uri_button.setText('🔓')
            self.unlock_uri_button.setToolTip('Unlock to edit redirect URI')

    def _open_spotify_dashboard(self):
        """Open Spotify Developer Dashboard in browser with instructions."""
        import webbrowser
        # Show quick instructions
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
        # Open the dashboard
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
                    'Client ID and Client Secret are required.'
                )
                return

            if not (ruri.startswith('http://') or ruri.startswith('https://')):
                QMessageBox.warning(
                    self,
                    'Validation Error',
                    'Redirect URI must start with http:// or https://'
                )
                return

            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(f"SPOTIPY_CLIENT_ID={cid}\n")
                f.write(f"SPOTIPY_CLIENT_SECRET={csec}\n")
                f.write(f"SPOTIPY_REDIRECT_URI={ruri}\n")

            load_dotenv(override=True)

            selected_theme = 'dark' if self.dark_radio.isChecked() else 'light'
            if selected_theme != self.initial_theme:
                self.theme_changed = True

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


class AlarmPreviewDialog(QDialog):
    """
    Dialog to preview all upcoming alarms for the next 7 days.
    
    Shows a list of all scheduled alarm triggers with:
    - Date and time
    - Day of week
    - Playlist name
    - Volume and fade-in settings
    """
    
    def __init__(self, alarm_manager, parent=None):
        """
        Initialize the alarm preview dialog.
        
        Args:
            alarm_manager: Alarm instance containing scheduled alarms.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.alarm_manager = alarm_manager
        self.setWindowTitle('Upcoming Alarms - Next 7 Days')
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        self._build_ui()
        self._load_upcoming_alarms()
    
    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        header = QLabel('Upcoming Alarms')
        header.setFont(QFont('Inter', 18, QFont.Bold))
        layout.addWidget(header)
        
        description = QLabel('All scheduled alarm triggers for the next 7 days:')
        description.setStyleSheet('color: #b3b3b3; padding: 8px;')
        layout.addWidget(description)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'Date & Time', 'Day', 'Playlist', 'Volume', 'Days Active'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        button_layout = QHBoxLayout()
        
        btn_refresh = QPushButton('Refresh')
        btn_refresh.clicked.connect(self._load_upcoming_alarms)
        button_layout.addWidget(btn_refresh)
        
        button_layout.addStretch()
        
        btn_close = QPushButton('Close')
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet('background-color: #1DB954; color: white; padding: 8px 24px; font-weight: bold;')
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
    
    def _load_upcoming_alarms(self):
        """Load and display all upcoming alarms."""
        upcoming = self.alarm_manager.get_upcoming_alarms(days=7)
        self.table.setRowCount(len(upcoming))
        
        if not upcoming:
            self.table.setRowCount(1)
            no_alarms_item = QTableWidgetItem('No upcoming alarms in the next 7 days')
            no_alarms_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, no_alarms_item)
            self.table.setSpan(0, 0, 1, 5)
            return
        
        for row, entry in enumerate(upcoming):
            trigger_datetime = entry['datetime']
            alarm_info = entry['alarm_info']
            
            # Format date and time
            date_str = trigger_datetime.strftime('%Y-%m-%d')
            time_str = trigger_datetime.strftime('%H:%M')
            datetime_str = f'{date_str} {time_str}'
            
            # Get day of week
            day_name = trigger_datetime.strftime('%A')
            
            # Format date/time item with relative time
            now = datetime.now()
            delta = trigger_datetime - now
            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            
            if hours < 24:
                relative = f'in {hours}h {minutes}m'
            else:
                days = hours // 24
                relative = f'in {days} day{"s" if days != 1 else ""}'
            
            datetime_display = f'{datetime_str}\n({relative})'
            
            self.table.setItem(row, 0, QTableWidgetItem(datetime_display))
            self.table.setItem(row, 1, QTableWidgetItem(day_name))
            self.table.setItem(row, 2, QTableWidgetItem(alarm_info.get('playlist', 'Unknown')))
            
            # Volume and fade-in
            volume_text = f"{alarm_info.get('volume', 80)}%"
            if alarm_info.get('fade_in_enabled', False):
                volume_text += f"\n(fade {alarm_info.get('fade_in_duration', 10)}min)"
            self.table.setItem(row, 3, QTableWidgetItem(volume_text))
            
            # Days active
            days_display = self._format_days_display(alarm_info.get('days'))
            self.table.setItem(row, 4, QTableWidgetItem(days_display))
            
            # Highlight next alarm (first row)
            if row == 0:
                for col in range(5):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor('#1DB954').lighter(150))
    
    def _format_days_display(self, days):
        """Format days list for display."""
        if days is None:
            return 'Every day'
        
        if len(days) == 7:
            return 'Every day'
        
        if set(days) == {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}:
            return 'Weekdays'
        
        if set(days) == {'Saturday', 'Sunday'}:
            return 'Weekends'
        
        abbrev = {
            'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
            'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'
        }
        
        return ', '.join([abbrev.get(day, day) for day in days])


class CrashReportDialog(QDialog):
    """
    Dialog to display crash/error details and save crash reports.
    
    Shows:
    - Error message and type
    - Full stack trace
    - Option to save crash report to file
    - Copy to clipboard functionality
    """
    
    def __init__(self, exc_type, exc_value, exc_traceback, parent=None):
        super().__init__(parent)
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_traceback = exc_traceback
        
        self.setWindowTitle('Application Error')
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        error_icon = QLabel('\u26A0')
        error_icon.setFont(QFont('Arial', 48))
        error_icon.setStyleSheet('color: #FF6B6B;')
        error_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(error_icon)
        
        title = QLabel('An unexpected error occurred')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        error_msg = QLabel(f'{self.exc_type.__name__}: {str(self.exc_value)}')
        error_msg.setWordWrap(True)
        error_msg.setStyleSheet('color: #FF6B6B; padding: 10px;')
        error_msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(error_msg)
        
        details_label = QLabel('Error Details:')
        details_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QFont('Courier New', 9))
        
        traceback_text = ''.join(traceback.format_exception(
            self.exc_type,
            self.exc_value,
            self.exc_traceback
        ))
        self.details_text.setPlainText(traceback_text)
        
        layout.addWidget(self.details_text)
        
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton('Save Crash Report')
        save_btn.clicked.connect(self._save_crash_report)
        btn_layout.addWidget(save_btn)
        
        copy_btn = QPushButton('Copy to Clipboard')
        copy_btn.clicked.connect(self._copy_to_clipboard)
        btn_layout.addWidget(copy_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _save_crash_report(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Save Crash Report',
            f'crash_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            'Text Files (*.txt);;All Files (*)'
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Alarmify Crash Report\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error: {self.exc_type.__name__}: {str(self.exc_value)}\n")
                f.write("=" * 80 + "\n\n")
                f.write("Traceback:\n")
                f.write(self.details_text.toPlainText())
            
            QMessageBox.information(self, 'Saved', f'Crash report saved to:\n{file_path}')
        except Exception as e:
            QMessageBox.critical(self, 'Save Failed', f'Failed to save crash report:\n{e}')
    
    def _copy_to_clipboard(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.details_text.toPlainText())
        QMessageBox.information(self, 'Copied', 'Error details copied to clipboard')


class AlarmHistoryStatsDialog(QDialog):
    """
    Dialog for viewing alarm history and statistics dashboard.
    
    Displays:
    - Recent alarm history with detailed information
    - Statistics: success rate, snooze patterns, wake-up trends
    - Visualization widgets for wake patterns and day distribution
    - Export functionality for sleep data
    """
    
    def __init__(self, alarm_manager, parent=None):
        """
        Initialize the alarm history and statistics dialog.
        
        Args:
            alarm_manager: Alarm instance with history manager.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.alarm_manager = alarm_manager
        self.history_manager = alarm_manager.history
        
        self.setWindowTitle('Alarm History & Statistics')
        self.setMinimumSize(1000, 700)
        self.setModal(True)
        
        self.current_days_filter = 30
        
        self._build_ui()
        self._load_data()
    
    def _build_ui(self):
        """Build the dialog UI with tabs for history and statistics."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        header = QLabel('Alarm History & Statistics Dashboard')
        header.setFont(QFont('Inter', 18, QFont.Bold))
        layout.addWidget(header)
        
        # Tab widget for different views
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setObjectName('historyTabs')
        
        # Statistics tab
        self.stats_tab = self._build_stats_tab()
        self.tabs.addTab(self.stats_tab, '📊 Statistics')
        
        # History tab
        self.history_tab = self._build_history_tab()
        self.tabs.addTab(self.history_tab, '📜 History')
        
        layout.addWidget(self.tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        # Time period filter
        filter_label = QLabel('Time Period:')
        button_layout.addWidget(filter_label)
        
        self.days_combo = QComboBox()
        self.days_combo.addItem('Last 7 days', 7)
        self.days_combo.addItem('Last 30 days', 30)
        self.days_combo.addItem('Last 90 days', 90)
        self.days_combo.addItem('All time', None)
        self.days_combo.setCurrentIndex(1)  # Default to 30 days
        self.days_combo.currentIndexChanged.connect(self._on_period_changed)
        button_layout.addWidget(self.days_combo)
        
        button_layout.addStretch()
        
        btn_export_csv = QPushButton('Export CSV')
        btn_export_csv.clicked.connect(self._export_csv)
        btn_export_csv.setStyleSheet('padding: 8px 16px;')
        button_layout.addWidget(btn_export_csv)
        
        btn_export_json = QPushButton('Export JSON')
        btn_export_json.clicked.connect(self._export_json)
        btn_export_json.setStyleSheet('padding: 8px 16px;')
        button_layout.addWidget(btn_export_json)
        
        btn_clear = QPushButton('Clear Old Data')
        btn_clear.clicked.connect(self._clear_old_data)
        btn_clear.setStyleSheet('padding: 8px 16px; background-color: #c44; color: white;')
        button_layout.addWidget(btn_clear)
        
        btn_refresh = QPushButton('Refresh')
        btn_refresh.clicked.connect(self._load_data)
        btn_refresh.setStyleSheet('padding: 8px 16px;')
        button_layout.addWidget(btn_refresh)
        
        btn_close = QPushButton('Close')
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet('padding: 8px 16px;')
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
    
    def _build_stats_tab(self):
        """Build the statistics tab with visualizations."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Scroll area for stats content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName('statsScrollArea')
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(24)
        
        # Summary statistics cards
        summary_container = QHBoxLayout()
        summary_container.setSpacing(16)
        
        self.total_alarms_card = self._create_stat_card('Total Alarms', '0', '#1DB954')
        summary_container.addWidget(self.total_alarms_card)
        
        self.success_rate_card = self._create_stat_card('Success Rate', '0%', '#1E90FF')
        summary_container.addWidget(self.success_rate_card)
        
        self.avg_snooze_card = self._create_stat_card('Avg Snoozes', '0', '#FFA500')
        summary_container.addWidget(self.avg_snooze_card)
        
        self.total_snoozes_card = self._create_stat_card('Total Snoozes', '0', '#FF6B6B')
        summary_container.addWidget(self.total_snoozes_card)
        
        content_layout.addLayout(summary_container)
        
        # Insights section
        insights_label = QLabel('Wake-Up Insights')
        insights_label.setFont(QFont('Inter', 16, QFont.Bold))
        content_layout.addWidget(insights_label)
        
        self.insights_container = QWidget()
        insights_layout = QVBoxLayout(self.insights_container)
        insights_layout.setSpacing(8)
        insights_layout.setContentsMargins(16, 16, 16, 16)
        self.insights_container.setStyleSheet(
            'QWidget { background-color: rgba(29, 185, 84, 0.1); '
            'border-radius: 8px; border: 1px solid rgba(29, 185, 84, 0.3); }'
        )
        
        self.most_successful_label = QLabel('Most Successful Time: N/A')
        self.most_successful_label.setFont(QFont('Inter', 12))
        insights_layout.addWidget(self.most_successful_label)
        
        self.most_snoozed_label = QLabel('Most Snoozed Time: N/A')
        self.most_snoozed_label.setFont(QFont('Inter', 12))
        insights_layout.addWidget(self.most_snoozed_label)
        
        self.fade_usage_label = QLabel('Fade-in Usage: 0%')
        self.fade_usage_label.setFont(QFont('Inter', 12))
        insights_layout.addWidget(self.fade_usage_label)
        
        content_layout.addWidget(self.insights_container)
        
        # Wake patterns visualization
        patterns_label = QLabel('Wake-Up Patterns by Hour')
        patterns_label.setFont(QFont('Inter', 16, QFont.Bold))
        content_layout.addWidget(patterns_label)
        
        self.patterns_widget = QWidget()
        self.patterns_widget.setMinimumHeight(200)
        self.patterns_widget.setStyleSheet(
            'QWidget { background-color: #2a2a2a; border-radius: 8px; padding: 16px; }'
        )
        patterns_layout = QVBoxLayout(self.patterns_widget)
        self.patterns_chart_label = QLabel('Loading...')
        self.patterns_chart_label.setAlignment(Qt.AlignCenter)
        patterns_layout.addWidget(self.patterns_chart_label)
        content_layout.addWidget(self.patterns_widget)
        
        # Day distribution visualization
        days_label = QLabel('Wake-Up Distribution by Day')
        days_label.setFont(QFont('Inter', 16, QFont.Bold))
        content_layout.addWidget(days_label)
        
        self.days_widget = QWidget()
        self.days_widget.setMinimumHeight(200)
        self.days_widget.setStyleSheet(
            'QWidget { background-color: #2a2a2a; border-radius: 8px; padding: 16px; }'
        )
        days_layout = QVBoxLayout(self.days_widget)
        self.days_chart_label = QLabel('Loading...')
        self.days_chart_label.setAlignment(Qt.AlignCenter)
        days_layout.addWidget(self.days_chart_label)
        content_layout.addWidget(self.days_widget)
        
        # Favorite playlists
        playlists_label = QLabel('Top 5 Alarm Playlists')
        playlists_label.setFont(QFont('Inter', 16, QFont.Bold))
        content_layout.addWidget(playlists_label)
        
        self.playlists_table = QTableWidget()
        self.playlists_table.setColumnCount(2)
        self.playlists_table.setHorizontalHeaderLabels(['Playlist Name', 'Usage Count'])
        self.playlists_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.playlists_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.playlists_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.playlists_table.setMaximumHeight(200)
        content_layout.addWidget(self.playlists_table)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def _build_history_tab(self):
        """Build the history tab with detailed alarm records."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Search/filter bar
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel('Filter:')
        filter_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem('All', None)
        self.filter_combo.addItem('Successful Only', 'success')
        self.filter_combo.addItem('Failed Only', 'failed')
        self.filter_combo.addItem('Snoozed', 'snoozed')
        self.filter_combo.currentIndexChanged.connect(self._apply_history_filter)
        filter_layout.addWidget(self.filter_combo)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            'Timestamp', 'Time', 'Playlist', 'Volume', 'Day', 'Status', 'Snoozes', 'Fade-in'
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history_table.setAlternatingRowColors(True)
        layout.addWidget(self.history_table)
        
        return tab
    
    def _create_stat_card(self, title, value, color):
        """Create a statistics card widget."""
        card = QWidget()
        card.setMinimumHeight(120)
        card.setStyleSheet(
            f'QWidget {{ background-color: rgba(42, 42, 42, 0.8); '
            f'border-left: 4px solid {color}; border-radius: 8px; padding: 16px; }}'
        )
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Inter', 11))
        title_label.setStyleSheet('color: #b3b3b3;')
        card_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont('Inter', 32, QFont.Bold))
        value_label.setStyleSheet(f'color: {color};')
        value_label.setObjectName(f'{title.replace(" ", "_")}_value')
        card_layout.addWidget(value_label)
        
        card_layout.addStretch()
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def _load_data(self):
        """Load and display statistics and history data."""
        days = self.current_days_filter
        
        # Get statistics
        stats = self.history_manager.get_statistics(days=days if days else 9999)
        
        # Update summary cards
        self.total_alarms_card.value_label.setText(str(stats['total_alarms']))
        self.success_rate_card.value_label.setText(f"{stats['success_rate']:.1f}%")
        self.avg_snooze_card.value_label.setText(f"{stats['avg_snooze_count']:.1f}")
        self.total_snoozes_card.value_label.setText(str(stats['total_snoozes']))
        
        # Update insights
        self.most_successful_label.setText(
            f'✅ Most Successful Time: {stats["most_successful_time"] or "N/A"} '
            f'(least snoozes per alarm)'
        )
        self.most_snoozed_label.setText(
            f'😴 Most Snoozed Time: {stats["most_snoozed_time"] or "N/A"} '
            f'(hardest to wake up)'
        )
        self.fade_usage_label.setText(
            f'🎵 Fade-in Usage: {stats["fade_in_usage"]:.1f}% of alarms use fade-in'
        )
        
        # Update wake patterns visualization
        self._update_patterns_chart(stats['wake_patterns'])
        
        # Update day distribution visualization
        self._update_days_chart(stats['day_distribution'])
        
        # Update favorite playlists
        self._update_playlists_table(stats['favorite_playlists'])
        
        # Load history table
        self._load_history_table()
    
    def _update_patterns_chart(self, wake_patterns):
        """Update wake patterns visualization with bar chart."""
        if not wake_patterns:
            self.patterns_chart_label.setText('No wake pattern data available')
            return
        
        # Create simple text-based bar chart
        chart_text = ''
        max_count = max(wake_patterns.values()) if wake_patterns else 1
        
        # Sort by hour
        sorted_hours = sorted(wake_patterns.items(), key=lambda x: int(x[0]))
        
        for hour, count in sorted_hours:
            bar_length = int((count / max_count) * 40)
            bar = '█' * bar_length
            chart_text += f'{hour}:00  {bar}  ({count})\n'
        
        self.patterns_chart_label.setText(chart_text)
        self.patterns_chart_label.setFont(QFont('JetBrains Mono', 10))
        self.patterns_chart_label.setAlignment(Qt.AlignLeft)
        self.patterns_chart_label.setStyleSheet('color: #1DB954; padding: 8px;')
    
    def _update_days_chart(self, day_distribution):
        """Update day distribution visualization with bar chart."""
        if not day_distribution:
            self.days_chart_label.setText('No day distribution data available')
            return
        
        # Create simple text-based bar chart
        chart_text = ''
        max_count = max(day_distribution.values()) if day_distribution else 1
        
        # Order by weekday
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in day_order:
            count = day_distribution.get(day, 0)
            if count > 0:
                bar_length = int((count / max_count) * 35)
                bar = '█' * bar_length
                chart_text += f'{day[:3]:3s}  {bar}  ({count})\n'
        
        self.days_chart_label.setText(chart_text)
        self.days_chart_label.setFont(QFont('JetBrains Mono', 10))
        self.days_chart_label.setAlignment(Qt.AlignLeft)
        self.days_chart_label.setStyleSheet('color: #1E90FF; padding: 8px;')
    
    def _update_playlists_table(self, favorite_playlists):
        """Update favorite playlists table."""
        self.playlists_table.setRowCount(len(favorite_playlists))
        
        for row, (playlist, count) in enumerate(favorite_playlists.items()):
            self.playlists_table.setItem(row, 0, QTableWidgetItem(playlist))
            
            count_item = QTableWidgetItem(str(count))
            count_item.setFont(QFont('Inter', 11, QFont.Bold))
            count_item.setForeground(QColor('#1DB954'))
            self.playlists_table.setItem(row, 1, count_item)
    
    def _load_history_table(self):
        """Load history entries into the table."""
        days = self.current_days_filter
        
        if days:
            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(days=days)
            history = self.history_manager.get_history(start_date=cutoff)
        else:
            history = self.history_manager.get_history()
        
        self.full_history = history
        self._apply_history_filter()
    
    def _apply_history_filter(self):
        """Apply filter to history table."""
        filter_type = self.filter_combo.currentData()
        
        if not hasattr(self, 'full_history'):
            return
        
        # Filter history
        if filter_type == 'success':
            filtered = [e for e in self.full_history if e.get('success', False)]
        elif filter_type == 'failed':
            filtered = [e for e in self.full_history if not e.get('success', False)]
        elif filter_type == 'snoozed':
            filtered = [e for e in self.full_history if e.get('snoozed', False)]
        else:
            filtered = self.full_history
        
        # Populate table
        self.history_table.setRowCount(len(filtered))
        
        for row, entry in enumerate(filtered):
            # Timestamp
            timestamp = entry.get('timestamp', '')
            if timestamp:
                dt = datetime.fromisoformat(timestamp)
                timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                timestamp_str = 'Unknown'
            self.history_table.setItem(row, 0, QTableWidgetItem(timestamp_str))
            
            # Time
            time_item = QTableWidgetItem(entry.get('trigger_time', 'N/A'))
            time_item.setFont(QFont('JetBrains Mono', 10, QFont.Bold))
            self.history_table.setItem(row, 1, time_item)
            
            # Playlist
            self.history_table.setItem(row, 2, QTableWidgetItem(entry.get('playlist_name', 'Unknown')))
            
            # Volume
            volume_item = QTableWidgetItem(f"{entry.get('volume', 80)}%")
            self.history_table.setItem(row, 3, volume_item)
            
            # Day
            self.history_table.setItem(row, 4, QTableWidgetItem(entry.get('day_of_week', 'Unknown')))
            
            # Status
            success = entry.get('success', False)
            status_item = QTableWidgetItem('✅ Success' if success else '❌ Failed')
            status_item.setForeground(QColor('#1DB954' if success else '#FF6B6B'))
            self.history_table.setItem(row, 5, status_item)
            
            # Snoozes
            snooze_count = entry.get('snooze_count', 0)
            snooze_item = QTableWidgetItem(str(snooze_count) if snooze_count > 0 else '-')
            if snooze_count > 0:
                snooze_item.setForeground(QColor('#FFA500'))
            self.history_table.setItem(row, 6, snooze_item)
            
            # Fade-in
            fade_enabled = entry.get('fade_in_enabled', False)
            fade_text = f"Yes ({entry.get('fade_in_duration', 10)}m)" if fade_enabled else 'No'
            self.history_table.setItem(row, 7, QTableWidgetItem(fade_text))
    
    def _on_period_changed(self, index):
        """Handle time period filter change."""
        self.current_days_filter = self.days_combo.itemData(index)
        self._load_data()
    
    def _export_csv(self):
        """Export alarm history to CSV file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Export Alarm History to CSV',
            f'alarm_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            'CSV Files (*.csv);;All Files (*)'
        )
        
        if not file_path:
            return
        
        try:
            from pathlib import Path
            success = self.history_manager.export_to_csv(Path(file_path))
            
            if success:
                QMessageBox.information(
                    self,
                    'Export Successful',
                    f'Alarm history exported to:\n{file_path}'
                )
                logger.info(f'Exported alarm history to CSV: {file_path}')
            else:
                QMessageBox.warning(
                    self,
                    'Export Failed',
                    'Failed to export alarm history. Check logs for details.'
                )
        except Exception as e:
            logger.error(f'Failed to export CSV: {e}', exc_info=True)
            QMessageBox.critical(
                self,
                'Export Error',
                f'An error occurred during export:\n{str(e)}'
            )
    
    def _export_json(self):
        """Export alarm history to JSON file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Export Alarm History to JSON',
            f'alarm_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            'JSON Files (*.json);;All Files (*)'
        )
        
        if not file_path:
            return
        
        try:
            from pathlib import Path
            success = self.history_manager.export_to_json(Path(file_path))
            
            if success:
                QMessageBox.information(
                    self,
                    'Export Successful',
                    f'Alarm history exported to:\n{file_path}'
                )
                logger.info(f'Exported alarm history to JSON: {file_path}')
            else:
                QMessageBox.warning(
                    self,
                    'Export Failed',
                    'Failed to export alarm history. Check logs for details.'
                )
        except Exception as e:
            logger.error(f'Failed to export JSON: {e}', exc_info=True)
            QMessageBox.critical(
                self,
                'Export Error',
                f'An error occurred during export:\n{str(e)}'
            )
    
    def _clear_old_data(self):
        """Clear old history entries."""
        dialog = QDialog(self)
        dialog.setWindowTitle('Clear Old Data')
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel('Clear alarm history older than:')
        layout.addWidget(label)
        
        days_input = QtWidgets.QSpinBox()
        days_input.setMinimum(1)
        days_input.setMaximum(365)
        days_input.setValue(90)
        days_input.setSuffix(' days')
        layout.addWidget(days_input)
        
        warning = QLabel('⚠️ This action cannot be undone!')
        warning.setStyleSheet('color: #FFA500; font-weight: bold;')
        layout.addWidget(warning)
        
        btn_layout = QHBoxLayout()
        
        btn_cancel = QPushButton('Cancel')
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_clear = QPushButton('Clear Old Data')
        btn_clear.setStyleSheet('background-color: #c44; color: white; padding: 8px 16px;')
        btn_clear.clicked.connect(dialog.accept)
        btn_layout.addWidget(btn_clear)
        
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            days = days_input.value()
            self.history_manager.clear_old_entries(days=days)
            QMessageBox.information(
                self,
                'Data Cleared',
                f'Alarm history older than {days} days has been cleared.'
            )
            self._load_data()
