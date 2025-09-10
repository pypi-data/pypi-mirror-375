import pytest
from mathlibdanval import square, factorial, is_prime, gcd, lcm

def test_square():
    assert square(3) == 9
    assert square(-4) == 16
    assert square(0) == 0

def test_factorial():
    assert factorial(5) == 120
    assert factorial(0) == 1
    assert factorial(1) == 1

def test_is_prime():
    assert is_prime(7) is True
    assert is_prime(10) is False
    assert is_prime(1) is False
    assert is_prime(2) is True

def test_gcd():
    assert gcd(48, 18) == 6
    assert gcd(101, 10) == 1
    assert gcd(0, 5) == 5

def test_lcm():
    assert lcm(4, 5) == 20
    assert lcm(0, 10) == 0
    assert lcm(7, 3) == 21
