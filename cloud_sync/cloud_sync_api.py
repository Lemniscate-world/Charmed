"""
cloud_sync_api.py - Cloud API for alarm backup/restore and synchronization

This module provides API endpoints for:
- Alarm backup and restore
- Settings synchronization
- Device registration and management
- Conflict resolution
- Sync status tracking
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging_config import get_logger

logger = get_logger(__name__)


class CloudSyncAPI:
    """
    API for cloud synchronization operations.
    
    Provides methods for backing up and restoring alarms,
    syncing settings, and managing device data.
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize cloud sync API.
        
        Args:
            storage_dir: Directory for storing cloud data (default: ~/.alarmify/cloud_data)
        """
        if storage_dir is None:
            storage_dir = Path.home() / '.alarmify' / 'cloud_data'
        
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f'CloudSyncAPI initialized with storage: {self.storage_dir}')
    
    def _get_user_dir(self, user_id: str) -> Path:
        """Get storage directory for a specific user."""
        user_dir = self.storage_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def _calculate_checksum(self, data: Dict) -> str:
        """Calculate MD5 checksum for data integrity."""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode('utf-8')).hexdigest()
    
    def backup_alarms(self, user_id: str, alarms: List[Dict], device_id: str) -> Tuple[bool, str]:
        """
        Backup alarms to cloud storage.
        
        Args:
            user_id: User identifier
            alarms: List of alarm dictionaries
            device_id: Device identifier
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user_dir = self._get_user_dir(user_id)
            backup_file = user_dir / 'alarms_backup.json'
            
            # Prepare backup data
            backup_data = {
                'user_id': user_id,
                'device_id': device_id,
                'timestamp': datetime.utcnow().isoformat(),
                'alarms': alarms,
                'version': '1.0',
                'alarm_count': len(alarms)
            }
            
            # Add checksum for integrity
            backup_data['checksum'] = self._calculate_checksum(backup_data)
            
            # Save to file
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backed up {len(alarms)} alarms for user {user_id} from device {device_id}")
            return True, f"Backed up {len(alarms)} alarms successfully"
        
        except Exception as e:
            logger.error(f"Failed to backup alarms: {e}", exc_info=True)
            return False, f"Backup failed: {str(e)}"
    
    def restore_alarms(self, user_id: str) -> Tuple[bool, str, Optional[List[Dict]]]:
        """
        Restore alarms from cloud storage.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (success, message, alarms_list)
        """
        try:
            user_dir = self._get_user_dir(user_id)
            backup_file = user_dir / 'alarms_backup.json'
            
            if not backup_file.exists():
                logger.info(f"No backup found for user {user_id}")
                return True, "No backup found", []
            
            # Load backup
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Verify checksum
            stored_checksum = backup_data.pop('checksum', None)
            if stored_checksum:
                calculated_checksum = self._calculate_checksum(backup_data)
                if stored_checksum != calculated_checksum:
                    logger.warning(f"Checksum mismatch for user {user_id} backup")
                    return False, "Backup data corrupted", None
            
            alarms = backup_data.get('alarms', [])
            timestamp = backup_data.get('timestamp', 'unknown')
            
            logger.info(f"Restored {len(alarms)} alarms for user {user_id} from {timestamp}")
            return True, f"Restored {len(alarms)} alarms from {timestamp}", alarms
        
        except Exception as e:
            logger.error(f"Failed to restore alarms: {e}", exc_info=True)
            return False, f"Restore failed: {str(e)}", None
    
    def backup_settings(self, user_id: str, settings: Dict, device_id: str) -> Tuple[bool, str]:
        """
        Backup settings to cloud storage.
        
        Args:
            user_id: User identifier
            settings: Settings dictionary
            device_id: Device identifier
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user_dir = self._get_user_dir(user_id)
            settings_file = user_dir / 'settings_backup.json'
            
            # Prepare backup data
            backup_data = {
                'user_id': user_id,
                'device_id': device_id,
                'timestamp': datetime.utcnow().isoformat(),
                'settings': settings,
                'version': '1.0'
            }
            
            # Add checksum
            backup_data['checksum'] = self._calculate_checksum(backup_data)
            
            # Save to file
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backed up settings for user {user_id} from device {device_id}")
            return True, "Settings backed up successfully"
        
        except Exception as e:
            logger.error(f"Failed to backup settings: {e}", exc_info=True)
            return False, f"Settings backup failed: {str(e)}"
    
    def restore_settings(self, user_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Restore settings from cloud storage.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (success, message, settings_dict)
        """
        try:
            user_dir = self._get_user_dir(user_id)
            settings_file = user_dir / 'settings_backup.json'
            
            if not settings_file.exists():
                logger.info(f"No settings backup found for user {user_id}")
                return True, "No settings backup found", {}
            
            # Load backup
            with open(settings_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Verify checksum
            stored_checksum = backup_data.pop('checksum', None)
            if stored_checksum:
                calculated_checksum = self._calculate_checksum(backup_data)
                if stored_checksum != calculated_checksum:
                    logger.warning(f"Settings checksum mismatch for user {user_id}")
                    return False, "Settings data corrupted", None
            
            settings = backup_data.get('settings', {})
            timestamp = backup_data.get('timestamp', 'unknown')
            
            logger.info(f"Restored settings for user {user_id} from {timestamp}")
            return True, f"Settings restored from {timestamp}", settings
        
        except Exception as e:
            logger.error(f"Failed to restore settings: {e}", exc_info=True)
            return False, f"Settings restore failed: {str(e)}", None
    
    def register_device(self, user_id: str, device_id: str, device_name: str, device_type: str) -> Tuple[bool, str]:
        """
        Register a device for a user.
        
        Args:
            user_id: User identifier
            device_id: Unique device identifier
            device_name: Human-readable device name
            device_type: Device type (e.g., 'windows', 'mac', 'linux')
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user_dir = self._get_user_dir(user_id)
            devices_file = user_dir / 'devices.json'
            
            # Load existing devices
            devices = {}
            if devices_file.exists():
                with open(devices_file, 'r', encoding='utf-8') as f:
                    devices = json.load(f)
            
            # Add or update device
            devices[device_id] = {
                'device_id': device_id,
                'device_name': device_name,
                'device_type': device_type,
                'registered_at': datetime.utcnow().isoformat(),
                'last_sync': datetime.utcnow().isoformat()
            }
            
            # Save devices
            with open(devices_file, 'w', encoding='utf-8') as f:
                json.dump(devices, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Registered device {device_name} ({device_id}) for user {user_id}")
            return True, f"Device {device_name} registered successfully"
        
        except Exception as e:
            logger.error(f"Failed to register device: {e}", exc_info=True)
            return False, f"Device registration failed: {str(e)}"
    
    def get_devices(self, user_id: str) -> Tuple[bool, str, Optional[List[Dict]]]:
        """
        Get all registered devices for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (success, message, devices_list)
        """
        try:
            user_dir = self._get_user_dir(user_id)
            devices_file = user_dir / 'devices.json'
            
            if not devices_file.exists():
                return True, "No devices registered", []
            
            # Load devices
            with open(devices_file, 'r', encoding='utf-8') as f:
                devices = json.load(f)
            
            devices_list = list(devices.values())
            
            logger.info(f"Retrieved {len(devices_list)} devices for user {user_id}")
            return True, f"Found {len(devices_list)} devices", devices_list
        
        except Exception as e:
            logger.error(f"Failed to get devices: {e}", exc_info=True)
            return False, f"Failed to get devices: {str(e)}", None
    
    def update_device_sync_time(self, user_id: str, device_id: str) -> Tuple[bool, str]:
        """
        Update last sync time for a device.
        
        Args:
            user_id: User identifier
            device_id: Device identifier
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user_dir = self._get_user_dir(user_id)
            devices_file = user_dir / 'devices.json'
            
            if not devices_file.exists():
                return False, "Device not registered"
            
            # Load devices
            with open(devices_file, 'r', encoding='utf-8') as f:
                devices = json.load(f)
            
            if device_id not in devices:
                return False, "Device not found"
            
            # Update sync time
            devices[device_id]['last_sync'] = datetime.utcnow().isoformat()
            
            # Save devices
            with open(devices_file, 'w', encoding='utf-8') as f:
                json.dump(devices, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Updated sync time for device {device_id}")
            return True, "Sync time updated"
        
        except Exception as e:
            logger.error(f"Failed to update device sync time: {e}", exc_info=True)
            return False, f"Failed to update sync time: {str(e)}"
    
    def get_sync_history(self, user_id: str, limit: int = 10) -> Tuple[bool, str, Optional[List[Dict]]]:
        """
        Get sync history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of history entries to return
            
        Returns:
            Tuple of (success, message, history_list)
        """
        try:
            user_dir = self._get_user_dir(user_id)
            history_file = user_dir / 'sync_history.json'
            
            if not history_file.exists():
                return True, "No sync history", []
            
            # Load history
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Sort by timestamp and limit
            history_list = sorted(
                history.get('entries', []),
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )[:limit]
            
            logger.info(f"Retrieved {len(history_list)} sync history entries for user {user_id}")
            return True, f"Found {len(history_list)} history entries", history_list
        
        except Exception as e:
            logger.error(f"Failed to get sync history: {e}", exc_info=True)
            return False, f"Failed to get sync history: {str(e)}", None
    
    def record_sync(self, user_id: str, device_id: str, sync_type: str, status: str, details: Optional[str] = None) -> Tuple[bool, str]:
        """
        Record a sync operation in history.
        
        Args:
            user_id: User identifier
            device_id: Device identifier
            sync_type: Type of sync (e.g., 'alarms', 'settings', 'full')
            status: Status of sync (e.g., 'success', 'failed', 'partial')
            details: Optional details about the sync
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user_dir = self._get_user_dir(user_id)
            history_file = user_dir / 'sync_history.json'
            
            # Load existing history
            history = {'entries': []}
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Add new entry
            entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'device_id': device_id,
                'sync_type': sync_type,
                'status': status,
                'details': details
            }
            
            history['entries'].append(entry)
            
            # Keep only last 100 entries
            history['entries'] = history['entries'][-100:]
            
            # Save history
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Recorded sync for user {user_id}: {sync_type} - {status}")
            return True, "Sync recorded"
        
        except Exception as e:
            logger.error(f"Failed to record sync: {e}", exc_info=True)
            return False, f"Failed to record sync: {str(e)}"
    
    def delete_user_data(self, user_id: str) -> Tuple[bool, str]:
        """
        Delete all cloud data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user_dir = self._get_user_dir(user_id)
            
            # Delete all files in user directory
            for file in user_dir.iterdir():
                if file.is_file():
                    file.unlink()
            
            # Remove directory
            user_dir.rmdir()
            
            logger.info(f"Deleted all cloud data for user {user_id}")
            return True, "User data deleted successfully"
        
        except Exception as e:
            logger.error(f"Failed to delete user data: {e}", exc_info=True)
            return False, f"Failed to delete user data: {str(e)}"
