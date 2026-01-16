"""
test_cloud_sync.py - Tests for cloud synchronization infrastructure

Tests the cloud sync system including authentication, backup/restore,
device management, and conflict resolution.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud_sync.cloud_auth import CloudAuthManager
from cloud_sync.cloud_sync_api import CloudSyncAPI
from cloud_sync.sync_conflict_resolver import SyncConflictResolver
from cloud_sync.cloud_sync_manager import CloudSyncManager


@pytest.fixture
def temp_dir():
    """Create temporary directory for test data."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def auth_manager(temp_dir):
    """Create CloudAuthManager with temporary storage."""
    auth_file = temp_dir / 'cloud_auth.json'
    return CloudAuthManager(auth_file=auth_file)


@pytest.fixture
def sync_api(temp_dir):
    """Create CloudSyncAPI with temporary storage."""
    storage_dir = temp_dir / 'cloud_data'
    return CloudSyncAPI(storage_dir=storage_dir)


@pytest.fixture
def conflict_resolver():
    """Create SyncConflictResolver."""
    return SyncConflictResolver()


class TestCloudAuth:
    """Tests for CloudAuthManager."""
    
    def test_register_success(self, auth_manager):
        """Test successful user registration."""
        success, message, user_id = auth_manager.register(
            'test@example.com',
            'password123',
            'Test User'
        )
        
        assert success
        assert user_id is not None
        assert 'success' in message.lower()
    
    def test_register_duplicate(self, auth_manager):
        """Test registration with duplicate email fails."""
        auth_manager.register('test@example.com', 'password123')
        success, message, user_id = auth_manager.register('test@example.com', 'password456')
        
        assert not success
        assert user_id is None
        assert 'exists' in message.lower()
    
    def test_register_weak_password(self, auth_manager):
        """Test registration with weak password fails."""
        success, message, user_id = auth_manager.register('test@example.com', 'weak')
        
        assert not success
        assert user_id is None
        assert '8 characters' in message.lower()
    
    def test_login_success(self, auth_manager):
        """Test successful login."""
        auth_manager.register('test@example.com', 'password123')
        success, message, access_token, refresh_token = auth_manager.login(
            'test@example.com',
            'password123'
        )
        
        assert success
        assert access_token is not None
        assert refresh_token is not None
        assert 'success' in message.lower()
    
    def test_login_wrong_password(self, auth_manager):
        """Test login with wrong password fails."""
        auth_manager.register('test@example.com', 'password123')
        success, message, access_token, refresh_token = auth_manager.login(
            'test@example.com',
            'wrongpassword'
        )
        
        assert not success
        assert access_token is None
        assert refresh_token is None
    
    def test_login_nonexistent_user(self, auth_manager):
        """Test login with non-existent user fails."""
        success, message, access_token, refresh_token = auth_manager.login(
            'nonexistent@example.com',
            'password123'
        )
        
        assert not success
        assert access_token is None
    
    def test_is_logged_in(self, auth_manager):
        """Test login status check."""
        assert not auth_manager.is_logged_in()
        
        auth_manager.register('test@example.com', 'password123')
        auth_manager.login('test@example.com', 'password123')
        
        assert auth_manager.is_logged_in()
    
    def test_logout(self, auth_manager):
        """Test logout clears session."""
        auth_manager.register('test@example.com', 'password123')
        auth_manager.login('test@example.com', 'password123')
        
        assert auth_manager.is_logged_in()
        
        auth_manager.logout()
        
        assert not auth_manager.is_logged_in()
    
    def test_get_current_user(self, auth_manager):
        """Test getting current user info."""
        auth_manager.register('test@example.com', 'password123', 'Test User')
        auth_manager.login('test@example.com', 'password123')
        
        user = auth_manager.get_current_user()
        
        assert user is not None
        assert user['email'] == 'test@example.com'
        assert user['display_name'] == 'Test User'
        assert 'password_hash' not in user


class TestCloudSyncAPI:
    """Tests for CloudSyncAPI."""
    
    def test_backup_alarms(self, sync_api):
        """Test backing up alarms."""
        alarms = [
            {'time': '07:00', 'playlist': 'Morning', 'volume': 80},
            {'time': '22:00', 'playlist': 'Night', 'volume': 60}
        ]
        
        success, message = sync_api.backup_alarms('user123', alarms, 'device1')
        
        assert success
        assert 'success' in message.lower()
    
    def test_restore_alarms(self, sync_api):
        """Test restoring alarms."""
        alarms = [
            {'time': '07:00', 'playlist': 'Morning', 'volume': 80},
            {'time': '22:00', 'playlist': 'Night', 'volume': 60}
        ]
        
        sync_api.backup_alarms('user123', alarms, 'device1')
        success, message, restored_alarms = sync_api.restore_alarms('user123')
        
        assert success
        assert len(restored_alarms) == 2
        assert restored_alarms[0]['time'] == '07:00'
        assert restored_alarms[1]['playlist'] == 'Night'
    
    def test_restore_no_backup(self, sync_api):
        """Test restoring when no backup exists."""
        success, message, alarms = sync_api.restore_alarms('nonexistent')
        
        assert success
        assert alarms == []
    
    def test_backup_settings(self, sync_api):
        """Test backing up settings."""
        settings = {'theme': 'dark', 'notifications': True}
        
        success, message = sync_api.backup_settings('user123', settings, 'device1')
        
        assert success
    
    def test_restore_settings(self, sync_api):
        """Test restoring settings."""
        settings = {'theme': 'dark', 'notifications': True}
        
        sync_api.backup_settings('user123', settings, 'device1')
        success, message, restored_settings = sync_api.restore_settings('user123')
        
        assert success
        assert restored_settings['theme'] == 'dark'
        assert restored_settings['notifications'] is True
    
    def test_register_device(self, sync_api):
        """Test registering a device."""
        success, message = sync_api.register_device(
            'user123',
            'device1',
            'My Computer',
            'windows'
        )
        
        assert success
    
    def test_get_devices(self, sync_api):
        """Test getting registered devices."""
        sync_api.register_device('user123', 'device1', 'Computer 1', 'windows')
        sync_api.register_device('user123', 'device2', 'Computer 2', 'mac')
        
        success, message, devices = sync_api.get_devices('user123')
        
        assert success
        assert len(devices) == 2
        assert any(d['device_name'] == 'Computer 1' for d in devices)


