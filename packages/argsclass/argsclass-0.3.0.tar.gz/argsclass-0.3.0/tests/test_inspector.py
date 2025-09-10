"""Tests for class inspection functionality."""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from typing import Optional, Union
from argsclass.inspector import inspect_class, get_argspecs, _is_bool_type, _infer_type_from_hint
from argsclass.descriptors import positional, option, flag
from argsclass.models import PositionalArgSpec, OptionArgSpec, FlagArgSpec, Cardinality, PrimitiveType
from argsclass.parser import ArgumentParsingError


class TestBasicClassInspection(unittest.TestCase):
    """Test basic class inspection functionality."""
    
    def test_simple_class_with_type_hints(self):
        """Test inspecting a simple class with type hints."""
        class Args:
            name: str
            age: int
            height: float
        
        specs = inspect_class(Args)
        
        self.assertEqual(len(specs), 3)
        
        # Check that all specs are OptionArgSpec (no defaults, so they become options)
        for spec in specs:
            assert isinstance(spec, OptionArgSpec)
        
        # Check specific specs
        name_spec = next(s for s in specs if s.name == "name")
        age_spec = next(s for s in specs if s.name == "age")
        height_spec = next(s for s in specs if s.name == "height")
        
        assert isinstance(name_spec.arg_type, PrimitiveType)
        assert name_spec.arg_type.primitive_type == str
        assert isinstance(age_spec.arg_type, PrimitiveType)
        assert age_spec.arg_type.primitive_type == int
        assert isinstance(height_spec.arg_type, PrimitiveType)
        assert height_spec.arg_type.primitive_type == float
    
    def test_class_with_defaults(self):
        """Test inspecting a class with default values."""
        class Args:
            name: str = "default"
            count: int = 42
            rate: float = 3.14
        
        specs = inspect_class(Args)
        
        self.assertEqual(len(specs), 3)
        
        # Check that all specs are OptionArgSpec with defaults
        for spec in specs:
            assert isinstance(spec, OptionArgSpec)
            assert spec.default is not None
        
        # Check specific specs
        name_spec = next(s for s in specs if s.name == "name")
        count_spec = next(s for s in specs if s.name == "count")
        rate_spec = next(s for s in specs if s.name == "rate")
        
        assert name_spec.default == "default"
        assert count_spec.default == 42
        assert rate_spec.default == 3.14
    
    def test_class_with_boolean_flags(self):
        """Test inspecting a class with boolean attributes (should become flags)."""
        class Args:
            verbose: bool
            debug: bool = True
            quiet: bool = False
        
        specs = inspect_class(Args)
        
        self.assertEqual(len(specs), 3)
        
        # Check that all specs are FlagArgSpec
        for spec in specs:
            assert isinstance(spec, FlagArgSpec)
        
        # Check specific specs
        verbose_spec = next(s for s in specs if s.name == "verbose")
        debug_spec = next(s for s in specs if s.name == "debug")
        quiet_spec = next(s for s in specs if s.name == "quiet")
        
        assert verbose_spec.default is False
        assert debug_spec.default is False  # Flags always default to False
        assert quiet_spec.default is False  # Flags always default to False
    
    def test_class_with_positional_descriptors(self):
        """Test inspecting a class with positional descriptors."""
        class Args:
            filename = positional(help_text="Input file", arg_type=str)
            count = positional(help_text="Number of items", arg_type=int, default=1)
        
        specs = inspect_class(Args)
        
        self.assertEqual(len(specs), 2)
        
        # Check that all specs are PositionalArgSpec
        for spec in specs:
            assert isinstance(spec, PositionalArgSpec)
        
        # Check specific specs
        filename_spec = next(s for s in specs if s.name == "filename")
        count_spec = next(s for s in specs if s.name == "count")
        
        assert filename_spec.help_text == "Input file"
        assert isinstance(filename_spec.arg_type, PrimitiveType)
        assert filename_spec.arg_type.primitive_type == str
        assert filename_spec.default is None
        
        assert count_spec.help_text == "Number of items"
        assert isinstance(count_spec.arg_type, PrimitiveType)
        assert count_spec.arg_type.primitive_type == int
        assert count_spec.default == 1
    
    def test_mixed_class_attributes(self):
        """Test inspecting a class with mixed attribute types."""
        class Args:
            # Boolean flag
            verbose: bool
            
            # Option with default
            output: str = "output.txt"
            
            # Positional argument
            filename = positional(help_text="Input file")
            
            # Option without default
            format: str
        
        specs = inspect_class(Args)
        
        self.assertEqual(len(specs), 4)
        
        # Check types
        verbose_spec = next(s for s in specs if s.name == "verbose")
        output_spec = next(s for s in specs if s.name == "output")
        filename_spec = next(s for s in specs if s.name == "filename")
        format_spec = next(s for s in specs if s.name == "format")
        
        assert isinstance(verbose_spec, FlagArgSpec)
        assert isinstance(output_spec, OptionArgSpec)
        assert isinstance(filename_spec, PositionalArgSpec)
        assert isinstance(format_spec, OptionArgSpec)
        
        # Check values
        assert verbose_spec.default is False
        assert output_spec.default == "output.txt"
        assert filename_spec.help_text == "Input file"
        assert format_spec.default is None
    
    def test_example_from_user_query(self):
        """Test the exact example from the user query."""
        class Args:
            flag: bool
            option: str = "default"
            Name: str = positional(help_text="foo")
        
        specs = inspect_class(Args)
        
        self.assertEqual(len(specs), 3)
        
        # Check types
        flag_spec = next(s for s in specs if s.name == "flag")
        option_spec = next(s for s in specs if s.name == "option")
        name_spec = next(s for s in specs if s.name == "Name")
        
        assert isinstance(flag_spec, FlagArgSpec)
        assert isinstance(option_spec, OptionArgSpec)
        assert isinstance(name_spec, PositionalArgSpec)
        
        # Check values
        assert flag_spec.default is False
        assert option_spec.default == "default"
        assert name_spec.help_text == "foo"


