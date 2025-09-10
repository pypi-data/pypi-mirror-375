"""ArgSpec classes for command line argument specification.

This module defines the core argument specification classes used throughout
the argsclass library. It includes base classes, cardinality management,
and specific argument types (positional, option, flag).

Classes:
    Cardinality: Specifies how many values an argument accepts
    BaseArgSpec: Base class for all argument specifications
    NamedArgSpec: Base class for named arguments with aliases
    PositionalArgSpec: Specification for positional arguments
    OptionArgSpec: Specification for option arguments (--option value)
    FlagArgSpec: Specification for flag arguments (--flag)

Example:
    >>> from argsclass.models.argspec import PositionalArgSpec, OptionArgSpec, FlagArgSpec, Cardinality
    >>> from argsclass.models.types import PrimitiveType
    >>> 
    >>> # Create argument specifications
    >>> input_spec = PositionalArgSpec(
    ...     name="input",
    ...     help_text="Input file",
    ...     arg_type=PrimitiveType(str),
    ...     cardinality=Cardinality.single()
    ... )
    >>> 
    >>> output_spec = OptionArgSpec(
    ...     name="output",
    ...     help_text="Output file",
    ...     aliases={"o"},
    ...     arg_type=PrimitiveType(str),
    ...     cardinality=Cardinality.single()
    ... )
    >>> 
    >>> verbose_spec = FlagArgSpec(
    ...     name="verbose",
    ...     help_text="Verbose output",
    ...     aliases={"v"}
    ... )
"""

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, List, Optional as OptionalType, Set, Type, Union
from .types import ArgumentType, PrimitiveType


@dataclass(frozen=True)
class Cardinality:
    """Specifies how many values an argument accepts.
    
    This class defines the cardinality (count) constraints for arguments,
    specifying the minimum and maximum number of values that can be provided.
    It provides both direct instantiation and convenient class methods for
    common cardinality patterns.
    
    Attributes:
        min (int): Minimum number of values required (default: 1)
        max (Optional[int]): Maximum number of values allowed (default: 1, None means unlimited)
    
    Example:
        >>> # Direct instantiation
        >>> single = Cardinality(min=1, max=1)
        >>> multiple = Cardinality(min=1, max=None)
        >>> 
        >>> # Using class methods
        >>> required = Cardinality.single()      # Exactly 1 value
        >>> optional = Cardinality.zero_or_one() # 0 or 1 value
        >>> many = Cardinality.one_or_more()     # 1 or more values
        >>> 
        >>> # Check properties
        >>> print(required.is_required)  # True
        >>> print(optional.is_required)  # False
    """
    min: int = 1
    max: OptionalType[int] = 1
    
    def __post_init__(self):
        """Validate cardinality constraints.
        
        Raises:
            ValueError: If min or max values are invalid
        """
        if not isinstance(self.min, int) or self.min < 0:
            raise ValueError("min must be a non-negative integer")
        if self.max is not None:
            if not isinstance(self.max, int) or self.max < 0:
                raise ValueError("max must be a non-negative integer")
            if self.max < self.min:
                raise ValueError("max cannot be less than min")
    
    @property
    def is_required(self) -> bool:
        """True if at least one value is required.
        
        Returns:
            bool: True if min > 0, False otherwise
        """
        return self.min > 0
    
    @classmethod
    def single(cls) -> 'Cardinality':
        """Exactly one value (default).
        
        Returns:
            Cardinality: Cardinality requiring exactly one value
        """
        return cls(min=1, max=1)
    
    @classmethod
    def zero_or_one(cls) -> 'Cardinality':
        """Zero or one value (optional).
        
        Returns:
            Cardinality: Cardinality allowing zero or one value
        """
        return cls(min=0, max=1)
    
    @classmethod
    def zero_or_more(cls) -> 'Cardinality':
        """Zero or more values (optional, multiple).
        
        Returns:
            Cardinality: Cardinality allowing zero or more values
        """
        return cls(min=0, max=None)
    
    @classmethod
    def one_or_more(cls) -> 'Cardinality':
        """One or more values (required, multiple).
        
        Returns:
            Cardinality: Cardinality requiring at least one value
        """
        return cls(min=1, max=None)
    
    @classmethod
    def exactly(cls, count: int) -> 'Cardinality':
        """Exactly N values.
        
        Args:
            count: Exact number of values required
            
        Returns:
            Cardinality: Cardinality requiring exactly the specified count
            
        Raises:
            ValueError: If count is negative
        """
        if count < 0:
            raise ValueError("Count must be non-negative")
        return cls(min=count, max=count)


