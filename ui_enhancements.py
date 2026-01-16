"""
ui_enhancements.py - UI enhancement utilities for Charm design system

Provides helper functions and utilities for applying consistent:
- Glassmorphism effects to dialogs and cards
- Spring-based animations
- Visual effects and shadows
- Proper styling for custom widgets
"""

from PyQt5.QtWidgets import QDialog, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from charm_animations import AnimationBuilder, apply_entrance_animations


def apply_glassmorphism_to_dialog(dialog):
    """
    Apply glassmorphism styling to a QDialog.
    
    Creates a semi-transparent background with proper borders
    and shadow effects for depth perception.
    
    Args:
        dialog: QDialog instance to enhance
    """
    dialog.setWindowFlags(dialog.windowFlags() | Qt.FramelessWindowHint)
    dialog.setAttribute(Qt.WA_TranslucentBackground)
    
    # Apply inline stylesheet for glassmorphism
    dialog.setStyleSheet("""
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(26, 26, 26, 0.95),
                stop:1 rgba(16, 16, 16, 0.98));
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
        }
    """)
    
    # Add shadow effect
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(30)
    shadow.setXOffset(0)
    shadow.setYOffset(8)
    shadow.setColor(QColor(0, 0, 0, 160))
    dialog.setGraphicsEffect(shadow)


def apply_card_effect(widget):
    """
    Apply card-style glassmorphism to a widget.
    
    Creates a glass card appearance suitable for content containers.
    
    Args:
        widget: QWidget instance to style as card
    """
    widget.setStyleSheet("""
        QWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(36, 36, 36, 0.7),
                stop:1 rgba(26, 26, 26, 0.9));
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 16px;
        }
    """)
    
    # Add subtle shadow
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setXOffset(0)
    shadow.setYOffset(4)
    shadow.setColor(QColor(0, 0, 0, 100))
    widget.setGraphicsEffect(shadow)


def apply_elevated_effect(widget):
    """
    Apply elevated surface styling with enhanced shadow.
    
    Suitable for floating action buttons or elevated panels.
    
    Args:
        widget: QWidget instance to elevate
    """
    widget.setStyleSheet("""
        QWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(52, 52, 52, 0.9),
                stop:1 rgba(42, 42, 42, 0.95));
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
        }
    """)
    
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(25)
    shadow.setXOffset(0)
    shadow.setYOffset(6)
    shadow.setColor(QColor(0, 0, 0, 140))
    widget.setGraphicsEffect(shadow)


def animate_dialog_entrance(dialog, duration=250):
    """
    Animate dialog appearance with fade-in.
    
    Args:
        dialog: QDialog to animate
        duration: Animation duration in milliseconds
        
    Returns:
        QPropertyAnimation: The animation object
    """
    return AnimationBuilder.create_fade_in(dialog, duration=duration)


def animate_widget_list(widgets, stagger=50):
    """
    Animate a list of widgets with staggered entrance.
    
    Args:
        widgets: List of QWidget instances
        stagger: Delay between each widget in milliseconds
    """
    apply_entrance_animations(widgets, stagger_delay=stagger)


def create_status_pill(text, color='green'):
    """
    Create a styled status pill widget.
    
    Args:
        text: Text to display
        color: Color theme ('green', 'blue', 'orange', 'red')
        
    Returns:
        QLabel: Styled status pill
    """
    from PyQt5.QtWidgets import QLabel
    
    label = QLabel(text)
    
    color_map = {
        'green': '#1DB954',
        'blue': '#1E90FF',
        'orange': '#FFA500',
        'red': '#FF6B6B'
    }
    
    bg_color = color_map.get(color, '#1DB954')
    
    label.setStyleSheet(f"""
        QLabel {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba({int(bg_color[1:3], 16)}, {int(bg_color[3:5], 16)}, {int(bg_color[5:7], 16)}, 0.3),
                stop:1 rgba({int(bg_color[1:3], 16)}, {int(bg_color[3:5], 16)}, {int(bg_color[5:7], 16)}, 0.2));
            color: {bg_color};
            border: 1px solid {bg_color};
            border-radius: 12px;
            padding: 4px 12px;
            font-weight: 600;
            font-size: 11px;
        }}
    """)
    
    return label


def apply_hover_glow(widget, glow_color='#1DB954'):
    """
    Apply hover glow effect to a widget.
    
    Note: This sets up the stylesheet; actual hover state managed by Qt.
    
    Args:
        widget: QWidget to apply glow to
        glow_color: Hex color for glow effect
    """
    widget.setStyleSheet(f"""
        QWidget {{
            border: 2px solid transparent;
            border-radius: 8px;
            transition: border 0.2s ease;
        }}
        QWidget:hover {{
            border: 2px solid {glow_color};
        }}
    """)


