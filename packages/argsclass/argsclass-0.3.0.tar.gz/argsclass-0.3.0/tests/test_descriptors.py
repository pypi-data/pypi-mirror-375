"""Tests for descriptor classes."""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from argsclass.descriptors import PositionalDescriptor, OptionDescriptor, FlagDescriptor, positional, option, flag
from argsclass.models import Cardinality, PrimitiveType


class TestPositionalDescriptor(unittest.TestCase):
    """Test PositionalDescriptor functionality."""
    
    def test_basic_positional_descriptor(self):
        """Test basic positional descriptor creation."""
        desc = PositionalDescriptor(help_text="A filename")
        assert desc.help_text == "A filename"
        assert desc.arg_type is None
        assert desc.choices is None
        assert desc.cardinality == Cardinality.single()
        assert desc.default is None
    
    def test_positional_descriptor_with_type(self):
        """Test positional descriptor with explicit type."""
        desc = PositionalDescriptor(arg_type=int, help_text="A number")
        assert desc.arg_type == int
        assert desc.help_text == "A number"
    
    def test_positional_descriptor_with_choices(self):
        """Test positional descriptor with choices."""
        desc = PositionalDescriptor(choices=["a", "b", "c"], help_text="Choose one")
        assert desc.choices == ["a", "b", "c"]
        assert desc.help_text == "Choose one"
    
    def test_positional_descriptor_with_cardinality(self):
        """Test positional descriptor with custom cardinality."""
        desc = PositionalDescriptor(cardinality=Cardinality.zero_or_more())
        assert desc.cardinality == Cardinality.zero_or_more()
    
    def test_positional_descriptor_with_default(self):
        """Test positional descriptor with default value."""
        desc = PositionalDescriptor(default="default.txt")
        assert desc.default == "default.txt"
    
    def test_positional_descriptor_set_name(self):
        """Test that __set_name__ sets the name correctly."""
        desc = PositionalDescriptor()
        
        class TestClass(unittest.TestCase):
            filename = desc
        
        assert desc.name == "filename"
    
    def test_positional_descriptor_get_set(self):
        """Test descriptor get/set behavior."""
        desc = PositionalDescriptor(default="default.txt")
        
        class TestClass(unittest.TestCase):
            filename = desc
        
        instance = TestClass()
        
        # Test getting default value
        assert instance.filename == "default.txt"
        
        # Test setting value
        instance.filename = "test.txt"
        assert instance.filename == "test.txt"
    
    def test_positional_descriptor_to_argspec(self):
        """Test converting descriptor to ArgSpec."""
        desc = PositionalDescriptor(
            help_text="A filename",
            arg_type=str,
            choices=["a.txt", "b.txt"],
            cardinality=Cardinality.single(),
            default="a.txt"
        )
        desc.name = "filename"  # Simulate __set_name__
        
        spec = desc.to_argspec()
        assert spec.name == "filename"
        assert spec.help_text == "A filename"
        assert isinstance(spec.arg_type, PrimitiveType)
        assert spec.arg_type.primitive_type == str
        assert spec.choices == ["a.txt", "b.txt"]
        assert spec.cardinality == Cardinality.single()
        assert spec.default == "a.txt"


class TestOptionDescriptor(unittest.TestCase):
    """Test OptionDescriptor functionality."""
    
    def test_basic_option_descriptor(self):
        """Test basic option descriptor creation."""
        desc = OptionDescriptor(help_text="An option")
        assert desc.help_text == "An option"
        assert desc.arg_type is None
        assert desc.choices is None
        assert desc.cardinality == Cardinality.single()
        assert desc.default is None
        assert desc.aliases == set()
    
    def test_option_descriptor_with_aliases(self):
        """Test option descriptor with aliases."""
        desc = OptionDescriptor(aliases={"v", "verbose"})
        assert desc.aliases == {"v", "verbose"}
    
    def test_option_descriptor_set_name(self):
        """Test that __set_name__ sets the name correctly."""
        desc = OptionDescriptor()
        
        class TestClass(unittest.TestCase):
            output = desc
        
        assert desc.name == "output"
    
    def test_option_descriptor_get_set(self):
        """Test descriptor get/set behavior."""
        desc = OptionDescriptor(default="output.txt")
        
        class TestClass(unittest.TestCase):
            output = desc
        
        instance = TestClass()
        
        # Test getting default value
        assert instance.output == "output.txt"
        
        # Test setting value
        instance.output = "result.txt"
        assert instance.output == "result.txt"
    
    def test_option_descriptor_to_argspec(self):
        """Test converting descriptor to ArgSpec."""
        desc = OptionDescriptor(
            help_text="Output file",
            arg_type=str,
            choices=["txt", "json", "xml"],
            cardinality=Cardinality.single(),
            default="txt",
            aliases={"o", "out"}
        )
        desc.name = "output"  # Simulate __set_name__
        
        spec = desc.to_argspec()
        assert spec.name == "output"
        assert spec.help_text == "Output file"
        assert isinstance(spec.arg_type, PrimitiveType)
        assert spec.arg_type.primitive_type == str
        assert spec.choices == ["txt", "json", "xml"]
        assert spec.cardinality == Cardinality.single()
        assert spec.default == "txt"
        assert spec.aliases == {"o", "out"}


