# Alarmify Design System - Charm-Inspired

## Color Palette

### Primary Colors
- **Spotify Green**: #1DB954 (primary accent)
- **Bright Green**: #1ED760 (hover states)
- **Dark Green**: #1AA34A (pressed states)

### Backgrounds (Dark Theme)
- **Primary Background**: #0a0a0a (near black)
- **Secondary Background**: #1a1a1a (cards, inputs)
- **Tertiary Background**: #2a2a2a (hover states)
- **Glass Background**: rgba(26, 26, 26, 0.7) with backdrop-filter: blur(10px)

### Backgrounds (Light Theme)
- **Primary Background**: #f5f5f5
- **Secondary Background**: #ffffff
- **Tertiary Background**: #e8e8e8
- **Glass Background**: rgba(255, 255, 255, 0.7) with backdrop-filter: blur(10px)

### Text Colors
- **Primary Text**: #ffffff (dark theme), #1a1a1a (light theme)
- **Secondary Text**: #b3b3b3 (dark), #666666 (light)
- **Accent Text**: #1DB954

## Typography

### Font Families
- **Primary**: Inter (UI text, labels, buttons)
- **Monospace**: JetBrains Mono (time display, logs, technical data)
- **Fallbacks**: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui

### Font Sizes
- **Display**: 32px, Bold (app title)
- **H1**: 24px, Bold (section headers)
- **H2**: 18px, Bold (subsection headers)
- **Body**: 14px, Regular (general text)
- **Small**: 12px, Regular (captions, metadata)
- **Time Display**: 28px, Bold, JetBrains Mono

### Font Weights
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

## Glassmorphism Effects

### Card Glass Effect
```css
background: rgba(26, 26, 26, 0.7);
backdrop-filter: blur(10px) saturate(150%);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 12px;
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
```

### Input Glass Effect
```css
background: rgba(42, 42, 42, 0.7);
backdrop-filter: blur(8px);
border: 2px solid rgba(255, 255, 255, 0.2);
border-radius: 8px;
```

### Hover Glass Effect
```css
background: rgba(42, 42, 42, 0.9);
border: 2px solid rgba(255, 255, 255, 0.3);
transform: translateY(-2px);
box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
```

## Spacing System
- **xs**: 4px
- **sm**: 8px
- **md**: 12px
- **lg**: 16px
- **xl**: 24px
- **2xl**: 32px
- **3xl**: 48px

## Border Radius
- **Small**: 6px (inputs, tags)
- **Medium**: 8px (buttons, cards)
- **Large**: 12px (large cards, panels)
- **XLarge**: 20px (primary buttons)
- **Round**: 500px (pill buttons)

## Animation System

### Spring-Based Animations
All animations use spring physics for natural motion:
- **Tension**: 200 (medium spring stiffness)
- **Friction**: 20 (medium damping)
- **Mass**: 1 (standard weight)

### Animation Durations
- **Fast**: 150ms (button hover, small transitions)
- **Medium**: 300ms (card transitions, dropdowns)
- **Slow**: 500ms (page transitions, large movements)

### Easing Functions
- **Ease-out-expo**: cubic-bezier(0.16, 1, 0.3, 1) - spring-like deceleration
- **Ease-out-back**: cubic-bezier(0.34, 1.56, 0.64, 1) - slight overshoot
- **Ease-in-out-circ**: cubic-bezier(0.785, 0.135, 0.15, 0.86) - smooth circular

### Common Animations
1. **Fade In**: opacity 0 -> 1, 300ms ease-out-expo
2. **Slide Up**: translateY(20px) -> 0, 300ms ease-out-expo
3. **Scale In**: scale(0.95) -> 1, 300ms ease-out-back
4. **Hover Lift**: translateY(0) -> translateY(-2px), 150ms ease-out-expo

## Button Styles

### Primary Button
```css
background: #1DB954;
color: #000000;
font-weight: 700;
font-size: 14px;
padding: 12px 32px;
border-radius: 500px;
border: none;
transition: all 150ms cubic-bezier(0.16, 1, 0.3, 1);

:hover {
  background: #1ED760;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(29, 185, 84, 0.4);
}

:active {
  background: #1AA34A;
  transform: translateY(0);
}
```

### Secondary Button
```css
background: rgba(42, 42, 42, 0.7);
border: 2px solid rgba(255, 255, 255, 0.2);
color: #ffffff;
```

### Icon Button
```css
width: 40px;
height: 40px;
border-radius: 50%;
background: rgba(42, 42, 42, 0.7);
```

## Visual Hierarchy

### Z-Index Layers
- **Base**: 0 (background, content)
- **Elevated**: 10 (cards, panels)
- **Dropdown**: 100 (dropdowns, tooltips)
- **Modal**: 1000 (dialogs, overlays)
- **Toast**: 2000 (notifications)

### Shadow Hierarchy
- **Level 1**: 0 2px 4px rgba(0, 0, 0, 0.1)
- **Level 2**: 0 4px 8px rgba(0, 0, 0, 0.2)
- **Level 3**: 0 8px 16px rgba(0, 0, 0, 0.3)
- **Level 4**: 0 16px 32px rgba(0, 0, 0, 0.4)

## Responsive Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px
