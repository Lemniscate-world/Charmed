"""
device_wake_manager.py - Device wake and reliability management for Alarmify

This module provides the DeviceWakeManager class for enhanced alarm reliability.

Features:
- Pre-alarm device wake: Pings devices 60 seconds before alarm trigger
- Retry logic: Monitors device health and retries playback if device becomes inactive
- Fallback notifications: Shows system notifications if playback fails after retries
- Health monitoring: Checks device status every 2 minutes during active alarm window
- Thread-safe operation: All monitoring runs in background threads
- Automatic monitoring duration limit: Stops monitoring after 30 minutes by default

Flow:
1. When alarm is scheduled: Pre-wake timer is set for 60 seconds before alarm time
2. Pre-wake timer fires: Device is activated if inactive, timer auto-reschedules for next day
3. Alarm triggers: Playback starts and health monitoring begins
4. Health checks run every 2 minutes:
   - If device is active: Continue monitoring
   - If device is inactive: Retry playback (up to 3 attempts with device wake)
   - If max retries exceeded: Show fallback notification and stop monitoring
5. After 30 minutes: Monitoring automatically stops

Dependencies:
- threading: Background monitoring threads
- time: Sleep and timing operations
- datetime: Time calculations for alarm windows
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Callable
from logging_config import get_logger

logger = get_logger(__name__)


class DeviceWakeManager:
    """
    Manager for device wake operations and reliability monitoring.
    
    Ensures devices are awake before alarms trigger and monitors device
    health during active alarm windows to retry playback if needed.
    
    Attributes:
        spotify_api: SpotifyAPI instance for device operations.
        gui_app: Reference to GUI application for showing fallback notifications.
        pre_wake_seconds: Seconds before alarm to wake device (default 60).
        health_check_interval: Seconds between device health checks (default 120).
        max_retry_attempts: Maximum playback retry attempts (default 3).
    """
    
    def __init__(self, spotify_api, gui_app=None, 
                 pre_wake_seconds=60, health_check_interval=120, max_retry_attempts=3):
        """
        Initialize the device wake manager.
        
        Args:
            spotify_api: SpotifyAPI instance for device operations.
            gui_app: Reference to GUI application for notifications (optional).
            pre_wake_seconds: Seconds before alarm to wake device (default 60).
            health_check_interval: Seconds between health checks (default 120).
            max_retry_attempts: Maximum retry attempts for playback (default 3).
        """
        logger.info('Initializing DeviceWakeManager')
        self.spotify_api = spotify_api
        self.gui_app = gui_app
        self.pre_wake_seconds = pre_wake_seconds
        self.health_check_interval = health_check_interval
        self.max_retry_attempts = max_retry_attempts
        
        # Thread management
        self._monitoring_active = False
        self._monitoring_thread = None
        self._wake_timers = {}
        self._timers_lock = threading.Lock()
        
        # Active alarm tracking for health monitoring
        self._active_alarms = {}
        self._active_alarms_lock = threading.Lock()
        
        logger.info(
            f'DeviceWakeManager initialized - pre_wake: {pre_wake_seconds}s, '
            f'health_check: {health_check_interval}s, max_retries: {max_retry_attempts}'
        )
    
    def schedule_pre_wake(self, alarm_time_str, alarm_id):
        """
        Schedule a pre-wake operation for an alarm.
        
        Wakes the device 60 seconds before the alarm is scheduled to trigger.
        For recurring alarms, automatically reschedules for the next day after wake.
        
        Args:
            alarm_time_str: Alarm time in HH:MM format.
            alarm_id: Unique identifier for the alarm.
        """
        logger.info(f'Scheduling pre-wake for alarm {alarm_id} at {alarm_time_str}')
        
        # Calculate wake time
        now = datetime.now()
        alarm_time = datetime.strptime(alarm_time_str, '%H:%M').replace(
            year=now.year, month=now.month, day=now.day
        )
        
        # If alarm time is in the past, schedule for tomorrow
        if alarm_time < now:
            alarm_time += timedelta(days=1)
        
        wake_time = alarm_time - timedelta(seconds=self.pre_wake_seconds)
        
        # If wake time is in the past, wake immediately and reschedule for tomorrow
        if wake_time < now:
            logger.info(f'Wake time for alarm {alarm_id} is in the past, waking immediately')
            self._wake_device(alarm_id)
            # Reschedule for tomorrow
            self.schedule_pre_wake(alarm_time_str, alarm_id)
            return
        
        # Schedule wake timer with auto-reschedule callback
        delay = (wake_time - now).total_seconds()
        
        def wake_and_reschedule():
            self._wake_device(alarm_id)
            # Reschedule for next occurrence (tomorrow for daily alarms)
            self.schedule_pre_wake(alarm_time_str, alarm_id)
        
        timer = threading.Timer(delay, wake_and_reschedule)
        timer.daemon = True
        
        with self._timers_lock:
            # Cancel existing timer if present
            if alarm_id in self._wake_timers:
                self._wake_timers[alarm_id].cancel()
            
            self._wake_timers[alarm_id] = timer
            timer.start()
        
        logger.info(
            f'Pre-wake scheduled for alarm {alarm_id} in {delay:.0f} seconds '
            f'(at {wake_time.strftime("%H:%M:%S")})'
        )
    
    def cancel_pre_wake(self, alarm_id):
        """
        Cancel a scheduled pre-wake operation.
        
        Args:
            alarm_id: Unique identifier for the alarm.
        """
        with self._timers_lock:
            if alarm_id in self._wake_timers:
                self._wake_timers[alarm_id].cancel()
                del self._wake_timers[alarm_id]
                logger.info(f'Pre-wake cancelled for alarm {alarm_id}')
    
    def _wake_device(self, alarm_id):
        """
        Wake a Spotify device before alarm triggers.
        
        Attempts to activate a device if none is currently active.
        
        Args:
            alarm_id: Unique identifier for the alarm.
        """
        logger.info(f'Waking device for alarm {alarm_id}')
        
        try:
            # Check for active device
            active_device = self.spotify_api.get_active_device()
            if active_device:
                logger.info(
                    f'Device already active for alarm {alarm_id}: '
                    f'{active_device.get("name")}'
                )
                return
            
            # Try to get available devices and activate one
            devices = self.spotify_api.get_devices()
            if not devices:
                logger.warning(f'No devices available to wake for alarm {alarm_id}')
                return
            
            # Prefer computer/desktop devices
            for device in devices:
                device_type = device.get('type', '').lower()
                if device_type in ['computer', 'desktop']:
                    device_id = device.get('id')
                    if device_id:
                        self.spotify_api.transfer_playback(device_id, force_play=False)
                        logger.info(
                            f'Woke device for alarm {alarm_id}: {device.get("name")} '
                            f'(type: {device_type})'
                        )
                        return
            
            # Fallback to first available device
            first_device = devices[0]
            device_id = first_device.get('id')
            if device_id:
                self.spotify_api.transfer_playback(device_id, force_play=False)
                logger.info(
                    f'Woke fallback device for alarm {alarm_id}: '
                    f'{first_device.get("name")}'
                )
        
        except Exception as e:
            logger.error(f'Failed to wake device for alarm {alarm_id}: {e}', exc_info=True)
    
    def start_alarm_monitoring(self, alarm_id, playlist_uri, playlist_name, 
                               volume, spotify_api, fade_in_enabled=False, 
                               fade_in_duration=10, monitoring_duration_minutes=30):
        """
        Start monitoring an active alarm for device health.
        
        Monitors device status every 2 minutes and retries playback if device
        becomes inactive. Shows fallback notification if all retries fail.
        Automatically stops monitoring after the specified duration.
        
        Args:
            alarm_id: Unique identifier for the alarm.
            playlist_uri: Spotify URI of the playlist.
            playlist_name: Name of the playlist for notifications.
            volume: Target volume level.
            spotify_api: SpotifyAPI instance.
            fade_in_enabled: Whether fade-in is enabled.
            fade_in_duration: Fade-in duration in minutes.
            monitoring_duration_minutes: Duration to monitor alarm (default 30 minutes).
        """
        logger.info(f'Starting alarm monitoring for alarm {alarm_id}: {playlist_name}')
        
        alarm_data = {
            'playlist_uri': playlist_uri,
            'playlist_name': playlist_name,
            'volume': volume,
            'spotify_api': spotify_api,
            'fade_in_enabled': fade_in_enabled,
            'fade_in_duration': fade_in_duration,
            'retry_count': 0,
            'start_time': datetime.now(),
            'monitoring_duration_minutes': monitoring_duration_minutes
        }
        
        with self._active_alarms_lock:
            self._active_alarms[alarm_id] = alarm_data
        
        # Start health monitoring thread if not already running
        if not self._monitoring_active:
            self._start_health_monitoring()
        
        logger.info(f'Alarm monitoring started for {alarm_id} (duration: {monitoring_duration_minutes} minutes)')
    
    def stop_alarm_monitoring(self, alarm_id):
        """
        Stop monitoring an alarm.
        
        Args:
            alarm_id: Unique identifier for the alarm.
        """
        with self._active_alarms_lock:
            if alarm_id in self._active_alarms:
                del self._active_alarms[alarm_id]
                logger.info(f'Stopped monitoring alarm {alarm_id}')
    
    def _start_health_monitoring(self):
        """Start the background health monitoring thread."""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        
        def monitor_loop():
            """Background thread loop for health monitoring."""
            logger.info('Health monitoring thread started')
            
            while self._monitoring_active:
                try:
                    self._check_alarm_health()
                except Exception as e:
                    logger.error(f'Error in health monitoring loop: {e}', exc_info=True)
                
                # Sleep in small intervals to allow quick shutdown
                for _ in range(self.health_check_interval):
                    if not self._monitoring_active:
                        break
                    time.sleep(1)
            
            logger.info('Health monitoring thread stopped')
        
        self._monitoring_thread = threading.Thread(
            target=monitor_loop,
            daemon=True,
            name='DeviceHealthMonitor'
        )
        self._monitoring_thread.start()
        logger.info('Health monitoring thread initialized')
    
    def _check_alarm_health(self):
        """
        Check health of all active alarms.
        
        Verifies that devices are still active and retries playback if needed.
        """
        with self._active_alarms_lock:
            if not self._active_alarms:
                # No active alarms, can stop monitoring
                self._monitoring_active = False
                return
            
            alarms_to_check = list(self._active_alarms.items())
        
        for alarm_id, alarm_data in alarms_to_check:
            try:
                self._check_single_alarm(alarm_id, alarm_data)
            except Exception as e:
                logger.error(
                    f'Error checking alarm {alarm_id}: {e}',
                    exc_info=True
                )
    
    def _check_single_alarm(self, alarm_id, alarm_data):
        """
        Check health of a single alarm.
        
        Args:
            alarm_id: Unique identifier for the alarm.
            alarm_data: Dictionary containing alarm information.
        """
        spotify_api = alarm_data['spotify_api']
        retry_count = alarm_data['retry_count']
        start_time = alarm_data['start_time']
        monitoring_duration_minutes = alarm_data.get('monitoring_duration_minutes', 30)
        
        # Check if monitoring duration has been exceeded
        elapsed_time = datetime.now() - start_time
        if elapsed_time.total_seconds() / 60 > monitoring_duration_minutes:
            logger.info(
                f'Monitoring duration exceeded for alarm {alarm_id} '
                f'({monitoring_duration_minutes} minutes), stopping monitoring'
            )
            self.stop_alarm_monitoring(alarm_id)
            return
        
        logger.debug(f'Checking health for alarm {alarm_id} (retries: {retry_count})')
        
        # Check if device is still active
        try:
            active_device = spotify_api.get_active_device()
            
            if not active_device:
                logger.warning(
                    f'Device inactive for alarm {alarm_id}, attempting retry '
                    f'(attempt {retry_count + 1}/{self.max_retry_attempts})'
                )
                
                if retry_count < self.max_retry_attempts:
                    # Retry playback
                    self._retry_playback(alarm_id, alarm_data)
                else:
                    # Max retries exceeded, show fallback notification
                    logger.error(
                        f'Max retries exceeded for alarm {alarm_id}, '
                        f'showing fallback notification'
                    )
                    self._show_fallback_notification(alarm_data)
                    self.stop_alarm_monitoring(alarm_id)
        
        except Exception as e:
            logger.error(f'Failed to check device status for alarm {alarm_id}: {e}')
    
    def _retry_playback(self, alarm_id, alarm_data):
        """
        Retry playback for an alarm.
        
        Args:
            alarm_id: Unique identifier for the alarm.
            alarm_data: Dictionary containing alarm information.
        """
        try:
            spotify_api = alarm_data['spotify_api']
            playlist_uri = alarm_data['playlist_uri']
            volume = alarm_data['volume']
            fade_in_enabled = alarm_data['fade_in_enabled']
            
            logger.info(f'Retrying playback for alarm {alarm_id}')
            
            # Try to wake device first
            self._wake_device(alarm_id)
            time.sleep(2)
            
            # Set volume
            if fade_in_enabled:
                spotify_api.set_volume(0)
            else:
                spotify_api.set_volume(volume)
            
            # Start playback
            spotify_api.play_playlist_by_uri(playlist_uri)
            
            logger.info(f'Successfully retried playback for alarm {alarm_id}')
            
            # Increment retry count
            with self._active_alarms_lock:
                if alarm_id in self._active_alarms:
                    self._active_alarms[alarm_id]['retry_count'] += 1
        
        except Exception as e:
            logger.error(f'Failed to retry playback for alarm {alarm_id}: {e}')
            
            # Increment retry count even on failure
            with self._active_alarms_lock:
                if alarm_id in self._active_alarms:
                    self._active_alarms[alarm_id]['retry_count'] += 1
    
    def _show_fallback_notification(self, alarm_data):
        """
        Show a system notification as fallback when playback fails.
        
        Args:
            alarm_data: Dictionary containing alarm information.
        """
        playlist_name = alarm_data['playlist_name']
        
        title = 'Alarm Notification'
        message = (
            f'⏰ Alarm Time!\n\n'
            f'Unable to play: {playlist_name}\n\n'
            f'Device became inactive after multiple retry attempts.\n'
            f'Please check your Spotify device.'
        )
        
        logger.info(f'Showing fallback notification for playlist: {playlist_name}')
        
        if self.gui_app and hasattr(self.gui_app, 'show_tray_notification'):
            try:
                from PyQt5.QtWidgets import QSystemTrayIcon
                self.gui_app.show_tray_notification(
                    title, message, QSystemTrayIcon.Warning
                )
            except Exception as e:
                logger.error(f'Failed to show fallback notification: {e}')
        else:
            logger.warning('No GUI app available for fallback notification')
    
    def shutdown(self):
        """
        Gracefully shutdown the device wake manager.
        
        Cancels all timers and stops monitoring threads.
        """
        logger.info('Shutting down DeviceWakeManager')
        
        # Stop monitoring
        self._monitoring_active = False
        
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=3.0)
            if self._monitoring_thread.is_alive():
                logger.warning('Health monitoring thread did not stop within timeout')
        
        # Cancel all wake timers
        with self._timers_lock:
            for alarm_id, timer in list(self._wake_timers.items()):
                timer.cancel()
            self._wake_timers.clear()
        
        # Clear active alarms
        with self._active_alarms_lock:
            self._active_alarms.clear()
        
        logger.info('DeviceWakeManager shutdown complete')
