"""Tests for the argument parser functionality."""

import unittest
from argsclass.help import ValidationErrorCollector
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from argsclass.parser import ParserContext, PositionalArgumentParser, OptionArgumentParser, FlagArgumentParser, parse, ArgumentParsingError
from argsclass.models import BaseArgSpec, PositionalArgSpec, OptionArgSpec, FlagArgSpec, Cardinality, PrimitiveType


class TestParserContext(unittest.TestCase):
    """Test the ParserContext class."""
    
    def test_context_initialization(self):
        """Test context initialization with argv."""
        argv = ["script.py", "arg1", "arg2", "arg3"]
        context = ParserContext(argv)
        
        assert context.original_argv == argv
        assert context.current_argv == argv
        assert dict(context) == {}
    
    def test_consume(self):
        """Test consuming arguments from context."""
        argv = ["script.py", "arg1", "arg2", "arg3"]
        context = ParserContext(argv)
        
        # Consume first argument
        consumed = context.consume(1)
        assert consumed == ["script.py"]
        assert context.current_argv == ["arg1", "arg2", "arg3"]
        
        # Consume multiple arguments
        consumed = context.consume(2)
        assert consumed == ["arg1", "arg2"]
        assert context.current_argv == ["arg3"]
        
        # Consume remaining
        consumed = context.consume(1)
        assert consumed == ["arg3"]
        assert context.current_argv == []
    
    def test_consume_zero(self):
        """Test consuming zero arguments."""
        argv = ["arg1", "arg2"]
        context = ParserContext(argv)
        
        consumed = context.consume(0)
        assert consumed == []
        assert context.current_argv == argv
    
    def test_peek(self):
        """Test peeking at arguments without consuming."""
        argv = ["arg1", "arg2", "arg3"]
        context = ParserContext(argv)
        
        # Peek at first argument
        peeked = context.peek(1)
        assert peeked == ["arg1"]
        assert context.current_argv == argv  # Should not change
        
        # Peek at multiple arguments
        peeked = context.peek(2)
        assert peeked == ["arg1", "arg2"]
        assert context.current_argv == argv  # Should not change
    
    def test_has(self):
        """Test checking if arguments are available."""
        argv = ["arg1", "arg2"]
        context = ParserContext(argv)
        
        assert context.has(1)
        assert context.has(2)
        assert not context.has(3)
        assert context.has(0)  # Always true
    
    def test_parsed_values(self):
        """Test setting and getting parsed values using dictionary interface."""
        context = ParserContext([])
        
        # Set values using dictionary interface
        context["filename"] = "test.txt"
        context["count"] = 42
        
        # Get individual values using dictionary interface
        assert context["filename"] == "test.txt"
        assert context["count"] == 42
        
        # Test KeyError for missing key
        with self.assertRaises(KeyError):
            _ = context["nonexistent"]
        
        # Get all values using dict() constructor
        all_values = dict(context)
        assert all_values == {"filename": "test.txt", "count": 42}
    
    def test_dictionary_like_access(self):
        """Test dictionary-like access methods."""
        context = ParserContext([])
        
        # Test __setitem__ and __getitem__
        context["filename"] = "test.txt"
        context["count"] = 42
        
        assert context["filename"] == "test.txt"
        assert context["count"] == 42
        
        # Test KeyError for missing key
        with self.assertRaises(KeyError):
            _ = context["nonexistent"]
    
    def test_dictionary_like_methods(self):
        """Test dictionary-like methods."""
        context = ParserContext([])
        
        # Set some values
        context["key1"] = "value1"
        context["key2"] = "value2"
        
        # Test __contains__
        self.assertIn("key1", context)
        self.assertIn("key2", context)
        self.assertNotIn("nonexistent", context)
        
        # Test __len__
        self.assertEqual(len(context), 2)
        
        # Test keys()
        assert set(context.keys()) == {"key1", "key2"}
        
        # Test values()
        assert set(context.values()) == {"value1", "value2"}
        
        # Test items()
        assert set(context.items()) == {("key1", "value1"), ("key2", "value2")}
    
    def test_dictionary_interface_consistency(self):
        """Test that dictionary interface methods work consistently."""
        context = ParserContext([])
        
        # Set values using dictionary interface
        context["key1"] = "value1"
        context["key2"] = "value2"
        
        # Access using dictionary interface
        assert context["key1"] == "value1"
        assert context["key2"] == "value2"
        
        # All methods access the same underlying data
        assert dict(context) == {"key1": "value1", "key2": "value2"}
    
    def test_dictionary_like_with_parsing(self):
        """Test dictionary-like access with actual argument parsing."""
        from argsclass.parser import parse
        from argsclass.models import PositionalArgSpec
        
        specs = [PositionalArgSpec(name="filename")]
        argv = ["script.py", "test.txt"]
        
        result = parse(specs, argv)
        
        # The result should be a regular dict, not a ParserContext
        assert isinstance(result, dict)
        assert result["filename"] == "test.txt"
        
        # Test that we can use the result like a dict
        self.assertIn("filename", result)
        self.assertEqual(len(result), 1)
        assert list(result.keys()) == ["filename"]
        assert list(result.values()) == ["test.txt"]


