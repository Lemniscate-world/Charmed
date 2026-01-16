"""
icon_generator.py - Generate custom Alarmify icons

Creates SVG-based icons following the design specifications in ICON_DESIGN.md.
Generates icons in multiple sizes for application and system tray use.
"""

from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter, QImage, QColor, QLinearGradient, QPen, QBrush, QFont, QPainterPath
from PyQt5.QtCore import Qt, QRectF, QPointF
from pathlib import Path
import xml.etree.ElementTree as ET


def create_icon_svg(size=512):
    """
    Create the Alarmify icon as SVG.
    
    Args:
        size: Icon size in pixels (square)
        
    Returns:
        str: SVG markup
    """
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1ED760;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1DB954;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="glassHighlight" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.3" />
      <stop offset="50%" style="stop-color:#ffffff;stop-opacity:0" />
    </linearGradient>
    <filter id="shadow">
      <feGaussianBlur in="SourceAlpha" stdDeviation="8"/>
      <feOffset dx="0" dy="4" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.3"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Shadow -->
  <circle cx="256" cy="260" r="200" fill="rgba(0,0,0,0.3)" filter="url(#shadow)"/>
  
  <!-- Main circle background -->
  <circle cx="256" cy="256" r="200" fill="url(#bgGradient)"/>
  
  <!-- Glass highlight overlay -->
  <ellipse cx="256" cy="180" rx="180" ry="120" fill="url(#glassHighlight)" opacity="0.4"/>
  
  <!-- Border -->
  <circle cx="256" cy="256" r="200" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="4"/>
  
  <!-- Clock face -->
  <circle cx="256" cy="256" r="160" fill="rgba(255,255,255,0.15)" opacity="0.8"/>
  
  <!-- Hour markers -->
  <line x1="256" y1="106" x2="256" y2="126" stroke="white" stroke-width="6" stroke-linecap="round" opacity="0.9"/>
  <line x1="406" y1="256" x2="386" y2="256" stroke="white" stroke-width="6" stroke-linecap="round" opacity="0.9"/>
  <line x1="256" y1="406" x2="256" y2="386" stroke="white" stroke-width="6" stroke-linecap="round" opacity="0.9"/>
  <line x1="106" y1="256" x2="126" y2="256" stroke="white" stroke-width="6" stroke-linecap="round" opacity="0.9"/>
  
  <!-- Hour hand (pointing to 10) -->
  <line x1="256" y1="256" x2="206" y2="176" stroke="white" stroke-width="12" stroke-linecap="round">
    <animate attributeName="opacity" values="1;0.8;1" dur="2s" repeatCount="indefinite"/>
  </line>
  
  <!-- Minute hand with music note (pointing to 2) -->
  <path d="M 256 256 L 336 206" stroke="white" stroke-width="10" stroke-linecap="round" fill="none"/>
  
  <!-- Music note at tip of minute hand -->
  <g transform="translate(336, 206)">
    <ellipse cx="0" cy="0" rx="12" ry="12" fill="#FFD700"/>
    <rect x="-2" y="-35" width="4" height="35" fill="#FFD700"/>
    <path d="M -2 -35 Q 15 -38 18 -30 L 18 -10 Q 18 -5 15 -5" stroke="#FFD700" stroke-width="3" fill="none"/>
  </g>
  
  <!-- Center dot -->
  <circle cx="256" cy="256" r="10" fill="white"/>
  
  <!-- Subtle sparkle effect -->
  <circle cx="340" cy="170" r="4" fill="white" opacity="0.8">
    <animate attributeName="opacity" values="0.3;1;0.3" dur="1.5s" repeatCount="indefinite"/>
  </circle>
  <circle cx="360" cy="200" r="3" fill="white" opacity="0.6">
    <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite"/>
  </circle>
</svg>'''
    return svg


def generate_icon_image(size=512, output_path=None):
    """
    Generate icon as QImage.
    
    Args:
        size: Icon size in pixels
        output_path: Optional path to save PNG file
        
    Returns:
        QImage: Rendered icon
    """
    svg_data = create_icon_svg(size).encode('utf-8')
    
    renderer = QSvgRenderer(svg_data)
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()
    
    if output_path:
        image.save(str(output_path), 'PNG')
    
    return image


def generate_tray_icon(size=32, monochrome=False):
    """
    Generate simplified tray icon.
    
    Args:
        size: Icon size in pixels
        monochrome: If True, generate black/white version
        
    Returns:
        QImage: Rendered icon
    """
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    
    center = size / 2
    radius = size * 0.4
    
    if monochrome:
        color = QColor(255, 255, 255)
    else:
        color = QColor(29, 185, 84)
    
    # Circle outline
    pen = QPen(color, max(2, size / 16))
    pen.setCapStyle(Qt.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(QPointF(center, center), radius, radius)
    
    # Clock hands
    painter.drawLine(QPointF(center, center), QPointF(center, center - radius * 0.5))
    painter.drawLine(QPointF(center, center), QPointF(center + radius * 0.6, center - radius * 0.3))
    
    # Music note
    note_x = center + radius * 0.6
    note_y = center - radius * 0.3
    painter.setBrush(QBrush(QColor(255, 215, 0) if not monochrome else color))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QPointF(note_x, note_y), size / 16, size / 16)
    
    painter.end()
    return image


def generate_all_icons(output_dir=None):
    """
    Generate all icon sizes needed for the application.
    
    Args:
        output_dir: Directory to save icon files (defaults to current directory)
    """
    if output_dir is None:
        output_dir = Path(__file__).parent
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Main application icons
    for size in [16, 32, 48, 64, 128, 256, 512]:
        img = generate_icon_image(size)
        img.save(str(output_dir / f'alarmify_icon_{size}.png'), 'PNG')
    
    # System tray icons
    for size in [16, 32, 48]:
        img = generate_tray_icon(size)
        img.save(str(output_dir / f'tray_icon_{size}.png'), 'PNG')
        
        img_mono = generate_tray_icon(size, monochrome=True)
        img_mono.save(str(output_dir / f'tray_icon_{size}_mono.png'), 'PNG')
    
    print(f"Generated all icons in: {output_dir}")


if __name__ == '__main__':
    generate_all_icons()
