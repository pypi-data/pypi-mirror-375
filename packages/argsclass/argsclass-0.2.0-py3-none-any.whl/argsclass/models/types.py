"""Simple argument type classes for command line argument parsing."""

from abc import ABC, abstractmethod
from typing import Any, Type


class ArgumentType(ABC):
    """Base class for all argument types."""
    
    @abstractmethod
    def convert(self, value: str) -> Any:
        """Convert a string value to the appropriate type."""
        pass
    
    @abstractmethod
    def validate(self, value: Any) -> bool:
        """Validate that a value is acceptable for this type."""
        pass


class PrimitiveType(ArgumentType):
    """Wrapper for primitive Python types."""
    
    def __init__(self, primitive_type: Type):
        if primitive_type not in (str, int, float):
            raise ValueError(f"Unsupported primitive type: {primitive_type}. Booleans are handled by flags, not options.")
        self.primitive_type = primitive_type
    
    def convert(self, value: str) -> Any:
        return self.primitive_type(value)
    
    def validate(self, value: Any) -> bool:
        if self.primitive_type == float:
            # Accept both int and float for float type
            return isinstance(value, (int, float))
        return isinstance(value, self.primitive_type)