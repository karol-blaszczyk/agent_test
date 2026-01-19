"""
Test cases for the calculator divide function.

This module contains comprehensive tests for the divide function including:
- Normal division operations
- Division by zero handling
- Negative number results
- Decimal/floating point results
"""

import pytest
from app.calculator import divide


class TestCalculatorDivide:
    """Test cases for the divide function."""
    
    def test_normal_division(self):
        """Test normal division with positive numbers."""
        # Test basic division
        assert divide(10, 2) == 5.0
        assert divide(20, 4) == 5.0
        assert divide(15, 3) == 5.0
        
        # Test division with different numbers
        assert divide(100, 5) == 20.0
        assert divide(7, 2) == 3.5
        
    def test_division_by_zero_raises_value_error(self):
        """Test that division by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)
            
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)
            
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(-10, 0)
            
    def test_negative_results(self):
        """Test division that results in negative numbers."""
        # Positive divided by negative
        assert divide(10, -2) == -5.0
        assert divide(20, -4) == -5.0
        
        # Negative divided by positive
        assert divide(-10, 2) == -5.0
        assert divide(-20, 4) == -5.0
        
        # Negative divided by negative (should be positive)
        assert divide(-10, -2) == 5.0
        assert divide(-20, -4) == 5.0
        
    def test_decimal_results(self):
        """Test division that results in decimal/floating point numbers."""
        # Division that doesn't result in whole number
        assert divide(5, 2) == 2.5
        assert divide(7, 3) == pytest.approx(2.333333, rel=1e-5)
        assert divide(1, 3) == pytest.approx(0.333333, rel=1e-5)
        
        # Test with very small numbers
        assert divide(1, 1000) == 0.001
        assert divide(0.1, 0.01) == 10.0
        
    def test_division_with_zero_numerator(self):
        """Test division when numerator is zero."""
        assert divide(0, 5) == 0.0
        assert divide(0, -5) == -0.0
        assert divide(0, 100) == 0.0
        
    def test_division_with_one(self):
        """Test division by one."""
        assert divide(42, 1) == 42.0
        assert divide(-42, 1) == -42.0
        assert divide(0, 1) == 0.0
        
    def test_division_with_same_numbers(self):
        """Test division of a number by itself."""
        assert divide(42, 42) == 1.0
        assert divide(-42, -42) == 1.0
        assert divide(1, 1) == 1.0
        
    def test_large_numbers(self):
        """Test division with large numbers."""
        assert divide(1000000, 1000) == 1000.0
        assert divide(1000000000, 1000000) == 1000.0
        
    def test_small_numbers(self):
        """Test division with very small numbers."""
        assert divide(0.001, 0.01) == 0.1
        assert divide(0.0001, 0.001) == 0.1
        
    def test_floating_point_precision(self):
        """Test floating point precision in division results."""
        # Test that we get the expected floating point precision
        result = divide(1, 7)
        assert result == pytest.approx(0.142857, rel=1e-5)
        
        result = divide(22, 7)
        assert result == pytest.approx(3.142857, rel=1e-5)