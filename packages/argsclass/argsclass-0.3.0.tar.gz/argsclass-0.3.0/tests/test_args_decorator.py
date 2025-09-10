"""Tests for @args class decorator."""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import sys
from argsclass import args
from argsclass.descriptors import positional, option, flag
from argsclass.models import Cardinality
from argsclass.ambiguity import AmbiguityError
from argsclass.parser import ArgumentParsingError


class TestArgsDecoratorBasic(unittest.TestCase):
    """Test basic functionality of @args decorator."""
    
    def test_args_decorator_basic_usage_with_brackets(self):
        """Test basic @args() decorator usage."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose", "--input_file", "custom.txt"]
        
        @args()
        class Args:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
        
        assert Args.input_file == "custom.txt"
        assert Args.output_file == "output.txt"
        assert Args.verbose is True
        assert hasattr(Args, '_original_class')
        assert hasattr(Args, '_program_name')
        assert Args._program_name == "script.py"
        
        sys.argv = original_argv
    
    def test_args_decorator_basic_usage_without_brackets(self):
        """Test basic @args decorator usage without brackets."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose", "--input_file", "custom.txt"]
        
        @args
        class Args:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
        
        assert Args.input_file == "custom.txt"
        assert Args.output_file == "output.txt"
        assert Args.verbose is True
        assert hasattr(Args, '_original_class')
        assert hasattr(Args, '_program_name')
        assert Args._program_name == "script.py"
        
        sys.argv = original_argv
    
    def test_args_decorator_with_descriptors_with_brackets(self):
        """Test @args() decorator with descriptors."""
        original_argv = sys.argv
        sys.argv = ["script.py", "process", "-v"]
        
        @args()
        class Args:
            command = positional(help_text="Command to execute")
            output = option(help_text="Output file", aliases={"o"}, default="output.txt")
            verbose = flag(help_text="Verbose output", aliases={"v"})
        
        assert Args.command == "process"
        assert Args.output == "output.txt"
        assert Args.verbose is True
        assert hasattr(Args, '_original_class')
        
        sys.argv = original_argv
    
    def test_args_decorator_with_descriptors_without_brackets(self):
        """Test @args decorator with descriptors without brackets."""
        original_argv = sys.argv
        sys.argv = ["script.py", "process", "-v"]
        
        @args
        class Args:
            command = positional(help_text="Command to execute")
            output = option(help_text="Output file", aliases={"o"}, default="output.txt")
            verbose = flag(help_text="Verbose output", aliases={"v"})
        
        assert Args.command == "process"
        assert Args.output == "output.txt"
        assert Args.verbose is True
        assert hasattr(Args, '_original_class')
        
        sys.argv = original_argv
    
    def test_args_decorator_with_mixed_definition_with_brackets(self):
        """Test @args() decorator with mixed type hints and descriptors."""
        original_argv = sys.argv
        sys.argv = ["script.py", "process", "--config", "config.json", "--verbose"]
        
        @args()
        class Args:
            # Type hint with default (becomes option)
            output: str = "output.txt"
            
            # Boolean type hint (becomes flag)
            verbose: bool
            
            # Descriptor (becomes positional)
            command = positional(help_text="Command to execute")
            
            # Descriptor (becomes option)
            config = option(help_text="Config file", aliases={"c"})
        
        assert Args.output == "output.txt"
        assert Args.verbose is True
        assert Args.command == "process"
        assert Args.config == "config.json"
        assert hasattr(Args, '_original_class')
        
        sys.argv = original_argv
    
    def test_args_decorator_with_mixed_definition_without_brackets(self):
        """Test @args decorator with mixed type hints and descriptors without brackets."""
        original_argv = sys.argv
        sys.argv = ["script.py", "process", "--config", "config.json", "--verbose"]
        
        @args
        class Args:
            # Type hint with default (becomes option)
            output: str = "output.txt"
            
            # Boolean type hint (becomes flag)
            verbose: bool
            
            # Descriptor (becomes positional)
            command = positional(help_text="Command to execute")
            
            # Descriptor (becomes option)
            config = option(help_text="Config file", aliases={"c"})
        
        assert Args.output == "output.txt"
        assert Args.verbose is True
        assert Args.command == "process"
        assert Args.config == "config.json"
        assert hasattr(Args, '_original_class')
        
        sys.argv = original_argv


