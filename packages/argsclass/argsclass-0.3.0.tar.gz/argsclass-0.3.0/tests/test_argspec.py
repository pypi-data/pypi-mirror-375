"""Basic tests for ArgSpec and argument types."""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from argsclass.models import (
    BaseArgSpec, PositionalArgSpec, OptionArgSpec, FlagArgSpec,
    ArgumentType, PrimitiveType, Cardinality
)


# PrimitiveType tests

def test_primitive_string_type():
    """Test PrimitiveType with str."""
    string_type = PrimitiveType(str)
    assert string_type.convert("hello") == "hello"
    assert string_type.validate("hello")
    assert not string_type.validate(123)


def test_primitive_integer_type():
    """Test PrimitiveType with int."""
    int_type = PrimitiveType(int)
    assert int_type.convert("42") == 42
    assert int_type.validate(42)
    assert not int_type.validate("42")


def test_primitive_float_type():
    """Test PrimitiveType with float."""
    float_type = PrimitiveType(float)
    assert float_type.convert("3.14") == 3.14
    assert float_type.validate(3.14)
    assert float_type.validate(42)  # int is acceptable for float
    assert not float_type.validate("3.14")


def test_primitive_boolean_type():
    """Test PrimitiveType with bool - should raise error since booleans are handled by flags."""
    with self.assertRaises(ArgumentParsingError):
        PrimitiveType(bool)


def test_primitive_unsupported_type():
    """Test PrimitiveType with unsupported type."""
    with self.assertRaises(ArgumentParsingError):
        PrimitiveType(dict)


# ArgSpec tests

def test_basic_positional_arg():
    """Test basic positional argument."""
    spec = PositionalArgSpec(name="filename")
    
    assert spec.name == "filename"
    assert spec.kind == "positional"
    assert isinstance(spec.arg_type, PrimitiveType)
    assert spec.arg_type.primitive_type == str
    # Can use isinstance directly
    assert isinstance(spec, PositionalArgSpec)
    assert not isinstance(spec, OptionArgSpec)
    assert not isinstance(spec, FlagArgSpec)
    
    # Or use utility methods
    assert spec.is_positional()
    assert not spec.is_option()
    assert not spec.is_flag()
    assert spec.is_required
    assert not spec.is_optional
    assert str(spec) == "filename"


def test_basic_option_arg():
    """Test basic option argument."""
    spec = OptionArgSpec(
        name="output",
        help_text="Output file"
    )
    
    assert spec.name == "output"
    assert spec.kind == "option"
    assert isinstance(spec.arg_type, PrimitiveType)
    assert spec.arg_type.primitive_type == str
    # Can use isinstance directly  
    assert not isinstance(spec, PositionalArgSpec)
    assert isinstance(spec, OptionArgSpec)
    assert not isinstance(spec, FlagArgSpec)
    
    # Or use utility methods
    assert not spec.is_positional()
    assert spec.is_option()
    assert not spec.is_flag()
    assert spec.help_text == "Output file"
    assert str(spec) == "--output"


def test_basic_flag_arg():
    """Test basic flag argument."""
    spec = FlagArgSpec(
        name="verbose"
    )
    
    assert spec.name == "verbose"
    assert spec.kind == "flag"
    # Can use isinstance directly
    assert not isinstance(spec, PositionalArgSpec)
    assert not isinstance(spec, OptionArgSpec)
    assert isinstance(spec, FlagArgSpec)
    
    # Or use utility methods
    assert not spec.is_positional()
    assert not spec.is_option()
    assert spec.is_flag()
    assert spec.default is False  # Flags always default to False
    assert str(spec) == "--verbose"


def test_flag_arg_always_defaults_to_false():
    """Test that flags always default to False regardless of user input."""
    # User tries to set default=True
    spec = FlagArgSpec(name="verbose", default=True)
    
    # Flag should always default to False
    assert spec.default is False
    
    # User tries to set default=False (redundant but should work)
    spec2 = FlagArgSpec(name="debug", default=False)
    assert spec2.default is False


