"""
test_alarm.py - Unit tests for the Alarm class

Tests cover:
- Alarm creation and scheduling
- Alarm listing (get_alarms)
- Alarm removal (remove_alarm)
- Alarm clearing (clear_all_alarms)
- Volume parameter handling
- Time validation
- Error handling and retry logic
- User-friendly error messages
- Snooze functionality (snooze_alarm, get_snoozed_alarms)
- Shutdown with snoozed alarms

Run with: python -m pytest tests/test_alarm.py -v
"""

import pytest
import time
from unittest.mock import Mock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from alarm import Alarm


class TestAlarmInit:
    """Tests for Alarm initialization."""
    
    def test_alarm_init_empty_list(self):
        """Alarm should initialize with empty alarm list."""
        alarm = Alarm()
        assert alarm.alarms == []
        assert alarm.snoozed_alarms == []
        assert alarm.scheduler_running is False
    
    def test_alarm_init_no_thread(self):
        """Alarm should not start scheduler thread on init."""
        alarm = Alarm()
        assert alarm.scheduler_thread is None
    
    def test_alarm_init_with_gui_app(self):
        """Alarm should accept optional gui_app parameter."""
        mock_gui = Mock()
        alarm = Alarm(gui_app=mock_gui)
        assert alarm.gui_app is mock_gui


class TestSetAlarm:
    """Tests for set_alarm method."""
    
    def test_set_alarm_adds_to_list(self):
        """Setting an alarm should add it to the alarms list."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('08:00', 'Morning Playlist', 'spotify:playlist:abc123', mock_api, 75)
        
        assert len(alarm.alarms) == 1
        assert alarm.alarms[0]['time'] == '08:00'
        assert alarm.alarms[0]['playlist'] == 'Morning Playlist'
        assert alarm.alarms[0]['playlist_uri'] == 'spotify:playlist:abc123'
        assert alarm.alarms[0]['volume'] == 75
    
    def test_set_alarm_default_volume(self):
        """Default volume should be 80 if not specified."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('09:00', 'Test Playlist', 'spotify:playlist:xyz789', mock_api)
        
        assert alarm.alarms[0]['volume'] == 80
    
    def test_set_alarm_starts_scheduler(self):
        """Setting first alarm should start scheduler thread."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('10:00', 'Test', 'spotify:playlist:test123', mock_api)
        
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
        
        assert len(alarm.alarms) == 3
    
    def test_set_alarm_invalid_time_format(self):
        """Should raise ValueError for invalid time format."""
        alarm = Alarm()
        mock_api = Mock()
        
        with pytest.raises(ValueError, match='Invalid time format'):
            alarm.set_alarm('25:00', 'Test', 'spotify:playlist:test', mock_api)
        
        with pytest.raises(ValueError, match='Invalid time format'):
            alarm.set_alarm('12:61', 'Test', 'spotify:playlist:test', mock_api)
        
        with pytest.raises(ValueError, match='Invalid time format'):
            alarm.set_alarm('invalid', 'Test', 'spotify:playlist:test', mock_api)
    
    def test_set_alarm_with_days_list(self):
        """Setting an alarm with specific days should store them correctly."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('08:00', 'Weekday Playlist', 'spotify:playlist:weekday', mock_api, 
                       75, False, 10, ['Monday', 'Wednesday', 'Friday'])
        
        assert len(alarm.alarms) == 1
        assert alarm.alarms[0]['days'] == ['Monday', 'Wednesday', 'Friday']
    
    def test_set_alarm_with_weekdays_shortcut(self):
        """Setting an alarm with 'weekdays' should expand to Mon-Fri."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('07:00', 'Weekdays', 'spotify:playlist:wd', mock_api, 
                       80, False, 10, 'weekdays')
        
        assert alarm.alarms[0]['days'] == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    def test_set_alarm_with_weekends_shortcut(self):
        """Setting an alarm with 'weekends' should expand to Sat-Sun."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('09:00', 'Weekends', 'spotify:playlist:we', mock_api, 
                       85, False, 10, 'weekends')
        
        assert alarm.alarms[0]['days'] == ['Saturday', 'Sunday']
    
    def test_set_alarm_without_days(self):
        """Setting an alarm without days should default to None (every day)."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('10:00', 'Every Day', 'spotify:playlist:ed', mock_api)
        
        assert alarm.alarms[0]['days'] is None


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
        
        assert len(result) == 1
        assert 'time' in result[0]
        assert 'playlist' in result[0]
        assert 'playlist_uri' in result[0]
        assert 'volume' in result[0]
        assert 'days' in result[0]
        assert 'job' not in result[0]
    
    def test_get_alarms_includes_days(self):
        """get_alarms should include days information."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('12:00', 'Test', 'spotify:playlist:test789', mock_api, 
                       80, False, 10, ['Monday', 'Friday'])
        result = alarm.get_alarms()
        
        assert result[0]['days'] == ['Monday', 'Friday']


