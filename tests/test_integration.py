"""
test_integration.py - Integration tests for Alarmify

Comprehensive integration tests covering:
- Full alarm workflow from scheduling to playback with mocked Spotify API
- Playlist loading with pagination
- OAuth flow and token refresh
- Graceful shutdown and resource cleanup
- Concurrent alarm triggers

Run with: python -m pytest tests/test_integration.py -v
"""

import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta
import queue

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alarm import Alarm
from spotify_api.spotify_api import SpotifyAPI


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
            
            job_func = mock_day.at.call_args[1]['do'] if 'do' in mock_day.at.call_args[1] else None
            if job_func is None:
                job_func = alarm.play_playlist
            
            job_func(playlist_uri, api, volume)
            
            mock_sp.volume.assert_called_once_with(volume)
            mock_sp.start_playback.assert_called_once_with(context_uri=playlist_uri)
            
            alarm.shutdown()
            assert alarm.scheduler_running is False
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_alarm_playback_with_volume_failure(self, mock_oauth, mock_spotify_class):
        """Test alarm continues playback even if volume setting fails."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp.volume.side_effect = Exception("No active device")
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            alarm.play_playlist('spotify:playlist:test123', api, 80)
            
            mock_sp.start_playback.assert_called_once()
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_multiple_alarms_workflow(self, mock_oauth, mock_spotify_class):
        """Test scheduling and managing multiple alarms."""
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
            
            alarms_config = [
                ('06:00', 'Morning Playlist', 'spotify:playlist:morning', 70),
                ('12:00', 'Lunch Playlist', 'spotify:playlist:lunch', 50),
                ('18:00', 'Evening Playlist', 'spotify:playlist:evening', 60),
            ]
            
            for time_str, name, uri, vol in alarms_config:
                alarm.set_alarm(time_str, name, uri, api, vol)
            
            alarms = alarm.get_alarms()
            assert len(alarms) == 3
            
            alarm.remove_alarm('12:00')
            alarms = alarm.get_alarms()
            assert len(alarms) == 2
            assert all(a['time'] != '12:00' for a in alarms)
            
            alarm.clear_all_alarms()
            assert len(alarm.get_alarms()) == 0
            
            alarm.shutdown()


class TestPlaylistLoadingPagination:
    """Integration tests for playlist loading with pagination."""
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_playlist_pagination_single_page(self, mock_oauth, mock_spotify_class):
        """Test loading playlists when all fit in one page."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        playlists_data = []
        for i in range(10):
            playlists_data.append({
                'name': f'Playlist {i}',
                'id': f'id{i}',
                'uri': f'spotify:playlist:id{i}',
                'tracks': {'total': 20 + i},
                'images': [{'url': f'https://example.com/img{i}.jpg'}],
                'owner': {'display_name': 'Test User'}
            })
        
        mock_sp.current_user_playlists.return_value = {
            'items': playlists_data,
            'next': None
        }
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            playlists = api.get_playlists_detailed()
            
            assert len(playlists) == 10
            for i, playlist in enumerate(playlists):
                assert playlist['name'] == f'Playlist {i}'
                assert playlist['track_count'] == 20 + i
                assert playlist['image_url'] == f'https://example.com/img{i}.jpg'
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_playlist_pagination_multiple_pages(self, mock_oauth, mock_spotify_class):
        """Test loading playlists across multiple pages."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        page1_data = []
        for i in range(50):
            page1_data.append({
                'name': f'Playlist {i}',
                'id': f'id{i}',
                'uri': f'spotify:playlist:id{i}',
                'tracks': {'total': 30},
                'images': [{'url': f'https://example.com/img{i}.jpg'}],
                'owner': {'display_name': 'User A'}
            })
        
        page2_data = []
        for i in range(50, 75):
            page2_data.append({
                'name': f'Playlist {i}',
                'id': f'id{i}',
                'uri': f'spotify:playlist:id{i}',
                'tracks': {'total': 25},
                'images': [{'url': f'https://example.com/img{i}.jpg'}],
                'owner': {'display_name': 'User B'}
            })
        
        page1_response = {
            'items': page1_data,
            'next': 'https://api.spotify.com/v1/users/test/playlists?offset=50'
        }
        
        page2_response = {
            'items': page2_data,
            'next': None
        }
        
        mock_sp.current_user_playlists.return_value = page1_response
        mock_sp.next.return_value = page2_response
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            playlists = api.get_playlists_detailed()
            
            assert len(playlists) == 75
            assert playlists[0]['name'] == 'Playlist 0'
            assert playlists[49]['name'] == 'Playlist 49'
            assert playlists[50]['name'] == 'Playlist 50'
            assert playlists[74]['name'] == 'Playlist 74'
            
            mock_sp.next.assert_called_once()
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_playlist_without_images(self, mock_oauth, mock_spotify_class):
        """Test handling playlists without cover images."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp.current_user_playlists.return_value = {
            'items': [
                {
                    'name': 'No Image Playlist',
                    'id': 'noimg1',
                    'uri': 'spotify:playlist:noimg1',
                    'tracks': {'total': 10},
                    'images': [],
                    'owner': {'display_name': 'Test User'}
                },
                {
                    'name': 'Has Image Playlist',
                    'id': 'hasimg1',
                    'uri': 'spotify:playlist:hasimg1',
                    'tracks': {'total': 20},
                    'images': [{'url': 'https://example.com/cover.jpg'}],
                    'owner': {'display_name': 'Test User'}
                }
            ],
            'next': None
        }
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            playlists = api.get_playlists_detailed()
            
            assert len(playlists) == 2
            assert playlists[0]['image_url'] is None
            assert playlists[1]['image_url'] == 'https://example.com/cover.jpg'


