# Charm-Inspired UI Implementation

This document describes the Charm-inspired UI redesign for Alarmify.

## Overview

Alarmify has been redesigned with a modern, Charm-inspired aesthetic featuring:
- **Glassmorphism effects** with backdrop blur and transparency
- **Inter font** for UI elements (labels, buttons, text)
- **JetBrains Mono** for monospace displays (time, logs)
- **Spring-based animations** for natural, fluid motion
- **Custom icon system** with SVG generation
- **Enhanced visual hierarchy** with improved spacing and shadows

## Key Components

### 1. Icon System (`icon_generator.py`)
- Generates custom Alarmify icons programmatically using PyQt5's SVG renderer
- Creates icons in multiple sizes (16, 32, 48, 64, 128, 256, 512)
- Generates system tray icons in normal and monochrome variants
- Features:
  - Gradient background (#1ED760 to #1DB954)
  - Clock face with hour markers
  - Music note integrated with minute hand
  - Glassmorphism highlight overlay
  - Animated sparkle effects in SVG

### 2. Stylesheet System (`charm_stylesheet.py`)
- Comprehensive stylesheet following DESIGN_SYSTEM.md specifications
- Glassmorphism effects using `rgba()` with transparency
- Consistent spacing (4px, 8px, 12px, 16px, 24px, 32px)
- Border radius system (6px, 8px, 12px, 20px, 500px for pills)
- Dark and light theme variants
- Components styled:
  - Buttons (primary, secondary, icon buttons)
  - Input fields (text, time, combo boxes)
  - Lists and tables
  - Sliders with gradient fill
  - Checkboxes and radio buttons
  - Scrollbars with rounded handles

### 3. Animation System (`charm_animations.py`)
- Spring-based physics for natural motion
- Animation types:
  - **Fade In**: Opacity 0 → 1 with OutExpo easing
  - **Slide Up**: Vertical translation with spring deceleration
  - **Scale In**: Scale with overshoot effect
  - **Hover Lift**: Subtle 2px elevation on hover
- `AnimationBuilder` class for creating animations
- `SpringPhysics` class for calculating natural durations
- `HoverAnimation` helper for widget hover effects
- Staggered entrance animations for lists

### 4. Enhanced UI Components

#### Main Window (`gui.py`)
- **Header**: Logo with custom icon, authentication status badges
- **Playlist List**: 
  - Glassmorphic cards with 8px spacing
  - Hover effects with gradient backgrounds
  - Smooth animations on hover
  - Search bar with icon and glassmorphic styling
- **Time Input**: 
  - Large JetBrains Mono font (32px bold)
  - Centered alignment
  - Glassmorphic background with 80px height
- **Volume Slider**:
  - Gradient fill (#1DB954 to #1ED760)
  - Enlarged handle on hover (18px → 20px)
  - Smooth rounded design
- **Buttons**:
  - Pill-shaped primary buttons (500px border radius)
  - Hover animations with color transitions
  - Icon buttons with circular shape

#### Setup Wizard (`gui_setup_wizard.py`)
- Charm design system applied to all wizard pages
- Custom icon in window title bar
- Consistent glassmorphism throughout
- Smooth page transitions

## Design System Reference

### Color Palette
- **Primary**: #1DB954 (Spotify Green)
- **Hover**: #1ED760 (Bright Green)
- **Pressed**: #1AA34A (Dark Green)
- **Background**: #0a0a0a (Near Black)
- **Surface**: #1a1a1a (Dark Gray)
- **Glass**: rgba(26, 26, 26, 0.7) with backdrop-filter

### Typography
- **Display**: Inter 32px Bold
- **Headers**: Inter 18px Bold
- **Body**: Inter 14px Regular
- **Time**: JetBrains Mono 32px Bold
- **Code**: JetBrains Mono 11px Regular

### Spacing Scale
- xs: 4px
- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px
- 2xl: 32px

### Animation Timings
- Fast: 150ms (hover effects)
- Medium: 300ms (transitions)
- Slow: 500ms (page changes)
- Easing: OutExpo (cubic-bezier(0.16, 1, 0.3, 1))

## Usage

### Applying Themes
```python
from charm_stylesheet import get_stylesheet

# Apply dark theme (default)
stylesheet = get_stylesheet('dark')
widget.setStyleSheet(stylesheet)

# Apply light theme
stylesheet = get_stylesheet('light')
widget.setStyleSheet(stylesheet)
```

### Creating Animations
```python
from charm_animations import AnimationBuilder

# Fade in animation
animation = AnimationBuilder.create_fade_in(widget, duration=300)
animation.start()

# Slide up animation
animation = AnimationBuilder.create_slide_up(widget, distance=20, duration=300)
animation.start()

# Staggered entrance for multiple widgets
from charm_animations import apply_entrance_animations
apply_entrance_animations([widget1, widget2, widget3], stagger_delay=50)
```

### Generating Icons
```python
from icon_generator import generate_icon_image, generate_tray_icon

# Generate application icon
icon_image = generate_icon_image(size=256)
pixmap = QPixmap.fromImage(icon_image)

# Generate tray icon
tray_image = generate_tray_icon(size=32, monochrome=False)
```

## File Structure

```
alarmify/
├── charm_stylesheet.py          # Stylesheet definitions
├── charm_animations.py          # Animation system
├── icon_generator.py            # Icon generation
├── DESIGN_SYSTEM.md            # Design specifications
├── ICON_DESIGN.md              # Icon design specs
├── gui.py                       # Main UI (updated)
├── gui_setup_wizard.py         # Setup wizard (updated)
└── main.py                      # Entry point (updated)
```

## Browser Compatibility Notes

While PyQt5 doesn't support CSS backdrop-filter directly, we achieve similar effects using:
- RGBA colors with alpha transparency
- Layered QLabel widgets for highlights
- QGraphicsEffect for blur-like appearances
- Gradient overlays for depth

## Performance Considerations

- Animations use Qt's native QPropertyAnimation for hardware acceleration
- Icons are cached after first generation
- Stylesheets are loaded once at startup
- Glassmorphism effects use efficient RGBA instead of actual blur filters

## Future Enhancements

Potential improvements for future versions:
- Custom QStyle subclass for true backdrop blur
- GPU-accelerated effects with QOpenGLWidget
- Micro-interactions (button press ripples, checkbox animations)
- Loading skeletons with shimmer effects
- Toast notifications with slide-in animations
- Dark mode auto-detection from system
- Custom scrollbar animations
