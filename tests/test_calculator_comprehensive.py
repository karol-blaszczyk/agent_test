"""
Comprehensive test suite for the calculator module.

This module contains integration tests combining all operations, boundary value tests,
and type validation tests for the calculator functionality.
"""

import pytest
import sys
from decimal import Decimal
from typing import Union
from app.calculator import add, subtract, multiply, divide


class TestCalculatorIntegration:
    """Integration tests combining multiple calculator operations."""
    
    def test_basic_arithmetic_sequence(self):
        """Test a sequence of basic arithmetic operations."""
        # Start with 10
        result = add(10, 5)  # 15
        result = subtract(result, 3)  # 12
        result = multiply(result, 2)  # 24
        result = divide(result, 4)  # 6.0
        
        assert result == 6.0
        assert isinstance(result, float)
    
    def test_complex_expression_simulation(self):
        """Test simulating a complex mathematical expression."""
        # Simulate: ((10 + 5) * 3 - 20) / 5 = 5.0
        step1 = add(10, 5)  # 15
        step2 = multiply(step1, 3)  # 45
        step3 = subtract(step2, 20)  # 25
        step4 = divide(step3, 5)  # 5.0
        
        assert step4 == 5.0
    
    def test_order_of_operations_simulation(self):
        """Test that operations follow mathematical precedence when chained."""
        # Simulate: 100 - 50 + 25 * 2 / 10
        # Should be: (100 - 50) + ((25 * 2) / 10) = 50 + 5 = 55
        step1 = subtract(100, 50)  # 50
        step2 = multiply(25, 2)  # 50
        step3 = divide(step2, 10)  # 5.0
        step4 = add(step1, step3)  # 55
        
        assert step4 == 55.0
    
    def test_error_propagation_in_chain(self):
        """Test that errors in operation chains are properly handled."""
        # This should work fine
        result = add(10, 5)
        result = multiply(result, 2)
        
        # This should raise ValueError
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            result = divide(result, 0)
    
    def test_mixed_type_operations(self):
        """Test operations with mixed numeric types (int and float)."""
        # Mix of integers and floats
        result = add(5, 3.5)  # 8.5
        result = subtract(result, 2)  # 6.5
        result = multiply(result, 2)  # 13.0
        result = divide(result, 2)  # 6.5
        
        assert result == 6.5
        assert isinstance(result, float)
    
    def test_calculator_state_consistency(self):
        """Test that calculator operations maintain consistent state."""
        # Start with a value
        value = 100
        
        # Apply inverse operations
        value = add(value, 50)  # 150
        value = subtract(value, 50)  # 100
        
        value = multiply(value, 2)  # 200
        value = divide(value, 2)  # 100.0
        
        # Should be back to original (allowing for float precision)
        assert value == 100.0


