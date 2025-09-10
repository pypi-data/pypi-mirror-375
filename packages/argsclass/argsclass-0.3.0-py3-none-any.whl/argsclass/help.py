"""Help message generation and validation error handling for command line arguments.

This module provides comprehensive help message generation in argparse style,
validation error collection and reporting, and utility functions for help flag
detection and processing.

Classes:
    HelpFormatter: Formats help messages with argparse-style output
    ValidationError: Represents a single validation error with context
    ValidationErrorCollector: Collects and manages multiple validation errors

Functions:
    format_help: Generate formatted help message for argument specifications
    detect_help_flag: Check if help flags are present in argv
    remove_help_flags: Remove help flags from argv list

Example:
    >>> from argsclass.help import format_help, detect_help_flag
    >>> from argsclass.models import PositionalArgSpec, OptionArgSpec, FlagArgSpec
    >>> 
    >>> specs = [
    ...     PositionalArgSpec(name="input", help_text="Input file"),
    ...     OptionArgSpec(name="output", help_text="Output file", aliases={"o"}),
    ...     FlagArgSpec(name="verbose", help_text="Verbose output", aliases={"v"})
    ... ]
    >>> 
    >>> # Check for help flag
    >>> if detect_help_flag(sys.argv):
    ...     print(format_help(specs, prog="myapp", description="My application"))
    ...     sys.exit(0)
"""

import sys
from typing import List, Optional, Dict, Any
from .models import BaseArgSpec, PositionalArgSpec, OptionArgSpec, FlagArgSpec, Cardinality


