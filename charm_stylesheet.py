"""
charm_stylesheet.py - Charm-inspired stylesheets with glassmorphism

Provides modern, animated stylesheets following DESIGN_SYSTEM.md specifications.
"""

DARK_THEME_STYLESHEET = """
/* Global Styles */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

QMainWindow {
    background-color: #0a0a0a;
}

QWidget {
    background-color: #0a0a0a;
    color: #ffffff;
}

QWidget#centralWidget {
    background-color: #0a0a0a;
}

/* Typography */
QLabel {
    color: #b3b3b3;
    font-size: 14px;
}

QLabel[objectName="appLogo"] {
    color: #1DB954;
    font-size: 32px;
    font-weight: 700;
}

QLabel[objectName="sectionHeader"] {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
}

QLabel[objectName="authStatus"],
QLabel[objectName="deviceStatus"] {
    font-size: 12px;
    font-weight: 500;
    padding: 4px 8px;
    border-radius: 6px;
    background: rgba(42, 42, 42, 0.5);
}

/* Buttons with Spring Animation */
QPushButton {
    background-color: #1DB954;
    color: #000000;
    border: none;
    border-radius: 500px;
    padding: 12px 32px;
    font-weight: 700;
    font-size: 14px;
    min-height: 40px;
}

QPushButton:hover {
    background-color: #1ED760;
}

QPushButton:pressed {
    background-color: #1AA34A;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    color: #666666;
}

QPushButton[objectName="settingsButton"],
QPushButton[objectName="refreshButton"] {
    background: rgba(42, 42, 42, 0.7);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    padding: 0;
    font-size: 18px;
}

QPushButton[objectName="settingsButton"]:hover,
QPushButton[objectName="refreshButton"]:hover {
    background: rgba(52, 52, 52, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Input Fields with Glassmorphism */
QLineEdit {
    background: rgba(42, 42, 42, 0.7);
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    selection-background-color: #1DB954;
    selection-color: #000000;
}

QLineEdit:focus {
    border: 2px solid #1DB954;
    background: rgba(51, 51, 51, 0.8);
}

QLineEdit::placeholder {
    color: #666666;
}

QLineEdit[objectName="playlistSearch"] {
    background: rgba(42, 42, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 12px 16px;
    color: #ffffff;
    font-size: 14px;
}

QLineEdit[objectName="playlistSearch"]:focus {
    border: 2px solid #1DB954;
    background: rgba(51, 51, 51, 0.8);
}

/* Time Input with Monospace Font */
QTimeEdit {
    background: rgba(26, 26, 26, 0.7);
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 16px 20px;
    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
    font-size: 28px;
    font-weight: 700;
    selection-background-color: #1DB954;
    selection-color: #000000;
}

QTimeEdit:focus {
    border: 2px solid #1DB954;
    background: rgba(31, 31, 31, 0.8);
}

QTimeEdit::up-button, QTimeEdit::down-button {
    background: rgba(42, 42, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    width: 24px;
    height: 16px;
}

QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
    background: rgba(52, 52, 52, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

QTimeEdit::up-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 5px solid #ffffff;
    width: 0;
    height: 0;
}

QTimeEdit::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #ffffff;
    width: 0;
    height: 0;
}

/* Playlist List with Glass Effect */
QListWidget {
    background: rgba(26, 26, 26, 0.7);
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 8px;
    color: #ffffff;
    outline: none;
}

QListWidget::item {
    padding: 8px;
    border-radius: 8px;
    margin: 2px;
    color: #ffffff;
    background-color: transparent;
}

QListWidget::item:hover {
    background: rgba(42, 42, 42, 0.9);
}

QListWidget::item:selected {
    background: rgba(29, 185, 84, 0.3);
    border-left: 4px solid #1DB954;
}

/* ComboBox with Glass Effect */
QComboBox {
    background: rgba(42, 42, 42, 0.7);
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    selection-background-color: #1DB954;
}

QComboBox:hover {
    border: 2px solid rgba(255, 255, 255, 0.3);
    background: rgba(52, 52, 52, 0.8);
}

QComboBox:focus {
    border: 2px solid #1DB954;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #ffffff;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background: rgba(26, 26, 26, 0.95);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 4px;
    selection-background-color: #1DB954;
    selection-color: #000000;
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    border-radius: 6px;
    min-height: 32px;
}

QComboBox QAbstractItemView::item:hover {
    background: rgba(42, 42, 42, 0.9);
}

/* Slider with Modern Design */
QSlider::groove:horizontal {
    background: rgba(58, 58, 58, 0.8);
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #1DB954;
    width: 20px;
    height: 20px;
    margin: -7px 0;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #1DB954, stop:1 #1ED760);
    border-radius: 3px;
}

/* Status Bar */
QStatusBar {
    background: rgba(16, 16, 16, 0.9);
    color: #b3b3b3;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding: 4px;
}

QStatusBar QLabel {
    color: #b3b3b3;
    font-size: 12px;
}

/* Checkboxes */
QCheckBox {
    color: #ffffff;
    spacing: 10px;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    background: rgba(42, 42, 42, 0.7);
}

QCheckBox::indicator:hover {
    border: 2px solid #1DB954;
    background: rgba(52, 52, 52, 0.8);
}

QCheckBox::indicator:checked {
    background: #1DB954;
    border: 2px solid #1DB954;
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNEw2IDExLjMzMzNMMi42NjY2NyA4IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
}

/* Radio Buttons */
QRadioButton {
    color: #ffffff;
    spacing: 10px;
    font-size: 14px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    background: rgba(42, 42, 42, 0.7);
}

QRadioButton::indicator:hover {
    border: 2px solid #1DB954;
    background: rgba(52, 52, 52, 0.8);
}

QRadioButton::indicator:checked {
    background: #1DB954;
    border: 2px solid #1DB954;
}

QRadioButton::indicator:checked::after {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 4px;
    background: #000000;
}

/* Text Edit */
QTextEdit {
    background: rgba(26, 26, 26, 0.7);
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 12px;
    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
    font-size: 11px;
    selection-background-color: #1DB954;
    selection-color: #000000;
}

QTextEdit:focus {
    border: 2px solid #1DB954;
}

/* Table Widget */
QTableWidget {
    background: rgba(26, 26, 26, 0.7);
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    gridline-color: rgba(255, 255, 255, 0.1);
    selection-background-color: rgba(29, 185, 84, 0.3);
    selection-color: #ffffff;
}

QTableWidget::item {
    padding: 8px;
    border: none;
}

QTableWidget::item:hover {
    background: rgba(42, 42, 42, 0.7);
}

QHeaderView::section {
    background: rgba(42, 42, 42, 0.8);
    color: #ffffff;
    padding: 8px;
    border: none;
    border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    font-weight: 600;
}

/* Dialog Styles */
QDialog {
    background: rgba(16, 16, 16, 0.95);
    color: #ffffff;
}

/* Menu Styles */
QMenu {
    background: rgba(26, 26, 26, 0.95);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 6px;
}

QMenu::item:selected {
    background: rgba(29, 185, 84, 0.3);
}

QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 0.1);
    margin: 4px 8px;
}

/* Scrollbar */
QScrollBar:vertical {
    background: rgba(26, 26, 26, 0.5);
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.3);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: rgba(26, 26, 26, 0.5);
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(255, 255, 255, 0.3);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Frame */
QFrame[frameShape="4"] {
    /* HLine */
    background: rgba(255, 255, 255, 0.1);
    max-height: 1px;
}

QFrame[frameShape="5"] {
    /* VLine */
    background: rgba(255, 255, 255, 0.1);
    max-width: 1px;
}
"""