class TestArgsDecoratorOptions(unittest.TestCase):
    """Test @args decorator with various options."""
    
    def test_args_decorator_with_program_name(self):
        """Test @args() decorator with custom program name."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose"]
        
        @args(program_name="myapp")
        class Args:
            verbose: bool
        
        assert Args.verbose is True
        assert Args._program_name == "myapp"
        
        sys.argv = original_argv
    
    def test_args_decorator_with_validate_ambiguities_false(self):
        """Test @args() decorator with validation disabled."""
        original_argv = sys.argv
        sys.argv = ["script.py", "file1.txt", "file2.txt"]
        
        @args(validate_ambiguities=False)
        class AmbiguousArgs:
            files1 = positional(cardinality=Cardinality.one_or_more())
            files2 = positional(cardinality=Cardinality.zero_or_more())
        
        assert hasattr(AmbiguousArgs, 'files1')
        assert hasattr(AmbiguousArgs, 'files2')
        assert AmbiguousArgs._validate_ambiguities is False
        
        sys.argv = original_argv
    
    def test_args_decorator_with_explicit_argv(self):
        """Test @args() decorator with explicit argv."""
        original_argv = sys.argv
        sys.argv = ["different_script.py", "--other", "args"]
        
        @args(argv=["script.py", "--verbose", "--input_file", "custom.txt"])
        class Args:
            input_file: str = "input.txt"
            verbose: bool
        
        assert Args.input_file == "custom.txt"
        assert Args.verbose is True
        assert Args._program_name == "script.py"
        
        sys.argv = original_argv
    
    def test_args_decorator_with_all_options(self):
        """Test @args() decorator with all options specified."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose"]
        
        @args(
            argv=["script.py", "--verbose", "--input_file", "custom.txt"],
            validate_ambiguities=False,
            program_name="myapp"
        )
        class Args:
            input_file: str = "input.txt"
            verbose: bool
        
        assert Args.input_file == "custom.txt"
        assert Args.verbose is True
        assert Args._program_name == "myapp"
        assert Args._validate_ambiguities is False
        
        sys.argv = original_argv


class TestArgsDecoratorEdgeCases(unittest.TestCase):
    """Test edge cases for @args decorator."""
    
    def test_args_decorator_with_empty_class(self):
        """Test @args() decorator with empty class."""
        original_argv = sys.argv
        sys.argv = ["script.py", "extra", "args"]
        
        @args()
        class EmptyArgs:
            pass
        
        assert hasattr(EmptyArgs, '_original_class')
        assert hasattr(EmptyArgs, '_program_name')
        
        sys.argv = original_argv
    
    def test_args_decorator_with_only_flags(self):
        """Test @args() decorator with class containing only flags."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose", "--debug"]
        
        @args()
        class FlagOnlyArgs:
            verbose: bool
            debug: bool
            quiet: bool
        
        assert FlagOnlyArgs.verbose is True
        assert FlagOnlyArgs.debug is True
        assert FlagOnlyArgs.quiet is False
        
        sys.argv = original_argv
    
    def test_args_decorator_with_only_options(self):
        """Test @args() decorator with class containing only options."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--input", "custom.txt"]
        
        @args()
        class OptionOnlyArgs:
            input: str = "input.txt"
            output: str = "output.txt"
            port: int = 8080
        
        assert OptionOnlyArgs.input == "custom.txt"
        assert OptionOnlyArgs.output == "output.txt"
        assert OptionOnlyArgs.port == 8080
        
        sys.argv = original_argv
    
    def test_args_decorator_with_only_positionals(self):
        """Test @args() decorator with class containing only positionals."""
        original_argv = sys.argv
        sys.argv = ["script.py", "process", "input.txt", "output.txt"]
        
        @args()
        class PositionalOnlyArgs:
            command = positional(help_text="Command")
            input_file = positional(help_text="Input file")
            output_file = positional(help_text="Output file")
        
        assert PositionalOnlyArgs.command == "process"
        assert PositionalOnlyArgs.input_file == "input.txt"
        assert PositionalOnlyArgs.output_file == "output.txt"
        
        sys.argv = original_argv
    
    def test_args_decorator_with_private_attributes_ignored(self):
        """Test that private attributes in class are ignored."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--public", "custom"]
        
        @args()
        class ArgsWithPrivate:
            _private: str = "private"
            public: str = "public"
            __very_private: int = 42
        
        assert ArgsWithPrivate.public == "custom"
        assert hasattr(ArgsWithPrivate, '_original_class')
        
        sys.argv = original_argv
    
    def test_args_decorator_with_methods_ignored(self):
        """Test that methods in class are ignored."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--name", "custom"]
        
        @args()
        class ArgsWithMethods:
            name: str = "default"
            
            def method(self):
                return "method"
            
            @staticmethod
            def static_method():
                return "static"
        
        assert ArgsWithMethods.name == "custom"
        assert hasattr(ArgsWithMethods, '_original_class')
        
        sys.argv = original_argv


