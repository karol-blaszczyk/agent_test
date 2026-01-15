import unittest
from greet import greet


class TestGreet(unittest.TestCase):
    """Test cases for the greet function."""
    
    def test_greet_normal_case(self):
        """Test greet function with a normal name."""
        result = greet("Alice")
        self.assertEqual(result, "Hello Alice")
    
    def test_greet_empty_string(self):
        """Test greet function with an empty string."""
        result = greet("")
        self.assertEqual(result, "Hello ")
    
    def test_greet_none_handling(self):
        """Test greet function with None input."""
        result = greet(None)
        self.assertEqual(result, "Hello None")
    
    def test_greet_with_spaces(self):
        """Test greet function with names containing spaces."""
        result = greet("John Doe")
        self.assertEqual(result, "Hello John Doe")
    
    def test_greet_with_special_characters(self):
        """Test greet function with names containing special characters."""
        result = greet("Mary-Jane")
        self.assertEqual(result, "Hello Mary-Jane")


if __name__ == '__main__':
    unittest.main()