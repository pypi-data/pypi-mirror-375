"""Tests for @parser class decorator."""

import unittest
from argsclass.help import ValidationErrorCollector
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import sys
from argsclass import parser
from argsclass.descriptors import positional, option, flag
from argsclass.models import Cardinality
from argsclass.ambiguity import AmbiguityError
from argsclass.parser import ArgumentParsingError


class TestParserDecoratorBasic(unittest.TestCase):
    """Test basic functionality of @parser decorator."""
    
    def test_parser_decorator_basic_usage_with_brackets(self):
        """Test basic @parser() decorator usage."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose", "--input_file", "custom.txt"]
        
        @parser()
        class Args:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
        
        assert hasattr(Args, 'parse')
        assert callable(Args.parse)
        
        # Parse when we want to
        args = Args.parse()
        assert args.input_file == "custom.txt"
        assert args.output_file == "output.txt"
        assert args.verbose is True
        assert hasattr(args, '_original_class')
        assert hasattr(args, '_program_name')
        assert args._program_name == "script.py"
        
        sys.argv = original_argv
    
    def test_parser_decorator_basic_usage_without_brackets(self):
        """Test basic @parser decorator usage without brackets."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose", "--input_file", "custom.txt"]
        
        @parser
        class Args:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
        
        assert hasattr(Args, 'parse')
        assert callable(Args.parse)
        
        # Parse when we want to
        args = Args.parse()
        assert args.input_file == "custom.txt"
        assert args.output_file == "output.txt"
        assert args.verbose is True
        assert hasattr(args, '_original_class')
        assert hasattr(args, '_program_name')
        assert args._program_name == "script.py"
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_descriptors_with_brackets(self):
        """Test @parser() decorator with descriptors."""
        original_argv = sys.argv
        sys.argv = ["script.py", "process", "-v"]
        
        @parser()
        class Args:
            command = positional(help_text="Command to execute")
            output = option(help_text="Output file", aliases={"o"}, default="output.txt")
            verbose = flag(help_text="Verbose output", aliases={"v"})
        
        assert hasattr(Args, 'parse')
        
        # Parse when we want to
        args = Args.parse()
        assert args.command == "process"
        assert args.output == "output.txt"
        assert args.verbose is True
        assert hasattr(args, '_original_class')
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_descriptors_without_brackets(self):
        """Test @parser decorator with descriptors without brackets."""
        original_argv = sys.argv
        sys.argv = ["script.py", "process", "-v"]
        
        @parser
        class Args:
            command = positional(help_text="Command to execute")
            output = option(help_text="Output file", aliases={"o"}, default="output.txt")
            verbose = flag(help_text="Verbose output", aliases={"v"})
        
        assert hasattr(Args, 'parse')
        
        # Parse when we want to
        args = Args.parse()
        assert args.command == "process"
        assert args.output == "output.txt"
        assert args.verbose is True
        assert hasattr(args, '_original_class')
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_mixed_definition_with_brackets(self):
        """Test @parser() decorator with mixed type hints and descriptors."""
        original_argv = sys.argv
        sys.argv = ["script.py", "process", "--config", "config.json", "--verbose"]
        
        @parser()
        class Args:
            # Type hint with default (becomes option)
            output: str = "output.txt"
            
            # Boolean type hint (becomes flag)
            verbose: bool
            
            # Descriptor (becomes positional)
            command = positional(help_text="Command to execute")
            
            # Descriptor (becomes option)
            config = option(help_text="Config file", aliases={"c"})
        
        assert hasattr(Args, 'parse')
        
        # Parse when we want to
        args = Args.parse()
        assert args.output == "output.txt"
        assert args.verbose is True
        assert args.command == "process"
        assert args.config == "config.json"
        assert hasattr(args, '_original_class')
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_mixed_definition_without_brackets(self):
        """Test @parser decorator with mixed type hints and descriptors without brackets."""
        original_argv = sys.argv
        sys.argv = ["script.py", "process", "--config", "config.json", "--verbose"]
        
        @parser
        class Args:
            # Type hint with default (becomes option)
            output: str = "output.txt"
            
            # Boolean type hint (becomes flag)
            verbose: bool
            
            # Descriptor (becomes positional)
            command = positional(help_text="Command to execute")
            
            # Descriptor (becomes option)
            config = option(help_text="Config file", aliases={"c"})
        
        assert hasattr(Args, 'parse')
        
        # Parse when we want to
        args = Args.parse()
        assert args.output == "output.txt"
        assert args.verbose is True
        assert args.command == "process"
        assert args.config == "config.json"
        assert hasattr(args, '_original_class')
        
        sys.argv = original_argv


