"""
alarm.py - Alarm scheduling module for Alarmify

This module provides the Alarm class for scheduling playlist alarms.
Uses the 'schedule' library for daily recurring tasks and runs
the scheduler in a background daemon thread.

Features:
- Schedule alarms at specific times (HH:MM format)
- Store alarm metadata (time, playlist, volume)
- List all scheduled alarms
- Remove individual alarms
- Set volume before playing
- Thread-safe alarm list management
- Retry logic with exponential backoff for Spotify API failures
- System tray notifications for alarm trigger status

Dependencies:
- schedule: Job scheduling library
- threading: Background execution and synchronization
"""

import schedule  # Job scheduling library
import time      # Time-related functions (sleep)
import threading  # Background thread execution
from datetime import datetime  # Date and time utilities
import re
from logging_config import get_logger

logger = get_logger(__name__)


class Alarm:
    """
    Alarm manager for scheduling Spotify playlist playback.

    Maintains a list of scheduled alarms and runs a background
    scheduler thread to trigger them at the specified times.

    Attributes:
        alarms: List of alarm info dictionaries with time, playlist, volume.
        scheduler_running: Boolean flag indicating if scheduler thread is active.
        gui_app: Reference to GUI application for showing notifications.
    """

    def __init__(self, gui_app=None):
        """
        Initialize the alarm manager with empty alarm list.

        Args:
            gui_app: Reference to GUI application for showing notifications (optional).
        """
        logger.info('Initializing Alarm manager')
        self.alarms = []
        self.scheduler_running = False
        self.scheduler_thread = None
        self._alarms_lock = threading.Lock()
        self.gui_app = gui_app
        logger.info("Alarm manager initialized")

    def set_alarm(self, time_str, playlist_name, playlist_uri, spotify_api, volume=80):
        """
        Schedule a new alarm.

        Creates a daily recurring job that plays the specified playlist
        at the given time with the specified volume.

        Args:
            time_str: Time in 'HH:MM' format (24-hour).
            playlist_name: Name of the Spotify playlist (for display).
            playlist_uri: Spotify URI of the playlist to play.
            spotify_api: SpotifyAPI instance for playback control.
            volume: Volume level 0-100 (default 80).

        Raises:
            ValueError: If time format is invalid.
        """
        logger.info(
            f"Scheduling alarm - Time: {time_str}, Playlist: {playlist_name}, "
            f"URI: {playlist_uri}, Volume: {volume}%"
        )

        if not self._validate_time_format(time_str):
            error_msg = f'Invalid time format: {time_str}. Expected HH:MM (24-hour format).'
            logger.error(f"Invalid time format for alarm: {time_str}")
            raise ValueError(error_msg)

        job = schedule.every().day.at(time_str).do(
            self.play_playlist,
            playlist_uri,
            spotify_api,
            volume,
            playlist_name
        )

        alarm_info = {
            'time': time_str,
            'playlist': playlist_name,
            'playlist_uri': playlist_uri,
            'volume': volume,
            'job': job
        }
        
        with self._alarms_lock:
            self.alarms.append(alarm_info)
            logger.info(f"Alarm successfully scheduled for {time_str}. Total alarms: {len(self.alarms)}")

        self._ensure_scheduler_running()

    def _validate_time_format(self, time_str):
        """
        Validate time string format.

        Args:
            time_str: Time string to validate.

        Returns:
            bool: True if valid HH:MM format in 24-hour time.
        """
        if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', time_str):
            return False

        try:
            hours, minutes = map(int, time_str.split(':'))
            return 0 <= hours <= 23 and 0 <= minutes <= 59
        except (ValueError, AttributeError):
            return False

    def _ensure_scheduler_running(self):
        """Start the scheduler background thread if not already running."""
        if self.scheduler_running:
            return

        def run_scheduler():
            """
            Background scheduler loop.

            Continuously checks for pending jobs and runs them.
            Sleeps 1 second between checks to avoid CPU spinning.
            """
            logger.info("Scheduler thread started")
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(1)
            logger.info("Scheduler thread stopped")

        self.scheduler_running = True

        self.scheduler_thread = threading.Thread(
            target=run_scheduler,
            daemon=True,
            name='AlarmScheduler'
        )
        self.scheduler_thread.start()
        logger.info("Alarm scheduler background thread initialized")

    def play_playlist(self, playlist_uri, spotify_api, volume=80, playlist_name='Playlist'):
        """
        Play a playlist - called by scheduler when alarm triggers.

        Sets the volume first, then starts playlist playback with retry logic.

        Args:
            playlist_uri: Spotify URI of playlist to play.
            spotify_api: SpotifyAPI instance for control.
            volume: Volume level 0-100.
            playlist_name: Name of playlist for notifications.
        """
        logger.info(f"Alarm triggered - Playing playlist: {playlist_name} ({playlist_uri}) at volume {volume}%")

        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                self._set_volume_with_retry(spotify_api, volume, max_retries=2)

                spotify_api.play_playlist_by_uri(playlist_uri)

                success_msg = f'Alarm triggered successfully!\nPlaying: {playlist_name}'
                self._show_notification('Alarm Success', success_msg, success=True)
                logger.info(f"Successfully started playlist playback: {playlist_name}")
                return

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Alarm playback attempt {attempt + 1}/{max_retries} failed for playlist {playlist_name}: {e}", exc_info=True)
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    failure_msg = self._get_user_friendly_error(error_msg, playlist_name)
                    self._show_notification('Alarm Failed', failure_msg, success=False)
                    logger.error(f"Alarm failed after {max_retries} attempts: {failure_msg}")

    def _set_volume_with_retry(self, spotify_api, volume, max_retries=2):
        """
        Set volume with retry logic.

        Args:
            spotify_api: SpotifyAPI instance.
            volume: Volume level 0-100.
            max_retries: Maximum number of retry attempts.
        """
        for attempt in range(max_retries):
            try:
                spotify_api.set_volume(volume)
                logger.info(f"Volume set to {volume}%")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to set volume (attempt {attempt + 1}/{max_retries}): {e}. Retrying...")
                    time.sleep(1)
                else:
                    logger.warning(f"Failed to set volume after {max_retries} attempts: {e}. Continuing with playback attempt.")
                    pass

    def _get_user_friendly_error(self, error_msg, playlist_name):
        """
        Convert technical error message to user-friendly guidance.

        Args:
            error_msg: Original error message.
            playlist_name: Name of playlist that failed to play.

        Returns:
            str: User-friendly error message with actionable guidance.
        """
        error_lower = error_msg.lower()

        if 'no active device' in error_lower or 'device' in error_lower:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                '⚠ No active Spotify device found.\n'
                'Open Spotify on any device and start playing something, then try again.'
            )
        elif 'authentication' in error_lower or 'token' in error_lower or 'unauthorized' in error_lower:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                '⚠ Authentication expired.\n'
                'Please log in to Spotify again in the Alarmify app.'
            )
        elif 'premium' in error_lower or 'restriction' in error_lower:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                '⚠ Spotify Premium required.\n'
                'Playback control requires a Spotify Premium account.'
            )
        elif 'rate' in error_lower or 'limit' in error_lower or '429' in error_msg:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                '⚠ Rate limit exceeded.\n'
                'Too many requests to Spotify. Wait a few minutes and try again.'
            )
        elif 'network' in error_lower or 'connection' in error_lower or 'timeout' in error_lower:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                '⚠ Network error.\n'
                'Check your internet connection and try again.'
            )
        elif 'not found' in error_lower or '404' in error_msg:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                '⚠ Playlist not found.\n'
                'The playlist may have been deleted or made private.'
            )
        else:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                f'⚠ Error: {error_msg}\n\n'
                'Check your Spotify connection and device status.'
            )

    def _show_notification(self, title, message, success=True):
        """
        Show system tray notification.

        Args:
            title: Notification title.
            message: Notification message.
            success: Whether this is a success (True) or failure (False) notification.
        """
        if self.gui_app and hasattr(self.gui_app, 'show_tray_notification'):
            try:
                from PyQt5.QtWidgets import QSystemTrayIcon
                icon_type = QSystemTrayIcon.Information if success else QSystemTrayIcon.Critical
                self.gui_app.show_tray_notification(title, message, icon_type)
            except Exception as e:
                logger.warning(f"Failed to show tray notification: {e}")

    def get_alarms(self):
        """
        Get list of all scheduled alarms.

        Returns:
            list[dict]: List of alarm info dictionaries with keys:
                - time: Alarm time (HH:MM)
                - playlist: Playlist name
                - playlist_uri: Playlist URI
                - volume: Volume percentage
        """
        with self._alarms_lock:
            alarm_list = [
                {
                    'time': a['time'],
                    'playlist': a['playlist'],
                    'playlist_uri': a['playlist_uri'],
                    'volume': a['volume']
                }
                for a in self.alarms
            ]
            logger.debug(f"Retrieved {len(alarm_list)} alarms")
            return alarm_list

    def get_next_alarm_time(self):
        """
        Get the next scheduled alarm trigger time.

        Returns:
            str: Next alarm time in human-readable format, or None if no alarms.
        """
        with self._alarms_lock:
            if not self.alarms:
                return None
            
            next_job = schedule.next_run()
            if next_job:
                now = datetime.now()
                delta = next_job - now
                
                hours = int(delta.total_seconds() // 3600)
                minutes = int((delta.total_seconds() % 3600) // 60)
                
                if hours > 0:
                    return f"in {hours}h {minutes}m"
                elif minutes > 0:
                    return f"in {minutes}m"
                else:
                    return "soon"
            
            return None

    def remove_alarm(self, time_str):
        """
        Remove an alarm by its scheduled time.

        Cancels the scheduled job and removes from alarm list.

        Args:
            time_str: Time of alarm to remove (HH:MM format).
        """
        logger.info(f"Removing alarm scheduled for {time_str}")
        with self._alarms_lock:
            for alarm in self.alarms[:]:
                if alarm['time'] == time_str:
                    schedule.cancel_job(alarm['job'])
                    self.alarms.remove(alarm)
                    logger.info(
                        f"Alarm removed - Time: {time_str}, Playlist: {alarm['playlist']}. "
                        f"Remaining alarms: {len(self.alarms)}"
                    )
                    break
            else:
                logger.warning(f"Attempted to remove non-existent alarm at {time_str}")

    def clear_all_alarms(self):
        """Remove all scheduled alarms."""
        logger.info("Clearing all alarms")
        with self._alarms_lock:
            alarm_count = len(self.alarms)
            for alarm in self.alarms:
                schedule.cancel_job(alarm['job'])
            self.alarms.clear()
            logger.info(f"All alarms cleared. Removed {alarm_count} alarm(s)")

    def shutdown(self):
        """
        Gracefully shutdown the alarm scheduler.

        Stops the scheduler thread, cancels all scheduled jobs,
        and cleans up resources. Should be called before application exit.
        """
        logger.info("Initiating alarm scheduler shutdown")
        if self.scheduler_running:
            self.scheduler_running = False
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=2.0)
                if self.scheduler_thread.is_alive():
                    logger.warning("Scheduler thread did not stop within timeout period")
                else:
                    logger.info("Scheduler thread stopped successfully")
        
        with self._alarms_lock:
            alarm_count = len(self.alarms)
            for alarm in self.alarms:
                schedule.cancel_job(alarm['job'])
            self.alarms.clear()
            logger.info(f"Alarm scheduler shutdown complete. Cleaned up {alarm_count} alarm(s)")