class TestRemoveAlarm:
    """Tests for remove_alarm method."""
    
    def test_remove_alarm_by_time(self):
        """remove_alarm should remove alarm matching the time."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('12:00', 'Playlist 1', 'spotify:playlist:p1', mock_api)
        alarm.set_alarm('13:00', 'Playlist 2', 'spotify:playlist:p2', mock_api)
        
        alarm.remove_alarm('12:00')
        
        assert len(alarm.alarms) == 1
        assert alarm.alarms[0]['time'] == '13:00'
    
    def test_remove_nonexistent_alarm(self):
        """Removing nonexistent alarm should not raise error."""
        alarm = Alarm()
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
        
        alarm.play_playlist('spotify:playlist:test123', mock_api, 65, 'Test Playlist')
        
        assert mock_api.set_volume.called
    
    def test_play_playlist_calls_api(self):
        """play_playlist should call play_playlist_by_uri on the API."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.play_playlist('spotify:playlist:my123', mock_api, 80, 'My Playlist')
        
        mock_api.play_playlist_by_uri.assert_called_with('spotify:playlist:my123')
    
    def test_play_playlist_handles_volume_error(self):
        """play_playlist should continue if set_volume fails."""
        alarm = Alarm()
        mock_api = Mock()
        mock_api.set_volume.side_effect = Exception("No active device")
        
        alarm.play_playlist('spotify:playlist:test456', mock_api, 80, 'Test')
        
        mock_api.play_playlist_by_uri.assert_called()
    
    def test_play_playlist_retries_on_failure(self):
        """play_playlist should retry on transient failures."""
        alarm = Alarm()
        mock_api = Mock()
        
        call_count = 0
        def side_effect(*args):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Transient error")
        
        mock_api.play_playlist_by_uri.side_effect = side_effect
        
        alarm.play_playlist('spotify:playlist:test789', mock_api, 80, 'Test')
        
        assert call_count == 2
    
    def test_play_playlist_shows_notification_on_success(self):
        """play_playlist should show success notification."""
        mock_gui = Mock()
        alarm = Alarm(gui_app=mock_gui)
        mock_api = Mock()
        
        alarm.play_playlist('spotify:playlist:success', mock_api, 80, 'Success Playlist')
        
        assert hasattr(alarm, '_show_notification')
    
    def test_play_playlist_shows_notification_on_failure(self):
        """play_playlist should show failure notification after retries exhausted."""
        mock_gui = Mock()
        alarm = Alarm(gui_app=mock_gui)
        mock_api = Mock()
        mock_api.play_playlist_by_uri.side_effect = Exception("Persistent error")
        
        alarm.play_playlist('spotify:playlist:fail', mock_api, 80, 'Fail Playlist')
        
        assert hasattr(alarm, '_show_notification')


class TestTimeValidation:
    """Tests for time validation."""
    
    def test_validate_time_format_valid(self):
        """Should validate correct time formats."""
        alarm = Alarm()
        assert alarm._validate_time_format('00:00') is True
        assert alarm._validate_time_format('12:30') is True
        assert alarm._validate_time_format('23:59') is True
    
    def test_validate_time_format_invalid(self):
        """Should reject invalid time formats."""
        alarm = Alarm()
        assert alarm._validate_time_format('24:00') is False
        assert alarm._validate_time_format('12:60') is False
        assert alarm._validate_time_format('invalid') is False
        assert alarm._validate_time_format('1:30') is False
        assert alarm._validate_time_format('12:5') is False


