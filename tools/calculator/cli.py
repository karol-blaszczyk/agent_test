#!/usr/bin/env python3
"""
Command-line interface for the calculator module.

Supports basic arithmetic operations: add, subtract, multiply, divide.
"""

import argparse
import sys
from typing import Callable

from .calculator import add, subtract, multiply, divide


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Calculator CLI - Perform basic arithmetic operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add 5 3
  %(prog)s subtract 10 4
  %(prog)s multiply 7 6
  %(prog)s divide 15 3
        """
    )
    
    parser.add_argument(
        "operation",
        choices=["add", "subtract", "multiply", "divide"],
        help="Arithmetic operation to perform"
    )
    
    parser.add_argument(
        "num1",
        type=float,
        help="First number"
    )
    
    parser.add_argument(
        "num2",
        type=float,
        help="Second number"
    )
    
    return parser


def get_operation_func(operation: str) -> Callable[[float, float], float]:
    """Get the appropriate calculator function based on operation name."""
    operations = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide
    }
    return operations[operation]


def format_result(result: float) -> str:
    """Format the result for display."""
    # Remove trailing zeros for cleaner output
    if result == int(result):
        return str(int(result))
    return str(result)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        operation_func = get_operation_func(args.operation)
        result = operation_func(args.num1, args.num2)
        print(f"Result: {format_result(result)}")
        
    except ValueError as e:
        # Handle division by zero and other validation errors
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        # Handle any unexpected errors
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()