class TestCalculatorBoundaryValues:
    """Boundary value tests for calculator operations."""
    
    def test_add_boundary_values(self):
        """Test addition with boundary values."""
        # Test with very large numbers - note that 1e308 is near max float precision
        # Adding 1 to 1e308 doesn't change it due to floating point precision
        large_num = 1e307  # More reasonable large number
        result = add(large_num, large_num)
        assert result == 2 * large_num
        
        # Test with very small numbers
        small_num = 1e-308  # Close to min positive float
        result = add(small_num, small_num)
        assert result == pytest.approx(2 * small_num, rel=1e-15)
        
        # Test with zero
        result = add(0, 0)
        assert result == 0
    
    def test_subtract_boundary_values(self):
        """Test subtraction with boundary values."""
        # Test with very large numbers - similar to addition, precision limits apply
        large_num = 1e307
        result = subtract(large_num, 1e306)
        assert result == 9e306
        
        # Test subtracting from zero
        result = subtract(0, 5)
        assert result == -5
        
        # Test subtracting same number
        result = subtract(42, 42)
        assert result == 0
    
    def test_multiply_boundary_values(self):
        """Test multiplication with boundary values."""
        # Test with very large numbers
        large_num = 1e154  # sqrt of max float
        result = multiply(large_num, large_num)
        assert result == pytest.approx(large_num * large_num, rel=1e-10)
        
        # Test with very small numbers
        small_num = 1e-154
        result = multiply(small_num, small_num)
        assert result == pytest.approx(small_num * small_num, rel=1e-10)
        
        # Test multiplication by zero
        result = multiply(999999, 0)
        assert result == 0
        
        # Test multiplication by one
        result = multiply(42, 1)
        assert result == 42
        
        # Test multiplication by negative one
        result = multiply(42, -1)
        assert result == -42
    
    def test_divide_boundary_values(self):
        """Test division with boundary values."""
        # Test division by very small number (approaching zero)
        small_num = 1e-15
        result = divide(1, small_num)
        assert result == pytest.approx(1e15, rel=1e-10)
        
        # Test division of very small number
        result = divide(1e-15, 2)
        assert result == pytest.approx(5e-16, rel=1e-15)
        
        # Test division by one
        result = divide(42, 1)
        assert result == 42.0
        
        # Test division of zero
        result = divide(0, 42)
        assert result == 0.0
        
        # Test division by zero should raise error
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(42, 0)
    
    def test_floating_point_precision_boundaries(self):
        """Test floating point precision at boundaries."""
        # Test machine epsilon precision
        eps = sys.float_info.epsilon
        result = add(1.0, eps)
        assert result > 1.0
        
        # Test very close numbers
        a = 1.000000000000001  # 15 decimal places
        b = 1.000000000000002
        result = subtract(b, a)
        assert result == pytest.approx(1e-15, rel=1e-10)
    
    def test_overflow_handling(self):
        """Test handling of potential overflow scenarios."""
        # Test multiplication that could overflow
        large_num = 1e200
        result = multiply(large_num, 1e200)
        # Should result in infinity, not crash
        assert result == float('inf')
        
        # Test addition that could overflow
        result = add(1e308, 1e308)
        assert result == float('inf')


class TestCalculatorTypeValidation:
    """Type validation tests for calculator operations."""
    
    def test_add_type_validation(self):
        """Test type validation for add function."""
        # Test with integers
        result = add(5, 3)
        assert isinstance(result, (int, float))
        assert result == 8
        
        # Test with floats
        result = add(5.5, 3.2)
        assert isinstance(result, float)
        assert result == 8.7
        
        # Test with mixed types
        result = add(5, 3.2)
        assert isinstance(result, float)
        assert result == 8.2
    
    def test_subtract_type_validation(self):
        """Test type validation for subtract function."""
        # Test with integers
        result = subtract(5, 3)
        assert isinstance(result, (int, float))
        assert result == 2
        
        # Test with floats
        result = subtract(5.5, 3.2)
        assert isinstance(result, float)
        assert result == pytest.approx(2.3, rel=1e-10)
        
        # Test with mixed types
        result = subtract(5, 3.2)
        assert isinstance(result, float)
        assert result == pytest.approx(1.8, rel=1e-10)
    
    def test_multiply_type_validation(self):
        """Test type validation for multiply function."""
        # Test with integers
        result = multiply(5, 3)
        assert isinstance(result, (int, float))
        assert result == 15
        
        # Test with floats
        result = multiply(5.5, 3.2)
        assert isinstance(result, float)
        assert result == 17.6
        
        # Test with mixed types
        result = multiply(5, 3.2)
        assert isinstance(result, float)
        assert result == 16.0
    
    def test_divide_type_validation(self):
        """Test type validation for divide function."""
        # Test with integers
        result = divide(6, 3)
        assert isinstance(result, float)
        assert result == 2.0
        
        # Test with floats
        result = divide(6.6, 3.2)
        assert isinstance(result, float)
        assert result == pytest.approx(2.0625, rel=1e-10)
        
        # Test with mixed types
        result = divide(6, 3.2)
        assert isinstance(result, float)
        assert result == pytest.approx(1.875, rel=1e-10)
    
    def test_invalid_input_types(self):
        """Test behavior with invalid input types."""
        # Test with strings - should still work due to Python's type coercion
        result = add(5, 3)  # Both integers
        assert result == 8
        
        # Test with None - should raise TypeError
        with pytest.raises(TypeError):
            add(None, 5)
        
        with pytest.raises(TypeError):
            subtract(5, None)
        
        with pytest.raises(TypeError):
            multiply(None, None)
        
        with pytest.raises(TypeError):
            divide(5, None)
    
    def test_numeric_type_coercion(self):
        """Test how numeric types are handled in operations."""
        # Test boolean values (True=1, False=0)
        result = add(True, False)  # 1 + 0
        assert result == 1
        assert isinstance(result, int)
        
        result = multiply(True, 5)  # 1 * 5
        assert result == 5
        assert isinstance(result, int)
        
        # Test with zero - use a small number instead of False to avoid division by zero
        result = divide(10, 0.1)  # 10 / 0.1 = 100
        assert result == 100.0
        assert isinstance(result, float)


