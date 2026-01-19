"""
Calculator module providing basic arithmetic operations.

This module contains functions for addition, subtraction, multiplication,
and division with proper error handling.
"""


def add(a: float, b: float) -> float:
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The sum of a and b
    """
    return a + b


def subtract(a: float, b: float) -> float:
    """
    Subtract the second number from the first number.
    
    Args:
        a: First number (minuend)
        b: Second number (subtrahend)
        
    Returns:
        The difference of a minus b
    """
    return a - b


def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The product of a and b
    """
    return a * b


def divide(a: float, b: float) -> float:
    """
    Divide the first number by the second number.
    
    Args:
        a: First number (dividend)
        b: Second number (divisor)
        
    Returns:
        The quotient of a divided by b
        
    Raises:
        ValueError: If b is zero (division by zero)
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b