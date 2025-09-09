"""ArgSpec classes for command line argument specification."""

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, List, Optional as OptionalType, Set, Type, Union
from .types import ArgumentType, PrimitiveType


@dataclass(frozen=True)
class Cardinality:
    """Specifies how many values an argument accepts."""
    min: int = 1
    max: OptionalType[int] = 1
    
    def __post_init__(self):
        if not isinstance(self.min, int) or self.min < 0:
            raise ValueError("min must be a non-negative integer")
        if self.max is not None:
            if not isinstance(self.max, int) or self.max < 0:
                raise ValueError("max must be a non-negative integer")
            if self.max < self.min:
                raise ValueError("max cannot be less than min")
    
    @property
    def is_required(self) -> bool:
        """True if at least one value is required."""
        return self.min > 0
    
    @classmethod
    def single(cls) -> 'Cardinality':
        """Exactly one value (default)."""
        return cls(min=1, max=1)
    
    @classmethod
    def zero_or_one(cls) -> 'Cardinality':
        """Zero or one value."""
        return cls(min=0, max=1)
    
    @classmethod
    def zero_or_more(cls) -> 'Cardinality':
        """Zero or more values."""
        return cls(min=0, max=None)
    
    @classmethod
    def one_or_more(cls) -> 'Cardinality':
        """One or more values."""
        return cls(min=1, max=None)
    
    @classmethod
    def exactly(cls, count: int) -> 'Cardinality':
        """Exactly N values."""
        return cls(min=count, max=count)


