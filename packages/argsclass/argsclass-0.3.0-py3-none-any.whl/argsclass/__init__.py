"""Simple class-based argument parsing for python scripts."""

from .models import (
    BaseArgSpec, NamedArgSpec, PositionalArgSpec, OptionArgSpec, FlagArgSpec,
    Cardinality,
    ArgumentType, PrimitiveType
)
from .parser import ParserContext, PositionalArgumentParser, OptionArgumentParser, FlagArgumentParser, parse, args, parser, HelpRequested, ArgumentParsingError
from .descriptors import positional, option, flag
from .inspector import inspect_class, get_argspecs
from .ambiguity import AmbiguityError, detect_ambiguities, validate_no_ambiguities, is_ambiguous, get_ambiguity_resolution_suggestions
from .help import format_help, detect_help_flag, remove_help_flags, ValidationErrorCollector, ValidationError

__version__ = "0.3.0"
__all__ = [
    "BaseArgSpec", "NamedArgSpec", "PositionalArgSpec", "OptionArgSpec", "FlagArgSpec",
    "Cardinality",
    "ArgumentType", "PrimitiveType",
    "ParserContext", "PositionalArgumentParser", "OptionArgumentParser", "FlagArgumentParser", "parse", "args", "parser",
    "HelpRequested", "ArgumentParsingError",
    "positional", "option", "flag",
    "inspect_class", "get_argspecs",
    "AmbiguityError", "detect_ambiguities", "validate_no_ambiguities", "is_ambiguous", "get_ambiguity_resolution_suggestions",
    "format_help", "detect_help_flag", "remove_help_flags", "ValidationErrorCollector", "ValidationError"
]