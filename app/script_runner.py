"""
Script Runner Module

This module provides a ScriptRunner class that can execute Python scripts,
capture their stdout/stderr, and return execution results with status,
output, and error information.
"""

import subprocess
import sys
import tempfile
import os
from typing import Dict, Any, Optional


def safe_script_runner(script_content: str, timeout: int = 30, script_name: str = "script.py") -> Dict[str, Any]:
    """
    Safely execute Python script in a subprocess with timeout and error handling.
    
    This function provides a safe way to execute Python scripts by running them
    in an isolated subprocess with timeout protection and comprehensive error
    handling. It captures both stdout and stderr output.
    
    Args:
        script_content: The Python code to execute
        timeout: Maximum execution time in seconds (default: 30)
        script_name: Optional name for the script file (default: "script.py")
        
    Returns:
        Dict containing execution results:
            - status: 'success' or 'error'
            - stdout: Standard output as string
            - stderr: Standard error as string  
            - return_code: Process return code (0 for success)
            - error_message: Error message if execution failed
            - execution_time: Time taken to execute in seconds
            
    Raises:
        This function does not raise exceptions - all errors are captured
        in the returned result dictionary.
        
    Example:
        >>> result = safe_script_runner('print("Hello World")')
        >>> print(result['status'])  # 'success'
        >>> print(result['stdout'])  # 'Hello World\n'
    """
    import time
    
    start_time = time.time()
    
    # Create a temporary file to store the script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(script_content)
        temp_file_path = temp_file.name
    
    try:
        # Execute the script using subprocess with timeout
        result = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        execution_time = time.time() - start_time
        
        # Determine status based on return code
        status = 'success' if result.returncode == 0 else 'error'
        
        return {
            'status': status,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode,
            'error_message': result.stderr if result.returncode != 0 else None,
            'execution_time': round(execution_time, 3)
        }
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return {
            'status': 'error',
            'stdout': '',
            'stderr': f'Script execution timed out after {timeout} seconds',
            'return_code': -1,
            'error_message': f'Script execution timed out after {timeout} seconds',
            'execution_time': round(execution_time, 3)
        }
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            'status': 'error',
            'stdout': '',
            'stderr': str(e),
            'return_code': -1,
            'error_message': f'Failed to execute script: {str(e)}',
            'execution_time': round(execution_time, 3)
        }
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass  # Ignore cleanup errors


class ScriptRunner:
    """
    A class to execute Python scripts and capture their output.
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the ScriptRunner.
        
        Args:
            timeout: Maximum execution time in seconds (default: 30)
        """
        self.timeout = timeout
    
    def execute_script(self, script_content: str, script_name: str = "script.py") -> Dict[str, Any]:
        """
        Execute a Python script and capture its output.
        
        Args:
            script_content: The Python code to execute
            script_name: Optional name for the script file (default: "script.py")
            
        Returns:
            Dict containing:
                - status: 'success' or 'error'
                - stdout: Standard output as string
                - stderr: Standard error as string
                - return_code: Process return code
                - error_message: Error message if execution failed
        """
        # Create a temporary file to store the script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(script_content)
            temp_file_path = temp_file.name
        
        try:
            # Execute the script using subprocess
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Determine status based on return code
            status = 'success' if result.returncode == 0 else 'error'
            
            return {
                'status': status,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'error_message': result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'error',
                'stdout': '',
                'stderr': f'Script execution timed out after {self.timeout} seconds',
                'return_code': -1,
                'error_message': f'Script execution timed out after {self.timeout} seconds'
            }
        except Exception as e:
            return {
                'status': 'error',
                'stdout': '',
                'stderr': str(e),
                'return_code': -1,
                'error_message': f'Failed to execute script: {str(e)}'
            }
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass  # Ignore cleanup errors
    
    def execute_file(self, file_path: str) -> Dict[str, Any]:
        """
        Execute a Python script from a file path.
        
        Args:
            file_path: Path to the Python script file
            
        Returns:
            Dict with execution results (same format as execute_script)
        """
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as file:
                script_content = file.read()
            
            # Execute using the main method
            return self.execute_script(script_content, os.path.basename(file_path))
            
        except FileNotFoundError:
            return {
                'status': 'error',
                'stdout': '',
                'stderr': f'File not found: {file_path}',
                'return_code': -1,
                'error_message': f'File not found: {file_path}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'stdout': '',
                'stderr': str(e),
                'return_code': -1,
                'error_message': f'Failed to read file: {str(e)}'
            }


# Example usage and testing
if __name__ == "__main__":
    print("=== Testing safe_script_runner function ===")
    
    # Test 1: Simple successful execution
    result = safe_script_runner('print("Hello from safe_script_runner!")')
    print(f"Test 1 - Status: {result['status']}, Output: {result['stdout'].strip()}")
    
    # Test 2: Script with error
    result = safe_script_runner('raise ValueError("Test error")')
    print(f"Test 2 - Status: {result['status']}, Error: {'ValueError' in result['stderr']}")
    
    # Test 3: Using custom timeout
    result = safe_script_runner('import time\ntime.sleep(2)', timeout=1)
    print(f"Test 3 - Timeout test: {result['status']}")
    
    print("\n=== Testing original ScriptRunner class ===")
    
    # Create a test script
    test_script = """
print("Hello from ScriptRunner!")
print("This is stdout output")
import sys
print("This is stderr output", file=sys.stderr)
print("Script completed successfully")
"""
    
    # Create a runner and execute the test script
    runner = ScriptRunner()
    result = runner.execute_script(test_script)
    
    print(f"ScriptRunner test - Status: {result['status']}")
    print(f"Return code: {result['return_code']}")
    print(f"Stdout: {result['stdout']}")
    print(f"Stderr: {result['stderr']}")
    if result['error_message']:
        print(f"Error: {result['error_message']}")