class TestOAuthFlowAndTokenRefresh:
    """Integration tests for OAuth authentication and token refresh."""
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_cached_token_usage(self, mock_oauth, mock_spotify_class):
        """Test using cached token on initialization."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        cached_token = {
            'access_token': 'cached_access',
            'refresh_token': 'cached_refresh',
            'expires_at': int(time.time()) + 3600
        }
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = cached_token
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = cached_token
        mock_oauth.return_value = mock_oauth_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            
            assert api.sp is not None
            mock_spotify_class.assert_called_once()
    
    @patch('spotify_api.spotify_api.webbrowser.open')
    @patch('spotify_api.spotify_api.HTTPServer')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_oauth_flow_with_callback(self, mock_oauth, mock_spotify_class, mock_httpserver, mock_browser):
        """Test OAuth flow with browser callback."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = None
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = None
        mock_oauth_instance.redirect_uri = 'http://localhost:8888/callback'
        mock_oauth_instance.get_authorize_url.return_value = 'https://accounts.spotify.com/authorize?...'
        mock_oauth_instance.get_access_token.return_value = {
            'access_token': 'new_access',
            'refresh_token': 'new_refresh',
            'expires_at': int(time.time()) + 3600
        }
        mock_oauth.return_value = mock_oauth_instance
        
        mock_server_instance = Mock()
        mock_server_instance.auth_code = 'auth_code_123'
        mock_httpserver.return_value = mock_server_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }):
            api = SpotifyAPI()
            
            token = api.authenticate(open_browser=True, timeout=60)
            
            mock_browser.assert_called_once()
            mock_httpserver.assert_called_once()
            mock_server_instance.handle_request.assert_called_once()
            mock_oauth_instance.get_access_token.assert_called_once_with('auth_code_123')
            
            assert token['access_token'] == 'new_access'
            assert api.sp is not None
    
    @patch('spotify_api.spotify_api.HTTPServer')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_oauth_flow_timeout(self, mock_oauth, mock_spotify_class, mock_httpserver):
        """Test OAuth flow handles timeout gracefully."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = None
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = None
        mock_oauth_instance.redirect_uri = 'http://localhost:8888/callback'
        mock_oauth_instance.get_authorize_url.return_value = 'https://accounts.spotify.com/authorize?...'
        mock_oauth.return_value = mock_oauth_instance
        
        mock_server_instance = Mock()
        mock_server_instance.auth_code = None
        mock_httpserver.return_value = mock_server_instance
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }):
            api = SpotifyAPI()
            
            with pytest.raises(RuntimeError) as exc_info:
                api.authenticate(open_browser=False, timeout=1)
            
            assert 'authorization code' in str(exc_info.value).lower()
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_is_authenticated_with_valid_token(self, mock_oauth, mock_spotify_class):
        """Test authentication check with valid token."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'valid_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'valid_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp.current_user.return_value = {'id': 'user123', 'display_name': 'Test User'}
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            assert api.is_authenticated() is True
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_is_authenticated_with_expired_token(self, mock_oauth, mock_spotify_class):
        """Test authentication check with expired token."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'expired_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'expired_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp.current_user.side_effect = Exception("Token expired")
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            assert api.is_authenticated() is False


class TestGracefulShutdownAndCleanup:
    """Integration tests for resource cleanup and graceful shutdown."""
    
    def test_alarm_shutdown_stops_scheduler(self):
        """Test that shutdown properly stops the scheduler thread."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('10:00', 'Test Playlist', 'spotify:playlist:test', mock_api)
        
        assert alarm.scheduler_running is True
        assert alarm.scheduler_thread is not None
        assert alarm.scheduler_thread.is_alive()
        
        alarm.shutdown()
        
        assert alarm.scheduler_running is False
        
        time.sleep(0.5)
        assert not alarm.scheduler_thread.is_alive()
    
    def test_alarm_shutdown_clears_jobs(self):
        """Test that shutdown clears all scheduled jobs."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('08:00', 'Playlist A', 'spotify:playlist:a', mock_api)
        alarm.set_alarm('09:00', 'Playlist B', 'spotify:playlist:b', mock_api)
        alarm.set_alarm('10:00', 'Playlist C', 'spotify:playlist:c', mock_api)
        
        assert len(alarm.get_alarms()) == 3
        
        alarm.shutdown()
        
        assert len(alarm.get_alarms()) == 0
    
    def test_alarm_shutdown_is_idempotent(self):
        """Test that calling shutdown multiple times is safe."""
        alarm = Alarm()
        mock_api = Mock()
        
        alarm.set_alarm('10:00', 'Test', 'spotify:playlist:test', mock_api)
        
        alarm.shutdown()
        alarm.shutdown()
        alarm.shutdown()
        
        assert alarm.scheduler_running is False
        assert len(alarm.get_alarms()) == 0
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_spotify_api_command_queue_cleanup(self, mock_oauth, mock_spotify_class):
        """Test command queue worker cleanup."""
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
            
            api.start_command_queue_worker()
            assert api._queue_worker_running is True
            assert api._queue_worker is not None
            
            api.stop_command_queue_worker()
            assert api._queue_worker_running is False
            
            time.sleep(0.5)
            if api._queue_worker:
                assert not api._queue_worker.is_alive()
    
    def test_cleanup_with_active_alarms_and_threads(self):
        """Test cleanup when multiple alarms and threads are active."""
        alarm = Alarm()
        mock_api = Mock()
        
        for i in range(5):
            alarm.set_alarm(f'{10 + i}:00', f'Playlist {i}', f'spotify:playlist:{i}', mock_api)
        
        assert alarm.scheduler_running is True
        assert len(alarm.get_alarms()) == 5
        
        alarm.shutdown()
        
        assert alarm.scheduler_running is False
        assert len(alarm.get_alarms()) == 0


class TestConcurrentAlarmTriggers:
    """Integration tests for concurrent alarm triggers."""
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_concurrent_alarm_playback_serialized(self, mock_oauth, mock_spotify_class):
        """Test that concurrent alarm triggers are properly serialized."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        playback_calls = []
        volume_calls = []
        
        def record_playback(context_uri):
            playback_calls.append(context_uri)
            time.sleep(0.01)
        
        def record_volume(vol):
            volume_calls.append(vol)
        
        mock_sp.start_playback.side_effect = record_playback
        mock_sp.volume.side_effect = record_volume
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            def trigger_alarm(playlist_uri, volume):
                alarm.play_playlist(playlist_uri, api, volume)
            
            threads = []
            for i in range(5):
                t = threading.Thread(
                    target=trigger_alarm,
                    args=(f'spotify:playlist:test{i}', 70 + i)
                )
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            assert len(playback_calls) == 5
            assert len(volume_calls) == 5
            
            assert set(playback_calls) == {
                'spotify:playlist:test0',
                'spotify:playlist:test1',
                'spotify:playlist:test2',
                'spotify:playlist:test3',
                'spotify:playlist:test4'
            }
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_alarm_trigger_during_api_operations(self, mock_oauth, mock_spotify_class):
        """Test alarm triggering while other API operations are in progress."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp.current_user_playlists.return_value = {
            'items': [
                {'name': 'Test', 'id': '1', 'uri': 'spotify:playlist:1',
                 'tracks': {'total': 10}, 'images': [], 'owner': {'display_name': 'User'}}
            ],
            'next': None
        }
        
        mock_sp.current_user.return_value = {'display_name': 'Test User', 'id': 'user1'}
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            results = {'playlists': [], 'users': [], 'playback': []}
            
            def fetch_playlists():
                for _ in range(10):
                    playlists = api.get_playlists_detailed()
                    results['playlists'].append(len(playlists))
                    time.sleep(0.001)
            
            def fetch_user():
                for _ in range(10):
                    user = api.get_current_user()
                    results['users'].append(user['id'])
                    time.sleep(0.001)
            
            def trigger_playback():
                time.sleep(0.005)
                for i in range(3):
                    alarm.play_playlist(f'spotify:playlist:alarm{i}', api, 80)
                    results['playback'].append(i)
            
            threads = [
                threading.Thread(target=fetch_playlists),
                threading.Thread(target=fetch_user),
                threading.Thread(target=trigger_playback)
            ]
            
            for t in threads:
                t.start()
            
            for t in threads:
                t.join()
            
            assert len(results['playlists']) == 10
            assert len(results['users']) == 10
            assert len(results['playback']) == 3
            
            assert mock_sp.start_playback.call_count == 3
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_command_queue_concurrent_processing(self, mock_oauth, mock_spotify_class):
        """Test command queue handles concurrent API commands."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp.volume.return_value = None
        mock_sp.start_playback.return_value = None
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            api.start_command_queue_worker()
            
            def submit_commands():
                for i in range(10):
                    api.enqueue_command_async(api.set_volume, 50 + i)
            
            threads = []
            for _ in range(3):
                t = threading.Thread(target=submit_commands)
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            time.sleep(0.5)
            
            api.stop_command_queue_worker()
            
            assert mock_sp.volume.call_count == 30


