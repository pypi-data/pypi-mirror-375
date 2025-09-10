# tests/test_mathlibdanval.py
import math
import pytest
from mathlibdanval import square, factorial, is_prime, gcd, lcm

# -------------------------
# square
# -------------------------
@pytest.mark.parametrize("x, esperado", [
    (3, 9),           # happy path int+
    (-4, 16),         # happy path int-
    (0, 0),           # borde: cero
    (2.5, 6.25),      # happy path float
])
def test_square_happy(x, esperado):
    assert square(x) == pytest.approx(esperado)

@pytest.mark.parametrize("x", ["3", None, object()])
def test_square_type_error(x):
    with pytest.raises(TypeError):
        square(x)

# -------------------------
# factorial
# -------------------------
@pytest.mark.parametrize("n, esperado", [
    (0, 1),           # borde: 0!
    (1, 1),           # happy path
    (5, 120),         # happy path
    (10, math.factorial(10)),  # comparación de referencia
])
def test_factorial_happy(n, esperado):
    assert factorial(n) == esperado

@pytest.mark.parametrize("n", [-1, -10])
def test_factorial_negativo_error(n):
    with pytest.raises(ValueError):
        factorial(n)

@pytest.mark.parametrize("n", [2.5, "5", None])
def test_factorial_tipo_error(n):
    with pytest.raises(TypeError):
        factorial(n)

# -------------------------
# is_prime
# -------------------------
@pytest.mark.parametrize("n, esperado", [
    (2, True),         # happy path primo mínimo
    (97, True),        # happy path primo grande
    (25, False),       # happy path compuesto
    (1, False),        # borde: 1 no es primo
    (0, False),        # borde: 0 no es primo
])
def test_is_prime_happy(n, esperado):
    assert is_prime(n) is esperado

@pytest.mark.parametrize("n", [-3, -100])
def test_is_prime_negativo_error(n):
    with pytest.raises(ValueError):
        is_prime(n)

@pytest.mark.parametrize("n", [2.5, "7", None])
def test_is_prime_tipo_error(n):
    with pytest.raises(TypeError):
        is_prime(n)

# -------------------------
# gcd
# -------------------------
@pytest.mark.parametrize("a,b,esperado", [
    (48, 18, 6),       # happy path
    (101, 10, 1),      # happy path coprimos
    (0, 5, 5),         # borde: cero con número
    (-8, 12, 4),       # happy path con signo (usa valor absoluto)
    (12, -8, 4),       # conmutatividad con signo
])
def test_gcd_happy(a, b, esperado):
    assert gcd(a, b) == esperado
    # opcional: conmutatividad
    assert gcd(b, a) == esperado

def test_gcd_cero_cero_error():
    with pytest.raises(ValueError):
        gcd(0, 0)

@pytest.mark.parametrize("a,b", [("8", 12), (8.2, 4), (None, 3)])
def test_gcd_tipo_error(a, b):
    with pytest.raises(TypeError):
        gcd(a, b)

# -------------------------
# lcm
# -------------------------
@pytest.mark.parametrize("a,b,esperado", [
    (4, 5, 20),        # happy path
    (7, 3, 21),        # happy path
    (0, 10, 0),        # borde: múltiplo con cero
    (-4, 6, 12),       # happy path con signo (resultado no negativo)
])
def test_lcm_happy(a, b, esperado):
    assert lcm(a, b) == esperado
    # opcional: simetría
    assert lcm(b, a) == esperado

def test_lcm_cero_cero_error():
    with pytest.raises(ValueError):
        lcm(0, 0)

@pytest.mark.parametrize("a,b", [("4", 5), (4.0, 5), (None, None)])
def test_lcm_tipo_error(a, b):
    with pytest.raises(TypeError):
        lcm(a, b)
