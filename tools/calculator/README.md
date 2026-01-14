# Calculator Tools

A Python package providing basic arithmetic operations with both programmatic and command-line interfaces.

## Features

- **Basic Arithmetic Operations**: Addition, subtraction, multiplication, and division
- **Type Safety**: Full type hints for all operations
- **Error Handling**: Proper validation and error messages
- **CLI Interface**: Command-line tool for quick calculations
- **Comprehensive Testing**: Extensive test suite with edge cases
- **Python Module Support**: Use as a library in your projects

## Installation

```bash
# Install the package
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

## Usage

### As a Python Library

```python
from tools.calculator import add, subtract, multiply, divide

# Addition
result = add(5, 3)  # Returns: 8

# Subtraction
result = subtract(10, 4)  # Returns: 6

# Multiplication
result = multiply(7, 6)  # Returns: 42

# Division
result = divide(15, 3)  # Returns: 5.0

# Division by zero raises ValueError
try:
    divide(10, 0)
except ValueError as e:
    print(e)  # "Cannot divide by zero"
```

### Command Line Interface

The calculator provides a comprehensive CLI with multiple usage patterns:

#### Basic Usage

```bash
# Addition
python -m tools.calculator add 5 3
# Output: Result: 8

# Subtraction
python -m tools.calculator subtract 10 4
# Output: Result: 6

# Multiplication
python -m tools.calculator multiply 7 6
# Output: Result: 42

# Division
python -m tools.calculator divide 15 3
# Output: Result: 5
```

#### Advanced Examples

```bash
# Working with negative numbers
python -m tools.calculator add -5 3
# Output: Result: -2

# Floating point numbers
python -m tools.calculator multiply 2.5 4
# Output: Result: 10

# Large numbers
python -m tools.calculator divide 1000000 1000
# Output: Result: 1000

# Division by zero (shows error)
python -m tools.calculator divide 10 0
# Output: Error: Cannot divide by zero
```

#### Help and Usage Information

```bash
# Show help
python -m tools.calculator --help

# Output:
# usage: __main__.py [-h] {add,subtract,multiply,divide} num1 num2
#
# Calculator CLI - Perform basic arithmetic operations
#
# positional arguments:
#   {add,subtract,multiply,divide}
#                         Arithmetic operation to perform
#   num1                  First number
#   num2                  Second number
#
# optional arguments:
#   -h, --help            show this help message and exit
#
# Examples:
#   __main__.py add 5 3
#   __main__.py subtract 10 4
#   __main__.py multiply 7 6
#   __main__.py divide 15 3
```

## API Reference

### Core Functions

#### `add(a: float, b: float) -> float`
Adds two numbers together.

**Parameters:**
- `a` (float): First number
- `b` (float): Second number

**Returns:**
- `float`: Sum of a and b

**Example:**
```python
add(5, 3)  # Returns: 8
```

#### `subtract(a: float, b: float) -> float`
Subtracts the second number from the first.

**Parameters:**
- `a` (float): First number
- `b` (float): Second number

**Returns:**
- `float`: Difference of a minus b

**Example:**
```python
subtract(10, 4)  # Returns: 6
```

#### `multiply(a: float, b: float) -> float`
Multiplies two numbers together.

**Parameters:**
- `a` (float): First number
- `b` (float): Second number

**Returns:**
- `float`: Product of a and b

**Example:**
```python
multiply(7, 6)  # Returns: 42
```

#### `divide(a: float, b: float) -> float`
Divides the first number by the second.

**Parameters:**
- `a` (float): Dividend
- `b` (float): Divisor

**Returns:**
- `float`: Quotient of a divided by b

**Raises:**
- `ValueError`: If b is zero (division by zero)

**Example:**
```python
divide(15, 3)  # Returns: 5.0
divide(10, 0)  # Raises ValueError: "Cannot divide by zero"
```

## Testing

The calculator includes comprehensive tests covering:

- Basic operations with positive and negative numbers
- Operations with zero
- Floating point arithmetic
- Large numbers
- Edge cases and mathematical properties
- Error conditions

### Running Tests

```bash
# Run all tests
pytest tools/calculator/tests/

# Run with verbose output
pytest -v tools/calculator/tests/

# Run specific test file
pytest tools/calculator/tests/test_calculator.py

# Run with coverage
pytest --cov=tools.calculator tools/calculator/tests/
```

### Test Coverage

The test suite covers:

- ✅ All four basic operations
- ✅ Positive and negative numbers
- ✅ Mixed number types
- ✅ Zero operations
- ✅ Floating point precision
- ✅ Large numbers
- ✅ Division by zero error handling
- ✅ Mathematical properties (commutative, associative, distributive)
- ✅ Identity elements
- ✅ Inverse operations

## Error Handling

The calculator implements proper error handling:

```python
# Division by zero
from tools.calculator import divide

try:
    result = divide(10, 0)
except ValueError as e:
    print(f"Error: {e}")  # "Error: Cannot divide by zero"

# Invalid CLI usage
# python -m tools.calculator divide 10 0
# Output: Error: Cannot divide by zero
```

## Mathematical Properties

The calculator operations follow standard mathematical properties:

### Commutative Property
- Addition: `add(a, b) == add(b, a)`
- Multiplication: `multiply(a, b) == multiply(b, a)`

### Associative Property
- Addition: `add(add(a, b), c) == add(a, add(b, c))`
- Multiplication: `multiply(multiply(a, b), c) == multiply(a, multiply(b, c))`

### Distributive Property
- `multiply(a, add(b, c)) == add(multiply(a, b), multiply(a, c))`

### Identity Elements
- Addition: `add(a, 0) == a`
- Multiplication: `multiply(a, 1) == a`

## Examples

### Financial Calculations
```python
from tools.calculator import add, multiply

# Calculate total cost with tax
item_price = 29.99
tax_rate = 0.08
tax_amount = multiply(item_price, tax_rate)
total_cost = add(item_price, tax_amount)
print(f"Total: ${total_cost:.2f}")  # Total: $32.39
```

### Scientific Calculations
```python
from tools.calculator import divide, multiply

# Convert temperature: Celsius to Fahrenheit
celsius = 25
fahrenheit = add(multiply(celsius, 9/5), 32)
print(f"{celsius}°C = {fahrenheit}°F")  # 25°C = 77.0°F
```

### Data Processing
```python
from tools.calculator import add, divide

# Calculate average of numbers
numbers = [10, 20, 30, 40, 50]
total = 0
for num in numbers:
    total = add(total, num)

average = divide(total, len(numbers))
print(f"Average: {average}")  # Average: 30.0
```

## Development

### Project Structure
```
tools/calculator/
├── __init__.py          # Package initialization
├── __main__.py          # Module entry point
├── calculator.py        # Core calculator functions
├── cli.py               # Command-line interface
├── requirements.txt     # Dependencies
├── tests/
│   ├── __init__.py
│   └── test_calculator.py
└── README.md           # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Include docstrings for all public functions
- Write comprehensive tests
- Handle edge cases and errors gracefully

## License

This project is part of the OpenHands development environment.

## Support

For issues and questions:
1. Check the test suite for usage examples
2. Review the error messages for common issues
3. Ensure you're using valid numeric inputs
4. Check that the calculator module is properly installed

## Changelog

- **1.0.0**: Initial release with basic operations and CLI
- **1.1.0**: Added comprehensive test suite
- **1.2.0**: Enhanced error handling and documentation