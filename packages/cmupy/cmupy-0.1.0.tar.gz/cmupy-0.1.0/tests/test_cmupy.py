import pytest
from cmupy import hello_world, add_numbers
from cmupy.core import factorial, is_prime

def test_hello_world():
    assert hello_world() == "Hello from cmupy!"

def test_add_numbers():
    assert add_numbers(2, 3) == 5
    assert add_numbers(-1, 1) == 0
    assert add_numbers(0, 0) == 0

def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    
    with pytest.raises(ValueError):
        factorial(-1)

def test_is_prime():
    assert is_prime(2) == True
    assert is_prime(3) == True
    assert is_prime(4) == False
    assert is_prime(17) == True
    assert is_prime(1) == False
    assert is_prime(0) == False