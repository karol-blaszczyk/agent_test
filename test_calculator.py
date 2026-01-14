import pytest
from calculator import Calculator


class TestCalculator:
    """Test cases for the Calculator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.calc = Calculator()
    
    def test_add(self):
        """Test addition operation with comprehensive edge cases."""
        # Basic positive numbers
        assert self.calc.add(2, 3) == 5
        assert self.calc.add(10, 20) == 30
        
        # Negative numbers
        assert self.calc.add(-1, -2) == -3
        assert self.calc.add(-5, 3) == -2
        assert self.calc.add(5, -3) == 2
        
        # Zero cases
        assert self.calc.add(0, 0) == 0
        assert self.calc.add(5, 0) == 5
        assert self.calc.add(0, -3) == -3
        
        # Decimal numbers
        assert self.calc.add(1.5, 2.5) == 4.0
        assert self.calc.add(0.1, 0.2) == pytest.approx(0.3)
        assert self.calc.add(-1.5, 2.5) == 1.0
        
        # Large numbers
        assert self.calc.add(1000000, 2000000) == 3000000
        assert self.calc.add(-1000000, 1000000) == 0
    
    def test_subtract(self):
        """Test subtraction operation with comprehensive edge cases."""
        # Basic positive numbers
        assert self.calc.subtract(5, 3) == 2
        assert self.calc.subtract(10, 5) == 5
        
        # Negative numbers
        assert self.calc.subtract(-1, -2) == 1
        assert self.calc.subtract(-5, 3) == -8
        assert self.calc.subtract(5, -3) == 8
        
        # Zero cases
        assert self.calc.subtract(0, 0) == 0
        assert self.calc.subtract(5, 0) == 5
        assert self.calc.subtract(0, 5) == -5
        
        # Same numbers
        assert self.calc.subtract(1, 1) == 0
        assert self.calc.subtract(-1, -1) == 0
        
        # Decimal numbers
        assert self.calc.subtract(2.5, 1.5) == 1.0
        assert self.calc.subtract(1.0, 0.9) == pytest.approx(0.1)
        assert self.calc.subtract(-2.5, 1.5) == -4.0
        
        # Large numbers
        assert self.calc.subtract(1000000, 500000) == 500000
        assert self.calc.subtract(-1000000, -500000) == -500000
    
    def test_multiply(self):
        """Test multiplication operation with comprehensive edge cases."""
        # Basic positive numbers
        assert self.calc.multiply(3, 4) == 12
        assert self.calc.multiply(5, 6) == 30
        
        # Negative numbers
        assert self.calc.multiply(-1, 5) == -5
        assert self.calc.multiply(-2, -3) == 6
        assert self.calc.multiply(4, -2) == -8
        
        # Zero cases
        assert self.calc.multiply(0, 0) == 0
        assert self.calc.multiply(5, 0) == 0
        assert self.calc.multiply(0, -10) == 0
        
        # One cases
        assert self.calc.multiply(1, 1) == 1
        assert self.calc.multiply(5, 1) == 5
        assert self.calc.multiply(1, -5) == -5
        
        # Decimal numbers
        assert self.calc.multiply(2.5, 4) == 10.0
        assert self.calc.multiply(0.5, 0.5) == pytest.approx(0.25)
        assert self.calc.multiply(-2.5, 2) == -5.0
        
        # Large numbers
        assert self.calc.multiply(1000, 1000) == 1000000
        assert self.calc.multiply(-1000, 1000) == -1000000
    
    def test_divide(self):
        """Test division operation with comprehensive edge cases."""
        # Basic positive numbers
        assert self.calc.divide(10, 2) == 5
        assert self.calc.divide(20, 4) == 5
        
        # Negative numbers
        assert self.calc.divide(-10, 2) == -5
        assert self.calc.divide(10, -2) == -5
        assert self.calc.divide(-10, -2) == 5
        
        # Zero numerator
        assert self.calc.divide(0, 5) == 0
        assert self.calc.divide(0, -5) == 0
        
        # Decimal numbers
        assert self.calc.divide(5, 2) == 2.5
        assert self.calc.divide(1, 3) == pytest.approx(0.333333, rel=1e-5)
        assert self.calc.divide(-5, 2) == -2.5
        
        # One cases
        assert self.calc.divide(5, 1) == 5
        assert self.calc.divide(-5, 1) == -5
        assert self.calc.divide(1, 1) == 1
        
        # Large numbers
        assert self.calc.divide(1000000, 1000) == 1000
        assert self.calc.divide(-1000000, 1000) == -1000
    
    def test_divide_by_zero(self):
        """Test division by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            self.calc.divide(10, 0)
        
        # Test with negative numbers
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            self.calc.divide(-10, 0)
        
        # Test with zero numerator
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            self.calc.divide(0, 0)
    
    def test_floating_point_precision(self):
        """Test floating point arithmetic precision."""
        # Test that floating point operations are handled correctly
        result = self.calc.add(0.1, 0.2)
        assert result == pytest.approx(0.3, rel=1e-10)
        
        result = self.calc.multiply(0.1, 3)
        assert result == pytest.approx(0.3, rel=1e-10)
        
        result = self.calc.divide(1, 3)
        assert result == pytest.approx(0.3333333333333333, rel=1e-10)
    
    def test_operation_commutativity(self):
        """Test that addition and multiplication are commutative."""
        # Addition should be commutative: a + b = b + a
        assert self.calc.add(5, 3) == self.calc.add(3, 5)
        assert self.calc.add(-2, 7) == self.calc.add(7, -2)
        
        # Multiplication should be commutative: a * b = b * a
        assert self.calc.multiply(4, 6) == self.calc.multiply(6, 4)
        assert self.calc.multiply(-3, 5) == self.calc.multiply(5, -3)
        
        # Subtraction and division are NOT commutative
        assert self.calc.subtract(10, 3) != self.calc.subtract(3, 10)
        assert self.calc.divide(12, 3) != self.calc.divide(3, 12)