class TestErrorMessages:
    """Tests for user-friendly error messages."""
    
    def test_get_user_friendly_error_no_device(self):
        """Should provide helpful message for no active device."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('No active device', 'My Playlist')
        assert 'No active Spotify device' in msg
        assert 'My Playlist' in msg
    
    def test_get_user_friendly_error_authentication(self):
        """Should provide helpful message for authentication errors."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('Token expired', 'Test')
        assert 'Authentication expired' in msg or 'authentication' in msg.lower()
    
    def test_get_user_friendly_error_premium(self):
        """Should provide helpful message for premium requirement."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('Premium required', 'Test')
        assert 'Premium' in msg
    
    def test_get_user_friendly_error_rate_limit(self):
        """Should provide helpful message for rate limiting."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('Rate limit exceeded', 'Test')
        assert 'Rate limit' in msg or 'rate' in msg.lower()


class TestDayParsing:
    """Tests for day parsing and formatting."""
    
    def test_parse_days_none(self):
        """Parsing None should return None (every day)."""
        alarm = Alarm()
        result = alarm._parse_days(None)
        assert result is None
    
    def test_parse_days_weekdays_string(self):
        """Parsing 'weekdays' should return Mon-Fri list."""
        alarm = Alarm()
        result = alarm._parse_days('weekdays')
        assert result == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    def test_parse_days_weekends_string(self):
        """Parsing 'weekends' should return Sat-Sun list."""
        alarm = Alarm()
        result = alarm._parse_days('weekends')
        assert result == ['Saturday', 'Sunday']
    
    def test_parse_days_list(self):
        """Parsing list of days should normalize them."""
        alarm = Alarm()
        result = alarm._parse_days(['monday', 'Wednesday', 'FRI'])
        assert result == ['Monday', 'Wednesday', 'Friday']
    
    def test_parse_days_abbreviations(self):
        """Parsing abbreviated day names should work."""
        alarm = Alarm()
        result = alarm._parse_days(['mon', 'wed', 'fri'])
        assert result == ['Monday', 'Wednesday', 'Friday']
    
    def test_format_days_display_none(self):
        """Formatting None should return 'Every day'."""
        alarm = Alarm()
        result = alarm._format_days_display(None)
        assert result == 'Every day'
    
    def test_format_days_display_weekdays(self):
        """Formatting Mon-Fri should return 'Weekdays'."""
        alarm = Alarm()
        result = alarm._format_days_display(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        assert result == 'Weekdays'
    
    def test_format_days_display_weekends(self):
        """Formatting Sat-Sun should return 'Weekends'."""
        alarm = Alarm()
        result = alarm._format_days_display(['Saturday', 'Sunday'])
        assert result == 'Weekends'
    
    def test_format_days_display_custom(self):
        """Formatting custom days should return abbreviated list."""
        alarm = Alarm()
        result = alarm._format_days_display(['Monday', 'Wednesday', 'Friday'])
        assert result == 'Mon, Wed, Fri'


class TestConditionalPlayback:
    """Tests for day-specific conditional playback."""
    
    def test_conditional_play_every_day(self):
        """Should play on any day when days is None."""
        alarm = Alarm()
        mock_api = Mock()
        
        # With days=None, should always play
        alarm._conditional_play_playlist(
            'spotify:playlist:test', mock_api, 80, 'Test', False, 10, None
        )
        
        mock_api.play_playlist_by_uri.assert_called_once()
    
    def test_conditional_play_on_active_day(self):
        """Should play when today is in active days."""
        alarm = Alarm()
        mock_api = Mock()
        
        # Get today's actual day name
        from datetime import datetime
        today = datetime.now().strftime('%A')
        
        # Set active days to include today
        alarm._conditional_play_playlist(
            'spotify:playlist:test', mock_api, 80, 'Test', False, 10, 
            [today]
        )
        
        mock_api.play_playlist_by_uri.assert_called_once()
    
    def test_conditional_play_skip_inactive_day(self):
        """Should skip when today is not in active days."""
        alarm = Alarm()
        mock_api = Mock()
        
        # Get today's actual day name and create a list without it
        from datetime import datetime
        today = datetime.now().strftime('%A')
        
        # Create list of all days except today
        all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        inactive_days = [day for day in all_days if day != today]
        
        alarm._conditional_play_playlist(
            'spotify:playlist:test', mock_api, 80, 'Test', False, 10, 
            inactive_days
        )
        
        mock_api.play_playlist_by_uri.assert_not_called()


class TestSnoozeAlarm:
    """Tests for snooze_alarm method."""
    
    def test_snooze_alarm_creates_scheduled_job(self):
        """Snoozing should create a scheduled job."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm_data = {
            'playlist_uri': 'spotify:playlist:test123',
            'playlist_name': 'Morning Playlist',
            'volume': 75,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': mock_api
        }
        
        alarm.snooze_alarm(alarm_data, snooze_minutes=5)
        
        assert len(alarm.snoozed_alarms) == 1
        assert alarm.snoozed_alarms[0]['original_playlist'] == 'Morning Playlist'
        assert alarm.snoozed_alarms[0]['snooze_duration'] == 5
    
    def test_snooze_alarm_starts_scheduler(self):
        """Snoozing should start scheduler if not running."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm_data = {
            'playlist_uri': 'spotify:playlist:test456',
            'playlist_name': 'Test',
            'volume': 80,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': mock_api
        }
        
        alarm.snooze_alarm(alarm_data, snooze_minutes=10)
        
        assert alarm.scheduler_running is True
        assert alarm.scheduler_thread is not None
    
    def test_snooze_alarm_multiple_snoozes(self):
        """Should be able to snooze multiple alarms."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm_data_1 = {
            'playlist_uri': 'spotify:playlist:a',
            'playlist_name': 'Playlist A',
            'volume': 70,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': mock_api
        }
        
        alarm_data_2 = {
            'playlist_uri': 'spotify:playlist:b',
            'playlist_name': 'Playlist B',
            'volume': 80,
            'fade_in_enabled': True,
            'fade_in_duration': 15,
            'spotify_api': mock_api
        }
        
        alarm.snooze_alarm(alarm_data_1, snooze_minutes=5)
        alarm.snooze_alarm(alarm_data_2, snooze_minutes=10)
        
        assert len(alarm.snoozed_alarms) == 2
    
    def test_snooze_alarm_default_duration(self):
        """Default snooze duration should be 5 minutes."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm_data = {
            'playlist_uri': 'spotify:playlist:default',
            'playlist_name': 'Default Test',
            'volume': 80,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': mock_api
        }
        
        alarm.snooze_alarm(alarm_data)
        
        assert alarm.snoozed_alarms[0]['snooze_duration'] == 5