class TestArgsDecoratorValidation(unittest.TestCase):
    """Test validation options for @args decorator."""
    
    def test_args_decorator_validation_enabled_by_default(self):
        """Test that validation is enabled by default."""
        original_argv = sys.argv
        sys.argv = ["script.py", "file1.txt", "file2.txt"]
        
        with self.assertRaises(AmbiguityError):
            @args()
            class AmbiguousArgs:
                files1 = positional(cardinality=Cardinality.one_or_more())
                files2 = positional(cardinality=Cardinality.zero_or_more())
        
        sys.argv = original_argv
    
    def test_args_decorator_validation_can_be_disabled(self):
        """Test that validation can be disabled."""
        original_argv = sys.argv
        sys.argv = ["script.py", "file1.txt", "file2.txt"]
        
        # Should not raise an exception when validation is disabled
        @args(validate_ambiguities=False)
        class AmbiguousArgs:
            files1 = positional(cardinality=Cardinality.one_or_more())
            files2 = positional(cardinality=Cardinality.zero_or_more())
        
        assert hasattr(AmbiguousArgs, 'files1')
        assert hasattr(AmbiguousArgs, 'files2')
        
        sys.argv = original_argv
    
    def test_args_decorator_validation_with_valid_specs(self):
        """Test that validation passes with valid specs."""
        original_argv = sys.argv
        sys.argv = ["script.py", "input.txt", "output.txt"]
        
        @args(validate_ambiguities=True)
        class ValidArgs:
            input_file = positional(help_text="Input file")
            output_file = positional(help_text="Output file")
        
        assert ValidArgs.input_file == "input.txt"
        assert ValidArgs.output_file == "output.txt"
        
        sys.argv = original_argv


class TestArgsDecoratorErrorHandling(unittest.TestCase):
    """Test error handling for @args decorator."""
    
    def test_args_decorator_with_invalid_arguments_raises_value_error(self):
        """Test that invalid arguments raise ValueError."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--port", "not_a_number"]
        
        with self.assertRaises(SystemExit) as exc_info:
            @args()
            class Args:
                port: int = 8080
        self.assertEqual(exc_info.exception.code, 2)
        
        sys.argv = original_argv
    
    def test_args_decorator_with_missing_required_arguments_raises_value_error(self):
        """Test that missing required arguments raise ValueError."""
        original_argv = sys.argv
        sys.argv = ["script.py"]  # No required argument provided
        
        with self.assertRaises(SystemExit) as exc_info:
            @args()
            class Args:
                required = positional(help_text="Required argument")
        self.assertEqual(exc_info.exception.code, 2)
        
        sys.argv = original_argv


class TestArgsDecoratorComplexTypes(unittest.TestCase):
    """Test @args decorator with complex types and cardinality."""
    
    def test_args_decorator_with_list_arguments(self):
        """Test parsing with arguments that accept multiple values."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--exclude", "temp.txt", "backup.txt"]
        
        @args()
        class Args:
            exclude = option(help_text="Files to exclude", cardinality=Cardinality.zero_or_more())
        
        assert Args.exclude == ["temp.txt"]
        
        sys.argv = original_argv
    
    def test_args_decorator_with_optional_arguments(self):
        """Test parsing with optional arguments."""
        original_argv = sys.argv
        sys.argv = ["script.py", "required_value", "--flag"]
        
        @args()
        class Args:
            required = positional(help_text="Required argument")
            optional = positional(help_text="Optional argument", cardinality=Cardinality.zero_or_one())
            flag: bool
        
        assert Args.required == "required_value"
        assert Args.optional is None
        assert Args.flag is True
        
        sys.argv = original_argv
    
    def test_args_decorator_with_choices(self):
        """Test parsing with choice constraints."""
        original_argv = sys.argv
        sys.argv = ["script.py", "medium", "--mode", "prod"]
        
        @args()
        class Args:
            mode = option(help_text="Mode", choices=["dev", "prod", "test"], default="dev")
            level = positional(help_text="Level", choices=["low", "medium", "high"])
        
        assert Args.mode == "prod"
        assert Args.level == "medium"
        
        sys.argv = original_argv


