"""
spotify_api.py - Thread-safe Spotify API wrapper for Alarmify

This module provides two classes for Spotify API interactions:

1. SpotifyAPI - Base API wrapper with built-in thread safety via decorator
2. ThreadSafeSpotifyAPI - Explicit thread-safe wrapper with RLock protection

Both classes handle:
- OAuth authentication with Spotify
- Fetching user playlists (with metadata like images, track counts)
- Starting playback on user's active device
- Volume control for alarm functionality
- Thread-safe API access with locks and command queue pattern

Thread Safety Implementation:
- SpotifyAPI: All public API methods protected with @thread_safe_api_call decorator
- ThreadSafeSpotifyAPI: Wraps SpotifyAPI with explicit RLock on all methods
- Both approaches prevent race conditions between GUI and alarm scheduler threads
- ThreadSafeSpotifyAPI recommended for multi-threaded applications

Dependencies:
- spotipy: Spotify Web API wrapper
- python-dotenv: Environment variable management
- threading: Thread synchronization primitives
"""

import os  # Operating system interface for environment variables
import webbrowser  # Opens URLs in the default browser
from urllib.parse import urlparse, parse_qs  # URL parsing utilities
from http.server import HTTPServer, BaseHTTPRequestHandler  # Local OAuth callback server
from dotenv import load_dotenv  # Load .env file into environment
import spotipy  # Spotify Web API wrapper
from spotipy.oauth2 import SpotifyOAuth  # OAuth2 authentication handler
import threading  # Thread synchronization
import queue  # Thread-safe queue for command pattern
from functools import wraps  # Decorator utilities
from spotipy.exceptions import SpotifyException  # Spotify API exceptions
import time  # For retry delays
from logging_config import get_logger

# Load environment variables from .env file at module import time
load_dotenv()

logger = get_logger(__name__)


