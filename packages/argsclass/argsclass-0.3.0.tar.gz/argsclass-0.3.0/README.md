# argsclass
Simple class-based argument parsing for python scripts

## Class Inspection

The `inspect_class` function allows you to convert a class definition into a list of `ArgSpec` objects. This enables you to define your command-line arguments using class attributes with type hints and descriptors.

### Basic Usage

```python
from argsclass import inspect_class, positional

class Args:
    flag: bool                    # Boolean attributes become flags
    option: str = "default"       # Attributes with defaults become options
    Name: str = positional(help_text="foo")  # Use descriptors for positional args

specs = inspect_class(Args)
# Returns: [FlagArgSpec("flag"), OptionArgSpec("option"), PositionalArgSpec("Name")]
```

### Type Inference

The inspector automatically infers argument types from type hints:

- `bool` → `FlagArgSpec` (boolean flags)
- `str`, `int`, `float` → `OptionArgSpec` or `PositionalArgSpec` (depending on descriptor)
- Attributes with default values → `OptionArgSpec`
- Attributes with `positional()` descriptor → `PositionalArgSpec`

### Descriptors

Use descriptors to create specific argument types:

```python
from argsclass import positional, option, flag

class Args:
    # Positional argument
    filename = positional(help_text="Input file", arg_type=str)
    
    # Option with choices
    format = option(help_text="Output format", choices=["json", "xml"], default="json")
    
    # Flag with aliases
    verbose = flag(help_text="Verbose output", aliases={"v"})
```

### Complete Example

```python
from argsclass import inspect_class, positional, option, flag

class MyArgs:
    # Boolean flag (inferred from type hint)
    verbose: bool
    
    # Option with default
    output: str = "output.txt"
    
    # Positional argument
    filename = positional(help_text="Input file", arg_type=str)
    
    # Option with choices and aliases
    format = option(help_text="Output format", choices=["json", "xml"], aliases={"f"})
    
    # Flag with aliases
    debug = flag(help_text="Enable debug mode", aliases={"d"})

# Convert to ArgSpec objects
specs = inspect_class(MyArgs)
for spec in specs:
    print(f"{spec.__class__.__name__}: {spec.name}")

## Argument Parsing

The `parse` function can parse command-line arguments using either a list of ArgSpec objects or a class definition.

### Parsing with Classes

```python
from argsclass import parse, positional, option, flag

class MyArgs:
    verbose: bool
    output: str = "output.txt"
    filename = positional(help_text="Input file")

# Parse directly from class
result = parse(MyArgs, ["script.py", "--verbose", "input.txt"])
print(result)  # {'verbose': True, 'output': 'output.txt', 'filename': 'input.txt'}
```

### Parsing with ArgSpec Lists

```python
from argsclass import parse, PositionalArgSpec, OptionArgSpec, FlagArgSpec

specs = [
    PositionalArgSpec(name="filename"),
    OptionArgSpec(name="output", aliases={"o"}),
    FlagArgSpec(name="verbose", aliases={"v"})
]

result = parse(specs, ["script.py", "input.txt", "-o", "output.txt", "-v"])
print(result)  # {'filename': 'input.txt', 'output': 'output.txt', 'verbose': True}
```

## Ambiguity Protection

The parser includes built-in protection against ambiguous argument configurations that could lead to unpredictable parsing behavior.

### Ambiguous Configurations

The following configurations are considered ambiguous and will raise an `AmbiguityError`:

1. **Multiple positional arguments with non-specific cardinality**:
   ```python
   class AmbiguousArgs:
       files1 = positional(cardinality=Cardinality.one_or_more())
       files2 = positional(cardinality=Cardinality.zero_or_more())
   ```

2. **Multiple option arguments with non-specific cardinality**:
   ```python
   class AmbiguousArgs:
       files1 = option(cardinality=Cardinality.one_or_more())
       files2 = option(cardinality=Cardinality.zero_or_more())
   ```

**Note**: Mixed positional and option arguments with non-specific cardinality are **NOT** ambiguous because they are parsed differently:
- Options are parsed by name (e.g., `--option value`)
- Positionals are parsed by position

This configuration is valid:
```python
class ValidArgs:
    files = positional(cardinality=Cardinality.one_or_more())  # Parsed by position
    tags = option(cardinality=Cardinality.zero_or_more())      # Parsed by name
```

**Note**: The parsing order matters! Arguments are processed in the order they appear in the class definition. For mixed positional and option arguments, it's recommended to define options first, then positionals:

```python
class RecommendedOrder:
    tags = option(cardinality=Cardinality.zero_or_more())      # Processed first
    files = positional(cardinality=Cardinality.one_or_more())  # Processed second
```

### Resolving Ambiguities

To resolve ambiguities, consider these approaches:

1. **Use specific cardinalities**:
   ```python
   class ValidArgs:
       input_file = positional()  # Single value
       output_file = positional()  # Single value
       files = positional(cardinality=Cardinality.one_or_more())  # Only one with non-specific
   ```

2. **Reorder arguments** (put non-specific cardinality last):
   ```python
   class ValidArgs:
       input_file = positional()  # Specific first
       output_file = positional()  # Specific second
       extra_files = positional(cardinality=Cardinality.zero_or_more())  # Non-specific last
   ```

3. **Use different argument types** (this is actually always valid):
   ```python
   class ValidArgs:
       input_file = positional()  # Positional for required
       extra_files = option(cardinality=Cardinality.zero_or_more())  # Option for optional
   ```

### Disabling Ambiguity Validation

If you need to disable ambiguity validation (not recommended), you can set `validate_ambiguities=False`:

```python
result = parse(MyArgs, argv, validate_ambiguities=False)
```

### Ambiguity Detection Functions

You can also manually check for ambiguities:

```python
from argsclass import detect_ambiguities, is_ambiguous, get_ambiguity_resolution_suggestions

# Check if configuration is ambiguous
if is_ambiguous(MyArgs):
    warnings = detect_ambiguities(MyArgs)
    suggestions = get_ambiguity_resolution_suggestions(MyArgs)
    print("Ambiguities found:", warnings)
    print("Suggestions:", suggestions)
```
