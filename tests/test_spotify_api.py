"""
test_spotify_api.py - Unit tests for the SpotifyAPI class

Tests cover:
- Initialization with environment variables
- Missing credentials handling
- Authentication status checking
- Playlist retrieval (basic and detailed)
- Playback control methods
- Volume control

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

                # Test clamping above 100
                api.set_volume(150)
                mock_sp_instance.volume.assert_called_with(100)

                # Test clamping below 0
                api.set_volume(-50)
                mock_sp_instance.volume.assert_called_with(0)

