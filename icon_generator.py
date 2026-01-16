"""
icon_generator.py - Generate custom Alarmify icons with Charm-inspired design

Creates high-quality SVG-based icons following the design specifications.
Generates icons in multiple sizes for application and system tray use.
Features modern glassmorphism effects and smooth gradients.
"""

from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter, QImage, QColor, QLinearGradient, QPen, QBrush, QFont, QPainterPath, QRadialGradient
from PyQt5.QtCore import Qt, QRectF, QPointF
from pathlib import Path
import xml.etree.ElementTree as ET


def create_icon_svg(size=512):
    """
    Create the Alarmify icon as SVG with enhanced Charm design.
    
    Features:
    - Modern gradient background
    - Glassmorphism effects
    - Animated elements
    - Music note integration
    - Soft shadows and highlights
    
    Args:
        size: Icon size in pixels (square)
        
    Returns:
        str: SVG markup
    """
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Enhanced gradients for modern look -->
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1ED760;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#1DB954;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#169C46;stop-opacity:1" />
    </linearGradient>
    
    <!-- Glass highlight gradient -->
    <linearGradient id="glassHighlight" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.4" />
      <stop offset="30%" style="stop-color:#ffffff;stop-opacity:0.2" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
    </linearGradient>
    
    <!-- Radial gradient for depth -->
    <radialGradient id="radialGlow" cx="50%" cy="40%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
    </radialGradient>
    
    <!-- Shadow filter -->
    <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="12"/>
      <feOffset dx="0" dy="8" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.4"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    <!-- Inner shadow for depth -->
    <filter id="innerShadow">
      <feGaussianBlur in="SourceAlpha" stdDeviation="4"/>
      <feOffset dx="0" dy="2" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.5"/>
      </feComponentTransfer>
    </filter>
  </defs>
  
  <!-- Outer glow/shadow -->
  <circle cx="256" cy="264" r="210" fill="rgba(0,0,0,0.25)" filter="url(#shadow)"/>
  
  <!-- Main circle background with gradient -->
  <circle cx="256" cy="256" r="210" fill="url(#bgGradient)"/>
  
  <!-- Radial glow overlay -->
  <circle cx="256" cy="256" r="210" fill="url(#radialGlow)"/>
  
  <!-- Glass highlight overlay -->
  <ellipse cx="256" cy="170" rx="190" ry="140" fill="url(#glassHighlight)" opacity="0.6"/>
  
  <!-- Subtle border with gradient -->
  <circle cx="256" cy="256" r="210" fill="none" stroke="url(#glassHighlight)" stroke-width="3"/>
  
  <!-- Clock face background -->
  <circle cx="256" cy="256" r="165" fill="rgba(255,255,255,0.18)" opacity="0.9"/>
  
  <!-- Inner clock face border -->
  <circle cx="256" cy="256" r="165" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
  
  <!-- Hour markers with improved design -->
  <g stroke="white" stroke-width="8" stroke-linecap="round" opacity="0.95">
    <!-- 12 o'clock -->
    <line x1="256" y1="101" x2="256" y2="121"/>
    <!-- 3 o'clock -->
    <line x1="411" y1="256" x2="391" y2="256"/>
    <!-- 6 o'clock -->
    <line x1="256" y1="411" x2="256" y2="391"/>
    <!-- 9 o'clock -->
    <line x1="101" y1="256" x2="121" y2="256"/>
  </g>
  
  <!-- Secondary hour markers (smaller) -->
  <g stroke="white" stroke-width="4" stroke-linecap="round" opacity="0.7">
    <!-- 1 o'clock -->
    <line x1="318" y1="127" x2="310" y2="140"/>
    <!-- 2 o'clock -->
    <line x1="375" y1="181" x2="365" y2="192"/>
    <!-- 4 o'clock -->
    <line x1="385" y1="318" x2="372" y2="310"/>
    <!-- 5 o'clock -->
    <line x1="330" y1="375" x2="320" y2="365"/>
    <!-- 7 o'clock -->
    <line x1="192" y1="385" x2="202" y2="372"/>
    <!-- 8 o'clock -->
    <line x1="137" y1="330" x2="147" y2="320"/>
    <!-- 10 o'clock -->
    <line x1="127" y1="194" x2="140" y2="202"/>
    <!-- 11 o'clock -->
    <line x1="181" y1="137" x2="192" y2="147"/>
  </g>
  
  <!-- Hour hand (pointing to 10) with shadow -->
  <g>
    <line x1="256" y1="256" x2="201" y2="168" stroke="rgba(0,0,0,0.2)" stroke-width="14" stroke-linecap="round"/>
    <line x1="256" y1="256" x2="199" y2="166" stroke="white" stroke-width="14" stroke-linecap="round">
      <animate attributeName="opacity" values="1;0.85;1" dur="3s" repeatCount="indefinite"/>
    </line>
  </g>
  
  <!-- Minute hand (pointing to 2) with shadow -->
  <g>
    <line x1="256" y1="256" x2="348" y2="198" stroke="rgba(0,0,0,0.2)" stroke-width="11" stroke-linecap="round"/>
    <line x1="256" y1="256" x2="346" y2="196" stroke="white" stroke-width="11" stroke-linecap="round"/>
  </g>
  
  <!-- Music note at tip of minute hand with enhanced design -->
  <g transform="translate(346, 196)">
    <!-- Note shadow -->
    <ellipse cx="2" cy="2" rx="16" ry="16" fill="rgba(0,0,0,0.3)"/>
    <rect x="0" y="-41" width="5" height="41" fill="rgba(0,0,0,0.3)"/>
    
    <!-- Note head -->
    <ellipse cx="0" cy="0" rx="15" ry="15" fill="#FFD700"/>
    <ellipse cx="-3" cy="-3" rx="6" ry="6" fill="rgba(255,255,255,0.4)"/>
    
    <!-- Note stem -->
    <rect x="-2" y="-40" width="4" height="40" fill="#FFD700"/>
    
    <!-- Note flag with curve -->
    <path d="M -2 -40 Q 16 -43 20 -34 L 20 -12 Q 20 -6 16 -6" stroke="#FFD700" stroke-width="4" fill="none" stroke-linecap="round"/>
    
    <!-- Shine effect on note -->
    <ellipse cx="-4" cy="-4" rx="5" ry="5" fill="rgba(255,255,255,0.6)">
      <animate attributeName="opacity" values="0.4;0.8;0.4" dur="2s" repeatCount="indefinite"/>
    </ellipse>
  </g>
  
  <!-- Center dot with depth -->
  <circle cx="256" cy="258" r="14" fill="rgba(0,0,0,0.3)"/>
  <circle cx="256" cy="256" r="13" fill="white"/>
  <circle cx="253" cy="253" r="5" fill="rgba(255,255,255,0.6)"/>
  
  <!-- Sparkle effects with animation -->
  <g opacity="0.9">
    <circle cx="350" cy="160" r="5" fill="white">
      <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="r" values="4;6;4" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="375" cy="195" r="3.5" fill="white">
      <animate attributeName="opacity" values="0.4;0.9;0.4" dur="2.5s" repeatCount="indefinite"/>
      <animate attributeName="r" values="3;5;3" dur="2.5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="165" cy="345" r="4" fill="white">
      <animate attributeName="opacity" values="0.5;1;0.5" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="r" values="3;5;3" dur="3s" repeatCount="indefinite"/>
    </circle>
  </g>
