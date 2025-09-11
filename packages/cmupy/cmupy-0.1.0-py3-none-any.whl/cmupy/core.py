"""
Core mathematical functions for cmupy.
"""

import math
from typing import Union

Number = Union[int, float]

def factorial(n: int) -> int:
    """
    Compute factorial of n.
    
    Args:
        n: Non-negative integer
        
    Returns:
        Factorial of n
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    return math.factorial(n)

def is_prime(n: int) -> bool:
    """
    Check if a number is prime.
    
    Args:
        n: Integer to check
        
    Returns:
        True if n is prime, False otherwise
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    
    return True

def hello_world() -> str:
    """
    Returns a hello world message.
    
    Returns:
        str: Hello world message
        
    Example:
        >>> import cmupy
        >>> cmupy.hello_world()
        'Hello from cmupy!'
    """
    return "Hello from cmupy!"

def add_numbers(a: float, b: float) -> float:
    """
    Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
        
    Example:
        >>> import cmupy
        >>> cmupy.add_numbers(2, 3)
        5.0
    """
    return a + b