class TestPositionalArgumentParser(unittest.TestCase):
    """Test the PositionalArgumentParser class."""
    
    def test_parse_single_required_argument(self):
        """Test parsing a single required positional argument."""
        spec = PositionalArgSpec(name="filename")
        parser = PositionalArgumentParser()
        context = ParserContext(["test.txt"])  # Script name already removed
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["filename"] == "test.txt"
        assert context.current_argv == []  # All args consumed
    
    def test_parse_single_optional_argument_with_value(self):
        """Test parsing a single optional positional argument that has a value."""
        spec = PositionalArgSpec(
            name="output",
            cardinality=Cardinality.zero_or_one(),
            default="default.txt"
        )
        parser = PositionalArgumentParser()
        context = ParserContext(["custom.txt"])  # Script name already removed
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["output"] == "custom.txt"
        assert context.current_argv == []
    
    def test_parse_single_optional_argument_without_value(self):
        """Test parsing a single optional positional argument without a value."""
        spec = PositionalArgSpec(
            name="output",
            cardinality=Cardinality.zero_or_one(),
            default="default.txt"
        )
        parser = PositionalArgumentParser()
        context = ParserContext([])  # No arguments provided
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["output"] == "default.txt"
        assert context.current_argv == []
    
    def test_parse_multiple_arguments(self):
        """Test parsing multiple positional arguments."""
        spec = PositionalArgSpec(
            name="files",
            cardinality=Cardinality.one_or_more()
        )
        parser = PositionalArgumentParser()
        context = ParserContext(["file1.txt", "file2.txt", "file3.txt"])  # Script name already removed
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["files"] == ["file1.txt", "file2.txt", "file3.txt"]
        assert context.current_argv == []
    
    def test_parse_exact_count_arguments(self):
        """Test parsing exactly N arguments."""
        spec = PositionalArgSpec(
            name="coords",
            cardinality=Cardinality.exactly(3)
        )
        parser = PositionalArgumentParser()
        context = ParserContext(["1", "2", "3"])  # Script name already removed
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["coords"] == ["1", "2", "3"]
        assert context.current_argv == []
    
    def test_parse_with_type_conversion(self):
        """Test parsing with type conversion."""
        spec = PositionalArgSpec(
            name="count",
            arg_type=PrimitiveType(int)
        )
        parser = PositionalArgumentParser()
        context = ParserContext(["42"])  # Script name already removed
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["count"] == 42
        assert isinstance(context["count"], int)
    
    def test_parse_with_choices(self):
        """Test parsing with choices constraint."""
        spec = PositionalArgSpec(
            name="format",
            choices=["json", "xml", "yaml"]
        )
        parser = PositionalArgumentParser()
        context = ParserContext(["json"])  # Script name already removed
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["format"] == "json"
    
    def test_parse_invalid_choice(self):
        """Test parsing with invalid choice."""
        spec = PositionalArgSpec(
            name="format",
            choices=["json", "xml", "yaml"]
        )
        parser = PositionalArgumentParser()
        context = ParserContext(["csv"])  # Script name already removed
        
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec, context, ValidationErrorCollector())
    
    def test_parse_invalid_type(self):
        """Test parsing with invalid type conversion."""
        spec = PositionalArgSpec(
            name="count",
            arg_type=PrimitiveType(int)
        )
        parser = PositionalArgumentParser()
        context = ParserContext(["not_a_number"])  # Script name already removed
        
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec, context, ValidationErrorCollector())
    
    def test_parse_insufficient_arguments(self):
        """Test parsing when there are insufficient arguments."""
        spec = PositionalArgSpec(
            name="files",
            cardinality=Cardinality.one_or_more()
        )
        parser = PositionalArgumentParser()
        context = ParserContext([])  # No arguments provided
        
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec, context, ValidationErrorCollector())
    
    def test_parse_insufficient_arguments_with_default(self):
        """Test parsing when there are insufficient arguments but default is available."""
        spec = PositionalArgSpec(
            name="output",
            cardinality=Cardinality.single(),
            default="default.txt"
        )
        parser = PositionalArgumentParser()
        context = ParserContext([])  # No arguments provided
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["output"] == "default.txt"
    
    def test_parse_wrong_spec_type(self):
        """Test parsing with wrong spec type."""
        from argsclass.models import OptionArgSpec
        
        spec = OptionArgSpec(name="test")
        parser = PositionalArgumentParser()
        context = ParserContext([])  # No arguments needed for this test
        
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec, context, ValidationErrorCollector())


