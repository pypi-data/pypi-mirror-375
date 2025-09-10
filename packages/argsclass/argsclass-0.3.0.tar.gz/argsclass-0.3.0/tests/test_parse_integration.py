"""Tests for parse function integration with class inspection and ambiguity detection."""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from argsclass.parser import parse
from argsclass.models import PositionalArgSpec, OptionArgSpec, FlagArgSpec, Cardinality, PrimitiveType
from argsclass.descriptors import positional, option, flag
from argsclass.ambiguity import AmbiguityError


class TestParseWithArgSpecList(unittest.TestCase):
    """Test parse function with explicit ArgSpec lists."""
    
    def test_parse_with_positional_argspec_list(self):
        """Test parsing with positional ArgSpec list."""
        specs = [
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="output")
        ]
        argv = ["script.py", "input.txt", "output.txt"]
        
        result = parse(specs, argv)
        assert result == {"input": "input.txt", "output": "output.txt"}
    
    def test_parse_with_mixed_argspec_list(self):
        """Test parsing with mixed ArgSpec list."""
        specs = [
            PositionalArgSpec(name="command"),
            OptionArgSpec(name="output", aliases={"o"}),
            FlagArgSpec(name="verbose", aliases={"v"})
        ]
        argv = ["script.py", "process", "-o", "output.txt", "-v"]
        
        result = parse(specs, argv)
        assert result == {
            "command": "process",
            "output": "output.txt",
            "verbose": True
        }
    
    def test_parse_with_ambiguous_argspec_list_raises_error(self):
        """Test that parse raises AmbiguityError with ambiguous ArgSpec list."""
        specs = [
            PositionalArgSpec(name="files1", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="files2", cardinality=Cardinality.zero_or_more())
        ]
        argv = ["script.py", "file1.txt", "file2.txt"]
        
        with self.assertRaises(AmbiguityError):
            parse(specs, argv)
    
    def test_parse_with_ambiguous_argspec_list_validation_disabled(self):
        """Test that parse can skip validation with ambiguous ArgSpec list."""
        specs = [
            PositionalArgSpec(name="files1", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="files2", cardinality=Cardinality.zero_or_more())
        ]
        argv = ["script.py", "file1.txt", "file2.txt"]
        
        # Should not raise an exception when validation is disabled
        result = parse(specs, argv, validate_ambiguities=False)
        # Note: The actual parsing behavior with ambiguities is undefined,
        # but we're just testing that validation can be disabled


class TestParseWithClass(unittest.TestCase):
    """Test parse function with class inspection."""
    
    def test_parse_with_simple_class(self):
        """Test parsing with a simple class definition."""
        class Args:
            input_file: str = "input.txt"  # Give it a default value
            output_file: str = "output.txt"
            verbose: bool
        
        argv = ["script.py", "--verbose"]
        
        result = parse(Args, argv)
        assert isinstance(result, Args)
        assert result.input_file == "input.txt"
        assert result.output_file == "output.txt"
        assert result.verbose is True
    
    def test_parse_with_class_using_descriptors(self):
        """Test parsing with a class using descriptors."""
        class Args:
            command = positional(help_text="Command to execute")
            output = option(help_text="Output file", aliases={"o"}, default="output.txt")
            verbose = flag(help_text="Verbose output", aliases={"v"})
        
        argv = ["script.py", "process", "-v"]
        
        result = parse(Args, argv)
        assert isinstance(result, Args)
        assert result.command == "process"
        assert result.output == "output.txt"
        assert result.verbose is True
    
    def test_parse_with_mixed_class_definition(self):
        """Test parsing with a class mixing type hints and descriptors."""
        class Args:
            # Type hint with default (becomes option)
            output: str = "output.txt"
            
            # Boolean type hint (becomes flag)
            verbose: bool
            
            # Descriptor (becomes positional)
            command = positional(help_text="Command to execute")
            
            # Descriptor (becomes option)
            config = option(help_text="Config file", aliases={"c"})
        
        argv = ["script.py", "process", "--config", "config.json", "--verbose"]
        
        result = parse(Args, argv)
        assert isinstance(result, Args)
        assert result.output == "output.txt"
        assert result.verbose is True
        assert result.command == "process"
        assert result.config == "config.json"
    
    def test_parse_with_ambiguous_class_raises_error(self):
        """Test that parse raises AmbiguityError with ambiguous class definition."""
        class AmbiguousArgs:
            files1 = positional(cardinality=Cardinality.one_or_more())
            files2 = positional(cardinality=Cardinality.zero_or_more())
        
        argv = ["script.py", "file1.txt", "file2.txt"]
        
        with self.assertRaises(AmbiguityError):
            parse(AmbiguousArgs, argv)
    
    def test_parse_with_ambiguous_class_validation_disabled(self):
        """Test that parse can skip validation with ambiguous class definition."""
        class AmbiguousArgs:
            files1 = positional(cardinality=Cardinality.one_or_more())
            files2 = positional(cardinality=Cardinality.zero_or_more())
        
        argv = ["script.py", "file1.txt", "file2.txt"]
        
        # Should not raise an exception when validation is disabled
        result = parse(AmbiguousArgs, argv, validate_ambiguities=False)
        assert isinstance(result, AmbiguousArgs)
        # Note: The actual parsing behavior with ambiguities is undefined,
        # but we're just testing that validation can be disabled
    
    def test_parse_with_valid_class_no_ambiguities(self):
        """Test that parse works with valid class definition."""
        class ValidArgs:
            input_file = positional(help_text="Input file")
            output_file = positional(help_text="Output file")
            verbose = flag(help_text="Verbose output")
        
        argv = ["script.py", "input.txt", "output.txt", "--verbose"]
        
        result = parse(ValidArgs, argv)
        assert isinstance(result, ValidArgs)
        assert result.input_file == "input.txt"
        assert result.output_file == "output.txt"
        assert result.verbose is True


