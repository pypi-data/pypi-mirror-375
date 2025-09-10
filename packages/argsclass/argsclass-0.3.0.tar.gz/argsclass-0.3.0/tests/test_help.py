"""Tests for help message generation and validation error handling."""

import unittest
import sys
import os
from io import StringIO

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from argsclass.help import HelpFormatter, ValidationErrorCollector, ValidationError, format_help, detect_help_flag, remove_help_flags
from argsclass.parser import HelpRequested, ArgumentParsingError, parse
from argsclass.models import PositionalArgSpec, OptionArgSpec, FlagArgSpec, Cardinality, PrimitiveType


class TestHelpFormatter(unittest.TestCase, ValidationErrorCollector):
    """Test the HelpFormatter class."""
    
    def test_basic_help_formatting(self):
        """Test basic help message formatting."""
        specs = [
            PositionalArgSpec(name="input", help_text="Input file"),
            OptionArgSpec(name="output", help_text="Output file", aliases={"o"}),
            FlagArgSpec(name="verbose", help_text="Verbose output", aliases={"v"})
        ]
        
        formatter = HelpFormatter(prog="test_program")
        help_text = formatter.format_help(specs)
        
        self.assertIn("usage: test_program", help_text)
        self.assertIn("INPUT", help_text)
        self.assertIn("--output, -o", help_text)
        self.assertIn("--verbose, -v", help_text)
        self.assertIn("Input file", help_text)
        self.assertIn("Output file", help_text)
        self.assertIn("Verbose output", help_text)
    
    def test_help_with_description(self):
        """Test help message with description."""
        specs = [PositionalArgSpec(name="input", help_text="Input file")]
        
        formatter = HelpFormatter(prog="test_program", description="A test program")
        help_text = formatter.format_help(specs)
        
        self.assertIn("A test program", help_text)
    
    def test_help_with_epilog(self):
        """Test help message with epilog."""
        specs = [PositionalArgSpec(name="input", help_text="Input file")]
        
        formatter = HelpFormatter(prog="test_program", epilog="See README for more info")
        help_text = formatter.format_help(specs)
        
        self.assertIn("See README for more info", help_text)
    
    def test_positional_help_formatting(self):
        """Test positional argument help formatting."""
        spec = PositionalArgSpec(
            name="files",
            help_text="Input files",
            cardinality=Cardinality.one_or_more(),
            arg_type=PrimitiveType(str),
            choices=["txt", "md"], default="txt"
        )
        
        formatter = HelpFormatter()
        help_text = formatter._format_positional_help(spec)
        
        self.assertIn("FILES", help_text)
        self.assertIn("Input files", help_text)
        self.assertIn("(one or more)", help_text)
        self.assertIn("(choices: txt, md)", help_text)
        self.assertIn("(default: txt)", help_text)
    
    def test_option_help_formatting(self):
        """Test option argument help formatting."""
        spec = OptionArgSpec(
            name="output",
            help_text="Output file",
            aliases={"o", "out"},
            cardinality=Cardinality.single(),
            arg_type=PrimitiveType(str),
            choices=["json", "xml"], default="json"
        )
        
        formatter = HelpFormatter()
        help_text = formatter._format_option_help(spec)
        
        self.assertIn("--output, -o, --out", help_text)
        self.assertIn("Output file", help_text)
        self.assertIn("(choices: json, xml)", help_text)
        self.assertIn("(default: json)", help_text)
    
    def test_flag_help_formatting(self):
        """Test flag argument help formatting."""
        spec = FlagArgSpec(
            name="verbose",
            help_text="Verbose output",
            aliases={"v", "verb"}
        )
        
        formatter = HelpFormatter()
        help_text = formatter._format_flag_help(spec)
        
        self.assertIn("--verbose, -v, --verb", help_text)
        self.assertIn("Verbose output", help_text)
        self.assertIn("(optional)", help_text)
    
    def test_usage_formatting(self):
        """Test usage line formatting."""
        specs = [
            PositionalArgSpec(name="command"),
            PositionalArgSpec(name="files", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="output", cardinality=Cardinality.zero_or_one()),
            OptionArgSpec(name="config"),
            FlagArgSpec(name="verbose")
        ]
        
        formatter = HelpFormatter(prog="test_program")
        usage = formatter._format_usage(specs)
        
        self.assertIn("usage: test_program COMMAND FILES [FILES ...] [OUTPUT] [options]", usage)
    
    def test_custom_usage(self):
        """Test custom usage string."""
        specs = [PositionalArgSpec(name="input")]
        
        formatter = HelpFormatter(prog="test_program", usage="test_program <input> [options]")
        usage = formatter._format_usage(specs)
        
        self.assertIn("usage: test_program <input> [options]", usage)