class TestTypeInference(unittest.TestCase):
    """Test type inference functionality."""
    
    def test_is_bool_type(self):
        """Test _is_bool_type function."""
        assert _is_bool_type(bool) is True
        assert _is_bool_type(str) is False
        assert _is_bool_type(int) is False
        
        # Test Optional[bool]
        assert _is_bool_type(Optional[bool]) is True
        
        # Test Union[bool, None]
        assert _is_bool_type(Union[bool, None]) is True
    
    def test_infer_type_from_hint(self):
        """Test _infer_type_from_hint function."""
        assert _infer_type_from_hint(str) == str
        assert _infer_type_from_hint(int) == int
        assert _infer_type_from_hint(float) == float
        assert _infer_type_from_hint(None) == str  # Default to string
        
        # Test Optional types
        assert _infer_type_from_hint(Optional[str]) == str
        assert _infer_type_from_hint(Optional[int]) == int
        
        # Test Union types
        assert _infer_type_from_hint(Union[str, None]) == str
        assert _infer_type_from_hint(Union[int, None]) == int
        
        # Test unknown types default to string
        assert _infer_type_from_hint(list) == str
        assert _infer_type_from_hint(dict) == str


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_empty_class(self):
        """Test inspecting an empty class."""
        class EmptyArgs:
            pass
        
        specs = inspect_class(EmptyArgs)
        self.assertEqual(len(specs), 0)
    
    def test_class_with_private_attributes(self):
        """Test that private attributes are ignored."""
        class Args:
            _private: str = "private"
            public: str = "public"
            __very_private: int = 42
        
        specs = inspect_class(Args)
        
        # Only public attribute should be included
        self.assertEqual(len(specs), 1)
        assert specs[0].name == "public"
        assert specs[0].default == "public"
    
    def test_class_with_methods(self):
        """Test that methods are ignored."""
        class Args:
            name: str = "test"
            
            def method(self):
                return "method"
            
            @staticmethod
            def static_method():
                return "static"
        
        specs = inspect_class(Args)
        
        # Only the attribute should be included
        self.assertEqual(len(specs), 1)
        assert specs[0].name == "name"
        assert specs[0].default == "test"
    
    def test_class_with_module_attribute(self):
        """Test that module attributes are ignored."""
        import sys
        
        class Args:
            name: str = "test"
            sys_module = sys
        
        specs = inspect_class(Args)
        
        # Only the attribute should be included
        self.assertEqual(len(specs), 1)
        assert specs[0].name == "name"
        assert specs[0].default == "test"
    
    def test_inspect_non_class(self):
        """Test that inspecting a non-class raises TypeError."""
        with self.assertRaises(ArgumentParsingError):
            inspect_class("not a class")
        
        with self.assertRaises(ArgumentParsingError):
            inspect_class(42)
        
        with self.assertRaises(ArgumentParsingError):
            inspect_class([])


