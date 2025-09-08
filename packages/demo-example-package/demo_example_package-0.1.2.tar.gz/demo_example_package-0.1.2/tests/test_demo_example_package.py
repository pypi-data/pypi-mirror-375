"""Tests for demo_example_package."""

import demo_example_package


def test_version() -> None:
    """Test version is defined."""
    assert hasattr(demo_example_package, "__version__")
    assert isinstance(demo_example_package.__version__, str)
