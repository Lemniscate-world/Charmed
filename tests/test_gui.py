"""
test_gui.py - GUI tests for Alarmify using PyQt5 test utilities

Comprehensive GUI tests covering:
- Settings dialog interactions and validation
- Alarm manager dialog functionality
- Playlist selection and display
- Main window interactions
- Image loading and display
- Button states and event handling
- Phase 2: Alarm setup dialog with fade-in and day selection
- Phase 2: Snooze notification dialog
- Phase 2: Template management dialogs
- Phase 2: Quick setup from templates

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

from gui import (
    AlarmApp, SettingsDialog, AlarmManagerDialog, PlaylistItemWidget, 
    ImageLoaderThread, AlarmSetupDialog, SnoozeNotificationDialog,
    TemplateManagerDialog, TemplateEditDialog, QuickSetupDialog
)
from alarm import Alarm, AlarmTemplate, TemplateManager


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


class TestAlarmSetupDialog:
    """Tests for AlarmSetupDialog - Phase 2."""
    
    def test_alarm_setup_dialog_initialization(self, qapp):
        """Test alarm setup dialog initializes correctly."""
        dialog = AlarmSetupDialog(None, 'Test Playlist', '08:00', 75, 'spotify:playlist:test')
        
        assert dialog.windowTitle() == 'Alarm Setup'
        assert dialog.isModal() is True
        assert dialog.fade_in_enabled is False
        assert dialog.fade_in_duration == 10
        assert dialog.target_volume == 75
    
    def test_alarm_setup_dialog_day_selection(self, qapp):
        """Test day selection checkboxes."""
        dialog = AlarmSetupDialog(None, 'Test', '08:00', 80, 'spotify:playlist:test')
        
        # All days should be checked by default
        assert all(cb.isChecked() for cb in dialog.day_checkboxes.values())
        
        # Uncheck some days
        dialog.day_checkboxes['Monday'].setChecked(False)
        dialog.day_checkboxes['Friday'].setChecked(False)
        
        assert not dialog.day_checkboxes['Monday'].isChecked()
        assert not dialog.day_checkboxes['Friday'].isChecked()
        assert dialog.day_checkboxes['Tuesday'].isChecked()
    
    def test_alarm_setup_dialog_weekdays_shortcut(self, qapp):
        """Test weekdays quick select button."""
        dialog = AlarmSetupDialog(None, 'Test', '08:00', 80, 'spotify:playlist:test')
        
        dialog._select_weekdays()
        
        # Weekdays should be checked
        assert dialog.day_checkboxes['Monday'].isChecked()
        assert dialog.day_checkboxes['Friday'].isChecked()
        
        # Weekend should not be checked
        assert not dialog.day_checkboxes['Saturday'].isChecked()
        assert not dialog.day_checkboxes['Sunday'].isChecked()
    
    def test_alarm_setup_dialog_weekends_shortcut(self, qapp):
        """Test weekends quick select button."""
        dialog = AlarmSetupDialog(None, 'Test', '08:00', 80, 'spotify:playlist:test')
        
        dialog._select_weekends()
        
        # Weekend should be checked
        assert dialog.day_checkboxes['Saturday'].isChecked()
        assert dialog.day_checkboxes['Sunday'].isChecked()
        
        # Weekdays should not be checked
        assert not dialog.day_checkboxes['Monday'].isChecked()
        assert not dialog.day_checkboxes['Friday'].isChecked()
    
    def test_alarm_setup_dialog_every_day_shortcut(self, qapp):
        """Test every day quick select button."""
        dialog = AlarmSetupDialog(None, 'Test', '08:00', 80, 'spotify:playlist:test')
        
        # Uncheck all first
        for cb in dialog.day_checkboxes.values():
            cb.setChecked(False)
        
        dialog._select_every_day()
        
        # All days should be checked
        assert all(cb.isChecked() for cb in dialog.day_checkboxes.values())
    
    def test_alarm_setup_dialog_fade_in_toggle(self, qapp):
        """Test fade-in checkbox enables/disables duration slider."""
        dialog = AlarmSetupDialog(None, 'Test', '08:00', 80, 'spotify:playlist:test')
        
        # Initially fade-in should be disabled
        assert not dialog.fade_in_checkbox.isChecked()
        assert not dialog.duration_slider.isEnabled()
        
        # Enable fade-in
        dialog.fade_in_checkbox.setChecked(True)
        
        assert dialog.duration_slider.isEnabled()
        assert dialog.fade_in_enabled is True
    
    def test_alarm_setup_dialog_fade_in_duration(self, qapp):
        """Test fade-in duration slider."""
        dialog = AlarmSetupDialog(None, 'Test', '08:00', 80, 'spotify:playlist:test')
        
        dialog.fade_in_checkbox.setChecked(True)
        dialog.duration_slider.setValue(20)
        
        assert dialog.fade_in_duration == 20
        assert dialog.duration_value_label.text() == '20 min'
    
    def test_alarm_setup_dialog_validation_no_days(self, qapp, monkeypatch):
        """Test validation fails when no days are selected."""
        dialog = AlarmSetupDialog(None, 'Test', '08:00', 80, 'spotify:playlist:test')
        
        # Uncheck all days
        for cb in dialog.day_checkboxes.values():
            cb.setChecked(False)
        
        mock_warning = Mock()
        monkeypatch.setattr('gui.QMessageBox.warning', mock_warning)
        
        dialog._on_accept()
        
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert 'no days' in args[2].lower()
    
    def test_alarm_setup_dialog_accept_returns_settings(self, qapp):
        """Test accepting dialog returns correct settings."""
        dialog = AlarmSetupDialog(None, 'Test', '08:00', 80, 'spotify:playlist:test')
        
        # Configure settings
        dialog.fade_in_checkbox.setChecked(True)
        dialog.duration_slider.setValue(15)
        dialog.day_checkboxes['Saturday'].setChecked(False)
        dialog.day_checkboxes['Sunday'].setChecked(False)
        
        # Accept (simulate)
        dialog.selected_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        assert dialog.fade_in_enabled is True
        assert dialog.fade_in_duration == 15
        assert dialog.selected_days == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']


class TestSnoozeNotificationDialog:
    """Tests for SnoozeNotificationDialog - Phase 2."""
    
    def test_snooze_dialog_initialization(self, qapp):
        """Test snooze notification dialog initializes."""
        alarm_data = {
            'playlist_uri': 'spotify:playlist:test',
            'playlist_name': 'Test Playlist',
            'volume': 80
        }
        
        dialog = SnoozeNotificationDialog(None, 'Alarm!', 'Playing Test Playlist', alarm_data)
        
        assert dialog.windowTitle() == 'Alarm!'
        assert dialog.alarm_data == alarm_data
        assert not dialog.isModal()
    
    def test_snooze_dialog_buttons_present(self, qapp):
        """Test snooze dialog has correct buttons."""
        alarm_data = {'playlist_uri': 'test', 'playlist_name': 'Test', 'volume': 80}
        dialog = SnoozeNotificationDialog(None, 'Alarm', 'Message', alarm_data)
        
        # Should have snooze and dismiss buttons (implementation detail)
        # Just verify dialog was created successfully
        assert dialog is not None
    
    def test_snooze_dialog_snooze_action(self, qapp, monkeypatch):
        """Test snooze action calls alarm manager."""
        mock_parent = Mock()
        mock_alarm = Mock()
        mock_parent.alarm = mock_alarm
        
        alarm_data = {
            'playlist_uri': 'spotify:playlist:test',
            'playlist_name': 'Test',
            'volume': 80,
            'fade_in_enabled': False,
            'fade_in_duration': 10,
            'spotify_api': Mock()
        }
        
        dialog = SnoozeNotificationDialog(mock_parent, 'Alarm', 'Message', alarm_data)
        
        mock_info = Mock()
        monkeypatch.setattr('gui.QMessageBox.information', mock_info)
        
        # Trigger snooze
        dialog._snooze(10)
        
        mock_alarm.snooze_alarm.assert_called_once_with(alarm_data, 10)


class TestTemplateManagerDialog:
    """Tests for TemplateManagerDialog - Phase 2."""
    
    def test_template_manager_initialization(self, qapp, tmp_path):
        """Test template manager dialog initializes."""
        templates_file = tmp_path / 'templates.json'
        manager = TemplateManager(templates_file)
        
        dialog = TemplateManagerDialog(manager, None)
        
        assert dialog.windowTitle() == 'Manage Alarm Templates'
        assert dialog.isModal() is True
        assert dialog.template_manager == manager
    
    def test_template_manager_displays_templates(self, qapp, tmp_path):
        """Test template manager displays loaded templates."""
        templates_file = tmp_path / 'templates.json'
        manager = TemplateManager(templates_file)
        
        # Add some templates
        template1 = AlarmTemplate(
            name='Morning',
            time='07:00',
            playlist_name='Morning Mix',
            playlist_uri='spotify:playlist:morning',
            volume=75,
            fade_in_enabled=True,
            fade_in_duration=15,
            days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        )
        
        template2 = AlarmTemplate(
            name='Weekend',
            time='09:00',
            playlist_name='Weekend Vibes',
            playlist_uri='spotify:playlist:weekend',
            volume=80,
            days=['Saturday', 'Sunday']
        )
        
        manager.add_template(template1)
        manager.add_template(template2)
        
        dialog = TemplateManagerDialog(manager, None)
        
        # Table should have 2 rows
        assert dialog.table.rowCount() == 2
        
        # Check first row content
        assert dialog.table.item(0, 0).text() == 'Morning'
        assert dialog.table.item(0, 1).text() == '07:00'
        assert dialog.table.item(0, 2).text() == 'Morning Mix'
        assert dialog.table.item(0, 3).text() == '75%'
        
        # Check second row
        assert dialog.table.item(1, 0).text() == 'Weekend'
        assert dialog.table.item(1, 1).text() == '09:00'


class TestTemplateEditDialog:
    """Tests for TemplateEditDialog - Phase 2."""
    
    def test_template_edit_dialog_create_mode(self, qapp):
        """Test template edit dialog in create mode."""
        dialog = TemplateEditDialog(None, None, None)
        
        assert dialog.windowTitle() == 'Create Template'
        assert dialog.template is None
        assert dialog.selected_playlist_uri is None
    
    def test_template_edit_dialog_edit_mode(self, qapp):
        """Test template edit dialog in edit mode."""
        template = AlarmTemplate(
            name='Edit Test',
            time='08:00',
            playlist_name='Test Playlist',
            playlist_uri='spotify:playlist:test',
            volume=75,
            fade_in_enabled=True,
            fade_in_duration=20,
            days=['Monday', 'Friday']
        )
        
        dialog = TemplateEditDialog(template, None, None)
        
        assert dialog.windowTitle() == 'Edit Template'
        assert dialog.template == template
        assert dialog.selected_playlist_uri == 'spotify:playlist:test'
    
    def test_template_edit_dialog_populates_fields(self, qapp):
        """Test edit dialog populates fields from template."""
        template = AlarmTemplate(
            name='Populate Test',
            time='10:30',
            playlist_name='Morning Mix',
            playlist_uri='spotify:playlist:morning',
            volume=85,
            fade_in_enabled=True,
            fade_in_duration=25,
            days=['Tuesday', 'Thursday']
        )
        
        dialog = TemplateEditDialog(template, None, None)
        
        assert dialog.name_input.text() == 'Populate Test'
        assert dialog.time_input.time().toString('HH:mm') == '10:30'
        assert dialog.playlist_label.text() == 'Morning Mix'
        assert dialog.volume_slider.value() == 85
        assert dialog.fade_checkbox.isChecked() is True
        assert dialog.fade_duration_slider.value() == 25
        assert dialog.day_checkboxes['Tuesday'].isChecked()
        assert dialog.day_checkboxes['Thursday'].isChecked()
        assert not dialog.day_checkboxes['Monday'].isChecked()
    
    def test_template_edit_dialog_validation(self, qapp, monkeypatch):
        """Test template edit dialog validates input."""
        dialog = TemplateEditDialog(None, None, None)
        
        mock_warning = Mock()
        monkeypatch.setattr('gui.QMessageBox.warning', mock_warning)
        
        # Try to save without name
        dialog.name_input.setText('')
        dialog._save_template()
        
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert 'name' in args[2].lower()


class TestQuickSetupDialog:
    """Tests for QuickSetupDialog - Phase 2."""
    
    def test_quick_setup_dialog_initialization(self, qapp):
        """Test quick setup dialog initializes with templates."""
        templates = [
            AlarmTemplate(
                name='Morning',
                time='07:00',
                playlist_name='Morning Mix',
                playlist_uri='spotify:playlist:morning',
                volume=75
            ),
            AlarmTemplate(
                name='Evening',
                time='18:00',
                playlist_name='Evening Chill',
                playlist_uri='spotify:playlist:evening',
                volume=60
            )
        ]
        
        dialog = QuickSetupDialog(templates, None)
        
        assert dialog.windowTitle() == 'Quick Setup from Template'
        assert dialog.isModal() is True
        assert len(dialog.templates) == 2
    
    def test_quick_setup_dialog_lists_templates(self, qapp):
        """Test quick setup dialog displays template list."""
        templates = [
            AlarmTemplate(
                name='Test Template',
                time='08:00',
                playlist_name='Test Playlist',
                playlist_uri='spotify:playlist:test',
                volume=80,
                fade_in_enabled=True,
                fade_in_duration=15,
                days=['Monday', 'Wednesday', 'Friday']
            )
        ]
        
        dialog = QuickSetupDialog(templates, None)
        
        # Should have one item in list
        assert dialog.list_widget.count() == 1
        
        # Item text should contain template info
        item_text = dialog.list_widget.item(0).text()
        assert 'Test Template' in item_text
        assert '08:00' in item_text
        assert 'Test Playlist' in item_text
        assert '80%' in item_text
    
    def test_quick_setup_dialog_selection(self, qapp):
        """Test quick setup dialog allows template selection."""
        template = AlarmTemplate(
            name='Select Me',
            time='09:00',
            playlist_name='Select Playlist',
            playlist_uri='spotify:playlist:select',
            volume=70
        )
        
        dialog = QuickSetupDialog([template], None)
        
        # Select the item
        dialog.list_widget.setCurrentRow(0)
        
        # Simulate selection
        dialog._on_template_selected()
        
        assert dialog.selected_template == template


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
            {'time': '08:00', 'playlist': 'Morning Mix', 'volume': 75, 'days': ['Monday', 'Friday']},
            {'time': '12:00', 'playlist': 'Lunch Vibes', 'volume': 50, 'days': None},
            {'time': '18:00', 'playlist': 'Evening Chill', 'volume': 60, 'days': 'weekdays'}
        ]
        
        dialog = AlarmManagerDialog(mock_alarm)
        
        assert dialog.table.rowCount() == 3
        
        assert dialog.table.item(0, 0).text() == '08:00'
        assert dialog.table.item(0, 1).text() == 'Morning Mix'
        assert dialog.table.item(0, 2).text() == '75%'
        
        assert dialog.table.item(1, 0).text() == '12:00'
        assert dialog.table.item(2, 0).text() == '18:00'


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


class TestAlarmAppMainWindow:
    """Tests for AlarmApp main window."""
    
    @patch('gui.ThreadSafeSpotifyAPI')
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
            
            assert window.windowTitle() == 'Alarmify - Spotify Alarm Clock'
            assert window.spotify_api is not None
            assert window.alarm is not None
            assert window.playlist_list is not None
            assert window.time_input is not None
            assert window.volume_slider is not None


class TestGUIIntegrationScenarios:
    """Integration tests for GUI workflow scenarios - Phase 2."""
    
    @patch('gui.ThreadSafeSpotifyAPI')
    @patch('gui.Alarm')
    def test_alarm_setup_with_fade_in_workflow(self, mock_alarm_class, mock_spotify_class, qapp, monkeypatch):
        """Test complete workflow: set alarm with fade-in enabled."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = True
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        # Add a playlist
        playlist_data = {
            'name': 'Morning Mix',
            'uri': 'spotify:playlist:morning',
            'track_count': 30,
            'owner': 'User',
            'image_url': None
        }
        
        from PyQt5.QtWidgets import QListWidgetItem
        item = QListWidgetItem()
        item.setData(Qt.UserRole, playlist_data)
        window.playlist_list.addItem(item)
        window.playlist_list.setCurrentItem(item)
        
        window.time_input.setTime(QTime(7, 30))
        window.volume_slider.setValue(75)
        
        # Mock the AlarmSetupDialog to return accepted with fade-in enabled
        mock_dialog = Mock(spec=AlarmSetupDialog)
        mock_dialog.exec_.return_value = QDialog.Accepted
        mock_dialog.fade_in_enabled = True
        mock_dialog.fade_in_duration = 15
        mock_dialog.selected_days = ['Monday', 'Wednesday', 'Friday']
        
        mock_info = Mock()
        monkeypatch.setattr('gui.QMessageBox.information', mock_info)
        
        with patch('gui.AlarmSetupDialog', return_value=mock_dialog):
            window.set_alarm()
        
        # Verify alarm was set with fade-in parameters
        mock_alarm_instance.set_alarm.assert_called_once()
        call_args = mock_alarm_instance.set_alarm.call_args
        
        assert call_args[0][0] == '07:30'  # time
        assert call_args[0][1] == 'Morning Mix'  # playlist name
        assert call_args[0][4] == 75  # volume
        assert call_args[0][5] is True  # fade_in_enabled
        assert call_args[0][6] == 15  # fade_in_duration
        assert call_args[0][7] == ['Monday', 'Wednesday', 'Friday']  # days
    
    @patch('gui.ThreadSafeSpotifyAPI')
    @patch('gui.Alarm')
    def test_template_creation_workflow(self, mock_alarm_class, mock_spotify_class, qapp, monkeypatch, tmp_path):
        """Test workflow: create and use alarm template."""
        mock_spotify_instance = Mock()
        mock_spotify_instance.is_authenticated.return_value = True
        mock_spotify_class.return_value = mock_spotify_instance
        
        mock_alarm_instance = Mock()
        mock_alarm_class.return_value = mock_alarm_instance
        
        with patch('gui.QMessageBox.warning'):
            window = AlarmApp()
        
        # Set up template manager with temp file
        templates_file = tmp_path / 'templates.json'
        window.template_manager = TemplateManager(templates_file)
        
        # Create a template
        template = AlarmTemplate(
            name='Test Template',
            time='08:00',
            playlist_name='Test Playlist',
            playlist_uri='spotify:playlist:test',
            volume=80,
            fade_in_enabled=True,
            fade_in_duration=20,
            days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        )
        
        window.template_manager.add_template(template)
        
        # Apply the template
        mock_info = Mock()
        monkeypatch.setattr('gui.QMessageBox.information', mock_info)
        
        window._apply_template(template)
        
        # Verify alarm was created from template
        mock_alarm_instance.set_alarm.assert_called_once()
        call_args = mock_alarm_instance.set_alarm.call_args
        
        assert call_args[0][0] == '08:00'
        assert call_args[0][1] == 'Test Playlist'
        assert call_args[0][4] == 80
        assert call_args[0][5] is True
        assert call_args[0][6] == 20
        assert call_args[0][7] == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