class HelpFormatter:
    """Formats help messages in argparse style.
    
    This class provides comprehensive help message formatting that closely follows
    the argparse library's output format. It handles usage lines, argument descriptions,
    type information, choices, defaults, and cardinality information.
    
    The formatter automatically detects terminal width and adjusts formatting
    accordingly. It supports custom program names, descriptions, and epilog text.
    
    Attributes:
        prog (str): Program name for usage line
        usage (Optional[str]): Custom usage string override
        description (Optional[str]): Program description
        epilog (Optional[str]): Text displayed after argument help
        max_help_position (int): Maximum column position for help text alignment
        width (int): Terminal width for text wrapping
    
    Example:
        >>> formatter = HelpFormatter(prog="myapp", description="My application")
        >>> help_text = formatter.format_help(arg_specs)
        >>> print(help_text)
    """
    
    def __init__(self, 
                 prog: Optional[str] = None,
                 usage: Optional[str] = None,
                 description: Optional[str] = None,
                 epilog: Optional[str] = None,
                 formatter_class: Optional[type] = None,
                 max_help_position: int = 24,
                 width: Optional[int] = None):
        """Initialize the help formatter.
        
        Args:
            prog: Program name (defaults to sys.argv[0] if available, otherwise "program")
            usage: Custom usage string override. If None, usage is auto-generated
            description: Program description displayed after usage line
            epilog: Text to display after argument help section
            formatter_class: Formatter class (for argparse compatibility, currently unused)
            max_help_position: Maximum column position for help text alignment (default: 24)
            width: Terminal width for text wrapping (defaults to auto-detect)
        
        Note:
            The formatter automatically detects terminal width using shutil.get_terminal_size().
            If detection fails, it defaults to 80 columns.
        """
        self.prog = prog or (sys.argv[0] if sys.argv else "program")
        self.usage = usage
        self.description = description
        self.epilog = epilog
        self.max_help_position = max_help_position
        self.width = width or self._get_terminal_width()
    
    def _get_terminal_width(self) -> int:
        """Get terminal width, defaulting to 80 if detection fails.
        
        Returns:
            int: Terminal width in columns, or 80 if detection fails
            
        Note:
            Uses shutil.get_terminal_size() for detection. Falls back to 80
            columns if the operation fails (e.g., in non-terminal environments).
        """
        try:
            import shutil
            return shutil.get_terminal_size().columns
        except (AttributeError, OSError):
            return 80
    
    def format_help(self, arg_specs: List[BaseArgSpec]) -> str:
        """Format a complete help message.
        
        Generates a comprehensive help message including usage line, description,
        argument help, and epilog. The format closely follows argparse conventions.
        
        Args:
            arg_specs: List of argument specifications to include in help
            
        Returns:
            str: Complete formatted help message
            
        Example:
            >>> specs = [PositionalArgSpec(name="input", help_text="Input file")]
            >>> formatter = HelpFormatter(prog="myapp")
            >>> help_text = formatter.format_help(specs)
            >>> print(help_text)
            usage: myapp INPUT
            <BLANKLINE>
            arguments:
              INPUT                    Input file
        """
        lines = []
        
        # Usage line
        usage_line = self._format_usage(arg_specs)
        if usage_line:
            lines.append(usage_line)
            lines.append("")
        
        # Description
        if self.description:
            lines.append(self.description)
            lines.append("")
        
        # Arguments help
        if arg_specs:
            lines.append("arguments:")
            for spec in arg_specs:
                help_text = self._format_argument_help(spec)
                if help_text:
                    lines.append(help_text)
            lines.append("")
        
        # Epilog
        if self.epilog:
            lines.append(self.epilog)
        
        return "\n".join(lines)
    
    def _format_usage(self, arg_specs: List[BaseArgSpec]) -> str:
        """Format the usage line.
        
        Generates a usage line showing how to use the program with its arguments.
        Follows argparse conventions with positional arguments first, then [options].
        
        Args:
            arg_specs: List of argument specifications
            
        Returns:
            str: Formatted usage line (e.g., "usage: program POSITIONAL [options]")
            
        Note:
            If a custom usage string was provided during initialization,
            it will be used instead of auto-generation.
        """
        if self.usage:
            return f"usage: {self.usage}"
        
        usage_parts = [f"usage: {self.prog}"]
        
        # Add positional arguments
        positional_specs = [spec for spec in arg_specs if isinstance(spec, PositionalArgSpec)]
        for spec in positional_specs:
            usage_parts.append(self._format_positional_usage(spec))
        
        # Add optional arguments (options and flags)
        optional_specs = [spec for spec in arg_specs if isinstance(spec, (OptionArgSpec, FlagArgSpec))]
        if optional_specs:
            usage_parts.append("[options]")
        
        return " ".join(usage_parts)
    
    def _format_positional_usage(self, spec: PositionalArgSpec) -> str:
        """Format usage for a positional argument.
        
        Generates the appropriate usage representation for a positional argument
        based on its cardinality (required, optional, multiple, etc.).
        
        Args:
            spec: Positional argument specification
            
        Returns:
            str: Usage representation (e.g., "INPUT", "[INPUT]", "INPUT [INPUT ...]")
            
        Examples:
            - Required single: "INPUT"
            - Optional single: "[INPUT]" 
            - One or more: "INPUT [INPUT ...]"
            - Exactly 3: "INPUT INPUT INPUT"
        """
        name = spec.name.upper()
        
        if spec.cardinality.min == 0:
            # Optional positional
            return f"[{name}]"
        elif spec.cardinality.max == 1:
            # Single required
            return name
        elif spec.cardinality.max is None:
            # One or more
            return f"{name} [{name} ...]"
        else:
            # Exact count
            return " ".join([name] * spec.cardinality.max)
    
    def _format_argument_help(self, spec: BaseArgSpec) -> str:
        """Format help for a single argument.
        
        Delegates to the appropriate formatting method based on argument type.
        
        Args:
            spec: Argument specification to format
            
        Returns:
            str: Formatted help line for the argument, or empty string if unsupported
        """
        if isinstance(spec, PositionalArgSpec):
            return self._format_positional_help(spec)
        elif isinstance(spec, OptionArgSpec):
            return self._format_option_help(spec)
        elif isinstance(spec, FlagArgSpec):
            return self._format_flag_help(spec)
        else:
            return ""
    
    def _format_positional_help(self, spec: PositionalArgSpec) -> str:
        """Format help for a positional argument.
        
        Creates a formatted help line for a positional argument including its name,
        help text, cardinality information, type, choices, and default value.
        
        Args:
            spec: Positional argument specification
            
        Returns:
            str: Formatted help line (e.g., "  INPUT                    Input file (optional) [str] (default: input.txt)")
        """
        name = spec.name.upper()
        help_text = spec.help_text or f"{spec.name} argument"
        
        # Add cardinality info
        if spec.cardinality.min == 0:
            help_text += " (optional)"
        elif spec.cardinality.max is None:
            help_text += " (one or more)"
        elif spec.cardinality.max > 1:
            help_text += f" (exactly {spec.cardinality.max})"
        
        # Add type info
        if hasattr(spec, 'arg_type') and spec.arg_type:
            type_name = self._get_type_name(spec.arg_type)
            if type_name != 'str':
                help_text += f" [{type_name}]"
        
        # Add choices info
        if hasattr(spec, 'choices') and spec.choices:
            choices_str = ", ".join(map(str, spec.choices))
            help_text += f" (choices: {choices_str})"
        
        # Add default info
        if spec.default is not None:
            help_text += f" (default: {spec.default})"
        
        return f"  {name:<{self.max_help_position}} {help_text}"
    
    def _format_option_help(self, spec: OptionArgSpec) -> str:
        """Format help for an option argument.
        
        Creates a formatted help line for an option argument including all its names
        (main name and aliases), help text, cardinality information, type, choices,
        and default value.
        
        Args:
            spec: Option argument specification
            
        Returns:
            str: Formatted help line (e.g., "  --output, -o             Output file [str] (default: output.txt)")
        """
        # Build option names
        option_names = [f"--{spec.name}"]
        for alias in spec.aliases:
            if len(alias) == 1:
                option_names.append(f"-{alias}")
            else:
                option_names.append(f"--{alias}")
        
        option_str = ", ".join(option_names)
        
        # Build help text
        help_text = spec.help_text or f"{spec.name} option"
        
        # Add cardinality info
        if spec.cardinality.min == 0:
            help_text += " (optional)"
        elif spec.cardinality.max is None:
            help_text += " (one or more)"
        elif spec.cardinality.max > 1:
            help_text += f" (exactly {spec.cardinality.max})"
        
        # Add type info
        if hasattr(spec, 'arg_type') and spec.arg_type:
            type_name = self._get_type_name(spec.arg_type)
            if type_name != 'str':
                help_text += f" [{type_name}]"
        
        # Add choices info
        if hasattr(spec, 'choices') and spec.choices:
            choices_str = ", ".join(map(str, spec.choices))
            help_text += f" (choices: {choices_str})"
        
        # Add default info
        if spec.default is not None:
            help_text += f" (default: {spec.default})"
        
        return f"  {option_str:<{self.max_help_position}} {help_text}"
    
    def _format_flag_help(self, spec: FlagArgSpec) -> str:
        """Format help for a flag argument.
        
        Creates a formatted help line for a flag argument including all its names
        (main name and aliases), help text, and optional indicator.
        
        Args:
            spec: Flag argument specification
            
        Returns:
            str: Formatted help line (e.g., "  --verbose, -v            Verbose output (optional)")
        """
        # Build flag names
        flag_names = [f"--{spec.name}"]
        for alias in spec.aliases:
            if len(alias) == 1:
                flag_names.append(f"-{alias}")
            else:
                flag_names.append(f"--{alias}")
        
        flag_str = ", ".join(flag_names)
        
        # Build help text
        help_text = spec.help_text or f"{spec.name} flag"
        help_text += " (optional)"
        
        return f"  {flag_str:<{self.max_help_position}} {help_text}"
    
    def _get_type_name(self, arg_type: Any) -> str:
        """Get a human-readable type name.
        
        Extracts a readable type name from various type representations,
        including primitive types, PrimitiveType objects, and custom types.
        
        Args:
            arg_type: Type object to extract name from
            
        Returns:
            str: Human-readable type name (e.g., "str", "int", "float")
            
        Note:
            Handles PrimitiveType objects by accessing their primitive_type attribute.
            Falls back to string representation if no other method works.
        """
        if hasattr(arg_type, '__name__'):
            return arg_type.__name__
        elif hasattr(arg_type, 'python_type'):
            return arg_type.python_type.__name__
        elif hasattr(arg_type, 'type_name'):
            return arg_type.type_name
        elif hasattr(arg_type, 'primitive_type'):
            # For PrimitiveType objects
            return arg_type.primitive_type.__name__
        else:
            return str(arg_type)


