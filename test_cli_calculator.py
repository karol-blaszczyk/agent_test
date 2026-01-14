#!/usr/bin/env python3
"""
Integration tests for the CLI calculator interface.
Tests command-line argument parsing and output formatting using subprocess.
"""

import subprocess
import sys
import os
import pytest


class TestCLICalculator:
    """Test suite for CLI calculator integration."""
    
    @classmethod
    def setup_class(cls):
        """Set up test class with CLI calculator path."""
        cls.cli_path = os.path.join(os.path.dirname(__file__), 'cli_calculator.py')
        cls.python_executable = sys.executable
    
    def run_cli(self, *args):
        """
        Helper method to run the CLI calculator with given arguments.
        
        Args:
            *args: Command line arguments to pass to the CLI
            
        Returns:
            tuple: (return_code, stdout, stderr)
        """
        cmd = [self.python_executable, self.cli_path] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    
    def test_addition_success(self):
        """Test successful addition operation."""
        returncode, stdout, stderr = self.run_cli('add', '5', '3')
        
        assert returncode == 0
        assert stdout == "5.0 + 3.0 = 8.0"
        assert stderr == ""
    
    def test_subtraction_success(self):
        """Test successful subtraction operation."""
        returncode, stdout, stderr = self.run_cli('subtract', '10', '4')
        
        assert returncode == 0
        assert stdout == "10.0 - 4.0 = 6.0"
        assert stderr == ""
    
    def test_multiplication_success(self):
        """Test successful multiplication operation."""
        returncode, stdout, stderr = self.run_cli('multiply', '7', '6')
        
        assert returncode == 0
        assert stdout == "7.0 * 6.0 = 42.0"
        assert stderr == ""
    
    def test_division_success(self):
        """Test successful division operation."""
        returncode, stdout, stderr = self.run_cli('divide', '15', '3')
        
        assert returncode == 0
        assert stdout == "15.0 / 3.0 = 5.0"
        assert stderr == ""
    
    def test_division_by_zero_error(self):
        """Test division by zero error handling."""
        returncode, stdout, stderr = self.run_cli('divide', '10', '0')
        
        assert returncode == 1
        assert stdout == ""
        assert "Error: Cannot divide by zero" in stderr
    
    def test_negative_numbers(self):
        """Test operations with negative numbers."""
        returncode, stdout, stderr = self.run_cli('add', '-5', '3')
        
        assert returncode == 0
        assert stdout == "-5.0 + 3.0 = -2.0"
        assert stderr == ""
    
    def test_decimal_numbers(self):
        """Test operations with decimal numbers."""
        returncode, stdout, stderr = self.run_cli('multiply', '2.5', '4.2')
        
        assert returncode == 0
        assert stdout == "2.5 * 4.2 = 10.5"
        assert stderr == ""
    
    def test_invalid_operation(self):
        """Test invalid operation choice."""
        returncode, stdout, stderr = self.run_cli('power', '2', '3')
        
        assert returncode == 2
        assert stdout == ""
        assert "error" in stderr.lower()
    
    def test_missing_arguments(self):
        """Test missing required arguments."""
        returncode, stdout, stderr = self.run_cli('add')
        
        assert returncode == 2
        assert stdout == ""
        assert "error" in stderr.lower()
    
    def test_too_many_arguments(self):
        """Test too many arguments provided."""
        returncode, stdout, stderr = self.run_cli('add', '1', '2', '3')
        
        assert returncode == 2
        assert stdout == ""
        assert "error" in stderr.lower()
    
    def test_non_numeric_arguments(self):
        """Test non-numeric arguments."""
        returncode, stdout, stderr = self.run_cli('add', 'abc', 'def')
        
        assert returncode == 2
        assert stdout == ""
        assert "error" in stderr.lower()
    
    def test_help_message(self):
        """Test help message display."""
        returncode, stdout, stderr = self.run_cli('--help')
        
        assert returncode == 0
        assert "command-line calculator" in stdout.lower()
        assert "add" in stdout
        assert "subtract" in stdout
        assert "multiply" in stdout
        assert "divide" in stdout
    
    def test_all_operations_consistency(self):
        """Test that all operations produce consistent output format."""
        operations = [
            ('add', '5', '3', '5.0 + 3.0 = 8.0'),
            ('subtract', '8', '3', '8.0 - 3.0 = 5.0'),
            ('multiply', '4', '5', '4.0 * 5.0 = 20.0'),
            ('divide', '12', '4', '12.0 / 4.0 = 3.0')
        ]
        
        for operation, a, b, expected in operations:
            returncode, stdout, stderr = self.run_cli(operation, a, b)
            
            assert returncode == 0, f"Operation {operation} failed"
            assert stdout == expected, f"Operation {operation} output mismatch"
            assert stderr == "", f"Operation {operation} produced stderr"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])