# src/mathlibdanval/mathlib.py

from __future__ import annotations
import math

def _ensure_int(x, name: str):
    # Evitar que bool pase como int
    if not isinstance(x, int) or isinstance(x, bool):
        raise TypeError(f"{name} must be an int")

def square(x):
    if not isinstance(x, (int, float)):
        raise TypeError("x must be int or float")
    return x * x

def factorial(n: int) -> int:
    _ensure_int(n, "n")
    if n < 0:
        raise ValueError("n must be >= 0")
    # iterativo para evitar recursión profunda
    acc = 1
    for k in range(2, n + 1):
        acc *= k
    return acc

def is_prime(n: int) -> bool:
    _ensure_int(n, "n")
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    r = int(math.isqrt(n))
    d = 3
    while d <= r:
        if n % d == 0:
            return False
        d += 2
    return True

def gcd(a: int, b: int) -> int:
    _ensure_int(a, "a")
    _ensure_int(b, "b")
    if a == 0 and b == 0:
        raise ValueError("gcd(0, 0) is undefined")
    # Euclides, resultado no negativo
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    _ensure_int(a, "a")
    _ensure_int(b, "b")
    if a == 0 and b == 0:
        raise ValueError("lcm(0, 0) is undefined")
    g = gcd(a, b)
    # asegurar no-negativo
    return abs(a // g * b)
