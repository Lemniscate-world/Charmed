"""
alarm.py - Alarm scheduling module for Alarmify

This module provides the Alarm class for scheduling playlist alarms.
Uses the 'schedule' library for daily recurring tasks and runs
the scheduler in a background daemon thread.

Features:
- Schedule alarms at specific times (HH:MM format)
- Store alarm metadata (time, playlist, volume, fade-in settings)
- List all scheduled alarms
- Remove individual alarms
- Set volume before playing
- Gradual volume fade-in (5-30 minutes) with smooth linear progression
- Thread-safe alarm list management
- Retry logic with exponential backoff for Spotify API failures
- System tray notifications for alarm trigger status
- Snooze functionality with fade-in preservation

Fade-In Implementation:
- FadeInController: QTimer-based volume controller with 5-second intervals
- Smooth linear volume ramp from 0% to target volume
- Configurable duration between 5-30 minutes
- Thread-safe operation compatible with concurrent alarms
- Preview mode for testing fade-in before alarm triggers

Dependencies:
- schedule: Job scheduling library
- threading: Background execution and synchronization
- PyQt5: QTimer and signals for fade-in controller (optional)
"""

import schedule  # Job scheduling library
import time      # Time-related functions (sleep)
import threading  # Background thread execution
from datetime import datetime  # Date and time utilities
import re
from logging_config import get_logger

logger = get_logger(__name__)

try:
    from PyQt5.QtCore import QTimer, QObject, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    logger.warning("PyQt5 not available - fade-in feature will not be available")


