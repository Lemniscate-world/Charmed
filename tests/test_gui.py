"""
test_gui.py - GUI tests for Alarmify using PyQt5 test utilities

Comprehensive GUI tests covering:
- Settings dialog interactions and validation
- Alarm manager dialog functionality
- Playlist selection and display
- Main window interactions
- Image loading and display
- Button states and event handling

Run with: python -m pytest tests/test_gui.py -v
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QPixmap

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui import AlarmApp, SettingsDialog, AlarmManagerDialog, PlaylistItemWidget, ImageLoaderThread
from alarm import Alarm


@pytest.fixture(scope='session')
def qapp():
    """Create QApplication instance for all GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    temp_dir = tempfile.mkdtemp()
    env_path = Path(temp_dir) / '.env'
    yield env_path
    if env_path.exists():
        env_path.unlink()
    Path(temp_dir).rmdir()


class TestSettingsDialog:
    """Tests for SettingsDialog widget."""
    
    def test_settings_dialog_initialization(self, qapp):
        """Test that settings dialog initializes correctly."""
        with patch('gui.load_dotenv'):
            with patch.dict(os.environ, {}, clear=True):
                dialog = SettingsDialog()
                
                assert dialog.windowTitle() == 'Spotify Settings'
                assert dialog.isModal() is True
                
                assert dialog.client_id is not None
                assert dialog.client_secret is not None
                assert dialog.redirect_uri is not None
    
    def test_settings_dialog_loads_existing_credentials(self, qapp):
        """Test that dialog loads existing credentials from environment."""
        with patch('gui.load_dotenv'):
            with patch.dict(os.environ, {
                'SPOTIPY_CLIENT_ID': 'existing_id',
                'SPOTIPY_CLIENT_SECRET': 'existing_secret',
                'SPOTIPY_REDIRECT_URI': 'http://localhost:9999/callback'
            }):
                dialog = SettingsDialog()
                
                assert dialog.client_id.text() == 'existing_id'
                assert dialog.client_secret.text() == 'existing_secret'
                assert dialog.redirect_uri.text() == 'http://localhost:9999/callback'
    
    def test_settings_dialog_validation_empty_fields(self, qapp, monkeypatch):
        """Test validation fails with empty required fields."""
        with patch('gui.load_dotenv'):
            with patch.dict(os.environ, {}, clear=True):
                dialog = SettingsDialog()
                
                dialog.client_id.setText('')
                dialog.client_secret.setText('')
                dialog.redirect_uri.setText('http://localhost:8888/callback')
                
                mock_warning = Mock()
                monkeypatch.setattr('gui.QMessageBox.warning', mock_warning)
                
                dialog.save()
                
                mock_warning.assert_called_once()
                args = mock_warning.call_args[0]
                assert 'required' in args[2].lower()
    
    def test_settings_dialog_validation_invalid_redirect_uri(self, qapp, monkeypatch):
        """Test validation fails with invalid redirect URI."""
        with patch('gui.load_dotenv'):
            with patch.dict(os.environ, {}, clear=True):
                dialog = SettingsDialog()
                
                dialog.client_id.setText('test_id')
                dialog.client_secret.setText('test_secret')
                dialog.redirect_uri.setText('invalid_uri')
                
                mock_warning = Mock()
                monkeypatch.setattr('gui.QMessageBox.warning', mock_warning)
                
                dialog.save()
                
                mock_warning.assert_called_once()
                args = mock_warning.call_args[0]
                assert 'http' in args[2].lower()
    
    def test_settings_dialog_saves_valid_credentials(self, qapp, monkeypatch):
        """Test that valid credentials are saved to .env file."""
        temp_dir = tempfile.mkdtemp()
        env_path = Path(temp_dir) / '.env'
        
        try:
            with patch('gui.load_dotenv'):
                with patch('gui.Path') as mock_path_class:
                    mock_path_instance = Mock()
                    mock_path_instance.resolve.return_value.parent = Path(temp_dir)
                    mock_path_class.return_value = mock_path_instance
                    
                    with patch.dict(os.environ, {}, clear=True):
                        dialog = SettingsDialog()
                        
                        dialog.client_id.setText('new_test_id')
                        dialog.client_secret.setText('new_test_secret')
                        dialog.redirect_uri.setText('http://localhost:8888/callback')
                        
                        dialog.save()
                        
                        assert env_path.exists()
                        
                        content = env_path.read_text()
                        assert 'SPOTIPY_CLIENT_ID=new_test_id' in content
                        assert 'SPOTIPY_CLIENT_SECRET=new_test_secret' in content
                        assert 'SPOTIPY_REDIRECT_URI=http://localhost:8888/callback' in content
        finally:
            if env_path.exists():
                env_path.unlink()
            Path(temp_dir).rmdir()
    
    def test_settings_dialog_cancel_closes_without_saving(self, qapp, monkeypatch):
        """Test that cancel button closes dialog without saving."""
        with patch('gui.load_dotenv'):
            with patch.dict(os.environ, {}, clear=True):
                dialog = SettingsDialog()
                
                dialog.client_id.setText('should_not_save')
                
                result = dialog.result()
                dialog.reject()
                
                assert dialog.result() == QDialog.Rejected


