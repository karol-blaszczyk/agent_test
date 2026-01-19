#!/usr/bin/env python3
"""
Comprehensive test cases for the calculator subtract function.

This module contains test cases covering:
- Positive results (minuend > subtrahend)
- Negative results (minuend < subtrahend) 
- Zero result (minuend = subtrahend)
- Large numbers
- Edge cases and boundary conditions
"""

import pytest
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from app.calculator import subtract


class TestSubtractPositiveResults:
    """Test cases where subtraction results in positive numbers."""
    
    def test_simple_positive_subtraction(self):
        """Test basic positive result subtraction."""
        assert subtract(10, 3) == 7
        assert subtract(15, 5) == 10
        assert subtract(100, 50) == 50
    
    def test_decimal_positive_subtraction(self):
        """Test positive result with decimal numbers."""
        assert subtract(5.5, 2.3) == 3.2
        assert subtract(10.75, 3.25) == 7.5
        assert subtract(1.5, 0.5) == 1.0
    
    def test_large_positive_subtraction(self):
        """Test positive result with moderately large numbers."""
        assert subtract(1000, 500) == 500
        assert subtract(9999, 1000) == 8999
        assert subtract(12345, 5432) == 6913


class TestSubtractNegativeResults:
    """Test cases where subtraction results in negative numbers."""
    
    def test_simple_negative_subtraction(self):
        """Test basic negative result subtraction."""
        assert subtract(3, 10) == -7
        assert subtract(5, 15) == -10
        assert subtract(20, 100) == -80
    
    def test_decimal_negative_subtraction(self):
        """Test negative result with decimal numbers."""
        assert subtract(2.3, 5.5) == -3.2
        assert subtract(3.25, 10.75) == -7.5
        assert subtract(0.5, 1.5) == -1.0
    
    def test_negative_to_positive_subtraction(self):
        """Test subtracting negative numbers (results in positive)."""
        assert subtract(5, -3) == 8
        assert subtract(-2, -5) == 3
        assert subtract(0, -10) == 10


class TestSubtractZeroResult:
    """Test cases where subtraction results in zero."""
    
    def test_identical_numbers_subtraction(self):
        """Test subtracting identical numbers."""
        assert subtract(5, 5) == 0
        assert subtract(100, 100) == 0
        assert subtract(3.14, 3.14) == 0
    
    def test_zero_subtraction(self):
        """Test subtracting zero."""
        assert subtract(0, 0) == 0
        assert subtract(10, 0) == 10
        assert subtract(0, 10) == -10


class TestSubtractLargeNumbers:
    """Test cases with very large numbers."""
    
    def test_large_positive_numbers(self):
        """Test subtraction with large positive numbers."""
        assert subtract(1000000, 500000) == 500000
        assert subtract(999999999, 111111111) == 888888888
        assert subtract(1234567890, 987654321) == 246913569
    
    def test_large_negative_numbers(self):
        """Test subtraction with large negative numbers."""
        assert subtract(-1000000, -500000) == -500000
        assert subtract(-999999999, -111111111) == -888888888
        assert subtract(-1234567890, -987654321) == -246913569
    
    def test_mixed_large_numbers(self):
        """Test subtraction mixing large positive and negative numbers."""
        assert subtract(1000000, -500000) == 1500000
        assert subtract(-1000000, 500000) == -1500000
        assert subtract(0, 1000000) == -1000000


class TestSubtractEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_small_numbers(self):
        """Test subtraction with very small decimal numbers."""
        assert subtract(0.001, 0.0001) == pytest.approx(0.0009)
        assert subtract(1e-10, 2e-10) == pytest.approx(-1e-10)
        assert subtract(0.000001, 0.0000005) == pytest.approx(0.0000005)
    
    def test_scientific_notation(self):
        """Test subtraction with scientific notation."""
        assert subtract(1e5, 5e4) == 50000.0
        assert subtract(2.5e6, 1.5e6) == 1000000.0
        assert subtract(1e-5, 5e-6) == pytest.approx(5e-6)
    
    def test_repeated_subtraction(self):
        """Test multiple subtractions in sequence."""
        result = subtract(100, 20)  # 80
        result = subtract(result, 30)  # 50
        result = subtract(result, 50)  # 0
        assert result == 0


class TestSubtractTypeHandling:
    """Test type handling and conversion."""
    
    def test_integer_subtraction(self):
        """Test subtraction with integers."""
        assert subtract(10, 3) == 7
        assert type(subtract(10, 3)) == int
    
    def test_float_subtraction(self):
        """Test subtraction with floats."""
        assert subtract(10.0, 3.0) == 7.0
        assert type(subtract(10.0, 3.0)) == float
    
    def test_mixed_type_subtraction(self):
        """Test subtraction with mixed int and float."""
        assert subtract(10, 3.5) == 6.5
        assert subtract(10.5, 3) == 7.5
        # Result should be float when mixing types
        assert type(subtract(10, 3.5)) == float