class TestParserDecoratorOptions(unittest.TestCase):
    """Test @parser decorator with various options."""
    
    def test_parser_decorator_with_program_name(self):
        """Test @parser() decorator with custom program name."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose"]
        
        @parser(program_name="myapp")
        class Args:
            verbose: bool
        
        assert hasattr(Args, 'parse')
        
        # Parse when we want to
        args = Args.parse()
        assert args.verbose is True
        assert args._program_name == "myapp"
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_validate_ambiguities_false(self):
        """Test @parser() decorator with validation disabled."""
        original_argv = sys.argv
        sys.argv = ["script.py", "file1.txt", "file2.txt"]
        
        @parser(validate_ambiguities=False)
        class AmbiguousArgs:
            files1 = positional(cardinality=Cardinality.one_or_more())
            files2 = positional(cardinality=Cardinality.zero_or_more())
        
        assert hasattr(AmbiguousArgs, 'parse')
        
        # Parse when we want to
        args = AmbiguousArgs.parse()
        assert hasattr(args, 'files1')
        assert hasattr(args, 'files2')
        assert args._validate_ambiguities is False
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_explicit_argv(self):
        """Test @parser() decorator with explicit argv."""
        original_argv = sys.argv
        sys.argv = ["different_script.py", "--other", "args"]
        
        @parser(argv=["script.py", "--verbose", "--input_file", "custom.txt"])
        class Args:
            input_file: str = "input.txt"
            verbose: bool
        
        assert hasattr(Args, 'parse')
        
        # Parse when we want to
        args = Args.parse()
        assert args.input_file == "custom.txt"
        assert args.verbose is True
        assert args._program_name == "script.py"
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_all_options(self):
        """Test @parser() decorator with all options specified."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose"]
        
        @parser(
            argv=["script.py", "--verbose", "--input_file", "custom.txt"],
            validate_ambiguities=False,
            program_name="myapp"
        )
        class Args:
            input_file: str = "input.txt"
            verbose: bool
        
        assert hasattr(Args, 'parse')
        
        # Parse when we want to
        args = Args.parse()
        assert args.input_file == "custom.txt"
        assert args.verbose is True
        assert args._program_name == "myapp"
        assert args._validate_ambiguities is False
        
        sys.argv = original_argv


class TestParserDecoratorCustomArgv(unittest.TestCase):
    """Test @parser decorator with custom argv parameter."""
    
    def test_parser_decorator_parse_with_custom_argv(self):
        """Test that parse() method accepts custom argv parameter."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose"]
        
        @parser()
        class Args:
            input_file: str = "input.txt"
            verbose: bool
        
        assert hasattr(Args, 'parse')
        
        # Parse with default argv
        args1 = Args.parse()
        assert args1.verbose is True
        assert args1.input_file == "input.txt"  # Default value
        
        # Parse with custom argv
        custom_argv = ["script.py", "--verbose", "--input_file", "custom.txt"]
        args2 = Args.parse(custom_argv)
        assert args2.verbose is True
        assert args2.input_file == "custom.txt"
        
        sys.argv = original_argv
    
    def test_parser_decorator_parse_with_custom_argv_override(self):
        """Test that custom argv overrides decorator argv."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose"]
        
        @parser(argv=["script.py", "--verbose", "--input_file", "decorator.txt"])
        class Args:
            input_file: str = "input.txt"
            verbose: bool
        
        assert hasattr(Args, 'parse')
        
        # Parse with decorator argv
        args1 = Args.parse()
        assert args1.verbose is True
        assert args1.input_file == "decorator.txt"
        
        # Parse with custom argv (should override decorator argv)
        custom_argv = ["script.py", "--verbose", "--input_file", "custom.txt"]
        args2 = Args.parse(custom_argv)
        assert args2.verbose is True
        assert args2.input_file == "custom.txt"
        
        sys.argv = original_argv


