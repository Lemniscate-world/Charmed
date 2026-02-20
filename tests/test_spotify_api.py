"""
test_spotify_api.py - Unit tests for the SpotifyAPI and ThreadSafeSpotifyAPI classes

Tests cover:
- Initialization with environment variables
- Missing credentials handling
- Authentication status checking
- Playlist retrieval (basic and detailed)
- Playback control methods
- Volume control
- Thread-safe wrapper functionality

Run with: python -m pytest tests/test_spotify_api.py -v
"""

import pytest  # Test framework
import os      # Environment variable manipulation
from unittest.mock import Mock, patch, MagicMock  # Mocking utilities

# Import the module under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSpotifyAPIInit:
    """Tests for SpotifyAPI initialization."""
    
    def test_init_missing_credentials_raises(self):
        """Should raise RuntimeError when credentials are missing."""
        # Clear any existing environment variables
        with patch.dict(os.environ, {}, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                from spotify_api.spotify_api import SpotifyAPI
                with pytest.raises(RuntimeError) as exc_info:
                    SpotifyAPI()
                assert 'credentials not set' in str(exc_info.value).lower()
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_init_with_valid_credentials(self, mock_spotify, mock_oauth):
        """Should initialize successfully with valid credentials."""
        # Create mock cache handler with the new pattern
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = None

        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = None
        mock_oauth.return_value = mock_oauth_instance

        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                # Re-import to get fresh module
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)

                api = api_module.SpotifyAPI()
                assert api.auth_manager is not None


class TestIsAuthenticated:
    """Tests for is_authenticated method."""
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_is_authenticated_false_when_no_client(self, mock_spotify, mock_oauth):
        """Should return False when sp is None."""
        # Create mock cache handler with the new pattern
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = None

        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = None
        mock_oauth.return_value = mock_oauth_instance

        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)

                api = api_module.SpotifyAPI()
                api.sp = None
                assert api.is_authenticated() is False