class TestSubtractSpecialValues:
    """Test subtraction with special mathematical values."""
    
    def test_subtract_from_self(self):
        """Test that any number minus itself equals zero."""
        assert subtract(42, 42) == 0
        assert subtract(3.14159, 3.14159) == 0
        assert subtract(-100, -100) == 0
    
    def test_subtract_zero(self):
        """Test subtracting zero from any number."""
        assert subtract(42, 0) == 42
        assert subtract(-42, 0) == -42
        assert subtract(0, 0) == 0
    
    def test_zero_minus_number(self):
        """Test subtracting any number from zero."""
        assert subtract(0, 42) == -42
        assert subtract(0, -42) == 42
        assert subtract(0, 0) == 0


class TestSubtractMathematicalProperties:
    """Test mathematical properties of subtraction."""
    
    def test_subtraction_not_commutative(self):
        """Test that subtraction is not commutative."""
        assert subtract(10, 5) != subtract(5, 10)
        assert subtract(10, 5) == 5
        assert subtract(5, 10) == -5
    
    def test_subtraction_not_associative(self):
        """Test that subtraction is not associative."""
        # (10 - 5) - 2 != 10 - (5 - 2)
        assert subtract(subtract(10, 5), 2) == 3
        assert subtract(10, subtract(5, 2)) == 7
    
    def test_subtracting_negative_equivalent_to_adding(self):
        """Test that subtracting a negative is equivalent to adding."""
        assert subtract(10, -5) == 15
        assert subtract(10, 5) == 5
        # subtract(10, -5) should equal 10 + 5
        assert subtract(10, -5) == 10 + 5


class TestSubtractBoundaryConditions:
    """Test boundary conditions and limits."""
    
    def test_maximum_precision_floats(self):
        """Test subtraction with high precision floats."""
        # Test with 15 decimal places (Python float precision)
        a = 1.123456789012345
        b = 0.123456789012345
        result = subtract(a, b)
        assert result == pytest.approx(1.0)
    
    def test_very_large_and_very_small(self):
        """Test subtraction mixing very large and very small numbers."""
        large = 1e15
        small = 1e-15
        result = subtract(large, small)
        # Due to floating point precision, this might not be exact
        assert result == pytest.approx(large - small)


class TestSubtractErrorHandling:
    """Test error handling and edge cases that might cause issues."""
    
    def test_subtraction_with_infinity(self):
        """Test subtraction involving infinity."""
        inf = float('inf')
        assert subtract(inf, 5) == inf
        assert subtract(5, inf) == -inf
        assert subtract(inf, inf) != subtract(inf, inf)  # NaN
    
    def test_subtraction_with_nan(self):
        """Test subtraction involving NaN."""
        nan = float('nan')
        result = subtract(nan, 5)
        assert result != result  # NaN property: NaN != NaN
    
    def test_subtraction_preserves_precision(self):
        """Test that subtraction preserves reasonable precision."""
        # This test ensures we don't lose too much precision
        a = 1.0000000001
        b = 1.0000000000
        result = subtract(a, b)
        assert result == pytest.approx(0.0000000001)


# Parametrized tests for comprehensive coverage
@pytest.mark.parametrize("a,b,expected", [
    # Basic positive results
    (10, 5, 5),
    (100, 50, 50),
    (7, 3, 4),
    
    # Basic negative results
    (5, 10, -5),
    (3, 7, -4),
    (50, 100, -50),
    
    # Zero results
    (5, 5, 0),
    (100, 100, 0),
    (0, 0, 0),
    
    # Decimal numbers
    (5.5, 2.5, 3.0),
    (2.5, 5.5, -3.0),
    (3.14, 3.14, 0.0),
    
    # Large numbers
    (1000000, 500000, 500000),
    (999999999, 111111111, 888888888),
])
def test_subtract_parametrized(a, b, expected):
    """Parametrized test covering various subtraction scenarios."""
    assert subtract(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [
    # Edge cases with very small numbers
    (0.001, 0.0009, pytest.approx(0.0001)),
    (1e-10, 2e-10, pytest.approx(-1e-10)),
    
    # Scientific notation
    (1e5, 5e4, 50000.0),
    (2.5e6, 1.5e6, 1000000.0),
])
def test_subtract_edge_cases_parametrized(a, b, expected):
    """Parametrized test for edge cases requiring approximate comparison."""
    assert subtract(a, b) == expected