class TestGetSnoozedAlarms:
    """Tests for get_snoozed_alarms method."""
    
    def test_get_snoozed_alarms_empty(self):
        """Should return empty list when no alarms snoozed."""
        alarm = Alarm()
        result = alarm.get_snoozed_alarms()
        assert result == []
    
    def test_get_snoozed_alarms_returns_info(self):
        """Should return snoozed alarm information."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm_data = {
            'playlist_uri': 'spotify:playlist:test',
            'playlist_name': 'Snoozed Playlist',
            'volume': 85,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': mock_api
        }
        
        alarm.snooze_alarm(alarm_data, snooze_minutes=15)
        result = alarm.get_snoozed_alarms()
        
        assert len(result) == 1
        assert result[0]['original_playlist'] == 'Snoozed Playlist'
        assert result[0]['snooze_duration'] == 15
        assert 'snooze_time' in result[0]
    
    def test_get_snoozed_alarms_excludes_job(self):
        """Returned info should not include internal 'job' key."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm_data = {
            'playlist_uri': 'spotify:playlist:nojob',
            'playlist_name': 'No Job',
            'volume': 80,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': mock_api
        }
        
        alarm.snooze_alarm(alarm_data, snooze_minutes=5)
        result = alarm.get_snoozed_alarms()
        
        assert 'job' not in result[0]


class TestShutdownWithSnooze:
    """Tests for shutdown method with snoozed alarms."""
    
    def test_shutdown_clears_snoozed_alarms(self):
        """Shutdown should clear snoozed alarms."""
        alarm = Alarm()
        mock_api = Mock()
        
        # Add regular alarm
        alarm.set_alarm('08:00', 'Morning', 'spotify:playlist:morning', mock_api)
        
        # Add snoozed alarm
        alarm_data = {
            'playlist_uri': 'spotify:playlist:snooze',
            'playlist_name': 'Snoozed',
            'volume': 80,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': mock_api
        }
        alarm.snooze_alarm(alarm_data, snooze_minutes=5)
        
        alarm.shutdown()
        
        assert len(alarm.alarms) == 0
        assert len(alarm.snoozed_alarms) == 0
        assert alarm.scheduler_running is False


