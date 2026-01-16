"""
charm_animations.py - Advanced spring-based animation system

Provides smooth, physics-based animations with proper spring dynamics.
Features:
- Spring physics with configurable tension, friction, and mass
- Fade-in, slide-up, scale, and hover animations
- Staggered entrance animations for lists
- Easing curves optimized for natural motion
- Support for parallel and sequential animations
"""

from PyQt5.QtCore import (
    QPropertyAnimation, QEasingCurve, QAbstractAnimation, 
    QParallelAnimationGroup, QSequentialAnimationGroup, QTimer, QPoint
)
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QWidget
import math


class SpringPhysics:
    """
    Spring physics calculator for natural motion.
    
    Based on spring-damper system physics:
    - Tension (stiffness): 200 (spring strength)
    - Friction (damping): 20 (resistance to motion)
    - Mass: 1.0 (weight of object)
    
    The spring equation: F = -k*x - c*v
    where k is tension, c is friction, x is displacement, v is velocity
    """
    
    def __init__(self, tension=200, friction=20, mass=1.0):
        """
        Initialize spring physics parameters.
        
        Args:
            tension: Spring stiffness (higher = stiffer, faster)
            friction: Damping coefficient (higher = more damped)
            mass: Object mass (affects inertia)
        """
        self.tension = tension
        self.friction = friction
        self.mass = mass
    
    def calculate_duration(self, distance):
        """
        Calculate optimal animation duration based on distance and spring physics.
        
        Uses damped harmonic oscillator formula to estimate settling time.
        
        Args:
            distance: Distance to travel in pixels
            
        Returns:
            int: Duration in milliseconds
        """
        # Natural frequency: ω = sqrt(k/m)
        omega = math.sqrt(self.tension / self.mass)
        
        # Damping ratio: ζ = c / (2*sqrt(k*m))
        damping_ratio = self.friction / (2 * math.sqrt(self.tension * self.mass))
        
        # Settling time for critically damped or overdamped: t ≈ 4/ζω
        if damping_ratio >= 1:
            settling_time = 4.0 / (damping_ratio * omega)
        else:
            # Underdamped: t ≈ 4/(ζω)
            settling_time = 4.0 / (damping_ratio * omega)
        
        # Scale by distance and convert to milliseconds
        base_duration = settling_time * 1000
        distance_factor = min(abs(distance) / 100, 2.0)
        
        return int(base_duration * distance_factor)
    
    def get_easing_curve(self):
        """
        Get the appropriate easing curve for spring-like motion.
        
        OutExpo provides a close approximation to spring deceleration.
        
        Returns:
            QEasingCurve: Easing curve for spring motion
        """
        return QEasingCurve.OutExpo


