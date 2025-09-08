"""Custom exceptions for Joy-Con library.

This module defines exceptions that can be raised during Joy-Con operations.
"""


class JoyConError(Exception):
    """Base exception for all Joy-Con related errors.
    
    Attributes:
        message: Error message describing what went wrong.
    """
    
    def __init__(self, message: str) -> None:
        """Initialize JoyConError.
        
        Args:
            message: Error message.
        """
        self.message = message
        super().__init__(self.message)


class ConnectionError(JoyConError):
    """Raised when connection to Joy-Con fails.
    
    This exception is raised when the library cannot establish or maintain
    a connection with the Joy-Con controller.
    """
    pass


class DeviceNotFoundError(JoyConError):
    """Raised when Joy-Con device is not found.
    
    This exception is raised when no Joy-Con controller can be detected
    via HID enumeration.
    """
    pass


class CommunicationError(JoyConError):
    """Raised when communication with Joy-Con fails.
    
    This exception is raised when sending or receiving data from the
    Joy-Con controller fails.
    """
    pass