@dataclass(frozen=True)
class BaseArgSpec(ABC):
    """Base class for all argument specifications.
    
    This abstract base class defines the common interface and functionality
    for all argument specifications. It provides core properties like name,
    default value, help text, and utility methods for type checking and
    value validation.
    
    Attributes:
        name (str): The primary name of the argument (without dashes for options)
        default (Any): Default value if the argument is not provided
        help_text (str): Help text describing this argument
    
    Properties:
        destination (str): The attribute name where parsed values are stored
        is_required (bool): True if this argument is required
        is_optional (bool): True if this argument is optional
        kind (str): The kind of argument ("positional", "option", "flag", or "unknown")
    
    Example:
        >>> spec = PositionalArgSpec(name="input", help_text="Input file")
        >>> print(spec.name)           # "input"
        >>> print(spec.destination)    # "input"
        >>> print(spec.is_required)    # True (for positional args)
        >>> print(spec.kind)           # "positional"
    """
    
    # Core identification
    name: str
    """The primary name of the argument (without dashes for options)."""
    
    default: Any = None
    """Default value if the argument is not provided."""
    
    help_text: str = ""
    """Help text describing this argument."""
    
    def __post_init__(self):
        """Basic validation common to all argument types.
        
        Performs validation that applies to all argument specifications,
        including name validation and any subclass-specific validation.
        """
        self._validate_name()
    
    def _validate_name(self) -> None:
        """Validate the argument name.
        
        Raises:
            ValueError: If the name is empty or not a string
        """
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Argument name must be a non-empty string")
    
    
    @property
    def destination(self) -> str:
        """The attribute name where the parsed value will be stored.
        
        Converts the argument name to a valid Python attribute name by
        removing leading dashes and replacing hyphens with underscores.
        
        Returns:
            str: The destination attribute name
        """
        return self.name.lstrip('-').replace('-', '_')
    
    @property
    def is_required(self) -> bool:
        """True if this argument is required.
        
        For arguments with cardinality, checks if cardinality.is_required.
        For flags, always returns False (flags are always optional).
        
        Returns:
            bool: True if the argument is required, False otherwise
        """
        # For arguments with cardinality, check cardinality.is_required
        if hasattr(self, 'cardinality'):
            return self.cardinality.is_required
        # For flags, always optional
        return False
    
    @property
    def is_optional(self) -> bool:
        """True if this argument is optional (not required).
        
        Returns:
            bool: True if the argument is optional, False otherwise
        """
        return not self.is_required
    
    # Utility methods using isinstance checks
    def is_positional(self) -> bool:
        """True if this is a positional argument.
        
        Returns:
            bool: True if this is a PositionalArgSpec instance
        """
        return self.__class__.__name__ == "PositionalArgSpec"
    
    def is_option(self) -> bool:
        """True if this is an option argument.
        
        Returns:
            bool: True if this is an OptionArgSpec instance
        """
        return self.__class__.__name__ == "OptionArgSpec"
    
    def is_flag(self) -> bool:
        """True if this is a flag argument.
        
        Returns:
            bool: True if this is a FlagArgSpec instance
        """
        return self.__class__.__name__ == "FlagArgSpec"
    
    @property
    def kind(self) -> str:
        """The kind of argument this is.
        
        Returns:
            str: The argument kind ("positional", "option", "flag", or "unknown")
        """
        if self.is_positional():
            return "positional"
        elif self.is_option():
            return "option"
        elif self.is_flag():
            return "flag"
        else:
            return "unknown"
    
    def _validate_choices(self) -> None:
        """Validate choices constraint.
        
        Ensures that if choices are specified, they are not empty and that
        the default value (if any) is one of the valid choices.
        
        Raises:
            ValueError: If choices are empty or default is not in choices
        """
        if hasattr(self, 'choices') and self.choices is not None:
            if not self.choices:
                raise ValueError("Choices cannot be empty")
            if self.default is not None and self.default not in self.choices:
                raise ValueError("Default value must be one of the choices")
    
    def _setup_default_type(self) -> None:
        """Set up default argument type if none specified.
        
        If no argument type is specified, defaults to PrimitiveType(str).
        If a raw type is provided, wraps it in PrimitiveType.
        """
        if hasattr(self, 'arg_type'):
            if self.arg_type is None:
                object.__setattr__(self, 'arg_type', PrimitiveType(str))
            elif isinstance(self.arg_type, type):
                object.__setattr__(self, 'arg_type', PrimitiveType(self.arg_type))
    
    def validate_value(self, value: Any) -> bool:
        """Validate a value using the argument type and choices constraint.
        
        Args:
            value: The value to validate
            
        Returns:
            bool: True if the value is valid, False otherwise
        """
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
        """Convert a string value using the argument type and validate choices.
        
        Args:
            value: String value to convert
            
        Returns:
            Any: Converted value of the appropriate type
            
        Raises:
            ValueError: If the value cannot be converted or is not a valid choice
        """
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
    """Base class for named arguments (options and flags) that can have aliases.
    
    This class extends BaseArgSpec to add support for aliases, which are
    alternative names for the same argument (e.g., --output and -o).
    
    Attributes:
        aliases (Set[str]): Alternative names/aliases for this argument (short forms, etc.)
    
    Example:
        >>> spec = OptionArgSpec(
        ...     name="output",
        ...     aliases={"o", "out"},
        ...     help_text="Output file"
        ... )
        >>> print(spec.aliases)  # {"o", "out"}
    """
    
    aliases: Set[str] = field(default_factory=set)
    """Alternative names/aliases for this argument (short forms, etc.)."""
    
    def __post_init__(self):
        """Validate named argument specification.
        
        Performs validation specific to named arguments, including alias validation.
        """
        super().__post_init__()
        self._validate_aliases()
    
    def _validate_aliases(self) -> None:
        """Validate argument aliases.
        
        Ensures that aliases are properly formatted and valid.
        
        Raises:
            TypeError: If aliases are not iterable or contain non-string values
            ValueError: If any alias is an empty string
        """
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
    """Specification for positional arguments.
    
    Positional arguments are identified by their position in the command line
    rather than by a name or flag. They support type conversion, cardinality
    constraints, and choice validation.
    
    Attributes:
        arg_type (Union[ArgumentType, Type, None]): The type of value this argument accepts
        choices (Optional[List[Any]]): Valid choices for this argument value
        cardinality (Cardinality): How many values this argument accepts
    
    Example:
        >>> from argsclass.models.types import PrimitiveType
        >>> 
        >>> spec = PositionalArgSpec(
        ...     name="input",
        ...     help_text="Input file",
        ...     arg_type=PrimitiveType(str),
        ...     cardinality=Cardinality.single(),
        ...     choices=["file1.txt", "file2.txt"]
        ... )
        >>> print(spec.name)  # "input"
    """
    
    arg_type: Union[ArgumentType, Type, None] = None
    """The type of value this argument accepts."""
    
    choices: OptionalType[List[Any]] = None
    """Valid choices for this argument value."""
    
    cardinality: Cardinality = field(default_factory=Cardinality.single)
    """How many values this argument accepts."""
    
    def __post_init__(self):
        """Validate positional argument specification.
        
        Performs validation specific to positional arguments, including
        choices validation and type setup.
        """
        super().__post_init__()
        self._validate_choices()
        self._setup_default_type()
    
    def __str__(self) -> str:
        """String representation of the argument.
        
        Returns:
            str: The argument name
        """
        return self.name


