"""Parser module for command line argument parsing.

This module provides the core parsing functionality for command line arguments,
including context management, argument-specific parsers, and high-level parsing
functions with help system integration.

Classes:
    ParserContext: Manages parsing state and argument consumption
    PositionalArgumentParser: Parses positional arguments
    OptionArgumentParser: Parses option arguments (--option value)
    FlagArgumentParser: Parses flag arguments (--flag)
    HelpRequested: Exception raised when help is requested
    ArgumentParsingError: Exception raised when parsing fails with errors

Functions:
    parse: Main parsing function for classes or argument specifications
    args: Class decorator for immediate argument parsing
    parser: Class decorator that adds a parse() method

Example:
    >>> from argsclass.parser import parse
    >>> from argsclass.models import PositionalArgSpec, OptionArgSpec, FlagArgSpec
    >>> 
    >>> specs = [
    ...     PositionalArgSpec(name="input", help_text="Input file"),
    ...     OptionArgSpec(name="output", help_text="Output file", aliases={"o"}),
    ...     FlagArgSpec(name="verbose", help_text="Verbose output", aliases={"v"})
    ... ]
    >>> 
    >>> try:
    ...     result = parse(specs, ["input.txt", "-o", "output.txt", "-v"])
    ...     print(f"Input: {result['input']}")
    ...     print(f"Output: {result['output']}")
    ...     print(f"Verbose: {result['verbose']}")
    ... except HelpRequested as e:
    ...     print(e.help_message)
    ...     sys.exit(0)
    ... except ArgumentParsingError as e:
    ...     print(e.error_message)
    ...     sys.exit(2)
"""

import inspect
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Type, TypeVar, Union, Callable
from .models import BaseArgSpec, PositionalArgSpec, FlagArgSpec, OptionArgSpec
from .help import ValidationErrorCollector, format_help, detect_help_flag, remove_help_flags

T = TypeVar('T')


class HelpRequested(Exception):
    """Exception raised when help is requested via --help flag.
    
    This exception is raised when the --help or -h flag is detected during
    argument parsing. It contains the formatted help message that should be
    displayed to the user.
    
    Attributes:
        help_message (str): The formatted help message to display
        
    Example:
        >>> try:
        ...     parse(specs, ["--help"])
        ... except HelpRequested as e:
        ...     print(e.help_message)
        ...     sys.exit(0)
    """
    
    def __init__(self, help_message: str):
        """Initialize help request exception.
        
        Args:
            help_message: The formatted help message to display
        """
        self.help_message = help_message
        super().__init__(help_message)


class ArgumentParsingError(Exception):
    """Exception raised when argument parsing fails with validation errors.
    
    This exception is raised when argument parsing encounters validation errors
    such as invalid values, missing required arguments, or unknown arguments.
    It contains both the error message describing the problems and an optional
    help message that can be displayed to guide the user.
    
    Attributes:
        error_message (str): The error message describing the problems
        help_message (Optional[str]): Optional help message to display
        
    Example:
        >>> try:
        ...     parse(specs, ["--unknown", "--port", "not_a_number"])
        ... except ArgumentParsingError as e:
        ...     print(e.error_message)
        ...     if e.help_message:
        ...         print()
        ...         print(e.help_message)
        ...     sys.exit(2)
    """
    
    def __init__(self, error_message: str, help_message: Optional[str] = None):
        """Initialize argument parsing error.
        
        Args:
            error_message: The error message describing the problems
            help_message: Optional help message to display
        """
        self.error_message = error_message
        self.help_message = help_message
        super().__init__(error_message)


