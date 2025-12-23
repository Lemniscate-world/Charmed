"""
Modern Flet-based GUI for Alarmify
Beautiful, modern UI with Material Design
"""

import flet as ft
from flet import colors
from datetime import datetime, time
import asyncio
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

# Import existing backend
from alarm import Alarm
from spotify_api.spotify_api import ThreadSafeSpotifyAPI
from spotify_api.mock_spotify import MockThreadSafeSpotifyAPI

logger = logging.getLogger(__name__)


class AlarmifyApp:
    """Modern Flet-based Alarmify application"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Alarmify"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(
            color_scheme_seed="#1DB954",
            use_material3=True,
        )
        self.page.padding = 0
        self.page.bgcolor = "#0a0a0a"
        
        # Backend
        test_mode = os.getenv('ALARMIFY_TEST_MODE', 'False').lower() == 'true'
        if test_mode:
            self.spotify_api = MockThreadSafeSpotifyAPI()
        else:
            self.spotify_api = ThreadSafeSpotifyAPI()
        
        # Initialize alarm with simple GUI adapter
        class SimpleGUI:
            def show_tray_notification(self, title, message, icon_type=None):
                pass  # Flet handles notifications differently
        
        self.alarm = Alarm(SimpleGUI())
        
        # UI State
        self.playlists = []
        self.devices = []
        self.selected_playlist = None
        self.selected_device = None
        self.alarm_time = time(7, 0)
        self.volume = 80
        
        # Build UI
        self._build_ui()
        
        # Load data
        self._load_initial_data()
    
    def _build_ui(self):
        """Build the beautiful modern UI"""
        
        # App Bar
        app_bar = ft.AppBar(
            title=ft.Text(
                "Alarmify",
                size=28,
                weight=ft.FontWeight.BOLD,
                color="#1DB954",
            ),
            bgcolor="#1a1a1a",
            actions=[
                ft.IconButton(
                    ft.icons.REFRESH,
                    tooltip="Refresh",
                    on_click=self._refresh_data,
                ),
                ft.IconButton(
                    ft.icons.SETTINGS,
                    tooltip="Settings",
                    on_click=self._open_settings,
                ),
            ],
        )
        
        # Status indicators
        self.auth_status = ft.Chip(
            label=ft.Text("Not connected"),
            bgcolor="#B71C1C",
            content_padding=ft.padding.symmetric(horizontal=12, vertical=6),
        )
        
        self.device_status = ft.Chip(
            label=ft.Text("No device"),
            bgcolor="#424242",
            content_padding=ft.padding.symmetric(horizontal=12, vertical=6),
        )
        
        status_row = ft.Row(
            [self.auth_status, self.device_status],
            alignment=ft.MainAxisAlignment.END,
        )
        
        # Playlist search
        self.search_field = ft.TextField(
            label="Search playlists...",
            prefix_icon=ft.icons.SEARCH,
            bgcolor="#1a1a1a",
            border_color="#616161",
            focused_border_color="#1DB954",
            color="#FFFFFF",
            on_change=self._filter_playlists,
        )
        
        # Playlist list
        self.playlist_list = ft.ListView(
            expand=True,
            spacing=8,
            padding=8,
        )
        
        playlist_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Your Playlists",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE,
                        ),
                        self.search_field,
                        ft.Container(
                            content=self.playlist_list,
                            expand=True,
                            border=ft.border.all(1, "#424242"),
                            border_radius=12,
                            bgcolor="#1a1a1a",
                            padding=8,
                        ),
                    ],
                    spacing=12,
                    expand=True,
                ),
                padding=16,
            ),
            color=ft.colors.GREY_900,
            elevation=2,
        )
        
        # Time picker
        self.time_display = ft.Text(
            "07:00",
            size=48,
            weight=ft.FontWeight.BOLD,
            color="#1DB954",
            font_family="monospace",
        )
        
        self.time_picker = ft.TimePicker(
            value=ft.Time(7, 0),
            on_change=self._on_time_changed,
        )
        
        time_button = ft.ElevatedButton(
            content=self.time_display,
            on_click=lambda _: self.time_picker.pick_time(),
            bgcolor="#1a1a1a",
            color="#1DB954",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            height=80,
        )
        
        # Volume slider
        self.volume_slider = ft.Slider(
            min=0,
            max=100,
            value=80,
            divisions=20,
            label="{value}%",
            active_color="#1DB954",
            on_change=self._on_volume_changed,
        )
        
        # Device selector
        self.device_dropdown = ft.Dropdown(
            label="Playback Device",
            bgcolor="#1a1a1a",
            border_color="#616161",
            focused_border_color="#1DB954",
            color="#FFFFFF",
            options=[ft.dropdown.Option("Auto (Use Active Device)", "auto")],
            on_change=self._on_device_changed,
        )
        
        # Buttons
        self.login_button = ft.ElevatedButton(
            "Login to Spotify",
            icon=ft.icons.SPOTIFY,
            on_click=self._login,
            bgcolor="#1DB954",
            color="#000000",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
            ),
        )
        
        self.set_alarm_button = ft.ElevatedButton(
            "Set Alarm",
            icon=ft.icons.ALARM,
            on_click=self._set_alarm,
            bgcolor="#1DB954",
            color="#000000",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
            ),
        )
        
        self.manage_alarms_button = ft.ElevatedButton(
            "Manage Alarms",
            icon=ft.icons.LIST,
            on_click=self._manage_alarms,
            bgcolor="#424242",
            color="#FFFFFF",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
            ),
        )
        
        # Right panel
        right_panel = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Alarm Settings",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                        ft.Divider(color="#424242"),
                        ft.Text("Alarm Time", size=16, color="#BDBDBD"),
                        time_button,
                        ft.Text("Volume", size=16, color="#BDBDBD"),
                        self.volume_slider,
                        ft.Text("Device", size=16, color="#BDBDBD"),
                        self.device_dropdown,
                        ft.Divider(color="#424242"),
                        self.set_alarm_button,
                        self.manage_alarms_button,
                    ],
                    spacing=16,
                    expand=True,
                ),
                padding=24,
            ),
            color=ft.colors.GREY_900,
            elevation=2,
        )
        
        # Main layout
        self.page.add(
            app_bar,
            ft.Container(
                content=status_row,
                padding=ft.padding.only(right=16, top=8),
            ),
            ft.Row(
                [
                    ft.Container(
                        content=playlist_card,
                        expand=2,
                        margin=ft.margin.all(16),
                    ),
                    ft.Container(
                        content=right_panel,
                        expand=1,
                        margin=ft.margin.all(16),
                    ),
                ],
                expand=True,
            ),
        )
        
        # Add time picker to page
        self.page.overlay.append(self.time_picker)
    
    def _load_initial_data(self):
        """Load playlists and devices"""
        if self.spotify_api.is_authenticated():
            self._load_playlists()
            self._refresh_devices()
            self._update_auth_status(True)
        else:
            self._update_auth_status(False)
    
    def _load_playlists(self):
        """Load playlists from Spotify"""
        try:
            playlists = self.spotify_api.get_user_playlists()
            self.playlists = playlists
            self._update_playlist_list(playlists)
        except Exception as e:
            logger.error(f"Failed to load playlists: {e}")
    
    def _update_playlist_list(self, playlists):
        """Update playlist list UI"""
        self.playlist_list.controls.clear()
        
        for playlist in playlists:
            playlist_item = ft.ListTile(
                leading=ft.CircleAvatar(
                    content=ft.Text(playlist.get('name', '?')[0].upper()),
                    bgcolor="#1DB954",
                    color="#000000",
                ),
                title=ft.Text(
                    playlist.get('name', 'Unknown'),
                    color="#FFFFFF",
                    weight=ft.FontWeight.BOLD,
                ),
                subtitle=ft.Text(
                    f"{playlist.get('track_count', 0)} tracks",
                    color="#BDBDBD",
                ),
                on_click=lambda e, p=playlist: self._select_playlist(p),
                bgcolor="#1a1a1a",
            )
            self.playlist_list.controls.append(playlist_item)
        
        self.page.update()
    
    def _select_playlist(self, playlist):
        """Select a playlist"""
        self.selected_playlist = playlist
        logger.info(f"Selected playlist: {playlist.get('name')}")
    
    def _filter_playlists(self, e):
        """Filter playlists by search"""
        query = e.control.value.lower()
        filtered = [
            p for p in self.playlists
            if query in p.get('name', '').lower()
        ]
        self._update_playlist_list(filtered)
    
    def _on_time_changed(self, e):
        """Handle time change"""
        self.alarm_time = e.control.value
        self.time_display.value = f"{self.alarm_time.hour:02d}:{self.alarm_time.minute:02d}"
        self.page.update()
    
    def _on_volume_changed(self, e):
        """Handle volume change"""
        self.volume = int(e.control.value)
    
    def _on_device_changed(self, e):
        """Handle device change"""
        self.selected_device = e.control.value
    
    def _login(self, e):
        """Login to Spotify"""
        try:
            self.spotify_api.authenticate()
            self._load_playlists()
            self._refresh_devices()
            self._update_auth_status(True)
        except Exception as e:
            logger.error(f"Login failed: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Login failed: {e}"),
                bgcolor="#F44336",
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _set_alarm(self, e):
        """Set an alarm"""
        if not self.selected_playlist:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Please select a playlist"),
                bgcolor="#FF9800",
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        try:
            playlist_uri = self.selected_playlist.get('uri')
            device_id = self.selected_device if self.selected_device != "auto" else None
            
            # Convert time object to HH:MM string
            time_str = f"{self.alarm_time.hour:02d}:{self.alarm_time.minute:02d}"
            playlist_name = self.selected_playlist.get('name', 'Unknown')
            
            self.alarm.set_alarm(
                time_str=time_str,
                playlist_name=playlist_name,
                playlist_uri=playlist_uri,
                spotify_api=self.spotify_api,
                volume=self.volume,
            )
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Alarm set for {self.time_display.value}"),
                bgcolor="#1DB954",
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            logger.error(f"Failed to set alarm: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Failed: {e}"),
                bgcolor="#F44336",
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _manage_alarms(self, e):
        """Open alarm manager"""
        # TODO: Implement alarm manager dialog
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Alarm manager coming soon"),
                bgcolor="#2196F3",
            )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _refresh_data(self, e):
        """Refresh playlists and devices"""
        self._load_playlists()
        self._refresh_devices()
    
    def _refresh_devices(self):
        """Refresh device list"""
        try:
            devices = self.spotify_api.get_devices()
            self.devices = devices
            
            options = [ft.dropdown.Option("Auto (Use Active Device)", "auto")]
            for device in devices:
                name = device.get('name', 'Unknown')
                device_id = device.get('id')
                options.append(ft.dropdown.Option(name, device_id))
            
            self.device_dropdown.options = options
            self.page.update()
        except Exception as e:
            logger.error(f"Failed to refresh devices: {e}")
    
    def _update_auth_status(self, authenticated: bool):
        """Update authentication status"""
        if authenticated:
            self.auth_status.label = ft.Text("Connected")
            self.auth_status.bgcolor = "#1B5E20"
        else:
            self.auth_status.label = ft.Text("Not connected")
            self.auth_status.bgcolor = "#B71C1C"
        self.page.update()
    
    def _open_settings(self, e):
        """Open settings dialog"""
        # TODO: Implement settings dialog
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Settings coming soon"),
                bgcolor="#2196F3",
            )
        self.page.snack_bar.open = True
        self.page.update()


def main(page: ft.Page):
    """Main entry point for Flet app"""
    app = AlarmifyApp(page)


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)