LIGHT_THEME_STYLESHEET = """
/* Global Styles */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

QMainWindow {
    background: #f5f5f5;
}

QWidget {
    background: #f5f5f5;
    color: #1a1a1a;
}

QLabel {
    color: #1a1a1a;
}

QLabel[objectName="sectionHeader"] {
    color: #000000;
    font-weight: 700;
}

QLabel[objectName="appLogo"] {
    color: #1DB954;
}

QLabel[objectName="authStatus"],
QLabel[objectName="deviceStatus"] {
    color: #555555;
}

QListWidget {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid #d0d0d0;
    color: #1a1a1a;
}

QListWidget::item {
    color: #1a1a1a;
}

QListWidget::item:selected {
    background: #1DB954;
    color: #000000;
}

QListWidget::item:hover {
    background: #e8e8e8;
}

QPushButton {
    background: #1DB954;
    color: #000000;
    border: none;
    border-radius: 500px;
    padding: 12px 32px;
    font-weight: 700;
    font-size: 14px;
}

QPushButton:hover {
    background: #1ed760;
}

QPushButton:disabled {
    background: #d0d0d0;
    color: #888888;
}

QTimeEdit {
    background: #ffffff;
    color: #1a1a1a;
    border: 2px solid #d0d0d0;
    border-radius: 6px;
    padding: 12px;
    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
    font-weight: 600;
}

QTimeEdit:focus {
    border: 2px solid #1DB954;
}

QLineEdit {
    background: #ffffff;
    color: #1a1a1a;
    border: 2px solid #d0d0d0;
    border-radius: 6px;
    padding: 10px 14px;
}

QLineEdit:focus {
    border: 2px solid #1DB954;
}

QComboBox {
    background: #ffffff;
    color: #1a1a1a;
    border: 2px solid #d0d0d0;
    border-radius: 6px;
    padding: 10px 14px;
}

QComboBox:hover, QComboBox:focus {
    border: 2px solid #1DB954;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    color: #1a1a1a;
    border: 1px solid #d0d0d0;
    selection-background-color: #1DB954;
    selection-color: #000000;
}

QSlider::groove:horizontal {
    background: #d0d0d0;
    height: 4px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #1a1a1a;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #1DB954;
}

QSlider::sub-page:horizontal {
    background: #1DB954;
}

QStatusBar {
    background: #e8e8e8;
    color: #1a1a1a;
    border-top: 1px solid #d0d0d0;
}

QStatusBar QLabel {
    color: #555555;
}
"""


def get_stylesheet(theme='dark'):
    """
    Get the stylesheet for the specified theme.
    
    Args:
        theme: 'dark' or 'light'
        
    Returns:
        str: Stylesheet CSS
    """
    if theme == 'light':
        return LIGHT_THEME_STYLESHEET
    return DARK_THEME_STYLESHEET
