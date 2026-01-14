#!/usr/bin/env python3
"""
Comprehensive tests for the calculator CLI module.
Tests both the CLI interface and the underlying functions.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

from tools.calculator.cli import (
    create_parser, get_operation_func, format_result, main
)
from tools.calculator.calculator import add, subtract, multiply, divide


class TestCLICreation:
    """Test CLI parser creation and configuration."""
    
    def test_create_parser_basic(self):
        """Test that parser is created with correct basic configuration."""
        parser = create_parser()
        
        # Test that parser has the correct program name and description
        assert parser.prog is not None
        assert "calculator" in parser.description.lower()
    
    def test_parser_operation_argument(self):
        """Test that operation argument is properly configured."""
        parser = create_parser()
        
        # Test valid operations
        for operation in ["add", "subtract", "multiply", "divide"]:
            args = parser.parse_args([operation, "1", "2"])
            assert args.operation == operation
            assert args.num1 == 1.0
            assert args.num2 == 2.0
    
    def test_parser_invalid_operation(self):
        """Test that invalid operation raises error."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(["invalid_op", "1", "2"])
    
    def test_parser_number_arguments(self):
        """Test that number arguments are properly parsed as floats."""
        parser = create_parser()
        
        # Test integers
        args = parser.parse_args(["add", "5", "3"])
        assert args.num1 == 5.0
        assert args.num2 == 3.0
        
        # Test floats
        args = parser.parse_args(["add", "5.5", "3.2"])
        assert args.num1 == 5.5
        assert args.num2 == 3.2
        
        # Test negative numbers
        args = parser.parse_args(["add", "-5", "-3.2"])
        assert args.num1 == -5.0
        assert args.num2 == -3.2
    
    def test_parser_missing_arguments(self):
        """Test that missing arguments raise appropriate errors."""
        parser = create_parser()
        
        # Missing operation
        with pytest.raises(SystemExit):
            parser.parse_args(["5", "3"])
        
        # Missing numbers
        with pytest.raises(SystemExit):
            parser.parse_args(["add"])
        
        with pytest.raises(SystemExit):
            parser.parse_args(["add", "5"])
    
    def test_parser_help_message(self):
        """Test that help message contains expected content."""
        parser = create_parser()
        help_text = parser.format_help()
        
        # Check for operation names
        assert "add" in help_text
        assert "subtract" in help_text
        assert "multiply" in help_text
        assert "divide" in help_text
        
        # Check for examples or usage information
        assert "examples" in help_text.lower() or "usage" in help_text.lower()


class TestOperationFunctionMapping:
    """Test operation function mapping."""
    
    def test_get_operation_func_valid_operations(self):
        """Test that valid operations return correct functions."""
        assert get_operation_func("add") == add
        assert get_operation_func("subtract") == subtract
        assert get_operation_func("multiply") == multiply
        assert get_operation_func("divide") == divide
    
    def test_get_operation_func_invalid_operation(self):
        """Test that invalid operation raises KeyError."""
        with pytest.raises(KeyError):
            get_operation_func("invalid_operation")
        
        with pytest.raises(KeyError):
            get_operation_func("power")
        
        with pytest.raises(KeyError):
            get_operation_func("")


class TestResultFormatting:
    """Test result formatting functionality."""
    
    def test_format_result_integers(self):
        """Test formatting of integer results."""
        assert format_result(5.0) == "5"
        assert format_result(0.0) == "0"
        assert format_result(-10.0) == "-10"
        assert format_result(100.0) == "100"
    
    def test_format_result_floats(self):
        """Test formatting of float results."""
        assert format_result(5.5) == "5.5"
        assert format_result(0.1) == "0.1"
        assert format_result(-3.14) == "-3.14"
        assert format_result(2.0) == "2"  # Should be converted to int
    
    def test_format_result_edge_cases(self):
        """Test formatting of edge case results."""
        assert format_result(1.0000000001) == "1.0000000001"
        assert format_result(0.9999999999) == "1.0"  # Python float precision


