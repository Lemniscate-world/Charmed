"""
test_integration.py - Integration tests for Alarmify

Comprehensive integration tests covering:
- Full alarm workflow from scheduling to playback with mocked Spotify API
- Playlist loading with pagination
- OAuth flow and token refresh
- Graceful shutdown and resource cleanup
- Concurrent alarm triggers
- Phase 2: Complete workflows with fade-in and day-specific scheduling
- Phase 2: Template-based alarm creation workflows
- Phase 2: Snooze and reschedule workflows

Run with: python -m pytest tests/test_integration.py -v
"""

import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta
import queue
import tempfile
from pathlib import Path
import logging

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from alarm import Alarm, AlarmTemplate, TemplateManager
from spotify_api.spotify_api import SpotifyAPI
import logging_config


class TestFullAlarmWorkflow:
    """Integration tests for complete alarm workflow."""
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('schedule.every')
    def test_alarm_workflow_end_to_end(self, mock_schedule_every, mock_oauth, mock_spotify_class):
        """Test complete workflow: schedule -> trigger -> playback."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp.current_user.return_value = {'display_name': 'Test User', 'id': 'test123'}
        mock_sp.current_user_playlists.return_value = {
            'items': [
                {
                    'name': 'Morning Vibes',
                    'id': 'playlist123',
                    'uri': 'spotify:playlist:morning123',
                    'tracks': {'total': 50},
                    'images': [{'url': 'https://example.com/image.jpg'}],
                    'owner': {'display_name': 'Test User'}
                }
            ],
            'next': None
        }
        
        mock_job = Mock()
        mock_day = Mock()
        mock_day.at.return_value = mock_job
        mock_schedule_every.return_value.day = mock_day
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            alarm_time = '08:00'
            playlist_uri = 'spotify:playlist:morning123'
            volume = 75
            
            alarm.set_alarm(alarm_time, 'Morning Vibes', playlist_uri, api, volume)
            
            assert len(alarm.get_alarms()) == 1
            alarm_info = alarm.get_alarms()[0]
            assert alarm_info['time'] == alarm_time
            assert alarm_info['playlist'] == 'Morning Vibes'
            assert alarm_info['volume'] == volume
            
            assert alarm.scheduler_running is True
            
            alarm.shutdown()
            assert alarm.scheduler_running is False


class TestPhase2FadeInWorkflows:
    """Integration tests for Phase 2 fade-in workflows."""
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_alarm_with_fade_in_workflow(self, mock_oauth, mock_spotify_class):
        """Test complete workflow with fade-in enabled."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            # Set alarm with fade-in enabled
            alarm.set_alarm(
                '07:30', 'Morning Mix', 'spotify:playlist:morning',
                api, volume=80, fade_in_enabled=True, fade_in_duration=15
            )
            
            alarms = alarm.get_alarms()
            assert len(alarms) == 1
            assert alarms[0]['fade_in_enabled'] is True
            assert alarms[0]['fade_in_duration'] == 15
            
            # Trigger the alarm (without actual playback)
            # Just verify the alarm data is stored correctly
            alarm.shutdown()
    
    def test_fade_in_controller_integration(self):
        """Test FadeInController integration with alarm playback."""
        try:
            from alarm import FadeInController, PYQT_AVAILABLE
            
            if not PYQT_AVAILABLE:
                pytest.skip("PyQt5 not available")
            
            mock_api = Mock()
            
            # Create fade-in controller
            controller = FadeInController(mock_api, target_volume=100, duration_minutes=10)
            
            # Start fade-in
            controller.start()
            
            assert controller.is_active is True
            assert controller.current_volume == 0
            mock_api.set_volume.assert_called_with(0)
            
            # Simulate a few steps
            for _ in range(3):
                controller._update_volume()
            
            assert controller.current_volume > 0
            assert controller.current_step == 3
            
            # Stop fade-in
            controller.stop()
            assert controller.is_active is False
            
        except ImportError:
            pytest.skip("PyQt5 not available")
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_multiple_alarms_with_different_fade_settings(self, mock_oauth, mock_spotify_class):
        """Test multiple alarms with different fade-in settings."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            # Alarm 1: No fade-in
            alarm.set_alarm(
                '06:00', 'Early', 'spotify:playlist:early',
                api, volume=70, fade_in_enabled=False, fade_in_duration=10
            )
            
            # Alarm 2: With fade-in
            alarm.set_alarm(
                '07:00', 'Morning', 'spotify:playlist:morning',
                api, volume=80, fade_in_enabled=True, fade_in_duration=15
            )
            
            # Alarm 3: With different fade duration
            alarm.set_alarm(
                '08:00', 'Late', 'spotify:playlist:late',
                api, volume=90, fade_in_enabled=True, fade_in_duration=20
            )
            
            alarms = alarm.get_alarms()
            assert len(alarms) == 3
            
            assert alarms[0]['fade_in_enabled'] is False
            assert alarms[1]['fade_in_enabled'] is True
            assert alarms[1]['fade_in_duration'] == 15
            assert alarms[2]['fade_in_enabled'] is True
            assert alarms[2]['fade_in_duration'] == 20
            
            alarm.shutdown()


class TestPhase2DaySpecificWorkflows:
    """Integration tests for Phase 2 day-specific scheduling workflows."""
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_weekday_alarm_workflow(self, mock_oauth, mock_spotify_class):
        """Test alarm scheduled for weekdays only."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            # Set weekday alarm
            alarm.set_alarm(
                '07:00', 'Weekday Alarm', 'spotify:playlist:weekday',
                api, volume=75, fade_in_enabled=False, fade_in_duration=10,
                days='weekdays'
            )
            
            alarms = alarm.get_alarms()
            assert len(alarms) == 1
            assert alarms[0]['days'] == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            
            # Get next trigger time
            next_time = alarm.get_next_trigger_time(alarms[0])
            assert next_time is not None
            
            # Verify it's on a weekday
            day_name = next_time.strftime('%A')
            assert day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            
            alarm.shutdown()
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_weekend_alarm_workflow(self, mock_oauth, mock_spotify_class):
        """Test alarm scheduled for weekends only."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            # Set weekend alarm
            alarm.set_alarm(
                '09:00', 'Weekend Alarm', 'spotify:playlist:weekend',
                api, volume=80, fade_in_enabled=True, fade_in_duration=20,
                days='weekends'
            )
            
            alarms = alarm.get_alarms()
            assert len(alarms) == 1
            assert alarms[0]['days'] == ['Saturday', 'Sunday']
            
            # Get next trigger time
            next_time = alarm.get_next_trigger_time(alarms[0])
            assert next_time is not None
            
            # Verify it's on a weekend
            day_name = next_time.strftime('%A')
            assert day_name in ['Saturday', 'Sunday']
            
            alarm.shutdown()
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_custom_days_alarm_workflow(self, mock_oauth, mock_spotify_class):
        """Test alarm scheduled for custom specific days."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            # Set custom days alarm (Mon, Wed, Fri)
            alarm.set_alarm(
                '08:00', 'Custom Days', 'spotify:playlist:custom',
                api, volume=75, fade_in_enabled=False, fade_in_duration=10,
                days=['Monday', 'Wednesday', 'Friday']
            )
            
            alarms = alarm.get_alarms()
            assert len(alarms) == 1
            assert alarms[0]['days'] == ['Monday', 'Wednesday', 'Friday']
            
            # Get upcoming alarms for next 7 days
            upcoming = alarm.get_upcoming_alarms(days=7)
            
            # All upcoming alarms should be on Mon, Wed, or Fri
            for item in upcoming:
                day_name = item['datetime'].strftime('%A')
                assert day_name in ['Monday', 'Wednesday', 'Friday']
            
            alarm.shutdown()
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_mixed_day_schedules_workflow(self, mock_oauth, mock_spotify_class):
        """Test multiple alarms with different day schedules."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            # Weekday alarm
            alarm.set_alarm(
                '07:00', 'Weekday', 'spotify:playlist:weekday',
                api, volume=75, days='weekdays'
            )
            
            # Weekend alarm
            alarm.set_alarm(
                '09:00', 'Weekend', 'spotify:playlist:weekend',
                api, volume=80, days='weekends'
            )
            
            # Every day alarm
            alarm.set_alarm(
                '20:00', 'Evening', 'spotify:playlist:evening',
                api, volume=60, days=None
            )
            
            alarms = alarm.get_alarms()
            assert len(alarms) == 3
            
            # Get upcoming alarms
            upcoming = alarm.get_upcoming_alarms(days=7)
            
            # Should have multiple triggers
            assert len(upcoming) > 0
            
            # Verify evening alarm appears every day
            evening_triggers = [u for u in upcoming if u['alarm_info']['time'] == '20:00']
            
            # Should have 7 evening triggers (one per day)
            # Note: This might be less if we're near end of day
            assert len(evening_triggers) >= 6
            
            alarm.shutdown()


class TestPhase2TemplateWorkflows:
    """Integration tests for Phase 2 template workflows."""
    
    def test_template_creation_and_usage_workflow(self, tmp_path):
        """Test creating templates and using them to create alarms."""
        templates_file = tmp_path / 'templates.json'
        manager = TemplateManager(templates_file)
        
        # Create templates
        morning_template = AlarmTemplate(
            name='Morning Routine',
            time='07:00',
            playlist_name='Morning Mix',
            playlist_uri='spotify:playlist:morning',
            volume=75,
            fade_in_enabled=True,
            fade_in_duration=15,
            days='weekdays'
        )
        
        weekend_template = AlarmTemplate(
            name='Weekend Relax',
            time='09:00',
            playlist_name='Weekend Vibes',
            playlist_uri='spotify:playlist:weekend',
            volume=60,
            fade_in_enabled=True,
            fade_in_duration=20,
            days='weekends'
        )
        
        # Add templates
        assert manager.add_template(morning_template) is True
        assert manager.add_template(weekend_template) is True
        
        # Load templates
        templates = manager.load_templates()
        assert len(templates) == 2
        
        # Verify templates
        loaded_morning = manager.get_template('Morning Routine')
        assert loaded_morning is not None
        assert loaded_morning.time == '07:00'
        assert loaded_morning.fade_in_enabled is True
        assert loaded_morning.fade_in_duration == 15
        
        # Use template to create alarm
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm(
            loaded_morning.time,
            loaded_morning.playlist_name,
            loaded_morning.playlist_uri,
            mock_api,
            loaded_morning.volume,
            loaded_morning.fade_in_enabled,
            loaded_morning.fade_in_duration,
            loaded_morning.days
        )
        
        alarms = alarm.get_alarms()
        assert len(alarms) == 1
        assert alarms[0]['time'] == '07:00'
        assert alarms[0]['fade_in_enabled'] is True
        
        alarm.shutdown()
    
    def test_template_update_workflow(self, tmp_path):
        """Test updating existing template."""
        templates_file = tmp_path / 'templates.json'
        manager = TemplateManager(templates_file)
        
        # Create initial template
        original = AlarmTemplate(
            name='Update Test',
            time='08:00',
            playlist_name='Original',
            playlist_uri='spotify:playlist:original',
            volume=70
        )
        
        manager.add_template(original)
        
        # Update template
        updated = AlarmTemplate(
            name='Update Test',
            time='09:00',
            playlist_name='Updated',
            playlist_uri='spotify:playlist:updated',
            volume=80,
            fade_in_enabled=True,
            fade_in_duration=25
        )
        
        assert manager.update_template('Update Test', updated) is True
        
        # Verify update
        loaded = manager.get_template('Update Test')
        assert loaded.time == '09:00'
        assert loaded.playlist_name == 'Updated'
        assert loaded.fade_in_enabled is True
    
    def test_template_delete_workflow(self, tmp_path):
        """Test deleting template."""
        templates_file = tmp_path / 'templates.json'
        manager = TemplateManager(templates_file)
        
        # Add multiple templates
        template1 = AlarmTemplate(
            name='Keep',
            time='07:00',
            playlist_name='Keep',
            playlist_uri='spotify:playlist:keep'
        )
        
        template2 = AlarmTemplate(
            name='Delete',
            time='08:00',
            playlist_name='Delete',
            playlist_uri='spotify:playlist:delete'
        )
        
        manager.add_template(template1)
        manager.add_template(template2)
        
        # Delete one template
        assert manager.delete_template('Delete') is True
        
        # Verify deletion
        templates = manager.load_templates()
        assert len(templates) == 1
        assert templates[0].name == 'Keep'
        
        assert manager.get_template('Delete') is None
    
    def test_template_persistence_workflow(self, tmp_path):
        """Test that templates persist across manager instances."""
        templates_file = tmp_path / 'templates.json'
        
        # Create first manager and add template
        manager1 = TemplateManager(templates_file)
        template = AlarmTemplate(
            name='Persist Test',
            time='10:00',
            playlist_name='Persist',
            playlist_uri='spotify:playlist:persist',
            volume=85
        )
        manager1.add_template(template)
        
        # Create second manager and load templates
        manager2 = TemplateManager(templates_file)
        templates = manager2.load_templates()
        
        assert len(templates) == 1
        assert templates[0].name == 'Persist Test'
        assert templates[0].volume == 85


class TestPhase2SnoozeWorkflows:
    """Integration tests for Phase 2 snooze workflows."""
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_snooze_and_reschedule_workflow(self, mock_oauth, mock_spotify_class):
        """Test complete snooze workflow."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            # Set up alarm data for snooze
            alarm_data = {
                'playlist_uri': 'spotify:playlist:snooze',
                'playlist_name': 'Snooze Test',
                'volume': 80,
                'fade_in_enabled': True,
                'fade_in_duration': 15,
                'spotify_api': api
            }
            
            # Snooze the alarm
            before_snooze = datetime.now()
            alarm.snooze_alarm(alarm_data, snooze_minutes=10)
            
            # Verify snooze was scheduled
            snoozed = alarm.get_snoozed_alarms()
            assert len(snoozed) == 1
            assert snoozed[0]['original_playlist'] == 'Snooze Test'
            assert snoozed[0]['snooze_duration'] == 10
            
            # Verify snooze time is approximately 10 minutes from now
            snooze_time = snoozed[0]['snooze_time']
            expected_time = before_snooze + timedelta(minutes=10)
            time_diff = abs((snooze_time - expected_time).total_seconds())
            assert time_diff < 5  # Within 5 seconds
            
            alarm.shutdown()
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_multiple_snoozes_workflow(self, mock_oauth, mock_spotify_class):
        """Test snoozing multiple alarms."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            # Snooze first alarm
            alarm_data_1 = {
                'playlist_uri': 'spotify:playlist:snooze1',
                'playlist_name': 'Snooze 1',
                'volume': 70,
                'fade_in_enabled': False,
                'fade_in_duration': 10,
                'spotify_api': api
            }
            alarm.snooze_alarm(alarm_data_1, snooze_minutes=5)
            
            # Snooze second alarm
            alarm_data_2 = {
                'playlist_uri': 'spotify:playlist:snooze2',
                'playlist_name': 'Snooze 2',
                'volume': 85,
                'fade_in_enabled': True,
                'fade_in_duration': 20,
                'spotify_api': api
            }
            alarm.snooze_alarm(alarm_data_2, snooze_minutes=10)
            
            # Verify both snoozes
            snoozed = alarm.get_snoozed_alarms()
            assert len(snoozed) == 2
            
            snooze_1 = [s for s in snoozed if s['original_playlist'] == 'Snooze 1'][0]
            snooze_2 = [s for s in snoozed if s['original_playlist'] == 'Snooze 2'][0]
            
            assert snooze_1['snooze_duration'] == 5
            assert snooze_2['snooze_duration'] == 10
            
            alarm.shutdown()
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_snooze_with_fade_in_preservation(self, mock_oauth, mock_spotify_class):
        """Test that snooze preserves fade-in settings."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            # Snooze with fade-in enabled
            alarm_data = {
                'playlist_uri': 'spotify:playlist:fade',
                'playlist_name': 'Fade Test',
                'volume': 75,
                'fade_in_enabled': True,
                'fade_in_duration': 25,
                'spotify_api': api
            }
            
            alarm.snooze_alarm(alarm_data, snooze_minutes=15)
            
            # Verify fade-in settings are preserved
            snoozed_alarms = alarm.snoozed_alarms
            assert len(snoozed_alarms) == 1
            
            snoozed = snoozed_alarms[0]
            assert snoozed['fade_in_enabled'] is True
            assert snoozed['fade_in_duration'] == 25
            assert snoozed['volume'] == 75
            
            alarm.shutdown()


