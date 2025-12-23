# Alarmify Design System - Charm-Inspired

## 🎨 Design Philosophy

Inspired by [Charm](https://charm.land/) - making the command line glamorous. We bring that same elegance to desktop applications.

### Core Principles
1. **Terminal Elegance** - Clean, monospace-inspired, but modern
2. **Glassmorphism** - Frosted glass effects, depth through blur
3. **Smooth Physics** - Spring-based animations, fluid motion
4. **Minimal Palette** - Dark base with vibrant, purposeful accents
5. **Typography First** - Clear hierarchy, readable, beautiful fonts

---

## 🎨 Color Palette

### Base Colors
```css
/* Backgrounds */
--bg-primary: #0a0a0a;      /* Deep black - main background */
--bg-secondary: #1a1a1a;   /* Slightly lighter - cards */
--bg-tertiary: #252525;    /* Elevated surfaces */
--bg-hover: #2a2a2a;       /* Hover states */
--bg-active: #333333;      /* Active/pressed states */

/* Text */
--text-primary: #ffffff;    /* Main text */
--text-secondary: #b3b3b3;  /* Secondary text */
--text-tertiary: #727272;   /* Tertiary/disabled text */

/* Accents */
--accent-primary: #1DB954;  /* Spotify green - primary actions */
--accent-hover: #1ed760;    /* Lighter green on hover */
--accent-secondary: #FF6B6B; /* Alert/important actions */
--accent-warning: #FFA500;  /* Warnings */
--accent-info: #4A9EFF;     /* Information */

/* Glass Effect */
--glass-bg: rgba(26, 26, 26, 0.8);
--glass-border: rgba(255, 255, 255, 0.1);
--glass-shadow: rgba(0, 0, 0, 0.3);
```

### Usage Guidelines
- **Primary Background:** Main window, panels
- **Secondary Background:** Cards, elevated elements
- **Accent Primary:** Buttons, links, active states
- **Text Hierarchy:** Use primary for headings, secondary for body, tertiary for hints

---

## 📝 Typography

### Font Stack
```css
/* Headings */
font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif;
font-weight: 700; /* Bold */

/* Body */
font-family: 'Inter', 'SF Pro Text', -apple-system, sans-serif;
font-weight: 400; /* Regular */

/* Monospace (for times, code) */
font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
font-weight: 400;
```

### Type Scale
```
H1: 32px / 2rem (Logo, main headings)
H2: 24px / 1.5rem (Section headers)
H3: 18px / 1.125rem (Subsections)
H4: 16px / 1rem (Labels)
Body: 14px / 0.875rem (Default text)
Small: 12px / 0.75rem (Hints, captions)
Tiny: 11px / 0.6875rem (Metadata)
```

### Line Heights
- Headings: 1.2
- Body: 1.5
- Tight: 1.3 (for compact layouts)

---

## 🧩 Components

### Buttons

#### Primary Button
```css
background: #1DB954;
color: #000000;
border-radius: 500px; /* Pill shape */
padding: 12px 32px;
font-weight: 700;
font-size: 14px;
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
```

**Hover:**
```css
background: #1ed760;
transform: scale(1.02);
```

**Pressed:**
```css
background: #1aa34a;
transform: scale(0.98);
```

#### Secondary Button
```css
background: transparent;
color: #b3b3b3;
border: 1px solid #2a2a2a;
border-radius: 500px;
```

**Hover:**
```css
background: #2a2a2a;
color: #ffffff;
border-color: #3a3a3a;
```

### Cards

```css
background: var(--glass-bg);
backdrop-filter: blur(20px);
border: 1px solid var(--glass-border);
border-radius: 12px;
box-shadow: 0 8px 32px var(--glass-shadow);
padding: 20px;
```

**Hover:**
```css
background: rgba(42, 42, 42, 0.9);
border-color: rgba(255, 255, 255, 0.15);
transform: translateY(-2px);
box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
```

### Input Fields

```css
background: #181818;
color: #ffffff;
border: 1px solid #2a2a2a;
border-radius: 6px;
padding: 10px 14px;
font-size: 14px;
transition: all 0.2s;
```

**Focus:**
```css
border: 2px solid #1DB954;
background: #1f1f1f;
outline: none;
box-shadow: 0 0 0 3px rgba(29, 185, 84, 0.1);
```

**Placeholder:**
```css
color: #727272;
```

### Playlist Items

```css
background: transparent;
border-radius: 8px;
padding: 12px;
margin: 4px 0;
transition: all 0.2s;
```

**Hover:**
```css
background: #2a2a2a;
transform: translateX(4px);
```

**Selected:**
```css
background: rgba(29, 185, 84, 0.15);
border-left: 3px solid #1DB954;
```

---

## ✨ Animations

### Principles
- **Spring Physics:** Natural, bouncy motion
- **Duration:** 200-300ms for interactions
- **Easing:** `cubic-bezier(0.4, 0, 0.2, 1)` (Material Design)

### Common Animations

#### Fade In
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

#### Slide In
```css
@keyframes slideIn {
  from {
    transform: translateX(-20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
```

#### Scale
```css
@keyframes scaleIn {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
```

#### Pulse (for loading)
```css
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
```

---

## 🎭 Glassmorphism Effects

### Light Glass
```css
background: rgba(26, 26, 26, 0.6);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.1);
```

### Medium Glass
```css
background: rgba(26, 26, 26, 0.8);
backdrop-filter: blur(20px);
border: 1px solid rgba(255, 255, 255, 0.15);
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
```

### Heavy Glass
```css
background: rgba(26, 26, 26, 0.9);
backdrop-filter: blur(30px);
border: 1px solid rgba(255, 255, 255, 0.2);
box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
```

---

## 📐 Spacing System

### Base Unit: 4px

```
xs: 4px   (0.25rem)
sm: 8px   (0.5rem)
md: 12px  (0.75rem)
lg: 16px  (1rem)
xl: 24px  (1.5rem)
2xl: 32px (2rem)
3xl: 48px (3rem)
```

### Usage
- **Cards:** `padding: lg` (16px)
- **Buttons:** `padding: md lg` (12px 16px)
- **Sections:** `margin-bottom: xl` (24px)
- **Elements:** `gap: md` (12px)

---

## 🎯 Icon Design Guidelines

### Style
- **Minimal:** Clean, simple shapes
- **Rounded:** Soft corners (2-4px radius)
- **Bold:** Strong, recognizable at small sizes
- **Consistent:** Same stroke width (2px)

### Sizes
- **16px:** System tray, small UI elements
- **24px:** Standard icons
- **32px:** Large icons, buttons
- **48px:** Feature icons
- **64px+:** App icon sizes

### Color
- **Default:** `#b3b3b3` (text-secondary)
- **Hover:** `#ffffff` (text-primary)
- **Active:** `#1DB954` (accent-primary)

---

## 🖼️ Layout Patterns

### Card Grid
```css
display: grid;
grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
gap: 16px;
```

### Sidebar Layout
```css
display: flex;
gap: 24px;
```

**Sidebar:**
```css
width: 280px;
flex-shrink: 0;
```

**Main:**
```css
flex: 1;
min-width: 0;
```

### Centered Content
```css
max-width: 1200px;
margin: 0 auto;
padding: 0 24px;
```

---

## 🎨 App Icon Design Brief

### Concept: "Musical Sunrise"

**Elements:**
- Circular alarm clock face (outer ring)
- Musical note/waveform (center)
- Sunrise rays (radiating from center)
- Modern, minimal style

### Design Variations

#### Option 1: Minimal
- Dark circle (#0a0a0a)
- Green musical note (#1DB954)
- Subtle rays

#### Option 2: Gradient
- Dark to green gradient background
- White/light musical note
- Prominent rays

#### Option 3: Glassmorphism
- Frosted glass effect
- Green accent
- Subtle depth

### Technical Specs
- **Format:** SVG (vector) + PNG (raster)
- **Sizes:** 16, 32, 64, 128, 256, 512, 1024px
- **Background:** Transparent or dark
- **Style:** Flat with subtle depth

### Color Options
1. **Primary:** Dark + Spotify green
2. **Alternative:** Gradient (dark → green)
3. **Monochrome:** For system integration

---

## 📱 Responsive Breakpoints

```
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: > 1024px
Large: > 1440px
```

---

## ♿ Accessibility

### Contrast Ratios
- **Text on background:** Minimum 4.5:1
- **Large text:** Minimum 3:1
- **Interactive elements:** Minimum 3:1

### Focus States
- **Visible outline:** 2px solid #1DB954
- **Offset:** 2px from element
- **High contrast:** Always visible

### Keyboard Navigation
- **Tab order:** Logical flow
- **Skip links:** For main content
- **Shortcuts:** Documented

---

## 🚀 Implementation Notes

### QSS (Qt Stylesheet)
- Use CSS-like syntax
- Support for custom properties (Qt 5.12+)
- Animation support limited (use QPropertyAnimation)

### Performance
- **Backdrop blur:** Expensive, use sparingly
- **Animations:** GPU-accelerated transforms
- **Images:** Optimize, use caching

### Browser Compatibility
- **Backdrop-filter:** Modern browsers only
- **Fallback:** Solid background if unsupported

---

## 📚 Resources

- [Charm Design System](https://charm.land/)
- [Material Design](https://material.io/design)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/)
- [Glassmorphism Guide](https://uxdesign.cc/glassmorphism-in-user-interfaces-1f39d130b9ce)

---

**Last Updated:** December 23, 2024
**Version:** 1.0