class TestParserDecoratorEdgeCases(unittest.TestCase):
    """Test edge cases for @parser decorator."""
    
    def test_parser_decorator_with_empty_class(self):
        """Test @parser() decorator with empty class."""
        original_argv = sys.argv
        sys.argv = ["script.py", "extra", "args"]
        
        @parser()
        class EmptyArgs:
            pass
        
        assert hasattr(EmptyArgs, 'parse')
        
        # Parse when we want to
        args = EmptyArgs.parse()
        assert hasattr(args, '_original_class')
        assert hasattr(args, '_program_name')
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_only_flags(self):
        """Test @parser() decorator with class containing only flags."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose", "--debug"]
        
        @parser()
        class FlagOnlyArgs:
            verbose: bool
            debug: bool
            quiet: bool
        
        assert hasattr(FlagOnlyArgs, 'parse')
        
        # Parse when we want to
        args = FlagOnlyArgs.parse()
        assert args.verbose is True
        assert args.debug is True
        assert args.quiet is False
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_only_options(self):
        """Test @parser() decorator with class containing only options."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--input", "custom.txt"]
        
        @parser()
        class OptionOnlyArgs:
            input: str = "input.txt"
            output: str = "output.txt"
            port: int = 8080
        
        assert hasattr(OptionOnlyArgs, 'parse')
        
        # Parse when we want to
        args = OptionOnlyArgs.parse()
        assert args.input == "custom.txt"
        assert args.output == "output.txt"
        assert args.port == 8080
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_only_positionals(self):
        """Test @parser() decorator with class containing only positionals."""
        original_argv = sys.argv
        sys.argv = ["script.py", "process", "input.txt", "output.txt"]
        
        @parser()
        class PositionalOnlyArgs:
            command = positional(help_text="Command")
            input_file = positional(help_text="Input file")
            output_file = positional(help_text="Output file")
        
        assert hasattr(PositionalOnlyArgs, 'parse')
        
        # Parse when we want to
        args = PositionalOnlyArgs.parse()
        assert args.command == "process"
        assert args.input_file == "input.txt"
        assert args.output_file == "output.txt"
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_private_attributes_ignored(self):
        """Test that private attributes in class are ignored."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--public", "custom"]
        
        @parser()
        class ArgsWithPrivate:
            _private: str = "private"
            public: str = "public"
            __very_private: int = 42
        
        assert hasattr(ArgsWithPrivate, 'parse')
        
        # Parse when we want to
        args = ArgsWithPrivate.parse()
        assert args.public == "custom"
        assert hasattr(args, '_original_class')
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_methods_ignored(self):
        """Test that methods in class are ignored."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--name", "custom"]
        
        @parser()
        class ArgsWithMethods:
            name: str = "default"
            
            def method(self):
                return "method"
            
            @staticmethod
            def static_method():
                return "static"
        
        assert hasattr(ArgsWithMethods, 'parse')
        
        # Parse when we want to
        args = ArgsWithMethods.parse()
        assert args.name == "custom"
        assert hasattr(args, '_original_class')
        
        sys.argv = original_argv


class TestParserDecoratorValidation(unittest.TestCase):
    """Test validation options for @parser decorator."""
    
    def test_parser_decorator_validation_enabled_by_default(self):
        """Test that validation is enabled by default."""
        original_argv = sys.argv
        sys.argv = ["script.py", "file1.txt", "file2.txt"]
        
        @parser()
        class AmbiguousArgs:
            files1 = positional(cardinality=Cardinality.one_or_more())
            files2 = positional(cardinality=Cardinality.zero_or_more())
        
        assert hasattr(AmbiguousArgs, 'parse')
        
        with self.assertRaises(AmbiguityError):
            AmbiguousArgs.parse()
        
        sys.argv = original_argv
    
    def test_parser_decorator_validation_can_be_disabled(self):
        """Test that validation can be disabled."""
        original_argv = sys.argv
        sys.argv = ["script.py", "file1.txt", "file2.txt"]
        
        @parser(validate_ambiguities=False)
        class AmbiguousArgs:
            files1 = positional(cardinality=Cardinality.one_or_more())
            files2 = positional(cardinality=Cardinality.zero_or_more())
        
        assert hasattr(AmbiguousArgs, 'parse')
        
        # Should not raise an exception when validation is disabled
        args = AmbiguousArgs.parse()
        assert hasattr(args, 'files1')
        assert hasattr(args, 'files2')
        
        sys.argv = original_argv
    
    def test_parser_decorator_validation_with_valid_specs(self):
        """Test that validation passes with valid specs."""
        original_argv = sys.argv
        sys.argv = ["script.py", "input.txt", "output.txt"]
        
        @parser(validate_ambiguities=True)
        class ValidArgs:
            input_file = positional(help_text="Input file")
            output_file = positional(help_text="Output file")
        
        assert hasattr(ValidArgs, 'parse')
        
        # Parse when we want to
        args = ValidArgs.parse()
        assert args.input_file == "input.txt"
        assert args.output_file == "output.txt"
        
        sys.argv = original_argv


