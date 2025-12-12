"""
test_alarm.py - Unit tests for the Alarm class

Tests cover:
- Alarm creation and scheduling
- Alarm listing (get_alarms)
- Alarm removal (remove_alarm)
- Alarm clearing (clear_all_alarms)
- Volume parameter handling

Run with: python -m pytest tests/test_alarm.py -v
"""

import pytest  # Test framework
import time    # For timing tests
from unittest.mock import Mock, patch  # Mocking utilities

# Import the module under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from alarm import Alarm


class TestAlarmInit:
    """Tests for Alarm initialization."""
    
    def test_alarm_init_empty_list(self):
        """Alarm should initialize with empty alarm list."""
        alarm = Alarm()
        # Verify alarms list is empty
        assert alarm.alarms == []
        # Verify scheduler is not running yet
        assert alarm.scheduler_running is False
    
    def test_alarm_init_no_thread(self):
        """Alarm should not start scheduler thread on init."""
        alarm = Alarm()
        # Scheduler thread should be None until first alarm is set
        assert alarm.scheduler_thread is None


class TestSetAlarm:
    """Tests for set_alarm method."""
    
    def test_set_alarm_adds_to_list(self):
        """Setting an alarm should add it to the alarms list."""
        alarm = Alarm()
        mock_api = Mock()  # Mock SpotifyAPI
        
        # Set an alarm
        alarm.set_alarm('08:00', 'Morning Playlist', 'spotify:playlist:abc123', mock_api, 75)
        
        # Verify alarm was added
        assert len(alarm.alarms) == 1
        assert alarm.alarms[0]['time'] == '08:00'
        assert alarm.alarms[0]['playlist'] == 'Morning Playlist'
        assert alarm.alarms[0]['playlist_uri'] == 'spotify:playlist:abc123'
        assert alarm.alarms[0]['volume'] == 75
    
    def test_set_alarm_default_volume(self):
        """Default volume should be 80 if not specified."""
        alarm = Alarm()
        mock_api = Mock()
        
        # Set alarm without volume parameter
        alarm.set_alarm('09:00', 'Test Playlist', 'spotify:playlist:xyz789', mock_api)
        
        # Verify default volume
        assert alarm.alarms[0]['volume'] == 80
    
    def test_set_alarm_starts_scheduler(self):
        """Setting first alarm should start scheduler thread."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('10:00', 'Test', 'spotify:playlist:test123', mock_api)
        
        # Verify scheduler is now running
        assert alarm.scheduler_running is True
        assert alarm.scheduler_thread is not None
        assert alarm.scheduler_thread.is_alive()
    
    def test_set_multiple_alarms(self):
        """Should be able to set multiple alarms."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('06:00', 'Playlist A', 'spotify:playlist:aaa111', mock_api, 50)
        alarm.set_alarm('07:00', 'Playlist B', 'spotify:playlist:bbb222', mock_api, 60)
        alarm.set_alarm('08:00', 'Playlist C', 'spotify:playlist:ccc333', mock_api, 70)
        
        # Verify all alarms were added
        assert len(alarm.alarms) == 3


class TestGetAlarms:
    """Tests for get_alarms method."""
    
    def test_get_alarms_empty(self):
        """get_alarms should return empty list when no alarms set."""
        alarm = Alarm()
        result = alarm.get_alarms()
        assert result == []
    
    def test_get_alarms_returns_copy(self):
        """get_alarms should return alarm info without internal 'job' key."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('11:00', 'Test', 'spotify:playlist:test456', mock_api, 85)
        result = alarm.get_alarms()
        
        # Should have time, playlist, playlist_uri, volume but NOT job
        assert len(result) == 1
        assert 'time' in result[0]
        assert 'playlist' in result[0]
        assert 'playlist_uri' in result[0]
        assert 'volume' in result[0]
        assert 'job' not in result[0]


class TestRemoveAlarm:
    """Tests for remove_alarm method."""
    
    def test_remove_alarm_by_time(self):
        """remove_alarm should remove alarm matching the time."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('12:00', 'Playlist 1', 'spotify:playlist:p1', mock_api)
        alarm.set_alarm('13:00', 'Playlist 2', 'spotify:playlist:p2', mock_api)
        
        # Remove first alarm
        alarm.remove_alarm('12:00')
        
        # Verify only second remains
        assert len(alarm.alarms) == 1
        assert alarm.alarms[0]['time'] == '13:00'
    
    def test_remove_nonexistent_alarm(self):
        """Removing nonexistent alarm should not raise error."""
        alarm = Alarm()
        # Should not raise exception
        alarm.remove_alarm('99:99')


class TestClearAllAlarms:
    """Tests for clear_all_alarms method."""
    
    def test_clear_all_alarms(self):
        """clear_all_alarms should remove all alarms."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('14:00', 'A', 'spotify:playlist:a', mock_api)
        alarm.set_alarm('15:00', 'B', 'spotify:playlist:b', mock_api)
        alarm.set_alarm('16:00', 'C', 'spotify:playlist:c', mock_api)
        
        alarm.clear_all_alarms()
        
        assert len(alarm.alarms) == 0


class TestPlayPlaylist:
    """Tests for play_playlist method."""
    
    def test_play_playlist_sets_volume(self):
        """play_playlist should call set_volume on the API."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.play_playlist('spotify:playlist:test123', mock_api, 65)
        
        mock_api.set_volume.assert_called_once_with(65)
    
    def test_play_playlist_calls_api(self):
        """play_playlist should call play_playlist_by_uri on the API."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.play_playlist('spotify:playlist:my123', mock_api, 80)
        
        mock_api.play_playlist_by_uri.assert_called_once_with('spotify:playlist:my123')
    
    def test_play_playlist_handles_volume_error(self):
        """play_playlist should continue if set_volume fails."""
        alarm = Alarm()
        mock_api = Mock()
        mock_api.set_volume.side_effect = Exception("No active device")
        
        # Should not raise exception
        alarm.play_playlist('spotify:playlist:test456', mock_api, 80)
        
        # play_playlist_by_uri should still be called
        mock_api.play_playlist_by_uri.assert_called_once()

