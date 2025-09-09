"""
Tests for ScratchAgent main module.
"""

import pytest
import sys
import os

# Add the src directory to the path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent.main import greet, main
from agent import __version__


def test_greet():
    """Test the greet function."""
    result = greet("Test")
    assert result == "Hello, Test!"
    
    result = greet("World")
    assert result == "Hello, World!"


def test_greet_empty_name():
    """Test greet with empty string."""
    result = greet("")
    assert result == "Hello, !"


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_main_function_exists():
    """Test that main function exists and is callable."""
    assert callable(main)