class TestParserDecoratorErrorHandling(unittest.TestCase):
    """Test error handling for @parser decorator."""
    
    def test_parser_decorator_with_invalid_arguments_raises_value_error(self):
        """Test that invalid arguments raise ValueError."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--port", "not_a_number"]
        
        @parser()
        class Args:
            port: int = 8080
        
        assert hasattr(Args, 'parse')
        
        with self.assertRaises(SystemExit) as exc_info:
            Args.parse()
        self.assertEqual(exc_info.exception.code, 2)
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_missing_required_arguments_raises_value_error(self):
        """Test that missing required arguments raise ValueError."""
        original_argv = sys.argv
        sys.argv = ["script.py"]  # No required argument provided
        
        @parser()
        class Args:
            required = positional(help_text="Required argument")
        
        assert hasattr(Args, 'parse')
        
        with self.assertRaises(SystemExit) as exc_info:
            Args.parse()
        self.assertEqual(exc_info.exception.code, 2)
        
        sys.argv = original_argv


class TestParserDecoratorComparisonWithArgs(unittest.TestCase):
    """Test that @parser decorator produces equivalent results to @args."""
    
    def test_parser_decorator_equivalent_to_args(self):
        """Test that @parser decorator produces equivalent results to @args."""
        from argsclass import args
        
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose", "--port", "9000", "--input_file", "custom.txt"]
        
        # Parse using @parser decorator
        @parser()
        class ParserArgs:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
            port: int = 8080
        
        # Parse using @args decorator
        @args()
        class ArgsDecorator:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
            port: int = 8080
        
        # Compare results
        parser_instance = ParserArgs.parse()
        assert parser_instance.input_file == ArgsDecorator.input_file
        assert parser_instance.output_file == ArgsDecorator.output_file
        assert parser_instance.verbose == ArgsDecorator.verbose
        assert parser_instance.port == ArgsDecorator.port
        
        # Verify the parser instance has the expected attributes
        assert hasattr(parser_instance, "input_file")
        assert hasattr(parser_instance, "output_file")
        assert hasattr(parser_instance, "verbose")
        assert hasattr(parser_instance, "port")
        
        sys.argv = original_argv
    
    def test_parser_decorator_with_and_without_brackets_equivalent(self):
        """Test that @parser and @parser() produce equivalent results."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose", "--input_file", "custom.txt"]
        
        # Parse using @parser (no brackets)
        @parser
        class ParserNoBrackets:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
        
        # Parse using @parser() (with brackets)
        @parser()
        class ParserWithBrackets:
            input_file: str = "input.txt"
            output_file: str = "output.txt"
            verbose: bool
        
        # Compare results
        args_no_brackets = ParserNoBrackets.parse()
        args_with_brackets = ParserWithBrackets.parse()
        
        assert args_no_brackets.input_file == args_with_brackets.input_file
        assert args_no_brackets.output_file == args_with_brackets.output_file
        assert args_no_brackets.verbose == args_with_brackets.verbose
        assert args_no_brackets._program_name == args_with_brackets._program_name
        assert args_no_brackets._validate_ambiguities == args_with_brackets._validate_ambiguities
        
        sys.argv = original_argv


class TestParserDecoratorIntrospection(unittest.TestCase):
    """Test introspection capabilities of @parser decorator."""
    
    def test_parser_decorator_preserves_original_class(self):
        """Test that @parser decorator preserves original class for introspection."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose"]
        
        @parser()
        class Args:
            verbose: bool
        
        assert hasattr(Args, 'parse')
        
        # Parse when we want to
        args = Args.parse()
        assert hasattr(args, '_original_class')
        assert args._original_class.__name__ == "Args"
        assert hasattr(args._original_class, '__dataclass_fields__')
        assert 'verbose' in args._original_class.__dataclass_fields__
        
        sys.argv = original_argv
    
    def test_parser_decorator_program_name_attribute(self):
        """Test that @parser decorator sets program name attribute."""
        original_argv = sys.argv
        sys.argv = ["my_script.py", "--verbose"]
        
        @parser()
        class Args:
            verbose: bool
        
        assert hasattr(Args, 'parse')
        
        # Parse when we want to
        args = Args.parse()
        assert hasattr(args, '_program_name')
        assert args._program_name == "my_script.py"
        
        sys.argv = original_argv
    
    def test_parser_decorator_validation_attribute(self):
        """Test that @parser decorator sets validation attribute."""
        original_argv = sys.argv
        sys.argv = ["script.py", "--verbose"]
        
        @parser(validate_ambiguities=False)
        class Args:
            verbose: bool
        
        assert hasattr(Args, 'parse')
        
        # Parse when we want to
        args = Args.parse()
        assert hasattr(args, '_validate_ambiguities')
        assert args._validate_ambiguities is False
        
        sys.argv = original_argv

if __name__ == "__main__":
    unittest.main()
