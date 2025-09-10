"""Tests for ambiguity detection functionality."""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from argsclass.ambiguity import (
    AmbiguityError, detect_ambiguities, validate_no_ambiguities, 
    is_ambiguous, get_ambiguity_resolution_suggestions
)
from argsclass.models import PositionalArgSpec, OptionArgSpec, FlagArgSpec, Cardinality, PrimitiveType


class TestAmbiguityDetection(unittest.TestCase):
    """Test ambiguity detection functionality."""
    
    def test_no_ambiguities_single_positional(self):
        """Test that single positional argument has no ambiguities."""
        specs = [PositionalArgSpec(name="filename")]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_no_ambiguities_multiple_specific_positionals(self):
        """Test that multiple positionals with specific cardinality have no ambiguities."""
        specs = [
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="output")
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_no_ambiguities_specific_and_optional_positional(self):
        """Test that specific and optional positionals have no ambiguities."""
        specs = [
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="output", cardinality=Cardinality.zero_or_one())
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_ambiguity_multiple_non_specific_positionals(self):
        """Test that multiple positionals with non-specific cardinality create ambiguities."""
        specs = [
            PositionalArgSpec(name="files1", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="files2", cardinality=Cardinality.zero_or_more())
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Multiple positional arguments with non-specific cardinality", warnings)[0]
        self.assertIn("files1, files2", warnings)[0]
        assert is_ambiguous(specs)
    
    def test_ambiguity_non_specific_before_specific_positional(self):
        """Test that non-specific positional before specific creates ambiguity."""
        specs = [
            PositionalArgSpec(name="files", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="output")
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 1)
        self.assertIn("comes before", warnings)[0]
        self.assertIn("files", warnings)[0]
        self.assertIn("output", warnings)[0]
        assert is_ambiguous(specs)
    
    def test_no_ambiguity_specific_before_non_specific_positional(self):
        """Test that specific positional before non-specific has no ambiguity."""
        specs = [
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="files", cardinality=Cardinality.one_or_more())
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_ambiguity_multiple_non_specific_options(self):
        """Test that multiple options with non-specific cardinality create ambiguities."""
        specs = [
            OptionArgSpec(name="files1", cardinality=Cardinality.one_or_more()),
            OptionArgSpec(name="files2", cardinality=Cardinality.zero_or_more())
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Multiple option arguments with non-specific cardinality", warnings)[0]
        self.assertIn("files1, files2", warnings)[0]
        assert is_ambiguous(specs)
    
    def test_no_ambiguity_multiple_specific_options(self):
        """Test that multiple options with specific cardinality have no ambiguities."""
        specs = [
            OptionArgSpec(name="input"),
            OptionArgSpec(name="output")
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_no_ambiguity_mixed_non_specific_positional_and_option(self):
        """Test that mixed non-specific positional and option do NOT create ambiguity."""
        specs = [
            PositionalArgSpec(name="files", cardinality=Cardinality.one_or_more()),
            OptionArgSpec(name="tags", cardinality=Cardinality.zero_or_more())
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_no_ambiguity_mixed_specific_positional_and_option(self):
        """Test that mixed specific positional and option have no ambiguity."""
        specs = [
            PositionalArgSpec(name="input"),
            OptionArgSpec(name="output")
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_no_ambiguity_flags_ignored(self):
        """Test that flags don't create ambiguities."""
        specs = [
            FlagArgSpec(name="verbose"),
            FlagArgSpec(name="debug"),
            PositionalArgSpec(name="files", cardinality=Cardinality.one_or_more())
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_multiple_ambiguities_detected(self):
        """Test that multiple types of ambiguities are detected."""
        specs = [
            PositionalArgSpec(name="files1", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="files2", cardinality=Cardinality.zero_or_more()),
            OptionArgSpec(name="tags1", cardinality=Cardinality.one_or_more()),
            OptionArgSpec(name="tags2", cardinality=Cardinality.zero_or_more())
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 2)  # Two ambiguities: positional and option (no mixed ambiguity)
        assert is_ambiguous(specs)
    
    def test_ambiguity_with_exact_cardinality(self):
        """Test that exact cardinality is not considered non-specific."""
        specs = [
            PositionalArgSpec(name="coords1", cardinality=Cardinality.exactly(3)),
            PositionalArgSpec(name="coords2", cardinality=Cardinality.exactly(2))
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_ambiguity_with_zero_or_one_cardinality(self):
        """Test that zero_or_one cardinality is not considered non-specific."""
        specs = [
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="output", cardinality=Cardinality.zero_or_one()),
            PositionalArgSpec(name="backup", cardinality=Cardinality.zero_or_one())
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)


class TestAmbiguityValidation(unittest.TestCase):
    """Test ambiguity validation functionality."""
    
    def test_validate_no_ambiguities_success(self):
        """Test successful validation with no ambiguities."""
        specs = [
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="output")
        ]
        # Should not raise an exception
        validate_no_ambiguities(specs)
    
    def test_validate_no_ambiguities_raises_error(self):
        """Test that validation raises AmbiguityError when ambiguities exist."""
        specs = [
            PositionalArgSpec(name="files1", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="files2", cardinality=Cardinality.zero_or_more())
        ]
        
        with self.assertRaises(AmbiguityError) as exc_info:
            validate_no_ambiguities(specs)
        
        self.assertIn("Ambiguous argument configuration detected", str)(exc_info.value)
        self.assertIn("files1, files2", str)(exc_info.value)
    
    def test_validate_no_ambiguities_multiple_warnings(self):
        """Test that validation includes all warnings in the error message."""
        specs = [
            PositionalArgSpec(name="files1", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="files2", cardinality=Cardinality.zero_or_more()),
            OptionArgSpec(name="tags", cardinality=Cardinality.one_or_more())
        ]
        
        with self.assertRaises(AmbiguityError) as exc_info:
            validate_no_ambiguities(specs)
        
        error_message = str(exc_info.value)
        self.assertIn("files1, files2", error_message)
        self.assertIn("Multiple positional arguments with non-specific cardinality", error_message)


class TestAmbiguityResolutionSuggestions(unittest.TestCase):
    """Test ambiguity resolution suggestions."""
    
    def test_suggestions_for_positional_ambiguities(self):
        """Test suggestions for positional argument ambiguities."""
        specs = [
            PositionalArgSpec(name="files1", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="files2", cardinality=Cardinality.zero_or_more())
        ]
        
        suggestions = get_ambiguity_resolution_suggestions(specs)
        
        self.assertGreater(len(suggestions), 0)
        self.assertIn("For positional arguments with non-specific cardinality", suggestions)[0]
        self.assertIn("files1", suggestions)[1]
        self.assertIn("files2", suggestions)[4]
    
    def test_suggestions_for_option_ambiguities(self):
        """Test suggestions for option argument ambiguities."""
        specs = [
            OptionArgSpec(name="files1", cardinality=Cardinality.one_or_more()),
            OptionArgSpec(name="files2", cardinality=Cardinality.zero_or_more())
        ]
        
        suggestions = get_ambiguity_resolution_suggestions(specs)
        
        self.assertGreater(len(suggestions), 0)
        self.assertIn("For option arguments with non-specific cardinality", suggestions)[0]
        self.assertIn("files1", suggestions)[1]
        self.assertIn("files2", suggestions)[4]
    
    def test_no_suggestions_for_mixed_non_ambiguous(self):
        """Test that no suggestions are provided for mixed positional and option (not ambiguous)."""
        specs = [
            PositionalArgSpec(name="files", cardinality=Cardinality.one_or_more()),
            OptionArgSpec(name="tags", cardinality=Cardinality.zero_or_more())
        ]
        
        suggestions = get_ambiguity_resolution_suggestions(specs)
        
        # No suggestions should be provided since this configuration is not ambiguous
        self.assertEqual(len(suggestions), 0)
    
    def test_no_suggestions_when_no_ambiguities(self):
        """Test that no suggestions are provided when there are no ambiguities."""
        specs = [
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="output")
        ]
        
        suggestions = get_ambiguity_resolution_suggestions(specs)
        self.assertEqual(len(suggestions), 0)


class TestAmbiguityIntegration(unittest.TestCase):
    """Test ambiguity detection integration with parsing."""
    
    def test_parse_with_ambiguity_validation_enabled(self):
        """Test that parse function validates ambiguities by default."""
        from argsclass.parser import parse
        
        specs = [
            PositionalArgSpec(name="files1", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="files2", cardinality=Cardinality.zero_or_more())
        ]
        
        with self.assertRaises(AmbiguityError):
            parse(specs, ["script.py", "file1.txt", "file2.txt"])
    
    def test_parse_with_ambiguity_validation_disabled(self):
        """Test that parse function can skip ambiguity validation."""
        from argsclass.parser import parse
        
        specs = [
            PositionalArgSpec(name="files1", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="files2", cardinality=Cardinality.zero_or_more())
        ]
        
        # Should not raise an exception when validation is disabled
        result = parse(specs, ["script.py", "file1.txt", "file2.txt"], validate_ambiguities=False)
        # Note: The actual parsing behavior with ambiguities is undefined,
        # but we're just testing that validation can be disabled
    
    def test_parse_with_class_and_ambiguity_validation(self):
        """Test that parse function validates ambiguities when using class inspection."""
        from argsclass.parser import parse
        from argsclass.descriptors import positional
        
        class AmbiguousArgs:
            files1 = positional(cardinality=Cardinality.one_or_more())
            files2 = positional(cardinality=Cardinality.zero_or_more())
        
        with self.assertRaises(AmbiguityError):
            parse(AmbiguousArgs, ["script.py", "file1.txt", "file2.txt"])
    
    def test_parse_with_class_and_no_ambiguities(self):
        """Test that parse function works with class inspection when no ambiguities exist."""
        from argsclass.parser import parse
        from argsclass.descriptors import positional
        
        class ValidArgs:
            input_file = positional()
            output_file = positional()
        
        result = parse(ValidArgs, ["script.py", "input.txt", "output.txt"])
        assert result.input_file == "input.txt"
        assert result.output_file == "output.txt"


class TestEdgeCases(unittest.TestCase):
    """Test edge cases for ambiguity detection."""
    
    def test_empty_specs_list(self):
        """Test ambiguity detection with empty specs list."""
        specs = []
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_single_spec(self):
        """Test ambiguity detection with single spec."""
        specs = [PositionalArgSpec(name="file", cardinality=Cardinality.one_or_more())]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_only_flags(self):
        """Test ambiguity detection with only flags."""
        specs = [
            FlagArgSpec(name="verbose"),
            FlagArgSpec(name="debug"),
            FlagArgSpec(name="quiet")
        ]
        warnings = detect_ambiguities(specs)
        self.assertEqual(len(warnings), 0)
        assert not is_ambiguous(specs)
    
    def test_mixed_specific_and_non_specific(self):
        """Test ambiguity detection with mixed specific and non-specific cardinalities."""
        specs = [
            PositionalArgSpec(name="input"),
            PositionalArgSpec(name="files", cardinality=Cardinality.one_or_more()),
            PositionalArgSpec(name="output"),
            OptionArgSpec(name="config"),
            OptionArgSpec(name="tags", cardinality=Cardinality.zero_or_more())
        ]
        warnings = detect_ambiguities(specs)
        # This IS ambiguous because 'files' (non-specific) comes before 'output' (specific)
        self.assertEqual(len(warnings), 1)
        self.assertIn("files", warnings)[0]
        self.assertIn("output", warnings)[0]
        assert is_ambiguous(specs)

if __name__ == "__main__":
    unittest.main()
