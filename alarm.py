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

Dependencies:
- schedule: Job scheduling library
- threading: Background execution
"""

import schedule  # Job scheduling library
import time      # Time-related functions (sleep)
import threading  # Background thread execution


class Alarm:
    """
    Alarm manager for scheduling Spotify playlist playback.

    Maintains a list of scheduled alarms and runs a background
    scheduler thread to trigger them at the specified times.

    Attributes:
        alarms: List of alarm info dictionaries with time, playlist, volume.
        scheduler_running: Boolean flag indicating if scheduler thread is active.
    """

    def __init__(self):
        """Initialize the alarm manager with empty alarm list."""
        # List to store alarm metadata for UI display
        # Each entry: {'time': 'HH:MM', 'playlist': 'name', 'playlist_uri': 'uri', 'volume': 80, 'job': schedule.Job}
        self.alarms = []

        # Flag to track if scheduler thread is running
        self.scheduler_running = False

        # Reference to scheduler thread
        self.scheduler_thread = None

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
        """
        # Create the scheduled job - runs daily at specified time
        # The job calls play_playlist with playlist URI, API, and volume
        job = schedule.every().day.at(time_str).do(
            self.play_playlist,      # Function to call
            playlist_uri,            # Playlist URI argument
            spotify_api,             # API instance argument
            volume                   # Volume argument
        )

        # Store alarm info for management UI
        alarm_info = {
            'time': time_str,        # Alarm time
            'playlist': playlist_name,  # Playlist name for display
            'playlist_uri': playlist_uri,  # Playlist URI for playback
            'volume': volume,        # Volume setting
            'job': job               # Reference to schedule.Job for removal
        }
        self.alarms.append(alarm_info)

        # Start scheduler thread if not already running
        self._ensure_scheduler_running()

    def _ensure_scheduler_running(self):
        """Start the scheduler background thread if not already running."""
        if self.scheduler_running:
            return  # Already running

        def run_scheduler():
            """
            Background scheduler loop.

            Continuously checks for pending jobs and runs them.
            Sleeps 1 second between checks to avoid CPU spinning.
            """
            while self.scheduler_running:
                schedule.run_pending()  # Execute any due jobs
                time.sleep(1)           # Wait 1 second

        # Mark scheduler as running
        self.scheduler_running = True

        # Create and start daemon thread
        # Daemon=True ensures thread stops when main program exits
        self.scheduler_thread = threading.Thread(
            target=run_scheduler,
            daemon=True,
            name='AlarmScheduler'
        )
        self.scheduler_thread.start()

    def play_playlist(self, playlist_uri, spotify_api, volume=80):
        """
        Play a playlist - called by scheduler when alarm triggers.

        Sets the volume first, then starts playlist playback.

        Args:
            playlist_uri: Spotify URI of playlist to play.
            spotify_api: SpotifyAPI instance for control.
            volume: Volume level 0-100.
        """
        try:
            # Set volume before playing
            spotify_api.set_volume(volume)
        except Exception:
            # Volume control may fail if no active device
            # Continue anyway - playback might wake the device
            pass

        try:
            # Start playlist playback by URI
            spotify_api.play_playlist_by_uri(playlist_uri)
        except Exception as e:
            # Log error (could add proper logging later)
            print(f"Alarm playback failed: {e}")

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
        # Return copy without 'job' key (internal implementation detail)
        return [
            {
                'time': a['time'],
                'playlist': a['playlist'],
                'playlist_uri': a['playlist_uri'],
                'volume': a['volume']
            }
            for a in self.alarms
        ]

    def remove_alarm(self, time_str):
        """
        Remove an alarm by its scheduled time.

        Cancels the scheduled job and removes from alarm list.

        Args:
            time_str: Time of alarm to remove (HH:MM format).
        """
        # Find and remove matching alarms
        for alarm in self.alarms[:]:  # Iterate copy to allow removal
            if alarm['time'] == time_str:
                # Cancel the scheduled job
                schedule.cancel_job(alarm['job'])
                # Remove from our list
                self.alarms.remove(alarm)
                break  # Remove first match only

    def clear_all_alarms(self):
        """Remove all scheduled alarms."""
        for alarm in self.alarms:
            schedule.cancel_job(alarm['job'])
        self.alarms.clear()

    def shutdown(self):
        """
        Gracefully shutdown the alarm scheduler.

        Stops the scheduler thread, cancels all scheduled jobs,
        and cleans up resources. Should be called before application exit.
        """
        if self.scheduler_running:
            self.scheduler_running = False
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=2.0)
        
        for alarm in self.alarms:
            schedule.cancel_job(alarm['job'])
        self.alarms.clear()
