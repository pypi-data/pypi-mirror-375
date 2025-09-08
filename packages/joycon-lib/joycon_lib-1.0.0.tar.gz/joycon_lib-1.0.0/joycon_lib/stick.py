"""Analog stick (joystick) support for Joy-Con controllers.

This module provides classes for managing analog stick input from Joy-Con controllers.
"""

from typing import Optional
from dataclasses import dataclass
import math


@dataclass
class StickState:
    """Represents the state of an analog stick.
    
    Attributes:
        x: X-axis value (-1.0 to 1.0, where -1 is left, 1 is right).
        y: Y-axis value (-1.0 to 1.0, where -1 is down, 1 is up).
        raw_x: Raw X value from the controller.
        raw_y: Raw Y value from the controller.
    """
    x: float = 0.0
    y: float = 0.0
    raw_x: int = 0
    raw_y: int = 0
    
    def get_angle(self) -> float:
        """Get the angle of the stick in degrees (0-360).
        
        Returns:
            Angle in degrees where 0 is right, 90 is up, 180 is left, 270 is down.
        """
        return (math.degrees(math.atan2(self.y, self.x)) + 360) % 360
    
    def get_magnitude(self) -> float:
        """Get the magnitude of stick displacement (0.0 to 1.0).
        
        Returns:
            Distance from center (0.0 = centered, 1.0 = fully displaced).
        """
        return min(math.sqrt(self.x ** 2 + self.y ** 2), 1.0)
    
    def is_centered(self, deadzone: float = 0.1) -> bool:
        """Check if the stick is centered within a deadzone.
        
        Args:
            deadzone: Threshold for considering the stick centered (0.0 to 1.0).
        
        Returns:
            True if stick is within the deadzone, False otherwise.
        """
        return self.get_magnitude() < deadzone
    
    def get_direction_4way(self) -> Optional[str]:
        """Get 4-way directional input from the stick.
        
        Returns:
            'up', 'down', 'left', 'right', or None if centered.
        """
        if self.is_centered(0.3):
            return None
        
        if abs(self.x) > abs(self.y):
            return 'right' if self.x > 0 else 'left'
        else:
            return 'up' if self.y > 0 else 'down'
    
    def get_direction_8way(self) -> Optional[str]:
        """Get 8-way directional input from the stick.
        
        Returns:
            Direction string ('up', 'up-right', 'right', etc.) or None if centered.
        """
        if self.is_centered(0.3):
            return None
        
        angle = self.get_angle()
        
        directions = [
            (337.5, 22.5, 'right'),
            (22.5, 67.5, 'up-right'),
            (67.5, 112.5, 'up'),
            (112.5, 157.5, 'up-left'),
            (157.5, 202.5, 'left'),
            (202.5, 247.5, 'down-left'),
            (247.5, 292.5, 'down'),
            (292.5, 337.5, 'down-right'),
        ]
        
        for start, end, direction in directions:
            if start > end:  # Wraps around 0
                if angle >= start or angle < end:
                    return direction
            else:
                if start <= angle < end:
                    return direction
        
        return 'right'  # Default fallback
    
    def __repr__(self) -> str:
        """Return string representation of stick state.
        
        Returns:
            String showing stick position.
        """
        if self.is_centered():
            return "StickState(centered)"
        return f"StickState(x={self.x:.2f}, y={self.y:.2f}, mag={self.get_magnitude():.2f})"


class StickCalibration:
    """Handles calibration for analog sticks.
    
    This class manages dead zones and calibration data for accurate
    stick input processing.
    
    Attributes:
        center_x: Calibrated center X value.
        center_y: Calibrated center Y value.
        max_x: Maximum X value.
        min_x: Minimum X value.
        max_y: Maximum Y value.
        min_y: Minimum Y value.
        deadzone: Deadzone threshold.
    """
    
    def __init__(self, center_x: int = 0, center_y: int = 0,
                 max_x: int = 32767, min_x: int = -32767,
                 max_y: int = 32767, min_y: int = -32767,
                 deadzone: float = 0.15) -> None:
        """Initialize stick calibration.
        
        Args:
            center_x: Center X position when stick is neutral.
            center_y: Center Y position when stick is neutral.
            max_x: Maximum X value.
            min_x: Minimum X value.
            max_y: Maximum Y value.
            min_y: Minimum Y value.
            deadzone: Deadzone threshold (0.0 to 1.0).
        """
        self.center_x = center_x
        self.center_y = center_y
        self.max_x = max_x
        self.min_x = min_x
        self.max_y = max_y
        self.min_y = min_y
        self.deadzone = deadzone
    
    def process(self, raw_x: int, raw_y: int) -> StickState:
        """Process raw stick values into normalized state.
        
        Args:
            raw_x: Raw X value from controller.
            raw_y: Raw Y value from controller.
        
        Returns:
            Processed StickState with normalized values.
        """
        # Calculate normalized values (-1.0 to 1.0)
        if raw_x >= self.center_x:
            x = (raw_x - self.center_x) / (self.max_x - self.center_x) if self.max_x != self.center_x else 0
        else:
            x = (raw_x - self.center_x) / (self.center_x - self.min_x) if self.center_x != self.min_x else 0
        
        # Invert Y axis so up is positive, down is negative
        if raw_y >= self.center_y:
            y = -(raw_y - self.center_y) / (self.max_y - self.center_y) if self.max_y != self.center_y else 0
        else:
            y = -(raw_y - self.center_y) / (self.center_y - self.min_y) if self.center_y != self.min_y else 0
        
        # Clamp to valid range
        x = max(-1.0, min(1.0, x))
        y = max(-1.0, min(1.0, y))
        
        # Apply deadzone
        magnitude = math.sqrt(x ** 2 + y ** 2)
        if magnitude < self.deadzone:
            x = y = 0.0
        elif magnitude > 1.0:
            # Normalize if outside unit circle
            x /= magnitude
            y /= magnitude
        
        return StickState(x=x, y=y, raw_x=raw_x, raw_y=raw_y)