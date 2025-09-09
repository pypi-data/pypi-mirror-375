"""Ambiguity detection for argument specifications."""

from typing import List, Set, Tuple
from .models import BaseArgSpec, PositionalArgSpec, OptionArgSpec, FlagArgSpec, Cardinality


class AmbiguityError(Exception):
    """Raised when argument specifications create ambiguous parsing scenarios."""
    pass


def detect_ambiguities(specs_or_class) -> List[str]:
    """Detect potential ambiguities in argument specifications.
    
    Args:
        specs_or_class: Either a list of argument specifications or a class to analyze
        
    Returns:
        List of ambiguity warning messages (empty if no ambiguities found)
    """
    # Convert class to ArgSpec list if needed
    if isinstance(specs_or_class, list):
        specs = specs_or_class
    else:
        # Assume it's a class that can be inspected
        from .inspector import inspect_class
        specs = inspect_class(specs_or_class)
    
    warnings = []
    
    # Check for multiple positional arguments with non-specific cardinality
    positional_warnings = _check_positional_ambiguities(specs)
    warnings.extend(positional_warnings)
    
    # Check for multiple option arguments with non-specific cardinality
    option_warnings = _check_option_ambiguities(specs)
    warnings.extend(option_warnings)
    
    # Check for mixed positional/option ambiguities
    mixed_warnings = _check_mixed_ambiguities(specs)
    warnings.extend(mixed_warnings)
    
    return warnings


def validate_no_ambiguities(specs_or_class) -> None:
    """Validate that argument specifications don't create ambiguities.
    
    Args:
        specs_or_class: Either a list of argument specifications or a class to validate
        
    Raises:
        AmbiguityError: If ambiguities are detected
    """
    warnings = detect_ambiguities(specs_or_class)
    if warnings:
        raise AmbiguityError(
            "Ambiguous argument configuration detected:\n" + 
            "\n".join(f"  - {warning}" for warning in warnings)
        )


def _check_positional_ambiguities(specs: List[BaseArgSpec]) -> List[str]:
    """Check for ambiguities between positional arguments."""
    warnings = []
    
    # Find all positional arguments
    positional_specs = [spec for spec in specs if isinstance(spec, PositionalArgSpec)]
    
    if len(positional_specs) <= 1:
        return warnings
    
    # Check for multiple positionals with non-specific cardinality
    non_specific_positionals = []
    for spec in positional_specs:
        if _has_non_specific_cardinality(spec.cardinality):
            non_specific_positionals.append(spec)
    
    if len(non_specific_positionals) > 1:
        names = [spec.name for spec in non_specific_positionals]
        warnings.append(
            f"Multiple positional arguments with non-specific cardinality: {', '.join(names)}. "
            f"This can cause ambiguity about which argument consumes which values."
        )
    
    # Check for positionals with non-specific cardinality after positionals with specific cardinality
    specific_positionals = [spec for spec in positional_specs if not _has_non_specific_cardinality(spec.cardinality)]
    if specific_positionals and non_specific_positionals:
        # Find the order of positionals
        spec_order = {spec: i for i, spec in enumerate(specs) if isinstance(spec, PositionalArgSpec)}
        
        # Check if any non-specific positional comes before a specific one
        for non_specific in non_specific_positionals:
            non_specific_index = spec_order[non_specific]
            for specific in specific_positionals:
                specific_index = spec_order[specific]
                if non_specific_index < specific_index:
                    warnings.append(
                        f"Positional argument '{non_specific.name}' with non-specific cardinality "
                        f"comes before '{specific.name}' with specific cardinality. "
                        f"This can cause ambiguity about value consumption order."
                    )
    
    return warnings


def _check_option_ambiguities(specs: List[BaseArgSpec]) -> List[str]:
    """Check for ambiguities between option arguments."""
    warnings = []
    
    # Find all option arguments
    option_specs = [spec for spec in specs if isinstance(spec, OptionArgSpec)]
    
    if len(option_specs) <= 1:
        return warnings
    
    # Check for multiple options with non-specific cardinality
    non_specific_options = []
    for spec in option_specs:
        if _has_non_specific_cardinality(spec.cardinality):
            non_specific_options.append(spec)
    
    if len(non_specific_options) > 1:
        names = [spec.name for spec in non_specific_options]
        warnings.append(
            f"Multiple option arguments with non-specific cardinality: {', '.join(names)}. "
            f"This can cause ambiguity about which option consumes which values."
        )
    
    return warnings