if PYQT_AVAILABLE:
    class FadeInController(QObject):
        """
        Controller for gradual volume fade-in using QTimer.
        
        Increases volume from 0 to target volume over the specified duration
        using incremental steps at regular intervals.
        
        Attributes:
            spotify_api: SpotifyAPI instance for volume control.
            target_volume: Final volume level (0-100).
            duration_minutes: Total fade-in duration in minutes.
            step_interval_ms: Milliseconds between volume updates.
        """
        
        fade_complete = pyqtSignal()
        
        def __init__(self, spotify_api, target_volume, duration_minutes):
            """
            Initialize the fade-in controller.
            
            Args:
                spotify_api: SpotifyAPI instance for volume control.
                target_volume: Final volume level (0-100).
                duration_minutes: Total fade-in duration in minutes (5-30).
            """
            super().__init__()
            self.spotify_api = spotify_api
            self.target_volume = target_volume
            self.duration_minutes = duration_minutes
            
            # Calculate fade parameters
            self.step_interval_ms = 5000  # 5 seconds between updates
            self.total_steps = int((duration_minutes * 60 * 1000) / self.step_interval_ms)
            self.volume_step = target_volume / self.total_steps
            
            self.current_volume = 0
            self.current_step = 0
            self.is_active = False
            
            # Create timer for incremental updates
            self.timer = QTimer()
            self.timer.timeout.connect(self._update_volume)
            
            logger.info(
                f"FadeInController initialized - target: {target_volume}%, "
                f"duration: {duration_minutes}min, steps: {self.total_steps}"
            )
        
        def start(self):
            """Start the fade-in process."""
            if self.is_active:
                logger.warning("Fade-in already active")
                return
            
            self.is_active = True
            self.current_volume = 0
            self.current_step = 0
            
            # Set initial volume to 0
            try:
                self.spotify_api.set_volume(0)
                logger.info(f"Starting fade-in over {self.duration_minutes} minutes")
            except Exception as e:
                logger.error(f"Failed to set initial volume: {e}")
            
            # Start timer
            self.timer.start(self.step_interval_ms)
        
        def _update_volume(self):
            """Update volume by one step."""
            if not self.is_active:
                return
            
            self.current_step += 1
            self.current_volume = min(
                int(self.current_step * self.volume_step),
                self.target_volume
            )
            
            try:
                self.spotify_api.set_volume(self.current_volume)
                logger.debug(
                    f"Fade-in step {self.current_step}/{self.total_steps}: "
                    f"volume={self.current_volume}%"
                )
            except Exception as e:
                logger.error(f"Failed to update volume during fade-in: {e}")
            
            # Check if fade-in is complete
            if self.current_step >= self.total_steps:
                self.stop()
                self.fade_complete.emit()
                logger.info(f"Fade-in complete at {self.target_volume}%")
        
        def stop(self):
            """Stop the fade-in process."""
            if not self.is_active:
                return
            
            self.is_active = False
            self.timer.stop()
            logger.info("Fade-in stopped")
        
        def is_running(self):
            """Check if fade-in is currently active."""
            return self.is_active


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
        self.snoozed_alarms = []
        self.scheduler_running = False
        self.scheduler_thread = None
        self._alarms_lock = threading.Lock()
        self.gui_app = gui_app
        self.active_fade_controller = None
        logger.info("Alarm manager initialized")

    def set_alarm(self, time_str, playlist_name, playlist_uri, spotify_api, volume=80, 
                   fade_in_enabled=False, fade_in_duration=10, days=None):
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
            fade_in_enabled: Whether to enable gradual volume fade-in (default False).
            fade_in_duration: Fade-in duration in minutes, 5-30 (default 10).
            days: List of weekday names ('Monday', 'Tuesday', etc.), or special values
                  'weekdays' (Mon-Fri), 'weekends' (Sat-Sun), or None for every day (default None).

        Raises:
            ValueError: If time format is invalid.
        """
        logger.info(
            f"Scheduling alarm - Time: {time_str}, Playlist: {playlist_name}, "
            f"URI: {playlist_uri}, Volume: {volume}%, "
            f"Fade-in: {fade_in_enabled}, Duration: {fade_in_duration}min, Days: {days}"
        )

        if not self._validate_time_format(time_str):
            error_msg = f'Invalid time format: {time_str}. Expected HH:MM (24-hour format).'
            logger.error(f"Invalid time format for alarm: {time_str}")
            raise ValueError(error_msg)

        # Parse and normalize days parameter
        active_days = self._parse_days(days)
        
        job = schedule.every().day.at(time_str).do(
            self._conditional_play_playlist,
            playlist_uri,
            spotify_api,
            volume,
            playlist_name,
            fade_in_enabled,
            fade_in_duration,
            active_days
        )

        alarm_info = {
            'time': time_str,
            'playlist': playlist_name,
            'playlist_uri': playlist_uri,
            'volume': volume,
            'fade_in_enabled': fade_in_enabled,
            'fade_in_duration': fade_in_duration,
            'days': active_days,
            'job': job
        }
        
        with self._alarms_lock:
            self.alarms.append(alarm_info)
            logger.info(f"Alarm successfully scheduled for {time_str} on {self._format_days_display(active_days)}. Total alarms: {len(self.alarms)}")

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

    def _parse_days(self, days):
        """
        Parse days parameter into a list of weekday names.

        Args:
            days: List of weekday names, 'weekdays', 'weekends', or None.

        Returns:
            list: List of weekday names ('Monday', 'Tuesday', etc.) or None for all days.
        """
        if days is None:
            return None
        
        if isinstance(days, str):
            if days.lower() == 'weekdays':
                return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            elif days.lower() == 'weekends':
                return ['Saturday', 'Sunday']
            else:
                days = [days]
        
        # Normalize day names
        day_mapping = {
            'mon': 'Monday', 'monday': 'Monday',
            'tue': 'Tuesday', 'tuesday': 'Tuesday',
            'wed': 'Wednesday', 'wednesday': 'Wednesday',
            'thu': 'Thursday', 'thursday': 'Thursday',
            'fri': 'Friday', 'friday': 'Friday',
            'sat': 'Saturday', 'saturday': 'Saturday',
            'sun': 'Sunday', 'sunday': 'Sunday'
        }
        
        normalized_days = []
        for day in days:
            day_lower = day.lower()
            if day_lower in day_mapping:
                normalized_days.append(day_mapping[day_lower])
            else:
                logger.warning(f"Unknown day name: {day}, ignoring")
        
        return normalized_days if normalized_days else None

    def _format_days_display(self, days):
        """
        Format days list for display.

        Args:
            days: List of weekday names or None.

        Returns:
            str: Formatted string for display.
        """
        if days is None:
            return 'Every day'
        
        if len(days) == 7:
            return 'Every day'
        
        if set(days) == {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}:
            return 'Weekdays'
        
        if set(days) == {'Saturday', 'Sunday'}:
            return 'Weekends'
        
        # Abbreviate day names
        abbrev = {
            'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
            'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'
        }
        
        return ', '.join([abbrev.get(day, day) for day in days])

    def _conditional_play_playlist(self, playlist_uri, spotify_api, volume, playlist_name,
                                    fade_in_enabled, fade_in_duration, active_days):
        """
        Conditionally play playlist based on active days.

        Checks if today is in the active days list before playing.

        Args:
            playlist_uri: Spotify URI of playlist to play.
            spotify_api: SpotifyAPI instance for control.
            volume: Volume level 0-100.
            playlist_name: Name of playlist for notifications.
            fade_in_enabled: Whether to enable gradual volume fade-in.
            fade_in_duration: Fade-in duration in minutes.
            active_days: List of weekday names or None for all days.
        """
        # If no specific days set, play every day
        if active_days is None:
            self.play_playlist(playlist_uri, spotify_api, volume, playlist_name,
                             fade_in_enabled, fade_in_duration)
            return
        
        # Check if today is in active days
        from datetime import datetime
        today_name = datetime.now().strftime('%A')
        
        if today_name in active_days:
            logger.info(f"Today ({today_name}) is in active days {active_days}, playing alarm")
            self.play_playlist(playlist_uri, spotify_api, volume, playlist_name,
                             fade_in_enabled, fade_in_duration)
        else:
            logger.info(f"Today ({today_name}) is not in active days {active_days}, skipping alarm")

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

    def play_playlist(self, playlist_uri, spotify_api, volume=80, playlist_name='Playlist',
                     fade_in_enabled=False, fade_in_duration=10):
        """
        Play a playlist - called by scheduler when alarm triggers.

        Sets the volume first, then starts playlist playback with retry logic.
        Auto-wakes Spotify device before playing. Optionally starts fade-in.

        Args:
            playlist_uri: Spotify URI of playlist to play.
            spotify_api: SpotifyAPI instance for control.
            volume: Volume level 0-100.
            playlist_name: Name of playlist for notifications.
            fade_in_enabled: Whether to enable gradual volume fade-in.
            fade_in_duration: Fade-in duration in minutes.
        """
        logger.info(
            f"Alarm triggered - Playing playlist: {playlist_name} ({playlist_uri}) "
            f"at volume {volume}%, fade-in: {fade_in_enabled}"
        )

        # Auto-wake Spotify device before alarm
        try:
            self._wake_spotify_device(spotify_api)
        except Exception as e:
            logger.warning(f"Failed to wake Spotify device: {e}")

        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                # If fade-in is enabled, start at volume 0 and use controller
                if fade_in_enabled and PYQT_AVAILABLE:
                    self._set_volume_with_retry(spotify_api, 0, max_retries=2)
                else:
                    self._set_volume_with_retry(spotify_api, volume, max_retries=2)

                spotify_api.play_playlist_by_uri(playlist_uri)

                # Start fade-in if enabled
                if fade_in_enabled and PYQT_AVAILABLE:
                    self._start_fade_in(spotify_api, volume, fade_in_duration, playlist_name)
                
                success_msg = f'Alarm triggered successfully!\nPlaying: {playlist_name}'
                if fade_in_enabled:
                    success_msg += f'\nVolume fading in over {fade_in_duration} minutes'
                
                # Prepare alarm data for snooze functionality
                alarm_data = {
                    'playlist_uri': playlist_uri,
                    'playlist_name': playlist_name,
                    'volume': volume,
                    'fade_in_enabled': fade_in_enabled,
                    'fade_in_duration': fade_in_duration,
                    'spotify_api': spotify_api
                }
                
                self._show_notification('Alarm Success', success_msg, success=True, alarm_data=alarm_data)
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

    def _wake_spotify_device(self, spotify_api):
        """
        Wake Spotify device before alarm triggers.
        
        Attempts to activate a device if none is active.
        
        Args:
            spotify_api: SpotifyAPI instance.
        """
        try:
            # Check for active device
            active_device = spotify_api.get_active_device()
            if active_device:
                logger.debug("Spotify device already active")
                return
            
            # Try to get available devices and activate one
            devices = spotify_api.get_devices()
            if devices:
                # Prefer computer/desktop devices
                for device in devices:
                    device_type = device.get('type', '').lower()
                    if device_type in ['computer', 'desktop']:
                        device_id = device.get('id')
                        if device_id:
                            spotify_api.transfer_playback(device_id, force_play=False)
                            logger.info(f"Woke up Spotify device: {device.get('name')}")
                            return
                
                # Fallback to first available device
                first_device = devices[0]
                device_id = first_device.get('id')
                if device_id:
                    spotify_api.transfer_playback(device_id, force_play=False)
                    logger.info(f"Woke up Spotify device: {first_device.get('name')}")
        except Exception as e:
            logger.warning(f"Could not wake Spotify device: {e}")
            # Don't raise - this is best effort

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
    
    def _start_fade_in(self, spotify_api, target_volume, duration_minutes, playlist_name):
        """
        Start gradual volume fade-in.
        
        Args:
            spotify_api: SpotifyAPI instance for volume control.
            target_volume: Final volume level (0-100).
            duration_minutes: Fade-in duration in minutes.
            playlist_name: Name of playlist for logging.
        """
        if not PYQT_AVAILABLE:
            logger.warning("PyQt5 not available - cannot start fade-in")
            return
        
        try:
            # Stop any existing fade-in
            if self.active_fade_controller and self.active_fade_controller.is_running():
                self.active_fade_controller.stop()
            
            # Create new fade-in controller
            self.active_fade_controller = FadeInController(
                spotify_api, target_volume, duration_minutes
            )
            self.active_fade_controller.start()
            
            logger.info(
                f"Started fade-in for {playlist_name}: "
                f"{duration_minutes}min to {target_volume}%"
            )
        except Exception as e:
            logger.error(f"Failed to start fade-in: {e}", exc_info=True)

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

        if 'premium' in error_lower or 'premium_required' in error_lower:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                '⚠️ Spotify Premium required.\n\n'
                'Alarmify requires Spotify Premium for playback control.\n'
                'Upgrade at: https://www.spotify.com/premium\n\n'
                'Free users: Alarmify will show a notification instead.'
            )
        elif 'no active device' in error_lower or 'device' in error_lower:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                '⚠️ No active Spotify device found.\n'
                'Open Spotify on any device and start playing something, then try again.'
            )
        elif 'authentication' in error_lower or 'token' in error_lower or 'unauthorized' in error_lower:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                'ÔÜá Authentication expired.\n'
                'Please log in to Spotify again in the Alarmify app.'
            )
        elif 'premium' in error_lower or 'restriction' in error_lower:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                'ÔÜá Spotify Premium required.\n'
                'Playback control requires a Spotify Premium account.'
            )
        elif 'rate' in error_lower or 'limit' in error_lower or '429' in error_msg:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                'ÔÜá Rate limit exceeded.\n'
                'Too many requests to Spotify. Wait a few minutes and try again.'
            )
        elif 'network' in error_lower or 'connection' in error_lower or 'timeout' in error_lower:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                'ÔÜá Network error.\n'
                'Check your internet connection and try again.'
            )
        elif 'not found' in error_lower or '404' in error_msg:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                'ÔÜá Playlist not found.\n'
                'The playlist may have been deleted or made private.'
            )
        else:
            return (
                f'Failed to play "{playlist_name}"\n\n'
                f'ÔÜá Error: {error_msg}\n\n'
                'Check your Spotify connection and device status.'
            )

    def _show_notification(self, title, message, success=True, alarm_data=None):
        """
        Show system tray notification.

        Args:
            title: Notification title.
            message: Notification message.
            success: Whether this is a success (True) or failure (False) notification.
            alarm_data: Optional alarm data dict for snooze functionality.
        """
        if self.gui_app and hasattr(self.gui_app, 'show_tray_notification'):
            try:
                from PyQt5.QtWidgets import QSystemTrayIcon
                icon_type = QSystemTrayIcon.Information if success else QSystemTrayIcon.Critical
                
                # Show snooze dialog if alarm_data provided and success
                if success and alarm_data:
                    self.gui_app.show_snooze_notification(title, message, alarm_data, icon_type)
                else:
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
                - fade_in_enabled: Whether fade-in is enabled
                - fade_in_duration: Fade-in duration in minutes
                - days: List of active days or None for every day
        """
        with self._alarms_lock:
            alarm_list = [
                {
                    'time': a['time'],
                    'playlist': a['playlist'],
                    'playlist_uri': a['playlist_uri'],
                    'volume': a['volume'],
                    'fade_in_enabled': a.get('fade_in_enabled', False),
                    'fade_in_duration': a.get('fade_in_duration', 10),
                    'days': a.get('days')
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

    def snooze_alarm(self, alarm_data, snooze_minutes=5):
        """
        Snooze an alarm by rescheduling it for a specified number of minutes later.

        Creates a one-time job that will trigger after the snooze duration.
        Tracks the snoozed alarm separately from regular recurring alarms.

        Args:
            alarm_data: Dictionary containing alarm information (playlist_uri, playlist_name, 
                       volume, fade_in_enabled, fade_in_duration, spotify_api).
            snooze_minutes: Number of minutes to snooze (default 5).
        """
        logger.info(
            f"Snoozing alarm - Playlist: {alarm_data.get('playlist_name')}, "
            f"Duration: {snooze_minutes} minutes"
        )

        from datetime import datetime, timedelta
        
        snooze_time = datetime.now() + timedelta(minutes=snooze_minutes)
        time_str = snooze_time.strftime('%H:%M:%S')
        
        # Schedule one-time job for snooze
        job = schedule.every().day.at(time_str).do(
            self.play_playlist,
            alarm_data.get('playlist_uri'),
            alarm_data.get('spotify_api'),
            alarm_data.get('volume', 80),
            alarm_data.get('playlist_name', 'Playlist'),
            alarm_data.get('fade_in_enabled', False),
            alarm_data.get('fade_in_duration', 10)
        )
        
        # Track as snoozed alarm
        snooze_info = {
            'snooze_time': snooze_time,
            'original_playlist': alarm_data.get('playlist_name'),
            'snooze_duration': snooze_minutes,
            'job': job
        }
        
        with self._alarms_lock:
            self.snoozed_alarms.append(snooze_info)
            logger.info(
                f"Alarm snoozed for {snooze_minutes} minutes. "
                f"Will trigger at {time_str}. Total snoozed alarms: {len(self.snoozed_alarms)}"
            )
        
        self._ensure_scheduler_running()

    def get_snoozed_alarms(self):
        """
        Get list of currently snoozed alarms.

        Returns:
            list[dict]: List of snoozed alarm info dictionaries with keys:
                - snooze_time: Datetime when alarm will trigger
                - original_playlist: Name of playlist
                - snooze_duration: Duration of snooze in minutes
        """
        with self._alarms_lock:
            from datetime import datetime
            # Filter out expired snoozes
            now = datetime.now()
            active_snoozes = [
                {
                    'snooze_time': s['snooze_time'],
                    'original_playlist': s['original_playlist'],
                    'snooze_duration': s['snooze_duration']
                }
                for s in self.snoozed_alarms
                if s['snooze_time'] > now
            ]
            
            # Clean up expired snoozes
            self.snoozed_alarms = [
                s for s in self.snoozed_alarms
                if s['snooze_time'] > now
            ]
            
            logger.debug(f"Retrieved {len(active_snoozes)} active snoozed alarms")
            return active_snoozes

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
            snoozed_count = len(self.snoozed_alarms)
            
            for alarm in self.alarms:
                schedule.cancel_job(alarm['job'])
            self.alarms.clear()
            
            for snooze in self.snoozed_alarms:
                schedule.cancel_job(snooze['job'])
            self.snoozed_alarms.clear()
            
            logger.info(
                f"Alarm scheduler shutdown complete. "
                f"Cleaned up {alarm_count} alarm(s) and {snoozed_count} snoozed alarm(s)"
            )