class TestMainFunction:
    """Test the main function integration."""
    
    @patch('tools.calculator.cli.create_parser')
    @patch('tools.calculator.cli.format_result')
    @patch('tools.calculator.cli.get_operation_func')
    def test_main_successful_operation(self, mock_get_func, mock_format, mock_create_parser):
        """Test main function with successful operation."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_create_parser.return_value = mock_parser
        
        mock_args = MagicMock()
        mock_args.operation = "add"
        mock_args.num1 = 5.0
        mock_args.num2 = 3.0
        mock_parser.parse_args.return_value = mock_args
        
        mock_operation_func = MagicMock(return_value=8.0)
        mock_get_func.return_value = mock_operation_func
        mock_format.return_value = "8"
        
        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            
            # Verify operation was called correctly
            mock_operation_func.assert_called_once_with(5.0, 3.0)
            mock_format.assert_called_once_with(8.0)
            
            # Verify output
            output = mock_stdout.getvalue().strip()
            assert output == "Result: 8"
    
    @patch('tools.calculator.cli.create_parser')
    @patch('tools.calculator.cli.get_operation_func')
    def test_main_division_by_zero(self, mock_get_func, mock_create_parser):
        """Test main function with division by zero error."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_create_parser.return_value = mock_parser
        
        mock_args = MagicMock()
        mock_args.operation = "divide"
        mock_args.num1 = 10.0
        mock_args.num2 = 0.0
        mock_parser.parse_args.return_value = mock_args
        
        mock_operation_func = MagicMock(side_effect=ValueError("Cannot divide by zero"))
        mock_get_func.return_value = mock_operation_func
        
        # Capture stderr and test sys.exit
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Verify exit code
            assert exc_info.value.code == 1
            
            # Verify error message
            error_output = mock_stderr.getvalue().strip()
            assert "Error: Cannot divide by zero" in error_output
    
    @patch('tools.calculator.cli.create_parser')
    @patch('tools.calculator.cli.get_operation_func')
    def test_main_unexpected_error(self, mock_get_func, mock_create_parser):
        """Test main function with unexpected error."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_create_parser.return_value = mock_parser
        
        mock_args = MagicMock()
        mock_args.operation = "add"
        mock_args.num1 = 5.0
        mock_args.num2 = 3.0
        mock_parser.parse_args.return_value = mock_args
        
        mock_operation_func = MagicMock(side_effect=Exception("Unexpected error"))
        mock_get_func.return_value = mock_operation_func
        
        # Capture stderr and test sys.exit
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Verify exit code
            assert exc_info.value.code == 1
            
            # Verify error message
            error_output = mock_stderr.getvalue().strip()
            assert "Unexpected error: Unexpected error" in error_output


class TestCLIIntegration:
    """Integration tests for the complete CLI workflow."""
    
    def test_addition_integration(self):
        """Test complete addition workflow."""
        parser = create_parser()
        args = parser.parse_args(["add", "5", "3"])
        
        operation_func = get_operation_func(args.operation)
        result = operation_func(args.num1, args.num2)
        formatted_result = format_result(result)
        
        assert result == 8.0
        assert formatted_result == "8"
    
    def test_subtraction_integration(self):
        """Test complete subtraction workflow."""
        parser = create_parser()
        args = parser.parse_args(["subtract", "10", "4"])
        
        operation_func = get_operation_func(args.operation)
        result = operation_func(args.num1, args.num2)
        formatted_result = format_result(result)
        
        assert result == 6.0
        assert formatted_result == "6"
    
    def test_multiplication_integration(self):
        """Test complete multiplication workflow."""
        parser = create_parser()
        args = parser.parse_args(["multiply", "7", "6"])
        
        operation_func = get_operation_func(args.operation)
        result = operation_func(args.num1, args.num2)
        formatted_result = format_result(result)
        
        assert result == 42.0
        assert formatted_result == "42"
    
    def test_division_integration(self):
        """Test complete division workflow."""
        parser = create_parser()
        args = parser.parse_args(["divide", "15", "3"])
        
        operation_func = get_operation_func(args.operation)
        result = operation_func(args.num1, args.num2)
        formatted_result = format_result(result)
        
        assert result == 5.0
        assert formatted_result == "5"
    
    def test_division_by_zero_integration(self):
        """Test division by zero in complete workflow."""
        parser = create_parser()
        args = parser.parse_args(["divide", "10", "0"])
        
        operation_func = get_operation_func(args.operation)
        
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            operation_func(args.num1, args.num2)
    
    def test_negative_numbers_integration(self):
        """Test operations with negative numbers."""
        parser = create_parser()
        args = parser.parse_args(["add", "-5", "3"])
        
        operation_func = get_operation_func(args.operation)
        result = operation_func(args.num1, args.num2)
        formatted_result = format_result(result)
        
        assert result == -2.0
        assert formatted_result == "-2"
    
    def test_decimal_numbers_integration(self):
        """Test operations with decimal numbers."""
        parser = create_parser()
        args = parser.parse_args(["multiply", "2.5", "4.2"])
        
        operation_func = get_operation_func(args.operation)
        result = operation_func(args.num1, args.num2)
        formatted_result = format_result(result)
        
        assert result == 10.5
        assert formatted_result == "10.5"


class TestCLICoverage:
    """Additional tests to ensure complete coverage of CLI functionality."""
    
    def test_format_result_zero(self):
        """Test formatting of zero."""
        assert format_result(0.0) == "0"
        assert format_result(-0.0) == "0"
    
    def test_format_result_very_small_floats(self):
        """Test formatting of very small floats."""
        result = format_result(0.0000001)
        assert isinstance(result, str)
        assert "0.0000001" in result or "1e-07" in result
    
    def test_format_result_large_numbers(self):
        """Test formatting of large numbers."""
        assert format_result(1000000.0) == "1000000"
        assert format_result(1e10) == "10000000000"
    
    def test_all_operations_with_zero(self):
        """Test all operations with zero operands."""
        parser = create_parser()
        
        # Add with zero
        args = parser.parse_args(["add", "0", "5"])
        operation_func = get_operation_func(args.operation)
        result = operation_func(args.num1, args.num2)
        assert result == 5.0
        
        # Subtract with zero
        args = parser.parse_args(["subtract", "5", "0"])
        operation_func = get_operation_func(args.operation)
        result = operation_func(args.num1, args.num2)
        assert result == 5.0
        
        # Multiply with zero
        args = parser.parse_args(["multiply", "5", "0"])
        operation_func = get_operation_func(args.operation)
        result = operation_func(args.num1, args.num2)
        assert result == 0.0
        
        # Divide zero by number
        args = parser.parse_args(["divide", "0", "5"])
        operation_func = get_operation_func(args.operation)
        result = operation_func(args.num1, args.num2)
        assert result == 0.0
    
    def test_operation_argument_validation(self):
        """Test that operation argument validation works correctly."""
        parser = create_parser()
        
        # Test all valid operations
        valid_operations = ["add", "subtract", "multiply", "divide"]
        for op in valid_operations:
            args = parser.parse_args([op, "1", "2"])
            assert args.operation == op
        
        # Test case variations (should work)
        args = parser.parse_args(["ADD", "1", "2"])
        assert args.operation == "ADD"  # argparse preserves case
    
    def test_number_parsing_edge_cases(self):
        """Test edge cases in number parsing."""
        parser = create_parser()
        
        # Very large numbers
        args = parser.parse_args(["add", "1e10", "2e10"])
        assert args.num1 == 1e10
        assert args.num2 == 2e10
        
        # Very small numbers
        args = parser.parse_args(["add", "1e-10", "2e-10"])
        assert args.num1 == 1e-10
        assert args.num2 == 2e-10
        
        # Scientific notation
        args = parser.parse_args(["add", "1.5e2", "2.5e2"])
        assert args.num1 == 150.0
        assert args.num2 == 250.0


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])