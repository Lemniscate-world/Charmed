"""
test_thread_safety.py - Thread safety tests for Alarmify

Tests concurrent access patterns to ensure no race conditions occur
between GUI thread and alarm scheduler thread.
"""

import threading
import time
import pytest
from unittest.mock import Mock, MagicMock, patch
from alarm import Alarm
from spotify_api.spotify_api import SpotifyAPI


class TestAlarmThreadSafety:
    """Test thread safety of Alarm class."""
    
    def test_concurrent_alarm_additions(self):
        """Test adding alarms from multiple threads simultaneously."""
        alarm = Alarm()
        mock_api = Mock(spec=SpotifyAPI)
        
        def add_alarm(index):
            alarm.set_alarm(f"10:{index:02d}", f"Playlist {index}", mock_api, 80)
        
        threads = []
        for i in range(10):
            t = threading.Thread(target=add_alarm, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        alarms = alarm.get_alarms()
        assert len(alarms) == 10
    
    def test_concurrent_reads_and_writes(self):
        """Test concurrent reads and writes to alarm list."""
        alarm = Alarm()
        mock_api = Mock(spec=SpotifyAPI)
        
        # Add initial alarms
        for i in range(5):
            alarm.set_alarm(f"10:{i:02d}", f"Playlist {i}", mock_api, 80)
        
        results = []
        
        def reader():
            for _ in range(10):
                alarms = alarm.get_alarms()
                results.append(len(alarms))
                time.sleep(0.001)
        
        def writer():
            for i in range(5, 10):
                alarm.set_alarm(f"11:{i:02d}", f"Playlist {i}", mock_api, 80)
                time.sleep(0.002)
        
        read_thread = threading.Thread(target=reader)
        write_thread = threading.Thread(target=writer)
        
        read_thread.start()
        write_thread.start()
        
        read_thread.join()
        write_thread.join()
        
        # Verify no crashes and all alarms were added
        assert len(alarm.get_alarms()) == 10
        # All reads should have returned valid counts
        assert all(count >= 5 and count <= 10 for count in results)
    
    def test_concurrent_removals(self):
        """Test removing alarms from multiple threads."""
        alarm = Alarm()
        mock_api = Mock(spec=SpotifyAPI)
        
        # Add alarms
        for i in range(10):
            alarm.set_alarm(f"10:{i:02d}", f"Playlist {i}", mock_api, 80)
        
        def remove_alarm(time_str):
            alarm.remove_alarm(time_str)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=remove_alarm, args=(f"10:{i:02d}",))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        alarms = alarm.get_alarms()
        assert len(alarms) == 5


class TestSpotifyAPIThreadSafety:
    """Test thread safety of SpotifyAPI class."""
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_concurrent_api_calls(self, mock_oauth, mock_spotify_class):
        """Test concurrent API method calls don't cause race conditions."""
        # Setup mocks
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        mock_sp.current_user.return_value = {'display_name': 'Test User'}
        
        # Create API instance
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
        
        results = []
        
        def call_api():
            for _ in range(10):
                user = api.get_current_user()
                results.append(user)
        
        threads = []
        for _ in range(5):
            t = threading.Thread(target=call_api)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify all calls succeeded
        assert len(results) == 50
        assert all(r['display_name'] == 'Test User' for r in results)
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_concurrent_playback_calls(self, mock_oauth, mock_spotify_class):
        """Test concurrent playback and volume calls are serialized."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
        
        # Mock playlist data
        mock_sp.current_user_playlists.return_value = {
            'items': [
                {'name': 'Playlist 1', 'uri': 'spotify:playlist:1'},
                {'name': 'Playlist 2', 'uri': 'spotify:playlist:2'}
            ]
        }
        
        def play_and_volume():
            api.set_volume(80)
            api.play_playlist('Playlist 1')
        
        threads = []
        for _ in range(5):
            t = threading.Thread(target=play_and_volume)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify methods were called (order doesn't matter due to threading)
        assert mock_sp.volume.call_count == 5
        assert mock_sp.start_playback.call_count == 5


class TestIntegratedThreadSafety:
    """Test integrated scenarios with both Alarm and SpotifyAPI."""
    
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    def test_alarm_trigger_while_gui_browsing(self, mock_oauth, mock_spotify_class):
        """Simulate alarm triggering while GUI is browsing playlists."""
        mock_sp = MagicMock()
        mock_spotify_class.return_value = mock_sp
        
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888'
        }):
            api = SpotifyAPI()
            api.sp = mock_sp
        
        alarm = Alarm()
        
        # Mock responses
        mock_sp.current_user_playlists.return_value = {
            'items': [
                {'name': 'Morning', 'uri': 'spotify:playlist:1', 'id': '1'},
                {'name': 'Evening', 'uri': 'spotify:playlist:2', 'id': '2'}
            ]
        }
        
        gui_results = []
        alarm_triggered = []
        
        def gui_browsing():
            """Simulate GUI browsing playlists repeatedly."""
            for _ in range(20):
                playlists = api.get_playlists_detailed()
                gui_results.append(len(playlists))
                time.sleep(0.001)
        
        def alarm_triggering():
            """Simulate alarm triggering playback."""
            time.sleep(0.005)  # Wait a bit then trigger
            alarm.play_playlist('Morning', api, 80)
            alarm_triggered.append(True)
        
        gui_thread = threading.Thread(target=gui_browsing)
        alarm_thread = threading.Thread(target=alarm_triggering)
        
        gui_thread.start()
        alarm_thread.start()
        
        gui_thread.join()
        alarm_thread.join()
        
        # Verify both operations completed successfully
        assert len(gui_results) == 20
        assert all(count == 2 for count in gui_results)
        assert len(alarm_triggered) == 1
        assert mock_sp.start_playback.call_count == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
