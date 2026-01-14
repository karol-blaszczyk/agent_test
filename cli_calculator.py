#!/usr/bin/env python3
"""
Command-line interface for the Calculator class.
Accepts command-line arguments for operation and operands.
"""

import argparse
import sys
from calculator import Calculator


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='A simple command-line calculator',
        epilog='Example: python cli_calculator.py add 5 3'
    )
    
    # Operation argument
    parser.add_argument(
        'operation',
        choices=['add', 'subtract', 'multiply', 'divide'],
        help='Mathematical operation to perform'
    )
    
    # Operands
    parser.add_argument(
        'operands',
        type=float,
        nargs=2,
        help='Two numbers to operate on'
    )
    
    return parser.parse_args()


def validate_operands(operation: str, operands: list[float]) -> None:
    """Validate operands for specific operations."""
    if operation == 'divide' and operands[1] == 0:
        raise ValueError("Cannot divide by zero")


def perform_calculation(calc: Calculator, operation: str, operands: list[float]) -> float:
    """Perform the calculation based on the operation."""
    a, b = operands
    
    operations = {
        'add': calc.add,
        'subtract': calc.subtract,
        'multiply': calc.multiply,
        'divide': calc.divide
    }
    
    return operations[operation](a, b)


def main():
    """Main function to handle CLI calculator operations."""
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Validate operands
        validate_operands(args.operation, args.operands)
        
        # Create calculator instance
        calc = Calculator()
        
        # Perform calculation
        result = perform_calculation(calc, args.operation, args.operands)
        
        # Display result
        operation_symbols = {
            'add': '+',
            'subtract': '-',
            'multiply': '*',
            'divide': '/'
        }
        
        symbol = operation_symbols[args.operation]
        a, b = args.operands
        print(f"{a} {symbol} {b} = {result}")
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()