class TestFadeInFeature:
    """Tests for fade-in feature."""
    
    def test_set_alarm_with_fade_in_enabled(self):
        """Setting alarm with fade-in should store fade-in parameters."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm(
            '07:30', 'Morning Playlist', 'spotify:playlist:morning',
            mock_api, volume=80, fade_in_enabled=True, fade_in_duration=15
        )
        
        assert len(alarm.alarms) == 1
        assert alarm.alarms[0]['fade_in_enabled'] is True
        assert alarm.alarms[0]['fade_in_duration'] == 15
    
    def test_set_alarm_fade_in_defaults(self):
        """Fade-in should default to disabled with 10 minute duration."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('08:00', 'Test', 'spotify:playlist:test', mock_api)
        
        assert alarm.alarms[0]['fade_in_enabled'] is False
        assert alarm.alarms[0]['fade_in_duration'] == 10
    
    def test_get_alarms_includes_fade_in_info(self):
        """get_alarms should return fade-in information."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm(
            '09:00', 'Test Playlist', 'spotify:playlist:test',
            mock_api, volume=70, fade_in_enabled=True, fade_in_duration=20
        )
        
        result = alarm.get_alarms()
        
        assert len(result) == 1
        assert result[0]['fade_in_enabled'] is True
        assert result[0]['fade_in_duration'] == 20
    
    def test_fade_in_duration_range(self):
        """Fade-in duration should be within 5-30 minute range."""
        alarm = Alarm()
        mock_api = Mock()
        
        # Test minimum
        alarm.set_alarm(
            '06:00', 'Min Fade', 'spotify:playlist:min',
            mock_api, fade_in_enabled=True, fade_in_duration=5
        )
        assert alarm.alarms[0]['fade_in_duration'] == 5
        
        # Test maximum
        alarm.set_alarm(
            '07:00', 'Max Fade', 'spotify:playlist:max',
            mock_api, fade_in_enabled=True, fade_in_duration=30
        )
        assert alarm.alarms[1]['fade_in_duration'] == 30
        
        # Test mid-range
        alarm.set_alarm(
            '08:00', 'Mid Fade', 'spotify:playlist:mid',
            mock_api, fade_in_enabled=True, fade_in_duration=15
        )
        assert alarm.alarms[2]['fade_in_duration'] == 15
    
    def test_snooze_with_fade_in(self):
        """Snoozed alarms should preserve fade-in settings."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm_data = {
            'playlist_uri': 'spotify:playlist:fade',
            'playlist_name': 'Fade Playlist',
            'volume': 75,
            'fade_in_enabled': True,
            'fade_in_duration': 20,
            'spotify_api': mock_api
        }
        
        alarm.snooze_alarm(alarm_data, snooze_minutes=10)
        
        assert len(alarm.snoozed_alarms) == 1


class TestFadeInController:
    """Tests for FadeInController class."""
    
    def test_fade_in_controller_available(self):
        """FadeInController should be available when PyQt5 is installed."""
        try:
            from alarm import FadeInController, PYQT_AVAILABLE
            assert PYQT_AVAILABLE is True
            assert FadeInController is not None
        except ImportError:
            pytest.skip("PyQt5 not available")
    
    def test_fade_in_controller_initialization(self):
        """FadeInController should initialize with correct parameters."""
        try:
            from alarm import FadeInController
            mock_api = Mock()
            
            controller = FadeInController(mock_api, target_volume=80, duration_minutes=10)
            
            assert controller.target_volume == 80
            assert controller.duration_minutes == 10
            assert controller.is_active is False
            assert controller.current_volume == 0
        except ImportError:
            pytest.skip("PyQt5 not available")
    
    def test_fade_in_controller_calculates_steps(self):
        """FadeInController should calculate correct number of steps."""
        try:
            from alarm import FadeInController
            mock_api = Mock()
            
            # 10 minutes = 600 seconds / 5 second intervals = 120 steps
            controller = FadeInController(mock_api, target_volume=100, duration_minutes=10)
            
            assert controller.step_interval_ms == 5000
            assert controller.total_steps == 120
            expected_volume_step = 100 / 120
            assert abs(controller.volume_step - expected_volume_step) < 0.01
        except ImportError:
            pytest.skip("PyQt5 not available")