class AnimationBuilder:
    """Builder for creating spring-based animations with proper physics."""
    
    # Default spring physics
    _spring = SpringPhysics(tension=200, friction=20, mass=1.0)
    
    @staticmethod
    def create_fade_in(widget, duration=300, start_opacity=0.0, end_opacity=1.0):
        """
        Create a smooth fade-in animation.
        
        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            start_opacity: Starting opacity (0.0 to 1.0)
            end_opacity: Ending opacity (0.0 to 1.0)
            
        Returns:
            QPropertyAnimation: Configured fade animation
        """
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setEasingCurve(QEasingCurve.OutExpo)
        
        return animation
    
    @staticmethod
    def create_slide_up(widget, distance=20, duration=300):
        """
        Create a slide-up animation with spring physics.
        
        Args:
            widget: Widget to animate
            distance: Distance to slide in pixels (positive = down to up)
            duration: Animation duration in milliseconds
            
        Returns:
            QPropertyAnimation: Configured slide animation
        """
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        
        # Store original position
        original_pos = widget.pos()
        start_pos = QPoint(original_pos.x(), original_pos.y() + distance)
        
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        animation.setEasingCurve(QEasingCurve.OutExpo)
        
        return animation
    
    @staticmethod
    def create_slide_in_from_left(widget, distance=50, duration=350):
        """
        Create a slide-in animation from the left.
        
        Args:
            widget: Widget to animate
            distance: Distance to slide in pixels
            duration: Animation duration in milliseconds
            
        Returns:
            QPropertyAnimation: Configured slide animation
        """
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        
        original_pos = widget.pos()
        start_pos = QPoint(original_pos.x() - distance, original_pos.y())
        
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        animation.setEasingCurve(QEasingCurve.OutExpo)
        
        return animation
    
    @staticmethod
    def create_slide_in_from_right(widget, distance=50, duration=350):
        """
        Create a slide-in animation from the right.
        
        Args:
            widget: Widget to animate
            distance: Distance to slide in pixels
            duration: Animation duration in milliseconds
            
        Returns:
            QPropertyAnimation: Configured slide animation
        """
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        
        original_pos = widget.pos()
        start_pos = QPoint(original_pos.x() + distance, original_pos.y())
        
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        animation.setEasingCurve(QEasingCurve.OutExpo)
        
        return animation
    
    @staticmethod
    def create_combined_fade_slide(widget, slide_distance=20, duration=350):
        """
        Create a combined fade-in and slide-up animation.
        
        Args:
            widget: Widget to animate
            slide_distance: Distance to slide in pixels
            duration: Animation duration in milliseconds
            
        Returns:
            QParallelAnimationGroup: Combined animation
        """
        group = QParallelAnimationGroup()
        
        fade = AnimationBuilder.create_fade_in(widget, duration)
        slide = AnimationBuilder.create_slide_up(widget, slide_distance, duration)
        
        group.addAnimation(fade)
        group.addAnimation(slide)
        
        return group
    
    @staticmethod
    def create_hover_lift(widget, lift_height=2, duration=150):
        """
        Create a subtle hover lift animation.
        
        Args:
            widget: Widget to animate
            lift_height: Height to lift in pixels
            duration: Animation duration in milliseconds
            
        Returns:
            QPropertyAnimation: Configured lift animation
        """
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        
        start_pos = widget.pos()
        end_pos = QPoint(start_pos.x(), start_pos.y() - lift_height)
        
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutExpo)
        
        return animation
    
    @staticmethod
    def create_spring_bounce(widget, duration=600):
        """
        Create a spring bounce animation for attention.
        
        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            
        Returns:
            QSequentialAnimationGroup: Bounce animation sequence
        """
        group = QSequentialAnimationGroup()
        
        # Bounce up
        up_animation = QPropertyAnimation(widget, b"pos")
        up_animation.setDuration(duration // 3)
        start_pos = widget.pos()
        up_pos = QPoint(start_pos.x(), start_pos.y() - 8)
        up_animation.setStartValue(start_pos)
        up_animation.setEndValue(up_pos)
        up_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # Bounce down
        down_animation = QPropertyAnimation(widget, b"pos")
        down_animation.setDuration(duration // 3)
        down_animation.setStartValue(up_pos)
        down_animation.setEndValue(start_pos)
        down_animation.setEasingCurve(QEasingCurve.OutBounce)
        
        group.addAnimation(up_animation)
        group.addAnimation(down_animation)
        
        return group
    
    @staticmethod
    def animate_widget_entrance(widget, animation_type='fade', duration=300, delay=0):
        """
        Animate a widget entrance with specified animation type.
        
        Args:
            widget: Widget to animate
            animation_type: 'fade', 'slide', 'slide_left', 'slide_right', or 'fade_slide'
            duration: Animation duration in milliseconds
            delay: Delay before animation starts in milliseconds
        
        Returns:
            QPropertyAnimation or QParallelAnimationGroup: The animation object
        """
        if animation_type == 'fade':
            animation = AnimationBuilder.create_fade_in(widget, duration)
        elif animation_type == 'slide':
            animation = AnimationBuilder.create_slide_up(widget, 20, duration)
        elif animation_type == 'slide_left':
            animation = AnimationBuilder.create_slide_in_from_left(widget, 50, duration)
        elif animation_type == 'slide_right':
            animation = AnimationBuilder.create_slide_in_from_right(widget, 50, duration)
        elif animation_type == 'fade_slide':
            animation = AnimationBuilder.create_combined_fade_slide(widget, 20, duration)
        else:
            animation = AnimationBuilder.create_fade_in(widget, duration)
        
        if delay > 0:
            # Use QTimer for delay
            QTimer.singleShot(delay, lambda: animation.start(QAbstractAnimation.DeleteWhenStopped))
            return animation
        else:
            animation.start(QAbstractAnimation.DeleteWhenStopped)
            return animation


class HoverAnimation:
    """
    Manages hover animations for widgets with spring physics.
    """
    
    def __init__(self, widget, lift_height=2):
        """
        Initialize hover animation manager.
        
        Args:
            widget: Widget to apply hover animation to
            lift_height: Height to lift on hover in pixels
        """
        self.widget = widget
        self.lift_height = lift_height
        self.hover_animation = None
        self.unhover_animation = None
        self.original_pos = None
    
    def setup(self):
        """Setup hover lift animation for the widget."""
        self.widget.setMouseTracking(True)
        
        # Store original position
        self.original_pos = self.widget.pos()
        
        # Create hover animation
        self.hover_animation = QPropertyAnimation(self.widget, b"pos")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.OutExpo)
        
        # Create unhover animation
        self.unhover_animation = QPropertyAnimation(self.widget, b"pos")
        self.unhover_animation.setDuration(150)
        self.unhover_animation.setEasingCurve(QEasingCurve.OutExpo)
    
    def on_hover_enter(self):
        """Trigger hover animation (lift up)."""
        if self.hover_animation and self.original_pos:
            current_pos = self.widget.pos()
            lifted_pos = QPoint(current_pos.x(), current_pos.y() - self.lift_height)
            
            self.hover_animation.setStartValue(current_pos)
            self.hover_animation.setEndValue(lifted_pos)
            self.hover_animation.start()
    
    def on_hover_leave(self):
        """Trigger unhover animation (return to original)."""
        if self.unhover_animation and self.original_pos:
            self.unhover_animation.setStartValue(self.widget.pos())
            self.unhover_animation.setEndValue(self.original_pos)
            self.unhover_animation.start()


def apply_entrance_animations(widgets, animation_type='fade_slide', stagger_delay=50, start_delay=0):
    """
    Apply staggered entrance animations to a list of widgets.
    
    Creates a cascading effect where each widget animates in sequence.
    
    Args:
        widgets: List of widgets to animate
        animation_type: Type of animation ('fade', 'slide', 'fade_slide', etc.)
        stagger_delay: Delay between each widget animation in milliseconds
        start_delay: Initial delay before first animation in milliseconds
    """
    for i, widget in enumerate(widgets):
        total_delay = start_delay + (i * stagger_delay)
        AnimationBuilder.animate_widget_entrance(
            widget,
            animation_type=animation_type,
            duration=350,
            delay=total_delay
        )


def apply_parallel_entrance(widgets, animation_type='fade_slide', duration=350):
    """
    Apply entrance animations to widgets simultaneously.
    
    Args:
        widgets: List of widgets to animate
        animation_type: Type of animation
        duration: Animation duration in milliseconds
    """
    for widget in widgets:
        AnimationBuilder.animate_widget_entrance(
            widget,
            animation_type=animation_type,
            duration=duration,
            delay=0
        )


def create_button_press_animation(button):
    """
    Create a press animation for a button.
    
    Simulates a physical button press with quick scale effect.
    
    Args:
        button: QPushButton to animate
        
    Returns:
        QPropertyAnimation: Press animation
    """
    effect = QGraphicsOpacityEffect(button)
    button.setGraphicsEffect(effect)
    
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(100)
    animation.setStartValue(1.0)
    animation.setKeyValueAt(0.5, 0.8)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.OutQuad)
    
    return animation