@dataclass(frozen=True)
class BaseArgSpec(ABC):
    """Base class for all argument specifications."""
    
    # Core identification
    name: str
    """The primary name of the argument (without dashes for options)."""
    
    default: Any = None
    """Default value if the argument is not provided."""
    
    help_text: str = ""
    """Help text describing this argument."""
    
    def __post_init__(self):
        """Basic validation common to all argument types."""
        self._validate_name()
    
    def _validate_name(self) -> None:
        """Validate the argument name."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Argument name must be a non-empty string")
    
    
    @property
    def destination(self) -> str:
        """The attribute name where the parsed value will be stored."""
        return self.name.lstrip('-').replace('-', '_')
    
    @property
    def is_required(self) -> bool:
        """True if this argument is required."""
        # For arguments with cardinality, check cardinality.is_required
        if hasattr(self, 'cardinality'):
            return self.cardinality.is_required
        # For flags, always optional
        return False
    
    @property
    def is_optional(self) -> bool:
        """True if this argument is optional (not required)."""
        return not self.is_required
    
    # Utility methods using isinstance checks
    def is_positional(self) -> bool:
        """True if this is a positional argument."""
        return self.__class__.__name__ == "PositionalArgSpec"
    
    def is_option(self) -> bool:
        """True if this is an option argument."""
        return self.__class__.__name__ == "OptionArgSpec"
    
    def is_flag(self) -> bool:
        """True if this is a flag argument."""
        return self.__class__.__name__ == "FlagArgSpec"
    
    @property
    def kind(self) -> str:
        """The kind of argument this is."""
        if self.is_positional():
            return "positional"
        elif self.is_option():
            return "option"
        elif self.is_flag():
            return "flag"
        else:
            return "unknown"
    
    def _validate_choices(self) -> None:
        """Validate choices constraint."""
        if hasattr(self, 'choices') and self.choices is not None:
            if not self.choices:
                raise ValueError("Choices cannot be empty")
            if self.default is not None and self.default not in self.choices:
                raise ValueError("Default value must be one of the choices")
    
    def _setup_default_type(self) -> None:
        """Set up default argument type if none specified."""
        if hasattr(self, 'arg_type'):
            if self.arg_type is None:
                object.__setattr__(self, 'arg_type', PrimitiveType(str))
            elif isinstance(self.arg_type, type):
                object.__setattr__(self, 'arg_type', PrimitiveType(self.arg_type))
    
    def validate_value(self, value: Any) -> bool:
        """Validate a value using the argument type and choices constraint."""
        # For flags, just check if it's a boolean
        if self.is_flag():
            return isinstance(value, bool)
        
        # For other types, use the arg_type
        if hasattr(self, 'arg_type') and self.arg_type:
            if not self.arg_type.validate(value):
                return False
        
        # Check choices constraint
        if hasattr(self, 'choices') and self.choices is not None:
            if value not in self.choices:
                return False
        
        return True
    
    def convert_value(self, value: str) -> Any:
        """Convert a string value using the argument type and validate choices."""
        # For flags, convert boolean
        if self.is_flag():
            if value.lower() in ('true', '1', 'yes', 'on'):
                return True
            elif value.lower() in ('false', '0', 'no', 'off'):
                return False
            else:
                raise ValueError(f"Invalid boolean value: {value}")
        
        # For other types, use the arg_type
        if hasattr(self, 'arg_type') and self.arg_type:
            converted = self.arg_type.convert(value)
        else:
            converted = str(value)
        
        # Check choices constraint
        if hasattr(self, 'choices') and self.choices is not None:
            if converted not in self.choices:
                raise ValueError(f"Invalid choice: {converted}. Must be one of: {', '.join(map(str, self.choices))}")
        
        return converted


@dataclass(frozen=True) 
class NamedArgSpec(BaseArgSpec):
    """Base class for named arguments (options and flags) that can have aliases."""
    
    aliases: Set[str] = field(default_factory=set)
    """Alternative names/aliases for this argument (short forms, etc.)."""
    
    def __post_init__(self):
        """Validate named argument specification."""
        super().__post_init__()
        self._validate_aliases()
    
    def _validate_aliases(self) -> None:
        """Validate argument aliases."""
        if not isinstance(self.aliases, set):
            # Convert to set if it's another iterable
            try:
                object.__setattr__(self, 'aliases', set(self.aliases))
            except TypeError:
                raise TypeError("aliases must be iterable")
        
        for alias in self.aliases:
            if not isinstance(alias, str):
                raise TypeError("All aliases must be strings")
            if not alias:
                raise ValueError("Aliases cannot be empty strings")


@dataclass(frozen=True)
class PositionalArgSpec(BaseArgSpec):
    """Specification for positional arguments."""
    
    arg_type: Union[ArgumentType, Type, None] = None
    """The type of value this argument accepts."""
    
    choices: OptionalType[List[Any]] = None
    """Valid choices for this argument value."""
    
    cardinality: Cardinality = field(default_factory=Cardinality.single)
    """How many values this argument accepts."""
    
    def __post_init__(self):
        """Validate positional argument specification."""
        super().__post_init__()
        self._validate_choices()
        self._setup_default_type()
    
    def __str__(self) -> str:
        """String representation of the argument."""
        return self.name


@dataclass(frozen=True)
class OptionArgSpec(NamedArgSpec):
    """Specification for option arguments (named arguments with values)."""
    
    arg_type: Union[ArgumentType, Type, None] = None
    """The type of value this argument accepts."""
    
    choices: OptionalType[List[Any]] = None
    """Valid choices for this argument value."""
    
    cardinality: Cardinality = field(default_factory=Cardinality.single)
    """How many values this argument accepts."""
    
    def __post_init__(self):
        """Validate option argument specification."""
        super().__post_init__()
        self._validate_choices()
        self._setup_default_type()
    
    def __str__(self) -> str:
        """String representation of the argument."""
        return f"--{self.name}"


@dataclass(frozen=True)
class FlagArgSpec(NamedArgSpec):
    """Specification for flag arguments (boolean switches)."""
    
    def __post_init__(self):
        """Validate flag argument specification."""
        super().__post_init__()
        # Flags always default to False by definition
        # Override any user-provided default to ensure consistency
        object.__setattr__(self, 'default', False)
    
    def __str__(self) -> str:
        """String representation of the argument."""
        return f"--{self.name}"