@dataclass(frozen=True)
class OptionArgSpec(NamedArgSpec):
    """Specification for option arguments (named arguments with values).
    
    Option arguments are named arguments that take values, such as --output file.txt
    or -o file.txt. They support aliases, type conversion, cardinality constraints,
    and choice validation.
    
    Attributes:
        arg_type (Union[ArgumentType, Type, None]): The type of value this argument accepts
        choices (Optional[List[Any]]): Valid choices for this argument value
        cardinality (Cardinality): How many values this argument accepts
    
    Example:
        >>> from argsclass.models.types import PrimitiveType
        >>> 
        >>> spec = OptionArgSpec(
        ...     name="output",
        ...     help_text="Output file",
        ...     aliases={"o"},
        ...     arg_type=PrimitiveType(str),
        ...     cardinality=Cardinality.single()
        ... )
        >>> print(spec)  # "--output"
    """
    
    arg_type: Union[ArgumentType, Type, None] = None
    """The type of value this argument accepts."""
    
    choices: OptionalType[List[Any]] = None
    """Valid choices for this argument value."""
    
    cardinality: Cardinality = field(default_factory=Cardinality.single)
    """How many values this argument accepts."""
    
    def __post_init__(self):
        """Validate option argument specification.
        
        Performs validation specific to option arguments, including
        choices validation and type setup.
        """
        super().__post_init__()
        self._validate_choices()
        self._setup_default_type()
    
    def __str__(self) -> str:
        """String representation of the argument.
        
        Returns:
            str: The argument name with leading dashes (e.g., "--output")
        """
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

