"""
spotify_api.py - Spotify API wrapper for Alarmify

This module provides the SpotifyAPI class that handles:
- OAuth authentication with Spotify
- Fetching user playlists (with metadata like images, track counts)
- Starting playback on user's active device
- Volume control for alarm functionality

Dependencies:
- spotipy: Spotify Web API wrapper
- python-dotenv: Environment variable management
"""

import os  # Operating system interface for environment variables
import webbrowser  # Opens URLs in the default browser
from urllib.parse import urlparse, parse_qs  # URL parsing utilities
from http.server import HTTPServer, BaseHTTPRequestHandler  # Local OAuth callback server
from dotenv import load_dotenv  # Load .env file into environment
import spotipy  # Spotify Web API wrapper
from spotipy.oauth2 import SpotifyOAuth  # OAuth2 authentication handler

# Load environment variables from .env file at module import time
load_dotenv()


class SpotifyAPI:
    """
    Wrapper class for Spotify Web API interactions.

    Handles OAuth authentication flow, playlist retrieval, and playback control.
    Requires SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI
    to be set in environment variables or .env file.
    """

    def __init__(self):
        """
        Initialize SpotifyAPI with credentials from environment variables.

        Reads credentials from environment (supports both SPOTIPY_* and legacy names).
        Creates an OAuth manager but does NOT trigger authentication yet.

        Raises:
            RuntimeError: If required credentials are missing.
        """
        # Read credentials from environment, supporting both naming conventions
        client_id = os.getenv('SPOTIPY_CLIENT_ID') or os.getenv('CLIENT_ID')
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET') or os.getenv('CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI') or os.getenv('REDIRECT_URI')

        # Define OAuth scopes - permissions we need from Spotify
        # user-library-read: Access saved tracks/albums
        # user-read-playback-state: Check current playback status
        # user-modify-playback-state: Control playback (play, pause, volume)
        # playlist-read-private: Access private playlists
        scope = os.getenv('SPOTIPY_SCOPE',
            'user-library-read,user-read-playback-state,user-modify-playback-state,playlist-read-private')

        # Validate that all required credentials are present
        if not client_id or not client_secret or not redirect_uri:
            raise RuntimeError(
                "Spotify credentials not set. Set SPOTIPY_CLIENT_ID, "
                "SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI environment "
                "variables or provide a .env file."
            )

        # Create OAuth manager - handles token caching and refresh
        self.auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        )

        # Spotify client instance - None until authenticated
        self.sp = None

        # Try to use cached token if available
        # Using validate_token with cache_handler to avoid deprecation warning
        cached_token = self.auth_manager.cache_handler.get_cached_token()
        token_info = self.auth_manager.validate_token(cached_token)
        if token_info:
            # Token exists and is valid (or was refreshed)
            self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def authenticate(self, open_browser=True, timeout=120):
        """
        Perform OAuth authentication with Spotify.

        If a cached token exists and is valid, uses that.
        Otherwise, opens the browser for user authorization and starts
        a local HTTP server to capture the OAuth callback.

        Args:
            open_browser: If True, automatically open the auth URL in browser.
            timeout: Seconds to wait for OAuth callback before giving up.

        Returns:
            dict: Token info containing access_token, refresh_token, etc.

        Raises:
            RuntimeError: If OAuth callback fails or times out.
        """
        # Check for cached token first (avoids re-auth if already logged in)
        # Using validate_token with cache_handler to avoid deprecation warning
        cached_token = self.auth_manager.cache_handler.get_cached_token()
        token_info = self.auth_manager.validate_token(cached_token)
        if token_info:
            # Create Spotify client with cached token
            self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
            return token_info

        # No cached token - need to perform OAuth flow
        # Get the authorization URL (Spotify's consent page)
        auth_url = self.auth_manager.get_authorize_url()

        # Open browser for user to authorize
        if open_browser:
            webbrowser.open(auth_url)

        # Parse redirect URI to get host and port for callback server
        parsed = urlparse(self.auth_manager.redirect_uri)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 8888

        # Define request handler for OAuth callback
        class OAuthHandler(BaseHTTPRequestHandler):
            """Handles the OAuth redirect from Spotify."""

            def do_GET(self):
                """Process GET request containing auth code."""
                # Parse query string from callback URL
                query = urlparse(self.path).query
                params = parse_qs(query)

                # Extract authorization code
                code = params.get('code', [None])[0]

                # Send success response to browser
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h1>Authentication successful!</h1>"
                    b"<p>You can close this window and return to Alarmify.</p>"
                    b"</body></html>"
                )

                # Store code on server instance for retrieval
                self.server.auth_code = code

            def log_message(self, format, *args):
                """Suppress HTTP server logging."""
                pass  # Silent - don't print to console

        # Start local HTTP server to receive OAuth callback
        httpd = HTTPServer((host, port), OAuthHandler)
        httpd.timeout = timeout  # Set timeout for handle_request

        # Wait for single request (the OAuth callback)
        httpd.handle_request()

        # Retrieve authorization code from server
        code = getattr(httpd, 'auth_code', None)
        if not code:
            raise RuntimeError(
                'Failed to receive authorization code during Spotify OAuth flow. '
                'Make sure the redirect URI matches your Spotify app settings.'
            )

        # Exchange authorization code for access token
        token_info = self.auth_manager.get_access_token(code)

        # Create Spotify client with new token
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

        return token_info

    def is_authenticated(self):
        """
        Check if user is currently authenticated.

        Returns:
            bool: True if authenticated with valid token, False otherwise.
        """
        if not self.sp:
            return False
        try:
            # Try to get current user - will fail if token invalid
            self.sp.current_user()
            return True
        except Exception:
            return False

    def get_current_user(self):
        """
        Get current authenticated user's profile.

        Returns:
            dict: User profile with 'display_name', 'id', 'images', etc.
                  Returns None if not authenticated.
        """
        if not self.sp:
            return None
        try:
            return self.sp.current_user()
        except Exception:
            return None

    def get_playlists(self):
        """
        Get list of user's playlists with basic info (names only).

        Returns:
            list[str]: List of playlist names.

        Raises:
            RuntimeError: If not authenticated.
        """
        if not self.sp:
            raise RuntimeError('Spotify client not authenticated')

        results = self.sp.current_user_playlists()
        # Extract just the names from playlist items
        playlists = [item['name'] for item in results.get('items', [])]
        return playlists

    def get_playlists_detailed(self):
        """
        Get list of user's playlists with full metadata.

        Returns detailed info including images, track counts, and URIs
        for enhanced UI display. Handles pagination to fetch all playlists
        beyond the initial 50-item limit.

        Returns:
            list[dict]: List of playlist dictionaries with keys:
                - name: Playlist name
                - id: Spotify playlist ID
                - uri: Spotify URI for playback
                - track_count: Number of tracks
                - image_url: URL of playlist cover image (or None)
                - owner: Playlist owner's display name

        Raises:
            RuntimeError: If not authenticated.
        """
        if not self.sp:
            raise RuntimeError('Spotify client not authenticated')

        playlists = []
        results = self.sp.current_user_playlists()

        while results:
            for item in results.get('items', []):
                # Get first image URL if available (highest resolution)
                images = item.get('images', [])
                image_url = images[0]['url'] if images else None

                # Build detailed playlist info
                playlist_info = {
                    'name': item.get('name', 'Unknown'),
                    'id': item.get('id'),
                    'uri': item.get('uri'),
                    'track_count': item.get('tracks', {}).get('total', 0),
                    'image_url': image_url,
                    'owner': item.get('owner', {}).get('display_name', 'Unknown')
                }
                playlists.append(playlist_info)

            # Check for next page of results
            if results.get('next'):
                results = self.sp.next(results)
            else:
                results = None

        return playlists

    def play_playlist(self, playlist_name):
        """
        Start playback of a playlist by name.

        Searches user's playlists for matching name and starts playback
        on the user's currently active Spotify device.

        Args:
            playlist_name: Name of playlist to play.

        Raises:
            RuntimeError: If not authenticated or no active device.
        """
        if not self.sp:
            raise RuntimeError('Spotify client not authenticated')

        # Find playlist URI by name
        results = self.sp.current_user_playlists()
        for item in results.get('items', []):
            if item.get('name') == playlist_name:
                # Start playback with playlist context
                # This plays on the user's active device
                self.sp.start_playback(context_uri=item.get('uri'))
                return

        # Playlist not found - could raise exception or log warning
        raise RuntimeError(f'Playlist "{playlist_name}" not found')

    def play_playlist_by_uri(self, playlist_uri):
        """
        Start playback of a playlist by Spotify URI.

        More reliable than by-name lookup since URIs are unique.

        Args:
            playlist_uri: Spotify URI (e.g., 'spotify:playlist:xxxxx')

        Raises:
            RuntimeError: If not authenticated or no active device.
        """
        if not self.sp:
            raise RuntimeError('Spotify client not authenticated')

        self.sp.start_playback(context_uri=playlist_uri)

    def set_volume(self, volume_percent):
        """
        Set playback volume on active device.

        Args:
            volume_percent: Volume level from 0 to 100.

        Raises:
            RuntimeError: If not authenticated or no active device.
        """
        if not self.sp:
            raise RuntimeError('Spotify client not authenticated')

        # Clamp volume to valid range
        volume = max(0, min(100, int(volume_percent)))
        self.sp.volume(volume)

    def get_active_device(self):
        """
        Get the currently active Spotify playback device.

        Returns:
            dict: Device info with 'name', 'type', 'volume_percent', etc.
                  Returns None if no active device.
        """
        if not self.sp:
            return None

        try:
            devices = self.sp.devices()
            for device in devices.get('devices', []):
                if device.get('is_active'):
                    return device
            return None
        except Exception:
            return None