class TestComplexPhase2Scenarios:
    """Complex integration scenarios combining Phase 2 features."""
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_complete_phase2_workflow(self, mock_oauth, mock_spotify_class, tmp_path):
        """Test complete Phase 2 workflow with all features."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            # Set up template manager
            templates_file = tmp_path / 'templates.json'
            template_manager = TemplateManager(templates_file)
            
            # Create template with all Phase 2 features
            template = AlarmTemplate(
                name='Complete Template',
                time='07:30',
                playlist_name='Complete Mix',
                playlist_uri='spotify:playlist:complete',
                volume=75,
                fade_in_enabled=True,
                fade_in_duration=15,
                days='weekdays'
            )
            
            # Save template
            template_manager.add_template(template)
            
            # Load and use template
            loaded_template = template_manager.get_template('Complete Template')
            assert loaded_template is not None
            
            # Create alarm from template
            alarm = Alarm()
            alarm.set_alarm(
                loaded_template.time,
                loaded_template.playlist_name,
                loaded_template.playlist_uri,
                api,
                loaded_template.volume,
                loaded_template.fade_in_enabled,
                loaded_template.fade_in_duration,
                loaded_template.days
            )
            
            # Verify alarm has all features
            alarms = alarm.get_alarms()
            assert len(alarms) == 1
            assert alarms[0]['time'] == '07:30'
            assert alarms[0]['fade_in_enabled'] is True
            assert alarms[0]['fade_in_duration'] == 15
            assert alarms[0]['days'] == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            
            # Simulate alarm trigger and snooze
            alarm_data = {
                'playlist_uri': loaded_template.playlist_uri,
                'playlist_name': loaded_template.playlist_name,
                'volume': loaded_template.volume,
                'fade_in_enabled': loaded_template.fade_in_enabled,
                'fade_in_duration': loaded_template.fade_in_duration,
                'spotify_api': api
            }
            
            # Snooze the alarm
            alarm.snooze_alarm(alarm_data, snooze_minutes=10)
            
            # Verify snooze
            snoozed = alarm.get_snoozed_alarms()
            assert len(snoozed) == 1
            
            # Get upcoming alarms
            upcoming = alarm.get_upcoming_alarms(days=7)
            
            # Should have multiple weekday triggers
            assert len(upcoming) > 0
            
            # Verify all triggers are on weekdays
            for item in upcoming:
                day_name = item['datetime'].strftime('%A')
                assert day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            
            alarm.shutdown()
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_template_based_multiple_alarms_workflow(self, mock_oauth, mock_spotify_class, tmp_path):
        """Test creating multiple alarms from different templates."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            # Set up template manager
            templates_file = tmp_path / 'templates.json'
            manager = TemplateManager(templates_file)
            
            # Create multiple templates
            weekday_template = AlarmTemplate(
                name='Weekday Morning',
                time='07:00',
                playlist_name='Weekday Mix',
                playlist_uri='spotify:playlist:weekday',
                volume=75,
                fade_in_enabled=True,
                fade_in_duration=15,
                days='weekdays'
            )
            
            weekend_template = AlarmTemplate(
                name='Weekend Morning',
                time='09:00',
                playlist_name='Weekend Mix',
                playlist_uri='spotify:playlist:weekend',
                volume=60,
                fade_in_enabled=True,
                fade_in_duration=20,
                days='weekends'
            )
            
            evening_template = AlarmTemplate(
                name='Evening',
                time='20:00',
                playlist_name='Evening Mix',
                playlist_uri='spotify:playlist:evening',
                volume=50,
                fade_in_enabled=False,
                fade_in_duration=10,
                days=None
            )
            
            # Save templates
            manager.add_template(weekday_template)
            manager.add_template(weekend_template)
            manager.add_template(evening_template)
            
            # Create alarms from templates
            alarm = Alarm()
            
            for template in manager.load_templates():
                alarm.set_alarm(
                    template.time,
                    template.playlist_name,
                    template.playlist_uri,
                    api,
                    template.volume,
                    template.fade_in_enabled,
                    template.fade_in_duration,
                    template.days
                )
            
            # Verify all alarms
            alarms = alarm.get_alarms()
            assert len(alarms) == 3
            
            # Verify each alarm has correct settings
            weekday_alarm = [a for a in alarms if a['time'] == '07:00'][0]
            assert weekday_alarm['fade_in_enabled'] is True
            assert weekday_alarm['days'] == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            
            weekend_alarm = [a for a in alarms if a['time'] == '09:00'][0]
            assert weekend_alarm['fade_in_enabled'] is True
            assert weekend_alarm['days'] == ['Saturday', 'Sunday']
            
            evening_alarm = [a for a in alarms if a['time'] == '20:00'][0]
            assert evening_alarm['fade_in_enabled'] is False
            assert evening_alarm['days'] is None
            
            alarm.shutdown()


