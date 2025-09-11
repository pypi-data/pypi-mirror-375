"""
cmupy - Computational Mathematics Utilities for Python

A comprehensive library for mathematical computations with CLI support.
"""

__version__ = "0.1.0"

# Import core functions to make them available at package level
from .core import factorial, is_prime
from .cli import main as cli_main

# Export public API
__all__ = [
    'hello_world',
    'add_numbers',
    'factorial', 
    'is_prime',
    'cli_main',
]

# Optional: Package initialization code
def _initialize():
    """Initialize package (can be used for setup tasks)"""
    # You can add initialization logic here if needed
    pass

# Initialize package when imported
_initialize()