def test_arg_with_explicit_type():
    """Test argument with explicit type."""
    spec = OptionArgSpec(
        name="port",
        arg_type=PrimitiveType(int)
    )
    
    assert isinstance(spec.arg_type, PrimitiveType)
    assert spec.arg_type.primitive_type == int
    assert spec.validate_value(8080)
    assert not spec.validate_value("8080")
    assert spec.convert_value("8080") == 8080


def test_arg_with_primitive_type_direct():
    """Test argument with primitive type directly."""
    spec = OptionArgSpec(
        name="count",
        arg_type=int
    )
    
    assert isinstance(spec.arg_type, PrimitiveType)
    assert spec.arg_type.primitive_type == int
    assert spec.validate_value(42)
    assert not spec.validate_value("42")
    assert spec.convert_value("42") == 42


def test_arg_with_choices_constraint():
    """Test argument with choices constraint."""
    spec = OptionArgSpec(
        name="format",
        arg_type=str,
        choices=["json", "xml", "yaml"]
    )
    
    assert spec.validate_value("json")
    assert not spec.validate_value("csv")
    assert spec.convert_value("json") == "json"
    
    with self.assertRaises(ArgumentParsingError):
        spec.convert_value("csv")


def test_destination_property():
    """Test destination property."""
    spec1 = OptionArgSpec(name="output-file")
    spec2 = FlagArgSpec(name="verbose")
    
    assert spec1.destination == "output_file"
    assert spec2.destination == "verbose"


def test_aliases():
    """Test argument aliases."""
    spec = OptionArgSpec(
        name="verbose",
        aliases={"v", "verb"}
    )
    
    assert spec.aliases == {"v", "verb"}


def test_validation_errors():
    """Test basic validation errors."""
    # Empty name
    with self.assertRaises(ArgumentParsingError):
        PositionalArgSpec(name="")
    
    # Positional with aliases should fail at creation time
    with self.assertRaises(ArgumentParsingError):
        PositionalArgSpec(
            name="test",
            aliases={"t"}
        )


def test_required_and_default():
    """Test required and default value handling using cardinality."""
    spec = OptionArgSpec(
        name="config",
        cardinality=Cardinality.single(),  # min=1, so required=True
        default="config.json"
    )
    
    assert spec.is_required is True
    assert spec.default == "config.json"


def test_required_vs_optional():
    """Test the distinction between required and optional using cardinality."""
    # Required option (min=1)
    required_option = OptionArgSpec(
        name="input",
        cardinality=Cardinality.single()  # min=1
    )
    
    # Optional option (min=0)
    optional_option = OptionArgSpec(
        name="output", 
        cardinality=Cardinality.zero_or_one()  # min=0
    )
    
    # Positional (always required for now)
    positional_arg = PositionalArgSpec(
        name="filename"
    )
    
    # Flag (never required)
    flag_arg = FlagArgSpec(
        name="verbose"
    )
    
    assert required_option.is_required
    assert not required_option.is_optional
    
    assert not optional_option.is_required
    assert optional_option.is_optional
    
    assert positional_arg.is_required
    assert not positional_arg.is_optional
    
    assert not flag_arg.is_required
    assert flag_arg.is_optional


def test_choices_validation():
    """Test choices validation during ArgSpec creation."""
    # Empty choices should raise error
    with self.assertRaises(ArgumentParsingError):
        OptionArgSpec(
            name="format",
            choices=[]
        )
    
    # Default not in choices should raise error
    with self.assertRaises(ArgumentParsingError):
        OptionArgSpec(
            name="format",
            choices=["json", "xml"],
            default="yaml"
        )