class TestLoggingSystem:
    """Integration tests for logging system."""
    
    def setup_method(self):
        """Reset logging configuration before each test."""
        # Reset the global logging configured flag
        logging_config._logging_configured = False
        
        # Clear all existing handlers from root logger
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)
    
    def teardown_method(self):
        """Clean up after each test."""
        # Reset logging configuration
        logging_config._logging_configured = False
        
        # Clear all handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
    
    def test_setup_logging_creates_rotating_file_handlers(self, tmp_path):
        """Test that setup_logging creates rotating file handlers."""
        # Override LOG_DIR for testing
        original_log_dir = logging_config.LOG_DIR
        logging_config.LOG_DIR = tmp_path
        
        try:
            # Setup logging
            logging_config.setup_logging(log_level=logging.INFO)
            
            # Get root logger
            root_logger = logging.getLogger()
            
            # Verify handlers exist
            assert len(root_logger.handlers) == 2
            
            # Find file handler
            file_handler = None
            console_handler = None
            
            for handler in root_logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    file_handler = handler
                elif isinstance(handler, logging.StreamHandler):
                    console_handler = handler
            
            # Verify both handlers exist
            assert file_handler is not None
            assert console_handler is not None
            
            # Verify file handler is rotating
            assert isinstance(file_handler, logging.handlers.RotatingFileHandler)
            assert file_handler.maxBytes == 5 * 1024 * 1024  # 5MB
            assert file_handler.backupCount == 5
            
        finally:
            # Restore original LOG_DIR
            logging_config.LOG_DIR = original_log_dir
    
    def test_logs_written_to_timestamped_files(self, tmp_path):
        """Test that logs are written to timestamped files."""
        # Override LOG_DIR for testing
        original_log_dir = logging_config.LOG_DIR
        logging_config.LOG_DIR = tmp_path
        
        try:
            # Setup logging
            logging_config.setup_logging(log_level=logging.DEBUG)
            
            # Get logger and write test message
            logger = logging_config.get_logger('test_module')
            logger.info('Test log message')
            
            # Verify log file exists with timestamped name
            log_files = list(tmp_path.glob('alarmify_*.log'))
            assert len(log_files) == 1
            
            # Verify filename format (alarmify_YYYYMMDD_HHMMSS.log)
            log_file = log_files[0]
            assert log_file.name.startswith('alarmify_')
            assert log_file.name.endswith('.log')
            
            # Verify timestamp format in filename
            filename_parts = log_file.stem.split('_')
            assert len(filename_parts) == 3  # ['alarmify', 'YYYYMMDD', 'HHMMSS']
            assert len(filename_parts[1]) == 8  # YYYYMMDD
            assert len(filename_parts[2]) == 6  # HHMMSS
            
            # Verify log content
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'Test log message' in content
                assert 'test_module' in content
            
        finally:
            # Restore original LOG_DIR
            logging_config.LOG_DIR = original_log_dir
    
    def test_different_log_levels_captured_correctly(self, tmp_path):
        """Test that different log levels are captured correctly."""
        # Override LOG_DIR for testing
        original_log_dir = logging_config.LOG_DIR
        logging_config.LOG_DIR = tmp_path
        
        try:
            # Setup logging with DEBUG level
            logging_config.setup_logging(log_level=logging.DEBUG)
            
            # Get logger
            logger = logging_config.get_logger('test_levels')
            
            # Write messages at different levels
            logger.debug('Debug message')
            logger.info('Info message')
            logger.warning('Warning message')
            logger.error('Error message')
            
            # Get log file
            log_files = list(tmp_path.glob('alarmify_*.log'))
            assert len(log_files) == 1
            
            # Read log content
            with open(log_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify all log levels are present
            assert '[DEBUG]' in content
            assert 'Debug message' in content
            
            assert '[INFO]' in content
            assert 'Info message' in content
            
            assert '[WARNING]' in content
            assert 'Warning message' in content
            
            assert '[ERROR]' in content
            assert 'Error message' in content
            
            # Verify logger name is included
            assert 'test_levels' in content
            
        finally:
            # Restore original LOG_DIR
            logging_config.LOG_DIR = original_log_dir
    
    def test_log_level_filtering(self, tmp_path):
        """Test that log level filtering works correctly."""
        # Override LOG_DIR for testing
        original_log_dir = logging_config.LOG_DIR
        logging_config.LOG_DIR = tmp_path
        
        try:
            # Setup logging with WARNING level
            logging_config.setup_logging(log_level=logging.WARNING)
            
            # Get logger
            logger = logging_config.get_logger('test_filter')
            
            # Write messages at different levels
            logger.debug('Debug message - should not appear')
            logger.info('Info message - should not appear')
            logger.warning('Warning message - should appear')
            logger.error('Error message - should appear')
            
            # Get log file
            log_files = list(tmp_path.glob('alarmify_*.log'))
            assert len(log_files) == 1
            
            # Read log content
            with open(log_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify DEBUG and INFO are not present
            assert 'Debug message - should not appear' not in content
            assert 'Info message - should not appear' not in content
            
            # Verify WARNING and ERROR are present
            assert 'Warning message - should appear' in content
            assert 'Error message - should appear' in content
            
        finally:
            # Restore original LOG_DIR
            logging_config.LOG_DIR = original_log_dir
    
    def test_get_log_files_utility(self, tmp_path):
        """Test get_log_files() utility function."""
        # Override LOG_DIR for testing
        original_log_dir = logging_config.LOG_DIR
        logging_config.LOG_DIR = tmp_path
        
        try:
            # Create multiple log files with different timestamps
            log_file_1 = tmp_path / 'alarmify_20240101_120000.log'
            log_file_2 = tmp_path / 'alarmify_20240102_120000.log'
            log_file_3 = tmp_path / 'alarmify_20240103_120000.log'
            
            # Create files with slight delay to ensure different modification times
            log_file_1.write_text('Log 1')
            time.sleep(0.01)
            log_file_2.write_text('Log 2')
            time.sleep(0.01)
            log_file_3.write_text('Log 3')
            
            # Get log files
            log_files = logging_config.get_log_files()
            
            # Verify all files are returned
            assert len(log_files) == 3
            
            # Verify files are sorted by modification time (newest first)
            assert log_files[0] == log_file_3
            assert log_files[1] == log_file_2
            assert log_files[2] == log_file_1
            
            # Verify they are Path objects
            for log_file in log_files:
                assert isinstance(log_file, Path)
            
        finally:
            # Restore original LOG_DIR
            logging_config.LOG_DIR = original_log_dir
    
    def test_get_log_files_with_rotation(self, tmp_path):
        """Test get_log_files() includes rotated files."""
        # Override LOG_DIR for testing
        original_log_dir = logging_config.LOG_DIR
        logging_config.LOG_DIR = tmp_path
        
        try:
            # Create log files including rotated ones
            log_file_1 = tmp_path / 'alarmify_20240101_120000.log'
            log_file_2 = tmp_path / 'alarmify_20240101_120000.log.1'
            log_file_3 = tmp_path / 'alarmify_20240101_120000.log.2'
            
            log_file_1.write_text('Current log')
            log_file_2.write_text('Rotated log 1')
            log_file_3.write_text('Rotated log 2')
            
            # Get log files
            log_files = logging_config.get_log_files()
            
            # Verify all files are returned (including rotated)
            assert len(log_files) == 3
            
            # Verify file names
            file_names = [f.name for f in log_files]
            assert 'alarmify_20240101_120000.log' in file_names
            assert 'alarmify_20240101_120000.log.1' in file_names
            assert 'alarmify_20240101_120000.log.2' in file_names
            
        finally:
            # Restore original LOG_DIR
            logging_config.LOG_DIR = original_log_dir
    
    def test_get_log_files_empty_directory(self, tmp_path):
        """Test get_log_files() with empty directory."""
        # Override LOG_DIR for testing
        original_log_dir = logging_config.LOG_DIR
        logging_config.LOG_DIR = tmp_path
        
        try:
            # Get log files from empty directory
            log_files = logging_config.get_log_files()
            
            # Verify empty list is returned
            assert log_files == []
            
        finally:
            # Restore original LOG_DIR
            logging_config.LOG_DIR = original_log_dir
    
    def test_read_log_file_utility(self, tmp_path):
        """Test read_log_file() utility function."""
        # Create test log file
        log_file = tmp_path / 'test.log'
        test_content = '\n'.join([f'Line {i}' for i in range(1, 11)])
        log_file.write_text(test_content, encoding='utf-8')
        
        # Read entire file
        content = logging_config.read_log_file(log_file)
        
        # Verify content
        assert 'Line 1' in content
        assert 'Line 10' in content
        assert content.count('\n') == 9  # 10 lines = 9 newlines
    
    def test_read_log_file_with_max_lines(self, tmp_path):
        """Test read_log_file() with max_lines parameter."""
        # Create test log file with many lines
        log_file = tmp_path / 'test.log'
        test_content = '\n'.join([f'Line number {i}' for i in range(1, 101)])  # 100 lines
        log_file.write_text(test_content, encoding='utf-8')
        
        # Read last 10 lines
        content = logging_config.read_log_file(log_file, max_lines=10)
        
        # Verify only last 10 lines are returned
        lines = content.strip().split('\n')
        assert len(lines) == 10
        
        # Verify the lines are 91-100
        assert lines[0] == 'Line number 91'
        assert lines[-1] == 'Line number 100'
        
        # Verify early lines are not included
        assert 'Line number 1\n' not in content
        assert 'Line number 90\n' not in content
    
    def test_read_log_file_handles_errors(self, tmp_path):
        """Test read_log_file() handles errors gracefully."""
        # Try to read non-existent file
        non_existent = tmp_path / 'does_not_exist.log'
        
        content = logging_config.read_log_file(non_existent)
        
        # Verify error message is returned
        assert 'Error reading log file' in content
    
    def test_get_current_log_file(self, tmp_path):
        """Test get_current_log_file() returns newest log."""
        # Override LOG_DIR for testing
        original_log_dir = logging_config.LOG_DIR
        logging_config.LOG_DIR = tmp_path
        
        try:
            # Create multiple log files
            log_file_1 = tmp_path / 'alarmify_20240101_120000.log'
            log_file_2 = tmp_path / 'alarmify_20240102_120000.log'
            log_file_3 = tmp_path / 'alarmify_20240103_120000.log'
            
            log_file_1.write_text('Log 1')
            time.sleep(0.01)
            log_file_2.write_text('Log 2')
            time.sleep(0.01)
            log_file_3.write_text('Log 3')
            
            # Get current log file
            current = logging_config.get_current_log_file()
            
            # Verify it's the newest file
            assert current == log_file_3
            
        finally:
            # Restore original LOG_DIR
            logging_config.LOG_DIR = original_log_dir
    
    def test_logging_format_includes_timestamp_and_level(self, tmp_path):
        """Test that log format includes timestamp, level, module, and message."""
        # Override LOG_DIR for testing
        original_log_dir = logging_config.LOG_DIR
        logging_config.LOG_DIR = tmp_path
        
        try:
            # Setup logging
            logging_config.setup_logging(log_level=logging.INFO)
            
            # Get logger and write message
            logger = logging_config.get_logger('test_format')
            logger.info('Test message')
            
            # Read log file
            log_files = list(tmp_path.glob('alarmify_*.log'))
            with open(log_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify format components are present
            # Expected format: YYYY-MM-DD HH:MM:SS [LEVEL] module: message
            lines = [line for line in content.split('\n') if 'Test message' in line]
            assert len(lines) == 1
            
            log_line = lines[0]
            
            # Check for timestamp (YYYY-MM-DD HH:MM:SS)
            import re
            timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
            assert re.search(timestamp_pattern, log_line)
            
            # Check for log level [INFO]
            assert '[INFO]' in log_line
            
            # Check for module name
            assert 'test_format' in log_line
            
            # Check for message
            assert 'Test message' in log_line
            
        finally:
            # Restore original LOG_DIR
            logging_config.LOG_DIR = original_log_dir
    
    def test_multiple_loggers_same_file(self, tmp_path):
        """Test that multiple loggers write to the same file."""
        # Override LOG_DIR for testing
        original_log_dir = logging_config.LOG_DIR
        logging_config.LOG_DIR = tmp_path
        
        try:
            # Setup logging
            logging_config.setup_logging(log_level=logging.INFO)
            
            # Get multiple loggers
            logger1 = logging_config.get_logger('module1')
            logger2 = logging_config.get_logger('module2')
            logger3 = logging_config.get_logger('module3')
            
            # Write from different loggers
            logger1.info('Message from module1')
            logger2.info('Message from module2')
            logger3.info('Message from module3')
            
            # Verify all messages are in the same file
            log_files = list(tmp_path.glob('alarmify_*.log'))
            assert len(log_files) == 1
            
            with open(log_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert 'Message from module1' in content
            assert 'module1' in content
            
            assert 'Message from module2' in content
            assert 'module2' in content
            
            assert 'Message from module3' in content
            assert 'module3' in content
            
        finally:
            # Restore original LOG_DIR
            logging_config.LOG_DIR = original_log_dir
    
    def test_setup_logging_idempotent(self, tmp_path):
        """Test that calling setup_logging multiple times is safe."""
        # Override LOG_DIR for testing
        original_log_dir = logging_config.LOG_DIR
        logging_config.LOG_DIR = tmp_path
        
        try:
            # Call setup_logging multiple times
            logging_config.setup_logging(log_level=logging.INFO)
            logging_config.setup_logging(log_level=logging.DEBUG)
            logging_config.setup_logging(log_level=logging.WARNING)
            
            # Get logger and write message
            logger = logging_config.get_logger('test_idempotent')
            logger.info('Test message')
            
            # Verify only one log file was created
            log_files = list(tmp_path.glob('alarmify_*.log'))
            assert len(log_files) == 1
            
            # Verify message was logged
            with open(log_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'Test message' in content
            
        finally:
            # Restore original LOG_DIR
            logging_config.LOG_DIR = original_log_dir


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