class ValidationError:
    """Represents a validation error with context.
    
    This class encapsulates a single validation error with all relevant context
    information including the error message, argument name, value that caused
    the error, and error type.
    
    Attributes:
        message (str): The error message describing what went wrong
        argument (Optional[str]): Name of the argument that caused the error
        value (Optional[str]): The value that caused the error
        error_type (str): Type of error (default: "error")
    
    Example:
        >>> error = ValidationError("Invalid choice", argument="format", value="csv")
        >>> print(error)
        Invalid choice (argument format, value 'csv')
    """
    
    def __init__(self, message: str, argument: Optional[str] = None, 
                 value: Optional[str] = None, error_type: str = "error"):
        """Initialize validation error.
        
        Args:
            message: Error message describing what went wrong
            argument: Name of the argument that caused the error (optional)
            value: The value that caused the error (optional)
            error_type: Type of error - "error", "warning", etc. (default: "error")
        """
        self.message = message
        self.argument = argument
        self.value = value
        self.error_type = error_type
    
    def __str__(self) -> str:
        """String representation of the error.
        
        Returns:
            str: Formatted error message with context information
        """
        parts = []
        if self.argument:
            parts.append(f"argument {self.argument}")
        if self.value:
            parts.append(f"value '{self.value}'")
        if parts:
            return f"{self.message} ({', '.join(parts)})"
        else:
            return self.message