class TestGetPlaylists:
    """Tests for get_playlists and get_playlists_detailed methods."""
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_get_playlists_not_authenticated(self, mock_spotify, mock_oauth):
        """Should raise RuntimeError when not authenticated."""
        # Create mock cache handler with the new pattern
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = None

        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = None
        mock_oauth.return_value = mock_oauth_instance

        env_vars = {
            'SPOTIPY_CLIENT_ID': 'id',
            'SPOTIPY_CLIENT_SECRET': 'secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)

                api = api_module.SpotifyAPI()
                api.sp = None

                with pytest.raises(RuntimeError):
                    api.get_playlists()

    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_get_playlists_returns_names(self, mock_spotify, mock_oauth):
        """Should return list of playlist names."""
        # Create mock cache handler with the new pattern
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}

        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance

        mock_sp_instance = Mock()
        mock_sp_instance.current_user_playlists.return_value = {
            'items': [
                {'name': 'Playlist 1'},
                {'name': 'Playlist 2'}
            ]
        }
        mock_spotify.return_value = mock_sp_instance

        env_vars = {
            'SPOTIPY_CLIENT_ID': 'id',
            'SPOTIPY_CLIENT_SECRET': 'secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)

                api = api_module.SpotifyAPI()
                # Manually set the sp instance since cached token triggers it
                api.sp = mock_sp_instance
                result = api.get_playlists()

                assert result == ['Playlist 1', 'Playlist 2']


class TestVolumeControl:
    """Tests for set_volume method."""

    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_set_volume_clamps_value(self, mock_spotify, mock_oauth):
        """Volume should be clamped between 0 and 100."""
        # Create mock cache handler with the new pattern
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}

        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance

        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance

        env_vars = {
            'SPOTIPY_CLIENT_ID': 'id',
            'SPOTIPY_CLIENT_SECRET': 'secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)

                api = api_module.SpotifyAPI()
                # Manually set the sp instance
                api.sp = mock_sp_instance
                mock_sp_instance.devices.return_value = {'devices': [{'is_active': True}]}

                # Test clamping above 100
                api.set_volume(150)
                mock_sp_instance.volume.assert_called_with(100)

                # Test clamping below 0
                api.set_volume(-50)
                mock_sp_instance.volume.assert_called_with(0)


class TestThreadSafeSpotifyAPIInit:
    """Tests for ThreadSafeSpotifyAPI initialization."""
    
    def test_init_missing_credentials_raises(self):
        """Should raise RuntimeError when credentials are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                from spotify_api.spotify_api import ThreadSafeSpotifyAPI
                with pytest.raises(RuntimeError) as exc_info:
                    ThreadSafeSpotifyAPI()
                assert 'credentials not set' in str(exc_info.value).lower()
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_init_with_valid_credentials(self, mock_spotify, mock_oauth):
        """Should initialize successfully with valid credentials."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = None
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = None
        mock_oauth.return_value = mock_oauth_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.ThreadSafeSpotifyAPI()
                assert api._api is not None
                assert api._lock is not None
                assert api._api.auth_manager is not None


class TestSpotifyAPIPagination:
    """Tests for SpotifyAPI.get_playlists_detailed() pagination logic."""
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_get_playlists_detailed_multiple_pages(self, mock_spotify, mock_oauth):
        """Should fetch all playlists across multiple pages using the next field."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        
        page1 = {
            'items': [
                {
                    'name': 'Playlist 1',
                    'id': 'id1',
                    'uri': 'spotify:playlist:id1',
                    'tracks': {'total': 10},
                    'images': [{'url': 'http://image1.jpg'}],
                    'owner': {'display_name': 'Owner 1'}
                },
                {
                    'name': 'Playlist 2',
                    'id': 'id2',
                    'uri': 'spotify:playlist:id2',
                    'tracks': {'total': 20},
                    'images': [{'url': 'http://image2.jpg'}],
                    'owner': {'display_name': 'Owner 2'}
                }
            ],
            'next': 'http://api.spotify.com/v1/playlists?offset=2'
        }
        
        page2 = {
            'items': [
                {
                    'name': 'Playlist 3',
                    'id': 'id3',
                    'uri': 'spotify:playlist:id3',
                    'tracks': {'total': 30},
                    'images': [{'url': 'http://image3.jpg'}],
                    'owner': {'display_name': 'Owner 3'}
                },
                {
                    'name': 'Playlist 4',
                    'id': 'id4',
                    'uri': 'spotify:playlist:id4',
                    'tracks': {'total': 40},
                    'images': [],
                    'owner': {'display_name': 'Owner 4'}
                }
            ],
            'next': 'http://api.spotify.com/v1/playlists?offset=4'
        }
        
        page3 = {
            'items': [
                {
                    'name': 'Playlist 5',
                    'id': 'id5',
                    'uri': 'spotify:playlist:id5',
                    'tracks': {'total': 50},
                    'images': [{'url': 'http://image5.jpg'}],
                    'owner': {'display_name': 'Owner 5'}
                }
            ],
            'next': None
        }
        
        mock_sp_instance.current_user_playlists.return_value = page1
        mock_sp_instance.next.side_effect = [page2, page3]
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'id',
            'SPOTIPY_CLIENT_SECRET': 'secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                result = api.get_playlists_detailed()
                
                assert len(result) == 5
                assert result[0]['name'] == 'Playlist 1'
                assert result[0]['track_count'] == 10
                assert result[0]['image_url'] == 'http://image1.jpg'
                assert result[2]['name'] == 'Playlist 3'
                assert result[3]['image_url'] is None
                assert result[4]['name'] == 'Playlist 5'
                
                assert mock_sp_instance.current_user_playlists.call_count == 1
                assert mock_sp_instance.next.call_count == 2
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_get_playlists_detailed_single_page(self, mock_spotify, mock_oauth):
        """Should handle single page response with no next field."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        
        single_page = {
            'items': [
                {
                    'name': 'Only Playlist',
                    'id': 'id1',
                    'uri': 'spotify:playlist:id1',
                    'tracks': {'total': 15},
                    'images': [{'url': 'http://image1.jpg'}],
                    'owner': {'display_name': 'Owner 1'}
                }
            ],
            'next': None
        }
        
        mock_sp_instance.current_user_playlists.return_value = single_page
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'id',
            'SPOTIPY_CLIENT_SECRET': 'secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                result = api.get_playlists_detailed()
                
                assert len(result) == 1
                assert result[0]['name'] == 'Only Playlist'
                assert result[0]['track_count'] == 15
                
                assert mock_sp_instance.current_user_playlists.call_count == 1
                mock_sp_instance.next.assert_not_called()
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_get_playlists_detailed_empty(self, mock_spotify, mock_oauth):
        """Should handle empty playlist response correctly."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        
        empty_page = {
            'items': [],
            'next': None
        }
        
        mock_sp_instance.current_user_playlists.return_value = empty_page
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'id',
            'SPOTIPY_CLIENT_SECRET': 'secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                result = api.get_playlists_detailed()
                
                assert len(result) == 0
                assert result == []
                
                assert mock_sp_instance.current_user_playlists.call_count == 1
                mock_sp_instance.next.assert_not_called()
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_get_playlists_detailed_missing_fields(self, mock_spotify, mock_oauth):
        """Should handle missing optional fields gracefully."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        
        page_with_missing_fields = {
            'items': [
                {
                    'id': 'id1',
                    'uri': 'spotify:playlist:id1',
                },
                {
                    'name': 'Playlist with Some Fields',
                    'id': 'id2',
                    'uri': 'spotify:playlist:id2',
                    'tracks': {},
                    'images': [],
                    'owner': {}
                }
            ],
            'next': None
        }
        
        mock_sp_instance.current_user_playlists.return_value = page_with_missing_fields
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'id',
            'SPOTIPY_CLIENT_SECRET': 'secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                result = api.get_playlists_detailed()
                
                assert len(result) == 2
                assert result[0]['name'] == 'Unknown'
                assert result[0]['track_count'] == 0
                assert result[0]['image_url'] is None
                assert result[0]['owner'] == 'Unknown'
                
                assert result[1]['name'] == 'Playlist with Some Fields'
                assert result[1]['track_count'] == 0
                assert result[1]['image_url'] is None
                assert result[1]['owner'] == 'Unknown'
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_get_playlists_detailed_accumulates_correctly(self, mock_spotify, mock_oauth):
        """Should correctly accumulate results from multiple pages without duplicates."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        
        page1 = {
            'items': [
                {'name': 'A', 'id': 'a', 'uri': 'spotify:playlist:a', 'tracks': {'total': 1}, 'images': [], 'owner': {'display_name': 'User'}}
            ],
            'next': 'url1'
        }
        
        page2 = {
            'items': [
                {'name': 'B', 'id': 'b', 'uri': 'spotify:playlist:b', 'tracks': {'total': 2}, 'images': [], 'owner': {'display_name': 'User'}}
            ],
            'next': 'url2'
        }
        
        page3 = {
            'items': [
                {'name': 'C', 'id': 'c', 'uri': 'spotify:playlist:c', 'tracks': {'total': 3}, 'images': [], 'owner': {'display_name': 'User'}}
            ],
            'next': None
        }
        
        mock_sp_instance.current_user_playlists.return_value = page1
        mock_sp_instance.next.side_effect = [page2, page3]
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'id',
            'SPOTIPY_CLIENT_SECRET': 'secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                result = api.get_playlists_detailed()
                
                assert len(result) == 3
                assert [p['name'] for p in result] == ['A', 'B', 'C']
                assert [p['id'] for p in result] == ['a', 'b', 'c']
                assert [p['track_count'] for p in result] == [1, 2, 3]


class TestRetryLogic:
    """Tests for _retry_api_call method with rate limiting and transient failures."""
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_retry_api_call_success_first_attempt(self, mock_spotify, mock_oauth):
        """Should return result on first successful attempt."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                
                mock_func = Mock(return_value={'result': 'success'})
                result = api._retry_api_call(mock_func, 'arg1', kwarg1='value1')
                
                assert result == {'result': 'success'}
                mock_func.assert_called_once_with('arg1', kwarg1='value1')
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.time.sleep')
    def test_retry_api_call_rate_limit_429(self, mock_sleep, mock_spotify, mock_oauth):
        """Should retry on 429 rate limit with exponential backoff."""
        from spotipy.exceptions import SpotifyException
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                
                call_count = 0
                def mock_func():
                    nonlocal call_count
                    call_count += 1
                    if call_count < 3:
                        error = SpotifyException(429, 'rate limit', 'Rate limit exceeded')
                        error.http_status = 429
                        raise error
                    return 'success'
                
                result = api._retry_api_call(mock_func)
                
                assert result == 'success'
                assert call_count == 3
                assert mock_sleep.call_count == 2
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.time.sleep')
    def test_retry_api_call_retry_after_header(self, mock_sleep, mock_spotify, mock_oauth):
        """Should respect Retry-After header on 429 errors."""
        from spotipy.exceptions import SpotifyException
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                
                call_count = 0
                def mock_func():
                    nonlocal call_count
                    call_count += 1
                    if call_count < 2:
                        error = SpotifyException(429, 'rate limit', 'Rate limit exceeded')
                        error.http_status = 429
                        error.headers = {'Retry-After': '10'}
                        raise error
                    return 'success'
                
                result = api._retry_api_call(mock_func)
                
                assert result == 'success'
                assert call_count == 2
                # Should have waited 10 seconds (from Retry-After header)
                mock_sleep.assert_called_with(10)
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.time.sleep')
    def test_retry_api_call_server_error_5xx(self, mock_sleep, mock_spotify, mock_oauth):
        """Should retry on 5xx server errors."""
        from spotipy.exceptions import SpotifyException
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                
                call_count = 0
                def mock_func():
                    nonlocal call_count
                    call_count += 1
                    if call_count < 2:
                        error = SpotifyException(503, 'service unavailable', 'Service unavailable')
                        error.http_status = 503
                        raise error
                    return 'recovered'
                
                result = api._retry_api_call(mock_func, max_retries=3)
                
                assert result == 'recovered'
                assert call_count == 2
                assert mock_sleep.call_count == 1
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_retry_api_call_no_retry_on_4xx(self, mock_spotify, mock_oauth):
        """Should not retry on 4xx client errors (except 429)."""
        from spotipy.exceptions import SpotifyException
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                
                call_count = 0
                def mock_func():
                    nonlocal call_count
                    call_count += 1
                    error = SpotifyException(404, 'not found', 'Resource not found')
                    error.http_status = 404
                    raise error
                
                with pytest.raises(SpotifyException) as exc_info:
                    api._retry_api_call(mock_func, max_retries=3)
                
                assert exc_info.value.http_status == 404
                assert call_count == 1  # Should only try once, no retries
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.time.sleep')
    def test_retry_api_call_transient_network_error(self, mock_sleep, mock_spotify, mock_oauth):
        """Should retry on transient network errors."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                
                call_count = 0
                def mock_func():
                    nonlocal call_count
                    call_count += 1
                    if call_count < 3:
                        raise ConnectionError("Network timeout")
                    return 'success'
                
                result = api._retry_api_call(mock_func, max_retries=3)
                
                assert result == 'success'
                assert call_count == 3
                assert mock_sleep.call_count == 2
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.time.sleep')
    def test_retry_api_call_max_retries_exceeded(self, mock_sleep, mock_spotify, mock_oauth):
        """Should raise exception after max retries exceeded."""
        from spotipy.exceptions import SpotifyException
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                
                call_count = 0
                def mock_func():
                    nonlocal call_count
                    call_count += 1
                    error = SpotifyException(503, 'service unavailable', 'Persistent error')
                    error.http_status = 503
                    raise error
                
                with pytest.raises(SpotifyException) as exc_info:
                    api._retry_api_call(mock_func, max_retries=3)
                
                assert call_count == 3  # Should try max_retries times
                assert exc_info.value.http_status == 503
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.time.sleep')
    def test_retry_api_call_exponential_backoff_delay(self, mock_sleep, mock_spotify, mock_oauth):
        """Should use exponential backoff for retry delays."""
        from spotipy.exceptions import SpotifyException
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                
                call_count = 0
                def mock_func():
                    nonlocal call_count
                    call_count += 1
                    if call_count < 4:
                        error = SpotifyException(500, 'server error', 'Server error')
                        error.http_status = 500
                        raise error
                    return 'success'
                
                result = api._retry_api_call(mock_func, max_retries=4, retry_delay=1)
                
                assert result == 'success'
                assert call_count == 4
                
                # Verify exponential backoff: delay * (attempt + 1)
                # attempt 0 -> 1, attempt 1 -> 2, attempt 2 -> 3
                expected_delays = [1, 2, 3]
                actual_delays = [call.args[0] for call in mock_sleep.call_args_list]
                assert actual_delays == expected_delays
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.time.sleep')
    def test_retry_api_call_different_retry_delay(self, mock_sleep, mock_spotify, mock_oauth):
        """Should accept custom retry_delay parameter."""
        from spotipy.exceptions import SpotifyException
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                
                call_count = 0
                def mock_func():
                    nonlocal call_count
                    call_count += 1
                    if call_count < 3:
                        error = SpotifyException(500, 'server error', 'Server error')
                        error.http_status = 500
                        raise error
                    return 'success'
                
                result = api._retry_api_call(mock_func, max_retries=3, retry_delay=2)
                
                assert result == 'success'
                # With retry_delay=2: attempt 0 -> 2, attempt 1 -> 4
                expected_delays = [2, 4]
                actual_delays = [call.args[0] for call in mock_sleep.call_args_list]
                assert actual_delays == expected_delays
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    @patch('spotify_api.spotify_api.time.sleep')
    def test_retry_api_call_with_args_and_kwargs(self, mock_sleep, mock_spotify, mock_oauth):
        """Should pass through args and kwargs to the function."""
        from spotipy.exceptions import SpotifyException
        
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.SpotifyAPI()
                api.sp = mock_sp_instance
                
                received_args = []
                received_kwargs = []
                call_count = 0
                
                def mock_func(*args, **kwargs):
                    nonlocal call_count
                    call_count += 1
                    received_args.append(args)
                    received_kwargs.append(kwargs)
                    if call_count < 2:
                        error = SpotifyException(500, 'server error', 'Server error')
                        error.http_status = 500
                        raise error
                    return 'success'
                
                result = api._retry_api_call(mock_func, 'arg1', 'arg2', key1='value1', key2='value2')
                
                assert result == 'success'
                assert call_count == 2
                # Verify args and kwargs were passed correctly on both attempts
                assert all(args == ('arg1', 'arg2') for args in received_args)
                assert all(kwargs == {'key1': 'value1', 'key2': 'value2'} for kwargs in received_kwargs)


class TestThreadSafeSpotifyAPIOperations:
    """Tests for ThreadSafeSpotifyAPI wrapper operations."""
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_is_authenticated_delegated(self, mock_spotify, mock_oauth):
        """Should delegate is_authenticated to wrapped API."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = None
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = None
        mock_oauth.return_value = mock_oauth_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.ThreadSafeSpotifyAPI()
                api._api.sp = None
                assert api.is_authenticated() is False
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_get_playlists_delegated(self, mock_spotify, mock_oauth):
        """Should delegate get_playlists to wrapped API."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_sp_instance.current_user_playlists.return_value = {
            'items': [
                {'name': 'Test Playlist 1'},
                {'name': 'Test Playlist 2'}
            ]
        }
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.ThreadSafeSpotifyAPI()
                api._api.sp = mock_sp_instance
                result = api.get_playlists()
                
                assert result == ['Test Playlist 1', 'Test Playlist 2']
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_play_playlist_by_uri_delegated(self, mock_spotify, mock_oauth):
        """Should delegate play_playlist_by_uri to wrapped API."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.ThreadSafeSpotifyAPI()
                api._api.sp = mock_sp_instance
                
                api.play_playlist_by_uri('spotify:playlist:test')
                mock_sp_instance.start_playback.assert_called_once_with(
                    context_uri='spotify:playlist:test'
                )
    
    @patch('spotify_api.spotify_api.SpotifyOAuth')
    @patch('spotify_api.spotify_api.spotipy.Spotify')
    def test_set_volume_delegated(self, mock_spotify, mock_oauth):
        """Should delegate set_volume to wrapped API."""
        mock_cache_handler = Mock()
        mock_cache_handler.get_cached_token.return_value = {'access_token': 'test'}
        
        mock_oauth_instance = Mock()
        mock_oauth_instance.cache_handler = mock_cache_handler
        mock_oauth_instance.validate_token.return_value = {'access_token': 'test'}
        mock_oauth.return_value = mock_oauth_instance
        
        mock_sp_instance = Mock()
        mock_spotify.return_value = mock_sp_instance
        
        env_vars = {
            'SPOTIPY_CLIENT_ID': 'test_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('spotify_api.spotify_api.load_dotenv'):
                import importlib
                import spotify_api.spotify_api as api_module
                importlib.reload(api_module)
                
                api = api_module.ThreadSafeSpotifyAPI()
                api._api.sp = mock_sp_instance
                
                api.set_volume(75)
                mock_sp_instance.volume.assert_called_once_with(75)

