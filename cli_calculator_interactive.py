#!/usr/bin/env python3
"""
Interactive CLI Calculator with menu-driven interface.
Provides add, subtract, multiply, divide operations with input validation and error handling.
"""

import sys
from calculator import Calculator


def display_menu():
    """Display the main menu options."""
    print("\n" + "="*40)
    print("        INTERACTIVE CALCULATOR")
    print("="*40)
    print("1. Addition (+)")
    print("2. Subtraction (-)")
    print("3. Multiplication (*)")
    print("4. Division (/)")
    print("5. Exit")
    print("="*40)


def get_number(prompt):
    """Get a valid number from user input."""
    while True:
        try:
            value = input(prompt)
            return float(value)
        except ValueError:
            print(f"❌ Invalid input: '{value}'. Please enter a valid number.")


def get_operation_choice():
    """Get a valid operation choice from user."""
    while True:
        choice = input("\nSelect operation (1-5): ").strip()
        if choice in ['1', '2', '3', '4', '5']:
            return choice
        print(f"❌ Invalid choice: '{choice}'. Please select 1-5.")


def perform_calculation(calc, operation, num1, num2):
    """Perform the selected calculation with error handling."""
    try:
        if operation == '1':  # Addition
            result = calc.add(num1, num2)
            operation_symbol = '+'
        elif operation == '2':  # Subtraction
            result = calc.subtract(num1, num2)
            operation_symbol = '-'
        elif operation == '3':  # Multiplication
            result = calc.multiply(num1, num2)
            operation_symbol = '*'
        elif operation == '4':  # Division
            result = calc.divide(num1, num2)
            operation_symbol = '/'
        else:
            raise ValueError("Invalid operation selected")
        
        print(f"\n✅ Result: {num1} {operation_symbol} {num2} = {result}")
        return result
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return None


def main():
    """Main function to run the interactive calculator."""
    print("Welcome to the Interactive Calculator!")
    calc = Calculator()
    
    while True:
        try:
            display_menu()
            choice = get_operation_choice()
            
            if choice == '5':  # Exit
                print("\n👋 Thank you for using the calculator. Goodbye!")
                break
            
            # Get numbers from user
            print(f"\n--- {get_operation_name(choice)} ---")
            num1 = get_number("Enter first number: ")
            num2 = get_number("Enter second number: ")
            
            # Perform calculation
            perform_calculation(calc, choice, num1, num2)
            
            # Ask if user wants to continue
            if not ask_continue():
                print("\n👋 Thank you for using the calculator. Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Calculator interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
            print("Please try again.")


def get_operation_name(choice):
    """Get the operation name for display."""
    names = {
        '1': 'Addition',
        '2': 'Subtraction', 
        '3': 'Multiplication',
        '4': 'Division'
    }
    return names.get(choice, 'Unknown Operation')


def ask_continue():
    """Ask user if they want to continue using the calculator."""
    while True:
        response = input("\nWould you like to perform another calculation? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("❌ Please enter 'y' for yes or 'n' for no.")


if __name__ == "__main__":
    main()