def create_separator(orientation='horizontal'):
    """
    Create a styled separator line.
    
    Args:
        orientation: 'horizontal' or 'vertical'
        
    Returns:
        QFrame: Styled separator
    """
    from PyQt5.QtWidgets import QFrame
    
    separator = QFrame()
    
    if orientation == 'horizontal':
        separator.setFrameShape(QFrame.HLine)
        separator.setMaximumHeight(1)
    else:
        separator.setFrameShape(QFrame.VLine)
        separator.setMaximumWidth(1)
    
    separator.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 0.05),
                stop:0.5 rgba(255, 255, 255, 0.12),
                stop:1 rgba(255, 255, 255, 0.05));
            border: none;
        }
    """)
    
    return separator


def apply_focus_glow(widget, glow_color='#1DB954'):
    """
    Apply focus glow effect for input widgets.
    
    Args:
        widget: Input widget (QLineEdit, QTextEdit, etc.)
        glow_color: Hex color for focus glow
    """
    # Get current stylesheet and append focus styling
    current_style = widget.styleSheet()
    focus_style = f"""
        {widget.__class__.__name__}:focus {{
            border: 2px solid {glow_color};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(61, 61, 61, 0.8),
                stop:1 rgba(51, 51, 51, 0.9));
        }}
    """
    
    widget.setStyleSheet(current_style + focus_style)


def create_gradient_button(text, color_start='#1ED760', color_end='#1DB954'):
    """
    Create a button with gradient styling.
    
    Args:
        text: Button text
        color_start: Hex color for gradient start
        color_end: Hex color for gradient end
        
    Returns:
        QPushButton: Styled button
    """
    from PyQt5.QtWidgets import QPushButton
    
    button = QPushButton(text)
    button.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {color_start},
                stop:1 {color_end});
            color: #000000;
            border: none;
            border-radius: 500px;
            padding: 12px 32px;
            font-weight: 700;
            font-size: 14px;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {color_start}ff,
                stop:1 {color_end}ff);
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {color_end},
                stop:1 {color_start});
        }}
    """)
    
    return button


def apply_glass_panel(widget, transparency=0.7):
    """
    Apply glass panel effect with adjustable transparency.
    
    Args:
        widget: QWidget to style
        transparency: Transparency level (0.0 to 1.0)
    """
    alpha_start = int(255 * transparency)
    alpha_end = int(255 * (transparency + 0.2))
    
    widget.setStyleSheet(f"""
        QWidget {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(36, 36, 36, {alpha_start / 255}),
                stop:1 rgba(26, 26, 26, {alpha_end / 255}));
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
        }}
    """)


def setup_window_for_dpi(window):
    """
    Configure window for proper DPI scaling.
    
    Args:
        window: QMainWindow or QDialog to configure
    """
    # Set size policy
    from PyQt5.QtWidgets import QSizePolicy
    window.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    
    # Enable high DPI pixmaps
    window.setAttribute(Qt.WA_StyledBackground, True)


def create_icon_button(icon_text, tooltip=''):
    """
    Create a circular icon button.
    
    Args:
        icon_text: Unicode character or emoji for icon
        tooltip: Tooltip text
        
    Returns:
        QPushButton: Styled icon button
    """
    from PyQt5.QtWidgets import QPushButton
    
    button = QPushButton(icon_text)
    button.setToolTip(tooltip)
    button.setFixedSize(40, 40)
    button.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(52, 52, 52, 0.8),
                stop:1 rgba(42, 42, 42, 0.9));
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 20px;
            font-size: 18px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(62, 62, 62, 0.9),
                stop:1 rgba(52, 52, 52, 1.0));
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
    """)
    
    return button


def apply_smooth_scroll(scroll_area):
    """
    Apply smooth scrolling behavior to scroll area.
    
    Args:
        scroll_area: QScrollArea to enhance
    """
    from PyQt5.QtCore import Qt
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll_area.setWidgetResizable(True)


# Preset color schemes
COLORS = {
    'spotify_green': '#1DB954',
    'spotify_green_light': '#1ED760',
    'spotify_green_dark': '#169C46',
    'gold': '#FFD700',
    'blue': '#1E90FF',
    'orange': '#FFA500',
    'red': '#FF6B6B',
    'gray_dark': '#1a1a1a',
    'gray_medium': '#2a2a2a',
    'gray_light': '#3a3a3a',
    'text_primary': '#ffffff',
    'text_secondary': '#b3b3b3',
    'text_tertiary': '#666666',
}


# Spacing constants (px)
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 24,
    'xxl': 32,
}


# Border radius constants (px)
RADIUS = {
    'sm': 6,
    'md': 8,
    'lg': 12,
    'pill': 500,
}


# Font sizes (px)
FONT_SIZES = {
    'xs': 11,
    'sm': 12,
    'md': 14,
    'lg': 18,
    'xl': 24,
    'xxl': 32,
}


def get_color(color_name):
    """Get color value from preset colors."""
    return COLORS.get(color_name, '#000000')


def get_spacing(size):
    """Get spacing value from preset sizes."""
    return SPACING.get(size, 8)


def get_radius(size):
    """Get border radius value from preset sizes."""
    return RADIUS.get(size, 8)


def get_font_size(size):
    """Get font size value from preset sizes."""
    return FONT_SIZES.get(size, 14)
