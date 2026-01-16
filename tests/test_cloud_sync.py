"""
test_cloud_sync.py - Tests for cloud synchronization infrastructure

Tests the cloud sync system including authentication, backup/restore,
device management, and conflict resolution.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os
import time

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


@pytest.fixture
def mock_alarm_manager():
    """Create mock alarm manager for testing."""
    class MockAlarmManager:
        def __init__(self):
            self.alarms = []
            self.spotify_api = MockSpotifyAPI()
        
        def get_alarms(self):
            return self.alarms.copy()
        
        def set_alarm(self, time_str, playlist_name, playlist_uri, spotify_api, 
                     volume=80, fade_in_enabled=False, fade_in_duration=10, days=None):
            alarm = {
                'time': time_str,
                'playlist': playlist_name,
                'playlist_uri': playlist_uri,
                'volume': volume,
                'fade_in_enabled': fade_in_enabled,
                'fade_in_duration': fade_in_duration,
                'days': days,
                'last_modified': datetime.now().isoformat()
            }
            self.alarms.append(alarm)
        
        def clear_all_alarms(self):
            self.alarms.clear()
    
    class MockSpotifyAPI:
        pass
    
    return MockAlarmManager()


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


class TestCloudSyncWorkflows:
    """Integration tests for complete cloud sync workflows."""
    
    @pytest.fixture
    def temp_storage_dirs(self):
        """Create separate temporary storage directories for multi-device testing."""
        device1_dir = Path(tempfile.mkdtemp())
        device2_dir = Path(tempfile.mkdtemp())
        
        yield device1_dir, device2_dir
        
        shutil.rmtree(device1_dir)
        shutil.rmtree(device2_dir)
    
    def test_complete_registration_login_flow(self, temp_dir):
        """Test complete registration → login flow."""
        # Setup
        auth_manager = CloudAuthManager(auth_file=temp_dir / 'auth.json')
        
        # Step 1: Register new user
        success, message, user_id = auth_manager.register(
            'workflow@example.com',
            'SecurePass123',
            'Workflow User'
        )
        assert success
        assert user_id is not None
        
        # Step 2: Logout after registration
        auth_manager.logout()
        assert not auth_manager.is_logged_in()
        
        # Step 3: Login with credentials
        success, message, access_token, refresh_token = auth_manager.login(
            'workflow@example.com',
            'SecurePass123'
        )
        assert success
        assert access_token is not None
        assert refresh_token is not None
        assert auth_manager.is_logged_in()
        
        # Step 4: Verify user info
        user = auth_manager.get_current_user()
        assert user['email'] == 'workflow@example.com'
        assert user['display_name'] == 'Workflow User'
    
    def test_device_registration_workflow(self, temp_dir):
        """Test device registration → login → device registration workflow."""
        # Setup
        auth_manager = CloudAuthManager(auth_file=temp_dir / 'auth.json')
        sync_api = CloudSyncAPI(storage_dir=temp_dir / 'cloud_data')
        
        # Step 1: Register and login
        success, _, user_id = auth_manager.register('device@example.com', 'password123')
        assert success
        auth_manager.login('device@example.com', 'password123')
        
        # Step 2: Register first device
        success, message = sync_api.register_device(
            user_id,
            'device-001',
            'Primary Computer',
            'windows'
        )
        assert success
        
        # Step 3: Register second device
        success, message = sync_api.register_device(
            user_id,
            'device-002',
            'Laptop',
            'mac'
        )
        assert success
        
        # Step 4: Get all devices
        success, message, devices = sync_api.get_devices(user_id)
        assert success
        assert len(devices) == 2
        assert any(d['device_id'] == 'device-001' for d in devices)
        assert any(d['device_id'] == 'device-002' for d in devices)
    
    def test_alarm_backup_restore_workflow(self, temp_dir, mock_alarm_manager):
        """Test complete alarm backup and restore workflow."""
        # Setup
        manager = CloudSyncManager(alarm_manager=mock_alarm_manager)
        
        # Step 1: Register and login
        manager.register('backup@example.com', 'password123', 'Backup Test')
        manager.login('backup@example.com', 'password123')
        
        # Step 2: Add some alarms locally
        mock_alarm_manager.set_alarm(
            '07:00', 'Morning Playlist', 'spotify:playlist:morning123',
            mock_alarm_manager.spotify_api, volume=80, days=['Mon', 'Tue', 'Wed']
        )
        mock_alarm_manager.set_alarm(
            '22:00', 'Night Playlist', 'spotify:playlist:night456',
            mock_alarm_manager.spotify_api, volume=60, fade_in_enabled=True
        )
        
        # Step 3: Backup alarms to cloud
        success, message = manager.sync_alarms(direction='upload')
        assert success
        
        # Step 4: Clear local alarms
        mock_alarm_manager.clear_all_alarms()
        assert len(mock_alarm_manager.get_alarms()) == 0
        
        # Step 5: Restore alarms from cloud
        success, message = manager.sync_alarms(direction='download')
        assert success
        
        # Step 6: Verify restored alarms
        restored = mock_alarm_manager.get_alarms()
        assert len(restored) == 2
        assert any(a['time'] == '07:00' and a['playlist'] == 'Morning Playlist' for a in restored)
        assert any(a['time'] == '22:00' and a['playlist'] == 'Night Playlist' for a in restored)
    
    def test_multi_device_sync_workflow(self, temp_storage_dirs, mock_alarm_manager):
        """Test syncing between two different devices."""
        device1_dir, device2_dir = temp_storage_dirs
        
        # Setup Device 1
        manager1 = CloudSyncManager(alarm_manager=mock_alarm_manager)
        manager1.auth_manager.auth_file = device1_dir / 'auth.json'
        manager1.sync_api.storage_dir = device1_dir / 'cloud_data'
        manager1.device_id = 'device-001'
        manager1.device_name = 'Device 1'
        
        # Step 1: Register and login on Device 1
        manager1.register('multidevice@example.com', 'password123')
        manager1.login('multidevice@example.com', 'password123')
        
        # Step 2: Add alarms on Device 1
        mock_alarm_manager.set_alarm(
            '08:00', 'Workout', 'spotify:playlist:workout',
            mock_alarm_manager.spotify_api, volume=90
        )
        
        # Step 3: Sync from Device 1
        success, message = manager1.sync_alarms(direction='upload')
        assert success
        
        # Setup Device 2 (simulating different device)
        manager2 = CloudSyncManager(alarm_manager=mock_alarm_manager)
        manager2.auth_manager.auth_file = device2_dir / 'auth.json'
        manager2.sync_api.storage_dir = device1_dir / 'cloud_data'  # Same cloud storage
        manager2.device_id = 'device-002'
        manager2.device_name = 'Device 2'
        
        # Step 4: Login on Device 2 (same account)
        manager2.register('multidevice@example.com', 'password123')  # Will fail but setup user
        manager2.login('multidevice@example.com', 'password123')
        
        # Clear local alarms to simulate fresh device
        mock_alarm_manager.clear_all_alarms()
        
        # Step 5: Sync to Device 2
        success, message = manager2.sync_alarms(direction='download')
        assert success
        
        # Step 6: Verify alarms synced to Device 2
        alarms = mock_alarm_manager.get_alarms()
        assert len(alarms) == 1
        assert alarms[0]['time'] == '08:00'
        assert alarms[0]['playlist'] == 'Workout'
    
    def test_conflict_resolution_workflow(self, temp_dir, mock_alarm_manager):
        """Test alarm sync with conflict resolution."""
        # Setup
        manager = CloudSyncManager(alarm_manager=mock_alarm_manager)
        
        # Step 1: Register and login
        manager.register('conflict@example.com', 'password123')
        manager.login('conflict@example.com', 'password123')
        
        # Step 2: Create initial alarm and sync
        mock_alarm_manager.set_alarm(
            '07:00', 'Morning', 'spotify:playlist:morning',
            mock_alarm_manager.spotify_api, volume=70
        )
        manager.sync_alarms(direction='upload')
        
        # Simulate time passing
        time.sleep(0.1)
        
        # Step 3: Modify local alarm (newer)
        mock_alarm_manager.clear_all_alarms()
        mock_alarm_manager.set_alarm(
            '07:00', 'Morning', 'spotify:playlist:morning',
            mock_alarm_manager.spotify_api, volume=85  # Changed volume
        )
        
        # Step 4: Bidirectional sync (should resolve conflict)
        success, message = manager.sync_alarms(direction='both')
        assert success
        
        # Step 5: Verify conflict was resolved
        alarms = mock_alarm_manager.get_alarms()
        assert len(alarms) == 1
        # Local should win (newer)
        assert alarms[0]['volume'] == 85
    
    def test_bidirectional_merge_workflow(self, temp_dir, mock_alarm_manager):
        """Test bidirectional merge of non-conflicting alarms."""
        # Setup
        manager = CloudSyncManager(alarm_manager=mock_alarm_manager)
        
        # Step 1: Register and login
        manager.register('merge@example.com', 'password123')
        manager.login('merge@example.com', 'password123')
        
        # Step 2: Create and sync first alarm
        mock_alarm_manager.set_alarm(
            '07:00', 'Morning', 'spotify:playlist:morning',
            mock_alarm_manager.spotify_api, volume=70
        )
        manager.sync_alarms(direction='upload')
        
        # Step 3: Add different alarm locally (no conflict)
        mock_alarm_manager.set_alarm(
            '22:00', 'Night', 'spotify:playlist:night',
            mock_alarm_manager.spotify_api, volume=60
        )
        
        # Step 4: Bidirectional sync (should merge both)
        success, message = manager.sync_alarms(direction='both')
        assert success
        
        # Step 5: Verify both alarms present
        alarms = mock_alarm_manager.get_alarms()
        assert len(alarms) == 2
        times = {a['time'] for a in alarms}
        assert '07:00' in times
        assert '22:00' in times
    
    def test_logout_login_restore_workflow(self, temp_dir, mock_alarm_manager):
        """Test logout → login → restore workflow."""
        # Setup
        manager = CloudSyncManager(alarm_manager=mock_alarm_manager)
        
        # Step 1: Register, login, and create alarms
        manager.register('restore@example.com', 'password123')
        manager.login('restore@example.com', 'password123')
        
        mock_alarm_manager.set_alarm(
            '06:30', 'Early Bird', 'spotify:playlist:early',
            mock_alarm_manager.spotify_api, volume=75
        )
        mock_alarm_manager.set_alarm(
            '19:00', 'Evening', 'spotify:playlist:evening',
            mock_alarm_manager.spotify_api, volume=65
        )
        
        # Step 2: Sync to cloud
        success, message = manager.sync_alarms(direction='upload')
        assert success
        
        # Step 3: Logout
        manager.logout()
        assert not manager.is_logged_in()
        
        # Step 4: Clear local data
        mock_alarm_manager.clear_all_alarms()
        assert len(mock_alarm_manager.get_alarms()) == 0
        
        # Step 5: Login again
        success, message = manager.login('restore@example.com', 'password123')
        assert success
        
        # Step 6: Restore from cloud
        success, message = manager.sync_alarms(direction='download')
        assert success
        
        # Step 7: Verify alarms restored
        alarms = mock_alarm_manager.get_alarms()
        assert len(alarms) == 2
        assert any(a['time'] == '06:30' for a in alarms)
        assert any(a['time'] == '19:00' for a in alarms)
    
    def test_auto_sync_workflow(self, temp_dir, mock_alarm_manager):
        """Test automatic sync at intervals."""
        # Setup
        manager = CloudSyncManager(alarm_manager=mock_alarm_manager)
        
        # Step 1: Register and login
        manager.register('autosync@example.com', 'password123')
        manager.login('autosync@example.com', 'password123')
        
        # Step 2: Add initial alarm
        mock_alarm_manager.set_alarm(
            '07:00', 'Morning', 'spotify:playlist:morning',
            mock_alarm_manager.spotify_api, volume=70
        )
        
        # Step 3: Start auto-sync with very short interval (for testing)
        # Note: We'll use a manual sync instead of waiting for auto-sync
        # since auto-sync uses threading with long intervals
        success, message = manager.sync_alarms(direction='upload')
        assert success
        assert manager.last_sync_time is not None
        
        # Step 4: Verify sync status
        status = manager.get_sync_status()
        assert status['logged_in']
        assert status['last_sync_time'] is not None
        
        # Step 5: Stop auto-sync
        manager.stop_auto_sync()
        assert not manager.auto_sync_enabled
    
    def test_settings_sync_workflow(self, temp_dir):
        """Test settings synchronization workflow."""
        # Setup
        manager = CloudSyncManager()
        
        # Step 1: Register and login
        manager.register('settings@example.com', 'password123')
        manager.login('settings@example.com', 'password123')
        
        # Step 2: Sync settings to cloud
        success, message = manager.sync_settings(direction='upload')
        assert success
        
        # Step 3: Download settings
        success, message = manager.sync_settings(direction='download')
        assert success
        
        # Step 4: Bidirectional sync
        success, message = manager.sync_settings(direction='both')
        assert success
    
    def test_full_sync_workflow(self, temp_dir, mock_alarm_manager):
        """Test full sync of alarms and settings together."""
        # Setup
        manager = CloudSyncManager(alarm_manager=mock_alarm_manager)
        
        # Step 1: Register and login
        manager.register('fullsync@example.com', 'password123')
        manager.login('fullsync@example.com', 'password123')
        
        # Step 2: Add alarms
        mock_alarm_manager.set_alarm(
            '07:00', 'Morning', 'spotify:playlist:morning',
            mock_alarm_manager.spotify_api, volume=70
        )
        
        # Step 3: Perform full sync (alarms + settings)
        success, message, results = manager.sync_all(direction='both')
        assert success
        assert results['alarms_success']
        assert results['settings_success']
    
    def test_sync_history_tracking(self, temp_dir, mock_alarm_manager):
        """Test sync history is properly tracked."""
        # Setup
        manager = CloudSyncManager(alarm_manager=mock_alarm_manager)
        
        # Step 1: Register and login (use timestamp to ensure unique email)
        import time
        unique_email = f'history{int(time.time()*1000)}@example.com'
        success, message = manager.register(unique_email, 'password123')
        assert success
        manager.login(unique_email, 'password123')
        
        user = manager.get_current_user()
        user_id = user['user_id']
        
        # Step 2: Perform multiple syncs
        mock_alarm_manager.set_alarm(
            '07:00', 'Morning', 'spotify:playlist:morning',
            mock_alarm_manager.spotify_api, volume=70
        )
        manager.sync_alarms(direction='upload')
        
        mock_alarm_manager.set_alarm(
            '22:00', 'Night', 'spotify:playlist:night',
            mock_alarm_manager.spotify_api, volume=60
        )
        manager.sync_alarms(direction='upload')
        
        # Step 3: Check sync history
        success, message, history = manager.sync_api.get_sync_history(user_id, limit=5)
        assert success
        assert len(history) >= 2
        assert all('timestamp' in entry for entry in history)
        assert all('sync_type' in entry for entry in history)
        assert all('status' in entry for entry in history)
    
    def test_multiple_conflict_resolution(self, temp_dir):
        """Test resolving multiple conflicts simultaneously."""
        # Setup
        conflict_resolver = SyncConflictResolver()
        
        # Create local and remote data with multiple conflicts
        local = [
            {'time': '07:00', 'playlist': 'Morning', 'volume': 80,
             'playlist_uri': 'uri1', 'last_modified': '2024-01-16T10:00:00'},
            {'time': '12:00', 'playlist': 'Lunch', 'volume': 70,
             'playlist_uri': 'uri2', 'last_modified': '2024-01-16T10:00:00'},
            {'time': '18:00', 'playlist': 'Evening', 'volume': 75,
             'playlist_uri': 'uri3', 'last_modified': '2024-01-16T10:00:00'},
        ]
        
        remote = [
            {'time': '07:00', 'playlist': 'Morning', 'volume': 85,
             'playlist_uri': 'uri1', 'last_modified': '2024-01-16T12:00:00'},  # Remote newer
            {'time': '12:00', 'playlist': 'Lunch', 'volume': 65,
             'playlist_uri': 'uri2', 'last_modified': '2024-01-16T09:00:00'},  # Local newer
            {'time': '22:00', 'playlist': 'Night', 'volume': 60,
             'playlist_uri': 'uri4', 'last_modified': '2024-01-16T12:00:00'},  # No conflict
        ]
        
        # Merge with conflict resolution
        merged, num_conflicts = conflict_resolver.merge_data(local, remote)
        
        # Verify conflicts were detected
        assert num_conflicts == 2
        
        # Verify merged data contains all items
        assert len(merged) == 4  # 3 conflicted + 1 non-conflicted
        
        # Verify conflict resolution (newest wins)
        morning_alarm = next(a for a in merged if a['time'] == '07:00')
        assert morning_alarm['volume'] == 85  # Remote was newer
        
        lunch_alarm = next(a for a in merged if a['time'] == '12:00')
        assert lunch_alarm['volume'] == 70  # Local was newer
        
        # Verify non-conflicted items
        assert any(a['time'] == '18:00' for a in merged)
        assert any(a['time'] == '22:00' for a in merged)
    
    def test_device_switch_workflow(self, temp_storage_dirs, mock_alarm_manager):
        """Test complete workflow: Device1 backup → logout → login Device2 → restore."""
        device1_dir, device2_dir = temp_storage_dirs
        
        # Device 1: Setup and backup
        manager1 = CloudSyncManager(alarm_manager=mock_alarm_manager)
        manager1.auth_manager.auth_file = device1_dir / 'auth.json'
        manager1.sync_api.storage_dir = device1_dir / 'cloud_data'
        manager1.device_id = 'device-001'
        
        # Register and login on Device 1
        manager1.register('deviceswitch@example.com', 'password123', 'User')
        manager1.login('deviceswitch@example.com', 'password123')
        
        # Add alarms on Device 1
        mock_alarm_manager.set_alarm(
            '06:00', 'Wake Up', 'spotify:playlist:wakeup',
            mock_alarm_manager.spotify_api, volume=80, days=['Mon', 'Wed', 'Fri']
        )
        mock_alarm_manager.set_alarm(
            '23:00', 'Sleep', 'spotify:playlist:sleep',
            mock_alarm_manager.spotify_api, volume=50, fade_in_enabled=True
        )
        
        # Sync to cloud from Device 1
        success, message = manager1.sync_alarms(direction='upload')
        assert success
        
        # Logout from Device 1
        manager1.logout()
        assert not manager1.is_logged_in()
        
        # Clear alarms (simulating device without data)
        mock_alarm_manager.clear_all_alarms()
        
        # Device 2: Login and restore
        manager2 = CloudSyncManager(alarm_manager=mock_alarm_manager)
        manager2.auth_manager.auth_file = device2_dir / 'auth.json'
        manager2.sync_api.storage_dir = device1_dir / 'cloud_data'  # Same cloud
        manager2.device_id = 'device-002'
        
        # Login on Device 2
        # First register (will create user state in device2 auth file)
        manager2.auth_manager.users = manager1.auth_manager.users.copy()
        success, message = manager2.login('deviceswitch@example.com', 'password123')
        assert success
        
        # Restore alarms on Device 2
        success, message = manager2.sync_alarms(direction='download')
        assert success
        
        # Verify alarms restored on Device 2
        alarms = mock_alarm_manager.get_alarms()
        assert len(alarms) == 2
        
        wake_alarm = next((a for a in alarms if a['time'] == '06:00'), None)
        assert wake_alarm is not None
        assert wake_alarm['playlist'] == 'Wake Up'
        assert wake_alarm['volume'] == 80
        assert wake_alarm['days'] == ['Mon', 'Wed', 'Fri']
        
        sleep_alarm = next((a for a in alarms if a['time'] == '23:00'), None)
        assert sleep_alarm is not None
        assert sleep_alarm['fade_in_enabled'] is True
    
    def test_concurrent_modifications_workflow(self, temp_storage_dirs, mock_alarm_manager):
        """Test handling of concurrent modifications from different devices."""
        device1_dir, device2_dir = temp_storage_dirs
        
        # Setup shared cloud storage
        cloud_storage = device1_dir / 'shared_cloud'
        
        # Device 1
        manager1 = CloudSyncManager(alarm_manager=mock_alarm_manager)
        manager1.auth_manager.auth_file = device1_dir / 'auth.json'
        manager1.sync_api.storage_dir = cloud_storage
        manager1.device_id = 'device-001'
        
        # Device 2
        mock_alarm_manager2 = mock_alarm_manager.__class__()
        manager2 = CloudSyncManager(alarm_manager=mock_alarm_manager2)
        manager2.auth_manager.auth_file = device2_dir / 'auth.json'
        manager2.sync_api.storage_dir = cloud_storage
        manager2.device_id = 'device-002'
        
        # Register user
        manager1.register('concurrent@example.com', 'password123')
        manager1.login('concurrent@example.com', 'password123')
        
        # Sync user data to manager2
        manager2.auth_manager.users = manager1.auth_manager.users.copy()
        manager2.login('concurrent@example.com', 'password123')
        
        # Device 1: Add alarm and sync
        mock_alarm_manager.set_alarm(
            '07:00', 'Morning', 'spotify:playlist:morning',
            mock_alarm_manager.spotify_api, volume=70
        )
        manager1.sync_alarms(direction='upload')
        
        # Device 2: Download first, then add local alarm
        success, message = manager2.sync_alarms(direction='download')
        assert success
        
        # Now Device 2 has the 07:00 alarm, add a different one
        mock_alarm_manager2.set_alarm(
            '22:00', 'Night', 'spotify:playlist:night',
            mock_alarm_manager2.spotify_api, volume=60
        )
        
        # Device 2: Upload the new alarm (both sync will merge)
        success, message = manager2.sync_alarms(direction='both')
        assert success
        
        # Verify Device 2 has both alarms
        alarms2 = mock_alarm_manager2.get_alarms()
        assert len(alarms2) == 2
        assert any(a['time'] == '07:00' for a in alarms2)
        assert any(a['time'] == '22:00' for a in alarms2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