class ValidationErrorCollector:
    """Collects and manages validation errors.
    
    This class provides a centralized way to collect multiple validation errors
    during argument parsing, allowing all errors to be reported together rather
    than stopping at the first error encountered.
    
    Attributes:
        errors (List[ValidationError]): List of collected validation errors
    
    Example:
        >>> collector = ValidationErrorCollector()
        >>> collector.add_error("Invalid choice", argument="format", value="csv")
        >>> collector.add_error("Missing required argument", argument="input")
        >>> if collector.has_errors():
        ...     print(collector.format_errors())
    """
    
    def __init__(self):
        """Initialize error collector."""
        self.errors: List[ValidationError] = []
    
    def add_error(self, message: str, argument: Optional[str] = None, 
                  value: Optional[str] = None, error_type: str = "error"):
        """Add a validation error.
        
        Creates a new ValidationError and adds it to the collection.
        
        Args:
            message: Error message describing what went wrong
            argument: Name of the argument that caused the error (optional)
            value: The value that caused the error (optional)
            error_type: Type of error - "error", "warning", etc. (default: "error")
        """
        self.errors.append(ValidationError(message, argument, value, error_type))
    
    def has_errors(self) -> bool:
        """Check if there are any errors.
        
        Returns:
            bool: True if any errors have been collected, False otherwise
        """
        return len(self.errors) > 0
    
    def get_errors(self) -> List[ValidationError]:
        """Get all errors.
        
        Returns:
            List[ValidationError]: Copy of the errors list
        """
        return self.errors.copy()
    
    def clear(self):
        """Clear all errors.
        
        Removes all collected errors from the collector.
        """
        self.errors.clear()
    
    def format_errors(self) -> str:
        """Format all errors into a help message.
        
        Creates a formatted error message that includes all collected errors
        and a suggestion to use --help for more information.
        
        Returns:
            str: Formatted error message, or empty string if no errors
            
        Example:
            >>> collector = ValidationErrorCollector()
            >>> collector.add_error("Invalid choice", argument="format", value="csv")
            >>> print(collector.format_errors())
            error: the following arguments had problems:
            <BLANKLINE>
              Invalid choice (argument format, value 'csv')
            <BLANKLINE>
            use --help for more information
        """
        if not self.errors:
            return ""
        
        lines = []
        lines.append("error: the following arguments had problems:")
        lines.append("")
        
        for error in self.errors:
            lines.append(f"  {error}")
        
        lines.append("")
        lines.append("use --help for more information")
        
        return "\n".join(lines)


def format_help(arg_specs: List[BaseArgSpec], 
                prog: Optional[str] = None,
                usage: Optional[str] = None,
                description: Optional[str] = None,
                epilog: Optional[str] = None) -> str:
    """Format a help message for the given argument specifications.
    
    Convenience function that creates a HelpFormatter and generates a complete
    help message for the provided argument specifications.
    
    Args:
        arg_specs: List of argument specifications to include in help
        prog: Program name (defaults to sys.argv[0] if available)
        usage: Custom usage string override (optional)
        description: Program description displayed after usage line (optional)
        epilog: Text to display after argument help section (optional)
        
    Returns:
        str: Complete formatted help message
        
    Example:
        >>> from argsclass.models import PositionalArgSpec, OptionArgSpec
        >>> specs = [
        ...     PositionalArgSpec(name="input", help_text="Input file"),
        ...     OptionArgSpec(name="output", help_text="Output file", aliases={"o"})
        ... ]
        >>> help_text = format_help(specs, prog="myapp", description="My application")
        >>> print(help_text)
    """
    formatter = HelpFormatter(prog=prog, usage=usage, description=description, epilog=epilog)
    return formatter.format_help(arg_specs)


def detect_help_flag(argv: List[str]) -> bool:
    """Detect if --help or -h flag is present in argv.
    
    Checks if any of the standard help flags (--help or -h) are present
    in the provided argument list.
    
    Args:
        argv: List of command line arguments to check
        
    Returns:
        bool: True if --help or -h is found, False otherwise
        
    Example:
        >>> detect_help_flag(["--help"])
        True
        >>> detect_help_flag(["-h"])
        True
        >>> detect_help_flag(["script.py", "--help"])
        True
        >>> detect_help_flag(["script.py", "--verbose"])
        False
    """
    help_flags = {'--help', '-h'}
    return any(arg in help_flags for arg in argv)


def remove_help_flags(argv: List[str]) -> List[str]:
    """Remove help flags from argv.
    
    Creates a new list with all help flags (--help and -h) removed from
    the original argument list.
    
    Args:
        argv: List of command line arguments
        
    Returns:
        List[str]: New list with help flags removed
        
    Example:
        >>> remove_help_flags(["--help"])
        []
        >>> remove_help_flags(["-h"])
        []
        >>> remove_help_flags(["script.py", "--help", "--verbose"])
        ["script.py", "--verbose"]
        >>> remove_help_flags(["script.py", "--verbose"])
        ["script.py", "--verbose"]
    """
    help_flags = {'--help', '-h'}
    return [arg for arg in argv if arg not in help_flags]