class TestParseEdgeCases(unittest.TestCase):
    """Test edge cases for parse function."""
    
    def test_parse_with_empty_class(self):
        """Test parsing with empty class definition."""
        class EmptyArgs:
            pass
        
        argv = ["script.py", "extra", "args"]
        
        result = parse(EmptyArgs, argv)
        assert isinstance(result, EmptyArgs)
    
    def test_parse_with_class_only_flags(self):
        """Test parsing with class containing only flags."""
        class FlagOnlyArgs:
            verbose: bool
            debug: bool
            quiet: bool
        
        argv = ["script.py", "--verbose", "--debug"]
        
        result = parse(FlagOnlyArgs, argv)
        assert isinstance(result, FlagOnlyArgs)
        assert result.verbose is True
        assert result.debug is True
        assert result.quiet is False
    
    def test_parse_with_class_only_options(self):
        """Test parsing with class containing only options."""
        class OptionOnlyArgs:
            input: str = "input.txt"
            output: str = "output.txt"
            port: int = 8080
        
        argv = ["script.py", "--input", "custom.txt"]
        
        result = parse(OptionOnlyArgs, argv)
        assert isinstance(result, OptionOnlyArgs)
        assert result.input == "custom.txt"
        assert result.output == "output.txt"
        assert result.port == 8080
    
    def test_parse_with_class_only_positionals(self):
        """Test parsing with class containing only positionals."""
        class PositionalOnlyArgs:
            command = positional(help_text="Command")
            input_file = positional(help_text="Input file")
            output_file = positional(help_text="Output file")
        
        argv = ["script.py", "process", "input.txt", "output.txt"]
        
        result = parse(PositionalOnlyArgs, argv)
        assert isinstance(result, PositionalOnlyArgs)
        assert result.command == "process"
        assert result.input_file == "input.txt"
        assert result.output_file == "output.txt"
    
    def test_parse_with_class_private_attributes_ignored(self):
        """Test that private attributes in class are ignored."""
        class ArgsWithPrivate:
            _private: str = "private"
            public: str = "public"
            __very_private: int = 42
        
        argv = ["script.py", "--public", "custom"]
        
        result = parse(ArgsWithPrivate, argv)
        assert isinstance(result, ArgsWithPrivate)
        assert result.public == "custom"
    
    def test_parse_with_class_methods_ignored(self):
        """Test that methods in class are ignored."""
        class ArgsWithMethods:
            name: str = "default"
            
            def method(self):
                return "method"
            
            @staticmethod
            def static_method():
                return "static"
        
        argv = ["script.py", "--name", "custom"]
        
        result = parse(ArgsWithMethods, argv)
        assert isinstance(result, ArgsWithMethods)
        assert result.name == "custom"


class TestParseValidationOptions(unittest.TestCase):
    """Test parse function validation options."""
    
    def test_parse_validation_enabled_by_default(self):
        """Test that validation is enabled by default."""
        class AmbiguousArgs:
            files1 = positional(cardinality=Cardinality.one_or_more())
            files2 = positional(cardinality=Cardinality.zero_or_more())
        
        argv = ["script.py", "file1.txt", "file2.txt"]
        
        with self.assertRaises(AmbiguityError):
            parse(AmbiguousArgs, argv)
    
    def test_parse_validation_can_be_disabled(self):
        """Test that validation can be disabled."""
        class AmbiguousArgs:
            files1 = positional(cardinality=Cardinality.one_or_more())
            files2 = positional(cardinality=Cardinality.zero_or_more())
        
        argv = ["script.py", "file1.txt", "file2.txt"]
        
        # Should not raise an exception when validation is disabled
        result = parse(AmbiguousArgs, argv, validate_ambiguities=False)
        assert isinstance(result, AmbiguousArgs)
        # Note: The actual parsing behavior with ambiguities is undefined,
        # but we're just testing that validation can be disabled
    
    def test_parse_validation_with_valid_specs(self):
        """Test that validation passes with valid specs."""
        class ValidArgs:
            input_file = positional(help_text="Input file")
            output_file = positional(help_text="Output file")
        
        argv = ["script.py", "input.txt", "output.txt"]
        
        result = parse(ValidArgs, argv, validate_ambiguities=True)
        assert isinstance(result, ValidArgs)
        assert result.input_file == "input.txt"
        assert result.output_file == "output.txt"


class TestParseBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility of parse function."""
    
    def test_parse_with_existing_argspec_list_works(self):
        """Test that existing ArgSpec list usage still works."""
        specs = [
            PositionalArgSpec(name="input"),
            OptionArgSpec(name="output", aliases={"o"}),
            FlagArgSpec(name="verbose", aliases={"v"})
        ]
        argv = ["script.py", "input.txt", "-o", "output.txt", "-v"]
        
        result = parse(specs, argv)
        assert result == {
            "input": "input.txt",
            "output": "output.txt",
            "verbose": True
        }
    
    def test_parse_with_existing_argspec_list_and_validation(self):
        """Test that existing ArgSpec list usage works with validation."""
        specs = [
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="output")
        ]
        argv = ["script.py", "input.txt", "output.txt"]
        
        result = parse(specs, argv, validate_ambiguities=True)
        assert result == {
            "input": "input.txt",
            "output": "output.txt"
        }

if __name__ == "__main__":
    unittest.main()
