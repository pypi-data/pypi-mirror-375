# src/aqi_pipeline/cli.py
import argparse
import os
from .mathlib import square, factorial, is_prime, gcd, lcm

def main():
    parser = argparse.ArgumentParser(description="Run the data processing pipeline.")
    parser.add_argument(
        "--operation",
        type=str,
        choices=["square", "factorial", "is_prime", "gcd", "lcm"],
        required=True,
        help="The mathematical operation to perform.",
    )
    parser.add_argument("operands", type=int, nargs="+", help="Operands for the operation.")
    args = parser.parse_args()
    operation = args.operation
    operands = args.operands
    result = None
    if operation == "square":
        if len(operands) != 1:
            raise ValueError("Square operation requires exactly one operand.")
        result = square(operands[0])
    elif operation == "factorial":
        if len(operands) != 1:
            raise ValueError("Factorial operation requires exactly one operand.")
        result = factorial(operands[0])
    elif operation == "is_prime":
        if len(operands) != 1:
            raise ValueError("is_prime operation requires exactly one operand.")
        result = is_prime(operands[0])
    elif operation == "gcd":
        if len(operands) != 2:
            raise ValueError("GCD operation requires exactly two operands.")
        result = gcd(operands[0], operands[1])
    elif operation == "lcm":
        if len(operands) != 2:
            raise ValueError("LCM operation requires exactly two operands.")
        result = lcm(operands[0], operands[1])
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
