#!/usr/bin/env python3
"""
Comprehensive test suite for the calculator multiplication function.

This module contains focused tests for the multiply function covering:
- Positive products (positive × positive)
- Negative products (negative × positive, positive × negative, negative × negative)
- Zero product (any number × zero)
- Identity property (any number × 1)
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
from app.calculator import multiply


class TestCalculatorMultiply:
    """Test cases for the multiply function in calculator module."""
    
    def test_multiply_positive_numbers(self):
        """Test multiplication of two positive numbers."""
        # Basic positive multiplication
        assert multiply(3, 4) == 12
        assert multiply(5, 7) == 35
        assert multiply(10, 10) == 100
        
        # Edge case: very large positive numbers
        assert multiply(1000, 1000) == 1000000
        
        # Decimal positive numbers
        assert multiply(2.5, 4) == 10.0
        # Use pytest.approx for floating point comparison
        assert multiply(3.3, 3.3) == pytest.approx(10.89)
    
    def test_multiply_negative_products(self):
        """Test multiplication resulting in negative products."""
        # Positive × Negative = Negative
        assert multiply(5, -3) == -15
        assert multiply(10, -2) == -20
        assert multiply(2.5, -4) == -10.0
        
        # Negative × Positive = Negative  
        assert multiply(-7, 8) == -56
        assert multiply(-3, 12) == -36
        assert multiply(-1.5, 6) == -9.0
        
        # Negative × Negative = Positive
        assert multiply(-4, -5) == 20
        assert multiply(-10, -10) == 100
        assert multiply(-2.5, -4) == 10.0
    
    def test_multiply_zero_product(self):
        """Test multiplication by zero (always results in zero)."""
        # Any number × 0 = 0
        assert multiply(5, 0) == 0
        assert multiply(-10, 0) == 0
        assert multiply(0, 0) == 0
        assert multiply(1000, 0) == 0
        
        # Zero × any number = 0
        assert multiply(0, 5) == 0
        assert multiply(0, -7) == 0
        assert multiply(0, 3.14) == 0
    
    def test_multiply_identity_property(self):
        """Test multiplication by 1 (identity property)."""
        # Any number × 1 = the same number
        assert multiply(42, 1) == 42
        assert multiply(-15, 1) == -15
        assert multiply(3.14, 1) == 3.14
        assert multiply(0, 1) == 0
        
        # 1 × any number = the same number
        assert multiply(1, 42) == 42
        assert multiply(1, -15) == -15
        assert multiply(1, 3.14) == 3.14
        assert multiply(1, 0) == 0
    
    def test_multiply_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Very small numbers
        assert multiply(0.001, 0.001) == 0.000001
        
        # Large numbers
        assert multiply(10000, 10000) == 100000000
        
        # Mixed positive and negative decimals
        assert multiply(-2.5, 4.2) == -10.5
        # Use pytest.approx for floating point comparison
        assert multiply(1.5, -3.3) == pytest.approx(-4.95)
    
    def test_multiply_commutative_property(self):
        """Test that multiplication is commutative (a×b = b×a)."""
        # Test with various number combinations
        assert multiply(7, 9) == multiply(9, 7)
        assert multiply(-4, 6) == multiply(6, -4)
        assert multiply(-3, -8) == multiply(-8, -3)
        assert multiply(2.5, 3.2) == multiply(3.2, 2.5)
    
    def test_multiply_with_one_negative_one(self):
        """Test multiplication with -1 (sign flip)."""
        # Any number × -1 = negative of that number
        assert multiply(5, -1) == -5
        assert multiply(-3, -1) == 3
        assert multiply(0, -1) == 0
        assert multiply(2.5, -1) == -2.5
    
    def test_multiply_float_precision(self):
        """Test multiplication with floating point numbers for precision."""
        # Test cases that might have floating point precision issues
        result = multiply(0.1, 0.1)
        assert abs(result - 0.01) < 1e-10  # Allow for small floating point errors
        
        result = multiply(0.3, 0.3)
        assert abs(result - 0.09) < 1e-10
    
    @pytest.mark.parametrize("a,b,expected", [
        (2, 3, 6),
        (5, 8, 40),
        (-3, 4, -12),
        (-5, -7, 35),
        (0, 100, 0),
        (1, 99, 99),
        (-1, 42, -42),
        (2.5, 4, 10.0),
        (-1.5, -2, 3.0),
    ])
    def test_multiply_parametrized(self, a, b, expected):
        """Test multiplication with various parameterized inputs."""
        assert multiply(a, b) == expected


if __name__ == "__main__":
    # Run a quick test to verify the module works
    print("Testing calculator multiply function...")
    
    # Test basic functionality
    assert multiply(3, 4) == 12
    assert multiply(-2, 5) == -10
    assert multiply(0, 100) == 0
    assert multiply(7, 1) == 7
    
    print("✅ All basic tests passed!")
    print("✅ Calculator multiply test module is ready for pytest execution.")