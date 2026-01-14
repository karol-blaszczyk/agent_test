#!/usr/bin/env python3
"""
Example usage of the Calculator class.
"""

from calculator import Calculator

def main():
    """Demonstrate calculator functionality."""
    calc = Calculator()
    
    print("Calculator Example")
    print("==================")
    
    # Addition
    result = calc.add(5, 3)
    print(f"5 + 3 = {result}")
    
    # Subtraction
    result = calc.subtract(10, 4)
    print(f"10 - 4 = {result}")
    
    # Multiplication
    result = calc.multiply(7, 6)
    print(f"7 * 6 = {result}")
    
    # Division
    result = calc.divide(15, 3)
    print(f"15 / 3 = {result}")
    
    # Division by zero (with error handling)
    try:
        result = calc.divide(10, 0)
    except ValueError as e:
        print(f"Error: {e}")
    
    print("\nCalculator operations completed successfully!")

if __name__ == "__main__":
    main()