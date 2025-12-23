"""
UI Enhancement utilities for Alarmify
Provides custom styling and visual effects that work reliably with PyQt5
"""

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QBrush, QPen, QFont
from PyQt5.QtWidgets import QWidget, QProxyStyle, QStyleOption


class ModernStyle(QProxyStyle):
    """Custom style that applies modern visual effects"""
    
    def drawPrimitive(self, element, option, painter, widget=None):
        """Override drawing for custom visual effects"""
        if element == self.PE_PanelItemViewItem:
            # Custom selection highlight
            if option.state & self.State_Selected:
                painter.setRenderHint(QPainter.Antialiasing)
                gradient = QLinearGradient(option.rect.topLeft(), option.rect.bottomLeft())
                gradient.setColorAt(0, QColor(29, 185, 84, 50))
                gradient.setColorAt(1, QColor(29, 185, 84, 30))
                painter.fillRect(option.rect, gradient)
                
                # Left border accent
                pen = QPen(QColor(29, 185, 84), 3)
                painter.setPen(pen)
                painter.drawLine(option.rect.left(), option.rect.top(), 
                               option.rect.left(), option.rect.bottom())
                return
        
        super().drawPrimitive(element, option, painter, widget)


class GlassWidget(QWidget):
    """A widget with glassmorphism effect"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Semi-transparent background
        bg_color = QColor(26, 26, 26, 230)
        painter.fillRect(self.rect(), bg_color)
        
        # Border
        pen = QPen(QColor(255, 255, 255, 30), 1)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 12, 12)


def apply_modern_styling(widget):
    """Apply modern styling directly to a widget"""
    widget.setStyleSheet("""
        QWidget {
            background-color: #0a0a0a;
            color: #ffffff;
        }
        QPushButton {
            background-color: #1DB954;
            color: #000000;
            border: none;
            border-radius: 20px;
            padding: 12px 32px;
            font-weight: 700;
            font-size: 14px;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: #1ed760;
        }
        QPushButton:pressed {
            background-color: #1aa34a;
        }
        QLineEdit, QTimeEdit {
            background-color: #1a1a1a;
            color: #ffffff;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
        }
        QLineEdit:focus, QTimeEdit:focus {
            border: 2px solid #1DB954;
            background-color: #1f1f1f;
        }
        QListWidget {
            background-color: #1a1a1a;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 8px;
        }
        QListWidget::item {
            padding: 8px;
            border-radius: 8px;
            margin: 2px;
        }
        QListWidget::item:selected {
            background-color: rgba(29, 185, 84, 0.3);
            border-left: 4px solid #1DB954;
        }
        QListWidget::item:hover {
            background-color: rgba(42, 42, 42, 0.9);
        }
        QComboBox {
            background-color: #1a1a1a;
            color: #ffffff;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px;
        }
        QComboBox:hover {
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        QComboBox:focus {
            border: 2px solid #1DB954;
        }
        QSlider::groove:horizontal {
            background: #3a3a3a;
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
        }
        QSlider::sub-page:horizontal {
            background: #1DB954;
        }
    """)


def create_gradient_button(text, parent=None):
    """Create a button with gradient effect"""
    from PyQt5.QtWidgets import QPushButton
    
    btn = QPushButton(text, parent)
    btn.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1DB954, stop:1 #1aa34a);
            color: #000000;
            border: none;
            border-radius: 20px;
            padding: 12px 32px;
            font-weight: 700;
            font-size: 14px;
            min-height: 40px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1ed760, stop:1 #1DB954);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1aa34a, stop:1 #189944);
        }
    """)
    return btn

