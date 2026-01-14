import pytest
from tools.calculator.calculator import add, subtract, multiply, divide


class TestCalculator:
    """Comprehensive test cases for the Calculator functions."""
    
    # Addition Tests
    def test_add_positive_numbers(self):
        """Test addition with positive numbers."""
        assert add(2, 3) == 5
        assert add(10, 15) == 25
        assert add(100, 200) == 300
    
    def test_add_negative_numbers(self):
        """Test addition with negative numbers."""
        assert add(-2, -3) == -5
        assert add(-10, -5) == -15
        assert add(-100, -200) == -300
    
    def test_add_mixed_numbers(self):
        """Test addition with mixed positive and negative numbers."""
        assert add(5, -3) == 2
        assert add(-5, 3) == -2
        assert add(10, -10) == 0
    
    def test_add_zero(self):
        """Test addition with zero."""
        assert add(0, 0) == 0
        assert add(5, 0) == 5
        assert add(0, -5) == -5
        assert add(0, 10) == 10
    
    def test_add_floats(self):
        """Test addition with floating point numbers."""
        assert add(1.5, 2.5) == 4.0
        assert add(0.1, 0.2) == pytest.approx(0.3)
        assert add(-1.5, 1.5) == 0.0
    
    def test_add_large_numbers(self):
        """Test addition with large numbers."""
        assert add(1e6, 2e6) == 3e6
        assert add(999999999, 1) == 1000000000
    
    # Subtraction Tests
    def test_subtract_positive_numbers(self):
        """Test subtraction with positive numbers."""
        assert subtract(10, 3) == 7
        assert subtract(5, 5) == 0
        assert subtract(100, 50) == 50
    
    def test_subtract_negative_numbers(self):
        """Test subtraction with negative numbers."""
        assert subtract(-5, -3) == -2
        assert subtract(-10, -10) == 0
        assert subtract(-5, -10) == 5
    
    def test_subtract_mixed_numbers(self):
        """Test subtraction with mixed positive and negative numbers."""
        assert subtract(5, -3) == 8
        assert subtract(-5, 3) == -8
        assert subtract(10, -10) == 20
    
    def test_subtract_zero(self):
        """Test subtraction with zero."""
        assert subtract(0, 0) == 0
        assert subtract(5, 0) == 5
        assert subtract(0, 5) == -5
        assert subtract(-5, 0) == -5
    
    def test_subtract_floats(self):
        """Test subtraction with floating point numbers."""
        assert subtract(5.5, 2.5) == 3.0
        assert subtract(0.3, 0.1) == pytest.approx(0.2)
        assert subtract(-1.5, -1.5) == 0.0
    
    def test_subtract_large_numbers(self):
        """Test subtraction with large numbers."""
        assert subtract(1e6, 5e5) == 5e5
        assert subtract(1000000000, 999999999) == 1
    
    # Multiplication Tests
    def test_multiply_positive_numbers(self):
        """Test multiplication with positive numbers."""
        assert multiply(3, 4) == 12
        assert multiply(5, 6) == 30
        assert multiply(10, 10) == 100
    
    def test_multiply_negative_numbers(self):
        """Test multiplication with negative numbers."""
        assert multiply(-2, -3) == 6
        assert multiply(-5, -4) == 20
        assert multiply(-1, -1) == 1
    
    def test_multiply_mixed_numbers(self):
        """Test multiplication with mixed positive and negative numbers."""
        assert multiply(5, -3) == -15
        assert multiply(-5, 3) == -15
        assert multiply(10, -1) == -10
    
    def test_multiply_zero(self):
        """Test multiplication with zero."""
        assert multiply(0, 0) == 0
        assert multiply(5, 0) == 0
        assert multiply(0, -5) == 0
        assert multiply(100, 0) == 0
    
    def test_multiply_floats(self):
        """Test multiplication with floating point numbers."""
        assert multiply(2.5, 4) == 10.0
        assert multiply(0.5, 0.5) == 0.25
        assert multiply(-1.5, 2) == -3.0
    
    def test_multiply_large_numbers(self):
        """Test multiplication with large numbers."""
        assert multiply(1e3, 1e3) == 1e6
        assert multiply(1000000, 1000) == 1000000000
    
    def test_multiply_by_one(self):
        """Test multiplication by one (identity property)."""
        assert multiply(42, 1) == 42
        assert multiply(-42, 1) == -42
        assert multiply(0, 1) == 0
    
    def test_multiply_by_negative_one(self):
        """Test multiplication by negative one."""
        assert multiply(42, -1) == -42
        assert multiply(-42, -1) == 42
        assert multiply(0, -1) == 0
    
    # Division Tests
    def test_divide_positive_numbers(self):
        """Test division with positive numbers."""
        assert divide(10, 2) == 5
        assert divide(15, 3) == 5
        assert divide(100, 4) == 25
    
    def test_divide_negative_numbers(self):
        """Test division with negative numbers."""
        assert divide(-10, -2) == 5
        assert divide(-15, -3) == 5
        assert divide(-100, -4) == 25
    
    def test_divide_mixed_numbers(self):
        """Test division with mixed positive and negative numbers."""
        assert divide(10, -2) == -5
        assert divide(-10, 2) == -5
        assert divide(15, -3) == -5
    
    def test_divide_by_one(self):
        """Test division by one."""
        assert divide(42, 1) == 42
        assert divide(-42, 1) == -42
        assert divide(0, 1) == 0
    
    def test_divide_floats(self):
        """Test division with floating point numbers."""
        assert divide(5.5, 2) == 2.75
        assert divide(1, 3) == pytest.approx(0.333333, rel=1e-5)
        assert divide(-4.5, 1.5) == -3.0
    
    def test_divide_large_numbers(self):
        """Test division with large numbers."""
        assert divide(1e6, 1e3) == 1e3
        assert divide(1000000000, 1000) == 1000000
    
    def test_divide_resulting_in_fractions(self):
        """Test division that results in fractions."""
        assert divide(1, 2) == 0.5
        assert divide(3, 2) == 1.5
        assert divide(5, 4) == 1.25
    
    # Division by Zero Tests
    def test_divide_by_zero_raises_exception(self):
        """Test that division by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)
        
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(-10, 0)
        
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(0, 0)
    
    def test_divide_by_zero_with_floats(self):
        """Test division by zero with floating point numbers."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5.5, 0)
        
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(-3.14, 0)
    
    # Edge Cases and Special Values
    def test_very_small_numbers(self):
        """Test operations with very small numbers."""
        assert add(1e-10, 2e-10) == pytest.approx(3e-10)
        assert subtract(1e-10, 0.5e-10) == pytest.approx(0.5e-10)
        assert multiply(1e-5, 1e-5) == pytest.approx(1e-10)
        assert divide(1e-10, 1e-5) == pytest.approx(1e-5)
    
    def test_infinity_operations(self):
        """Test operations that result in infinity."""
        result = divide(1, 1e-308)
        assert result == float('inf') or result > 1e300
    
    # Type Tests
    def test_operations_with_integers(self):
        """Test that operations work with integer inputs."""
        assert isinstance(add(1, 2), (int, float))
        assert isinstance(subtract(5, 3), (int, float))
        assert isinstance(multiply(2, 3), (int, float))
        assert isinstance(divide(6, 2), (int, float))
    
    def test_operations_with_floats(self):
        """Test that operations work with float inputs."""
        assert isinstance(add(1.0, 2.0), (int, float))
        assert isinstance(subtract(5.0, 3.0), (int, float))
        assert isinstance(multiply(2.0, 3.0), (int, float))
        assert isinstance(divide(6.0, 2.0), (int, float))
    
    # Mathematical Properties
    def test_commutative_property(self):
        """Test that addition and multiplication are commutative."""
        a, b = 5, 7
        assert add(a, b) == add(b, a)
        assert multiply(a, b) == multiply(b, a)
        # Subtraction and division are not commutative
        assert subtract(a, b) != subtract(b, a)
        assert divide(a, b) != divide(b, a)
    
    def test_associative_property(self):
        """Test that addition and multiplication are associative."""
        a, b, c = 2, 3, 4
        assert add(add(a, b), c) == add(a, add(b, c))
        assert multiply(multiply(a, b), c) == multiply(a, multiply(b, c))
    
    def test_distributive_property(self):
        """Test distributive property of multiplication over addition."""
        a, b, c = 2, 3, 4
        left = multiply(a, add(b, c))
        right = add(multiply(a, b), multiply(a, c))
        assert left == right
    
    def test_identity_elements(self):
        """Test identity elements for operations."""
        # Addition identity: 0
        assert add(42, 0) == 42
        assert add(0, 42) == 42
        
        # Multiplication identity: 1
        assert multiply(42, 1) == 42
        assert multiply(1, 42) == 42
        
        # Subtraction and division don't have identity elements in the same way
    
    def test_inverse_operations(self):
        """Test that operations are inverses of each other."""
        a, b = 10, 3
        # Addition and subtraction are inverses
        assert subtract(add(a, b), b) == a
        assert add(subtract(a, b), b) == a
        
        # Multiplication and division are inverses (except for divide by zero)
        assert divide(multiply(a, b), b) == a
        assert multiply(divide(a, b), b) == pytest.approx(a)