class TestAlarmManagerDialog:
    """Tests for AlarmManagerDialog widget."""
    
    def test_alarm_manager_initialization(self, qapp):
        """Test that alarm manager dialog initializes correctly."""
        mock_alarm = Mock(spec=Alarm)
        mock_alarm.get_alarms.return_value = []
        
        dialog = AlarmManagerDialog(mock_alarm)
        
        assert dialog.windowTitle() == 'Manage Alarms'
        assert dialog.isModal() is True
        assert dialog.table.columnCount() == 4
    
    def test_alarm_manager_displays_alarms(self, qapp):
        """Test that alarms are displayed in the table."""
        mock_alarm = Mock(spec=Alarm)
        mock_alarm.get_alarms.return_value = [
            {'time': '08:00', 'playlist': 'Morning Mix', 'volume': 75},
            {'time': '12:00', 'playlist': 'Lunch Vibes', 'volume': 50},
            {'time': '18:00', 'playlist': 'Evening Chill', 'volume': 60}
        ]
        
        dialog = AlarmManagerDialog(mock_alarm)
        
        assert dialog.table.rowCount() == 3
        
        assert dialog.table.item(0, 0).text() == '08:00'
        assert dialog.table.item(0, 1).text() == 'Morning Mix'
        assert dialog.table.item(0, 2).text() == '75%'
        
        assert dialog.table.item(1, 0).text() == '12:00'
        assert dialog.table.item(2, 0).text() == '18:00'
    
    def test_alarm_manager_delete_alarm(self, qapp):
        """Test deleting an alarm from the manager."""
        initial_alarms = [
            {'time': '08:00', 'playlist': 'Morning Mix', 'volume': 75},
            {'time': '12:00', 'playlist': 'Lunch Vibes', 'volume': 50}
        ]
        
        remaining_alarms = [
            {'time': '12:00', 'playlist': 'Lunch Vibes', 'volume': 50}
        ]
        
        mock_alarm = Mock(spec=Alarm)
        mock_alarm.get_alarms.side_effect = [initial_alarms, remaining_alarms]
        
        dialog = AlarmManagerDialog(mock_alarm)
        
        assert dialog.table.rowCount() == 2
        
        dialog._delete_alarm(0)
        
        mock_alarm.remove_alarm.assert_called_once_with('08:00')
        
        assert dialog.table.rowCount() == 1
    
    def test_alarm_manager_empty_state(self, qapp):
        """Test alarm manager with no alarms."""
        mock_alarm = Mock(spec=Alarm)
        mock_alarm.get_alarms.return_value = []
        
        dialog = AlarmManagerDialog(mock_alarm)
        
        assert dialog.table.rowCount() == 0
    
    def test_alarm_manager_delete_out_of_range(self, qapp):
        """Test that deleting out-of-range row doesn't crash."""
        mock_alarm = Mock(spec=Alarm)
        mock_alarm.get_alarms.return_value = [
            {'time': '08:00', 'playlist': 'Test', 'volume': 80}
        ]
        
        dialog = AlarmManagerDialog(mock_alarm)
        
        dialog._delete_alarm(999)
        
        mock_alarm.remove_alarm.assert_not_called()