def test_integer_choices():
    """Test integer argument with choices."""
    spec = OptionArgSpec(
        name="priority",
        arg_type=int,
        choices=[1, 2, 3, 4, 5]
    )
    
    assert spec.validate_value(3)
    assert not spec.validate_value(10)
    assert spec.convert_value("2") == 2
    
    with self.assertRaises(ArgumentParsingError):
        spec.convert_value("10")


# Integration tests

def test_complete_argument_definition():
    """Test a complete argument definition."""
    spec = OptionArgSpec(
        name="log-level",
        arg_type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        aliases={"l"},
        default="INFO",
        help_text="Set the logging level"
    )
    
    assert spec.name == "log-level"
    assert spec.destination == "log_level"
    self.assertIn("l", spec).aliases
    assert spec.default == "INFO"
    assert spec.help_text == "Set the logging level"
    assert spec.choices == ["DEBUG", "INFO", "WARNING", "ERROR"]
    assert spec.validate_value("DEBUG")
    assert not spec.validate_value("INVALID")
    assert spec.convert_value("ERROR") == "ERROR"


def test_different_primitive_types():
    """Test different primitive types."""
    # String argument
    str_spec = OptionArgSpec("name", arg_type=str)
    assert str_spec.arg_type.primitive_type == str
    assert str_spec.convert_value("hello") == "hello"
    
    # Integer argument
    int_spec = OptionArgSpec("count", arg_type=int)
    assert int_spec.arg_type.primitive_type == int
    assert int_spec.convert_value("42") == 42
    
    # Float argument
    float_spec = OptionArgSpec("rate", arg_type=float)
    assert float_spec.arg_type.primitive_type == float
    assert float_spec.convert_value("3.14") == 3.14
    
    # Boolean flag
    bool_spec = FlagArgSpec("debug")
    assert bool_spec.convert_value("true") is True


def test_argument_cardinality():
    """Test the Cardinality cardinality class."""
    # Single value (default)
    single = PositionalArgSpec("file")
    assert single.cardinality.min == 1
    assert single.cardinality.max == 1
    assert single.is_required
    
    # Zero or one
    zero_or_one = PositionalArgSpec("output", cardinality=Cardinality.zero_or_one())
    assert zero_or_one.cardinality.min == 0
    assert zero_or_one.cardinality.max == 1
    assert not zero_or_one.is_required
    
    # Zero or more
    zero_or_more = PositionalArgSpec("files", cardinality=Cardinality.zero_or_more())
    assert zero_or_more.cardinality.min == 0
    assert zero_or_more.cardinality.max is None
    assert not zero_or_more.is_required
    
    # One or more
    one_or_more = PositionalArgSpec("sources", cardinality=Cardinality.one_or_more())
    assert one_or_more.cardinality.min == 1
    assert one_or_more.cardinality.max is None
    assert one_or_more.is_required
    
    # Exact count
    exact = PositionalArgSpec("coords", cardinality=Cardinality.exactly(3))
    assert exact.cardinality.min == 3
    assert exact.cardinality.max == 3
    assert exact.is_required
    
    # Custom range
    custom = PositionalArgSpec("items", cardinality=Cardinality(min=2, max=5))
    assert custom.cardinality.min == 2
    assert custom.cardinality.max == 5
    assert custom.is_required


def test_cardinality_validation():
    """Test Cardinality cardinality validation."""
    # Invalid min value
    with self.assertRaises(ArgumentParsingError):
        Cardinality(min=-1)
    
    # Invalid max value
    with self.assertRaises(ArgumentParsingError):
        Cardinality(min=1, max=-1)
    
    # Max less than min
    with self.assertRaises(ArgumentParsingError):
        Cardinality(min=5, max=2)
    
    # Zero minimum should not be required
    zero_min = PositionalArgSpec("test", cardinality=Cardinality(min=0, max=5))
    assert not zero_min.is_required
    
    # Positive minimum should be required
    positive_min = PositionalArgSpec("test", cardinality=Cardinality(min=3, max=5))
    assert positive_min.is_required

if __name__ == "__main__":
    unittest.main()
