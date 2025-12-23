"""
mock_spotify.py - Mock Spotify API for testing without Premium account

This module provides a mock implementation of the Spotify API that can be used
for testing UI features, workflows, and error handling without requiring:
- Spotify Premium account
- Real API calls
- Active internet connection (for UI testing)

Usage:
    Set environment variable: ALARMIFY_TEST_MODE=true
    Or import directly: from spotify_api.mock_spotify import MockSpotifyAPI
"""

from typing import List, Dict, Optional
from logging_config import get_logger

logger = get_logger(__name__)


class MockSpotifyAPI:
    """
    Mock Spotify API implementation for testing.
    
    Simulates all Spotify API methods with realistic mock data.
    Useful for:
    - UI/UX testing
    - Workflow testing
    - Development without Premium
    - Offline development
    """
    
    def __init__(self):
        """Initialize mock API with test data."""
        logger.info('Initializing Mock Spotify API (TEST MODE)')
        self._authenticated = True
        self._premium = False  # Set to True to test Premium features
        self._current_user = {
            'display_name': 'Test User',
            'id': 'test_user_123',
            'product': 'free',  # or 'premium'
            'images': []
        }
        
    def authenticate(self, open_browser=True, timeout=120):
        """
        Mock authentication - always succeeds.
        
        Args:
            open_browser: Ignored in mock mode
            timeout: Ignored in mock mode
            
        Returns:
            dict: Mock token info
        """
        logger.info('[MOCK] Authentication successful')
        self._authenticated = True
        return {
            'access_token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token',
            'expires_in': 3600
        }
    
    def is_authenticated(self) -> bool:
        """Check if authenticated (always True in mock mode)."""
        return self._authenticated
    
    def is_premium_user(self) -> Optional[bool]:
        """
        Check if user has Premium.
        
        Returns:
            bool: True if Premium, False if Free, None if unknown
        """
        return self._premium
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user profile."""
        if not self._authenticated:
            return None
        user = self._current_user.copy()
        user['product'] = 'premium' if self._premium else 'free'
        return user
    
    def get_playlists_detailed(self) -> List[Dict]:
        """
        Get mock playlists with detailed metadata.
        
        Returns:
            list: List of playlist dictionaries
        """
        if not self._authenticated:
            raise RuntimeError('Not authenticated with Spotify. Please log in first.')
        
        logger.info('[MOCK] Returning mock playlists')
        return [
            {
                'name': 'Morning Energy',
                'id': 'mock_morning_1',
                'uri': 'spotify:playlist:mock_morning_1',
                'track_count': 45,
                'image_url': 'https://via.placeholder.com/300/1DB954/ffffff?text=Morning+Energy',
                'owner': 'You'
            },
            {
                'name': 'Chill Vibes',
                'id': 'mock_chill_1',
                'uri': 'spotify:playlist:mock_chill_1',
                'track_count': 120,
                'image_url': 'https://via.placeholder.com/300/FF6B6B/ffffff?text=Chill+Vibes',
                'owner': 'You'
            },
            {
                'name': 'Workout Mix',
                'id': 'mock_workout_1',
                'uri': 'spotify:playlist:mock_workout_1',
                'track_count': 80,
                'image_url': 'https://via.placeholder.com/300/4A9EFF/ffffff?text=Workout',
                'owner': 'You'
            },
            {
                'name': 'Focus Time',
                'id': 'mock_focus_1',
                'uri': 'spotify:playlist:mock_focus_1',
                'track_count': 60,
                'image_url': 'https://via.placeholder.com/300/FFA500/ffffff?text=Focus',
                'owner': 'You'
            },
            {
                'name': 'Sleep Sounds',
                'id': 'mock_sleep_1',
                'uri': 'spotify:playlist:mock_sleep_1',
                'track_count': 200,
                'image_url': 'https://via.placeholder.com/300/9B59B6/ffffff?text=Sleep',
                'owner': 'You'
            },
            {
                'name': 'Road Trip',
                'id': 'mock_roadtrip_1',
                'uri': 'spotify:playlist:mock_roadtrip_1',
                'track_count': 150,
                'image_url': 'https://via.placeholder.com/300/E74C3C/ffffff?text=Road+Trip',
                'owner': 'You'
            }
        ]
    
    def get_devices(self) -> List[Dict]:
        """
        Get mock devices.
        
        Returns:
            list: List of device dictionaries
        """
        if not self._authenticated:
            return []
        
        logger.info('[MOCK] Returning mock devices')
        return [
            {
                'id': 'mock_desktop_1',
                'name': 'Your Computer',
                'type': 'Computer',
                'is_active': True,
                'volume_percent': 50
            },
            {
                'id': 'mock_phone_1',
                'name': 'Your Phone',
                'type': 'Smartphone',
                'is_active': False,
                'volume_percent': 80
            },
            {
                'id': 'mock_speaker_1',
                'name': 'Living Room Speaker',
                'type': 'Speaker',
                'is_active': False,
                'volume_percent': 60
            }
        ]
    
    def get_active_device(self) -> Optional[Dict]:
        """Get currently active device."""
        devices = self.get_devices()
        for device in devices:
            if device.get('is_active'):
                return device
        return None
    
    def play_playlist_by_uri(self, playlist_uri: str):
        """
        Mock playlist playback.
        
        Args:
            playlist_uri: Spotify playlist URI
            
        Raises:
            RuntimeError: If not Premium (when _premium=False)
        """
        if not self._authenticated:
            raise RuntimeError('Not authenticated with Spotify. Please log in first.')
        
        if not self._premium:
            raise RuntimeError(
                'Playback requires Spotify Premium.\n\n'
                'Please upgrade to Spotify Premium to use Alarmify.\n'
                'Visit: https://www.spotify.com/premium'
            )
        
        logger.info(f'[MOCK] Would play playlist: {playlist_uri}')
        # In real implementation, this would start playback
        return True
    
    def set_volume(self, volume_percent: int):
        """
        Mock volume control.
        
        Args:
            volume_percent: Volume level 0-100
        """
        if not self._authenticated:
            raise RuntimeError('Not authenticated with Spotify. Please log in first.')
        
        volume = max(0, min(100, int(volume_percent)))
        logger.info(f'[MOCK] Would set volume to {volume}%')
        return True
    
    def transfer_playback(self, device_id: str, force_play: bool = False):
        """
        Mock device transfer.
        
        Args:
            device_id: Device ID to transfer to
            force_play: Whether to start playback
        """
        if not self._authenticated:
            raise RuntimeError('Spotify client not authenticated')
        
        logger.info(f'[MOCK] Would transfer playback to device: {device_id}')
        return True
    
    def get_playlists(self) -> List[str]:
        """Get list of playlist names (basic)."""
        playlists = self.get_playlists_detailed()
        return [p['name'] for p in playlists]
    
    def play_playlist(self, playlist_name: str):
        """Play playlist by name (mock)."""
        playlists = self.get_playlists_detailed()
        for playlist in playlists:
            if playlist['name'] == playlist_name:
                return self.play_playlist_by_uri(playlist['uri'])
        raise RuntimeError(f'Playlist "{playlist_name}" not found')
    
    # Properties for compatibility
    @property
    def sp(self):
        """Mock Spotify client (returns self for compatibility)."""
        return self if self._authenticated else None
    
    @property
    def auth_manager(self):
        """Mock auth manager (returns None for compatibility)."""
        return None


class MockThreadSafeSpotifyAPI:
    """
    Thread-safe wrapper for MockSpotifyAPI.
    
    Provides same interface as ThreadSafeSpotifyAPI but with mock implementation.
    """
    
    def __init__(self):
        """Initialize mock thread-safe API."""
        self._api = MockSpotifyAPI()
    
    def authenticate(self, open_browser=True, timeout=120):
        """Thread-safe mock authentication."""
        return self._api.authenticate(open_browser, timeout)
    
    def is_authenticated(self) -> bool:
        """Thread-safe authentication check."""
        return self._api.is_authenticated()
    
    def is_premium_user(self) -> Optional[bool]:
        """Thread-safe Premium check."""
        return self._api.is_premium_user()
    
    def get_current_user(self) -> Optional[Dict]:
        """Thread-safe user retrieval."""
        return self._api.get_current_user()
    
    def get_playlists_detailed(self) -> List[Dict]:
        """Thread-safe playlist retrieval."""
        return self._api.get_playlists_detailed()
    
    def get_devices(self) -> List[Dict]:
        """Thread-safe device retrieval."""
        return self._api.get_devices()
    
    def get_active_device(self) -> Optional[Dict]:
        """Thread-safe active device retrieval."""
        return self._api.get_active_device()
    
    def play_playlist_by_uri(self, playlist_uri: str):
        """Thread-safe playlist playback."""
        return self._api.play_playlist_by_uri(playlist_uri)
    
    def set_volume(self, volume_percent: int):
        """Thread-safe volume control."""
        return self._api.set_volume(volume_percent)
    
    def transfer_playback(self, device_id: str, force_play: bool = False):
        """Thread-safe device transfer."""
        return self._api.transfer_playback(device_id, force_play)
    
    @property
    def sp(self):
        """Thread-safe Spotify client access."""
        return self._api.sp
    
    @property
    def auth_manager(self):
        """Thread-safe auth manager access."""
        return self._api.auth_manager