def thread_safe_api_call(func):
    """
    Decorator to ensure thread-safe access to Spotify API methods.
    
    Acquires the instance's lock before executing the method and releases it after.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self._api_lock:
            return func(self, *args, **kwargs)
    return wrapper


class SpotifyAPI:
    """
    Wrapper class for Spotify Web API interactions.

    Handles OAuth authentication flow, playlist retrieval, and playback control.
    Requires SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI
    to be set in environment variables or .env file.
    
    Thread-safe: All API methods are protected by locks to prevent race conditions
    between GUI and alarm scheduler threads.
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
            logger.error('Spotify credentials not configured')
            raise RuntimeError(
                "Spotify credentials not set. Set SPOTIPY_CLIENT_ID, "
                "SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI environment "
                "variables or provide a .env file."
            )

        logger.info('Initializing Spotify API with provided credentials')
        
        # Create OAuth manager - handles token caching and refresh
        self.auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        )

        # Spotify client instance - None until authenticated
        self.sp = None

        # Thread safety: RLock for protecting API access (reentrant to allow nested calls)
        self._api_lock = threading.RLock()

        # Command queue for coordinating API calls across threads
        self._command_queue = queue.Queue()
        self._queue_worker = None
        self._queue_worker_running = False

        # Try to use cached token if available
        # Using validate_token with cache_handler to avoid deprecation warning
        cached_token = self.auth_manager.cache_handler.get_cached_token()
        token_info = self.auth_manager.validate_token(cached_token)
        if token_info:
            # Token exists and is valid (or was refreshed)
            self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
            logger.info('Using cached Spotify authentication token')

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
        logger.info('Starting Spotify OAuth authentication')
        
        # Check for cached token first (avoids re-auth if already logged in)
        # Using validate_token with cache_handler to avoid deprecation warning
        cached_token = self.auth_manager.cache_handler.get_cached_token()
        token_info = self.auth_manager.validate_token(cached_token)
        if token_info:
            # Create Spotify client with cached token
            self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
            logger.info('Authentication successful using cached token')
            return token_info

        # No cached token - need to perform OAuth flow
        logger.info('No cached token found, initiating OAuth flow')
        
        # Get the authorization URL (Spotify's consent page)
        auth_url = self.auth_manager.get_authorize_url()
        logger.debug(f'OAuth authorization URL: {auth_url}')

        # Open browser for user to authorize
        if open_browser:
            logger.info('Opening browser for user authorization')
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
        logger.info(f'Starting OAuth callback server on {host}:{port}')
        httpd = HTTPServer((host, port), OAuthHandler)
        httpd.timeout = timeout  # Set timeout for handle_request

        # Wait for single request (the OAuth callback)
        logger.info(f'Waiting for OAuth callback (timeout: {timeout}s)')
        httpd.handle_request()

        # Retrieve authorization code from server
        code = getattr(httpd, 'auth_code', None)
        if not code:
            logger.error('OAuth callback failed: no authorization code received')
            raise RuntimeError(
                'Failed to receive authorization code during Spotify OAuth flow. '
                'Make sure the redirect URI matches your Spotify app settings.'
            )

        logger.info('Authorization code received, exchanging for access token')
        
        # Exchange authorization code for access token
        token_info = self.auth_manager.get_access_token(code)

        # Create Spotify client with new token
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        
        logger.info('Spotify authentication completed successfully')
        return token_info

    @thread_safe_api_call
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

    @thread_safe_api_call
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

    def _retry_api_call(self, func, *args, max_retries=3, retry_delay=1, **kwargs):
        """
        Execute an API call with retry logic for transient failures.
        
        Args:
            func: Function to call
            *args: Positional arguments for func
            max_retries: Maximum number of retry attempts
            retry_delay: Seconds to wait between retries
            **kwargs: Keyword arguments for func
            
        Returns:
            Result of the API call
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except SpotifyException as e:
                last_exception = e
                # Check if it's a transient error (5xx server errors, rate limiting, timeout)
                if hasattr(e, 'http_status'):
                    status = e.http_status
                    # Retry on server errors (5xx) or rate limiting (429)
                    if status >= 500 or status == 429:
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (attempt + 1)
                            if status == 429 and hasattr(e, 'headers'):
                                retry_after = e.headers.get('Retry-After')
                                if retry_after:
                                    wait_time = int(retry_after)
                            time.sleep(wait_time)
                            continue
                    # Don't retry on client errors (4xx except 429)
                    elif 400 <= status < 500:
                        raise
                # Retry on general network/connection errors
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
            except Exception as e:
                last_exception = e
                # Retry on general network/connection errors
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise
        
        # All retries exhausted
        if last_exception:
            raise last_exception

    @thread_safe_api_call
    def get_playlists(self):
        """
        Get list of user's playlists with basic info (names only).

        Returns:
            list[str]: List of playlist names.

        Raises:
            RuntimeError: If not authenticated or API call fails.
        """
        if not self.sp:
            raise RuntimeError('Not authenticated with Spotify. Please log in first.')

        try:
            results = self._retry_api_call(self.sp.current_user_playlists)
            # Extract just the names from playlist items
            playlists = [item['name'] for item in results.get('items', [])]
            return playlists
        except SpotifyException as e:
            raise RuntimeError(f'Failed to fetch playlists from Spotify: {e}')
        except Exception as e:
            raise RuntimeError(f'Unexpected error fetching playlists: {e}')

    @thread_safe_api_call
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
            RuntimeError: If not authenticated or API call fails.
        """
        if not self.sp:
            logger.error('Attempted to get playlists without authentication')
            raise RuntimeError('Not authenticated with Spotify. Please log in first.')

        logger.info('Fetching user playlists with detailed metadata')
        try:
            playlists = []
            results = self._retry_api_call(self.sp.current_user_playlists)

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
                    results = self._retry_api_call(self.sp.next, results)
                else:
                    results = None

            logger.info(f'Retrieved {len(playlists)} playlists')
            return playlists
        except SpotifyException as e:
            raise RuntimeError(f'Failed to fetch playlists from Spotify: {e}')
        except Exception as e:
            raise RuntimeError(f'Unexpected error fetching playlists: {e}')

    @thread_safe_api_call
    def play_playlist(self, playlist_name):
        """
        Start playback of a playlist by name.

        Searches user's playlists for matching name and starts playback
        on the user's currently active Spotify device.

        Args:
            playlist_name: Name of playlist to play.

        Raises:
            RuntimeError: If not authenticated, no active device, or playlist not found.
        """
        if not self.sp:
            logger.error('Attempted to play playlist without authentication')
            raise RuntimeError('Not authenticated with Spotify. Please log in first.')

        logger.info(f'Attempting to play playlist: {playlist_name}')
        
        try:
            # Find playlist URI by name
            results = self._retry_api_call(self.sp.current_user_playlists)
            playlist_uri = None
            
            for item in results.get('items', []):
                if item.get('name') == playlist_name:
                    playlist_uri = item.get('uri')
                    logger.debug(f'Found playlist URI: {playlist_uri}')
                    break
            
            if not playlist_uri:
                logger.error(f'Playlist "{playlist_name}" not found')
                raise RuntimeError(f'Playlist "{playlist_name}" not found in your library')
            
            # Check for active device before attempting playback
            devices = self._retry_api_call(self.sp.devices)
            active_device = None
            for device in devices.get('devices', []):
                if device.get('is_active'):
                    active_device = device
                    break
            
            if not active_device:
                available_devices = [d.get('name') for d in devices.get('devices', [])]
                if available_devices:
                    raise RuntimeError(
                        f'No active Spotify device found. Available devices: {", ".join(available_devices)}. '
                        'Please start Spotify on one of your devices.'
                    )
                else:
                    raise RuntimeError(
                        'No Spotify devices found. Please open Spotify on your phone, computer, or another device.'
                    )
            
            # Start playback with playlist context
            self._retry_api_call(self.sp.start_playback, context_uri=playlist_uri)
            logger.info(f'Started playback of playlist: {playlist_name}')
            
        except SpotifyException as e:
            if hasattr(e, 'http_status'):
                if e.http_status == 403:
                    raise RuntimeError(
                        'Playback requires Spotify Premium. Please upgrade your account.'
                    )
                elif e.http_status == 404:
                    raise RuntimeError(
                        'No active device found. Please start Spotify on one of your devices.'
                    )
            raise RuntimeError(f'Failed to start playback: {e}')
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f'Unexpected error during playback: {e}')

    @thread_safe_api_call
    def play_playlist_by_uri(self, playlist_uri):
        """
        Start playback of a playlist by Spotify URI.

        More reliable than by-name lookup since URIs are unique.

        Args:
            playlist_uri: Spotify URI (e.g., 'spotify:playlist:xxxxx')

        Raises:
            RuntimeError: If not authenticated, no active device, or playback fails.
        """
        if not self.sp:
            logger.error('Attempted to play playlist by URI without authentication')
            raise RuntimeError('Not authenticated with Spotify. Please log in first.')

        logger.info(f'Attempting to play playlist by URI: {playlist_uri}')
        
        try:
            # Check for active device before attempting playback
            devices = self._retry_api_call(self.sp.devices)
            active_device = None
            for device in devices.get('devices', []):
                if device.get('is_active'):
                    active_device = device
                    break
            
            if not active_device:
                available_devices = [d.get('name') for d in devices.get('devices', [])]
                if available_devices:
                    raise RuntimeError(
                        f'No active Spotify device found. Available devices: {", ".join(available_devices)}. '
                        'Please start Spotify on one of your devices.'
                    )
                else:
                    raise RuntimeError(
                        'No Spotify devices found. Please open Spotify on your phone, computer, or another device.'
                    )
            
            self._retry_api_call(self.sp.start_playback, context_uri=playlist_uri)
            logger.info(f'Successfully started playback by URI: {playlist_uri}')
            
        except SpotifyException as e:
            if hasattr(e, 'http_status'):
                if e.http_status == 403:
                    raise RuntimeError(
                        'Playback requires Spotify Premium. Please upgrade your account.'
                    )
                elif e.http_status == 404:
                    raise RuntimeError(
                        'No active device found. Please start Spotify on one of your devices.'
                    )
            raise RuntimeError(f'Failed to start playback: {e}')
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f'Unexpected error during playback: {e}')

    @thread_safe_api_call
    def set_volume(self, volume_percent):
        """
        Set playback volume on active device.

        Args:
            volume_percent: Volume level from 0 to 100.

        Raises:
            RuntimeError: If not authenticated, no active device, or operation fails.
        """
        if not self.sp:
            logger.error('Attempted to set volume without authentication')
            raise RuntimeError('Not authenticated with Spotify. Please log in first.')

        # Clamp volume to valid range
        volume = max(0, min(100, int(volume_percent)))
        logger.debug(f'Setting Spotify volume to {volume}%')
        
        try:
            # Check for active device
            devices = self._retry_api_call(self.sp.devices)
            active_device = None
            for device in devices.get('devices', []):
                if device.get('is_active'):
                    active_device = device
                    break
            
            if not active_device:
                raise RuntimeError('No active Spotify device found to set volume')
            
            self._retry_api_call(self.sp.volume, volume)
            logger.info(f'Volume set to {volume}%')
            
        except SpotifyException as e:
            if hasattr(e, 'http_status') and e.http_status == 403:
                raise RuntimeError('Volume control requires Spotify Premium')
            raise RuntimeError(f'Failed to set volume: {e}')
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f'Unexpected error setting volume: {e}')

    @thread_safe_api_call
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
    
    @thread_safe_api_call
    def get_all_devices(self):
        """
        Get all available Spotify playback devices.

        Returns:
            list[dict]: List of device info dictionaries with 'name', 'type', 
                       'volume_percent', 'is_active', etc.
                       Returns empty list if no devices or on error.
        """
        if not self.sp:
            return []

        try:
            result = self.sp.devices()
            return result.get('devices', [])
        except Exception:
            return []

    @thread_safe_api_call
    def get_devices(self):
        """
        Get all available Spotify playback devices.

        Returns:
            list[dict]: List of device dictionaries with 'id', 'name', 'type', 'is_active', etc.
                        Returns empty list if not authenticated or error occurs.
        """
        if not self.sp:
            return []

        try:
            devices = self.sp.devices()
            return devices.get('devices', [])
        except Exception:
            return []

    @thread_safe_api_call
    def transfer_playback(self, device_id, force_play=False):
        """
        Transfer playback to a specific device.

        Args:
            device_id: Spotify device ID to transfer to.
            force_play: If True, start playback on the device immediately.

        Raises:
            RuntimeError: If not authenticated or device not found.
        """
        if not self.sp:
            raise RuntimeError('Spotify client not authenticated')

        self.sp.transfer_playback(device_id, force_play=force_play)

    def start_command_queue_worker(self):
        """
        Start the command queue worker thread for processing API commands.
        
        This provides an alternative pattern for handling concurrent API access
        where commands are queued and processed sequentially by a worker thread.
        """
        if self._queue_worker_running:
            return
        
        self._queue_worker_running = True
        
        def worker():
            while self._queue_worker_running:
                try:
                    cmd = self._command_queue.get(timeout=1.0)
                    if cmd is None:
                        break
                    
                    func, args, kwargs, result_queue = cmd
                    try:
                        result = func(*args, **kwargs)
                        if result_queue:
                            result_queue.put(('success', result))
                    except Exception as e:
                        if result_queue:
                            result_queue.put(('error', e))
                    finally:
                        self._command_queue.task_done()
                        
                except queue.Empty:
                    continue
        
        self._queue_worker = threading.Thread(
            target=worker,
            daemon=True,
            name='SpotifyAPICommandWorker'
        )
        self._queue_worker.start()
    
    def stop_command_queue_worker(self):
        """Stop the command queue worker thread."""
        if not self._queue_worker_running:
            return
        
        self._queue_worker_running = False
        self._command_queue.put(None)
        
        if self._queue_worker:
            self._queue_worker.join(timeout=5.0)
            self._queue_worker = None
    
    def enqueue_command(self, func, *args, **kwargs):
        """
        Enqueue a command for execution by the worker thread.
        
        Args:
            func: The function to call (should be a bound method of this instance)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        
        Returns:
            Result queue that will contain ('success', result) or ('error', exception)
        """
        result_queue = queue.Queue()
        self._command_queue.put((func, args, kwargs, result_queue))
        return result_queue
    
    def enqueue_command_async(self, func, *args, **kwargs):
        """
        Enqueue a command without waiting for result (fire-and-forget).
        
        Args:
            func: The function to call (should be a bound method of this instance)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        self._command_queue.put((func, args, kwargs, None))


class ThreadSafeSpotifyAPI:
    """
    Thread-safe wrapper for SpotifyAPI ensuring synchronized access from multiple threads.
    
    This class wraps all SpotifyAPI methods with a reentrant lock (RLock) to prevent
    race conditions when the API is accessed from both the GUI thread and the alarm
    scheduler thread. The RLock ensures that API calls are serialized even if the
    same thread makes nested calls.
    
    Usage:
        spotify = ThreadSafeSpotifyAPI()
        spotify.authenticate()
        playlists = spotify.get_playlists()
        spotify.play_playlist_by_uri(playlist_uri)
    
    All methods are protected by the same lock, ensuring thread-safe access to
    the underlying Spotify API client.
    """
    
    def __init__(self):
        """
        Initialize the thread-safe Spotify API wrapper.
        
        Creates an underlying SpotifyAPI instance and a reentrant lock for
        protecting all API access.
        """
        self._api = SpotifyAPI()
        self._lock = threading.RLock()
    
    def authenticate(self, open_browser=True, timeout=120):
        """
        Thread-safe OAuth authentication with Spotify.
        
        Args:
            open_browser: If True, automatically open the auth URL in browser.
            timeout: Seconds to wait for OAuth callback before giving up.
            
        Returns:
            dict: Token info containing access_token, refresh_token, etc.
            
        Raises:
            RuntimeError: If OAuth callback fails or times out.
        """
        with self._lock:
            return self._api.authenticate(open_browser, timeout)
    
    def is_authenticated(self):
        """
        Thread-safe check if user is currently authenticated.
        
        Returns:
            bool: True if authenticated with valid token, False otherwise.
        """
        with self._lock:
            return self._api.is_authenticated()
    
    def get_current_user(self):
        """
        Thread-safe retrieval of current authenticated user's profile.
        
        Returns:
            dict: User profile with 'display_name', 'id', 'images', etc.
                  Returns None if not authenticated.
        """
        with self._lock:
            return self._api.get_current_user()
    
    def get_playlists(self):
        """
        Thread-safe retrieval of user's playlists with basic info.
        
        Returns:
            list[str]: List of playlist names.
            
        Raises:
            RuntimeError: If not authenticated.
        """
        with self._lock:
            return self._api.get_playlists()
    
    def get_playlists_detailed(self):
        """
        Thread-safe retrieval of user's playlists with full metadata.
        
        Returns detailed info including images, track counts, and URIs
        for enhanced UI display. Handles pagination automatically.
        
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
        with self._lock:
            return self._api.get_playlists_detailed()
    
    def play_playlist(self, playlist_name):
        """
        Thread-safe playback of a playlist by name.
        
        Args:
            playlist_name: Name of playlist to play.
            
        Raises:
            RuntimeError: If not authenticated or no active device.
        """
        with self._lock:
            return self._api.play_playlist(playlist_name)
    
    def play_playlist_by_uri(self, playlist_uri):
        """
        Thread-safe playback of a playlist by Spotify URI.
        
        Args:
            playlist_uri: Spotify URI (e.g., 'spotify:playlist:xxxxx')
            
        Raises:
            RuntimeError: If not authenticated or no active device.
        """
        with self._lock:
            return self._api.play_playlist_by_uri(playlist_uri)
    
    def set_volume(self, volume_percent):
        """
        Thread-safe volume control on active device.
        
        Args:
            volume_percent: Volume level from 0 to 100.
            
        Raises:
            RuntimeError: If not authenticated or no active device.
        """
        with self._lock:
            return self._api.set_volume(volume_percent)
    
    def get_active_device(self):
        """
        Thread-safe retrieval of currently active Spotify playback device.
        
        Returns:
            dict: Device info with 'name', 'type', 'volume_percent', etc.
                  Returns None if no active device.
        """
        with self._lock:
            return self._api.get_active_device()
    
    @property
    def sp(self):
        """
        Thread-safe access to the underlying Spotify client.
        
        Returns:
            Spotify client instance or None if not authenticated.
        """
        with self._lock:
            return self._api.sp
    
    @property
    def auth_manager(self):
        """
        Thread-safe access to the OAuth manager.
        
        Returns:
            SpotifyOAuth instance for authentication management.
        """
        with self._lock:
            return self._api.auth_manager