class TestValidationErrorCollector(unittest.TestCase):
    """Test the ValidationErrorCollector class."""
    
    def test_add_error(self):
        """Test adding errors to collector."""
        collector = ValidationErrorCollector()
        
        collector.add_error("Test error", argument="test_arg", value="test_value")
        
        assert collector.has_errors()
        errors = collector.get_errors()
        self.assertEqual(len(errors), 1)
        assert errors[0].message == "Test error"
        assert errors[0].argument == "test_arg"
        assert errors[0].value == "test_value"
    
    def test_multiple_errors(self):
        """Test collecting multiple errors."""
        collector = ValidationErrorCollector()
        
        collector.add_error("Error 1", argument="arg1")
        collector.add_error("Error 2", argument="arg2")
        collector.add_error("Error 3", argument="arg3")
        
        assert collector.has_errors()
        errors = collector.get_errors()
        self.assertEqual(len(errors), 3)
    
    def test_clear_errors(self):
        """Test clearing errors."""
        collector = ValidationErrorCollector()
        
        collector.add_error("Test error")
        assert collector.has_errors()
        
        collector.clear()
        assert not collector.has_errors()
    
    def test_format_errors(self):
        """Test formatting errors into help message."""
        collector = ValidationErrorCollector()
        
        collector.add_error("Not enough arguments", argument="input")
        collector.add_error("Invalid choice", argument="format", value="csv")
        
        error_text = collector.format_errors()
        
        self.assertIn("error: the following arguments had problems:", error_text)
        self.assertIn("Not enough arguments (argument input)", error_text)
        self.assertIn("Invalid choice (argument format, value 'csv')", error_text)
        self.assertIn("use --help for more information", error_text)


class TestValidationError(unittest.TestCase):
    """Test the ValidationError class."""
    
    def test_validation_error_creation(self):
        """Test creating validation errors."""
        error = ValidationError("Test message", argument="test_arg", value="test_value")
        
        assert error.message == "Test message"
        assert error.argument == "test_arg"
        assert error.value == "test_value"
        assert error.error_type == "error"
    
    def test_validation_error_string_representation(self):
        """Test string representation of validation errors."""
        error1 = ValidationError("Test message")
        assert str(error1) == "Test message"
        
        error2 = ValidationError("Test message", argument="test_arg")
        assert str(error2) == "Test message (argument test_arg)"
        
        error3 = ValidationError("Test message", argument="test_arg", value="test_value")
        assert str(error3) == "Test message (argument test_arg, value 'test_value')"


class TestHelpUtilityFunctions(unittest.TestCase):
    """Test help utility functions."""
    
    def test_detect_help_flag(self):
        """Test help flag detection."""
        assert detect_help_flag(["--help"])
        assert detect_help_flag(["-h"])
        assert detect_help_flag(["script.py", "--help"])
        assert detect_help_flag(["script.py", "-h", "other"])
        assert not detect_help_flag([])
        assert not detect_help_flag(["script.py"])
        assert not detect_help_flag(["--helpful"])
    
    def test_remove_help_flags(self):
        """Test removing help flags from argv."""
        assert remove_help_flags(["--help"]) == []
        assert remove_help_flags(["-h"]) == []
        assert remove_help_flags(["script.py", "--help"]) == ["script.py"]
        assert remove_help_flags(["script.py", "-h", "other"]) == ["script.py", "other"]
        assert remove_help_flags(["script.py", "--help", "--verbose"]) == ["script.py", "--verbose"]
        assert remove_help_flags(["script.py"]) == ["script.py"]
        assert remove_help_flags([]) == []
    
    def test_format_help_function(self):
        """Test the format_help function."""
        specs = [
            PositionalArgSpec(name="input", help_text="Input file"),
            OptionArgSpec(name="output", help_text="Output file", aliases={"o"})
        ]
        
        help_text = format_help(specs, prog="test_program", description="A test program")
        
        self.assertIn("usage: test_program", help_text)
        self.assertIn("A test program", help_text)
        self.assertIn("INPUT", help_text)
        self.assertIn("--output, -o", help_text)