class TestGetArgspecsAlias(unittest.TestCase):
    """Test the get_argspecs alias function."""
    
    def test_get_argspecs_alias(self):
        """Test that get_argspecs is an alias for inspect_class."""
        class Args:
            name: str = "test"
        
        specs1 = inspect_class(Args)
        specs2 = get_argspecs(Args)
        
        self.assertEqual(len(specs1), 1)
        self.assertEqual(len(specs2), 1)
        assert specs1[0].name == "name"
        assert specs2[0].name == "name"
        # Compare the actual values instead of object identity
        assert specs1[0].name == specs2[0].name
        assert specs1[0].default == specs2[0].default
        assert specs1[0].help_text == specs2[0].help_text


class TestComplexTypeHints(unittest.TestCase):
    """Test complex type hints and edge cases."""
    
    def test_optional_types(self):
        """Test Optional type hints."""
        class Args:
            name: Optional[str] = None
            count: Optional[int] = 42
            rate: Optional[float] = None
        
        specs = inspect_class(Args)
        
        self.assertEqual(len(specs), 3)
        
        name_spec = next(s for s in specs if s.name == "name")
        count_spec = next(s for s in specs if s.name == "count")
        rate_spec = next(s for s in specs if s.name == "rate")
        
        assert isinstance(name_spec, OptionArgSpec)
        assert isinstance(count_spec, OptionArgSpec)
        assert isinstance(rate_spec, OptionArgSpec)
        
        assert name_spec.default is None
        assert count_spec.default == 42
        assert rate_spec.default is None
        
        assert isinstance(name_spec.arg_type, PrimitiveType)
        assert name_spec.arg_type.primitive_type == str
        assert isinstance(count_spec.arg_type, PrimitiveType)
        assert count_spec.arg_type.primitive_type == int
        assert isinstance(rate_spec.arg_type, PrimitiveType)
        assert rate_spec.arg_type.primitive_type == float
    
    def test_union_types(self):
        """Test Union type hints."""
        class Args:
            value: Union[str, int] = "default"
            number: Union[int, float] = 42
        
        specs = inspect_class(Args)
        
        self.assertEqual(len(specs), 2)
        
        value_spec = next(s for s in specs if s.name == "value")
        number_spec = next(s for s in specs if s.name == "number")
        
        assert isinstance(value_spec, OptionArgSpec)
        assert isinstance(number_spec, OptionArgSpec)
        
        assert value_spec.default == "default"
        assert number_spec.default == 42
        
        # Should infer the first non-None type
        assert isinstance(value_spec.arg_type, PrimitiveType)
        assert value_spec.arg_type.primitive_type == str
        assert isinstance(number_spec.arg_type, PrimitiveType)
        assert number_spec.arg_type.primitive_type == int
    
    def test_boolean_union_types(self):
        """Test Union types with boolean."""
        class Args:
            flag1: Union[bool, None] = None
            flag2: Union[bool, str] = True
        
        specs = inspect_class(Args)
        
        self.assertEqual(len(specs), 2)
        
        flag1_spec = next(s for s in specs if s.name == "flag1")
        flag2_spec = next(s for s in specs if s.name == "flag2")
        
        # Both should be flags because they contain bool
        assert isinstance(flag1_spec, FlagArgSpec)
        assert isinstance(flag2_spec, FlagArgSpec)
        
        assert flag1_spec.default is False
        assert flag2_spec.default is False  # Flags always default to False

if __name__ == "__main__":
    unittest.main()
