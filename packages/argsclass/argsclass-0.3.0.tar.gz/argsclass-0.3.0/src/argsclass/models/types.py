"""Simple argument type classes for command line argument parsing.

This module provides type classes for handling argument value conversion and validation.
It includes both abstract base classes and concrete implementations for primitive types.

Classes:
    ArgumentType: Abstract base class for all argument types
    PrimitiveType: Wrapper for primitive Python types (str, int, float)

Example:
    >>> from argsclass.models.types import PrimitiveType
    >>> 
    >>> # Create type converters
    >>> str_type = PrimitiveType(str)
    >>> int_type = PrimitiveType(int)
    >>> float_type = PrimitiveType(float)
    >>> 
    >>> # Convert values
    >>> print(str_type.convert("hello"))  # "hello"
    >>> print(int_type.convert("42"))     # 42
    >>> print(float_type.convert("3.14")) # 3.14
    >>> 
    >>> # Validate values
    >>> print(int_type.validate(42))      # True
    >>> print(int_type.validate("42"))    # False
"""

from abc import ABC, abstractmethod
from typing import Any, Type


class ArgumentType(ABC):
    """Base class for all argument types.
    
    This abstract base class defines the interface that all argument type
    classes must implement. It provides methods for converting string values
    to the appropriate type and validating values.
    
    Subclasses must implement:
        convert: Convert a string value to the appropriate type
        validate: Validate that a value is acceptable for this type
    """
    
    @abstractmethod
    def convert(self, value: str) -> Any:
        """Convert a string value to the appropriate type.
        
        Args:
            value: String value to convert
            
        Returns:
            Any: Converted value of the appropriate type
            
        Raises:
            ValueError: If the value cannot be converted
        """
        pass
    
    @abstractmethod
    def validate(self, value: Any) -> bool:
        """Validate that a value is acceptable for this type.
        
        Args:
            value: Value to validate
            
        Returns:
            bool: True if the value is acceptable, False otherwise
        """
        pass


class PrimitiveType(ArgumentType):
    """Wrapper for primitive Python types.
    
    This class provides type conversion and validation for primitive Python types
    (str, int, float). It handles the conversion of string values to the appropriate
    type and validates that values are of the correct type.
    
    Attributes:
        primitive_type (Type): The primitive Python type (str, int, or float)
    
    Example:
        >>> int_type = PrimitiveType(int)
        >>> print(int_type.convert("42"))     # 42
        >>> print(int_type.validate(42))      # True
        >>> print(int_type.validate("42"))    # False
    """
    
    def __init__(self, primitive_type: Type):
        """Initialize primitive type wrapper.
        
        Args:
            primitive_type: The primitive Python type (str, int, or float)
            
        Raises:
            ValueError: If primitive_type is not str, int, or float
        """
        if primitive_type not in (str, int, float):
            raise ValueError(f"Unsupported primitive type: {primitive_type}. Booleans are handled by flags, not options.")
        self.primitive_type = primitive_type
    
    def convert(self, value: str) -> Any:
        """Convert a string value to the primitive type.
        
        Args:
            value: String value to convert
            
        Returns:
            Any: Converted value of the primitive type
            
        Raises:
            ValueError: If the value cannot be converted to the primitive type
        """
        return self.primitive_type(value)
    
    def validate(self, value: Any) -> bool:
        """Validate that a value is of the primitive type.
        
        Args:
            value: Value to validate
            
        Returns:
            bool: True if the value is of the correct type, False otherwise
            
        Note:
            For float types, both int and float values are considered valid.
        """
        if self.primitive_type == float:
            # Accept both int and float for float type
            return isinstance(value, (int, float))
        return isinstance(value, self.primitive_type)