class TestArgsDecoratorComparisonWithParse(unittest.TestCase):
    """Test that @args decorator produces equivalent results to parse."""
    
    def test_args_decorator_equivalent_to_parse(self):
        """Test that @args decorator produces equivalent results to parse."""
        from argsclass import parse
        
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose", "--port", "9000", "--input_file", "custom.txt"]
        
        # Parse using @args decorator
        @args()
        class ArgsDecorator:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
            port: int = 8080
        
        # Parse using parse function
        class ArgsParse:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
            port: int = 8080
        
        parsed_instance = parse(ArgsParse)
        
        # Compare results
        assert ArgsDecorator.input_file == parsed_instance.input_file
        assert ArgsDecorator.output_file == parsed_instance.output_file
        assert ArgsDecorator.verbose == parsed_instance.verbose
        assert ArgsDecorator.port == parsed_instance.port
        
        # Verify the decorator instance has the expected attributes
        assert hasattr(ArgsDecorator, "input_file")
        assert hasattr(ArgsDecorator, "output_file")
        assert hasattr(ArgsDecorator, "verbose")
        assert hasattr(ArgsDecorator, "port")
        
        sys.argv = original_argv
    
    def test_args_decorator_with_and_without_brackets_equivalent(self):
        """Test that @args and @args() produce equivalent results."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose", "--input_file", "custom.txt"]
        
        # Parse using @args (no brackets)
        @args
        class ArgsNoBrackets:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
        
        # Parse using @args() (with brackets)
        @args()
        class ArgsWithBrackets:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
        
        # Compare results
        assert ArgsNoBrackets.input_file == ArgsWithBrackets.input_file
        assert ArgsNoBrackets.output_file == ArgsWithBrackets.output_file
        assert ArgsNoBrackets.verbose == ArgsWithBrackets.verbose
        assert ArgsNoBrackets._program_name == ArgsWithBrackets._program_name
        assert ArgsNoBrackets._validate_ambiguities == ArgsWithBrackets._validate_ambiguities
        
        sys.argv = original_argv


class TestArgsDecoratorIntrospection(unittest.TestCase):
    """Test introspection capabilities of @args decorator."""
    
    def test_args_decorator_preserves_original_class(self):
        """Test that @args decorator preserves original class for introspection."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose"]
        
        @args()
        class Args:
            verbose: bool
        
        assert hasattr(Args, '_original_class')
        assert Args._original_class.__name__ == "Args"
        assert hasattr(Args._original_class, '__dataclass_fields__')
        assert 'verbose' in Args._original_class.__dataclass_fields__
        
        sys.argv = original_argv
    
    def test_args_decorator_program_name_attribute(self):
        """Test that @args decorator sets program name attribute."""
        original_argv = sys.argv
        sys.argv = ["my_script.py", "--verbose"]
        
        @args()
        class Args:
            verbose: bool
        
        assert hasattr(Args, '_program_name')
        assert Args._program_name == "my_script.py"
        
        sys.argv = original_argv
    
    def test_args_decorator_validation_attribute(self):
        """Test that @args decorator sets validation attribute."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose"]
        
        @args(validate_ambiguities=False)
        class Args:
            verbose: bool
        
        assert hasattr(Args, '_validate_ambiguities')
        assert Args._validate_ambiguities is False
        
        sys.argv = original_argv

if __name__ == "__main__":
    unittest.main()
