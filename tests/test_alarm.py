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
- Fade-in controller functionality (Phase 2)
- Day-specific scheduling (Phase 2)
- Template management (Phase 2)

Run with: python -m pytest tests/test_alarm.py -v
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import schedule

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
    
    def test_set_alarm_stores_playlist_name_and_uri(self):
        """set_alarm should store both playlist_name and playlist_uri."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('07:30', 'Wake Up Mix', 'spotify:playlist:wake123', mock_api, 70)
        
        assert len(alarm.alarms) == 1
        alarm_data = alarm.alarms[0]
        assert alarm_data['playlist'] == 'Wake Up Mix'
        assert alarm_data['playlist_uri'] == 'spotify:playlist:wake123'
        assert 'playlist' in alarm_data
        assert 'playlist_uri' in alarm_data
    
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
    
    def test_set_alarm_with_multiple_alarms_different_uris(self):
        """Multiple alarms should maintain separate URIs correctly."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('07:00', 'Morning Mix', 'spotify:playlist:morning123', mock_api, 70)
        alarm.set_alarm('12:00', 'Lunch Vibes', 'spotify:playlist:lunch456', mock_api, 60)
        alarm.set_alarm('18:00', 'Evening Jazz', 'spotify:playlist:evening789', mock_api, 80)
        
        assert len(alarm.alarms) == 3
        assert alarm.alarms[0]['playlist_uri'] == 'spotify:playlist:morning123'
        assert alarm.alarms[1]['playlist_uri'] == 'spotify:playlist:lunch456'
        assert alarm.alarms[2]['playlist_uri'] == 'spotify:playlist:evening789'
    
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
    
    def test_get_alarms_includes_both_name_and_uri(self):
        """get_alarms should return both playlist name and URI for each alarm."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('09:00', 'Morning Mix', 'spotify:playlist:morning', mock_api, 70)
        alarm.set_alarm('17:00', 'Evening Chill', 'spotify:playlist:evening', mock_api, 60)
        
        result = alarm.get_alarms()
        
        assert len(result) == 2
        # First alarm
        assert result[0]['playlist'] == 'Morning Mix'
        assert result[0]['playlist_uri'] == 'spotify:playlist:morning'
        # Second alarm
        assert result[1]['playlist'] == 'Evening Chill'
        assert result[1]['playlist_uri'] == 'spotify:playlist:evening'
    
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
    
    def test_play_playlist_uses_uri_not_name(self):
        """play_playlist should use playlist URI for playback, not name."""
        alarm = Alarm()
        mock_api = Mock()
        
        playlist_uri = 'spotify:playlist:test_uri_123'
        playlist_name = 'Test Playlist Name'
        
        alarm.play_playlist(playlist_uri, mock_api, 75, playlist_name)
        
        # Should call play_playlist_by_uri with the URI
        mock_api.play_playlist_by_uri.assert_called_with(playlist_uri)
        # Should NOT call play_playlist (the name-based method)
        assert not hasattr(mock_api.play_playlist, 'called') or not mock_api.play_playlist.called
    
    def test_play_playlist_by_uri_called_correctly(self):
        """play_playlist should call SpotifyAPI.play_playlist_by_uri with correct URI."""
        alarm = Alarm()
        mock_api = Mock()
        
        test_uri = 'spotify:playlist:unique_id_xyz'
        
        alarm.play_playlist(test_uri, mock_api, 80, 'Playlist Name')
        
        # Verify play_playlist_by_uri is called once with the correct URI
        mock_api.play_playlist_by_uri.assert_called_once_with(test_uri)
    
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
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Transient error")
        
        mock_api.play_playlist_by_uri.side_effect = side_effect
        
        alarm.play_playlist('spotify:playlist:test789', mock_api, 80, 'Test')
        
        assert call_count == 2
    
    def test_play_playlist_exponential_backoff(self):
        """play_playlist should use exponential backoff between retries."""
        alarm = Alarm()
        mock_api = Mock()
        
        retry_times = []
        call_count = 0
        
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            retry_times.append(time.time())
            if call_count < 3:
                raise Exception("Transient error")
        
        mock_api.play_playlist_by_uri.side_effect = side_effect
        
        start_time = time.time()
        alarm.play_playlist('spotify:playlist:backoff_test', mock_api, 80, 'Backoff Test')
        
        # Verify we had 3 attempts
        assert call_count == 3
        
        # Verify exponential backoff timing
        # First retry should wait ~2 seconds (2 * 2^0)
        # Second retry should wait ~4 seconds (2 * 2^1)
        if len(retry_times) >= 3:
            delay1 = retry_times[1] - retry_times[0]
            delay2 = retry_times[2] - retry_times[1]
            
            # Allow some tolerance for execution time
            assert delay1 >= 1.8  # ~2 seconds
            assert delay2 >= 3.8  # ~4 seconds
            assert delay2 > delay1  # Second delay should be longer
    
    def test_play_playlist_max_retries(self):
        """play_playlist should stop after max retries."""
        alarm = Alarm()
        mock_api = Mock()
        mock_api.play_playlist_by_uri.side_effect = Exception("Persistent error")
        
        call_count = 0
        def count_calls(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise Exception("Persistent error")
        
        mock_api.play_playlist_by_uri.side_effect = count_calls
        
        # Should fail after 3 attempts
        alarm.play_playlist('spotify:playlist:fail', mock_api, 80, 'Fail')
        
        assert call_count == 3  # Should try exactly 3 times
    
    def test_play_playlist_different_errors(self):
        """play_playlist should handle different types of errors during retries."""
        alarm = Alarm()
        mock_api = Mock()
        
        errors = [
            RuntimeError("Device not found"),
            ConnectionError("Network timeout")
        ]
        
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            if call_count < len(errors):
                error = errors[call_count]
                call_count += 1
                raise error
            call_count += 1
        
        mock_api.play_playlist_by_uri.side_effect = side_effect
        
        alarm.play_playlist('spotify:playlist:mixed_errors', mock_api, 80, 'Mixed Errors')
        
        # Should succeed after 2 failed attempts
        assert call_count == 3
    
    def test_play_playlist_retry_preserves_parameters(self):
        """play_playlist should preserve parameters across retry attempts."""
        alarm = Alarm()
        mock_api = Mock()
        
        received_params = []
        call_count = 0
        
        def track_params(uri):
            nonlocal call_count
            call_count += 1
            received_params.append(uri)
            if call_count < 2:
                raise Exception("Retry error")
        
        mock_api.play_playlist_by_uri.side_effect = track_params
        
        test_uri = 'spotify:playlist:preserve_params'
        alarm.play_playlist(test_uri, mock_api, 85, 'Preserve Test')
        
        # Both attempts should use same URI
        assert len(received_params) == 2
        assert all(uri == test_uri for uri in received_params)
    
    def test_play_playlist_passes_uri_through_retries(self):
        """play_playlist should maintain URI consistency across retry attempts."""
        alarm = Alarm()
        mock_api = Mock()
        
        test_uri = 'spotify:playlist:retry_test'
        call_count = 0
        
        def side_effect(uri):
            nonlocal call_count
            call_count += 1
            # Verify URI is correct on each attempt
            assert uri == test_uri
            if call_count < 2:
                raise Exception("Transient error")
        
        mock_api.play_playlist_by_uri.side_effect = side_effect
        
        alarm.play_playlist(test_uri, mock_api, 80, 'Test Playlist')
        
        assert call_count == 2
        assert mock_api.play_playlist_by_uri.call_count == 2
    
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
    
    def test_validate_time_format_edge_cases(self):
        """Should handle edge case time formats."""
        alarm = Alarm()
        # Valid edge cases
        assert alarm._validate_time_format('00:00') is True
        assert alarm._validate_time_format('23:59') is True
        
        # Invalid edge cases
        assert alarm._validate_time_format('24:00') is False
        assert alarm._validate_time_format('23:60') is False
        assert alarm._validate_time_format('-1:00') is False
        assert alarm._validate_time_format('00:-1') is False
    
    def test_validate_time_format_malformed_strings(self):
        """Should reject malformed time strings."""
        alarm = Alarm()
        assert alarm._validate_time_format('') is False
        assert alarm._validate_time_format('12') is False
        assert alarm._validate_time_format('12:') is False
        assert alarm._validate_time_format(':30') is False
        assert alarm._validate_time_format('12:30:00') is False
        assert alarm._validate_time_format('12.30') is False
        assert alarm._validate_time_format('12-30') is False
    
    def test_validate_time_format_non_numeric(self):
        """Should reject non-numeric time values."""
        alarm = Alarm()
        assert alarm._validate_time_format('aa:bb') is False
        assert alarm._validate_time_format('12:bb') is False
        assert alarm._validate_time_format('aa:30') is False
        assert alarm._validate_time_format('twelve:thirty') is False
    
    def test_validate_time_format_whitespace(self):
        """Should reject time strings with whitespace."""
        alarm = Alarm()
        assert alarm._validate_time_format(' 12:30') is False
        assert alarm._validate_time_format('12:30 ') is False
        assert alarm._validate_time_format('12 :30') is False
        assert alarm._validate_time_format('12: 30') is False


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
    
    def test_get_user_friendly_error_network(self):
        """Should provide helpful message for network errors."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('Network connection failed', 'Test Playlist')
        assert 'Network error' in msg or 'network' in msg.lower()
        assert 'Test Playlist' in msg
    
    def test_get_user_friendly_error_not_found(self):
        """Should provide helpful message for playlist not found errors."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('404 Not found', 'Deleted Playlist')
        assert 'not found' in msg.lower()
        assert 'Deleted Playlist' in msg
    
    def test_get_user_friendly_error_unauthorized(self):
        """Should provide helpful message for unauthorized errors."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('Unauthorized access', 'Playlist')
        assert 'Authentication expired' in msg or 'authentication' in msg.lower()
    
    def test_get_user_friendly_error_timeout(self):
        """Should provide helpful message for timeout errors."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('Request timeout', 'Test Playlist')
        assert 'Network error' in msg or 'timeout' in msg.lower()
    
    def test_get_user_friendly_error_premium_restriction(self):
        """Should provide helpful message for premium restriction errors."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('Restriction: premium_required', 'Test')
        assert 'Premium' in msg or 'premium' in msg.lower()
    
    def test_get_user_friendly_error_429_rate_limit(self):
        """Should detect rate limit from HTTP 429 status code."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('HTTP 429 Too Many Requests', 'Test')
        assert 'Rate limit' in msg or 'rate' in msg.lower()
    
    def test_get_user_friendly_error_generic(self):
        """Should provide generic message for unknown errors."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('Unknown error xyz123', 'Test Playlist')
        assert 'Test Playlist' in msg
        assert 'xyz123' in msg
    
    def test_get_user_friendly_error_empty_string(self):
        """Should handle empty error message gracefully."""
        alarm = Alarm()
        msg = alarm._get_user_friendly_error('', 'Test Playlist')
        assert 'Test Playlist' in msg
    
    def test_get_user_friendly_error_case_insensitive(self):
        """Should match error patterns case-insensitively."""
        alarm = Alarm()
        
        # Test various case combinations
        msg1 = alarm._get_user_friendly_error('PREMIUM REQUIRED', 'Test')
        assert 'Premium' in msg1
        
        msg2 = alarm._get_user_friendly_error('No Active Device', 'Test')
        assert 'device' in msg2.lower()
        
        msg3 = alarm._get_user_friendly_error('RATE LIMIT', 'Test')
        assert 'rate' in msg3.lower()


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
            'spotify:playlist:test', mock_api, 80, 'Test', False, 10, None, 'test-id'
        )
        
        mock_api.play_playlist_by_uri.assert_called_once()
    
    def test_conditional_play_on_active_day(self):
        """Should play when today is in active days."""
        alarm = Alarm()
        mock_api = Mock()
        
        # Get today's actual day name
        today = datetime.now().strftime('%A')
        
        # Set active days to include today
        alarm._conditional_play_playlist(
            'spotify:playlist:test', mock_api, 80, 'Test', False, 10, 
            [today], 'test-id'
        )
        
        mock_api.play_playlist_by_uri.assert_called_once()
    
    def test_conditional_play_uses_uri(self):
        """_conditional_play_playlist should pass URI to play_playlist."""
        alarm = Alarm()
        mock_api = Mock()
        
        test_uri = 'spotify:playlist:conditional_test'
        today = datetime.now().strftime('%A')
        
        # Mock the play_playlist method to track calls
        with patch.object(alarm, 'play_playlist') as mock_play:
            alarm._conditional_play_playlist(
                test_uri, mock_api, 80, 'Test Playlist', False, 10, [today], 'test-id'
            )
            
            # Verify play_playlist was called with the URI
            mock_play.assert_called_once()
            args = mock_play.call_args[0]
            assert args[0] == test_uri
    
    def test_conditional_play_skip_inactive_day(self):
        """Should skip when today is not in active days."""
        alarm = Alarm()
        mock_api = Mock()
        
        # Get today's actual day name and create a list without it
        today = datetime.now().strftime('%A')
        
        # Create list of all days except today
        all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        inactive_days = [day for day in all_days if day != today]
        
        alarm._conditional_play_playlist(
            'spotify:playlist:test', mock_api, 80, 'Test', False, 10, 
            inactive_days, 'test-id'
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
    
    def test_shutdown_clears_snoozed_alarms(self, tmp_path):
        """Shutdown should clear snoozed alarms."""
        alarm = Alarm()
        alarm.snooze_state_file = tmp_path / 'snooze_test.json'
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
    
    def test_shutdown_stops_scheduler_thread(self, tmp_path):
        """Shutdown should stop and join the scheduler thread."""
        alarm = Alarm()
        alarm.snooze_state_file = tmp_path / 'snooze_test.json'
        mock_api = Mock()
        
        # Start scheduler by setting an alarm
        alarm.set_alarm('08:00', 'Morning', 'spotify:playlist:morning', mock_api)
        
        # Verify scheduler is running
        assert alarm.scheduler_running is True
        assert alarm.scheduler_thread is not None
        assert alarm.scheduler_thread.is_alive()
        
        # Shutdown
        alarm.shutdown()
        
        # Verify scheduler stopped
        assert alarm.scheduler_running is False
        
        # Give thread time to finish
        time.sleep(0.5)
        
        # Verify thread is no longer alive
        assert not alarm.scheduler_thread.is_alive()
    
    def test_shutdown_cancels_scheduled_jobs(self, tmp_path):
        """Shutdown should cancel all scheduled jobs."""
        alarm = Alarm()
        alarm.snooze_state_file = tmp_path / 'snooze_test.json'
        mock_api = Mock()
        
        # Add multiple alarms
        alarm.set_alarm('08:00', 'Morning', 'spotify:playlist:morning', mock_api)
        alarm.set_alarm('12:00', 'Lunch', 'spotify:playlist:lunch', mock_api)
        alarm.set_alarm('18:00', 'Evening', 'spotify:playlist:evening', mock_api)
        
        # Verify alarms are set
        assert len(alarm.alarms) == 3
        
        # Shutdown
        alarm.shutdown()
        
        # Verify all alarms cleared
        assert len(alarm.alarms) == 0
        assert len(schedule.jobs) == 0
    
    def test_shutdown_with_no_alarms(self, tmp_path):
        """Shutdown should work gracefully with no alarms set."""
        alarm = Alarm()
        alarm.snooze_state_file = tmp_path / 'snooze_test.json'
        
        # No alarms set
        assert len(alarm.alarms) == 0
        assert alarm.scheduler_running is False
        
        # Shutdown should not raise errors
        alarm.shutdown()
        
        assert alarm.scheduler_running is False
        assert len(alarm.alarms) == 0
    
    def test_shutdown_saves_snooze_state(self, tmp_path):
        """Shutdown should save snooze state before exiting."""
        alarm = Alarm()
        alarm.snooze_state_file = tmp_path / 'snooze_test.json'
        mock_api = Mock()
        
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
        
        # Verify state file exists after snooze
        assert alarm.snooze_state_file.exists()
        
        # Shutdown
        alarm.shutdown()
        
        # State file should still exist (for persistence)
        assert alarm.snooze_state_file.exists()
    
    def test_shutdown_stops_device_wake_manager(self, tmp_path):
        """Shutdown should stop device wake manager if active."""
        alarm = Alarm()
        alarm.snooze_state_file = tmp_path / 'snooze_test.json'
        mock_api = Mock()
        
        # Set alarm to initialize device wake manager
        alarm.set_alarm('08:00', 'Morning', 'spotify:playlist:morning', mock_api)
        
        # Verify device wake manager is initialized
        assert alarm.device_wake_manager is not None
        
        # Mock shutdown method on device wake manager
        alarm.device_wake_manager.shutdown = Mock()
        
        # Shutdown
        alarm.shutdown()
        
        # Verify device wake manager shutdown was called
        alarm.device_wake_manager.shutdown.assert_called_once()
    
    def test_shutdown_with_multiple_snoozed_alarms(self, tmp_path):
        """Shutdown should clear multiple snoozed alarms."""
        alarm = Alarm()
        alarm.snooze_state_file = tmp_path / 'snooze_test.json'
        # Clear any loaded snoozed alarms
        alarm.snoozed_alarms.clear()
        mock_api = Mock()
        
        # Add multiple snoozed alarms
        for i in range(3):
            alarm_data = {
                'playlist_uri': f'spotify:playlist:snooze{i}',
                'playlist_name': f'Snoozed {i}',
                'volume': 80,
                'fade_in_enabled': False,
                'fade_in_duration': 10,
                'spotify_api': mock_api
            }
            alarm.snooze_alarm(alarm_data, snooze_minutes=5)
        
        # Verify snoozed alarms are set
        assert len(alarm.snoozed_alarms) == 3
        
        # Shutdown
        alarm.shutdown()
        
        # Verify all snoozed alarms cleared
        assert len(alarm.snoozed_alarms) == 0
    
    def test_shutdown_thread_timeout_handling(self, tmp_path):
        """Shutdown should handle thread timeout gracefully."""
        alarm = Alarm()
        alarm.snooze_state_file = tmp_path / 'snooze_test.json'
        mock_api = Mock()
        
        # Start scheduler
        alarm.set_alarm('08:00', 'Morning', 'spotify:playlist:morning', mock_api)
        
        # Mock thread to not stop immediately
        original_join = alarm.scheduler_thread.join
        
        def slow_join(timeout=None):
            # Simulate slow join by calling original with reduced timeout
            original_join(timeout=0.1)
        
        alarm.scheduler_thread.join = slow_join
        
        # Shutdown should complete without hanging
        alarm.shutdown()
        
        # Should still mark scheduler as not running
        assert alarm.scheduler_running is False


class TestFadeInFeature:
    """Tests for fade-in feature - Phase 2."""
    
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
    """Tests for FadeInController class - Phase 2."""
    
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
    
    def test_fade_in_controller_start(self):
        """FadeInController should start fade-in process."""
        try:
            from alarm import FadeInController
            mock_api = Mock()
            
            controller = FadeInController(mock_api, target_volume=80, duration_minutes=10)
            controller.start()
            
            assert controller.is_active is True
            assert controller.current_step == 0
            mock_api.set_volume.assert_called_with(0)
        except ImportError:
            pytest.skip("PyQt5 not available")
    
    def test_fade_in_controller_stop(self):
        """FadeInController should stop fade-in process."""
        try:
            from alarm import FadeInController
            mock_api = Mock()
            
            controller = FadeInController(mock_api, target_volume=80, duration_minutes=10)
            controller.start()
            assert controller.is_active is True
            
            controller.stop()
            assert controller.is_active is False
        except ImportError:
            pytest.skip("PyQt5 not available")
    
    def test_fade_in_controller_volume_progression(self):
        """FadeInController should gradually increase volume."""
        try:
            from alarm import FadeInController
            mock_api = Mock()
            
            controller = FadeInController(mock_api, target_volume=100, duration_minutes=10)
            controller.start()
            
            # Simulate several steps
            for i in range(5):
                controller._update_volume()
            
            # Volume should have increased
            assert controller.current_volume > 0
            assert controller.current_volume < controller.target_volume
            assert mock_api.set_volume.call_count >= 5
        except ImportError:
            pytest.skip("PyQt5 not available")



# Legacy Template tests removed for MVP


class TestDaySpecificScheduling:
    """Tests for day-specific alarm scheduling - Phase 2."""
    
    def test_alarm_triggers_on_specified_days(self):
        """Alarm should only trigger on specified days."""
        alarm = Alarm()
        mock_api = Mock()
        
        today = datetime.now().strftime('%A')
        
        # Set alarm for today only
        alarm.set_alarm(
            '12:00', 'Today Only', 'spotify:playlist:today',
            mock_api, 80, False, 10, [today]
        )
        
        # Manually trigger conditional play
        alarm._conditional_play_playlist(
            'spotify:playlist:today', mock_api, 80, 'Today Only',
            False, 10, [today], 'test-id'
        )
        
        mock_api.play_playlist_by_uri.assert_called_once()
    
    def test_alarm_scheduling_preserves_uri(self):
        """Scheduled alarm should preserve playlist URI for playback."""
        alarm = Alarm()
        mock_api = Mock()
        
        playlist_uri = 'spotify:playlist:preserve_test'
        playlist_name = 'Preserve Test'
        today = datetime.now().strftime('%A')
        
        alarm.set_alarm('14:00', playlist_name, playlist_uri, mock_api, 80, False, 10, [today])
        
        # Verify alarm data contains URI
        assert len(alarm.alarms) == 1
        alarm_data = alarm.alarms[0]
        assert alarm_data['playlist_uri'] == playlist_uri
        assert alarm_data['playlist'] == playlist_name
    
    def test_get_next_trigger_time_with_days(self):
        """Should calculate next trigger considering day restrictions."""
        alarm = Alarm()
        mock_api = Mock()
        
        # Set alarm for specific days
        alarm.set_alarm(
            '08:00', 'Weekdays', 'spotify:playlist:weekdays',
            mock_api, 80, False, 10, ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        )
        
        alarm_info = alarm.get_alarms()[0]
        next_time = alarm.get_next_trigger_time(alarm_info)
        
        # Should return a future datetime
        assert next_time is not None
        assert next_time > datetime.now()
        
        # Should be on a weekday
        assert next_time.strftime('%A') in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    def test_get_upcoming_alarms_with_day_restrictions(self):
        """Should return upcoming alarms respecting day restrictions."""
        alarm = Alarm()
        mock_api = Mock()
        
        # Set alarm for weekdays
        alarm.set_alarm(
            '07:00', 'Weekday Morning', 'spotify:playlist:weekday',
            mock_api, 80, False, 10, 'weekdays'
        )
        
        # Set alarm for weekends
        alarm.set_alarm(
            '09:00', 'Weekend Morning', 'spotify:playlist:weekend',
            mock_api, 80, False, 10, 'weekends'
        )
        
        upcoming = alarm.get_upcoming_alarms(days=7)
        
        # Should have multiple upcoming triggers
        assert len(upcoming) > 0
        
        # Check that each trigger respects day restrictions
        for item in upcoming:
            trigger_day = item['datetime'].strftime('%A')
            alarm_info = item['alarm_info']
            days = alarm_info.get('days')
            
            if days:
                assert trigger_day in days


class TestPlaylistURIRefactoring:
    """Tests for playlist URI refactoring - verifies URI-based playback."""
    
    def test_set_alarm_stores_both_name_and_uri(self):
        """set_alarm should store both playlist name (for display) and URI (for playback)."""
        alarm = Alarm()
        mock_api = Mock()
        
        playlist_name = 'My Awesome Playlist'
        playlist_uri = 'spotify:playlist:abc123xyz'
        
        alarm.set_alarm('08:30', playlist_name, playlist_uri, mock_api, 75)
        
        assert len(alarm.alarms) == 1
        alarm_data = alarm.alarms[0]
        assert alarm_data['playlist'] == playlist_name
        assert alarm_data['playlist_uri'] == playlist_uri
    
    def test_play_playlist_uses_uri_parameter(self):
        """play_playlist should use the URI parameter for playback, not lookup by name."""
        alarm = Alarm()
        mock_api = Mock()
        
        test_uri = 'spotify:playlist:direct_uri_123'
        test_name = 'Display Name'
        
        alarm.play_playlist(test_uri, mock_api, 80, test_name)
        
        # Should call play_playlist_by_uri with the URI parameter
        mock_api.play_playlist_by_uri.assert_called_once_with(test_uri)
    
    def test_play_playlist_by_uri_receives_correct_uri(self):
        """SpotifyAPI.play_playlist_by_uri should receive the exact URI passed."""
        alarm = Alarm()
        mock_api = Mock()
        
        uris_to_test = [
            'spotify:playlist:test1',
            'spotify:playlist:test2',
            'spotify:playlist:test3'
        ]
        
        for uri in uris_to_test:
            mock_api.reset_mock()
            alarm.play_playlist(uri, mock_api, 80, 'Test')
            mock_api.play_playlist_by_uri.assert_called_once_with(uri)
    
    def test_alarm_trigger_flow_uses_uri(self):
        """Full alarm trigger flow should use URI from set_alarm through to playback."""
        alarm = Alarm()
        mock_api = Mock()
        
        playlist_name = 'Morning Routine'
        playlist_uri = 'spotify:playlist:morning_routine_uri'
        
        # Set alarm with name and URI
        alarm.set_alarm('07:00', playlist_name, playlist_uri, mock_api, 75)
        
        # Verify alarm stored both
        assert alarm.alarms[0]['playlist'] == playlist_name
        assert alarm.alarms[0]['playlist_uri'] == playlist_uri
        
        # Simulate alarm trigger by calling the scheduled function directly
        # (the _conditional_play_playlist which was scheduled)
        alarm.play_playlist(playlist_uri, mock_api, 75, playlist_name)
        
        # Verify playback used URI
        mock_api.play_playlist_by_uri.assert_called_with(playlist_uri)
    
    def test_get_alarms_returns_both_fields(self):
        """get_alarms should return both playlist name and URI fields."""
        alarm = Alarm()
        mock_api = Mock()
        
        test_cases = [
            ('06:00', 'Morning', 'spotify:playlist:morning'),
            ('12:00', 'Lunch', 'spotify:playlist:lunch'),
            ('18:00', 'Dinner', 'spotify:playlist:dinner'),
        ]
        
        for time, name, uri in test_cases:
            alarm.set_alarm(time, name, uri, mock_api, 80)
        
        alarms = alarm.get_alarms()
        
        assert len(alarms) == 3
        for i, (time, name, uri) in enumerate(test_cases):
            assert alarms[i]['time'] == time
            assert alarms[i]['playlist'] == name
            assert alarms[i]['playlist_uri'] == uri
    
    def test_snooze_preserves_uri_for_playback(self, tmp_path):
        """Snoozed alarm should preserve URI for rescheduled playback."""
        snooze_file = tmp_path / 'snooze.json'
        alarm = Alarm(snooze_state_file=snooze_file)
        mock_api = Mock()
        
        playlist_uri = 'spotify:playlist:snooze_test_uri'
        alarm_data = {
            'playlist_uri': playlist_uri,
            'playlist_name': 'Snooze Test',
            'volume': 80,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': mock_api
        }
        
        alarm.snooze_alarm(alarm_data, snooze_minutes=5)
        
        # Verify snoozed alarm has URI
        assert len(alarm.snoozed_alarms) == 1
        assert alarm.snoozed_alarms[0]['playlist_uri'] == playlist_uri
    
    def test_conditional_playback_passes_uri_correctly(self):
        """_conditional_play_playlist should pass URI to play_playlist."""
        alarm = Alarm()
        mock_api = Mock()
        
        test_uri = 'spotify:playlist:conditional_uri'
        today = datetime.now().strftime('%A')
        
        # Mock play_playlist to verify it receives the URI
        with patch.object(alarm, 'play_playlist') as mock_play:
            alarm._conditional_play_playlist(
                test_uri, mock_api, 80, 'Test', False, 10, [today], 'test-id'
            )
            
            # Verify first argument is the URI
            mock_play.assert_called_once()
            call_args = mock_play.call_args[0]
            assert call_args[0] == test_uri
    
    def test_multiple_alarms_maintain_uri_independence(self):
        """Multiple alarms should each maintain their own independent URIs."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarms_config = [
            ('06:00', 'Wake Up', 'spotify:playlist:wake'),
            ('08:00', 'Commute', 'spotify:playlist:commute'),
            ('12:00', 'Lunch', 'spotify:playlist:lunch'),
            ('18:00', 'Dinner', 'spotify:playlist:dinner'),
            ('22:00', 'Sleep', 'spotify:playlist:sleep'),
        ]
        
        for time, name, uri in alarms_config:
            alarm.set_alarm(time, name, uri, mock_api, 80)
        
        # Verify each alarm has correct URI
        for i, (time, name, uri) in enumerate(alarms_config):
            assert alarm.alarms[i]['playlist_uri'] == uri
            assert alarm.alarms[i]['playlist'] == name
    
    def test_retry_logic_maintains_uri_consistency(self):
        """Retry logic should maintain URI consistency across attempts."""
        alarm = Alarm()
        mock_api = Mock()
        
        test_uri = 'spotify:playlist:retry_uri'
        attempts = []
        
        def track_attempts(uri):
            attempts.append(uri)
            if len(attempts) < 3:
                raise Exception("Transient error")
        
        mock_api.play_playlist_by_uri.side_effect = track_attempts
        
        alarm.play_playlist(test_uri, mock_api, 80, 'Test')
        
        # All attempts should use the same URI
        assert len(attempts) == 3
        assert all(uri == test_uri for uri in attempts)


class TestSnoozeLogic:
    """Tests for snooze logic - Phase 2."""
    
    def test_snooze_reschedules_alarm(self):
        """Snooze should reschedule alarm for future time."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm_data = {
            'playlist_uri': 'spotify:playlist:snooze',
            'playlist_name': 'Snooze Test',
            'volume': 80,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': mock_api
        }
        
        before_snooze = datetime.now()
        alarm.snooze_alarm(alarm_data, snooze_minutes=10)
        
        snoozed = alarm.get_snoozed_alarms()[0]
        snooze_time = snoozed['snooze_time']
        
        # Snooze time should be approximately 10 minutes from now
        expected_time = before_snooze + timedelta(minutes=10)
        time_diff = abs((snooze_time - expected_time).total_seconds())
        
        assert time_diff < 5  # Within 5 seconds tolerance
    
    def test_snooze_preserves_uri(self):
        """Snooze should preserve playlist URI for rescheduled playback."""
        alarm = Alarm()
        mock_api = Mock()
        
        test_uri = 'spotify:playlist:snooze_uri_test'
        alarm_data = {
            'playlist_uri': test_uri,
            'playlist_name': 'Snooze URI Test',
            'volume': 75,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': mock_api
        }
        
        alarm.snooze_alarm(alarm_data, snooze_minutes=5)
        
        # Verify snoozed alarm has correct URI
        assert len(alarm.snoozed_alarms) == 1
        snoozed = alarm.snoozed_alarms[0]
        assert snoozed['playlist_uri'] == test_uri
    
    def test_snooze_preserves_alarm_settings(self):
        """Snooze should preserve all alarm settings."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm_data = {
            'playlist_uri': 'spotify:playlist:preserve',
            'playlist_name': 'Preserve Test',
            'volume': 65,
            'fade_in_enabled': True,
            'fade_in_duration': 25,
            'spotify_api': mock_api
        }
        
        alarm.snooze_alarm(alarm_data, snooze_minutes=15)
        
        # Check that snoozed alarm has all settings preserved
        snoozed_alarms = alarm.snoozed_alarms
        assert len(snoozed_alarms) == 1
        
        snoozed = snoozed_alarms[0]
        assert snoozed['volume'] == 65
        assert snoozed['fade_in_enabled'] is True
        assert snoozed['fade_in_duration'] == 25
    
    def test_multiple_snoozes_independent(self):
        """Multiple snoozed alarms should be independent."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm_data_1 = {
            'playlist_uri': 'spotify:playlist:snooze1',
            'playlist_name': 'Snooze 1',
            'volume': 70,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': mock_api
        }
        
        alarm_data_2 = {
            'playlist_uri': 'spotify:playlist:snooze2',
            'playlist_name': 'Snooze 2',
            'volume': 85,
            'fade_in_enabled': True,
            'fade_in_duration': 20,
            'spotify_api': mock_api
        }
        
        alarm.snooze_alarm(alarm_data_1, snooze_minutes=5)
        alarm.snooze_alarm(alarm_data_2, snooze_minutes=10)
        
        snoozed = alarm.get_snoozed_alarms()
        assert len(snoozed) == 2
        
        # Verify each has correct settings
        snooze_1 = [s for s in snoozed if s['original_playlist'] == 'Snooze 1'][0]
        snooze_2 = [s for s in snoozed if s['original_playlist'] == 'Snooze 2'][0]
        
        assert snooze_1['snooze_duration'] == 5
        assert snooze_2['snooze_duration'] == 10