class TestFlagArgumentParser(unittest.TestCase):
    """Test the FlagArgumentParser class."""
    
    def test_parse_flag_present(self):
        """Test parsing when flag is present."""
        spec = FlagArgSpec(name="verbose")
        parser = FlagArgumentParser()
        context = ParserContext(["--verbose"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["verbose"] is True
        assert context.current_argv == []  # Flag consumed
    
    def test_parse_flag_absent(self):
        """Test parsing when flag is absent."""
        spec = FlagArgSpec(name="verbose")
        parser = FlagArgumentParser()
        context = ParserContext([])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["verbose"] is False  # Default value
        assert context.current_argv == []
    
    def test_parse_flag_with_other_args(self):
        """Test parsing flag when other arguments are present."""
        spec = FlagArgSpec(name="verbose")
        parser = FlagArgumentParser()
        context = ParserContext(["--verbose", "file.txt", "--debug"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["verbose"] is True
        assert context.current_argv == ["file.txt", "--debug"]  # Other args preserved
    
    def test_parse_flag_with_short_alias(self):
        """Test parsing flag with short alias."""
        spec = FlagArgSpec(name="verbose", aliases={"v"})
        parser = FlagArgumentParser()
        context = ParserContext(["-v"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["verbose"] is True
        assert context.current_argv == []
    
    def test_parse_flag_with_long_alias(self):
        """Test parsing flag with long alias."""
        spec = FlagArgSpec(name="verbose", aliases={"verb"})
        parser = FlagArgumentParser()
        
        # Test with double dash
        context1 = ParserContext(["--verb"])
        parser.parse(spec, context1, ValidationErrorCollector())
        assert context1["verbose"] is True
        assert context1.current_argv == []
        
        # Test with single dash (multi-character alias with single dash)
        context2 = ParserContext(["-verb"])
        parser.parse(spec, context2, ValidationErrorCollector())
        assert context2["verbose"] is True
        assert context2.current_argv == []
    
    def test_parse_flag_with_multiple_aliases(self):
        """Test parsing flag with multiple aliases."""
        spec = FlagArgSpec(name="verbose", aliases={"v", "verb"})
        parser = FlagArgumentParser()
        
        # Test short alias
        context1 = ParserContext(["-v"])
        parser.parse(spec, context1, ValidationErrorCollector())
        assert context1["verbose"] is True
        
        # Test long alias
        context2 = ParserContext(["--verb"])
        parser.parse(spec, context2, ValidationErrorCollector())
        assert context2["verbose"] is True
        
        # Test main name
        context3 = ParserContext(["--verbose"])
        parser.parse(spec, context3, ValidationErrorCollector())
        assert context3["verbose"] is True
    
    def test_parse_flag_always_defaults_to_false(self):
        """Test that flags always default to False regardless of user input."""
        spec = FlagArgSpec(name="verbose", default=True)  # User tries to set default=True
        parser = FlagArgumentParser()
        context = ParserContext([])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        # Flag should always default to False, even if user specified default=True
        assert context["verbose"] is False
        assert spec.default is False  # The spec itself should have default=False
    
    def test_parse_flag_consumes_all_instances(self):
        """Test that flag parser consumes all instances of the flag."""
        spec = FlagArgSpec(name="verbose")
        parser = FlagArgumentParser()
        context = ParserContext(["--verbose", "file1.txt", "--verbose", "file2.txt"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["verbose"] is True
        assert context.current_argv == ["file1.txt", "file2.txt"]  # All flag instances consumed
    
    def test_parse_flag_with_dash_in_name(self):
        """Test parsing flag with dash in name."""
        spec = FlagArgSpec(name="dry-run")
        parser = FlagArgumentParser()
        context = ParserContext(["--dry-run"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["dry_run"] is True  # Destination converts dashes to underscores
        assert context.current_argv == []
    
    def test_parse_flag_wrong_spec_type(self):
        """Test parsing with wrong spec type."""
        from argsclass.models import PositionalArgSpec
        
        spec = PositionalArgSpec(name="test")
        parser = FlagArgumentParser()
        context = ParserContext([])
        
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec, context, ValidationErrorCollector())
    
    def test_parse_multiple_flags(self):
        """Test parsing multiple different flags."""
        verbose_spec = FlagArgSpec(name="verbose", aliases={"v"})
        debug_spec = FlagArgSpec(name="debug", aliases={"d"})
        parser = FlagArgumentParser()
        
        context = ParserContext(["-v", "--debug", "file.txt"])
        
        # Parse verbose flag
        parser.parse(verbose_spec, context, ValidationErrorCollector())
        assert context["verbose"] is True
        assert context.current_argv == ["--debug", "file.txt"]
        
        # Parse debug flag
        parser.parse(debug_spec, context, ValidationErrorCollector())
        assert context["debug"] is True
        assert context.current_argv == ["file.txt"]
    
    def test_parse_multi_char_alias_with_single_dash(self):
        """Test parsing multi-character alias with single dash."""
        spec = FlagArgSpec(name="verbose", aliases={"verb"})
        parser = FlagArgumentParser()
        
        # Test all possible forms
        test_cases = [
            "--verbose",  # Main name
            "--verb",     # Multi-char alias with double dash
            "-verb"       # Multi-char alias with single dash
        ]
        
        for test_case in test_cases:
            context = ParserContext([test_case])
            parser.parse(spec, context, ValidationErrorCollector())
            assert context["verbose"] is True, f"Failed for {test_case}"
            assert context.current_argv == []
    
    def test_parse_complex_multi_char_aliases(self):
        """Test parsing with complex multi-character aliases."""
        spec = FlagArgSpec(name="dry-run", aliases={"dry", "dryrun"})
        parser = FlagArgumentParser()
        
        # Test all possible forms
        test_cases = [
            "--dry-run",  # Main name
            "--dry",      # Multi-char alias with double dash
            "-dry",       # Multi-char alias with single dash
            "--dryrun",   # Another multi-char alias with double dash
            "-dryrun"     # Another multi-char alias with single dash
        ]
        
        for test_case in test_cases:
            context = ParserContext([test_case])
            parser.parse(spec, context, ValidationErrorCollector())
            assert context["dry_run"] is True, f"Failed for {test_case}"
            assert context.current_argv == []
    
    def test_parse_flag_with_explicit_true_value(self):
        """Test parsing flag with explicit true value."""
        spec = FlagArgSpec(name="verbose")
        parser = FlagArgumentParser()
        
        # Test --flag=true format
        context1 = ParserContext(["--verbose=true"])
        parser.parse(spec, context1, ValidationErrorCollector())
        assert context1["verbose"] is True
        assert context1.current_argv == []
        
        # Test --flag true format
        context2 = ParserContext(["--verbose", "true"])
        parser.parse(spec, context2, ValidationErrorCollector())
        assert context2["verbose"] is True
        assert context2.current_argv == []
    
    def test_parse_flag_with_explicit_false_value(self):
        """Test parsing flag with explicit false value."""
        spec = FlagArgSpec(name="verbose")
        parser = FlagArgumentParser()
        
        # Test --flag=false format
        context1 = ParserContext(["--verbose=false"])
        parser.parse(spec, context1, ValidationErrorCollector())
        assert context1["verbose"] is False
        assert context1.current_argv == []
        
        # Test --flag false format
        context2 = ParserContext(["--verbose", "false"])
        parser.parse(spec, context2, ValidationErrorCollector())
        assert context2["verbose"] is False
        assert context2.current_argv == []
    
    def test_parse_flag_with_explicit_values_and_other_args(self):
        """Test parsing flag with explicit values when other arguments are present."""
        spec = FlagArgSpec(name="verbose")
        parser = FlagArgumentParser()
        
        # Test with other arguments
        context = ParserContext(["--verbose=false", "file.txt", "--debug"])
        parser.parse(spec, context, ValidationErrorCollector())
        assert context["verbose"] is False
        assert context.current_argv == ["file.txt", "--debug"]
    
    def test_parse_flag_with_explicit_values_and_aliases(self):
        """Test parsing flag with explicit values using aliases."""
        spec = FlagArgSpec(name="verbose", aliases={"v"})
        parser = FlagArgumentParser()
        
        # Test short alias with explicit value
        context1 = ParserContext(["-v=true"])
        parser.parse(spec, context1, ValidationErrorCollector())
        assert context1["verbose"] is True
        assert context1.current_argv == []
        
        # Test short alias with space-separated value
        context2 = ParserContext(["-v", "false"])
        parser.parse(spec, context2, ValidationErrorCollector())
        assert context2["verbose"] is False
        assert context2.current_argv == []
    
    def test_parse_flag_with_mixed_explicit_values(self):
        """Test parsing multiple flags with mixed explicit values."""
        verbose_spec = FlagArgSpec(name="verbose", aliases={"v"})
        debug_spec = FlagArgSpec(name="debug", aliases={"d"})
        parser = FlagArgumentParser()
        
        context = ParserContext(["-v=true", "--debug=false", "file.txt"])
        
        # Parse verbose flag
        parser.parse(verbose_spec, context, ValidationErrorCollector())
        assert context["verbose"] is True
        assert context.current_argv == ["--debug=false", "file.txt"]
        
        # Parse debug flag
        parser.parse(debug_spec, context, ValidationErrorCollector())
        assert context["debug"] is False
        assert context.current_argv == ["file.txt"]
    
    def test_parse_flag_with_case_insensitive_values(self):
        """Test parsing flag with case insensitive boolean values."""
        spec = FlagArgSpec(name="verbose")
        parser = FlagArgumentParser()
        
        # Test various case combinations
        test_cases = [
            ("--verbose=TRUE", True),
            ("--verbose=True", True),
            ("--verbose=true", True),
            ("--verbose=FALSE", False),
            ("--verbose=False", False),
            ("--verbose=false", False)
        ]
        
        for test_case, expected in test_cases:
            context = ParserContext([test_case])
            parser.parse(spec, context, ValidationErrorCollector())
            assert context["verbose"] is expected, f"Failed for {test_case}"
            assert context.current_argv == []
    
    def test_parse_flag_with_non_boolean_values(self):
        """Test parsing flag with non-boolean values (should be treated as present)."""
        spec = FlagArgSpec(name="verbose")
        parser = FlagArgumentParser()
        
        # Test with non-boolean values in = format (should be treated as flag present)
        context1 = ParserContext(["--verbose=yes"])
        parser.parse(spec, context1, ValidationErrorCollector())
        assert context1["verbose"] is True  # Non-boolean value treated as present
        assert context1.current_argv == []
        
        # Test with space-separated non-boolean value
        # The flag should be treated as present, but the value should remain for other parsers
        context2 = ParserContext(["--verbose", "yes"])
        parser.parse(spec, context2, ValidationErrorCollector())
        assert context2["verbose"] is True  # Non-boolean value treated as present
        assert context2.current_argv == ["yes"]  # Value remains for other parsers to use


class TestOptionArgumentParser(unittest.TestCase):
    """Test the OptionArgumentParser class."""
    
    def test_parse_single_required_option(self):
        """Test parsing a single required option."""
        spec = OptionArgSpec(name="output")
        parser = OptionArgumentParser()
        context = ParserContext(["--output", "file.txt"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["output"] == "file.txt"
        assert context.current_argv == []  # All args consumed
    
    def test_parse_single_optional_option_with_value(self):
        """Test parsing a single optional option that has a value."""
        spec = OptionArgSpec(
            name="config",
            cardinality=Cardinality.zero_or_one(),
            default="default.json"
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--config", "custom.json"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["config"] == "custom.json"
        assert context.current_argv == []
    
    def test_parse_single_optional_option_without_value(self):
        """Test parsing a single optional option without a value."""
        spec = OptionArgSpec(
            name="config",
            cardinality=Cardinality.zero_or_one(),
            default="default.json"
        )
        parser = OptionArgumentParser()
        context = ParserContext([])  # No arguments provided
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["config"] == "default.json"
        assert context.current_argv == []
    
    def test_parse_option_with_equals_format(self):
        """Test parsing option with --option=value format."""
        spec = OptionArgSpec(name="output")
        parser = OptionArgumentParser()
        context = ParserContext(["--output=file.txt"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["output"] == "file.txt"
        assert context.current_argv == []
    
    def test_parse_option_with_short_alias(self):
        """Test parsing option with short alias."""
        spec = OptionArgSpec(name="output", aliases={"o"})
        parser = OptionArgumentParser()
        context = ParserContext(["-o", "file.txt"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["output"] == "file.txt"
        assert context.current_argv == []
    
    def test_parse_option_with_long_alias(self):
        """Test parsing option with long alias."""
        spec = OptionArgSpec(name="output", aliases={"out"})
        parser = OptionArgumentParser()
        
        # Test with double dash
        context1 = ParserContext(["--out", "file.txt"])
        parser.parse(spec, context1, ValidationErrorCollector())
        assert context1["output"] == "file.txt"
        assert context1.current_argv == []
        
        # Test with single dash (multi-character alias with single dash)
        context2 = ParserContext(["-out", "file.txt"])
        parser.parse(spec, context2, ValidationErrorCollector())
        assert context2["output"] == "file.txt"
        assert context2.current_argv == []
    
    def test_parse_option_with_multiple_aliases(self):
        """Test parsing option with multiple aliases."""
        spec = OptionArgSpec(name="output", aliases={"o", "out"})
        parser = OptionArgumentParser()
        
        # Test short alias
        context1 = ParserContext(["-o", "file1.txt"])
        parser.parse(spec, context1, ValidationErrorCollector())
        assert context1["output"] == "file1.txt"
        
        # Test long alias
        context2 = ParserContext(["--out", "file2.txt"])
        parser.parse(spec, context2, ValidationErrorCollector())
        assert context2["output"] == "file2.txt"
        
        # Test main name
        context3 = ParserContext(["--output", "file3.txt"])
        parser.parse(spec, context3, ValidationErrorCollector())
        assert context3["output"] == "file3.txt"
    
    def test_parse_option_with_type_conversion(self):
        """Test parsing option with type conversion."""
        spec = OptionArgSpec(
            name="port",
            arg_type=PrimitiveType(int)
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--port", "8080"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["port"] == 8080
        assert isinstance(context["port"], int)
    
    def test_parse_option_with_choices(self):
        """Test parsing option with choices constraint."""
        spec = OptionArgSpec(
            name="format",
            choices=["json", "xml", "yaml"]
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--format", "json"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["format"] == "json"
    
    def test_parse_option_invalid_choice(self):
        """Test parsing option with invalid choice."""
        spec = OptionArgSpec(
            name="format",
            choices=["json", "xml", "yaml"]
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--format", "csv"])
        error_collector = ValidationErrorCollector()
        
        parser.parse(spec, context, error_collector)
        
        self.assertTrue(error_collector.has_errors())
        self.assertIn("Invalid choice", error_collector.format_errors())
    
    def test_parse_option_invalid_type(self):
        """Test parsing option with invalid type conversion."""
        spec = OptionArgSpec(
            name="port",
            arg_type=PrimitiveType(int)
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--port", "not_a_number"])
        error_collector = ValidationErrorCollector()
        
        parser.parse(spec, context, error_collector)
        
        self.assertTrue(error_collector.has_errors())
        self.assertIn("Error parsing option", error_collector.format_errors())
    
    def test_parse_option_insufficient_values(self):
        """Test parsing option when there are insufficient values."""
        spec = OptionArgSpec(
            name="files",
            cardinality=Cardinality.one_or_more()
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--files"])  # No values provided
        
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec, context, ValidationErrorCollector())
    
    def test_parse_option_insufficient_values_with_default(self):
        """Test parsing option when there are insufficient values but default is available."""
        spec = OptionArgSpec(
            name="output",
            cardinality=Cardinality.single(),
            default="default.txt"
        )
        parser = OptionArgumentParser()
        context = ParserContext([])  # No arguments provided
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["output"] == "default.txt"
    
    def test_parse_option_wrong_spec_type(self):
        """Test parsing option with wrong spec type."""
        from argsclass.models import PositionalArgSpec
        
        spec = PositionalArgSpec(name="test")
        parser = OptionArgumentParser()
        context = ParserContext([])
        
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec, context, ValidationErrorCollector())
    
    def test_parse_option_with_other_args(self):
        """Test parsing option when other arguments are present."""
        spec = OptionArgSpec(name="output")
        parser = OptionArgumentParser()
        context = ParserContext(["--output", "file.txt", "positional", "--flag"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["output"] == "file.txt"
        assert context.current_argv == ["positional", "--flag"]  # Other args preserved
    
    def test_parse_option_with_dash_in_name(self):
        """Test parsing option with dash in name."""
        spec = OptionArgSpec(name="output-file")
        parser = OptionArgumentParser()
        context = ParserContext(["--output-file", "file.txt"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["output_file"] == "file.txt"  # Destination converts dashes to underscores
        assert context.current_argv == []
    
    def test_parse_multiple_options(self):
        """Test parsing multiple different options."""
        output_spec = OptionArgSpec(name="output", aliases={"o"})
        config_spec = OptionArgSpec(name="config", aliases={"c"})
        parser = OptionArgumentParser()
        
        context = ParserContext(["-o", "file.txt", "--config", "config.json", "positional"])
        
        # Parse output option
        parser.parse(output_spec, context, ValidationErrorCollector())
        assert context["output"] == "file.txt"
        assert context.current_argv == ["--config", "config.json", "positional"]
        
        # Parse config option
        parser.parse(config_spec, context, ValidationErrorCollector())
        assert context["config"] == "config.json"
        assert context.current_argv == ["positional"]
    
    def test_parse_option_with_multiple_values_repeated_names(self):
        """Test parsing option with multiple values using repeated option names."""
        spec = OptionArgSpec(
            name="files",
            cardinality=Cardinality.one_or_more()
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--files", "file1.txt", "--files", "file2.txt", "--files", "file3.txt"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["files"] == ["file1.txt", "file2.txt", "file3.txt"]
        assert context.current_argv == []
    
    def test_parse_option_with_consecutive_values(self):
        """Test parsing option with consecutive values - only first value consumed."""
        spec = OptionArgSpec(
            name="files",
            cardinality=Cardinality.one_or_more()
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--files", "file1.txt", "file2.txt", "file3.txt"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        # Only first value is consumed by the option, rest remain for positional arguments
        assert context["files"] == ["file1.txt"]
        assert context.current_argv == ["file2.txt", "file3.txt"]
    
    def test_parse_option_with_exact_count_values_repeated_names(self):
        """Test parsing option with exact count of values using repeated option names."""
        spec = OptionArgSpec(
            name="coords",
            cardinality=Cardinality.exactly(3)
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--coords", "1", "--coords", "2", "--coords", "3"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["coords"] == ["1", "2", "3"]
        assert context.current_argv == []
    
    def test_parse_option_with_exact_count_consecutive_values(self):
        """Test parsing option with exact count but consecutive values - should raise error."""
        spec = OptionArgSpec(
            name="coords",
            cardinality=Cardinality.exactly(3)
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--coords", "1", "2", "3"])
        
        # Should raise error because exact count requires repeated option names
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec, context, ValidationErrorCollector())
    
    def test_parse_option_with_zero_or_more_values_repeated_names(self):
        """Test parsing option with zero or more values using repeated option names."""
        spec = OptionArgSpec(
            name="tags",
            cardinality=Cardinality.zero_or_more()
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--tags", "tag1", "--tags", "tag2"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["tags"] == ["tag1", "tag2"]
        assert context.current_argv == []
    
    def test_parse_option_with_zero_or_more_consecutive_values(self):
        """Test parsing option with zero or more but consecutive values - only first consumed."""
        spec = OptionArgSpec(
            name="tags",
            cardinality=Cardinality.zero_or_more()
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--tags", "tag1", "tag2"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        # Only first value is consumed, rest remain for positional arguments
        assert context["tags"] == ["tag1"]
        assert context.current_argv == ["tag2"]
    
    def test_parse_option_with_zero_or_more_values_none_provided(self):
        """Test parsing option with zero or more values when none provided."""
        spec = OptionArgSpec(
            name="tags",
            cardinality=Cardinality.zero_or_more(),
            default=[]
        )
        parser = OptionArgumentParser()
        context = ParserContext([])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        assert context["tags"] == []
        assert context.current_argv == []
    
    def test_parse_option_with_mixed_equals_and_space_formats(self):
        """Test parsing option with mixed equals and space formats."""
        spec = OptionArgSpec(name="output", aliases={"o"})
        parser = OptionArgumentParser()
        
        # Test equals format
        context1 = ParserContext(["--output=file1.txt"])
        parser.parse(spec, context1, ValidationErrorCollector())
        assert context1["output"] == "file1.txt"
        
        # Test space format
        context2 = ParserContext(["-o", "file2.txt"])
        parser.parse(spec, context2, ValidationErrorCollector())
        assert context2["output"] == "file2.txt"
    
    def test_parse_option_consumes_all_instances(self):
        """Test that option parser consumes all instances of the option."""
        spec = OptionArgSpec(name="output")
        parser = OptionArgumentParser()
        context = ParserContext(["--output", "file1.txt", "--output", "file2.txt"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        # Should get the first value (only first value consumed for single cardinality)
        assert context["output"] == "file1.txt"  # Single value, so first one wins
        assert context.current_argv == []
    
    def test_parse_option_with_multiple_instances_and_cardinality(self):
        """Test parsing option with multiple instances and appropriate cardinality."""
        spec = OptionArgSpec(
            name="files",
            cardinality=Cardinality.one_or_more()
        )
        parser = OptionArgumentParser()
        context = ParserContext(["--files", "file1.txt", "--files", "file2.txt"])
        
        parser.parse(spec, context, ValidationErrorCollector())
        
        # Should collect all values from all instances
        assert context["files"] == ["file1.txt", "file2.txt"]
        assert context.current_argv == []
    
    def test_parse_option_with_complex_multi_char_aliases(self):
        """Test parsing option with complex multi-character aliases."""
        spec = OptionArgSpec(name="output-file", aliases={"out", "output"})
        parser = OptionArgumentParser()
        
        # Test all possible forms
        test_cases = [
            ("--output-file", "file1.txt"),  # Main name
            ("--out", "file2.txt"),          # Multi-char alias with double dash
            ("-out", "file3.txt"),           # Multi-char alias with single dash
            ("--output", "file4.txt"),       # Another multi-char alias with double dash
            ("-output", "file5.txt")         # Another multi-char alias with single dash
        ]
        
        for option_name, filename in test_cases:
            context = ParserContext([option_name, filename])
            parser.parse(spec, context, ValidationErrorCollector())
            assert context["output_file"] == filename, f"Failed for {option_name}"
            assert context.current_argv == []
    
    def test_parse_option_without_value_is_always_error(self):
        """Test that options without values are always errors, even for optional options."""
        parser = OptionArgumentParser()
        
        # Test required option without value
        spec1 = OptionArgSpec(name="output")
        context1 = ParserContext(["--output"])
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec1, context1, ValidationErrorCollector())
        
        # Test optional option without value (should still be error)
        spec2 = OptionArgSpec(
            name="config",
            cardinality=Cardinality.zero_or_one(),
            default="default.json"
        )
        context2 = ParserContext(["--config"])
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec2, context2, ValidationErrorCollector())
        
        # Test option with alias without value
        spec3 = OptionArgSpec(name="output", aliases={"o"})
        context3 = ParserContext(["-o"])
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec3, context3, ValidationErrorCollector())
        
        # Test option at end of argv without value
        spec4 = OptionArgSpec(name="output")
        context4 = ParserContext(["--output"])
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec4, context4, ValidationErrorCollector())
        
        # Test option followed by another option without value
        spec5 = OptionArgSpec(name="output")
        context5 = ParserContext(["--output", "--other"])
        with self.assertRaises(ArgumentParsingError):
            parser.parse(spec5, context5, ValidationErrorCollector())
    


class TestParseFunction(unittest.TestCase):
    """Test the root parse function."""
    
    def test_parse_single_positional(self):
        """Test parsing a single positional argument."""
        specs = [PositionalArgSpec(name="filename")]
        argv = ["script.py", "test.txt"]
        
        result = parse(specs, argv)
        
        assert result == {"filename": "test.txt"}
    
    def test_parse_multiple_positionals(self):
        """Test parsing multiple positional arguments."""
        specs = [
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="output")
        ]
        argv = ["script.py", "input.txt", "output.txt"]
        
        result = parse(specs, argv)
        
        assert result == {"input": "input.txt", "output": "output.txt"}
    
    def test_parse_mixed_cardinality(self):
        """Test parsing arguments with mixed cardinality."""
        specs = [
            PositionalArgSpec(name="required_file"),
            PositionalArgSpec(
                name="optional_files",
                cardinality=Cardinality.zero_or_more()
            )
        ]
        argv = ["script.py", "required.txt", "opt1.txt", "opt2.txt"]
        
        result = parse(specs, argv)
        
        assert result == {
            "required_file": "required.txt",
            "optional_files": ["opt1.txt", "opt2.txt"]
        }
    
    def test_parse_with_types_and_choices(self):
        """Test parsing with type conversion and choices."""
        specs = [
            PositionalArgSpec(
                name="count",
                arg_type=PrimitiveType(int)
            ),
            PositionalArgSpec(
                name="format",
                choices=["json", "xml"]
            )
        ]
        argv = ["script.py", "42", "json"]
        
        result = parse(specs, argv)
        
        assert result == {"count": 42, "format": "json"}
        assert isinstance(result["count"], int)
    
    def test_parse_with_defaults(self):
        """Test parsing with default values."""
        specs = [
            PositionalArgSpec(name="required"),
            PositionalArgSpec(
                name="optional",
                cardinality=Cardinality.zero_or_one(),
                default="default_value"
            )
        ]
        argv = ["script.py", "required_value"]
        
        result = parse(specs, argv)
        
        assert result == {
            "required": "required_value",
            "optional": "default_value"
        }
    
    def test_parse_single_option(self):
        """Test parsing a single option argument."""
        specs = [OptionArgSpec(name="output")]
        argv = ["script.py", "--output", "file.txt"]
        
        result = parse(specs, argv)
        
        assert result == {"output": "file.txt"}
    
    def test_parse_single_option_absent(self):
        """Test parsing a single option argument when not present."""
        specs = [OptionArgSpec(name="output", default="default.txt")]
        argv = ["script.py"]
        
        result = parse(specs, argv)
        
        assert result == {"output": "default.txt"}
    
    def test_parse_multiple_options(self):
        """Test parsing multiple option arguments."""
        specs = [
            OptionArgSpec(name="output", aliases={"o"}),
            OptionArgSpec(name="config", aliases={"c"}),
            FlagArgSpec(name="verbose", aliases={"v"})
        ]
        argv = ["script.py", "-o", "file.txt", "--config", "config.json", "-v"]
        
        result = parse(specs, argv)
        
        assert result == {
            "output": "file.txt",
            "config": "config.json",
            "verbose": True
        }
    
    def test_parse_options_with_positionals(self):
        """Test parsing options mixed with positional arguments."""
        specs = [
            OptionArgSpec(name="output", aliases={"o"}),
            PositionalArgSpec(name="filename"),
            OptionArgSpec(name="config", aliases={"c"})
        ]
        argv = ["script.py", "--output", "output.txt", "input.txt", "-c", "config.json"]
        
        result = parse(specs, argv)
        
        assert result == {
            "output": "output.txt",
            "filename": "input.txt",
            "config": "config.json"
        }
    
    def test_parse_options_with_flags(self):
        """Test parsing options mixed with flag arguments."""
        specs = [
            OptionArgSpec(name="output", aliases={"o"}),
            FlagArgSpec(name="verbose", aliases={"v"}),
            OptionArgSpec(name="config", aliases={"c"})
        ]
        argv = ["script.py", "-o", "file.txt", "--verbose", "-c", "config.json"]
        
        result = parse(specs, argv)
        
        assert result == {
            "output": "file.txt",
            "verbose": True,
            "config": "config.json"
        }
    
    def test_parse_options_with_equals_format(self):
        """Test parsing options with equals format."""
        specs = [
            OptionArgSpec(name="output", aliases={"o"}),
            OptionArgSpec(name="port", arg_type=PrimitiveType(int))
        ]
        argv = ["script.py", "--output=file.txt", "-o=backup.txt", "--port=8080"]
        
        result = parse(specs, argv)
        
        assert result == {
            "output": "file.txt",  # First value wins for single cardinality
            "port": 8080
        }
    
    def test_parse_options_with_type_conversion(self):
        """Test parsing options with type conversion."""
        specs = [
            OptionArgSpec(name="port", arg_type=PrimitiveType(int)),
            OptionArgSpec(name="rate", arg_type=PrimitiveType(float))
        ]
        argv = ["script.py", "--port", "8080", "--rate", "3.14"]
        
        result = parse(specs, argv)
        
        assert result == {"port": 8080, "rate": 3.14}
        assert isinstance(result["port"], int)
        assert isinstance(result["rate"], float)
    
    def test_parse_options_with_choices(self):
        """Test parsing options with choices constraint."""
        specs = [
            OptionArgSpec(name="format", choices=["json", "xml", "yaml"]),
            OptionArgSpec(name="level", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
        ]
        argv = ["script.py", "--format", "json", "--level", "INFO"]
        
        result = parse(specs, argv)
        
        assert result == {"format": "json", "level": "INFO"}
    
    def test_parse_options_with_defaults(self):
        """Test parsing options with default values."""
        specs = [
            OptionArgSpec(name="output", default="output.txt"),
            OptionArgSpec(name="config", default="config.json"),
            OptionArgSpec(name="port", arg_type=PrimitiveType(int), default=8080)
        ]
        argv = ["script.py", "--config", "custom.json"]  # Only config provided
        
        result = parse(specs, argv)
        
        assert result == {
            "output": "output.txt",
            "config": "custom.json",
            "port": 8080
        }
    
    def test_parse_options_with_multiple_values_repeated_names(self):
        """Test parsing options with multiple values using repeated option names."""
        specs = [
            OptionArgSpec(name="files", cardinality=Cardinality.one_or_more()),
            OptionArgSpec(name="tags", cardinality=Cardinality.zero_or_more(), default=[])
        ]
        argv = ["script.py", "--files", "file1.txt", "--files", "file2.txt", "--tags", "tag1", "--tags", "tag2"]
        
        # This configuration is ambiguous, so we need to disable validation for this test
        result = parse(specs, argv, validate_ambiguities=False)
        
        assert result == {
            "files": ["file1.txt", "file2.txt"],
            "tags": ["tag1", "tag2"]
        }
    
    def test_parse_options_with_consecutive_values(self):
        """Test parsing options with consecutive values - only first value consumed per option."""
        specs = [
            OptionArgSpec(name="files", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="command")
        ]
        argv = ["script.py", "--files", "file1.txt", "file2.txt", "process"]
        
        result = parse(specs, argv)
        
        # Only first value consumed by option, rest become positional arguments
        assert result == {
            "files": ["file1.txt"],
            "command": "file2.txt"
        }
    
    def test_parse_complex_mixed_scenario_with_options(self):
        """Test a complex scenario with options, flags, and positionals."""
        specs = [
            OptionArgSpec(name="output", aliases={"o"}),
            FlagArgSpec(name="verbose", aliases={"v"}),
            PositionalArgSpec(name="command"),
            OptionArgSpec(name="config", aliases={"c"}),
            PositionalArgSpec(name="files", cardinality=Cardinality.one_or_more()),
            FlagArgSpec(name="debug", aliases={"d"})
        ]
        argv = ["script.py", "-o", "output.txt", "-v", "process", "--config", "config.json", "file1.txt", "file2.txt", "-d"]
        
        result = parse(specs, argv)
        
        assert result == {
            "output": "output.txt",
            "verbose": True,
            "command": "process",
            "config": "config.json",
            "files": ["file1.txt", "file2.txt"],
            "debug": True
        }
    
    def test_parse_options_insufficient_values(self):
        """Test parsing options when there are insufficient values."""
        specs = [OptionArgSpec(name="files", cardinality=Cardinality.one_or_more())]
        argv = ["script.py", "--files"]  # No values provided
        
        with self.assertRaises(ArgumentParsingError):
            parse(specs, argv)
    
    def test_parse_options_invalid_choice(self):
        """Test parsing options with invalid choice."""
        specs = [OptionArgSpec(name="format", choices=["json", "xml"])]
        argv = ["script.py", "--format", "csv"]
        
        with self.assertRaises(ArgumentParsingError):
            parse(specs, argv)
    
    def test_parse_options_invalid_type(self):
        """Test parsing options with invalid type conversion."""
        specs = [OptionArgSpec(name="port", arg_type=PrimitiveType(int))]
        argv = ["script.py", "--port", "not_a_number"]
        
        with self.assertRaises(ArgumentParsingError):
            parse(specs, argv)
    
    def test_parse_options_without_value_is_always_error(self):
        """Test that options without values are always errors in main parse function."""
        # Test required option without value
        specs1 = [OptionArgSpec(name="output")]
        argv1 = ["script.py", "--output"]
        with self.assertRaises(ArgumentParsingError):
            parse(specs1, argv1)
        
        # Test optional option without value (should still be error)
        specs2 = [OptionArgSpec(name="config", cardinality=Cardinality.zero_or_one(), default="default.json")]
        argv2 = ["script.py", "--config"]
        with self.assertRaises(ArgumentParsingError):
            parse(specs2, argv2)
        
        # Test option with alias without value
        specs3 = [OptionArgSpec(name="output", aliases={"o"})]
        argv3 = ["script.py", "-o"]
        with self.assertRaises(ArgumentParsingError):
            parse(specs3, argv3)
    
    
    def test_parse_empty_specs(self):
        """Test parsing with empty specifications."""
        specs = []
        argv = ["script.py", "extra", "args"]
        
        result = parse(specs, argv)
        
        assert result == {}
    
    def test_parse_complex_scenario(self):
        """Test a complex parsing scenario."""
        specs = [
            PositionalArgSpec(name="command"),
            PositionalArgSpec(
                name="files",
                cardinality=Cardinality.one_or_more()
            ),
            PositionalArgSpec(
                name="output",
                cardinality=Cardinality.zero_or_one(),
                default="output.txt"
            )
        ]
        argv = ["script.py", "process", "file1.txt", "file2.txt"]
        
        # This configuration is ambiguous (non-specific before specific), so disable validation
        result = parse(specs, argv, validate_ambiguities=False)
        
        assert result == {
            "command": "process",
            "files": ["file1.txt", "file2.txt"],
            "output": "output.txt"
        }
    
    def test_parse_with_mixed_flags_and_positionals(self):
        """Test parsing with flags mixed between positional arguments."""
        specs = [
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="output")
        ]
        argv = ["script.py", "--verbose", "input.txt", "--debug", "output.txt"]
        
        result = parse(specs, argv, ignore_unknown=True)
        
        assert result == {
            "input": "input.txt",
            "output": "output.txt"
        }
    
    def test_parse_positionals_with_flags_before(self):
        """Test parsing positional arguments when flags come before them."""
        specs = [PositionalArgSpec(name="filename")]
        argv = ["script.py", "--verbose", "--debug", "test.txt"]
        
        result = parse(specs, argv, ignore_unknown=True)
        
        assert result == {"filename": "test.txt"}
    
    def test_parse_positionals_with_flags_after(self):
        """Test parsing positional arguments when flags come after them."""
        specs = [PositionalArgSpec(name="filename")]
        argv = ["script.py", "test.txt", "--verbose", "--debug"]
        
        result = parse(specs, argv, ignore_unknown=True)
        
        assert result == {"filename": "test.txt"}
    
    def test_parse_multiple_positionals_with_scattered_flags(self):
        """Test parsing multiple positional arguments with flags scattered throughout."""
        specs = [
            PositionalArgSpec(name="command"),
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="output")
        ]
        argv = ["script.py", "--verbose", "process", "--debug", "input.txt", "--quiet", "output.txt"]
        
        result = parse(specs, argv, ignore_unknown=True)
        
        assert result == {
            "command": "process",
            "input": "input.txt",
            "output": "output.txt"
        }
    
    def test_parse_with_cardinality_and_mixed_flags(self):
        """Test parsing with cardinality when flags are mixed in."""
        specs = [PositionalArgSpec(name="files", cardinality=Cardinality.one_or_more())]
        argv = ["script.py", "--verbose", "file1.txt", "--debug", "file2.txt", "file3.txt"]
        
        result = parse(specs, argv, ignore_unknown=True)
        
        assert result == {"files": ["file1.txt", "file2.txt", "file3.txt"]}
    
    def test_parse_optional_positional_with_only_flags(self):
        """Test parsing optional positional argument when only flags are provided."""
        specs = [
            PositionalArgSpec(
                name="filename",
                cardinality=Cardinality.zero_or_one(),
                default="default.txt"
            )
        ]
        argv = ["script.py", "--verbose", "--debug"]
        
        result = parse(specs, argv, ignore_unknown=True)
        
        assert result == {"filename": "default.txt"}
    
    def test_parse_with_type_conversion_and_flags(self):
        """Test parsing with type conversion when flags are present."""
        specs = [PositionalArgSpec(name="count", arg_type=PrimitiveType(int))]
        argv = ["script.py", "--verbose", "42", "--debug"]
        
        result = parse(specs, argv, ignore_unknown=True)
        
        assert result == {"count": 42}
        assert isinstance(result["count"], int)
    
    def test_parse_with_choices_and_flags(self):
        """Test parsing with choices constraint when flags are present."""
        specs = [PositionalArgSpec(name="format", choices=["json", "xml", "yaml"])]
        argv = ["script.py", "--verbose", "json", "--debug"]
        
        result = parse(specs, argv, ignore_unknown=True)
        
        assert result == {"format": "json"}
    
    def test_parse_insufficient_positionals_with_flags(self):
        """Test parsing when there are insufficient positional arguments but flags are present."""
        specs = [PositionalArgSpec(name="required")]
        argv = ["script.py", "--verbose", "--debug"]
        
        with self.assertRaises(ArgumentParsingError):
            parse(specs, argv)
    
    def test_parse_invalid_choice_with_flags(self):
        """Test parsing with invalid choice when flags are present."""
        specs = [PositionalArgSpec(name="format", choices=["json", "xml"])]
        argv = ["script.py", "--verbose", "csv", "--debug"]
        
        with self.assertRaises(ArgumentParsingError):
            parse(specs, argv)
    
    def test_parse_invalid_type_with_flags(self):
        """Test parsing with invalid type conversion when flags are present."""
        specs = [PositionalArgSpec(name="count", arg_type=PrimitiveType(int))]
        argv = ["script.py", "--verbose", "not_a_number", "--debug"]
        
        with self.assertRaises(ArgumentParsingError):
            parse(specs, argv)
    
    def test_parse_single_flag(self):
        """Test parsing a single flag argument."""
        specs = [FlagArgSpec(name="verbose")]
        argv = ["script.py", "--verbose"]
        
        result = parse(specs, argv)
        
        assert result == {"verbose": True}
    
    def test_parse_single_flag_absent(self):
        """Test parsing a single flag argument when not present."""
        specs = [FlagArgSpec(name="verbose")]
        argv = ["script.py"]
        
        result = parse(specs, argv)
        
        assert result == {"verbose": False}
    
    def test_parse_multiple_flags(self):
        """Test parsing multiple flag arguments."""
        specs = [
            FlagArgSpec(name="verbose", aliases={"v"}),
            FlagArgSpec(name="debug", aliases={"d"}),
            FlagArgSpec(name="quiet")
        ]
        argv = ["script.py", "-v", "--debug"]
        
        result = parse(specs, argv)
        
        assert result == {
            "verbose": True,
            "debug": True,
            "quiet": False
        }
    
    def test_parse_flags_with_positionals(self):
        """Test parsing flags mixed with positional arguments."""
        specs = [
            FlagArgSpec(name="verbose", aliases={"v"}),
            PositionalArgSpec(name="filename"),
            FlagArgSpec(name="debug", aliases={"d"})
        ]
        argv = ["script.py", "--verbose", "test.txt", "-d"]
        
        result = parse(specs, argv)
        
        assert result == {
            "verbose": True,
            "filename": "test.txt",
            "debug": True
        }
    
    def test_parse_flags_with_aliases(self):
        """Test parsing flags with various aliases."""
        specs = [
            FlagArgSpec(name="verbose", aliases={"v", "verb"}),
            FlagArgSpec(name="output", aliases={"o"})
        ]
        argv = ["script.py", "-v", "--output"]
        
        result = parse(specs, argv)
        
        assert result == {
            "verbose": True,
            "output": True
        }
    
    def test_parse_flags_with_multi_char_single_dash_aliases(self):
        """Test parsing flags with multi-character aliases using single dash."""
        specs = [
            FlagArgSpec(name="verbose", aliases={"verb"}),
            FlagArgSpec(name="debug", aliases={"dbg"})
        ]
        argv = ["script.py", "-verb", "-dbg"]
        
        result = parse(specs, argv)
        
        assert result == {
            "verbose": True,
            "debug": True
        }
    
    def test_parse_flags_mixed_dash_forms(self):
        """Test parsing flags with mixed dash forms for aliases."""
        specs = [
            FlagArgSpec(name="dry-run", aliases={"dry", "dryrun"}),
            FlagArgSpec(name="verbose", aliases={"v", "verb"})
        ]
        argv = ["script.py", "-dry", "--verb", "-v", "--dryrun"]
        
        result = parse(specs, argv)
        
        assert result == {
            "dry_run": True,
            "verbose": True
        }
    
    def test_parse_flags_always_default_to_false(self):
        """Test that flags always default to False regardless of user specification."""
        specs = [
            FlagArgSpec(name="verbose", default=True),  # User tries to set default=True
            FlagArgSpec(name="debug", default=False)    # User sets default=False (redundant)
        ]
        argv = ["script.py", "--debug"]  # Only debug flag present
        
        result = parse(specs, argv)
        
        assert result == {
            "verbose": False,  # Always defaults to False, even if user specified True
            "debug": True      # Present in argv
        }
        
        # Verify the specs themselves have default=False
        assert specs[0].default is False
        assert specs[1].default is False
    
    def test_parse_flags_with_dash_names(self):
        """Test parsing flags with dashes in names."""
        specs = [
            FlagArgSpec(name="dry-run"),
            FlagArgSpec(name="no-cache")
        ]
        argv = ["script.py", "--dry-run", "--no-cache"]
        
        result = parse(specs, argv)
        
        assert result == {
            "dry_run": True,    # Dashes converted to underscores
            "no_cache": True
        }
    
    def test_parse_complex_mixed_scenario(self):
        """Test a complex scenario with flags and positionals."""
        specs = [
            FlagArgSpec(name="verbose", aliases={"v"}),
            PositionalArgSpec(name="command"),
            FlagArgSpec(name="debug", aliases={"d"}),
            PositionalArgSpec(name="files", cardinality=Cardinality.one_or_more()),
            FlagArgSpec(name="quiet")
        ]
        argv = ["script.py", "-v", "process", "--debug", "file1.txt", "file2.txt", "--quiet"]
        
        result = parse(specs, argv)
        
        assert result == {
            "verbose": True,
            "command": "process",
            "debug": True,
            "files": ["file1.txt", "file2.txt"],
            "quiet": True
        }
    
    def test_parse_flags_consume_all_instances(self):
        """Test that flags consume all instances when repeated."""
        specs = [FlagArgSpec(name="verbose")]
        argv = ["script.py", "--verbose", "file1.txt", "--verbose", "file2.txt"]
        
        result = parse(specs, argv)
        
        assert result == {"verbose": True}  # Flag consumed all instances
    
    def test_parse_unsupported_argument_type(self):
        """Test parsing with unsupported argument type."""
        # Create a mock unsupported argument type
        class UnsupportedArgSpec(BaseArgSpec):
            pass
        
        specs = [UnsupportedArgSpec(name="test")]
        argv = ["script.py"]
        
        with self.assertRaises(ArgumentParsingError):
            parse(specs, argv)
    
    def test_parse_flags_with_explicit_boolean_values(self):
        """Test parsing flags with explicit boolean values in main parse function."""
        specs = [
            FlagArgSpec(name="verbose", aliases={"v"}),
            FlagArgSpec(name="debug", aliases={"d"})
        ]
        
        # Test with explicit true values
        argv1 = ["script.py", "--verbose=true", "-d", "false"]
        result1 = parse(specs, argv1)
        assert result1 == {"verbose": True, "debug": False}
        
        # Test with space-separated values
        argv2 = ["script.py", "-v", "true", "--debug=false"]
        result2 = parse(specs, argv2)
        assert result2 == {"verbose": True, "debug": False}
    
    def test_parse_flags_with_mixed_explicit_values_and_positionals(self):
        """Test parsing flags with explicit values mixed with positionals."""
        specs = [
            FlagArgSpec(name="verbose", aliases={"v"}),
            PositionalArgSpec(name="filename"),
            FlagArgSpec(name="debug", aliases={"d"})
        ]
        
        argv = ["script.py", "--verbose=false", "test.txt", "-d", "true"]
        result = parse(specs, argv)
        
        assert result == {
            "verbose": False,
            "filename": "test.txt",
            "debug": True
        }
    
    def test_parse_flags_with_case_insensitive_boolean_values(self):
        """Test parsing flags with case insensitive boolean values."""
        specs = [FlagArgSpec(name="verbose")]
        
        # Test various case combinations
        test_cases = [
            (["script.py", "--verbose=TRUE"], {"verbose": True}),
            (["script.py", "--verbose=True"], {"verbose": True}),
            (["script.py", "--verbose=true"], {"verbose": True}),
            (["script.py", "--verbose=FALSE"], {"verbose": False}),
            (["script.py", "--verbose=False"], {"verbose": False}),
            (["script.py", "--verbose=false"], {"verbose": False}),
            (["script.py", "--verbose", "TRUE"], {"verbose": True}),
            (["script.py", "--verbose", "FALSE"], {"verbose": False})
        ]
        
        for argv, expected in test_cases:
            result = parse(specs, argv)
            self.assertEqual(result, expected), f"Failed for {argv}"
    
    def test_parse_flags_with_non_boolean_explicit_values(self):
        """Test parsing flags with non-boolean explicit values (treated as present)."""
        specs = [FlagArgSpec(name="verbose")]
        
        # Non-boolean values in = format should be treated as flag present (True)
        test_cases = [
            ["script.py", "--verbose=yes"],
            ["script.py", "--verbose=1"],
            ["script.py", "--verbose=on"]
        ]
        
        for argv in test_cases:
            result = parse(specs, argv)
            assert result == {"verbose": True}, f"Failed for {argv}"
        
        # Non-boolean values in space-separated format should be treated as flag present (True)
        # but the value should remain for other parsers
        test_cases_space = [
            ["script.py", "--verbose", "yes"],
            ["script.py", "--verbose", "1"]
        ]
        
        for argv in test_cases_space:
            result = parse(specs, argv)
            assert result == {"verbose": True}, f"Failed for {argv}"

if __name__ == "__main__":
    unittest.main()