def create_pulse_animation(widget, duration=1000):
    """
    Create a subtle pulse animation for notification or attention.
    
    Args:
        widget: Widget to pulse
        duration: Full cycle duration in milliseconds
        
    Returns:
        QPropertyAnimation: Pulse animation
    """
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(1.0)
    animation.setKeyValueAt(0.5, 0.6)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.InOutSine)
    animation.setLoopCount(-1)  # Infinite loop
    
    return animation


class AnimationPresets:
    """
    Predefined animation presets for common UI patterns.
    """
    
    @staticmethod
    def dialog_entrance(dialog):
        """
        Animate dialog appearance with fade and slight scale.
        
        Args:
            dialog: QDialog to animate
        """
        return AnimationBuilder.create_fade_in(dialog, duration=250)
    
    @staticmethod
    def card_hover(card_widget):
        """
        Setup hover animation for card widget.
        
        Args:
            card_widget: Widget to setup hover for
            
        Returns:
            HoverAnimation: Configured hover animation manager
        """
        hover = HoverAnimation(card_widget, lift_height=3)
        hover.setup()
        return hover
    
    @staticmethod
    def list_item_entrance(items, start_index=0):
        """
        Animate list items with staggered entrance.
        
        Args:
            items: List of QListWidgetItem or widgets
            start_index: Index to start animation from
        """
        apply_entrance_animations(
            items[start_index:],
            animation_type='fade_slide',
            stagger_delay=30,
            start_delay=100
        )
    
    @staticmethod
    def notification_appear(notification_widget):
        """
        Animate notification appearance from top.
        
        Args:
            notification_widget: Widget to animate
            
        Returns:
            QPropertyAnimation: Slide animation
        """
        return AnimationBuilder.create_slide_up(
            notification_widget,
            distance=-30,  # Negative for slide down
            duration=400
        )


# Global animation manager instance
_animation_cache = {}

def get_cached_animation(widget_id, animation_type):
    """
    Get or create cached animation for reuse.
    
    Args:
        widget_id: Unique identifier for widget
        animation_type: Type of animation
        
    Returns:
        Animation object or None
    """
    key = f"{widget_id}_{animation_type}"
    return _animation_cache.get(key)


def cache_animation(widget_id, animation_type, animation):
    """
    Cache animation for reuse.
    
    Args:
        widget_id: Unique identifier for widget
        animation_type: Type of animation
        animation: Animation object to cache
    """
    key = f"{widget_id}_{animation_type}"
    _animation_cache[key] = animation
