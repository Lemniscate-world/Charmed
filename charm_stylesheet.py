"""
charm_stylesheet.py - Charm-inspired stylesheets with advanced glassmorphism

Provides modern, animated stylesheets following DESIGN_SYSTEM.md specifications.
Features:
- Advanced glassmorphism effects with blur and transparency
- Smooth spring-based transitions
- Enhanced visual hierarchy with proper shadows
- Inter font for UI, JetBrains Mono for code/time
- Spotify green (#1DB954) as primary accent
- High DPI support with proper scaling
"""

DARK_THEME_STYLESHEET = """
/* ============================================================================
   GLOBAL STYLES & TYPOGRAPHY
   ============================================================================ */

* {
    font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    font-weight: 400;
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

/* Typography Hierarchy */
QLabel {
    color: #b3b3b3;
    font-size: 14px;
    font-weight: 400;
    line-height: 1.5;
}

QLabel[objectName="appLogo"] {
    color: #1DB954;
    font-size: 32px;
    font-weight: 700;
    letter-spacing: -0.5px;
}

QLabel[objectName="sectionHeader"] {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.3px;
    margin-bottom: 8px;
}

QLabel[objectName="authStatus"],
QLabel[objectName="deviceStatus"] {
    font-size: 12px;
    font-weight: 500;
    padding: 6px 12px;
    border-radius: 6px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(42, 42, 42, 0.6),
        stop:1 rgba(32, 32, 32, 0.8));
    border: 1px solid rgba(255, 255, 255, 0.08);
}

/* ============================================================================
   BUTTONS - Spring Animation Ready
   ============================================================================ */

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1ED760,
        stop:1 #1DB954);
    color: #000000;
    border: none;
    border-radius: 500px;
    padding: 12px 32px;
    font-weight: 700;
    font-size: 14px;
    min-height: 40px;
    letter-spacing: 0.3px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1FED70,
        stop:1 #1ED760);
    transform: translateY(-1px);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1AA34A,
        stop:1 #169C46);
    transform: translateY(0px);
}

QPushButton:disabled {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(42, 42, 42, 0.6),
        stop:1 rgba(32, 32, 32, 0.8));
    color: #666666;
}

/* Icon Buttons */
QPushButton[objectName="settingsButton"],
QPushButton[objectName="refreshButton"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(52, 52, 52, 0.8),
        stop:1 rgba(42, 42, 42, 0.9));
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 50%;
    padding: 0;
    font-size: 18px;
    min-height: 40px;
}

QPushButton[objectName="settingsButton"]:hover,
QPushButton[objectName="refreshButton"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(62, 62, 62, 0.9),
        stop:1 rgba(52, 52, 52, 1.0));
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* ============================================================================
   INPUT FIELDS - Glassmorphism
   ============================================================================ */

QLineEdit {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(52, 52, 52, 0.6),
        stop:1 rgba(42, 42, 42, 0.8));
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 500;
    selection-background-color: #1DB954;
    selection-color: #000000;
}

QLineEdit:focus {
    border: 2px solid #1DB954;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(61, 61, 61, 0.8),
        stop:1 rgba(51, 51, 51, 0.9));
}

QLineEdit:hover {
    border: 2px solid rgba(255, 255, 255, 0.25);
}

QLineEdit::placeholder {
    color: #666666;
}

QLineEdit[objectName="playlistSearch"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(52, 52, 52, 0.6),
        stop:1 rgba(42, 42, 42, 0.8));
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 12px 16px;
    color: #ffffff;
    font-size: 14px;
    font-weight: 500;
}

QLineEdit[objectName="playlistSearch"]:focus {
    border: 2px solid #1DB954;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(61, 61, 61, 0.8),
        stop:1 rgba(51, 51, 51, 0.9));
}

/* ============================================================================
   TIME INPUT - Monospace with Glassmorphism
   ============================================================================ */

QTimeEdit {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(36, 36, 36, 0.7),
        stop:1 rgba(26, 26, 26, 0.9));
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: 16px 20px;
    font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
    font-size: 32px;
    font-weight: 700;
    selection-background-color: #1DB954;
    selection-color: #000000;
}

QTimeEdit:focus {
    border: 2px solid #1DB954;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(41, 41, 41, 0.8),
        stop:1 rgba(31, 31, 31, 0.95));
}

QTimeEdit:hover {
    border: 2px solid rgba(255, 255, 255, 0.25);
}

QTimeEdit::up-button, QTimeEdit::down-button {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(52, 52, 52, 0.8),
        stop:1 rgba(42, 42, 42, 0.9));
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    width: 28px;
    height: 18px;
}

QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(62, 62, 62, 0.9),
        stop:1 rgba(52, 52, 52, 1.0));
    border: 1px solid rgba(255, 255, 255, 0.2);
}

QTimeEdit::up-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-bottom: 6px solid #ffffff;
    width: 0;
    height: 0;
}

QTimeEdit::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #ffffff;
    width: 0;
    height: 0;
}

/* ============================================================================
   PLAYLIST LIST - Glass Card Effect
   ============================================================================ */

QListWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(36, 36, 36, 0.7),
        stop:1 rgba(26, 26, 26, 0.9));
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
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(52, 52, 52, 0.8),
        stop:1 rgba(42, 42, 42, 0.9));
}

QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(29, 185, 84, 0.35),
        stop:1 rgba(29, 185, 84, 0.25));
    border-left: 4px solid #1DB954;
}

/* ============================================================================
   COMBOBOX - Glassmorphism Dropdown
   ============================================================================ */

QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(52, 52, 52, 0.7),
        stop:1 rgba(42, 42, 42, 0.9));
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 500;
    selection-background-color: #1DB954;
}

QComboBox:hover {
    border: 2px solid rgba(255, 255, 255, 0.25);
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(62, 62, 62, 0.8),
        stop:1 rgba(52, 52, 52, 0.9));
}

QComboBox:focus {
    border: 2px solid #1DB954;
}

QComboBox::drop-down {
    border: none;
    width: 32px;
    padding-right: 8px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #ffffff;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(36, 36, 36, 0.95),
        stop:1 rgba(26, 26, 26, 0.98));
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 6px;
    selection-background-color: #1DB954;
    selection-color: #000000;
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 10px 14px;
    border-radius: 6px;
    min-height: 36px;
    font-weight: 500;
}

QComboBox QAbstractItemView::item:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(52, 52, 52, 0.9),
        stop:1 rgba(42, 42, 42, 0.95));
}

/* ============================================================================
   SLIDER - Modern with Spring Effect
   ============================================================================ */

QSlider::groove:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(58, 58, 58, 0.8),
        stop:1 rgba(48, 48, 48, 0.9));
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff,
        stop:1 #f0f0f0);
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
    border: 2px solid rgba(255, 255, 255, 0.9);
}

QSlider::handle:horizontal:hover {
    background: #1DB954;
    width: 24px;
    height: 24px;
    margin: -8px 0;
    border: 2px solid #1ED760;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #1DB954, 
                                stop:0.5 #1ED760,
                                stop:1 #1FED70);
    border-radius: 4px;
}

/* ============================================================================
   STATUS BAR
   ============================================================================ */

QStatusBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(26, 26, 26, 0.95),
        stop:1 rgba(16, 16, 16, 0.98));
    color: #b3b3b3;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding: 6px;
    font-size: 12px;
}

QStatusBar QLabel {
    color: #b3b3b3;
    font-size: 12px;
    font-weight: 500;
}

/* ============================================================================
   CHECKBOXES - Modern Style
   ============================================================================ */

QCheckBox {
    color: #ffffff;
    spacing: 10px;
    font-size: 14px;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 22px;
    height: 22px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 7px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(52, 52, 52, 0.7),
        stop:1 rgba(42, 42, 42, 0.9));
}

QCheckBox::indicator:hover {
    border: 2px solid #1DB954;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(62, 62, 62, 0.8),
        stop:1 rgba(52, 52, 52, 0.9));
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1ED760,
        stop:1 #1DB954);
    border: 2px solid #1DB954;
}

/* ============================================================================
   RADIO BUTTONS
   ============================================================================ */

QRadioButton {
    color: #ffffff;
    spacing: 10px;
    font-size: 14px;
    font-weight: 500;
}

QRadioButton::indicator {
    width: 22px;
    height: 22px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 11px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(52, 52, 52, 0.7),
        stop:1 rgba(42, 42, 42, 0.9));
}

QRadioButton::indicator:hover {
    border: 2px solid #1DB954;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(62, 62, 62, 0.8),
        stop:1 rgba(52, 52, 52, 0.9));
}

QRadioButton::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1ED760,
        stop:1 #1DB954);
    border: 2px solid #1DB954;
}

/* ============================================================================
   TEXT EDIT - Code Style
   ============================================================================ */

QTextEdit {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(36, 36, 36, 0.7),
        stop:1 rgba(26, 26, 26, 0.9));
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 14px;
    font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    line-height: 1.6;
    selection-background-color: #1DB954;
    selection-color: #000000;
}

QTextEdit:focus {
    border: 2px solid #1DB954;
}

/* ============================================================================
   TABLE WIDGET
   ============================================================================ */

QTableWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(36, 36, 36, 0.7),
        stop:1 rgba(26, 26, 26, 0.9));
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    gridline-color: rgba(255, 255, 255, 0.08);
    selection-background-color: rgba(29, 185, 84, 0.35);
    selection-color: #ffffff;
}

QTableWidget::item {
    padding: 10px;
    border: none;
}

QTableWidget::item:hover {
    background: rgba(52, 52, 52, 0.7);
}

QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(52, 52, 52, 0.9),
        stop:1 rgba(42, 42, 42, 0.95));
    color: #ffffff;
    padding: 10px;
    border: none;
    border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    font-weight: 600;
    font-size: 13px;
}

/* ============================================================================
   DIALOG STYLES - Enhanced Glassmorphism
   ============================================================================ */

QDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(26, 26, 26, 0.95),
        stop:1 rgba(16, 16, 16, 0.98));
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
}

/* ============================================================================
   MENU STYLES
   ============================================================================ */

QMenu {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(36, 36, 36, 0.95),
        stop:1 rgba(26, 26, 26, 0.98));
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 10px 28px 10px 14px;
    border-radius: 6px;
    font-weight: 500;
}

QMenu::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(29, 185, 84, 0.35),
        stop:1 rgba(29, 185, 84, 0.25));
}

QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 0.1);
    margin: 6px 10px;
}

/* ============================================================================
   SCROLLBAR - Minimal Design
   ============================================================================ */

QScrollBar:vertical {
    background: rgba(26, 26, 26, 0.5);
    width: 14px;
    border-radius: 7px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(255, 255, 255, 0.25),
        stop:1 rgba(255, 255, 255, 0.2));
    border-radius: 7px;
    min-height: 40px;
}

QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(255, 255, 255, 0.35),
        stop:1 rgba(255, 255, 255, 0.3));
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: rgba(26, 26, 26, 0.5);
    height: 14px;
    border-radius: 7px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.25),
        stop:1 rgba(255, 255, 255, 0.2));
    border-radius: 7px;
    min-width: 40px;
}

QScrollBar::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.35),
        stop:1 rgba(255, 255, 255, 0.3));
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ============================================================================
   FRAME / SEPARATOR
   ============================================================================ */

QFrame[frameShape="4"] {
    /* HLine */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(255, 255, 255, 0.05),
        stop:0.5 rgba(255, 255, 255, 0.12),
        stop:1 rgba(255, 255, 255, 0.05));
    max-height: 1px;
    border: none;
}

QFrame[frameShape="5"] {
    /* VLine */
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.05),
        stop:0.5 rgba(255, 255, 255, 0.12),
        stop:1 rgba(255, 255, 255, 0.05));
    max-width: 1px;
    border: none;
}

/* ============================================================================
   TAB WIDGET
   ============================================================================ */

QTabWidget::pane {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(36, 36, 36, 0.7),
        stop:1 rgba(26, 26, 26, 0.9));
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px;
}

QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(52, 52, 52, 0.7),
        stop:1 rgba(42, 42, 42, 0.9));
    color: #b3b3b3;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(62, 62, 62, 0.8),
        stop:1 rgba(52, 52, 52, 0.9));
    color: #ffffff;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(29, 185, 84, 0.3),
        stop:1 rgba(29, 185, 84, 0.4));
    color: #ffffff;
    border: 1px solid rgba(29, 185, 84, 0.5);
    border-bottom: none;
}

/* ============================================================================
   TOOLTIP
   ============================================================================ */

QToolTip {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(42, 42, 42, 0.95),
        stop:1 rgba(32, 32, 32, 0.98));
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    font-weight: 500;
}
"""