class TestComplexIntegrationScenarios:
    """Complex integration scenarios combining multiple features."""
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_full_application_lifecycle(self, mock_oauth, mock_spotify_class):
        """Test complete application lifecycle: init -> use -> shutdown."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp.current_user.return_value = {'display_name': 'Test User', 'id': 'user123'}
        mock_sp.current_user_playlists.return_value = {
            'items': [
                {'name': 'Morning', 'id': 'm1', 'uri': 'spotify:playlist:m1',
                 'tracks': {'total': 25}, 'images': [{'url': 'http://img.jpg'}],
                 'owner': {'display_name': 'Test User'}},
                {'name': 'Evening', 'id': 'e1', 'uri': 'spotify:playlist:e1',
                 'tracks': {'total': 30}, 'images': [{'url': 'http://img2.jpg'}],
                 'owner': {'display_name': 'Test User'}}
            ],
            'next': None
        }
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            assert api.is_authenticated()
            
            user = api.get_current_user()
            assert user['id'] == 'user123'
            
            playlists = api.get_playlists_detailed()
            assert len(playlists) == 2
            
            alarm = Alarm()
            
            alarm.set_alarm('06:30', 'Morning', 'spotify:playlist:m1', api, 70)
            alarm.set_alarm('20:00', 'Evening', 'spotify:playlist:e1', api, 60)
            
            alarms = alarm.get_alarms()
            assert len(alarms) == 2
            
            alarm.play_playlist('spotify:playlist:m1', api, 70)
            mock_sp.start_playback.assert_called_once_with(context_uri='spotify:playlist:m1')
            
            alarm.remove_alarm('06:30')
            assert len(alarm.get_alarms()) == 1
            
            alarm.shutdown()
            assert alarm.scheduler_running is False
            assert len(alarm.get_alarms()) == 0
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_error_recovery_during_operations(self, mock_oauth, mock_spotify_class):
        """Test that system recovers from API errors during operations."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test_token'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_oauth_instance
        
        call_count = [0]
        
        def flaky_playback(context_uri):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise Exception("Device not found")
        
        mock_sp.start_playback.side_effect = flaky_playback
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
            
            alarm = Alarm()
            
            alarm.play_playlist('spotify:playlist:test1', api, 80)
            
            alarm.play_playlist('spotify:playlist:test2', api, 80)
            
            alarm.play_playlist('spotify:playlist:test3', api, 80)
            
            assert mock_sp.start_playback.call_count == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
