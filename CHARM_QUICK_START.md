# Charm Design Quick Start Guide

Quick reference for using the new Charm-inspired design system in Alarmify.

## Running the Application

The Charm design is automatically applied when you start Alarmify:

```bash
python main.py
```

## Generating Icons

Icons are generated automatically on first use. To pre-generate all icons:

```bash
python icon_generator.py
```

This creates:
- `alarmify_icon_16.png` through `alarmify_icon_512.png`
- `tray_icon_16.png`, `tray_icon_32.png`, `tray_icon_48.png`
- `tray_icon_16_mono.png`, `tray_icon_32_mono.png`, `tray_icon_48_mono.png`

## Using Stylesheets in New Components

```python
from charm_stylesheet import get_stylesheet

# In your widget's __init__ or setup method:
stylesheet = get_stylesheet('dark')  # or 'light'
self.setStyleSheet(stylesheet)
```

## Adding Animations to Widgets

### Fade In Animation
```python
from charm_animations import AnimationBuilder

animation = AnimationBuilder.create_fade_in(my_widget, duration=300)
animation.start()
```

### Slide Up Animation
```python
animation = AnimationBuilder.create_slide_up(my_widget, distance=20, duration=300)
animation.start()
```

### Hover Effect
```python
from charm_animations import HoverAnimation

hover_anim = HoverAnimation(my_button)
hover_anim.setup_hover_lift(lift_height=2)

# In your button's enterEvent:
def enterEvent(self, event):
    self.hover_anim.on_hover_enter()
    super().enterEvent(event)

# In your button's leaveEvent:
def leaveEvent(self, event):
    self.hover_anim.on_hover_leave()
    super().leaveEvent(event)
```

### Staggered Entrance (Multiple Widgets)
```python
from charm_animations import apply_entrance_animations

widgets = [widget1, widget2, widget3, widget4]
apply_entrance_animations(widgets, stagger_delay=50)
```

## Creating Custom Icons

```python
from icon_generator import generate_icon_image, generate_tray_icon
from PyQt5.QtGui import QPixmap, QIcon

# Application icon
icon_image = generate_icon_image(size=256)
pixmap = QPixmap.fromImage(icon_image)
app_icon = QIcon(pixmap)
window.setWindowIcon(app_icon)

# System tray icon
tray_image = generate_tray_icon(size=32, monochrome=False)
tray_pixmap = QPixmap.fromImage(tray_image)
tray_icon.setIcon(QIcon(tray_pixmap))
```

## Design System Reference

### Colors
```python
PRIMARY = "#1DB954"      # Spotify Green
HOVER = "#1ED760"        # Bright Green  
PRESSED = "#1AA34A"      # Dark Green
BACKGROUND = "#0a0a0a"   # Near Black
SURFACE = "#1a1a1a"      # Dark Gray
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#b3b3b3"
```

### Typography
```python
from PyQt5.QtGui import QFont

# UI Text
font = QFont('Inter', 14)

# Headers
header_font = QFont('Inter', 18, QFont.Bold)

# Time Display
time_font = QFont('JetBrains Mono', 32, QFont.Bold)

# Code/Logs
code_font = QFont('JetBrains Mono', 11)
```

### Spacing
```python
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 24,
    '2xl': 32
}
```

### Border Radius
```python
RADIUS = {
    'small': 6,    # inputs, tags
    'medium': 8,   # buttons, cards
    'large': 12,   # large cards
    'xlarge': 20,  # primary buttons
    'round': 500   # pill buttons
}
```

## Common Glassmorphism Patterns

### Glass Card
```css
background: rgba(26, 26, 26, 0.7);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 12px;
```

### Glass Input
```css
background: rgba(42, 42, 42, 0.7);
border: 2px solid rgba(255, 255, 255, 0.2);
border-radius: 8px;
padding: 12px 16px;
```

### Glass Button (Hover)
```css
background: rgba(42, 42, 42, 0.9);
border: 2px solid rgba(255, 255, 255, 0.3);
```

## Animation Timing Reference

```python
DURATIONS = {
    'fast': 150,    # hover, small transitions
    'medium': 300,  # standard transitions
    'slow': 500     # page transitions
}

# Easing
# Use QEasingCurve.OutExpo for spring-like deceleration
# Use QEasingCurve.OutBack for slight overshoot
```

## Widget Styling Examples

### Primary Button
```python
button = QPushButton("Click Me")
button.setStyleSheet("""
    QPushButton {
        background-color: #1DB954;
        color: #000000;
        border: none;
        border-radius: 500px;
        padding: 12px 32px;
        font-weight: 700;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #1ED760;
    }
""")
```

### Glass Input Field
```python
line_edit = QLineEdit()
line_edit.setStyleSheet("""
    QLineEdit {
        background: rgba(42, 42, 42, 0.7);
        color: #ffffff;
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 12px 16px;
    }
    QLineEdit:focus {
        border: 2px solid #1DB954;
        background: rgba(51, 51, 51, 0.8);
    }
""")
```

### Section Header
```python
header = QLabel("Section Title")
header.setObjectName('sectionHeader')
header.setFont(QFont('Inter', 18, QFont.Bold))
# Styling applied automatically via stylesheet
```

## Tips

1. **Always use objectName** for components you want to style specifically
2. **Prefer stylesheet over inline styles** for consistency
3. **Use animations sparingly** - not every interaction needs animation
4. **Test both themes** (dark and light) when adding new components
5. **Follow spacing system** - use predefined spacing values (8px base)
6. **Check contrast** - ensure text is readable on glassmorphic backgrounds

## Troubleshooting

### Fonts not appearing?
The app falls back to system fonts automatically. Inter and JetBrains Mono are loaded if available, otherwise it uses Segoe UI or system defaults.

### Animations not smooth?
Ensure you're using QPropertyAnimation with appropriate easing curves (OutExpo recommended).

### Icons not showing?
Icons are generated at runtime. Check console for any error messages from icon_generator.py.

### Glassmorphism looks wrong?
PyQt5 doesn't support true backdrop-filter. We use RGBA transparency which works well but requires proper layering.

## Resources

- **Full Design System**: See `DESIGN_SYSTEM.md`
- **Icon Specifications**: See `ICON_DESIGN.md`
- **Implementation Details**: See `CHARM_DESIGN_IMPLEMENTATION.md`
- **Change Summary**: See `IMPLEMENTATION_SUMMARY.md`

## Support

For questions or issues with the Charm design system, refer to the documentation files or check the implementation in:
- `charm_stylesheet.py` - Stylesheet definitions
- `charm_animations.py` - Animation system
- `icon_generator.py` - Icon generation
- `gui.py` - Usage examples