LIGHT_THEME_STYLESHEET = """
/* Light theme optimized for daytime use */
* {
    font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
}

QMainWindow {
    background: #f8f8f8;
}

QWidget {
    background: #f8f8f8;
    color: #1a1a1a;
}

QLabel {
    color: #333333;
}

QLabel[objectName="sectionHeader"] {
    color: #000000;
    font-weight: 700;
    font-size: 18px;
}

QLabel[objectName="appLogo"] {
    color: #1DB954;
    font-size: 32px;
    font-weight: 700;
}

QLabel[objectName="authStatus"],
QLabel[objectName="deviceStatus"] {
    color: #555555;
    font-weight: 500;
    background: rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 6px;
    padding: 6px 12px;
}

QListWidget {
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid rgba(0, 0, 0, 0.1);
    border-radius: 12px;
    color: #1a1a1a;
}

QListWidget::item {
    color: #1a1a1a;
    border-radius: 8px;
    padding: 8px;
}

QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(29, 185, 84, 0.25),
        stop:1 rgba(29, 185, 84, 0.15));
    border-left: 4px solid #1DB954;
}

QListWidget::item:hover {
    background: rgba(0, 0, 0, 0.05);
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1ED760,
        stop:1 #1DB954);
    color: #000000;
    border: none;
    border-radius: 500px;
    padding: 12px 32px;
    font-weight: 700;
    font-size: 14px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1FED70,
        stop:1 #1ED760);
}

QPushButton:disabled {
    background: rgba(0, 0, 0, 0.1);
    color: #888888;
}

QTimeEdit {
    background: #ffffff;
    color: #1a1a1a;
    border: 2px solid rgba(0, 0, 0, 0.15);
    border-radius: 12px;
    padding: 16px;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 32px;
    font-weight: 700;
}

QTimeEdit:focus {
    border: 2px solid #1DB954;
}

QLineEdit {
    background: #ffffff;
    color: #1a1a1a;
    border: 2px solid rgba(0, 0, 0, 0.15);
    border-radius: 8px;
    padding: 12px 16px;
    font-weight: 500;
}

QLineEdit:focus {
    border: 2px solid #1DB954;
}

QComboBox {
    background: #ffffff;
    color: #1a1a1a;
    border: 2px solid rgba(0, 0, 0, 0.15);
    border-radius: 8px;
    padding: 12px 16px;
    font-weight: 500;
}

QComboBox:hover, QComboBox:focus {
    border: 2px solid #1DB954;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    color: #1a1a1a;
    border: 1px solid rgba(0, 0, 0, 0.2);
    selection-background-color: #1DB954;
    selection-color: #000000;
}

QSlider::groove:horizontal {
    background: rgba(0, 0, 0, 0.1);
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #1a1a1a;
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background: #1DB954;
    width: 24px;
    height: 24px;
    margin: -8px 0;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1DB954, 
        stop:1 #1ED760);
}

QStatusBar {
    background: rgba(0, 0, 0, 0.05);
    color: #555555;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
}

QStatusBar QLabel {
    color: #555555;
}

QCheckBox::indicator {
    width: 22px;
    height: 22px;
    border: 2px solid rgba(0, 0, 0, 0.3);
    border-radius: 7px;
    background: #ffffff;
}

QCheckBox::indicator:checked {
    background: #1DB954;
    border-color: #1DB954;
}

QRadioButton::indicator {
    width: 22px;
    height: 22px;
    border: 2px solid rgba(0, 0, 0, 0.3);
    border-radius: 11px;
    background: #ffffff;
}

QRadioButton::indicator:checked {
    background: #1DB954;
    border-color: #1DB954;
}
"""


def get_stylesheet(theme='dark'):
    """
    Get the stylesheet for the specified theme.
    
    Args:
        theme: 'dark' or 'light'
        
    Returns:
        str: Stylesheet CSS with advanced glassmorphism
    """
    if theme == 'light':
        return LIGHT_THEME_STYLESHEET
    return DARK_THEME_STYLESHEET