</svg>'''
    return svg


def generate_icon_image(size=512, output_path=None):
    """
    Generate icon as QImage with high quality rendering.
    
    Args:
        size: Icon size in pixels
        output_path: Optional path to save PNG file
        
    Returns:
        QImage: Rendered icon with antialiasing
    """
    svg_data = create_icon_svg(size).encode('utf-8')
    
    renderer = QSvgRenderer(svg_data)
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
    renderer.render(painter)
    painter.end()
    
    if output_path:
        image.save(str(output_path), 'PNG', 100)
    
    return image


def generate_tray_icon(size=32, monochrome=False):
    """
    Generate simplified tray icon with clean design.
    
    Features:
    - Minimalist clock design
    - Optional monochrome for system compatibility
    - Clear visual at small sizes
    
    Args:
        size: Icon size in pixels (16, 32, or 48 recommended)
        monochrome: If True, generate monochrome version for system tray
        
    Returns:
        QImage: Rendered tray icon
    """
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    
    center = size / 2
    radius = size * 0.38
    
    # Color selection
    if monochrome:
        main_color = QColor(255, 255, 255)
        accent_color = QColor(255, 255, 255)
    else:
        main_color = QColor(29, 185, 84)  # Spotify green
        accent_color = QColor(255, 215, 0)  # Gold for music note
    
    # Draw circle background with subtle gradient
    if not monochrome:
        gradient = QRadialGradient(center, center * 0.7, radius * 1.2)
        gradient.setColorAt(0, QColor(30, 215, 96, 200))
        gradient.setColorAt(1, QColor(29, 185, 84, 255))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(center, center), radius * 1.05, radius * 1.05)
    
    # Circle outline
    pen = QPen(main_color, max(2, size / 16))
    pen.setCapStyle(Qt.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(QPointF(center, center), radius, radius)
    
    # Clock hands with improved proportions
    pen.setWidth(int(max(2, size / 20)))
    painter.setPen(pen)
    
    # Hour hand (shorter, thicker)
    hour_length = radius * 0.5
    painter.drawLine(
        QPointF(center, center),
        QPointF(center - hour_length * 0.5, center - hour_length * 0.866)  # 10 o'clock position
    )
    
    # Minute hand (longer, thinner)
    pen.setWidth(int(max(2, size / 24)))
    painter.setPen(pen)
    minute_length = radius * 0.7
    painter.drawLine(
        QPointF(center, center),
        QPointF(center + minute_length * 0.866, center - minute_length * 0.5)  # 2 o'clock position
    )
    
    # Music note at minute hand tip
    note_x = center + minute_length * 0.866
    note_y = center - minute_length * 0.5
    note_size = max(3, size / 10)
    
    painter.setBrush(QBrush(accent_color))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QPointF(note_x, note_y), note_size * 0.8, note_size * 0.8)
    
    # Note stem
    painter.fillRect(
        int(note_x - note_size * 0.15),
        int(note_y - note_size * 2),
        max(1, int(note_size * 0.3)),
        int(note_size * 2),
        accent_color
    )
    
    # Center dot
    painter.setBrush(QBrush(main_color))
    painter.drawEllipse(QPointF(center, center), max(2, size / 16), max(2, size / 16))
    
    painter.end()
    return image


def generate_all_icons(output_dir=None):
    """
    Generate all icon sizes needed for the application.
    
    Creates:
    - Application icons: 16, 32, 48, 64, 128, 256, 512px
    - System tray icons: 16, 32, 48px (color and monochrome)
    
    Args:
        output_dir: Directory to save icon files (defaults to current directory)
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / 'icons'
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating Charm-inspired Alarmify icons...")
    
    # Main application icons
    for size in [16, 32, 48, 64, 128, 256, 512]:
        print(f"  Creating app icon: {size}x{size}px")
        img = generate_icon_image(size)
        img.save(str(output_dir / f'alarmify_icon_{size}.png'), 'PNG', 100)
    
    # System tray icons (color)
    for size in [16, 32, 48]:
        print(f"  Creating tray icon (color): {size}x{size}px")
        img = generate_tray_icon(size, monochrome=False)
        img.save(str(output_dir / f'tray_icon_{size}.png'), 'PNG', 100)
    
    # System tray icons (monochrome for dark mode compatibility)
    for size in [16, 32, 48]:
        print(f"  Creating tray icon (mono): {size}x{size}px")
        img_mono = generate_tray_icon(size, monochrome=True)
        img_mono.save(str(output_dir / f'tray_icon_{size}_mono.png'), 'PNG', 100)
    
    print(f"\n✓ All icons generated successfully in: {output_dir}")
    print(f"  Total files: {len(list(output_dir.glob('*.png')))}")


if __name__ == '__main__':
    generate_all_icons()
