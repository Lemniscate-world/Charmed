"""
test_device_wake_manager.py - Unit tests for DeviceWakeManager

Tests the device wake and reliability management functionality including:
- Pre-wake timer scheduling and rescheduling
- Device health monitoring thread lifecycle
- Device retry logic and retry attempts
- Fallback notifications
"""

import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch, call
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
        """Create a DeviceWakeManager instance with short intervals for testing."""
        return DeviceWakeManager(
            mock_spotify_api,
            mock_gui_app,
            pre_wake_seconds=5,
            health_check_interval=2,
            max_retry_attempts=3
        )
    
    def test_initialization(self, wake_manager, mock_spotify_api, mock_gui_app):
        """Test DeviceWakeManager initialization with correct parameters."""
        assert wake_manager.spotify_api == mock_spotify_api
        assert wake_manager.gui_app == mock_gui_app
        assert wake_manager.pre_wake_seconds == 5
        assert wake_manager.health_check_interval == 2
        assert wake_manager.max_retry_attempts == 3
        assert not wake_manager._monitoring_active
        assert wake_manager._monitoring_thread is None
        assert wake_manager._wake_timers == {}
        assert wake_manager._active_alarms == {}
    
    def test_initialization_default_values(self, mock_spotify_api):
        """Test DeviceWakeManager initialization with default values."""
        manager = DeviceWakeManager(mock_spotify_api)
        assert manager.gui_app is None
        assert manager.pre_wake_seconds == 60
        assert manager.health_check_interval == 120
        assert manager.max_retry_attempts == 3
    
    # Schedule Pre-Wake Tests
    
    def test_schedule_pre_wake_future_time(self, wake_manager, mock_spotify_api):
        """Test scheduling a pre-wake operation for a future alarm time."""
        alarm_time = (datetime.now() + timedelta(seconds=10)).strftime('%H:%M')
        alarm_id = 'test_alarm_1'
        
        wake_manager.schedule_pre_wake(alarm_time, alarm_id)
        
        assert alarm_id in wake_manager._wake_timers
        assert wake_manager._wake_timers[alarm_id].is_alive()
        mock_spotify_api.get_active_device.assert_not_called()
    
    def test_schedule_pre_wake_past_time_schedules_tomorrow(self, wake_manager, mock_spotify_api):
        """Test that pre-wake for past time schedules for tomorrow."""
        # Alarm time that already passed today - implementation schedules for tomorrow
        alarm_time = (datetime.now() - timedelta(minutes=1)).strftime('%H:%M')
        alarm_id = 'test_alarm_past'
        
        wake_manager.schedule_pre_wake(alarm_time, alarm_id)
        
        # Timer should be scheduled (for tomorrow)
        assert alarm_id in wake_manager._wake_timers
        assert wake_manager._wake_timers[alarm_id].is_alive()
        
        # Should not wake immediately since alarm_time gets moved to tomorrow
        mock_spotify_api.get_active_device.assert_not_called()
    
    def test_schedule_pre_wake_cancels_existing_timer(self, wake_manager):
        """Test that scheduling pre-wake cancels existing timer for same alarm."""
        alarm_time = (datetime.now() + timedelta(seconds=10)).strftime('%H:%M')
        alarm_id = 'test_alarm_cancel'
        
        wake_manager.schedule_pre_wake(alarm_time, alarm_id)
        first_timer = wake_manager._wake_timers[alarm_id]
        
        wake_manager.schedule_pre_wake(alarm_time, alarm_id)
        second_timer = wake_manager._wake_timers[alarm_id]
        
        assert first_timer != second_timer
        assert not first_timer.is_alive()
        assert second_timer.is_alive()
    
    def test_schedule_pre_wake_timer_behavior(self, wake_manager, mock_spotify_api):
        """Test that pre-wake timer is created with auto-reschedule callback."""
        # Schedule for future time (next minute to ensure it's in future)
        future_time = datetime.now() + timedelta(minutes=1)
        alarm_time = future_time.strftime('%H:%M')
        alarm_id = 'test_alarm_timer'
        
        wake_manager.schedule_pre_wake(alarm_time, alarm_id)
        
        # Timer should be scheduled
        assert alarm_id in wake_manager._wake_timers
        timer = wake_manager._wake_timers[alarm_id]
        assert timer.is_alive()
        # Timer should be a daemon thread
        assert timer.daemon
        
        # Cleanup
        wake_manager.cancel_pre_wake(alarm_id)
    
    def test_cancel_pre_wake(self, wake_manager):
        """Test canceling a pre-wake operation."""
        alarm_time = (datetime.now() + timedelta(seconds=10)).strftime('%H:%M')
        alarm_id = 'test_alarm_cancel_explicit'
        
        wake_manager.schedule_pre_wake(alarm_time, alarm_id)
        assert alarm_id in wake_manager._wake_timers
        timer = wake_manager._wake_timers[alarm_id]
        
        wake_manager.cancel_pre_wake(alarm_id)
        
        assert alarm_id not in wake_manager._wake_timers
        assert not timer.is_alive()
    
    def test_cancel_pre_wake_nonexistent(self, wake_manager):
        """Test canceling a pre-wake for nonexistent alarm does not error."""
        wake_manager.cancel_pre_wake('nonexistent_alarm')
        # Should not raise exception
    
    # Wake Device Tests
    
    def test_wake_device_already_active(self, wake_manager, mock_spotify_api):
        """Test waking a device that is already active does nothing."""
        mock_spotify_api.get_active_device.return_value = {
            'id': 'device1', 'name': 'Active Device'
        }
        
        wake_manager._wake_device('test_alarm')
        
        mock_spotify_api.get_active_device.assert_called_once()
        mock_spotify_api.get_devices.assert_not_called()
        mock_spotify_api.transfer_playback.assert_not_called()
    
    def test_wake_device_prefers_computer_type(self, wake_manager, mock_spotify_api):
        """Test that device wake prefers computer/desktop devices."""
        mock_spotify_api.get_devices.return_value = [
            {'id': 'phone1', 'name': 'Phone', 'type': 'Smartphone'},
            {'id': 'tablet1', 'name': 'Tablet', 'type': 'Tablet'},
            {'id': 'computer1', 'name': 'Computer', 'type': 'Computer'}
        ]
        
        wake_manager._wake_device('test_alarm')
        
        mock_spotify_api.transfer_playback.assert_called_once_with('computer1', force_play=False)
    
    def test_wake_device_prefers_desktop_type(self, wake_manager, mock_spotify_api):
        """Test that device wake prefers desktop type devices."""
        mock_spotify_api.get_devices.return_value = [
            {'id': 'phone1', 'name': 'Phone', 'type': 'Smartphone'},
            {'id': 'desktop1', 'name': 'Desktop', 'type': 'Desktop'}
        ]
        
        wake_manager._wake_device('test_alarm')
        
        mock_spotify_api.transfer_playback.assert_called_once_with('desktop1', force_play=False)
    
    def test_wake_device_fallback_to_first_device(self, wake_manager, mock_spotify_api):
        """Test that device wake falls back to first available device."""
        mock_spotify_api.get_devices.return_value = [
            {'id': 'phone1', 'name': 'Phone', 'type': 'Smartphone'},
            {'id': 'tablet1', 'name': 'Tablet', 'type': 'Tablet'}
        ]
        
        wake_manager._wake_device('test_alarm')
        
        mock_spotify_api.transfer_playback.assert_called_once_with('phone1', force_play=False)
    
    def test_wake_device_no_devices_available(self, wake_manager, mock_spotify_api):
        """Test waking device when no devices are available."""
        mock_spotify_api.get_devices.return_value = []
        
        wake_manager._wake_device('test_alarm')
        
        mock_spotify_api.transfer_playback.assert_not_called()
    
    def test_wake_device_handles_api_exception(self, wake_manager, mock_spotify_api):
        """Test that device wake handles API exceptions gracefully."""
        mock_spotify_api.get_active_device.side_effect = Exception('API Error')
        
        # Should not raise exception
        wake_manager._wake_device('test_alarm')
    
    # Start Health Monitoring Tests
    
    def test_start_health_monitoring_creates_thread(self, wake_manager, mock_spotify_api):
        """Test that start_health_monitoring creates monitoring thread."""
        assert not wake_manager._monitoring_active
        assert wake_manager._monitoring_thread is None
        
        # Add an active alarm so the thread doesn't immediately exit
        wake_manager.start_alarm_monitoring(
            'test_alarm', 'spotify:playlist:123', 'Test Playlist',
            80, mock_spotify_api
        )
        
        assert wake_manager._monitoring_active
        assert wake_manager._monitoring_thread is not None
        assert wake_manager._monitoring_thread.is_alive()
        assert wake_manager._monitoring_thread.daemon
        
        # Cleanup
        wake_manager.shutdown()
    
    def test_start_health_monitoring_does_not_create_duplicate_thread(self, wake_manager, mock_spotify_api):
        """Test that starting monitoring twice does not create duplicate threads."""
        # Add an active alarm so the thread doesn't immediately exit
        wake_manager.start_alarm_monitoring(
            'test_alarm', 'spotify:playlist:123', 'Test Playlist',
            80, mock_spotify_api
        )
        first_thread = wake_manager._monitoring_thread
        
        wake_manager._start_health_monitoring()
        second_thread = wake_manager._monitoring_thread
        
        assert first_thread == second_thread
        
        # Cleanup
        wake_manager.shutdown()
    
    def test_health_monitoring_thread_stops_when_no_active_alarms(self, wake_manager):
        """Test that health monitoring thread stops when no active alarms."""
        # Start monitoring without active alarms - thread should exit immediately
        wake_manager._start_health_monitoring()
        
        # Give the thread a moment to check and exit
        time.sleep(0.5)
        
        # Thread should have stopped due to no active alarms
        assert not wake_manager._monitoring_active
    
    # Start/Stop Alarm Monitoring Tests
    
    def test_start_alarm_monitoring(self, wake_manager, mock_spotify_api):
        """Test starting alarm monitoring adds alarm to active alarms."""
        alarm_id = 'test_alarm_monitor'
        playlist_uri = 'spotify:playlist:123'
        playlist_name = 'Test Playlist'
        volume = 80
        
        wake_manager.start_alarm_monitoring(
            alarm_id, playlist_uri, playlist_name,
            volume, mock_spotify_api, fade_in_enabled=False,
            fade_in_duration=10, monitoring_duration_minutes=30
        )
        
        assert alarm_id in wake_manager._active_alarms
        alarm_data = wake_manager._active_alarms[alarm_id]
        assert alarm_data['playlist_uri'] == playlist_uri
        assert alarm_data['playlist_name'] == playlist_name
        assert alarm_data['volume'] == volume
        assert alarm_data['spotify_api'] == mock_spotify_api
        assert alarm_data['fade_in_enabled'] == False
        assert alarm_data['fade_in_duration'] == 10
        assert alarm_data['retry_count'] == 0
        assert alarm_data['monitoring_duration_minutes'] == 30
        assert 'start_time' in alarm_data
        assert wake_manager._monitoring_active
        
        # Cleanup
        wake_manager.shutdown()
    
    def test_start_alarm_monitoring_with_fade_in(self, wake_manager, mock_spotify_api):
        """Test starting alarm monitoring with fade-in enabled."""
        alarm_id = 'test_alarm_fade'
        
        wake_manager.start_alarm_monitoring(
            alarm_id, 'spotify:playlist:123', 'Test Playlist',
            80, mock_spotify_api, fade_in_enabled=True, fade_in_duration=15
        )
        
        alarm_data = wake_manager._active_alarms[alarm_id]
        assert alarm_data['fade_in_enabled'] == True
        assert alarm_data['fade_in_duration'] == 15
        
        # Cleanup
        wake_manager.shutdown()
    
    def test_stop_alarm_monitoring(self, wake_manager, mock_spotify_api):
        """Test stopping alarm monitoring removes alarm from active alarms."""
        alarm_id = 'test_alarm_stop'
        
        wake_manager.start_alarm_monitoring(
            alarm_id, 'spotify:playlist:123', 'Test Playlist',
            80, mock_spotify_api
        )
        assert alarm_id in wake_manager._active_alarms
        
        wake_manager.stop_alarm_monitoring(alarm_id)
        
        assert alarm_id not in wake_manager._active_alarms
        
        # Cleanup
        wake_manager.shutdown()
    
    def test_stop_alarm_monitoring_nonexistent(self, wake_manager):
        """Test stopping monitoring for nonexistent alarm does not error."""
        wake_manager.stop_alarm_monitoring('nonexistent_alarm')
        # Should not raise exception
    
    # Device Retry Logic Tests
    
    def test_retry_playback_without_fade_in(self, wake_manager, mock_spotify_api):
        """Test retrying playback when device becomes inactive (no fade-in)."""
        alarm_id = 'test_alarm_retry'
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
        
        # Should wake device first
        mock_spotify_api.get_active_device.assert_called()
        # Should set volume to target volume
        mock_spotify_api.set_volume.assert_called_once_with(80)
        # Should start playback
        mock_spotify_api.play_playlist_by_uri.assert_called_once_with('spotify:playlist:123')
        # Should increment retry count
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 1
    
    def test_retry_playback_with_fade_in(self, wake_manager, mock_spotify_api):
        """Test retrying playback with fade-in enabled."""
        alarm_id = 'test_alarm_retry_fade'
        alarm_data = {
            'playlist_uri': 'spotify:playlist:123',
            'playlist_name': 'Test Playlist',
            'volume': 80,
            'spotify_api': mock_spotify_api,
            'fade_in_enabled': True,
            'fade_in_duration': 10,
            'retry_count': 0,
            'start_time': datetime.now()
        }
        
        wake_manager._active_alarms[alarm_id] = alarm_data
        wake_manager._retry_playback(alarm_id, alarm_data)
        
        # Should set volume to 0 for fade-in
        mock_spotify_api.set_volume.assert_called_once_with(0)
        mock_spotify_api.play_playlist_by_uri.assert_called_once_with('spotify:playlist:123')
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 1
    
    def test_retry_playback_increments_count_on_failure(self, wake_manager, mock_spotify_api):
        """Test that retry count increments even when playback fails."""
        alarm_id = 'test_alarm_retry_fail'
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
        
        mock_spotify_api.play_playlist_by_uri.side_effect = Exception('Playback Error')
        
        wake_manager._active_alarms[alarm_id] = alarm_data
        wake_manager._retry_playback(alarm_id, alarm_data)
        
        # Should still increment retry count
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 1
    
    def test_multiple_retry_attempts(self, wake_manager, mock_spotify_api):
        """Test multiple retry attempts increment count correctly."""
        alarm_id = 'test_alarm_multi_retry'
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
        
        # First retry
        wake_manager._retry_playback(alarm_id, alarm_data)
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 1
        
        # Second retry
        wake_manager._retry_playback(alarm_id, alarm_data)
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 2
        
        # Third retry
        wake_manager._retry_playback(alarm_id, alarm_data)
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 3
    
    # Health Check Tests
    
    def test_check_single_alarm_device_active_continues_monitoring(self, wake_manager, mock_spotify_api):
        """Test that health check continues monitoring when device is active."""
        mock_spotify_api.get_active_device.return_value = {
            'id': 'device1', 'name': 'Active Device'
        }
        
        alarm_id = 'test_alarm_active'
        alarm_data = {
            'playlist_uri': 'spotify:playlist:123',
            'playlist_name': 'Test Playlist',
            'volume': 80,
            'spotify_api': mock_spotify_api,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'retry_count': 0,
            'start_time': datetime.now(),
            'monitoring_duration_minutes': 30
        }
        
        wake_manager._active_alarms[alarm_id] = alarm_data
        wake_manager._check_single_alarm(alarm_id, alarm_data)
        
        # Should check device status
        mock_spotify_api.get_active_device.assert_called()
        # Should not retry playback
        mock_spotify_api.play_playlist_by_uri.assert_not_called()
        # Should still be in active alarms
        assert alarm_id in wake_manager._active_alarms
    
    def test_check_single_alarm_device_inactive_retries(self, wake_manager, mock_spotify_api):
        """Test that health check retries playback when device is inactive."""
        mock_spotify_api.get_active_device.return_value = None
        
        alarm_id = 'test_alarm_inactive'
        alarm_data = {
            'playlist_uri': 'spotify:playlist:123',
            'playlist_name': 'Test Playlist',
            'volume': 80,
            'spotify_api': mock_spotify_api,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'retry_count': 0,
            'start_time': datetime.now(),
            'monitoring_duration_minutes': 30
        }
        
        wake_manager._active_alarms[alarm_id] = alarm_data
        wake_manager._check_single_alarm(alarm_id, alarm_data)
        
        # Should retry playback
        mock_spotify_api.play_playlist_by_uri.assert_called_once()
        # Should increment retry count
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 1
    
    def test_check_single_alarm_max_retries_shows_notification(self, wake_manager, mock_spotify_api, mock_gui_app):
        """Test that max retries triggers fallback notification."""
        mock_spotify_api.get_active_device.return_value = None
        
        alarm_id = 'test_alarm_max_retry'
        alarm_data = {
            'playlist_uri': 'spotify:playlist:123',
            'playlist_name': 'Test Playlist',
            'volume': 80,
            'spotify_api': mock_spotify_api,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'retry_count': 3,  # Already at max
            'start_time': datetime.now(),
            'monitoring_duration_minutes': 30
        }
        
        wake_manager._active_alarms[alarm_id] = alarm_data
        wake_manager._check_single_alarm(alarm_id, alarm_data)
        
        # Should show fallback notification
        mock_gui_app.show_tray_notification.assert_called_once()
        # Should stop monitoring this alarm
        assert alarm_id not in wake_manager._active_alarms
    
    def test_check_single_alarm_exceeds_duration_stops_monitoring(self, wake_manager, mock_spotify_api):
        """Test that monitoring stops after duration limit."""
        alarm_id = 'test_alarm_duration'
        alarm_data = {
            'playlist_uri': 'spotify:playlist:123',
            'playlist_name': 'Test Playlist',
            'volume': 80,
            'spotify_api': mock_spotify_api,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'retry_count': 0,
            'start_time': datetime.now() - timedelta(minutes=31),  # Started 31 minutes ago
            'monitoring_duration_minutes': 30
        }
        
        wake_manager._active_alarms[alarm_id] = alarm_data
        wake_manager._check_single_alarm(alarm_id, alarm_data)
        
        # Should stop monitoring
        assert alarm_id not in wake_manager._active_alarms
    
    def test_check_single_alarm_handles_api_exception(self, wake_manager, mock_spotify_api):
        """Test that health check handles API exceptions gracefully."""
        mock_spotify_api.get_active_device.side_effect = Exception('API Error')
        
        alarm_id = 'test_alarm_exception'
        alarm_data = {
            'playlist_uri': 'spotify:playlist:123',
            'playlist_name': 'Test Playlist',
            'volume': 80,
            'spotify_api': mock_spotify_api,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'retry_count': 0,
            'start_time': datetime.now(),
            'monitoring_duration_minutes': 30
        }
        
        wake_manager._active_alarms[alarm_id] = alarm_data
        
        # Should not raise exception
        wake_manager._check_single_alarm(alarm_id, alarm_data)
    
    # Fallback Notification Tests
    
    def test_fallback_notification_calls_gui(self, wake_manager, mock_gui_app):
        """Test that fallback notification calls GUI app with correct parameters."""
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
        call_args = mock_gui_app.show_tray_notification.call_args[0]
        assert call_args[0] == 'Alarm Notification'
        assert 'Test Playlist' in call_args[1]
        assert 'Unable to play' in call_args[1]
        assert 'Device became inactive' in call_args[1]
    
    def test_fallback_notification_without_gui(self, mock_spotify_api):
        """Test that fallback notification handles missing GUI gracefully."""
        manager = DeviceWakeManager(mock_spotify_api, gui_app=None)
        
        alarm_data = {
            'playlist_name': 'Test Playlist',
            'playlist_uri': 'spotify:playlist:123',
            'volume': 80,
            'spotify_api': mock_spotify_api,
            'fade_in_enabled': False,
            'fade_in_duration': 10
        }
        
        # Should not raise exception
        manager._show_fallback_notification(alarm_data)
    
    def test_fallback_notification_handles_gui_exception(self, wake_manager, mock_gui_app):
        """Test that fallback notification handles GUI exceptions gracefully."""
        mock_gui_app.show_tray_notification.side_effect = Exception('GUI Error')
        
        alarm_data = {
            'playlist_name': 'Test Playlist',
            'playlist_uri': 'spotify:playlist:123',
            'volume': 80,
            'spotify_api': wake_manager.spotify_api,
            'fade_in_enabled': False,
            'fade_in_duration': 10
        }
        
        # Should not raise exception
        wake_manager._show_fallback_notification(alarm_data)
    
    # Shutdown Tests
    
    def test_shutdown_stops_monitoring(self, wake_manager, mock_spotify_api):
        """Test that shutdown stops monitoring thread."""
        # Add an active alarm so the thread doesn't immediately exit
        wake_manager.start_alarm_monitoring(
            'test_alarm', 'spotify:playlist:123', 'Test Playlist',
            80, mock_spotify_api
        )
        assert wake_manager._monitoring_active
        
        wake_manager.shutdown()
        
        assert not wake_manager._monitoring_active
    
    def test_shutdown_waits_for_thread(self, wake_manager):
        """Test that shutdown waits for monitoring thread to stop."""
        wake_manager._start_health_monitoring()
        thread = wake_manager._monitoring_thread
        
        wake_manager.shutdown()
        
        # Thread should have stopped
        assert not thread.is_alive()
    
    def test_shutdown_cancels_all_timers(self, wake_manager):
        """Test that shutdown cancels all pre-wake timers."""
        alarm_time = (datetime.now() + timedelta(seconds=10)).strftime('%H:%M')
        
        wake_manager.schedule_pre_wake(alarm_time, 'alarm1')
        wake_manager.schedule_pre_wake(alarm_time, 'alarm2')
        wake_manager.schedule_pre_wake(alarm_time, 'alarm3')
        
        assert len(wake_manager._wake_timers) == 3
        
        wake_manager.shutdown()
        
        assert len(wake_manager._wake_timers) == 0
    
    def test_shutdown_clears_active_alarms(self, wake_manager, mock_spotify_api):
        """Test that shutdown clears all active alarms."""
        wake_manager.start_alarm_monitoring(
            'alarm1', 'spotify:playlist:123', 'Playlist 1',
            80, mock_spotify_api
        )
        wake_manager.start_alarm_monitoring(
            'alarm2', 'spotify:playlist:456', 'Playlist 2',
            70, mock_spotify_api
        )
        
        assert len(wake_manager._active_alarms) == 2
        
        wake_manager.shutdown()
        
        assert len(wake_manager._active_alarms) == 0
    
    def test_shutdown_idempotent(self, wake_manager):
        """Test that shutdown can be called multiple times safely."""
        wake_manager._start_health_monitoring()
        
        wake_manager.shutdown()
        wake_manager.shutdown()  # Should not error
        
        assert not wake_manager._monitoring_active
    
    # Integration Tests
    
    def test_full_monitoring_lifecycle(self, wake_manager, mock_spotify_api, mock_gui_app):
        """Test complete monitoring lifecycle from start to max retries."""
        mock_spotify_api.get_active_device.return_value = None
        
        alarm_id = 'test_alarm_full'
        
        # Create alarm data manually to avoid automatic monitoring thread
        alarm_data = {
            'playlist_uri': 'spotify:playlist:123',
            'playlist_name': 'Test Playlist',
            'volume': 80,
            'spotify_api': mock_spotify_api,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'retry_count': 0,
            'start_time': datetime.now(),
            'monitoring_duration_minutes': 30
        }
        
        wake_manager._active_alarms[alarm_id] = alarm_data
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 0
        
        # Simulate first health check - device inactive, should retry
        wake_manager._check_single_alarm(alarm_id, wake_manager._active_alarms[alarm_id])
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 1
        
        # Simulate second health check
        wake_manager._check_single_alarm(alarm_id, wake_manager._active_alarms[alarm_id])
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 2
        
        # Simulate third health check
        wake_manager._check_single_alarm(alarm_id, wake_manager._active_alarms[alarm_id])
        assert wake_manager._active_alarms[alarm_id]['retry_count'] == 3
        
        # Simulate fourth health check - max retries, should show notification
        wake_manager._check_single_alarm(alarm_id, wake_manager._active_alarms[alarm_id])
        assert alarm_id not in wake_manager._active_alarms
        mock_gui_app.show_tray_notification.assert_called_once()
    
    def test_concurrent_alarms_monitoring(self, wake_manager, mock_spotify_api):
        """Test monitoring multiple alarms concurrently."""
        mock_spotify_api.get_active_device.return_value = {
            'id': 'device1', 'name': 'Active Device'
        }
        
        wake_manager.start_alarm_monitoring(
            'alarm1', 'spotify:playlist:123', 'Playlist 1',
            80, mock_spotify_api
        )
        wake_manager.start_alarm_monitoring(
            'alarm2', 'spotify:playlist:456', 'Playlist 2',
            70, mock_spotify_api
        )
        wake_manager.start_alarm_monitoring(
            'alarm3', 'spotify:playlist:789', 'Playlist 3',
            90, mock_spotify_api
        )
        
        assert len(wake_manager._active_alarms) == 3
        assert wake_manager._monitoring_active
        
        # Check all alarms
        wake_manager._check_alarm_health()
        
        # All should still be active (device is active)
        assert len(wake_manager._active_alarms) == 3
        
        # Cleanup
        wake_manager.shutdown()
    
    def test_timer_thread_safety(self, wake_manager):
        """Test that timer operations are thread-safe."""
        alarm_time = (datetime.now() + timedelta(seconds=5)).strftime('%H:%M')
        
        def schedule_and_cancel():
            for i in range(10):
                wake_manager.schedule_pre_wake(alarm_time, f'alarm_{i}')
                wake_manager.cancel_pre_wake(f'alarm_{i}')
        
        # Run multiple threads
        threads = [threading.Thread(target=schedule_and_cancel) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should complete without errors
        wake_manager.shutdown()
    
    def test_active_alarms_thread_safety(self, wake_manager, mock_spotify_api):
        """Test that active alarms operations are thread-safe."""
        mock_spotify_api.get_active_device.return_value = {
            'id': 'device1', 'name': 'Active Device'
        }
        
        def start_and_stop():
            for i in range(10):
                alarm_id = f'alarm_{threading.current_thread().name}_{i}'
                wake_manager.start_alarm_monitoring(
                    alarm_id, 'spotify:playlist:123', 'Test Playlist',
                    80, mock_spotify_api
                )
                wake_manager.stop_alarm_monitoring(alarm_id)
        
        # Run multiple threads
        threads = [threading.Thread(target=start_and_stop) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should complete without errors
        wake_manager.shutdown()