class TestPlaylistItemWidget:
    """Tests for PlaylistItemWidget custom widget."""
    
    def test_playlist_widget_initialization(self, qapp):
        """Test that playlist widget initializes with correct data."""
        playlist_data = {
            'name': 'Test Playlist',
            'track_count': 42,
            'owner': 'Test User',
            'image_url': 'https://example.com/image.jpg',
            'uri': 'spotify:playlist:test123'
        }
        
        widget = PlaylistItemWidget(playlist_data)
        
        assert widget.playlist_data == playlist_data
        assert widget.name_label.text() == 'Test Playlist'
        assert '42 tracks' in widget.info_label.text()
        assert 'Test User' in widget.info_label.text()
    
    def test_playlist_widget_set_image(self, qapp):
        """Test setting image on playlist widget."""
        playlist_data = {
            'name': 'Test Playlist',
            'track_count': 10,
            'owner': 'User',
            'image_url': None,
            'uri': 'spotify:playlist:test'
        }
        
        widget = PlaylistItemWidget(playlist_data)
        
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.red)
        
        widget.set_image(pixmap)
        
        assert not widget.image_label.pixmap().isNull()
    
    def test_playlist_widget_null_image(self, qapp):
        """Test that null pixmap doesn't update image."""
        playlist_data = {
            'name': 'Test',
            'track_count': 5,
            'owner': 'User',
            'image_url': None,
            'uri': 'spotify:playlist:test'
        }
        
        widget = PlaylistItemWidget(playlist_data)
        
        null_pixmap = QPixmap()
        
        widget.set_image(null_pixmap)


class TestImageLoaderThread:
    """Tests for ImageLoaderThread background loading."""
    
    def test_image_loader_initialization(self, qapp):
        """Test image loader thread initialization."""
        loader = ImageLoaderThread('playlist123', 'https://example.com/image.jpg')
        
        assert loader.playlist_id == 'playlist123'
        assert loader.image_url == 'https://example.com/image.jpg'
        assert loader._is_running is True
    
    @patch('gui.requests.get')
    def test_image_loader_successful_load(self, mock_get, qapp):
        """Test successful image loading."""
        mock_response = Mock()
        mock_response.content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        loader = ImageLoaderThread('playlist123', 'https://example.com/image.jpg')
        
        signal_received = []
        
        def on_image_loaded(playlist_id, pixmap):
            signal_received.append((playlist_id, pixmap))
        
        loader.image_loaded.connect(on_image_loaded)
        
        loader.run()
        
        assert len(signal_received) == 1
        assert signal_received[0][0] == 'playlist123'
    
    @patch('gui.requests.get')
    def test_image_loader_handles_error(self, mock_get, qapp):
        """Test image loader handles network errors gracefully."""
        mock_get.side_effect = Exception("Network error")
        
        loader = ImageLoaderThread('playlist123', 'https://example.com/image.jpg')
        
        signal_received = []
        
        def on_image_loaded(playlist_id, pixmap):
            signal_received.append((playlist_id, pixmap))
        
        loader.image_loaded.connect(on_image_loaded)
        
        loader.run()
        
        assert len(signal_received) == 1
        assert signal_received[0][0] == 'playlist123'
        assert signal_received[0][1].isNull()
    
    def test_image_loader_stop(self, qapp):
        """Test stopping image loader thread."""
        loader = ImageLoaderThread('playlist123', 'https://example.com/image.jpg')
        
        assert loader._is_running is True
        
        loader.stop()
        
        assert loader._is_running is False


