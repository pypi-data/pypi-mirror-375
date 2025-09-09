"""Descriptors for class-based argument specification."""

from typing import Any, Optional
from .models import PositionalArgSpec, OptionArgSpec, FlagArgSpec, Cardinality, PrimitiveType


class PositionalDescriptor:
    """Descriptor for positional arguments."""
    
    def __init__(self, help_text: str = "", arg_type: Any = None, choices: Optional[list] = None, 
                 cardinality: Optional[Cardinality] = None, default: Any = None):
        self.help_text = help_text
        self.arg_type = arg_type
        self.choices = choices
        self.cardinality = cardinality or Cardinality.single()
        self.default = default
        self.name = None  # Will be set when the descriptor is bound to a class
    
    def __set_name__(self, owner, name):
        """Called when the descriptor is assigned to a class attribute."""
        self.name = name
    
    def __get__(self, instance, owner):
        """Get the value from the instance or return the descriptor itself."""
        if instance is None:
            return self
        return getattr(instance, f"_{self.name}", self.default)
    
    def __set__(self, instance, value):
        """Set the value on the instance."""
        setattr(instance, f"_{self.name}", value)
    
    def to_argspec(self) -> PositionalArgSpec:
        """Convert this descriptor to a PositionalArgSpec."""
        return PositionalArgSpec(
            name=self.name,
            help_text=self.help_text,
            arg_type=self.arg_type,
            choices=self.choices,
            cardinality=self.cardinality,
            default=self.default
        )


class OptionDescriptor:
    """Descriptor for option arguments."""
    
    def __init__(self, help_text: str = "", arg_type: Any = None, choices: Optional[list] = None,
                 cardinality: Optional[Cardinality] = None, default: Any = None, aliases: Optional[set] = None):
        self.help_text = help_text
        self.arg_type = arg_type
        self.choices = choices
        self.cardinality = cardinality or Cardinality.single()
        self.default = default
        self.aliases = aliases or set()
        self.name = None  # Will be set when the descriptor is bound to a class
    
    def __set_name__(self, owner, name):
        """Called when the descriptor is assigned to a class attribute."""
        self.name = name
    
    def __get__(self, instance, owner):
        """Get the value from the instance or return the descriptor itself."""
        if instance is None:
            return self
        return getattr(instance, f"_{self.name}", self.default)
    
    def __set__(self, instance, value):
        """Set the value on the instance."""
        setattr(instance, f"_{self.name}", value)
    
    def to_argspec(self) -> OptionArgSpec:
        """Convert this descriptor to an OptionArgSpec."""
        return OptionArgSpec(
            name=self.name,
            help_text=self.help_text,
            arg_type=self.arg_type,
            choices=self.choices,
            cardinality=self.cardinality,
            default=self.default,
            aliases=self.aliases
        )


class FlagDescriptor:
    """Descriptor for flag arguments."""
    
    def __init__(self, help_text: str = "", aliases: Optional[set] = None):
        self.help_text = help_text
        self.aliases = aliases or set()
        self.name = None  # Will be set when the descriptor is bound to a class
    
    def __set_name__(self, owner, name):
        """Called when the descriptor is assigned to a class attribute."""
        self.name = name
    
    def __get__(self, instance, owner):
        """Get the value from the instance or return the descriptor itself."""
        if instance is None:
            return self
        return getattr(instance, f"_{self.name}", False)
    
    def __set__(self, instance, value):
        """Set the value on the instance."""
        setattr(instance, f"_{self.name}", value)
    
    def to_argspec(self) -> FlagArgSpec:
        """Convert this descriptor to a FlagArgSpec."""
        return FlagArgSpec(
            name=self.name,
            help_text=self.help_text,
            aliases=self.aliases
        )


def positional(help_text: str = "", arg_type: Any = None, choices: Optional[list] = None,
               cardinality: Optional[Cardinality] = None, default: Any = None) -> PositionalDescriptor:
    """Create a positional argument descriptor.
    
    Args:
        help_text: Help text for the argument
        arg_type: Type for the argument (str, int, float, or PrimitiveType)
        choices: Valid choices for the argument
        cardinality: How many values this argument accepts
        default: Default value for the argument
    
    Returns:
        PositionalDescriptor instance
    """
    return PositionalDescriptor(
        help_text=help_text,
        arg_type=arg_type,
        choices=choices,
        cardinality=cardinality,
        default=default
    )


def option(help_text: str = "", arg_type: Any = None, choices: Optional[list] = None,
           cardinality: Optional[Cardinality] = None, default: Any = None, aliases: Optional[set] = None) -> OptionDescriptor:
    """Create an option argument descriptor.
    
    Args:
        help_text: Help text for the argument
        arg_type: Type for the argument (str, int, float, or PrimitiveType)
        choices: Valid choices for the argument
        cardinality: How many values this argument accepts
        default: Default value for the argument
        aliases: Alternative names for the argument
    
    Returns:
        OptionDescriptor instance
    """
    return OptionDescriptor(
        help_text=help_text,
        arg_type=arg_type,
        choices=choices,
        cardinality=cardinality,
        default=default,
        aliases=aliases
    )


def flag(help_text: str = "", aliases: Optional[set] = None) -> FlagDescriptor:
    """Create a flag argument descriptor.
    
    Args:
        help_text: Help text for the argument
        aliases: Alternative names for the argument
    
    Returns:
        FlagDescriptor instance
    """
    return FlagDescriptor(
        help_text=help_text,
        aliases=aliases
    )