class ParserContext:
    """Context for managing argument parsing state.
    
    This class manages the state during argument parsing, including the original
    and current argument lists, and provides a dictionary-like interface for
    storing parsed argument values.
    
    The context tracks which arguments have been consumed and provides methods
    to peek at, consume, and check for available arguments. It also stores
    the parsed values using a dictionary-like interface.
    
    Attributes:
        original_argv (List[str]): The original unmodified argument list
        current_argv (List[str]): The current argument list with consumed args removed
        _parsed_values (Dict[str, Any]): Dictionary storing parsed argument values
    
    Example:
        >>> context = ParserContext(["script.py", "input.txt", "--verbose"])
        >>> print(context.original_argv)
        ['script.py', 'input.txt', '--verbose']
        >>> print(context.current_argv)
        ['script.py', 'input.txt', '--verbose']
        >>> context["verbose"] = True
        >>> print(context["verbose"])
        True
    """
    
    def __init__(self, argv: List[str]):
        """Initialize parser context with original argv.
        
        Args:
            argv: List of command line arguments to parse
        """
        self._original_argv = argv.copy()
        self._current_argv = argv.copy()
        self._parsed_values: Dict[str, Any] = {}
    
    @property
    def original_argv(self) -> List[str]:
        """Get the original unaltered argv.
        
        Returns:
            List[str]: Copy of the original argument list
        """
        return self._original_argv.copy()
    
    @property
    def current_argv(self) -> List[str]:
        """Get the current unparsed argv.
        
        Returns:
            List[str]: Copy of the current argument list (with consumed args removed)
        """
        return self._current_argv.copy()
    
    def consume(self, count: int) -> List[str]:
        """Consume and return the first N arguments from current argv.
        
        Removes and returns the first `count` arguments from the current argv list.
        The consumed arguments are no longer available in current_argv.
        
        Args:
            count: Number of arguments to consume
            
        Returns:
            List[str]: List of consumed arguments
            
        Note:
            If count is 0 or negative, returns an empty list without modifying argv.
        """
        if count <= 0:
            return []
        
        consumed = self._current_argv[:count]
        self._current_argv = self._current_argv[count:]
        return consumed
    
    def peek(self, count: int) -> List[str]:
        """Peek at the first N arguments without consuming them.
        
        Returns the first `count` arguments without removing them from current_argv.
        This allows looking ahead at arguments without consuming them.
        
        Args:
            count: Number of arguments to peek at
            
        Returns:
            List[str]: List of arguments (empty if count <= 0)
        """
        if count <= 0:
            return []
        return self._current_argv[:count]
    
    def has(self, count: int = 1) -> bool:
        """Check if there are at least N arguments available.
        
        Args:
            count: Minimum number of arguments to check for (default: 1)
            
        Returns:
            bool: True if at least `count` arguments are available
        """
        return len(self._current_argv) >= count
    
    
    def __getitem__(self, key: str) -> Any:
        """Get a parsed value using dictionary-style access.
        
        Args:
            key: Argument name to retrieve
            
        Returns:
            Any: The parsed value for the argument
            
        Raises:
            KeyError: If the key is not found
        """
        return self._parsed_values[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set a parsed value using dictionary-style access.
        
        Args:
            key: Argument name to set
            value: Value to store for the argument
        """
        self._parsed_values[key] = value
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists in parsed values.
        
        Args:
            key: Argument name to check
            
        Returns:
            bool: True if the key exists in parsed values
        """
        return key in self._parsed_values
    
    def __len__(self) -> int:
        """Get the number of parsed values.
        
        Returns:
            int: Number of parsed argument values
        """
        return len(self._parsed_values)
    
    def keys(self):
        """Get all keys in parsed values.
        
        Returns:
            Keys view of parsed values dictionary
        """
        return self._parsed_values.keys()
    
    def values(self):
        """Get all values in parsed values.
        
        Returns:
            Values view of parsed values dictionary
        """
        return self._parsed_values.values()
    
    def items(self):
        """Get all key-value pairs in parsed values.
        
        Returns:
            Items view of parsed values dictionary
        """
        return self._parsed_values.items()


class ArgumentParser(Protocol):
    """Protocol for argument parsers.
    
    This protocol defines the interface that all argument parsers must implement.
    Each parser is responsible for parsing a specific type of argument (positional,
    option, or flag) and updating the parsing context with the results.
    """
    
    def parse(self, spec: BaseArgSpec, context: ParserContext, error_collector: ValidationErrorCollector) -> None:
        """Parse an argument specification and update the context.
        
        Args:
            spec: The argument specification to parse
            context: The parsing context to update
            error_collector: Collector for validation errors
        """
        ...


class PositionalArgumentParser:
    """Parser for positional arguments.
    
    This parser handles positional arguments, which are arguments that don't
    start with a dash and are identified by their position in the argument list.
    It supports various cardinalities (single, multiple, optional, etc.) and
    type conversion.
    
    Example:
        >>> parser = PositionalArgumentParser()
        >>> spec = PositionalArgSpec(name="input", help_text="Input file")
        >>> context = ParserContext(["input.txt"])
        >>> error_collector = ValidationErrorCollector()
        >>> parser.parse(spec, context, error_collector)
        >>> print(context["input"])
        input.txt
    """
    
    def parse(self, spec: PositionalArgSpec, context: ParserContext, error_collector: ValidationErrorCollector) -> None:
        """Parse a positional argument from the current argv.
        
        Parses positional arguments from the current argv list, handling cardinality
        requirements, type conversion, and validation. Collects errors instead of
        raising exceptions immediately.
        
        Args:
            spec: Positional argument specification
            context: Parsing context to update
            error_collector: Collector for validation errors
        """
        if not isinstance(spec, PositionalArgSpec):
            error_collector.add_error(f"Expected PositionalArgSpec, got {type(spec)}")
            return
        
        # Find all positional arguments (those that don't start with -)
        # We need to collect all positional args, not just consecutive ones
        positional_args = [arg for arg in context.current_argv if not arg.startswith('-')]
        
        # Determine how many arguments to consume
        min_args = spec.cardinality.min
        max_args = spec.cardinality.max
        
        # Check if we have enough positional arguments
        available_positional = len(positional_args)
        
        if available_positional < min_args:
            if spec.default is not None:
                # Use default value
                context[spec.destination] = spec.default
                return
            else:
                error_collector.add_error(
                    f"Not enough positional arguments for '{spec.name}'. Expected at least {min_args}, got {available_positional}",
                    argument=spec.name
                )
                return
        
        # Determine how many to consume
        if max_args is None:
            # Consume all available positional arguments
            consume_count = available_positional
        else:
            # Consume up to max_args
            consume_count = min(available_positional, max_args)
        
        # Consume the positional arguments (skip non-positional ones)
        raw_values = []
        consumed_count = 0
        remaining_argv = []
        
        for arg in context.current_argv:
            if not arg.startswith('-') and consumed_count < consume_count:
                raw_values.append(arg)
                consumed_count += 1
            else:
                remaining_argv.append(arg)
        
        # Update the context with remaining argv
        context._current_argv = remaining_argv
        
        # Convert and validate values
        converted_values = []
        for raw_value in raw_values:
            try:
                converted_value = spec.convert_value(raw_value)
                converted_values.append(converted_value)
            except Exception as e:
                error_collector.add_error(
                    f"Error parsing argument '{spec.name}': {e}",
                    argument=spec.name,
                    value=raw_value
                )
                return
        
        # Handle single vs multiple values
        if spec.cardinality.max == 1:
            # Single value
            if converted_values:
                context[spec.destination] = converted_values[0]
            else:
                context[spec.destination] = spec.default
        else:
            # Multiple values
            context[spec.destination] = converted_values


class FlagArgumentParser:
    """Parser for flag arguments (boolean switches).
    
    This parser handles flag arguments, which are boolean switches that don't
    take values. Flags can be present (True) or absent (False). The parser
    supports aliases and explicit boolean values (--flag=true, --flag=false).
    
    Example:
        >>> parser = FlagArgumentParser()
        >>> spec = FlagArgSpec(name="verbose", help_text="Verbose output", aliases={"v"})
        >>> context = ParserContext(["--verbose"])
        >>> error_collector = ValidationErrorCollector()
        >>> parser.parse(spec, context, error_collector)
        >>> print(context["verbose"])
        True
    """
    
    def parse(self, spec: FlagArgSpec, context: ParserContext, error_collector: ValidationErrorCollector) -> None:
        """Parse a flag argument from the current argv.
        
        Parses flag arguments from the current argv list, handling aliases and
        explicit boolean values. Collects errors instead of raising exceptions
        immediately.
        
        Args:
            spec: Flag argument specification
            context: Parsing context to update
            error_collector: Collector for validation errors
        """
        if not isinstance(spec, FlagArgSpec):
            error_collector.add_error(f"Expected FlagArgSpec, got {type(spec)}")
            return
        
        # Check if the flag or any of its aliases are present in the argv
        flag_present = False
        remaining_argv = []
        
        # Build list of all possible flag names (including aliases)
        all_flag_names = {f"--{spec.name}"}
        for alias in spec.aliases:
            if len(alias) == 1:
                # Single character aliases get single dash
                all_flag_names.add(f"-{alias}")
            else:
                # Multi-character aliases can use both single and double dash
                all_flag_names.add(f"-{alias}")
                all_flag_names.add(f"--{alias}")
        
        # Process each argument in the current argv
        i = 0
        while i < len(context.current_argv):
            arg = context.current_argv[i]
            
            if arg in all_flag_names:
                # Flag is present, check for explicit value
                flag_present = True
                
                # Check if next argument is a boolean value
                if i + 1 < len(context.current_argv):
                    next_arg = context.current_argv[i + 1]
                    if next_arg.lower() in ('true', 'false'):
                        # Explicit boolean value provided
                        if next_arg.lower() == 'false':
                            flag_present = False
                        # Skip the boolean value argument
                        i += 1
                    else:
                        # Non-boolean value, treat as flag present but don't consume the value
                        # This allows the value to be used by other parsers (like positional args)
                        pass
                # Don't add this argument to remaining_argv (consume it)
            elif '=' in arg:
                # Check for --flag=true or --flag=false format
                flag_found = False
                for flag_name in all_flag_names:
                    if arg.startswith(flag_name + '='):
                        # Extract the value after =
                        value_str = arg[len(flag_name) + 1:]
                        if value_str.lower() in ('true', 'false'):
                            if value_str.lower() == 'true':
                                flag_present = True
                            else:  # false
                                flag_present = False
                        else:
                            # Non-boolean value, treat as flag present
                            flag_present = True
                        flag_found = True
                        # Don't add this argument to remaining_argv (consume it)
                        break
                
                if not flag_found:
                    # Not our flag, keep it in the remaining argv
                    remaining_argv.append(arg)
            else:
                # Not our flag, keep it in the remaining argv
                remaining_argv.append(arg)
            
            i += 1
        
        # Update the context with remaining argv (flags consumed)
        context._current_argv = remaining_argv
        
        # Set the flag value
        if flag_present:
            context[spec.destination] = True
        else:
            context[spec.destination] = spec.default


class OptionArgumentParser:
    """Parser for option arguments (named arguments with values).
    
    This parser handles option arguments, which are named arguments that take
    values (e.g., --output file.txt, -o file.txt). It supports aliases, various
    cardinalities, type conversion, and both space-separated and equals-separated
    formats (--option=value).
    
    Example:
        >>> parser = OptionArgumentParser()
        >>> spec = OptionArgSpec(name="output", help_text="Output file", aliases={"o"})
        >>> context = ParserContext(["--output", "file.txt"])
        >>> error_collector = ValidationErrorCollector()
        >>> parser.parse(spec, context, error_collector)
        >>> print(context["output"])
        file.txt
    """
    
    def parse(self, spec: OptionArgSpec, context: ParserContext, error_collector: ValidationErrorCollector) -> None:
        """Parse an option argument from the current argv.
        
        Parses option arguments from the current argv list, handling aliases,
        cardinality requirements, type conversion, and validation. Collects
        errors instead of raising exceptions immediately.
        
        Args:
            spec: Option argument specification
            context: Parsing context to update
            error_collector: Collector for validation errors
        """
        if not isinstance(spec, OptionArgSpec):
            error_collector.add_error(f"Expected OptionArgSpec, got {type(spec)}")
            return
        
        # Build list of all possible option names (including aliases)
        all_option_names = {f"--{spec.name}"}
        for alias in spec.aliases:
            if len(alias) == 1:
                # Single character aliases get single dash
                all_option_names.add(f"-{alias}")
            else:
                # Multi-character aliases can use both single and double dash
                all_option_names.add(f"-{alias}")
                all_option_names.add(f"--{alias}")
        
        # Track found values
        found_values = []
        remaining_argv = []
        
        # Process each argument in the current argv
        i = 0
        while i < len(context.current_argv):
            arg = context.current_argv[i]
            
            if arg in all_option_names:
                # Option is present, look for its value
                if i + 1 < len(context.current_argv):
                    # Check if next argument is a value (not another option)
                    next_arg = context.current_argv[i + 1]
                    if not next_arg.startswith('-'):
                        # Next argument is a value
                        found_values.append(next_arg)
                        # Skip both the option and its value
                        i += 2
                        continue
                    else:
                        # Next argument is another option, this option has no value
                        error_collector.add_error(
                            f"Option '{arg}' requires a value",
                            argument=arg
                        )
                        return
                else:
                    # No more arguments, this option has no value
                    error_collector.add_error(
                        f"Option '{arg}' requires a value",
                        argument=arg
                    )
                    return
                
                # Don't add this argument to remaining_argv (consume it)
                i += 1
            elif '=' in arg:
                # Check for --option=value format
                option_found = False
                for option_name in all_option_names:
                    if arg.startswith(option_name + '='):
                        # Extract the value after =
                        value_str = arg[len(option_name) + 1:]
                        found_values.append(value_str)
                        option_found = True
                        # Don't add this argument to remaining_argv (consume it)
                        break
                
                if not option_found:
                    # Not our option, keep it in the remaining argv
                    remaining_argv.append(arg)
                i += 1
            else:
                # Not our option, keep it in the remaining argv
                remaining_argv.append(arg)
                i += 1
        
        # Update the context with remaining argv (options consumed)
        context._current_argv = remaining_argv
        
        # Validate cardinality and convert values
        min_values = spec.cardinality.min
        max_values = spec.cardinality.max
        
        if len(found_values) < min_values:
            if spec.default is not None:
                # Use default value
                context[spec.destination] = spec.default
                return
            else:
                error_collector.add_error(
                    f"Not enough values for option '{spec.name}'. Expected at least {min_values}, got {len(found_values)}",
                    argument=spec.name
                )
                return
        
        # Determine how many values to use
        if max_values is None:
            # Use all found values
            values_to_use = found_values
        else:
            # Use up to max_values
            values_to_use = found_values[:max_values]
        
        # Convert and validate values
        converted_values = []
        for raw_value in values_to_use:
            try:
                converted_value = spec.convert_value(raw_value)
                converted_values.append(converted_value)
            except Exception as e:
                error_collector.add_error(
                    f"Error parsing option '{spec.name}': {e}",
                    argument=spec.name,
                    value=raw_value
                )
                return
        
        # Handle single vs multiple values
        if spec.cardinality.max == 1:
            # Single value
            if converted_values:
                context[spec.destination] = converted_values[0]
            else:
                context[spec.destination] = spec.default
        else:
            # Multiple values
            context[spec.destination] = converted_values


def parse(arg_specs_or_class, argv: Optional[List[str]] = None, validate_ambiguities: bool = True,
          prog: Optional[str] = None, description: Optional[str] = None, epilog: Optional[str] = None,
          ignore_unknown: bool = False) -> Any:
    """Parse command line arguments and return a class instance or dictionary.
    
    This is the main parsing function that handles both class-based and specification-based
    argument parsing. It automatically detects help flags, validates arguments, and
    provides comprehensive error reporting.
    
    Args:
        arg_specs_or_class: Either a list of argument specifications (List[BaseArgSpec]) 
                           or a class that can be inspected to generate ArgSpec objects
        argv: Command line arguments to parse (defaults to sys.argv)
        validate_ambiguities: Whether to validate for ambiguous configurations (default: True)
        prog: Program name for help messages (defaults to sys.argv[0])
        description: Program description for help messages
        epilog: Text to display after argument help
        ignore_unknown: Whether to ignore unknown arguments instead of raising errors (default: False)
        
    Returns:
        If arg_specs_or_class is a class: An instance of that class with parsed argument values
        If arg_specs_or_class is a list: Dictionary of parsed argument values keyed by destination names
        
    Raises:
        HelpRequested: If --help flag is detected (contains help_message attribute)
        ArgumentParsingError: If parsing fails with validation errors (contains error_message and help_message)
        AmbiguityError: If ambiguous argument configurations are detected (when validate_ambiguities=True)
    
    Example:
        >>> # Using with argument specifications
        >>> specs = [
        ...     PositionalArgSpec(name="input", help_text="Input file"),
        ...     OptionArgSpec(name="output", help_text="Output file", aliases={"o"}),
        ...     FlagArgSpec(name="verbose", help_text="Verbose output", aliases={"v"})
        ... ]
        >>> result = parse(specs, ["input.txt", "-o", "output.txt", "-v"])
        >>> print(result["input"], result["output"], result["verbose"])
        input.txt output.txt True
        
        >>> # Using with a class
        >>> class Args:
        ...     input_file: str = "input.txt"
        ...     verbose: bool
        >>> args = parse(Args, ["--verbose"])
        >>> print(args.input_file, args.verbose)
        input.txt True
    """
    # Default argv to sys.argv if not provided
    if argv is None:
        argv = sys.argv
    
    # Convert class to ArgSpec list if needed
    if isinstance(arg_specs_or_class, list):
        arg_specs = arg_specs_or_class
        is_class = False
    else:
        # Assume it's a class that can be inspected
        from .inspector import inspect_class
        arg_specs = inspect_class(arg_specs_or_class)
        is_class = True
        cls = arg_specs_or_class
    
    # Check for help flag before processing
    if detect_help_flag(argv):
        help_message = format_help(arg_specs, prog=prog, description=description, epilog=epilog)
        raise HelpRequested(help_message)
    
    # Validate for ambiguities if requested
    if validate_ambiguities:
        from .ambiguity import validate_no_ambiguities
        validate_no_ambiguities(arg_specs)
    
    # Skip the script name (first argument) if present
    if argv and argv[0].endswith('.py'):
        argv = argv[1:]
    
    # Remove help flags from argv
    argv = remove_help_flags(argv)
    
    context = ParserContext(argv)
    error_collector = ValidationErrorCollector()
    
    # Create parsers for different argument types
    positional_parser = PositionalArgumentParser()
    flag_parser = FlagArgumentParser()
    option_parser = OptionArgumentParser()
    
    for spec in arg_specs:
        if isinstance(spec, PositionalArgSpec):
            positional_parser.parse(spec, context, error_collector)
        elif isinstance(spec, FlagArgSpec):
            flag_parser.parse(spec, context, error_collector)
        elif isinstance(spec, OptionArgSpec):
            option_parser.parse(spec, context, error_collector)
        else:
            error_collector.add_error(f"Unsupported argument type: {type(spec)}")
    
    # Check for unknown arguments (unless ignore_unknown is True)
    if context.current_argv and not ignore_unknown:
        for unknown_arg in context.current_argv:
            if unknown_arg.startswith('-'):
                error_collector.add_error(f"unrecognized arguments: {unknown_arg}", argument=unknown_arg)
    
    # If there are errors, raise an exception with help message
    if error_collector.has_errors():
        help_message = format_help(arg_specs, prog=prog, description=description, epilog=epilog)
        error_message = error_collector.format_errors()
        raise ArgumentParsingError(error_message, help_message)
    
    # Return class instance if a class was provided, otherwise return dict
    if is_class:
        # Ensure the class has @dataclass decorator if it doesn't have a custom __init__
        cls = _ensure_dataclass(cls)
        
        # Create an instance of the class with the parsed values
        try:
            # Check if the class is a dataclass with init=False
            if hasattr(cls, '__dataclass_fields__'):
                # Check if it's a dataclass with init=False by looking at the __init__ signature
                init_signature = inspect.signature(cls.__init__)
                # For init=False dataclasses, the signature is (self, /, *args, **kwargs)
                # For init=True dataclasses, the signature has specific field parameters
                if len(init_signature.parameters) == 3 and 'args' in init_signature.parameters and 'kwargs' in init_signature.parameters:
                    # It's a dataclass with init=False, manually set attributes
                    instance = object.__new__(cls)
                    for field_name, value in dict(context).items():
                        setattr(instance, field_name, value)
                    return instance
            
            # Regular class or dataclass with init=True, use normal instantiation
            return cls(**dict(context))
        except TypeError as e:
            # Provide more helpful error message
            help_message = format_help(arg_specs, prog=prog, description=description, epilog=epilog)
            error_message = f"Failed to create instance of {cls.__name__} with parsed values: {e}"
            raise ArgumentParsingError(error_message, help_message)
    else:
        # Return dictionary for backward compatibility with ArgSpec lists
        return dict(context)


def _ensure_dataclass(cls: Type[T]) -> Type[T]:
    """Ensure a class has the @dataclass decorator applied.
    
    This function checks if a class already has a custom __init__ method or
    is already a dataclass. If not, it applies the @dataclass decorator with
    init=False to avoid field ordering issues.
    
    Args:
        cls: The class to check and potentially modify
        
    Returns:
        Type[T]: The class with @dataclass decorator applied if needed
        
    Note:
        The function uses init=False to avoid field ordering issues and handles
        initialization manually in the parse function.
    """
    # Check if the class already has __init__ method
    if hasattr(cls, '__init__') and cls.__init__ is not object.__init__:
        # Class already has a custom __init__, don't modify it
        return cls
    
    # Check if the class is already a dataclass
    if hasattr(cls, '__dataclass_fields__'):
        return cls
    
    # Apply @dataclass decorator with init=False to avoid field ordering issues
    # We'll handle initialization manually in the parse function
    return dataclass(init=False)(cls)


def args(
    cls_or_argv: Union[Type[T], Optional[List[str]]] = None,
    validate_ambiguities: bool = True,
    program_name: Optional[str] = None,
    argv: Optional[List[str]] = None,
    description: Optional[str] = None,
    epilog: Optional[str] = None,
    ignore_unknown: bool = False
) -> Union[T, Callable[[Type[T]], T]]:
    """Class decorator that automatically parses command line arguments and returns an instance.
    
    This decorator transforms a class into an instance with parsed command line arguments.
    The class name becomes a reference to the parsed instance. It automatically handles
    help requests and validation errors by printing messages and exiting with appropriate codes.
    
    Supports both @args and @args() syntax:
    - @args: Uses default options (sys.argv, validate_ambiguities=True)
    - @args(): Same as @args
    - @args(program_name="myapp"): Custom options
    
    Args:
        cls_or_argv: Either a class (when used as @args) or argv list (when used as @args(...))
        validate_ambiguities: Whether to validate for ambiguous configurations (default: True)
        program_name: Override program name for help text (defaults to script name)
        argv: Command line arguments to parse (defaults to sys.argv)
        description: Program description for help messages
        epilog: Text to display after argument help
        ignore_unknown: Whether to ignore unknown arguments instead of raising errors (default: False)
        
    Returns:
        Either a parsed instance (when used as @args) or a decorator function (when used as @args(...))
        
    Note:
        This decorator automatically handles help requests (--help) and validation errors
        by printing appropriate messages and exiting with codes 0 (help) or 2 (error).
        
    Example:
        @args
        class Args:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
        
        # Args is now an instance with parsed values
        print(Args.input_file)  # Access parsed values directly
        print(Args.verbose)
        
    Example with options:
        @args(program_name="myapp", validate_ambiguities=False)
        class Config:
            port: int = 8080
            debug: bool
    """
    # Check if the first argument is a class (no brackets usage)
    if cls_or_argv is not None and inspect.isclass(cls_or_argv):
        # @args usage (no brackets) - cls_or_argv is actually the class
        cls = cls_or_argv
        method_argv = argv  # Use provided argv or None (which will default to sys.argv)
        
        # Store the original class before any modifications
        original_class = cls
        
        try:
            # Parse the arguments and create an instance
            instance = parse(cls, method_argv, validate_ambiguities, 
                           prog=program_name, description=description, epilog=epilog, ignore_unknown=ignore_unknown)
        except HelpRequested as e:
            print(e.help_message)
            sys.exit(0)
        except ArgumentParsingError as e:
            print(e.error_message)
            if e.help_message:
                print()
                print(e.help_message)
            sys.exit(2)
        
        # Store the original class for introspection
        instance._original_class = original_class
        
        # Add some useful attributes
        instance._program_name = program_name or (sys.argv[0] if sys.argv else "program")
        instance._validate_ambiguities = validate_ambiguities
        
        return instance
    
    # @args(...) usage (with brackets) - cls_or_argv is actually argv
    decorator_argv = cls_or_argv
    
    def decorator(cls: Type[T]) -> T:
        """The actual decorator that transforms the class into an instance."""
        # Use provided argv or decorator argv or None (which will default to sys.argv)
        method_argv = argv if argv is not None else decorator_argv
        
        # Store the original class before any modifications
        original_class = cls
        
        try:
            # Parse the arguments and create an instance
            instance = parse(original_class, method_argv, validate_ambiguities,
                           prog=program_name, description=description, epilog=epilog, ignore_unknown=ignore_unknown)
        except HelpRequested as e:
            print(e.help_message)
            sys.exit(0)
        except ArgumentParsingError as e:
            print(e.error_message)
            if e.help_message:
                print()
                print(e.help_message)
            sys.exit(2)
        
        # Store the original class for introspection
        instance._original_class = original_class
        
        # Add some useful attributes
        instance._program_name = program_name or (method_argv[0] if method_argv else sys.argv[0]) if (method_argv or sys.argv) else "program"
        instance._validate_ambiguities = validate_ambiguities
        
        return instance
    
    return decorator


def parser(
    cls_or_argv: Union[Type[T], Optional[List[str]]] = None,
    validate_ambiguities: bool = True,
    program_name: Optional[str] = None,
    argv: Optional[List[str]] = None,
    description: Optional[str] = None,
    epilog: Optional[str] = None,
    ignore_unknown: bool = False
) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
    """Class decorator that adds a static parse() method to the class.
    
    This decorator transforms a class by adding a static parse() method that
    returns an instance with parsed command line arguments. Unlike @args,
    this doesn't parse immediately - it adds the parse() method for later use.
    The parse() method automatically handles help requests and validation errors.
    
    Supports both @parser and @parser() syntax:
    - @parser: Adds parse() method with default options
    - @parser(): Same as @parser
    - @parser(program_name="myapp"): Custom options for the parse() method
    
    Args:
        cls_or_argv: Either a class (when used as @parser) or argv list (when used as @parser(...))
        validate_ambiguities: Whether to validate for ambiguous configurations (default: True)
        program_name: Override program name for help text (defaults to script name)
        argv: Command line arguments to parse (defaults to sys.argv)
        description: Program description for help messages
        epilog: Text to display after argument help
        ignore_unknown: Whether to ignore unknown arguments instead of raising errors (default: False)
        
    Returns:
        Either the modified class (when used as @parser) or a decorator function (when used as @parser(...))
        
    Note:
        The added parse() method automatically handles help requests (--help) and validation errors
        by printing appropriate messages and exiting with codes 0 (help) or 2 (error).
        
    Example:
        @parser
        class Args:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
        
        # Parse when you want to
        args = Args.parse()
        print(args.input_file)  # Access parsed values
        
    Example with options:
        @parser(program_name="myapp", validate_ambiguities=False)
        class Config:
            port: int = 8080
            debug: bool
        
        # Parse with custom options
        config = Config.parse()
    """
    # Check if the first argument is a class (no brackets usage)
    if cls_or_argv is not None and inspect.isclass(cls_or_argv):
        # @parser usage (no brackets) - cls_or_argv is actually the class
        cls = cls_or_argv
        decorator_argv = argv  # Use provided argv or None (which will default to sys.argv)
        
        # Store the original class before any modifications
        original_class = cls
        
        # Add the parse method to the class
        @staticmethod
        def parse_method(custom_argv: Optional[List[str]] = None) -> T:
            """Static method that parses command line arguments and returns an instance."""
            # Use custom_argv if provided, otherwise use the decorator's argv, otherwise use sys.argv
            method_argv = custom_argv if custom_argv is not None else decorator_argv
            
            try:
                # Parse the arguments and create an instance
                instance = parse(original_class, method_argv, validate_ambiguities,
                               prog=program_name, description=description, epilog=epilog)
            except HelpRequested as e:
                print(e.help_message)
                sys.exit(0)
            except ArgumentParsingError as e:
                print(e.error_message)
                if e.help_message:
                    print()
                    print(e.help_message)
                sys.exit(2)
            
            # Store the original class for introspection
            instance._original_class = original_class
            
            # Add some useful attributes
            instance._program_name = program_name or (method_argv[0] if method_argv else sys.argv[0]) if (method_argv or sys.argv) else "program"
            instance._validate_ambiguities = validate_ambiguities
            
            return instance
        
        # Add the static method to the class
        cls.parse = parse_method
        
        return cls
    
    # @parser(...) usage (with brackets) - cls_or_argv is actually argv
    decorator_argv = cls_or_argv
    
    def decorator(cls: Type[T]) -> Type[T]:
        """The actual decorator that adds the parse method to the class."""
        # Store the original class before any modifications
        original_class = cls
        
        # Add the parse method to the class
        @staticmethod
        def parse_method(custom_argv: Optional[List[str]] = None) -> T:
            """Static method that parses command line arguments and returns an instance."""
            # Use custom_argv if provided, otherwise use the decorator's argv, otherwise use sys.argv
            method_argv = custom_argv if custom_argv is not None else (argv if argv is not None else decorator_argv)
            
            try:
                # Parse the arguments and create an instance
                instance = parse(original_class, method_argv, validate_ambiguities,
                               prog=program_name, description=description, epilog=epilog)
            except HelpRequested as e:
                print(e.help_message)
                sys.exit(0)
            except ArgumentParsingError as e:
                print(e.error_message)
                if e.help_message:
                    print()
                    print(e.help_message)
                sys.exit(2)
            
            # Store the original class for introspection
            instance._original_class = original_class
            
            # Add some useful attributes
            instance._program_name = program_name or (method_argv[0] if method_argv else sys.argv[0]) if (method_argv or sys.argv) else "program"
            instance._validate_ambiguities = validate_ambiguities
            
            return instance
        
        # Add the static method to the class
        cls.parse = parse_method
        
        return cls
    
    return decorator