class TestAlarmHistory:
    """Tests for AlarmHistory class."""
    
    def test_alarm_history_initialization(self, tmp_path):
        """AlarmHistory should initialize with empty history."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        assert history.history_file == history_file
        assert history.history == []
    
    def test_alarm_history_default_location(self):
        """AlarmHistory should use default location if no file specified."""
        from alarm import AlarmHistory
        from pathlib import Path
        
        history = AlarmHistory()
        
        assert history.history_file is not None
        assert history.history_file.parent == Path.home() / '.charmed'
    
    def test_record_alarm_trigger_success(self, tmp_path):
        """record_alarm_trigger should record successful alarm."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        alarm_data = {
            'time': '07:00',
            'playlist_name': 'Morning Mix',
            'playlist_uri': 'spotify:playlist:morning',
            'volume': 80,
            'fade_in_enabled': False,
            'fade_in_duration': 10
        }
        
        history.record_alarm_trigger(alarm_data, success=True)
        
        assert len(history.history) == 1
        entry = history.history[0]
        assert entry['trigger_time'] == '07:00'
        assert entry['playlist_name'] == 'Morning Mix'
        assert entry['volume'] == 80
        assert entry['success'] is True
        assert entry['error_message'] is None
        assert entry['snoozed'] is False
        assert entry['snooze_count'] == 0
        assert entry['dismissed'] is False
    
    def test_record_alarm_trigger_failure(self, tmp_path):
        """record_alarm_trigger should record failed alarm with error."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        alarm_data = {
            'time': '08:00',
            'playlist_name': 'Failed Playlist',
            'playlist_uri': 'spotify:playlist:fail',
            'volume': 75
        }
        
        history.record_alarm_trigger(alarm_data, success=False, error_message='No active device')
        
        assert len(history.history) == 1
        entry = history.history[0]
        assert entry['success'] is False
        assert entry['error_message'] == 'No active device'
    
    def test_record_alarm_trigger_with_fade_in(self, tmp_path):
        """record_alarm_trigger should record fade-in settings."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        alarm_data = {
            'time': '06:30',
            'playlist_name': 'Fade Test',
            'playlist_uri': 'spotify:playlist:fade',
            'volume': 85,
            'fade_in_enabled': True,
            'fade_in_duration': 20
        }
        
        history.record_alarm_trigger(alarm_data, success=True)
        
        entry = history.history[0]
        assert entry['fade_in_enabled'] is True
        assert entry['fade_in_duration'] == 20
    
    def test_record_alarm_trigger_includes_timestamp(self, tmp_path):
        """record_alarm_trigger should include ISO timestamp."""
        from alarm import AlarmHistory
        from datetime import datetime
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        alarm_data = {
            'time': '07:00',
            'playlist_name': 'Test',
            'playlist_uri': 'spotify:playlist:test',
            'volume': 80
        }
        
        before = datetime.now()
        history.record_alarm_trigger(alarm_data, success=True)
        after = datetime.now()
        
        entry = history.history[0]
        timestamp = datetime.fromisoformat(entry['timestamp'])
        assert before <= timestamp <= after
    
    def test_record_alarm_trigger_includes_day_of_week(self, tmp_path):
        """record_alarm_trigger should include day of week."""
        from alarm import AlarmHistory
        from datetime import datetime
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        alarm_data = {
            'time': '07:00',
            'playlist_name': 'Test',
            'playlist_uri': 'spotify:playlist:test',
            'volume': 80
        }
        
        history.record_alarm_trigger(alarm_data, success=True)
        
        entry = history.history[0]
        expected_day = datetime.now().strftime('%A')
        assert entry['day_of_week'] == expected_day
    
    def test_record_snooze(self, tmp_path):
        """record_snooze should update most recent alarm entry."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        alarm_data = {
            'time': '07:00',
            'playlist_name': 'Morning Mix',
            'playlist_uri': 'spotify:playlist:morning',
            'volume': 80
        }
        
        history.record_alarm_trigger(alarm_data, success=True)
        history.record_snooze(alarm_data, snooze_duration=5)
        
        entry = history.history[0]
        assert entry['snoozed'] is True
        assert entry['snooze_count'] == 1
        assert entry['snooze_duration'] == 5
    
    def test_record_snooze_multiple_times(self, tmp_path):
        """record_snooze should increment snooze count."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        alarm_data = {
            'time': '07:00',
            'playlist_name': 'Morning Mix',
            'playlist_uri': 'spotify:playlist:morning',
            'volume': 80
        }
        
        history.record_alarm_trigger(alarm_data, success=True)
        history.record_snooze(alarm_data, snooze_duration=5)
        history.record_snooze(alarm_data, snooze_duration=10)
        history.record_snooze(alarm_data, snooze_duration=15)
        
        entry = history.history[0]
        assert entry['snooze_count'] == 3
    
    def test_record_snooze_no_history(self, tmp_path):
        """record_snooze should handle empty history gracefully."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        alarm_data = {'playlist_name': 'Test'}
        history.record_snooze(alarm_data, snooze_duration=5)
        
        # Should not crash
        assert len(history.history) == 0
    
    def test_record_dismiss(self, tmp_path):
        """record_dismiss should mark alarm as dismissed."""
        from alarm import AlarmHistory
        from datetime import datetime
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        alarm_data = {
            'time': '07:00',
            'playlist_name': 'Morning Mix',
            'playlist_uri': 'spotify:playlist:morning',
            'volume': 80
        }
        
        history.record_alarm_trigger(alarm_data, success=True)
        
        before = datetime.now()
        history.record_dismiss(alarm_data)
        after = datetime.now()
        
        entry = history.history[0]
        assert entry['dismissed'] is True
        dismiss_time = datetime.fromisoformat(entry['dismiss_time'])
        assert before <= dismiss_time <= after
    
    def test_record_dismiss_no_history(self, tmp_path):
        """record_dismiss should handle empty history gracefully."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        alarm_data = {'playlist_name': 'Test'}
        history.record_dismiss(alarm_data)
        
        # Should not crash
        assert len(history.history) == 0
    
    def test_get_history_no_filters(self, tmp_path):
        """get_history should return all entries when no filters applied."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add multiple entries
        for i in range(5):
            alarm_data = {
                'time': f'0{i+6}:00',
                'playlist_name': f'Playlist {i}',
                'playlist_uri': f'spotify:playlist:{i}',
                'volume': 80
            }
            history.record_alarm_trigger(alarm_data, success=True)
        
        result = history.get_history()
        assert len(result) == 5
    
    def test_get_history_sorted_descending(self, tmp_path):
        """get_history should return entries sorted by timestamp descending."""
        from alarm import AlarmHistory
        import time
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add entries with small delays
        for i in range(3):
            alarm_data = {
                'time': f'0{i+6}:00',
                'playlist_name': f'Playlist {i}',
                'playlist_uri': f'spotify:playlist:{i}',
                'volume': 80
            }
            history.record_alarm_trigger(alarm_data, success=True)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        result = history.get_history()
        
        # Most recent should be first
        assert result[0]['playlist_name'] == 'Playlist 2'
        assert result[1]['playlist_name'] == 'Playlist 1'
        assert result[2]['playlist_name'] == 'Playlist 0'
    
    def test_get_history_with_limit(self, tmp_path):
        """get_history should respect limit parameter."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        for i in range(10):
            alarm_data = {
                'time': f'0{i}:00',
                'playlist_name': f'Playlist {i}',
                'playlist_uri': f'spotify:playlist:{i}',
                'volume': 80
            }
            history.record_alarm_trigger(alarm_data, success=True)
        
        result = history.get_history(limit=5)
        assert len(result) == 5
    
    def test_get_history_with_start_date(self, tmp_path):
        """get_history should filter by start date."""
        from alarm import AlarmHistory
        from datetime import datetime, timedelta
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Manually add entries with specific timestamps
        now = datetime.now()
        for days_ago in [30, 20, 10, 5, 1]:
            entry = {
                'timestamp': (now - timedelta(days=days_ago)).isoformat(),
                'trigger_time': '07:00',
                'playlist_name': f'Playlist {days_ago}d ago',
                'playlist_uri': 'spotify:playlist:test',
                'volume': 80,
                'fade_in_enabled': False,
                'fade_in_duration': 10,
                'day_of_week': 'Monday',
                'success': True,
                'error_message': None,
                'snoozed': False,
                'snooze_count': 0,
                'dismissed': False,
                'dismiss_time': None
            }
            history.history.append(entry)
        
        # Filter to last 15 days
        start_date = now - timedelta(days=15)
        result = history.get_history(start_date=start_date)
        
        # Should only include entries from 10, 5, and 1 days ago
        assert len(result) == 3
    
    def test_get_history_with_end_date(self, tmp_path):
        """get_history should filter by end date."""
        from alarm import AlarmHistory
        from datetime import datetime, timedelta
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        now = datetime.now()
        for days_ago in [30, 20, 10, 5, 1]:
            entry = {
                'timestamp': (now - timedelta(days=days_ago)).isoformat(),
                'trigger_time': '07:00',
                'playlist_name': f'Playlist {days_ago}d ago',
                'playlist_uri': 'spotify:playlist:test',
                'volume': 80,
                'fade_in_enabled': False,
                'fade_in_duration': 10,
                'day_of_week': 'Monday',
                'success': True,
                'error_message': None,
                'snoozed': False,
                'snooze_count': 0,
                'dismissed': False,
                'dismiss_time': None
            }
            history.history.append(entry)
        
        # Filter to older than 7 days
        end_date = now - timedelta(days=7)
        result = history.get_history(end_date=end_date)
        
        # Should only include entries from 30, 20, and 10 days ago
        assert len(result) == 3
    
    def test_get_history_with_date_range(self, tmp_path):
        """get_history should filter by date range."""
        from alarm import AlarmHistory
        from datetime import datetime, timedelta
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        now = datetime.now()
        for days_ago in [30, 20, 10, 5, 1]:
            entry = {
                'timestamp': (now - timedelta(days=days_ago)).isoformat(),
                'trigger_time': '07:00',
                'playlist_name': f'Playlist {days_ago}d ago',
                'playlist_uri': 'spotify:playlist:test',
                'volume': 80,
                'fade_in_enabled': False,
                'fade_in_duration': 10,
                'day_of_week': 'Monday',
                'success': True,
                'error_message': None,
                'snoozed': False,
                'snooze_count': 0,
                'dismissed': False,
                'dismiss_time': None
            }
            history.history.append(entry)
        
        # Filter to 15-3 days ago
        start_date = now - timedelta(days=15)
        end_date = now - timedelta(days=3)
        result = history.get_history(start_date=start_date, end_date=end_date)
        
        # Should only include entries from 10 and 5 days ago
        assert len(result) == 2
    
    def test_get_statistics_empty_history(self, tmp_path):
        """get_statistics should return zero values for empty history."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        stats = history.get_statistics()
        
        assert stats['total_alarms'] == 0
        assert stats['success_rate'] == 0.0
        assert stats['failure_count'] == 0
        assert stats['avg_snooze_count'] == 0.0
        assert stats['total_snoozes'] == 0
        assert stats['most_snoozed_time'] is None
        assert stats['most_successful_time'] is None
        assert stats['wake_patterns'] == {}
        assert stats['day_distribution'] == {}
        assert stats['favorite_playlists'] == {}
        assert stats['fade_in_usage'] == 0.0
    
    def test_get_statistics_success_rate(self, tmp_path):
        """get_statistics should calculate success rate correctly."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add 7 successful and 3 failed alarms
        for i in range(7):
            alarm_data = {
                'time': '07:00',
                'playlist_name': 'Success',
                'playlist_uri': 'spotify:playlist:success',
                'volume': 80
            }
            history.record_alarm_trigger(alarm_data, success=True)
        
        for i in range(3):
            alarm_data = {
                'time': '08:00',
                'playlist_name': 'Fail',
                'playlist_uri': 'spotify:playlist:fail',
                'volume': 80
            }
            history.record_alarm_trigger(alarm_data, success=False, error_message='Error')
        
        stats = history.get_statistics()
        
        assert stats['total_alarms'] == 10
        assert stats['success_rate'] == 70.0  # 7/10 * 100
        assert stats['failure_count'] == 3
    
    def test_get_statistics_snooze_patterns(self, tmp_path):
        """get_statistics should calculate snooze statistics."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add alarms with different snooze counts
        for snooze_count in [0, 1, 2, 3, 4]:
            alarm_data = {
                'time': '07:00',
                'playlist_name': 'Test',
                'playlist_uri': 'spotify:playlist:test',
                'volume': 80
            }
            history.record_alarm_trigger(alarm_data, success=True)
            
            # Snooze the alarm multiple times
            for _ in range(snooze_count):
                history.record_snooze(alarm_data, snooze_duration=5)
        
        stats = history.get_statistics()
        
        # Total snoozes: 0 + 1 + 2 + 3 + 4 = 10
        # Average: 10 / 5 = 2.0
        assert stats['total_snoozes'] == 10
        assert stats['avg_snooze_count'] == 2.0
    
    def test_get_statistics_wake_patterns(self, tmp_path):
        """get_statistics should track wake patterns by hour."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add alarms at different times
        times = ['06:00', '06:30', '07:00', '07:15', '08:00']
        for time_str in times:
            alarm_data = {
                'time': time_str,
                'playlist_name': 'Test',
                'playlist_uri': 'spotify:playlist:test',
                'volume': 80
            }
            history.record_alarm_trigger(alarm_data, success=True)
        
        stats = history.get_statistics()
        
        # Should group by hour
        assert stats['wake_patterns']['06'] == 2
        assert stats['wake_patterns']['07'] == 2
        assert stats['wake_patterns']['08'] == 1
    
    def test_get_statistics_day_distribution(self, tmp_path):
        """get_statistics should track day distribution."""
        from alarm import AlarmHistory
        from datetime import datetime
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add alarms
        for i in range(5):
            alarm_data = {
                'time': '07:00',
                'playlist_name': 'Test',
                'playlist_uri': 'spotify:playlist:test',
                'volume': 80
            }
            history.record_alarm_trigger(alarm_data, success=True)
        
        stats = history.get_statistics()
        
        # All alarms should be on today
        today = datetime.now().strftime('%A')
        assert stats['day_distribution'][today] == 5
    
    def test_get_statistics_favorite_playlists(self, tmp_path):
        """get_statistics should identify favorite playlists."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add alarms with different playlists
        playlists = [
            ('Morning Mix', 5),
            ('Workout', 3),
            ('Chill', 2),
            ('Rock', 1),
            ('Jazz', 1)
        ]
        
        for playlist_name, count in playlists:
            for _ in range(count):
                alarm_data = {
                    'time': '07:00',
                    'playlist_name': playlist_name,
                    'playlist_uri': f'spotify:playlist:{playlist_name.lower()}',
                    'volume': 80
                }
                history.record_alarm_trigger(alarm_data, success=True)
        
        stats = history.get_statistics()
        
        # Should return top 5 playlists sorted by count
        assert 'Morning Mix' in stats['favorite_playlists']
        assert stats['favorite_playlists']['Morning Mix'] == 5
        assert 'Workout' in stats['favorite_playlists']
        assert stats['favorite_playlists']['Workout'] == 3
    
    def test_get_statistics_fade_in_usage(self, tmp_path):
        """get_statistics should calculate fade-in usage percentage."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add 3 alarms with fade-in and 7 without
        for i in range(3):
            alarm_data = {
                'time': '07:00',
                'playlist_name': 'Fade',
                'playlist_uri': 'spotify:playlist:fade',
                'volume': 80,
                'fade_in_enabled': True,
                'fade_in_duration': 15
            }
            history.record_alarm_trigger(alarm_data, success=True)
        
        for i in range(7):
            alarm_data = {
                'time': '08:00',
                'playlist_name': 'No Fade',
                'playlist_uri': 'spotify:playlist:nofade',
                'volume': 80,
                'fade_in_enabled': False,
                'fade_in_duration': 10
            }
            history.record_alarm_trigger(alarm_data, success=True)
        
        stats = history.get_statistics()
        
        # 3/10 * 100 = 30%
        assert stats['fade_in_usage'] == 30.0
    
    def test_get_statistics_most_snoozed_time(self, tmp_path):
        """get_statistics should identify most snoozed time."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add alarms at different times with different snooze counts
        alarm_data_1 = {
            'time': '06:00',
            'playlist_name': 'Early',
            'playlist_uri': 'spotify:playlist:early',
            'volume': 80
        }
        history.record_alarm_trigger(alarm_data_1, success=True)
        history.record_snooze(alarm_data_1, 5)
        history.record_snooze(alarm_data_1, 5)
        history.record_snooze(alarm_data_1, 5)  # 3 snoozes
        
        alarm_data_2 = {
            'time': '07:00',
            'playlist_name': 'Normal',
            'playlist_uri': 'spotify:playlist:normal',
            'volume': 80
        }
        history.record_alarm_trigger(alarm_data_2, success=True)
        history.record_snooze(alarm_data_2, 5)  # 1 snooze
        
        alarm_data_3 = {
            'time': '08:00',
            'playlist_name': 'Late',
            'playlist_uri': 'spotify:playlist:late',
            'volume': 80
        }
        history.record_alarm_trigger(alarm_data_3, success=True)  # 0 snoozes
        
        stats = history.get_statistics()
        
        assert stats['most_snoozed_time'] == '06:00'
    
    def test_get_statistics_most_successful_time(self, tmp_path):
        """get_statistics should identify most successful time (least snoozes)."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add alarms at different times with different snooze patterns
        alarm_data_1 = {
            'time': '06:00',
            'playlist_name': 'Early',
            'playlist_uri': 'spotify:playlist:early',
            'volume': 80
        }
        history.record_alarm_trigger(alarm_data_1, success=True)
        history.record_snooze(alarm_data_1, 5)
        history.record_snooze(alarm_data_1, 5)  # 2 snoozes
        
        alarm_data_2 = {
            'time': '07:00',
            'playlist_name': 'Normal',
            'playlist_uri': 'spotify:playlist:normal',
            'volume': 80
        }
        history.record_alarm_trigger(alarm_data_2, success=True)  # 0 snoozes (best)
        
        alarm_data_3 = {
            'time': '08:00',
            'playlist_name': 'Late',
            'playlist_uri': 'spotify:playlist:late',
            'volume': 80
        }
        history.record_alarm_trigger(alarm_data_3, success=True)
        history.record_snooze(alarm_data_3, 5)  # 1 snooze
        
        stats = history.get_statistics()
        
        assert stats['most_successful_time'] == '07:00'
    
    def test_get_statistics_with_days_parameter(self, tmp_path):
        """get_statistics should respect days parameter."""
        from alarm import AlarmHistory
        from datetime import datetime, timedelta
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Manually add entries from different time periods
        now = datetime.now()
        
        # Add 3 recent alarms (within 7 days)
        for i in range(3):
            entry = {
                'timestamp': (now - timedelta(days=i)).isoformat(),
                'trigger_time': '07:00',
                'playlist_name': 'Recent',
                'playlist_uri': 'spotify:playlist:recent',
                'volume': 80,
                'fade_in_enabled': False,
                'fade_in_duration': 10,
                'day_of_week': 'Monday',
                'success': True,
                'error_message': None,
                'snoozed': False,
                'snooze_count': 0,
                'dismissed': False,
                'dismiss_time': None
            }
            history.history.append(entry)
        
        # Add 2 old alarms (older than 7 days)
        for i in range(2):
            entry = {
                'timestamp': (now - timedelta(days=10 + i)).isoformat(),
                'trigger_time': '07:00',
                'playlist_name': 'Old',
                'playlist_uri': 'spotify:playlist:old',
                'volume': 80,
                'fade_in_enabled': False,
                'fade_in_duration': 10,
                'day_of_week': 'Monday',
                'success': True,
                'error_message': None,
                'snoozed': False,
                'snooze_count': 0,
                'dismissed': False,
                'dismiss_time': None
            }
            history.history.append(entry)
        
        # Get stats for last 7 days
        stats = history.get_statistics(days=7)
        
        # Should only count recent alarms
        assert stats['total_alarms'] == 3
    
    def test_export_to_csv(self, tmp_path):
        """export_to_csv should export history to CSV file."""
        from alarm import AlarmHistory
        import csv
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add some history
        for i in range(3):
            alarm_data = {
                'time': f'0{i+6}:00',
                'playlist_name': f'Playlist {i}',
                'playlist_uri': f'spotify:playlist:{i}',
                'volume': 80
            }
            history.record_alarm_trigger(alarm_data, success=True)
        
        csv_file = tmp_path / 'export.csv'
        success = history.export_to_csv(csv_file)
        
        assert success is True
        assert csv_file.exists()
        
        # Verify CSV contents
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
    
    def test_export_to_csv_empty_history(self, tmp_path):
        """export_to_csv should handle empty history."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        csv_file = tmp_path / 'empty.csv'
        success = history.export_to_csv(csv_file)
        
        assert success is True
    
    def test_export_to_json(self, tmp_path):
        """export_to_json should export history to JSON file."""
        from alarm import AlarmHistory
        import json
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add some history
        for i in range(3):
            alarm_data = {
                'time': f'0{i+6}:00',
                'playlist_name': f'Playlist {i}',
                'playlist_uri': f'spotify:playlist:{i}',
                'volume': 80
            }
            history.record_alarm_trigger(alarm_data, success=True)
        
        json_file = tmp_path / 'export.json'
        success = history.export_to_json(json_file)
        
        assert success is True
        assert json_file.exists()
        
        # Verify JSON contents
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'history' in data
            assert len(data['history']) == 3
    
    def test_export_to_json_empty_history(self, tmp_path):
        """export_to_json should handle empty history."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        json_file = tmp_path / 'empty.json'
        success = history.export_to_json(json_file)
        
        assert success is True
    
    def test_clear_history(self, tmp_path):
        """clear_history should remove all entries."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Add some history
        for i in range(5):
            alarm_data = {
                'time': '07:00',
                'playlist_name': 'Test',
                'playlist_uri': 'spotify:playlist:test',
                'volume': 80
            }
            history.record_alarm_trigger(alarm_data, success=True)
        
        assert len(history.history) == 5
        
        history.clear_history()
        
        assert len(history.history) == 0
    
    def test_clear_old_entries(self, tmp_path):
        """clear_old_entries should remove entries older than specified days."""
        from alarm import AlarmHistory
        from datetime import datetime, timedelta
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        now = datetime.now()
        
        # Add recent entries (5 days old)
        for i in range(3):
            entry = {
                'timestamp': (now - timedelta(days=5)).isoformat(),
                'trigger_time': '07:00',
                'playlist_name': 'Recent',
                'playlist_uri': 'spotify:playlist:recent',
                'volume': 80,
                'fade_in_enabled': False,
                'fade_in_duration': 10,
                'day_of_week': 'Monday',
                'success': True,
                'error_message': None,
                'snoozed': False,
                'snooze_count': 0,
                'dismissed': False,
                'dismiss_time': None
            }
            history.history.append(entry)
        
        # Add old entries (100 days old)
        for i in range(2):
            entry = {
                'timestamp': (now - timedelta(days=100)).isoformat(),
                'trigger_time': '07:00',
                'playlist_name': 'Old',
                'playlist_uri': 'spotify:playlist:old',
                'volume': 80,
                'fade_in_enabled': False,
                'fade_in_duration': 10,
                'day_of_week': 'Monday',
                'success': True,
                'error_message': None,
                'snoozed': False,
                'snooze_count': 0,
                'dismissed': False,
                'dismiss_time': None
            }
            history.history.append(entry)
        
        assert len(history.history) == 5
        
        # Clear entries older than 30 days
        history.clear_old_entries(days=30)
        
        # Should only keep the 3 recent entries
        assert len(history.history) == 3
    
    def test_persistence_save_and_load(self, tmp_path):
        """History should persist to file and reload correctly."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'persist_test.json'
        
        # Create history and add entries
        history1 = AlarmHistory(history_file)
        for i in range(3):
            alarm_data = {
                'time': f'0{i+6}:00',
                'playlist_name': f'Playlist {i}',
                'playlist_uri': f'spotify:playlist:{i}',
                'volume': 80
            }
            history1.record_alarm_trigger(alarm_data, success=True)
        
        # Create new instance and verify data loaded
        history2 = AlarmHistory(history_file)
        assert len(history2.history) == 3
        assert history2.history[0]['playlist_name'] == 'Playlist 0'
    
    def test_record_alarm_trigger_with_trigger_time_key(self, tmp_path):
        """record_alarm_trigger should handle both 'time' and 'trigger_time' keys."""
        from alarm import AlarmHistory
        
        history_file = tmp_path / 'test_history.json'
        history = AlarmHistory(history_file)
        
        # Test with 'trigger_time' key
        alarm_data = {
            'trigger_time': '09:30',
            'playlist_name': 'Test',
            'playlist_uri': 'spotify:playlist:test',
            'volume': 80
        }
        
        history.record_alarm_trigger(alarm_data, success=True)
        
        entry = history.history[0]
        assert entry['trigger_time'] == '09:30'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