class TestAlarmAppMainWindow:
    """Tests for AlarmApp main window."""
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_initialization(self, mock_alarm_class, mock_spotify_class, qapp):
        """Test main window initializes correctly."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = False
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
            
            assert window.windowTitle() == 'Alarmify'
            assert window.spotify_api is not None
            assert window.alarm is not None
            assert window.playlist_list is not None
            assert window.time_input is not None
            assert window.volume_slider is not None
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_no_credentials(self, mock_alarm_class, mock_spotify_class, qapp, monkeypatch):
        """Test main window handles missing credentials."""
        mock_spotify_class.side_effect = RuntimeError("Credentials not set")
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        mock_warning = Mock()
        monkeypatch.setattr('gui.QMessageBox.warning', mock_warning)
        
        window = AlarmApp()
        
        mock_warning.assert_called_once()
        assert window.spotify_api is None
        assert window.login_button.isEnabled() is False
        assert window.set_alarm_button.isEnabled() is False
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_volume_slider(self, mock_alarm_class, mock_spotify_class, qapp):
        """Test volume slider updates label."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = False
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
            
            window.volume_slider.setValue(65)
            
            assert window.volume_value_label.text() == '65%'
            
            window.volume_slider.setValue(100)
            assert window.volume_value_label.text() == '100%'
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_set_alarm_no_playlist_selected(self, mock_alarm_class, mock_spotify_class, qapp, monkeypatch):
        """Test set alarm fails when no playlist is selected."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = True
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        mock_warning = Mock()
        monkeypatch.setattr('gui.QMessageBox.warning', mock_warning)
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        window.set_alarm()
        
        mock_warning.assert_called()
        args = mock_warning.call_args[0]
        assert 'playlist' in args[2].lower()
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_set_alarm_success(self, mock_alarm_class, mock_spotify_class, qapp, monkeypatch):
        """Test successfully setting an alarm."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = True
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        mock_info = Mock()
        monkeypatch.setattr('gui.QMessageBox.information', mock_info)
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        playlist_data = {
            'name': 'Test Playlist',
            'uri': 'spotify:playlist:test123',
            'track_count': 20,
            'owner': 'User',
            'image_url': None
        }
        
        from PyQt5.QtWidgets import QListWidgetItem
        item = QListWidgetItem()
        item.setData(Qt.UserRole, playlist_data)
        window.playlist_list.addItem(item)
        window.playlist_list.setCurrentItem(item)
        
        window.time_input.setTime(QTime(8, 30))
        window.volume_slider.setValue(75)
        
        window.set_alarm()
        
        mock_alarm_instance.set_alarm.assert_called_once_with(
            '08:30',
            'Test Playlist',
            'spotify:playlist:test123',
            mock_spotify_instance,
            75
        )
        
        mock_info.assert_called_once()
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_login_to_spotify(self, mock_alarm_class, mock_spotify_class, qapp, monkeypatch):
        """Test login to Spotify button."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = False
        mock_spotify_instance.authenticate.return_value = {'access_token': 'test'}
        mock_spotify_instance.get_playlists_detailed.return_value = []
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        window.login_to_spotify()
        
        mock_spotify_instance.authenticate.assert_called_once()
        mock_spotify_instance.get_playlists_detailed.assert_called_once()
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_load_playlists(self, mock_alarm_class, mock_spotify_class, qapp):
        """Test loading playlists into list widget."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = True
        mock_spotify_instance.get_playlists_detailed.return_value = [
            {
                'name': 'Playlist 1',
                'id': 'id1',
                'uri': 'spotify:playlist:id1',
                'track_count': 30,
                'owner': 'User A',
                'image_url': 'https://example.com/img1.jpg'
            },
            {
                'name': 'Playlist 2',
                'id': 'id2',
                'uri': 'spotify:playlist:id2',
                'track_count': 25,
                'owner': 'User B',
                'image_url': None
            }
        ]
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        window._load_playlists()
        
        assert window.playlist_list.count() == 2
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_open_settings(self, mock_alarm_class, mock_spotify_class, qapp, monkeypatch):
        """Test opening settings dialog."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = False
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        mock_dialog = Mock(spec=SettingsDialog)
        mock_dialog.exec_.return_value = QDialog.Rejected
        
        with patch('gui.SettingsDialog', return_value=mock_dialog):
            window.open_settings()
            
            mock_dialog.exec_.assert_called_once()
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_open_alarm_manager(self, mock_alarm_class, mock_spotify_class, qapp):
        """Test opening alarm manager dialog."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = False
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_instance.get_alarms.return_value = []
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        mock_dialog = Mock(spec=AlarmManagerDialog)
        mock_dialog.exec_.return_value = QDialog.Accepted
        
        with patch('gui.AlarmManagerDialog', return_value=mock_dialog):
            window.open_alarm_manager()
            
            mock_dialog.exec_.assert_called_once()
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_cleanup_on_close(self, mock_alarm_class, mock_spotify_class, qapp):
        """Test resource cleanup when window closes."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = False
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        mock_loader1 = Mock()
        mock_loader1.isRunning.return_value = True
        mock_loader2 = Mock()
        mock_loader2.isRunning.return_value = False
        
        window.image_loaders = [mock_loader1, mock_loader2]
        
        from PyQt5.QtGui import QCloseEvent
        event = QCloseEvent()
        
        window.closeEvent(event)
        
        mock_loader1.stop.assert_called_once()
        mock_loader1.wait.assert_called_once()
        mock_alarm_instance.shutdown.assert_called_once()
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_image_loading(self, mock_alarm_class, mock_spotify_class, qapp):
        """Test that images are loaded for playlists."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = True
        mock_spotify_instance.get_playlists_detailed.return_value = [
            {
                'name': 'Test Playlist',
                'id': 'id1',
                'uri': 'spotify:playlist:id1',
                'track_count': 20,
                'owner': 'User',
                'image_url': 'https://example.com/image.jpg'
            }
        ]
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        with patch('gui.ImageLoaderThread') as mock_loader_class:
            mock_loader_instance = Mock()
            mock_loader_class.return_value = mock_loader_instance
            
            window._load_playlists()
            
            mock_loader_class.assert_called_once_with('id1', 'https://example.com/image.jpg')
            mock_loader_instance.image_loaded.connect.assert_called_once()
            mock_loader_instance.start.assert_called_once()
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_on_image_loaded(self, mock_alarm_class, mock_spotify_class, qapp):
        """Test handling loaded images."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = False
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        mock_widget = Mock(spec=PlaylistItemWidget)
        window.playlist_widgets['playlist123'] = mock_widget
        
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.blue)
        
        window._on_image_loaded('playlist123', pixmap)
        
        mock_widget.set_image.assert_called_once()
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_main_window_update_auth_status(self, mock_alarm_class, mock_spotify_class, qapp):
        """Test authentication status display updates."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = True
        mock_spotify_instance.get_current_user.return_value = {
            'display_name': 'John Doe',
            'id': 'user123'
        }
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        window._update_auth_status()
        
        assert 'John Doe' in window.auth_status_label.text()