class TestFlagDescriptor(unittest.TestCase):
    """Test FlagDescriptor functionality."""
    
    def test_basic_flag_descriptor(self):
        """Test basic flag descriptor creation."""
        desc = FlagDescriptor(help_text="A flag")
        assert desc.help_text == "A flag"
        assert desc.aliases == set()
    
    def test_flag_descriptor_with_aliases(self):
        """Test flag descriptor with aliases."""
        desc = FlagDescriptor(aliases={"v", "verbose"})
        assert desc.aliases == {"v", "verbose"}
    
    def test_flag_descriptor_set_name(self):
        """Test that __set_name__ sets the name correctly."""
        desc = FlagDescriptor()
        
        class TestClass(unittest.TestCase):
            verbose = desc
        
        assert desc.name == "verbose"
    
    def test_flag_descriptor_get_set(self):
        """Test descriptor get/set behavior."""
        desc = FlagDescriptor()
        
        class TestClass(unittest.TestCase):
            verbose = desc
        
        instance = TestClass()
        
        # Test getting default value (should be False)
        assert instance.verbose is False
        
        # Test setting value
        instance.verbose = True
        assert instance.verbose is True
    
    def test_flag_descriptor_to_argspec(self):
        """Test converting descriptor to ArgSpec."""
        desc = FlagDescriptor(
            help_text="Enable verbose output",
            aliases={"v", "verbose"}
        )
        desc.name = "verbose"  # Simulate __set_name__
        
        spec = desc.to_argspec()
        assert spec.name == "verbose"
        assert spec.help_text == "Enable verbose output"
        assert spec.aliases == {"v", "verbose"}
        assert spec.default is False  # Flags always default to False


class TestFactoryFunctions(unittest.TestCase):
    """Test the factory functions for creating descriptors."""
    
    def test_positional_function(self):
        """Test the positional() factory function."""
        desc = positional(help_text="A file", arg_type=str, choices=["a", "b"])
        assert isinstance(desc, PositionalDescriptor)
        assert desc.help_text == "A file"
        assert desc.arg_type == str
        assert desc.choices == ["a", "b"]
    
    def test_option_function(self):
        """Test the option() factory function."""
        desc = option(help_text="Output", aliases={"o"}, default="out.txt")
        assert isinstance(desc, OptionDescriptor)
        assert desc.help_text == "Output"
        assert desc.aliases == {"o"}
        assert desc.default == "out.txt"
    
    def test_flag_function(self):
        """Test the flag() factory function."""
        desc = flag(help_text="Verbose", aliases={"v"})
        assert isinstance(desc, FlagDescriptor)
        assert desc.help_text == "Verbose"
        assert desc.aliases == {"v"}


class TestDescriptorIntegration(unittest.TestCase):
    """Test descriptors in actual class definitions."""
    
    def test_positional_in_class(self):
        """Test using positional descriptor in a class."""
        class Args:
            filename = positional(help_text="Input file", arg_type=str)
            count = positional(help_text="Number of items", arg_type=int, default=1)
        
        # Test that descriptors are properly bound
        assert Args.filename.name == "filename"
        assert Args.count.name == "count"
        
        # Test that we can get the ArgSpecs
        filename_spec = Args.filename.to_argspec()
        count_spec = Args.count.to_argspec()
        
        assert filename_spec.name == "filename"
        assert filename_spec.help_text == "Input file"
        assert isinstance(filename_spec.arg_type, PrimitiveType)
        assert filename_spec.arg_type.primitive_type == str
        
        assert count_spec.name == "count"
        assert count_spec.help_text == "Number of items"
        assert isinstance(count_spec.arg_type, PrimitiveType)
        assert count_spec.arg_type.primitive_type == int
        assert count_spec.default == 1
    
    def test_option_in_class(self):
        """Test using option descriptor in a class."""
        class Args:
            output = option(help_text="Output file", aliases={"o"}, default="out.txt")
            format = option(help_text="Output format", choices=["json", "xml"])
        
        # Test that descriptors are properly bound
        assert Args.output.name == "output"
        assert Args.format.name == "format"
        
        # Test that we can get the ArgSpecs
        output_spec = Args.output.to_argspec()
        format_spec = Args.format.to_argspec()
        
        assert output_spec.name == "output"
        assert output_spec.help_text == "Output file"
        assert output_spec.aliases == {"o"}
        assert output_spec.default == "out.txt"
        
        assert format_spec.name == "format"
        assert format_spec.help_text == "Output format"
        assert format_spec.choices == ["json", "xml"]
    
    def test_flag_in_class(self):
        """Test using flag descriptor in a class."""
        class Args:
            verbose = flag(help_text="Verbose output", aliases={"v"})
            debug = flag(help_text="Debug mode")
        
        # Test that descriptors are properly bound
        assert Args.verbose.name == "verbose"
        assert Args.debug.name == "debug"
        
        # Test that we can get the ArgSpecs
        verbose_spec = Args.verbose.to_argspec()
        debug_spec = Args.debug.to_argspec()
        
        assert verbose_spec.name == "verbose"
        assert verbose_spec.help_text == "Verbose output"
        assert verbose_spec.aliases == {"v"}
        assert verbose_spec.default is False
        
        assert debug_spec.name == "debug"
        assert debug_spec.help_text == "Debug mode"
        assert debug_spec.default is False

if __name__ == "__main__":
    unittest.main()