class TestHelpIntegration(unittest.TestCase):
    """Test help system integration with parser."""
    
    def test_help_requested_exception(self):
        """Test HelpRequested exception."""
        specs = [PositionalArgSpec(name="input", help_text="Input file")]
        
        with self.assertRaises(HelpRequested) as exc_info:
            parse(specs, ["--help"])
        
        self.assertIn("usage:", exc_info).value.help_message
        self.assertIn("INPUT", exc_info).value.help_message
    
    def test_help_with_class(self):
        """Test help with class-based arguments."""
        class Args:
            input_file: str = "input.txt"
            verbose: bool
        
        with self.assertRaises(HelpRequested) as exc_info:
            parse(Args, ["--help"])
        
        self.assertIn("usage:", exc_info).value.help_message
        self.assertIn("input_file", exc_info).value.help_message or "INPUT_FILE" in exc_info.value.help_message
    
    def test_help_with_custom_program_name(self):
        """Test help with custom program name."""
        specs = [PositionalArgSpec(name="input", help_text="Input file")]
        
        with self.assertRaises(HelpRequested) as exc_info:
            parse(specs, ["--help"], prog="my_program")
        
        self.assertIn("usage: my_program", exc_info).value.help_message
    
    def test_help_with_description(self):
        """Test help with description."""
        specs = [PositionalArgSpec(name="input", help_text="Input file")]
        
        with self.assertRaises(HelpRequested) as exc_info:
            parse(specs, ["--help"], description="A test program")
        
        self.assertIn("A test program", exc_info).value.help_message
    
    def test_help_with_epilog(self):
        """Test help with epilog."""
        specs = [PositionalArgSpec(name="input", help_text="Input file")]
        
        with self.assertRaises(HelpRequested) as exc_info:
            parse(specs, ["--help"], epilog="See README for more info")
        
        self.assertIn("See README for more info", exc_info).value.help_message


class TestArgumentParsingError(unittest.TestCase):
    """Test ArgumentParsingError exception."""
    
    def test_argument_parsing_error_with_help(self):
        """Test ArgumentParsingError with help message."""
        specs = [PositionalArgSpec(name="input", help_text="Input file")]
        
        with self.assertRaises(ArgumentParsingError) as exc_info:
            parse(specs, ["--unknown"])
        
        self.assertIn("unrecognized arguments", exc_info).value.error_message
        self.assertIn("usage:", exc_info).value.help_message
    
    def test_multiple_validation_errors(self):
        """Test multiple validation errors."""
        specs = [
            PositionalArgSpec(name="input", help_text="Input file"),
            OptionArgSpec(name="port", help_text="Port number", arg_type=PrimitiveType(int))
        ]
        
        with self.assertRaises(ArgumentParsingError) as exc_info:
            parse(specs, ["--port", "not_a_number", "--unknown"])
        
        error_message = exc_info.value.error_message
        self.assertIn("Error parsing option 'port'", error_message)
        self.assertIn("unrecognized arguments", error_message)
    
    def test_insufficient_arguments_error(self):
        """Test insufficient arguments error."""
        specs = [PositionalArgSpec(name="input", help_text="Input file")]
        
        with self.assertRaises(ArgumentParsingError) as exc_info:
            parse(specs, [])
        
        self.assertIn("Not enough positional arguments", exc_info).value.error_message
    
    def test_invalid_choice_error(self):
        """Test invalid choice error."""
        specs = [PositionalArgSpec(name="format", help_text="Format", choices=["json", "xml"])]
        
        with self.assertRaises(ArgumentParsingError) as exc_info:
            parse(specs, ["csv"])
        
        self.assertIn("Invalid choice", exc_info).value.error_message