class TestGUIIntegrationScenarios:
    """Integration tests for GUI workflow scenarios."""
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_complete_alarm_setup_workflow(self, mock_alarm_class, mock_spotify_class, qapp, monkeypatch):
        """Test complete workflow: login -> browse -> select -> set alarm."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.side_effect = [False, True, True]
        mock_spotify_instance.authenticate.return_value = {'access_token': 'test'}
        mock_spotify_instance.get_current_user.return_value = {
            'display_name': 'Test User',
            'id': 'user123'
        }
        mock_spotify_instance.get_playlists_detailed.return_value = [
            {
                'name': 'Morning Mix',
                'id': 'morning1',
                'uri': 'spotify:playlist:morning1',
                'track_count': 30,
                'owner': 'Spotify',
                'image_url': 'https://example.com/morning.jpg'
            }
        ]
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        mock_info = Mock()
        monkeypatch.setattr('gui.QMessageBox.information', mock_info)
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        window.login_to_spotify()
        
        assert window.playlist_list.count() == 1
        
        item = window.playlist_list.item(0)
        window.playlist_list.setCurrentItem(item)
        
        window.time_input.setTime(QTime(7, 0))
        window.volume_slider.setValue(80)
        
        window.set_alarm()
        
        mock_alarm_instance.set_alarm.assert_called_once()
    
    @patch('gui.SpotifyAPI')
    @patch('gui.Alarm')
    def test_settings_update_workflow(self, mock_alarm_class, mock_spotify_class, qapp, monkeypatch):
        """Test workflow: open settings -> update credentials -> reload API."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = False
        mock_spotify_class.side_effect = [
            RuntimeError("Credentials not set"),
            mock_spotify_instance
        ]
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        mock_warning = Mock()
        mock_info = Mock()
        monkeypatch.setattr('gui.QMessageBox.warning', mock_warning)
        monkeypatch.setattr('gui.QMessageBox.information', mock_info)
        
        window = AlarmApp()
        
        assert window.spotify_api is None
        
        temp_dir = tempfile.mkdtemp()
        env_path = Path(temp_dir) / '.env'
        
        try:
            mock_dialog = Mock(spec=SettingsDialog)
            mock_dialog.exec_.return_value = QDialog.Accepted
            
            with patch('gui.SettingsDialog', return_value=mock_dialog):
                with patch('gui.load_dotenv'):
                    with patch('gui.Path') as mock_path_class:
                        mock_path_instance = Mock()
                        mock_path_instance.resolve.return_value.parent = Path(temp_dir)
                        mock_path_class.return_value = mock_path_instance
                        
                        window.open_settings()
            
            assert window.login_button.isEnabled() is True
            assert window.set_alarm_button.isEnabled() is True
        finally:
            if env_path.exists():
                env_path.unlink()
            Path(temp_dir).rmdir()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
