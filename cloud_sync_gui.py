"""
cloud_sync_gui.py - GUI components for cloud synchronization

This module provides GUI dialogs and widgets for cloud sync functionality:
- CloudSyncDialog: Main dialog for managing cloud sync
- CloudLoginDialog: Login/registration dialog
- SyncStatusWidget: Widget showing sync status
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFormLayout, QMessageBox, QGroupBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QTabWidget, QWidget, QTextEdit, QComboBox, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont
from datetime import datetime
from typing import Optional
from logging_config import get_logger
from cloud_sync.cloud_sync_manager import CloudSyncManager

logger = get_logger(__name__)


class SyncWorkerThread(QThread):
    """Background thread for sync operations."""
    
    sync_complete = pyqtSignal(bool, str, dict)
    
    def __init__(self, sync_manager, direction='both'):
        super().__init__()
        self.sync_manager = sync_manager
        self.direction = direction
    
    def run(self):
        """Run sync operation in background."""
        try:
            success, message, details = self.sync_manager.sync_all(self.direction)
            self.sync_complete.emit(success, message, details)
        except Exception as e:
            logger.error(f"Sync thread error: {e}", exc_info=True)
            self.sync_complete.emit(False, str(e), {})


class CloudLoginDialog(QDialog):
    """Dialog for cloud login and registration."""
    
    def __init__(self, sync_manager: CloudSyncManager, parent=None):
        super().__init__(parent)
        self.sync_manager = sync_manager
        self.setWindowTitle('Cloud Sync Login')
        self.setMinimumWidth(450)
        self.setModal(True)
        
        self._build_ui()
    
    def _build_ui(self):
        """Build dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header = QLabel('Alarmify Cloud Sync')
        header.setFont(QFont('Inter', 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        description = QLabel(
            'Sign in to synchronize your alarms and settings across devices'
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet('color: #b3b3b3; margin-bottom: 10px;')
        layout.addWidget(description)
        
        # Form
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(12)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('your.email@example.com')
        self.email_input.setMinimumHeight(40)
        form_layout.addRow('Email:', self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Password (min 8 characters)')
        self.password_input.setMinimumHeight(40)
        form_layout.addRow('Password:', self.password_input)
        
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText('Optional display name')
        self.display_name_input.setMinimumHeight(40)
        self.display_name_input.hide()
        self.display_name_label = QLabel('Display Name:')
        self.display_name_label.hide()
        form_layout.addRow(self.display_name_label, self.display_name_input)
        
        layout.addWidget(form_widget)
        
        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        self.login_button = QPushButton('Sign In')
        self.login_button.setMinimumHeight(45)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
        """)
        self.login_button.clicked.connect(self._handle_login)
        button_layout.addWidget(self.login_button)
        
        self.register_button = QPushButton('Create Account')
        self.register_button.setMinimumHeight(40)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: 2px solid #1DB954;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
        """)
        self.register_button.clicked.connect(self._toggle_register_mode)
        button_layout.addWidget(self.register_button)
        
        layout.addLayout(button_layout)
        
        # Mode flag
        self.is_register_mode = False
    
    def _toggle_register_mode(self):
        """Toggle between login and registration mode."""
        self.is_register_mode = not self.is_register_mode
        
        if self.is_register_mode:
            self.setWindowTitle('Create Cloud Sync Account')
            self.login_button.setText('Create Account')
            self.register_button.setText('Back to Sign In')
            self.display_name_input.show()
            self.display_name_label.show()
        else:
            self.setWindowTitle('Cloud Sync Login')
            self.login_button.setText('Sign In')
            self.register_button.setText('Create Account')
            self.display_name_input.hide()
            self.display_name_label.hide()
    
    def _handle_login(self):
        """Handle login or registration."""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, 'Missing Information', 'Please enter email and password')
            return
        
        if self.is_register_mode:
            # Registration
            display_name = self.display_name_input.text().strip() or None
            success, message = self.sync_manager.register(email, password, display_name)
            
            if success:
                QMessageBox.information(
                    self,
                    'Registration Successful',
                    'Account created successfully! You can now sign in.'
                )
                self._toggle_register_mode()
                self.password_input.clear()
            else:
                QMessageBox.warning(self, 'Registration Failed', message)
        else:
            # Login
            success, message = self.sync_manager.login(email, password)
            
            if success:
                logger.info("Cloud login successful")
                self.accept()
            else:
                QMessageBox.warning(self, 'Login Failed', message)


class CloudSyncDialog(QDialog):
    """Main dialog for cloud synchronization management."""
    
    def __init__(self, sync_manager: CloudSyncManager, parent=None):
        super().__init__(parent)
        self.sync_manager = sync_manager
        self.setWindowTitle('Cloud Sync')
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        self._build_ui()
        self._update_status()
        
        # Auto-update status every 5 seconds
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(5000)
    
    def _build_ui(self):
        """Build dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Header
        header = QLabel('Cloud Synchronization')
        header.setFont(QFont('Inter', 18, QFont.Bold))
        layout.addWidget(header)
        
        # Tabs
        tabs = QTabWidget()
        
        # Status tab
        status_tab = self._create_status_tab()
        tabs.addTab(status_tab, 'Status')
        
        # Devices tab
        devices_tab = self._create_devices_tab()
        tabs.addTab(devices_tab, 'Devices')
        
        # Settings tab
        settings_tab = self._create_settings_tab()
        tabs.addTab(settings_tab, 'Settings')
        
        layout.addWidget(tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.logout_button = QPushButton('Sign Out')
        self.logout_button.clicked.connect(self._handle_logout)
        button_layout.addWidget(self.logout_button)
        
        button_layout.addStretch()
        
        btn_close = QPushButton('Close')
        btn_close.clicked.connect(self.accept)
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
    
    def _create_status_tab(self) -> QWidget:
        """Create status tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # User info
        user_group = QGroupBox('Account')
        user_layout = QVBoxLayout(user_group)
        
        self.user_label = QLabel('Not logged in')
        self.user_label.setStyleSheet('font-size: 14px;')
        user_layout.addWidget(self.user_label)
        
        layout.addWidget(user_group)
        
        # Sync status
        sync_group = QGroupBox('Synchronization Status')
        sync_layout = QVBoxLayout(sync_group)
        
        self.last_sync_label = QLabel('Last sync: Never')
        sync_layout.addWidget(self.last_sync_label)
        
        self.sync_status_label = QLabel('Status: Idle')
        sync_layout.addWidget(self.sync_status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        sync_layout.addWidget(self.progress_bar)
        
        sync_buttons = QHBoxLayout()
        
        btn_sync_now = QPushButton('Sync Now')
        btn_sync_now.clicked.connect(lambda: self._perform_sync('both'))
        btn_sync_now.setStyleSheet('background-color: #1DB954; color: white; padding: 8px 16px;')
        sync_buttons.addWidget(btn_sync_now)
        
        btn_upload = QPushButton('Upload Only')
        btn_upload.clicked.connect(lambda: self._perform_sync('upload'))
        sync_buttons.addWidget(btn_upload)
        
        btn_download = QPushButton('Download Only')
        btn_download.clicked.connect(lambda: self._perform_sync('download'))
        sync_buttons.addWidget(btn_download)
        
        sync_layout.addLayout(sync_buttons)
        
        layout.addWidget(sync_group)
        
        # Auto-sync
        auto_sync_group = QGroupBox('Automatic Sync')
        auto_sync_layout = QVBoxLayout(auto_sync_group)
        
        self.auto_sync_checkbox = QCheckBox('Enable automatic synchronization')
        self.auto_sync_checkbox.stateChanged.connect(self._toggle_auto_sync)
        auto_sync_layout.addWidget(self.auto_sync_checkbox)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel('Sync interval:'))
        
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(['15 minutes', '30 minutes', '1 hour', '2 hours'])
        self.interval_combo.setCurrentIndex(1)
        interval_layout.addWidget(self.interval_combo)
        interval_layout.addStretch()
        
        auto_sync_layout.addLayout(interval_layout)
        
        layout.addWidget(auto_sync_group)
        
        layout.addStretch()
        
        return widget
    
    def _create_devices_tab(self) -> QWidget:
        """Create devices tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        description = QLabel('Devices registered to your account:')
        layout.addWidget(description)
        
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(4)
        self.devices_table.setHorizontalHeaderLabels([
            'Device Name', 'Type', 'Last Sync', 'Status'
        ])
        self.devices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.devices_table)
        
        btn_refresh_devices = QPushButton('Refresh Devices')
        btn_refresh_devices.clicked.connect(self._load_devices)
        layout.addWidget(btn_refresh_devices)
        
        return widget
    
    def _create_settings_tab(self) -> QWidget:
        """Create settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Data management
        data_group = QGroupBox('Data Management')
        data_layout = QVBoxLayout(data_group)
        
        description = QLabel(
            'Warning: These actions cannot be undone.'
        )
        description.setStyleSheet('color: #ff6b6b; font-weight: bold;')
        data_layout.addWidget(description)
        
        btn_delete_cloud_data = QPushButton('Delete All Cloud Data')
        btn_delete_cloud_data.clicked.connect(self._delete_cloud_data)
        btn_delete_cloud_data.setStyleSheet('background-color: #d32f2f; color: white; padding: 8px 16px;')
        data_layout.addWidget(btn_delete_cloud_data)
        
        layout.addWidget(data_group)
        
        # Account management
        account_group = QGroupBox('Account Management')
        account_layout = QVBoxLayout(account_group)
        
        btn_change_password = QPushButton('Change Password')
        btn_change_password.clicked.connect(self._change_password)
        account_layout.addWidget(btn_change_password)
        
        layout.addWidget(account_group)
        
        layout.addStretch()
        
        return widget
    
    def _update_status(self):
        """Update status display."""
        user = self.sync_manager.get_current_user()
        
        if user:
            self.user_label.setText(
                f"Logged in as: {user['display_name']} ({user['email']})"
            )
        else:
            self.user_label.setText('Not logged in')
        
        status = self.sync_manager.get_sync_status()
        
        if status['last_sync_time']:
            try:
                last_sync = datetime.fromisoformat(status['last_sync_time'])
                self.last_sync_label.setText(f"Last sync: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception:
                self.last_sync_label.setText('Last sync: Unknown')
        else:
            self.last_sync_label.setText('Last sync: Never')
        
        if status['sync_in_progress']:
            self.sync_status_label.setText('Status: Syncing...')
            self.progress_bar.setRange(0, 0)
            self.progress_bar.show()
        else:
            self.sync_status_label.setText('Status: Idle')
            self.progress_bar.hide()
        
        self.auto_sync_checkbox.setChecked(status['auto_sync_enabled'])
    
    def _perform_sync(self, direction: str):
        """Perform synchronization in background thread."""
        status = self.sync_manager.get_sync_status()
        if status['sync_in_progress']:
            QMessageBox.warning(self, 'Sync In Progress', 'Synchronization already in progress')
            return
        
        if not status['logged_in']:
            QMessageBox.warning(self, 'Not Logged In', 'Please log in before syncing')
            return
        
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.sync_status_label.setText('Status: Syncing...')
        
        self.sync_thread = SyncWorkerThread(self.sync_manager, direction)
        self.sync_thread.sync_complete.connect(self._on_sync_complete)
        self.sync_thread.start()
    
    def _on_sync_complete(self, success: bool, message: str, details: dict):
        """Handle sync completion."""
        self.progress_bar.hide()
        self._update_status()
        
        if success:
            QMessageBox.information(self, 'Sync Complete', message)
        else:
            QMessageBox.warning(self, 'Sync Failed', message)
    
    def _toggle_auto_sync(self, state):
        """Toggle automatic sync."""
        if state == Qt.Checked:
            interval_text = self.interval_combo.currentText()
            
            # Parse interval
            if '15 minutes' in interval_text:
                interval_minutes = 15
            elif '30 minutes' in interval_text:
                interval_minutes = 30
            elif '1 hour' in interval_text:
                interval_minutes = 60
            elif '2 hours' in interval_text:
                interval_minutes = 120
            else:
                interval_minutes = 30
            
            self.sync_manager.start_auto_sync(interval_minutes)
            logger.info(f"Auto sync enabled with {interval_minutes} minute interval")
        else:
            self.sync_manager.stop_auto_sync()
            logger.info("Auto sync disabled")
    
    def _load_devices(self):
        """Load and display registered devices."""
        try:
            devices = self.sync_manager.get_devices()
            
            if not devices:
                self.devices_table.setRowCount(0)
                return
            
            self.devices_table.setRowCount(len(devices))
            
            for row, device in enumerate(devices):
                self.devices_table.setItem(row, 0, QTableWidgetItem(device.get('device_name', 'Unknown')))
                self.devices_table.setItem(row, 1, QTableWidgetItem(device.get('device_type', 'Unknown')))
                
                last_sync = device.get('last_sync', 'Never')
                if last_sync != 'Never':
                    try:
                        last_sync_dt = datetime.fromisoformat(last_sync)
                        last_sync = last_sync_dt.strftime('%Y-%m-%d %H:%M')
                    except Exception:
                        pass
                
                self.devices_table.setItem(row, 2, QTableWidgetItem(last_sync))
                
                # Determine status
                current_device = device.get('device_id') == self.sync_manager.device_id
                status = 'This Device' if current_device else 'Other'
                self.devices_table.setItem(row, 3, QTableWidgetItem(status))
        
        except Exception as e:
            logger.error(f"Failed to load devices: {e}", exc_info=True)
            QMessageBox.warning(self, 'Error', f'Failed to load devices: {str(e)}')
    
    def _handle_logout(self):
        """Handle logout."""
        reply = QMessageBox.question(
            self,
            'Confirm Logout',
            'Are you sure you want to sign out?\n\nAuto-sync will be disabled.',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.sync_manager.logout()
            self._update_status()
            QMessageBox.information(self, 'Logged Out', 'Successfully signed out')
            self.accept()
    
    def _delete_cloud_data(self):
        """Delete all cloud data."""
        reply = QMessageBox.warning(
            self,
            'Delete Cloud Data',
            'Are you sure you want to delete ALL your cloud data?\n\n'
            'This will delete your account and all synced alarms and settings.\n'
            'This action cannot be undone!',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Get password
        password, ok = QInputDialog.getText(
            self,
            'Confirm Deletion',
            'Enter your password to confirm deletion:',
            QLineEdit.Password
        )
        
        if not ok or not password:
            return
        
        success, message = self.sync_manager.delete_cloud_data(password)
        
        if success:
            QMessageBox.information(self, 'Data Deleted', 'All cloud data has been deleted')
            self.accept()
        else:
            QMessageBox.warning(self, 'Deletion Failed', message)
    
    def _change_password(self):
        """Change password."""
        from PyQt5.QtWidgets import QInputDialog
        
        old_password, ok = QInputDialog.getText(
            self,
            'Change Password',
            'Enter current password:',
            QLineEdit.Password
        )
        
        if not ok or not old_password:
            return
        
        new_password, ok = QInputDialog.getText(
            self,
            'Change Password',
            'Enter new password (min 8 characters):',
            QLineEdit.Password
        )
        
        if not ok or not new_password:
            return
        
        success, message = self.sync_manager.auth_manager.change_password(old_password, new_password)
        
        if success:
            QMessageBox.information(self, 'Password Changed', message)
        else:
            QMessageBox.warning(self, 'Change Failed', message)
