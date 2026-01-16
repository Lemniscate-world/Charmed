"""
test_device_wake_manager.py - Unit tests for DeviceWakeManager

Tests the device wake and reliability management functionality.
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from device_wake_manager import DeviceWakeManager


class TestDeviceWakeManager:
    """Test suite for DeviceWakeManager class."""
    
    @pytest.fixture
    def mock_spotify_api(self):
        """Create a mock Spotify API."""
        api = Mock()
        api.get_active_device.return_value = None
        api.get_devices.return_value = [
            {'id': 'device1', 'name': 'Test Device', 'type': 'Computer', 'is_active': False}
        ]
        api.transfer_playback.return_value = None
        api.set_volume.return_value = None
        api.play_playlist_by_uri.return_value = None
        return api
    
    @pytest.fixture
    def mock_gui_app(self):
        """Create a mock GUI application."""
        app = Mock()
        app.show_tray_notification = Mock()
        return app
    
    @pytest.fixture
    def wake_manager(self, mock_spotify_api, mock_gui_app):
        """Create a DeviceWakeManager instance."""
        return DeviceWakeManager(
            mock_spotify_api,
            mock_gui_app,
            pre_wake_seconds=5,
            health_check_interval=2,
            max_retry_attempts=3
        )
    
    def test_initialization(self, wake_manager):
        """Test DeviceWakeManager initialization."""
        assert wake_manager.pre_wake_seconds == 5
        assert wake_manager.health_check_interval == 2
        assert wake_manager.max_retry_attempts == 3
        assert not wake_manager._monitoring_active
        assert wake_manager._wake_timers == {}
        assert wake_manager._active_alarms == {}
    
    def test_schedule_pre_wake(self, wake_manager):
        """Test scheduling a pre-wake operation."""
        alarm_time = (datetime.now() + timedelta(seconds=10)).strftime('%H:%M')
        alarm_id = 'test_alarm_1'
        
        wake_manager.schedule_pre_wake(alarm_time, alarm_id)
        
        assert alarm_id in wake_manager._wake_timers
        assert wake_manager._wake_timers[alarm_id].is_alive()
    
    def test_cancel_pre_wake(self, wake_manager):
        """Test canceling a pre-wake operation."""
        alarm_time = (datetime.now() + timedelta(seconds=10)).strftime('%H:%M')
        alarm_id = 'test_alarm_2'
        
        wake_manager.schedule_pre_wake(alarm_time, alarm_id)
        assert alarm_id in wake_manager._wake_timers
        
        wake_manager.cancel_pre_wake(alarm_id)
        assert alarm_id not in wake_manager._wake_timers
    
    def test_wake_device_already_active(self, wake_manager, mock_spotify_api):
        """Test waking a device that is already active."""
        mock_spotify_api.get_active_device.return_value = {
            'id': 'device1', 'name': 'Active Device'
        }
        
        wake_manager._wake_device('test_alarm')
        
        mock_spotify_api.get_active_device.assert_called_once()
        mock_spotify_api.transfer_playback.assert_not_called()
    
    def test_wake_device_prefers_computer(self, wake_manager, mock_spotify_api):
        """Test that device wake prefers computer/desktop devices."""
        mock_spotify_api.get_devices.return_value = [
            {'id': 'phone1', 'name': 'Phone', 'type': 'Smartphone'},
            {'id': 'computer1', 'name': 'Computer', 'type': 'Computer'}
        ]
        
        wake_manager._wake_device('test_alarm')
        
        mock_spotify_api.transfer_playback.assert_called_once_with('computer1', force_play=False)
    
    def test_start_alarm_monitoring(self, wake_manager):
        """Test starting alarm monitoring."""
        alarm_id = 'test_alarm_3'
        
        wake_manager.start_alarm_monitoring(
            alarm_id, 'spotify:playlist:123', 'Test Playlist',
            80, wake_manager.spotify_api
        )
        
        assert alarm_id in wake_manager._active_alarms
        assert wake_manager._monitoring_active
    
    def test_stop_alarm_monitoring(self, wake_manager):
        """Test stopping alarm monitoring."""
        alarm_id = 'test_alarm_4'
        
        wake_manager.start_alarm_monitoring(
            alarm_id, 'spotify:playlist:123', 'Test Playlist',
            80, wake_manager.spotify_api
        )
        
        wake_manager.stop_alarm_monitoring(alarm_id)
        
        assert alarm_id not in wake_manager._active_alarms
    
    def test_fallback_notification(self, wake_manager, mock_gui_app):
        """Test showing fallback notification."""
        alarm_data = {
            'playlist_name': 'Test Playlist',
            'playlist_uri': 'spotify:playlist:123',
            'volume': 80,
            'spotify_api': wake_manager.spotify_api,
            'fade_in_enabled': False,
            'fade_in_duration': 10
        }
        
        wake_manager._show_fallback_notification(alarm_data)
        
        mock_gui_app.show_tray_notification.assert_called_once()
        call_args = mock_gui_app.show_tray_notification.call_args
        assert 'Alarm Notification' in call_args[0]
        assert 'Test Playlist' in call_args[0][1]
    
    def test_retry_playback(self, wake_manager, mock_spotify_api):
        """Test retrying playback when device becomes inactive."""
        alarm_id = 'test_alarm_5'
        alarm_data = {
            'playlist_uri': 'spotify:playlist:123',
            'playlist_name': 'Test Playlist',
            'volume': 80,
            'spotify_api': mock_spotify_api,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'retry_count': 0,
            'start_time': datetime.now()
        }
        
        wake_manager._active_alarms[alarm_id] = alarm_data
        wake_manager._retry_playback(alarm_id, alarm_data)
        
        mock_spotify_api.set_volume.assert_called_once_with(80)
        mock_spotify_api.play_playlist_by_uri.assert_called_once_with('spotify:playlist:123')
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 1
    
    def test_shutdown(self, wake_manager):
        """Test graceful shutdown of DeviceWakeManager."""
        alarm_time = (datetime.now() + timedelta(seconds=10)).strftime('%H:%M')
        alarm_id = 'test_alarm_6'
        
        wake_manager.schedule_pre_wake(alarm_time, alarm_id)
        wake_manager.start_alarm_monitoring(
            alarm_id, 'spotify:playlist:123', 'Test Playlist',
            80, wake_manager.spotify_api
        )
        
        wake_manager.shutdown()
        
        assert not wake_manager._monitoring_active
        assert len(wake_manager._wake_timers) == 0
        assert len(wake_manager._active_alarms) == 0
    
    def test_monitoring_duration_limit(self, wake_manager, mock_spotify_api):
        """Test that monitoring stops after duration limit."""
        alarm_id = 'test_alarm_7'
        
        # Create alarm with very short monitoring duration for testing
        alarm_data = {
            'playlist_uri': 'spotify:playlist:123',
            'playlist_name': 'Test Playlist',
            'volume': 80,
            'spotify_api': mock_spotify_api,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'retry_count': 0,
            'start_time': datetime.now() - timedelta(minutes=31),
            'monitoring_duration_minutes': 30
        }
        
        wake_manager._active_alarms[alarm_id] = alarm_data
        wake_manager._check_single_alarm(alarm_id, alarm_data)
        
        assert alarm_id not in wake_manager._active_alarms
