"""
charm_animations.py - Spring-based animation system

Provides smooth, physics-based animations following DESIGN_SYSTEM.md specifications.
"""

from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QAbstractAnimation, QParallelAnimationGroup
from PyQt5.QtWidgets import QGraphicsOpacityEffect


class AnimationBuilder:
    """Builder for creating spring-based animations."""
    
    @staticmethod
    def create_fade_in(widget, duration=300):
        """
        Create a fade-in animation.
        
        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            
        Returns:
            QPropertyAnimation: Configured animation
        """
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutExpo)
        
        return animation
    
    @staticmethod
    def create_slide_up(widget, distance=20, duration=300):
        """
        Create a slide-up animation.
        
        Args:
            widget: Widget to animate
            distance: Distance to slide in pixels
            duration: Animation duration in milliseconds
            
        Returns:
            QPropertyAnimation: Configured animation
        """
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        
        start_pos = widget.pos()
        start_pos.setY(start_pos.y() + distance)
        
        animation.setStartValue(start_pos)
        animation.setEndValue(widget.pos())
        animation.setEasingCurve(QEasingCurve.OutExpo)
        
        return animation
    
    @staticmethod
    def create_scale_in(widget, duration=300):
        """
        Create a scale-in animation with spring overshoot.
        
        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            
        Returns:
            QParallelAnimationGroup: Combined scale and fade animation
        """
        # Note: QWidget doesn't have a scale property by default
        # This would need to be implemented with QGraphicsView or custom property
        # For now, we'll use fade-in as a placeholder
        return AnimationBuilder.create_fade_in(widget, duration)
    
    @staticmethod
    def create_hover_lift(widget, lift_height=2, duration=150):
        """
        Create a hover lift animation.
        
        Args:
            widget: Widget to animate
            lift_height: Height to lift in pixels
            duration: Animation duration in milliseconds
            
        Returns:
            QPropertyAnimation: Configured animation
        """
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        
        start_pos = widget.pos()
        end_pos = widget.pos()
        end_pos.setY(end_pos.y() - lift_height)
        
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutExpo)
        
        return animation
    
    @staticmethod
    def animate_widget_entrance(widget, animation_type='fade', duration=300, delay=0):
        """
        Animate a widget entrance with specified animation type.
        
        Args:
            widget: Widget to animate
            animation_type: 'fade', 'slide', or 'scale'
            duration: Animation duration in milliseconds
            delay: Delay before animation starts in milliseconds
        """
        if animation_type == 'fade':
            animation = AnimationBuilder.create_fade_in(widget, duration)
        elif animation_type == 'slide':
            animation = AnimationBuilder.create_slide_up(widget, 20, duration)
        elif animation_type == 'scale':
            animation = AnimationBuilder.create_scale_in(widget, duration)
        else:
            animation = AnimationBuilder.create_fade_in(widget, duration)
        
        if delay > 0:
            animation.setStartValue(animation.startValue())
            # Note: QTimer could be used for delay
        
        animation.start(QAbstractAnimation.DeleteWhenStopped)
        return animation


class SpringPhysics:
    """
    Spring physics calculator for natural motion.
    
    Based on DESIGN_SYSTEM.md spring specifications:
    - Tension: 200 (spring stiffness)
    - Friction: 20 (damping)
    - Mass: 1 (weight)
    """
    
    def __init__(self, tension=200, friction=20, mass=1.0):
        self.tension = tension
        self.friction = friction
        self.mass = mass
    
    def calculate_duration(self, distance):
        """
        Calculate animation duration based on distance and spring physics.
        
        Args:
            distance: Distance to travel
            
        Returns:
            int: Duration in milliseconds
        """
        # Simplified spring physics calculation
        # In a real implementation, this would solve the spring differential equation
        base_duration = 300
        distance_factor = min(distance / 100, 2.0)
        return int(base_duration * distance_factor)
    
    def get_easing_curve(self):
        """
        Get the appropriate easing curve for spring motion.
        
        Returns:
            QEasingCurve: Easing curve type
        """
        # OutExpo provides a spring-like deceleration
        return QEasingCurve.OutExpo


class HoverAnimation:
    """
    Manages hover animations for widgets.
    """
    
    def __init__(self, widget):
        self.widget = widget
        self.hover_animation = None
        self.unhover_animation = None
    
    def setup_hover_lift(self, lift_height=2):
        """
        Setup hover lift animation for a widget.
        
        Args:
            lift_height: Height to lift on hover
        """
        self.widget.setMouseTracking(True)
        
        # Store original position
        self.original_pos = self.widget.pos()
        
        # Create animations
        self.hover_animation = QPropertyAnimation(self.widget, b"pos")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.OutExpo)
        
        self.unhover_animation = QPropertyAnimation(self.widget, b"pos")
        self.unhover_animation.setDuration(150)
        self.unhover_animation.setEasingCurve(QEasingCurve.OutExpo)
    
    def on_hover_enter(self):
        """Trigger hover animation."""
        if self.hover_animation:
            lifted_pos = self.widget.pos()
            lifted_pos.setY(lifted_pos.y() - 2)
            
            self.hover_animation.setStartValue(self.widget.pos())
            self.hover_animation.setEndValue(lifted_pos)
            self.hover_animation.start()
    
    def on_hover_leave(self):
        """Trigger unhover animation."""
        if self.unhover_animation:
            self.unhover_animation.setStartValue(self.widget.pos())
            self.unhover_animation.setEndValue(self.original_pos)
            self.unhover_animation.start()


def apply_entrance_animations(widgets, stagger_delay=50):
    """
    Apply staggered entrance animations to a list of widgets.
    
    Args:
        widgets: List of widgets to animate
        stagger_delay: Delay between each widget animation in milliseconds
    """
    for i, widget in enumerate(widgets):
        AnimationBuilder.animate_widget_entrance(
            widget,
            animation_type='fade',
            duration=300,
            delay=i * stagger_delay
        )


def create_button_press_animation(button):
    """
    Create a press animation for a button.
    
    Args:
        button: QPushButton to animate
        
    Returns:
        QPropertyAnimation: Press animation
    """
    # This would typically use a scale transform
    # For PyQt5 without QGraphicsView, we use opacity as a substitute
    effect = QGraphicsOpacityEffect(button)
    button.setGraphicsEffect(effect)
    
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(100)
    animation.setStartValue(1.0)
    animation.setKeyValueAt(0.5, 0.7)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.OutQuad)
    
    return animation