class TestSyncConflictResolver:
    """Tests for SyncConflictResolver."""
    
    def test_no_conflicts(self, conflict_resolver):
        """Test detection when no conflicts exist."""
        local = [{'time': '07:00', 'playlist': 'Morning'}]
        remote = [{'time': '22:00', 'playlist': 'Night'}]
        
        has_conflicts, conflicts = conflict_resolver.detect_conflicts(local, remote)
        
        assert not has_conflicts
        assert len(conflicts) == 0
    
    def test_detect_conflicts(self, conflict_resolver):
        """Test conflict detection."""
        local = [{'time': '07:00', 'playlist': 'Morning', 'volume': 80}]
        remote = [{'time': '07:00', 'playlist': 'Morning', 'volume': 60}]
        
        has_conflicts, conflicts = conflict_resolver.detect_conflicts(local, remote)
        
        assert has_conflicts
        assert len(conflicts) == 1
    
    def test_resolve_newest_wins(self, conflict_resolver):
        """Test newest wins conflict resolution."""
        conflict = {
            'key': '07:00:Morning',
            'local': {
                'time': '07:00',
                'playlist': 'Morning',
                'volume': 80,
                'last_modified': '2024-01-16T10:00:00'
            },
            'remote': {
                'time': '07:00',
                'playlist': 'Morning',
                'volume': 60,
                'last_modified': '2024-01-16T12:00:00'
            }
        }
        
        resolved = conflict_resolver._resolve_newest_wins(conflict)
        
        # Remote is newer, should win
        assert resolved['volume'] == 60
    
    def test_merge_data_no_conflicts(self, conflict_resolver):
        """Test merging data without conflicts."""
        local = [
            {'time': '07:00', 'playlist': 'Morning', 'volume': 80},
            {'time': '12:00', 'playlist': 'Lunch', 'volume': 70}
        ]
        remote = [
            {'time': '22:00', 'playlist': 'Night', 'volume': 60}
        ]
        
        merged, num_conflicts = conflict_resolver.merge_data(local, remote)
        
        assert num_conflicts == 0
        assert len(merged) == 3
    
    def test_merge_data_with_conflicts(self, conflict_resolver):
        """Test merging data with conflicts."""
        local = [
            {'time': '07:00', 'playlist': 'Morning', 'volume': 80,
             'last_modified': '2024-01-16T10:00:00'}
        ]
        remote = [
            {'time': '07:00', 'playlist': 'Morning', 'volume': 60,
             'last_modified': '2024-01-16T12:00:00'}
        ]
        
        merged, num_conflicts = conflict_resolver.merge_data(local, remote)
        
        assert num_conflicts == 1
        assert len(merged) == 1
        # Remote should win (newer)
        assert merged[0]['volume'] == 60


class TestCloudSyncManager:
    """Tests for CloudSyncManager (integration tests)."""
    
    def test_initialization(self):
        """Test CloudSyncManager initialization."""
        manager = CloudSyncManager()
        
        assert manager.device_id is not None
        assert manager.device_name is not None
        assert not manager.is_logged_in()
    
    def test_register_and_login(self):
        """Test registration and login flow."""
        manager = CloudSyncManager()
        
        # Register
        success, message = manager.register('test@example.com', 'password123', 'Test')
        assert success
        
        # Logout
        manager.logout()
        assert not manager.is_logged_in()
        
        # Login
        success, message = manager.login('test@example.com', 'password123')
        assert success
        assert manager.is_logged_in()
    
    def test_get_sync_status(self):
        """Test getting sync status."""
        manager = CloudSyncManager()
        status = manager.get_sync_status()
        
        assert 'logged_in' in status
        assert 'auto_sync_enabled' in status
        assert 'device_id' in status
    
    def test_device_registration_on_login(self):
        """Test device is automatically registered on login."""
        manager = CloudSyncManager()
        
        manager.register('test@example.com', 'password123')
        manager.login('test@example.com', 'password123')
        
        devices = manager.get_devices()
        
        assert len(devices) > 0
        assert any(d['device_id'] == manager.device_id for d in devices)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