def _check_mixed_ambiguities(specs: List[BaseArgSpec]) -> List[str]:
    """Check for ambiguities between positional and option arguments."""
    warnings = []
    
    # Mixed positional and option arguments with non-specific cardinality are NOT ambiguous
    # because they are parsed differently:
    # - Options are parsed by name (--option value)
    # - Positionals are parsed by position
    # 
    # The only real ambiguity occurs when there are multiple positional arguments
    # with non-specific cardinality, which is already handled in _check_positional_ambiguities
    
    return warnings


def _has_non_specific_cardinality(cardinality: Cardinality) -> bool:
    """Check if a cardinality is non-specific (can consume variable number of values)."""
    # Non-specific cardinalities are those where max is None (unlimited)
    return cardinality.max is None


def get_ambiguity_resolution_suggestions(specs_or_class) -> List[str]:
    """Get suggestions for resolving ambiguities in argument specifications.
    
    Args:
        specs_or_class: Either a list of argument specifications or a class to analyze
        
    Returns:
        List of suggestions for resolving ambiguities
    """
    # Convert class to ArgSpec list if needed
    if isinstance(specs_or_class, list):
        specs = specs_or_class
    else:
        # Assume it's a class that can be inspected
        from .inspector import inspect_class
        specs = inspect_class(specs_or_class)
    
    suggestions = []
    warnings = detect_ambiguities(specs)
    
    if not warnings:
        return suggestions
    
    # Find all non-specific cardinality arguments
    non_specific_positionals = [
        spec for spec in specs 
        if isinstance(spec, PositionalArgSpec) and _has_non_specific_cardinality(spec.cardinality)
    ]
    
    non_specific_options = [
        spec for spec in specs 
        if isinstance(spec, OptionArgSpec) and _has_non_specific_cardinality(spec.cardinality)
    ]
    
    if non_specific_positionals:
        suggestions.append(
            "For positional arguments with non-specific cardinality, consider:"
        )
        for spec in non_specific_positionals:
            suggestions.append(
                f"  - Use specific cardinality for '{spec.name}' (e.g., Cardinality.exactly(n))"
            )
            suggestions.append(
                f"  - Use Cardinality.zero_or_one() for '{spec.name}' if only one value is expected"
            )
            suggestions.append(
                f"  - Reorder arguments so '{spec.name}' comes last among positionals"
            )
    
    if non_specific_positionals:
        suggestions.append(
            "For positional arguments with non-specific cardinality, consider:"
        )
        for spec in non_specific_positionals:
            suggestions.append(
                f"  - Use specific cardinality for '{spec.name}' (e.g., Cardinality.exactly(n))"
            )
            suggestions.append(
                f"  - Use Cardinality.zero_or_one() for '{spec.name}' if only one value is expected"
            )
            suggestions.append(
                f"  - Place '{spec.name}' at the end of positional arguments to avoid consumption conflicts"
            )
    
    if non_specific_options:
        suggestions.append(
            "For option arguments with non-specific cardinality, consider:"
        )
        for spec in non_specific_options:
            suggestions.append(
                f"  - Use specific cardinality for '{spec.name}' (e.g., Cardinality.exactly(n))"
            )
            suggestions.append(
                f"  - Use Cardinality.zero_or_one() for '{spec.name}' if only one value is expected"
            )
            suggestions.append(
                f"  - Use repeated option names (--{spec.name} val1 --{spec.name} val2) instead of consecutive values"
            )
    
    # Note: Mixed positional and option arguments with non-specific cardinality are NOT ambiguous
    # because they are parsed differently (by name vs by position)
    
    return suggestions


def is_ambiguous(specs_or_class) -> bool:
    """Check if argument specifications create ambiguous parsing scenarios.
    
    Args:
        specs_or_class: Either a list of argument specifications or a class to check
        
    Returns:
        True if ambiguities are detected, False otherwise
    """
    return len(detect_ambiguities(specs_or_class)) > 0