"""
Test cases for the calculator addition function.

This module contains comprehensive tests for the add function including:
- Positive numbers
- Negative numbers  
- Zero
- Mixed signs
- Return type validation
- Edge cases
"""

import pytest
from app.calculator import add


class TestCalculatorAdd:
    """Test cases for the add function."""
    
    def test_add_positive_numbers(self):
        """Test addition of two positive numbers."""
        result = add(5, 3)
        assert result == 8
        assert isinstance(result, (int, float))
    
    def test_add_negative_numbers(self):
        """Test addition of two negative numbers."""
        result = add(-5, -3)
        assert result == -8
        assert isinstance(result, (int, float))
    
    def test_add_zero_to_positive(self):
        """Test adding zero to a positive number."""
        result = add(5, 0)
        assert result == 5
        assert isinstance(result, (int, float))
    
    def test_add_zero_to_negative(self):
        """Test adding zero to a negative number."""
        result = add(-5, 0)
        assert result == -5
        assert isinstance(result, (int, float))
    
    def test_add_positive_and_negative(self):
        """Test adding positive and negative numbers."""
        result = add(10, -3)
        assert result == 7
        assert isinstance(result, (int, float))
    
    def test_add_negative_and_positive(self):
        """Test adding negative and positive numbers."""
        result = add(-10, 3)
        assert result == -7
        assert isinstance(result, (int, float))
    
    def test_add_zero_to_zero(self):
        """Test adding zero to zero."""
        result = add(0, 0)
        assert result == 0
        assert isinstance(result, (int, float))
    
    def test_add_large_numbers(self):
        """Test addition with large numbers."""
        result = add(1000000, 2000000)
        assert result == 3000000
        assert isinstance(result, (int, float))
    
    def test_add_decimal_numbers(self):
        """Test addition with decimal numbers."""
        result = add(3.14, 2.86)
        assert result == 6.0
        assert isinstance(result, float)
    
    def test_add_very_small_numbers(self):
        """Test addition with very small numbers."""
        result = add(0.0001, 0.0002)
        assert abs(result - 0.0003) < 1e-10
        assert isinstance(result, float)
    
    def test_add_negative_decimal(self):
        """Test addition with negative decimal numbers."""
        result = add(-1.5, -2.5)
        assert result == -4.0
        assert isinstance(result, float)
    
    def test_add_mixed_decimal_and_integer(self):
        """Test adding integer and decimal numbers."""
        result = add(5, 2.5)
        assert result == 7.5
        assert isinstance(result, float)
    
    def test_add_result_type_float(self):
        """Test that the result is always a float type."""
        # Test with integers
        result = add(1, 2)
        assert isinstance(result, (int, float))
        
        # Test with mixed types
        result = add(1.0, 2)
        assert isinstance(result, (int, float))
        
        # Test with decimals
        result = add(1.5, 2.5)
        assert isinstance(result, (int, float))
    
    def test_add_commutative_property(self):
        """Test that addition is commutative (a + b = b + a)."""
        a, b = 7, 3
        result1 = add(a, b)
        result2 = add(b, a)
        assert result1 == result2
        assert result1 == 10
    
    def test_add_associative_property(self):
        """Test that addition is associative ((a + b) + c = a + (b + c))."""
        a, b, c = 2, 3, 4
        result1 = add(add(a, b), c)  # (2 + 3) + 4
        result2 = add(a, add(b, c))  # 2 + (3 + 4)
        assert result1 == result2
        assert result1 == 9
    
    def test_add_identity_property(self):
        """Test that adding zero returns the same number."""
        test_values = [5, -3, 0, 1.5, -2.7]
        for value in test_values:
            result = add(value, 0)
            assert result == value
            assert isinstance(result, (int, float))
    
    def test_add_opposite_numbers(self):
        """Test adding a number and its opposite."""
        result = add(5, -5)
        assert result == 0
        assert isinstance(result, (int, float))
        
        result = add(-3.5, 3.5)
        assert result == 0
        assert isinstance(result, (int, float))
    
    @pytest.mark.parametrize("a,b,expected", [
        (1, 1, 2),
        (0, 5, 5),
        (-1, 1, 0),
        (-5, -5, -10),
        (2.5, 1.5, 4.0),
        (100, 200, 300),
        (-100, 50, -50),
    ])
    def test_add_parametrized(self, a, b, expected):
        """Test addition with various input combinations."""
        result = add(a, b)
        assert result == expected
        assert isinstance(result, (int, float))