class TestDecoratorHelpIntegration(unittest.TestCase):
    """Test help system integration with decorators."""
    
    def test_args_decorator_help(self):
        """Test help with @args decorator."""
        from argsclass.parser import args
        
        class Args:
            input_file: str = "input.txt"
            verbose: bool
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # This should print help and exit
            with self.assertRaises(SystemExit) as exc_info:
                args(Args, ["--help"])
            
            # Should exit with code 0 for help
            assert exc_info.value.code == 0
            
            help_output = captured_output.getvalue()
            self.assertIn("usage:", help_output)
        finally:
            sys.stdout = old_stdout
    
    def test_args_decorator_validation_error(self):
        """Test validation error with @args decorator."""
        from argsclass.parser import args
        
        class Args:
            input_file: str = "input.txt"
            verbose: bool
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # This should print error and exit
            with self.assertRaises(SystemExit) as exc_info:
                args(Args, ["--unknown"])
            
            # Should exit with code 2 for error
            assert exc_info.value.code == 2
            
            error_output = captured_output.getvalue()
            self.assertIn("unrecognized arguments", error_output)
        finally:
            sys.stdout = old_stdout
    
    def test_parser_decorator_help(self):
        """Test help with @parser decorator."""
        from argsclass.parser import parser
        
        @parser
        class Args:
            input_file: str = "input.txt"
            verbose: bool
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # This should print help and exit
            with self.assertRaises(SystemExit) as exc_info:
                Args.parse(["--help"], ValidationErrorCollector())
            
            # Should exit with code 0 for help
            assert exc_info.value.code == 0
            
            help_output = captured_output.getvalue()
            self.assertIn("usage:", help_output)
        finally:
            sys.stdout = old_stdout
    
    def test_parser_decorator_validation_error(self):
        """Test validation error with @parser decorator."""
        from argsclass.parser import parser
        
        @parser
        class Args:
            input_file: str = "input.txt"
            verbose: bool
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # This should print error and exit
            with self.assertRaises(SystemExit) as exc_info:
                Args.parse(["--unknown"], ValidationErrorCollector())
            
            # Should exit with code 2 for error
            assert exc_info.value.code == 2
            
            error_output = captured_output.getvalue()
            self.assertIn("unrecognized arguments", error_output)
        finally:
            sys.stdout = old_stdout


class TestComplexHelpScenarios(unittest.TestCase):
    """Test complex help scenarios."""
    
    def test_help_with_mixed_argument_types(self):
        """Test help with mixed argument types."""
        specs = [
            PositionalArgSpec(name="command", help_text="Command to execute"),
            PositionalArgSpec(name="files", help_text="Input files", cardinality=Cardinality.one_or_more()),
            OptionArgSpec(name="output", help_text="Output file", aliases={"o"}, default="output.txt"),
            OptionArgSpec(name="port", help_text="Port number", arg_type=PrimitiveType(int), default=8080),
            OptionArgSpec(name="format", help_text="Output format", choices=["json", "xml", "yaml"]),
            FlagArgSpec(name="verbose", help_text="Verbose output", aliases={"v"}),
            FlagArgSpec(name="debug", help_text="Debug mode", aliases={"d"})
        ]
        
        with self.assertRaises(HelpRequested) as exc_info:
            parse(specs, ["--help"])
        
        help_message = exc_info.value.help_message
        
        # Check usage line
        self.assertIn("usage:", help_message)
        self.assertIn("COMMAND", help_message)
        self.assertIn("FILES", help_message)
        self.assertIn("[options]", help_message)
        
        # Check argument descriptions
        self.assertIn("Command to execute", help_message)
        self.assertIn("Input files", help_message)
        self.assertIn("Output file", help_message)
        self.assertIn("Port number", help_message)
        self.assertIn("Output format", help_message)
        self.assertIn("Verbose output", help_message)
        self.assertIn("Debug mode", help_message)
        
        # Check aliases
        self.assertIn("--output, -o", help_message)
        self.assertIn("--verbose, -v", help_message)
        self.assertIn("--debug, -d", help_message)
        
        # Check choices
        self.assertIn("(choices: json, xml, yaml)", help_message)
        
        # Check defaults
        self.assertIn("(default: output.txt)", help_message)
        self.assertIn("(default: 8080)", help_message)
    
    def test_help_with_complex_cardinality(self):
        """Test help with complex cardinality."""
        specs = [
            PositionalArgSpec(name="required", help_text="Required argument"),
            PositionalArgSpec(name="optional", help_text="Optional argument", cardinality=Cardinality.zero_or_one()),
            PositionalArgSpec(name="multiple", help_text="Multiple arguments", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="exact", help_text="Exactly 3 arguments", cardinality=Cardinality.exactly(3))
        ]
        
        with self.assertRaises(HelpRequested) as exc_info:
            parse(specs, ["--help"])
        
        help_message = exc_info.value.help_message
        
        # Check usage line
        self.assertIn("REQUIRED", help_message)
        self.assertIn("[OPTIONAL]", help_message)
        self.assertIn("MULTIPLE [MULTIPLE ...]", help_message)
        self.assertIn("EXACT EXACT EXACT", help_message)
        
        # Check cardinality descriptions
        self.assertIn("(optional)", help_message)
        self.assertIn("(one or more)", help_message)
        self.assertIn("(exactly 3)", help_message)

if __name__ == "__main__":
    unittest.main()
