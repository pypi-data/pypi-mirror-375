"""Dummy tests for argsclass package."""

import argsclass


def test_package_import():
    """Test that the package can be imported."""
    assert argsclass is not None


def test_version():
    """Test that the version is defined."""
    assert hasattr(argsclass, '__version__')
    assert argsclass.__version__ == "0.2.0"


def test_dummy():
    """Dummy test to ensure pytest runs successfully."""
    assert True