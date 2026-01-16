"""
cloud_sync_manager.py - Main cloud synchronization manager

This module provides the main CloudSyncManager class that coordinates:
- Authentication with CloudAuthManager
- Alarm backup/restore with CloudSyncAPI
- Settings synchronization
- Device management
- Conflict resolution
- Automatic sync scheduling
"""

import uuid
import platform
import threading
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Callable
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging_config import get_logger
from cloud_sync.cloud_auth import CloudAuthManager
from cloud_sync.cloud_sync_api import CloudSyncAPI
from cloud_sync.sync_conflict_resolver import SyncConflictResolver

logger = get_logger(__name__)


class CloudSyncManager:
    """
    Main manager for cloud synchronization.
    
    Coordinates authentication, data backup/restore, conflict resolution,
    and automatic synchronization across devices.
    """
    
    def __init__(self, alarm_manager=None, settings_manager=None):
        """
        Initialize cloud sync manager.
        
        Args:
            alarm_manager: Reference to alarm manager for syncing alarms
            settings_manager: Reference to settings manager for syncing settings
        """
        self.auth_manager = CloudAuthManager()
        self.sync_api = CloudSyncAPI()
        self.conflict_resolver = SyncConflictResolver()
        
        self.alarm_manager = alarm_manager
        self.settings_manager = settings_manager
        
        # Device identification
        self.device_id = self._get_or_create_device_id()
        self.device_name = self._get_device_name()
        self.device_type = self._get_device_type()
        
        # Sync state
        self.auto_sync_enabled = False
        self.sync_interval_minutes = 30
        self.last_sync_time: Optional[datetime] = None
        self.sync_in_progress = False
        
        # Threading
        self._sync_thread: Optional[threading.Thread] = None
        self._sync_stop_event = threading.Event()
        
        # Callbacks
        self.on_sync_complete: Optional[Callable] = None
        self.on_sync_error: Optional[Callable] = None
        
        logger.info(f'CloudSyncManager initialized for device: {self.device_name} ({self.device_id})')
    
    def _get_or_create_device_id(self) -> str:
        """Get or create unique device ID."""
        device_id_file = Path.home() / '.alarmify' / '.device_id'
        
        if device_id_file.exists():
            try:
                with open(device_id_file, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                logger.warning(f"Failed to read device ID: {e}")
        
        # Generate new device ID
        device_id = str(uuid.uuid4())
        
        try:
            device_id_file.parent.mkdir(parents=True, exist_ok=True)
            with open(device_id_file, 'w') as f:
                f.write(device_id)
            logger.info(f"Generated new device ID: {device_id}")
        except Exception as e:
            logger.error(f"Failed to save device ID: {e}")
        
        return device_id
    
    def _get_device_name(self) -> str:
        """Get device name."""
        try:
            return platform.node() or f"Device-{self.device_id[:8]}"
        except Exception:
            return f"Device-{self.device_id[:8]}"
    
    def _get_device_type(self) -> str:
        """Get device type."""
        system = platform.system().lower()
        if 'windows' in system:
            return 'windows'
        elif 'darwin' in system:
            return 'mac'
        elif 'linux' in system:
            return 'linux'
        else:
            return 'unknown'
    
    def is_logged_in(self) -> bool:
        """
        Check if user is logged in.
        
        Returns:
            True if logged in, False otherwise
        """
        return self.auth_manager.is_logged_in()
    
    def register(self, email: str, password: str, display_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Register new user account.
        
        Args:
            email: User email
            password: User password
            display_name: Optional display name
            
        Returns:
            Tuple of (success, message)
        """
        success, message, user_id = self.auth_manager.register(email, password, display_name)
        
        if success:
            logger.info(f"User registered successfully: {email}")
        
        return success, message
    
    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Login with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, message)
        """
        success, message, access_token, refresh_token = self.auth_manager.login(email, password)
        
        if success:
            # Register device
            user = self.auth_manager.get_current_user()
            if user:
                self.sync_api.register_device(
                    user['user_id'],
                    self.device_id,
                    self.device_name,
                    self.device_type
                )
            
            logger.info(f"User logged in successfully: {email}")
        
        return success, message
    
    def logout(self) -> None:
        """Logout current user."""
        # Stop auto sync if running
        self.stop_auto_sync()
        
        self.auth_manager.logout()
        self.last_sync_time = None
        
        logger.info("User logged out")
    
    def get_current_user(self) -> Optional[Dict]:
        """
        Get current user information.
        
        Returns:
            User dictionary if logged in, None otherwise
        """
        return self.auth_manager.get_current_user()
    
    def sync_alarms(self, direction: str = 'both') -> Tuple[bool, str]:
        """
        Synchronize alarms with cloud.
        
        Args:
            direction: 'upload', 'download', or 'both'
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_logged_in():
            return False, "Not logged in"
        
        if self.sync_in_progress:
            return False, "Sync already in progress"
        
        self.sync_in_progress = True
        
        try:
            user = self.auth_manager.get_current_user()
            if not user:
                return False, "User not found"
            
            user_id = user['user_id']
            
            # Get local alarms
            local_alarms = self._get_local_alarms()
            
            if direction in ['upload', 'both']:
                # Upload alarms to cloud
                success, message = self.sync_api.backup_alarms(user_id, local_alarms, self.device_id)
                if not success:
                    logger.error(f"Failed to upload alarms: {message}")
                    if direction == 'upload':
                        return False, message
            
            if direction in ['download', 'both']:
                # Download alarms from cloud
                success, message, remote_alarms = self.sync_api.restore_alarms(user_id)
                if not success:
                    logger.error(f"Failed to download alarms: {message}")
                    if direction == 'download':
                        return False, message
                
                # Resolve conflicts and merge
                if remote_alarms and direction == 'both':
                    merged_alarms, num_conflicts = self.conflict_resolver.merge_data(
                        local_alarms,
                        remote_alarms
                    )
                    
                    if num_conflicts > 0:
                        logger.info(f"Resolved {num_conflicts} conflicts during sync")
                    
                    # Apply merged alarms
                    self._apply_alarms(merged_alarms)
                elif remote_alarms:
                    # Download only - replace local with remote
                    self._apply_alarms(remote_alarms)
            
            # Update sync time
            self.last_sync_time = datetime.now()
            self.sync_api.update_device_sync_time(user_id, self.device_id)
            self.sync_api.record_sync(user_id, self.device_id, 'alarms', 'success')
            
            logger.info("Alarm sync completed successfully")
            return True, "Alarms synchronized successfully"
        
        except Exception as e:
            logger.error(f"Alarm sync failed: {e}", exc_info=True)
            self.sync_api.record_sync(
                user['user_id'] if user else '',
                self.device_id,
                'alarms',
                'failed',
                str(e)
            )
            return False, f"Sync failed: {str(e)}"
        
        finally:
            self.sync_in_progress = False
    
    def sync_settings(self, direction: str = 'both') -> Tuple[bool, str]:
        """
        Synchronize settings with cloud.
        
        Args:
            direction: 'upload', 'download', or 'both'
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_logged_in():
            return False, "Not logged in"
        
        if self.sync_in_progress:
            return False, "Sync already in progress"
        
        self.sync_in_progress = True
        
        try:
            user = self.auth_manager.get_current_user()
            if not user:
                return False, "User not found"
            
            user_id = user['user_id']
            
            # Get local settings
            local_settings = self._get_local_settings()
            
            if direction in ['upload', 'both']:
                # Upload settings to cloud
                success, message = self.sync_api.backup_settings(user_id, local_settings, self.device_id)
                if not success:
                    logger.error(f"Failed to upload settings: {message}")
                    if direction == 'upload':
                        return False, message
            
            if direction in ['download', 'both']:
                # Download settings from cloud
                success, message, remote_settings = self.sync_api.restore_settings(user_id)
                if not success:
                    logger.error(f"Failed to download settings: {message}")
                    if direction == 'download':
                        return False, message
                
                # Apply remote settings
                if remote_settings:
                    if direction == 'both':
                        # Merge settings intelligently
                        merged_settings = {**remote_settings, **local_settings}
                        self._apply_settings(merged_settings)
                    else:
                        # Download only - replace local with remote
                        self._apply_settings(remote_settings)
            
            # Update sync time
            self.last_sync_time = datetime.now()
            self.sync_api.update_device_sync_time(user_id, self.device_id)
            self.sync_api.record_sync(user_id, self.device_id, 'settings', 'success')
            
            logger.info("Settings sync completed successfully")
            return True, "Settings synchronized successfully"
        
        except Exception as e:
            logger.error(f"Settings sync failed: {e}", exc_info=True)
            self.sync_api.record_sync(
                user['user_id'] if user else '',
                self.device_id,
                'settings',
                'failed',
                str(e)
            )
            return False, f"Sync failed: {str(e)}"
        
        finally:
            self.sync_in_progress = False
    
    def sync_all(self, direction: str = 'both') -> Tuple[bool, str, Dict]:
        """
        Synchronize all data (alarms and settings).
        
        Args:
            direction: 'upload', 'download', or 'both'
            
        Returns:
            Tuple of (success, message, details_dict)
        """
        results = {
            'alarms_success': False,
            'alarms_message': '',
            'settings_success': False,
            'settings_message': ''
        }
        
        # Sync alarms
        alarms_success, alarms_message = self.sync_alarms(direction)
        results['alarms_success'] = alarms_success
        results['alarms_message'] = alarms_message
        
        # Sync settings
        settings_success, settings_message = self.sync_settings(direction)
        results['settings_success'] = settings_success
        results['settings_message'] = settings_message
        
        # Overall success if both succeeded
        overall_success = alarms_success and settings_success
        
        if overall_success:
            message = "All data synchronized successfully"
        elif alarms_success:
            message = f"Alarms synced, but settings failed: {settings_message}"
        elif settings_success:
            message = f"Settings synced, but alarms failed: {alarms_message}"
        else:
            message = "Sync failed for both alarms and settings"
        
        if self.on_sync_complete and overall_success:
            try:
                self.on_sync_complete(results)
            except Exception as e:
                logger.error(f"Error in sync complete callback: {e}")
        
        if self.on_sync_error and not overall_success:
            try:
                self.on_sync_error(message, results)
            except Exception as e:
                logger.error(f"Error in sync error callback: {e}")
        
        return overall_success, message, results
    
    def start_auto_sync(self, interval_minutes: int = 30) -> None:
        """
        Start automatic synchronization.
        
        Args:
            interval_minutes: Sync interval in minutes
        """
        if self.auto_sync_enabled:
            logger.warning("Auto sync already enabled")
            return
        
        if not self.is_logged_in():
            logger.warning("Cannot start auto sync: not logged in")
            return
        
        self.auto_sync_enabled = True
        self.sync_interval_minutes = interval_minutes
        self._sync_stop_event.clear()
        
        def auto_sync_worker():
            logger.info(f"Auto sync started with {interval_minutes} minute interval")
            
            while not self._sync_stop_event.is_set():
                try:
                    # Wait for interval or stop event
                    if self._sync_stop_event.wait(interval_minutes * 60):
                        break
                    
                    # Perform sync
                    if self.is_logged_in():
                        logger.info("Performing automatic sync")
                        self.sync_all('both')
                    else:
                        logger.info("Auto sync stopped: user logged out")
                        break
                
                except Exception as e:
                    logger.error(f"Error in auto sync: {e}", exc_info=True)
            
            logger.info("Auto sync stopped")
        
        self._sync_thread = threading.Thread(
            target=auto_sync_worker,
            daemon=True,
            name='CloudAutoSync'
        )
        self._sync_thread.start()
    
    def stop_auto_sync(self) -> None:
        """Stop automatic synchronization."""
        if not self.auto_sync_enabled:
            return
        
        self.auto_sync_enabled = False
        self._sync_stop_event.set()
        
        if self._sync_thread and self._sync_thread.is_alive():
            self._sync_thread.join(timeout=5.0)
        
        logger.info("Auto sync stopped")
    
    def get_devices(self) -> List[Dict]:
        """
        Get all registered devices for current user.
        
        Returns:
            List of device dictionaries
        """
        if not self.is_logged_in():
            return []
        
        user = self.auth_manager.get_current_user()
        if not user:
            return []
        
        success, message, devices = self.sync_api.get_devices(user['user_id'])
        
        if success and devices:
            return devices
        
        return []
    
    def get_sync_status(self) -> Dict:
        """
        Get current sync status.
        
        Returns:
            Dictionary with sync status information
        """
        return {
            'logged_in': self.is_logged_in(),
            'auto_sync_enabled': self.auto_sync_enabled,
            'sync_in_progress': self.sync_in_progress,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'device_id': self.device_id,
            'device_name': self.device_name
        }
    
    def _get_local_alarms(self) -> List[Dict]:
        """Get local alarms from alarm manager."""
        if not self.alarm_manager:
            return []
        
        try:
            alarms = self.alarm_manager.get_alarms()
            # Add timestamp if not present
            for alarm in alarms:
                if 'last_modified' not in alarm:
                    alarm['last_modified'] = datetime.now().isoformat()
            return alarms
        except Exception as e:
            logger.error(f"Failed to get local alarms: {e}", exc_info=True)
            return []
    
    def _apply_alarms(self, alarms: List[Dict]) -> None:
        """Apply alarms to alarm manager."""
        if not self.alarm_manager:
            logger.warning("No alarm manager available to apply alarms")
            return
        
        try:
            # Clear existing alarms
            self.alarm_manager.clear_all_alarms()
            
            # Add synced alarms
            for alarm in alarms:
                # Extract alarm data
                time_str = alarm.get('time')
                playlist_name = alarm.get('playlist')
                playlist_uri = alarm.get('playlist_uri')
                volume = alarm.get('volume', 80)
                fade_in_enabled = alarm.get('fade_in_enabled', False)
                fade_in_duration = alarm.get('fade_in_duration', 10)
                days = alarm.get('days')
                
                if time_str and playlist_uri:
                    # Need spotify_api - get from alarm_manager if available
                    if hasattr(self.alarm_manager, 'spotify_api'):
                        spotify_api = self.alarm_manager.spotify_api
                    else:
                        spotify_api = None
                    
                    if spotify_api:
                        self.alarm_manager.set_alarm(
                            time_str,
                            playlist_name or 'Synced Playlist',
                            playlist_uri,
                            spotify_api,
                            volume,
                            fade_in_enabled,
                            fade_in_duration,
                            days
                        )
            
            logger.info(f"Applied {len(alarms)} alarms from sync")
        
        except Exception as e:
            logger.error(f"Failed to apply alarms: {e}", exc_info=True)
    
    def _get_local_settings(self) -> Dict:
        """Get local settings."""
        # Placeholder - would integrate with actual settings manager
        return {
            'theme': 'dark',
            'notifications_enabled': True,
            'last_modified': datetime.now().isoformat()
        }
    
    def _apply_settings(self, settings: Dict) -> None:
        """Apply settings."""
        # Placeholder - would integrate with actual settings manager
        logger.info(f"Applied settings from sync: {settings}")
    
    def delete_cloud_data(self, password: str) -> Tuple[bool, str]:
        """
        Delete all cloud data for current user.
        
        Args:
            password: Password for verification
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_logged_in():
            return False, "Not logged in"
        
        user = self.auth_manager.get_current_user()
        if not user:
            return False, "User not found"
        
        # Verify password
        success, message = self.auth_manager.delete_account(password)
        
        if not success:
            return False, message
        
        # Delete cloud data
        user_id = user['user_id']
        success, message = self.sync_api.delete_user_data(user_id)
        
        if success:
            logger.info("All cloud data deleted")
        
        return success, message