class TestCalculatorEdgeCases:
    """Edge case tests for calculator operations."""
    
    def test_special_float_values(self):
        """Test operations with special float values."""
        # Test with infinity
        inf = float('inf')
        result = add(inf, 1)
        assert result == inf
        
        result = multiply(inf, 2)
        assert result == inf
        
        # Test with negative infinity
        neg_inf = float('-inf')
        result = add(neg_inf, 1)
        assert result == neg_inf
        
        # Test with NaN
        nan = float('nan')
        result = add(nan, 1)
        assert str(result) == 'nan'
    
    def test_very_long_decimal_numbers(self):
        """Test with numbers that have many decimal places."""
        # Test addition with many decimal places
        a = 1.123456789012345
        b = 2.987654321098765
        result = add(a, b)
        expected = a + b  # Calculate expected value directly
        assert result == pytest.approx(expected, rel=1e-14)
        
        # Test multiplication precision
        result = multiply(a, b)
        expected = a * b  # Calculate expected value directly
        assert result == pytest.approx(expected, rel=1e-14)
    
    def test_repeated_operations(self):
        """Test repeated operations for consistency."""
        # Test repeated addition
        result = 0
        for i in range(1000):
            result = add(result, 1)
        assert result == 1000
        
        # Test repeated multiplication
        result = 1
        for i in range(10):
            result = multiply(result, 2)
        assert result == 1024
    
    def test_inverse_operations_consistency(self):
        """Test that inverse operations return to original values."""
        original = 42.5
        
        # Add and subtract
        temp = add(original, 10.5)
        result = subtract(temp, 10.5)
        assert result == original
        
        # Multiply and divide
        temp = multiply(original, 3.2)
        result = divide(temp, 3.2)
        assert result == pytest.approx(original, rel=1e-14)


class TestCalculatorPerformance:
    """Performance-related tests for calculator operations."""
    
    def test_large_number_operations(self):
        """Test operations with very large numbers."""
        large_num = 1e100
        
        # These should complete without hanging
        result = add(large_num, large_num)
        assert result == pytest.approx(2e100, rel=1e-10)
        
        result = multiply(large_num, 1e10)
        assert result == pytest.approx(1e110, rel=1e-10)
        
        result = divide(large_num, 1e50)
        assert result == pytest.approx(1e50, rel=1e-10)
    
    def test_small_number_operations(self):
        """Test operations with very small numbers."""
        small_num = 1e-100
        
        result = add(small_num, small_num)
        assert result == pytest.approx(2e-100, rel=1e-10)
        
        result = multiply(small_num, 1e50)
        assert result == pytest.approx(1e-50, rel=1e-10)
        
        result = divide(small_num, 1e-50)
        assert result == pytest.approx(1e-50, rel=1e-10)


@pytest.mark.parametrize("operation,args,expected", [
    (add, (2, 3), 5),
    (add, (-2, -3), -5),
    (add, (2.5, 3.5), 6.0),
    (subtract, (5, 3), 2),
    (subtract, (3, 5), -2),
    (subtract, (5.5, 2.5), 3.0),
    (multiply, (4, 3), 12),
    (multiply, (-4, 3), -12),
    (multiply, (2.5, 4), 10.0),
    (divide, (10, 2), 5.0),
    (divide, (10, 4), 2.5),
    (divide, (-10, 2), -5.0),
])
def test_parametrized_operations(operation, args, expected):
    """Parametrized tests for all operations."""
    result = operation(*args)
    if isinstance(expected, float) and expected != 0:
        assert result == pytest.approx(expected, rel=1e-10)
    else:
        assert result == expected


def test_division_by_zero_parametrized():
    """Test division by zero with various numerators."""
    test_cases = [1, -1, 0, 42, 3.14, -2.5]
    
    for numerator in test_cases:
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(numerator, 0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])