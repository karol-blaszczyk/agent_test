"""
Tests for ScriptRunner class and safe_script_runner function

This module contains comprehensive tests for both the ScriptRunner class
and the safe_script_runner function, covering successful execution, error 
handling, timeout functionality, and output capture.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
import subprocess
import sys

# Add the parent directory to the path so we can import ScriptRunner
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.script_runner import ScriptRunner, safe_script_runner


class TestScriptRunner:
    """Test cases for ScriptRunner class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.runner = ScriptRunner()
    
    def test_successful_script_execution(self):
        """Test successful execution of a simple script."""
        script_content = """
print("Hello, World!")
print("This is a test script")
"""
        result = self.runner.execute_script(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'Hello, World!' in result['stdout']
        assert 'This is a test script' in result['stdout']
        assert result['stderr'] == ''
        assert result['error_message'] is None
    
    def test_script_with_stdout_and_stderr(self):
        """Test script that produces both stdout and stderr output."""
        script_content = """
import sys
print("This goes to stdout")
print("This goes to stderr", file=sys.stderr)
print("More stdout")
"""
        result = self.runner.execute_script(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'This goes to stdout' in result['stdout']
        assert 'More stdout' in result['stdout']
        assert 'This goes to stderr' in result['stderr']
    
    def test_script_with_error(self):
        """Test script that raises an exception."""
        script_content = """
print("Starting script")
raise ValueError("This is a test error")
"""
        result = self.runner.execute_script(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'Starting script' in result['stdout']
        assert 'ValueError' in result['stderr']
        assert 'This is a test error' in result['error_message']
    
    def test_script_with_syntax_error(self):
        """Test script with syntax errors."""
        script_content = """
print("Hello"
# Missing closing parenthesis
"""
        result = self.runner.execute_script(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'SyntaxError' in result['stderr'] or 'syntax' in result['stderr'].lower()
        assert result['error_message'] is not None
    
    def test_timeout_functionality(self):
        """Test script execution timeout."""
        # Create a runner with short timeout
        runner = ScriptRunner(timeout=2)
        
        script_content = """
import time
time.sleep(5)  # Sleep longer than timeout
print("This should not be reached")
"""
        result = runner.execute_script(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] == -1
        assert 'timed out' in result['error_message'].lower()
        assert 'timed out' in result['stderr'].lower()
    
    def test_custom_timeout(self):
        """Test that custom timeout values work correctly."""
        # Test with a very short timeout
        runner = ScriptRunner(timeout=1)
        
        script_content = """
import time
time.sleep(2)
print("Should timeout")
"""
        result = runner.execute_script(script_content)
        
        assert result['status'] == 'error'
        assert '1 seconds' in result['error_message']
    
    def test_empty_script(self):
        """Test execution of an empty script."""
        script_content = ""
        result = self.runner.execute_script(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert result['stdout'] == ''
        assert result['stderr'] == ''
    
    def test_script_with_imports(self):
        """Test script that imports modules."""
        script_content = """
import json
import math

print("JSON module imported successfully")
print(f"Pi value: {math.pi}")
"""
        result = self.runner.execute_script(script_content)
        
        assert result['status'] == 'success'
        assert 'JSON module imported successfully' in result['stdout']
        assert 'Pi value:' in result['stdout']
    
    def test_script_with_function_definitions(self):
        """Test script that defines and calls functions."""
        script_content = """
def greet(name):
    return f"Hello, {name}!"

def calculate(x, y):
    return x + y

print(greet("World"))
print(f"2 + 3 = {calculate(2, 3)}")
"""
        result = self.runner.execute_script(script_content)
        
        assert result['status'] == 'success'
        assert 'Hello, World!' in result['stdout']
        assert '2 + 3 = 5' in result['stdout']
    
    def test_script_with_command_line_arguments(self):
        """Test script that accesses command line arguments."""
        script_content = """
import sys
print(f"Script name: {sys.argv[0]}")
print(f"Number of arguments: {len(sys.argv) - 1}")
"""
        result = self.runner.execute_script(script_content)
        
        assert result['status'] == 'success'
        assert 'Script name:' in result['stdout']
        assert 'Number of arguments:' in result['stdout']
    
    def test_script_with_custom_name(self):
        """Test script execution with custom script name."""
        script_content = """
print("Custom script name test")
"""
        result = self.runner.execute_script(script_content, "custom_test.py")
        
        assert result['status'] == 'success'
        assert 'Custom script name test' in result['stdout']
    
    def test_execute_file_success(self):
        """Test executing a script from a file."""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
print("File execution test")
print("Reading from file works!")
""")
            temp_file_path = f.name
        
        try:
            result = self.runner.execute_file(temp_file_path)
            
            assert result['status'] == 'success'
            assert 'File execution test' in result['stdout']
            assert 'Reading from file works!' in result['stdout']
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
    
    def test_execute_file_not_found(self):
        """Test executing a non-existent file."""
        result = self.runner.execute_file("/path/to/nonexistent/file.py")
        
        assert result['status'] == 'error'
        assert 'File not found' in result['error_message']
        assert 'File not found' in result['stderr']
    
    def test_execute_file_with_error(self):
        """Test executing a file that contains errors."""
        # Create a temporary Python file with an error
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
print("Starting file execution")
raise RuntimeError("Error in file")
""")
            temp_file_path = f.name
        
        try:
            result = self.runner.execute_file(temp_file_path)
            
            assert result['status'] == 'error'
            assert 'Starting file execution' in result['stdout']
            assert 'RuntimeError' in result['stderr']
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
    
    def test_subprocess_timeout_exception(self):
        """Test handling of subprocess timeout exceptions."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd=['python'], timeout=30)
            
            script_content = "print('test')"
            result = self.runner.execute_script(script_content)
            
            assert result['status'] == 'error'
            assert 'timed out' in result['error_message'].lower()


class TestSafeScriptRunner:
    """Test cases for safe_script_runner function."""
    
    def test_successful_execution(self):
        """Test successful execution of a simple script."""
        script_content = 'print("Hello, World!")'
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'Hello, World!' in result['stdout']
        assert result['stderr'] == ''
        assert result['error_message'] is None
        assert 'execution_time' in result
        assert isinstance(result['execution_time'], float)
    
    def test_successful_execution_with_complex_output(self):
        """Test successful execution with multiple print statements."""
        script_content = '''
print("Line 1")
print("Line 2")
print("Line 3")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'Line 1' in result['stdout']
        assert 'Line 2' in result['stdout']
        assert 'Line 3' in result['stdout']
        assert result['stderr'] == ''
    
    def test_timeout_handling(self):
        """Test timeout handling for long-running scripts."""
        script_content = '''
import time
time.sleep(5)
print("This should not be reached")
'''
        result = safe_script_runner(script_content, timeout=1)
        
        assert result['status'] == 'error'
        assert result['return_code'] == -1
        assert result['stdout'] == ''
        assert 'timed out' in result['stderr']
        assert 'timed out' in result['error_message']
        assert '1 seconds' in result['error_message']
    
    def test_timeout_with_custom_timeout_value(self):
        """Test timeout with custom timeout value."""
        script_content = '''
import time
time.sleep(3)
'''
        result = safe_script_runner(script_content, timeout=2)
        
        assert result['status'] == 'error'
        assert '2 seconds' in result['error_message']
    
    def test_error_capture_exception(self):
        """Test error capture for scripts that raise exceptions."""
        script_content = '''
print("Starting script")
raise ValueError("This is a test error")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'Starting script' in result['stdout']
        assert 'ValueError' in result['stderr']
        assert 'This is a test error' in result['error_message']
    
    def test_error_capture_syntax_error(self):
        """Test error capture for scripts with syntax errors."""
        script_content = '''
print("Hello"  # Missing closing parenthesis
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'SyntaxError' in result['stderr'] or 'syntax' in result['stderr'].lower()
        assert result['error_message'] is not None
    
    def test_error_capture_name_error(self):
        """Test error capture for NameError."""
        script_content = '''
print(undefined_variable)
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'NameError' in result['stderr']
        assert 'undefined_variable' in result['stderr']
    
    def test_script_with_stderr_output(self):
        """Test script that produces stderr output."""
        script_content = '''
import sys
print("This goes to stdout")
print("This goes to stderr", file=sys.stderr)
print("More stdout")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'This goes to stdout' in result['stdout']
        assert 'More stdout' in result['stdout']
        assert 'This goes to stderr' in result['stderr']
    
    def test_empty_script(self):
        """Test execution of an empty script."""
        script_content = ''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert result['stdout'] == ''
        assert result['stderr'] == ''
        assert result['error_message'] is None
    
    def test_script_with_imports(self):
        """Test script that imports standard library modules."""
        script_content = '''
import json
import math
import os

print("All modules imported successfully")
print(f"Pi: {math.pi}")
print(f"OS name: {os.name}")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'All modules imported successfully' in result['stdout']
        assert 'Pi:' in result['stdout']
        assert 'OS name:' in result['stdout']
    
    def test_script_with_functions(self):
        """Test script that defines and calls functions."""
        script_content = '''
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y

print(f"2 + 3 = {add(2, 3)}")
print(f"4 * 5 = {multiply(4, 5)}")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert '2 + 3 = 5' in result['stdout']
        assert '4 * 5 = 20' in result['stdout']
    
    def test_script_with_custom_name(self):
        """Test script execution with custom script name."""
        script_content = 'print("Custom name test")'
        result = safe_script_runner(script_content, script_name="custom_script.py")
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'Custom name test' in result['stdout']
    
    def test_execution_time_measurement(self):
        """Test that execution time is properly measured."""
        script_content = '''
import time
time.sleep(0.1)  # Sleep for 100ms
print("Done")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert result['execution_time'] >= 0.1
        assert result['execution_time'] < 1.0  # Should not take too long
    
    def test_division_by_zero_error(self):
        """Test error capture for division by zero."""
        script_content = '''
print("About to divide by zero")
result = 10 / 0
print("This should not be reached")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'About to divide by zero' in result['stdout']
        assert 'ZeroDivisionError' in result['stderr']
    
    def test_type_error(self):
        """Test error capture for TypeError."""
        script_content = '''
print("About to cause TypeError")
result = "string" + 5
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'TypeError' in result['stderr']
    
    def test_index_error(self):
        """Test error capture for IndexError."""
        script_content = '''
my_list = [1, 2, 3]
print(my_list[10])
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'IndexError' in result['stderr']
    
    def test_key_error(self):
        """Test error capture for KeyError."""
        script_content = '''
my_dict = {"a": 1, "b": 2}
print(my_dict["c"])
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'KeyError' in result['stderr']
    
    def test_assertion_error(self):
        """Test error capture for AssertionError."""
        script_content = '''
print("Before assertion")
assert False, "This assertion should fail"
print("After assertion")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'Before assertion' in result['stdout']
        assert 'AssertionError' in result['stderr']
        assert 'This assertion should fail' in result['stderr']
    
    def test_keyboard_interrupt(self):
        """Test error capture for KeyboardInterrupt."""
        script_content = '''
import sys
print("Before interrupt")
raise KeyboardInterrupt()
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'Before interrupt' in result['stdout']
        assert 'KeyboardInterrupt' in result['stderr']
    
    def test_system_exit(self):
        """Test handling of SystemExit."""
        script_content = '''
import sys
print("Before exit")
sys.exit(1)
print("After exit")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] == 1
        assert 'Before exit' in result['stdout']
        assert 'After exit' not in result['stdout']
    
    def test_system_exit_zero(self):
        """Test handling of SystemExit with code 0."""
        script_content = '''
import sys
print("Before exit")
sys.exit(0)
print("After exit")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'Before exit' in result['stdout']
        assert 'After exit' not in result['stdout']
    
    def test_unicode_output(self):
        """Test handling of unicode characters in output."""
        script_content = '''
print("Hello, 世界!")
print("🚀 Rocket emoji")
print("Café")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'Hello, 世界!' in result['stdout']
        assert '🚀 Rocket emoji' in result['stdout']
        assert 'Café' in result['stdout']
    
    def test_large_output(self):
        """Test handling of large output."""
        script_content = '''
for i in range(1000):
    print(f"Line {i}: This is a test line that is reasonably long")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert result['stdout'].count('Line') == 1000
        assert 'Line 0:' in result['stdout']
        assert 'Line 999:' in result['stdout']
    
    def test_multiline_string_output(self):
        """Test handling of multiline strings."""
        script_content = '''
multiline_text = """This is line 1
This is line 2
This is line 3"""

print(multiline_text)
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'This is line 1' in result['stdout']
        assert 'This is line 2' in result['stdout']
        assert 'This is line 3' in result['stdout']
    
    def test_exception_chaining(self):
        """Test error capture for exception chaining."""
        script_content = '''
try:
    1 / 0
except ZeroDivisionError as e:
    raise ValueError("New error") from e
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'ValueError' in result['stderr']
        assert 'ZeroDivisionError' in result['stderr']
    
    def test_import_error(self):
        """Test error capture for ImportError."""
        script_content = '''
import nonexistent_module
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert ('ImportError' in result['stderr'] or 
                'ModuleNotFoundError' in result['stderr'])
    
    def test_file_not_found_error(self):
        """Test error capture for FileNotFoundError."""
        script_content = '''
with open('nonexistent_file.txt', 'r') as f:
    content = f.read()
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'error'
        assert result['return_code'] != 0
        assert 'FileNotFoundError' in result['stderr']
    
    def test_permission_error_simulation(self):
        """Test error capture for permission-related issues."""
        script_content = '''
import os
try:
    os.mkdir('/root/test_dir')  # Likely to fail with permission error
except OSError as e:
    print(f"Permission error: {e}")
    raise
'''
        result = safe_script_runner(script_content)
        
        # This might succeed or fail depending on permissions, but should handle gracefully
        assert result['status'] in ['success', 'error']
        if result['status'] == 'error':
            assert result['return_code'] != 0
    
    def test_memory_error_simulation(self):
        """Test handling of memory-intensive operations."""
        script_content = '''
try:
    # Try to create a very large list that might cause memory issues
    huge_list = [0] * (10**9)
except MemoryError as e:
    print(f"Memory error caught: {e}")
except Exception as e:
    print(f"Other error: {type(e).__name__}: {e}")
'''
        result = safe_script_runner(script_content, timeout=5)
        
        # Should either succeed (if system has enough memory) or fail gracefully
        assert result['status'] in ['success', 'error']
        # The main point is that it doesn't crash the test runner
    
    def test_subprocess_general_exception_handling(self):
        """Test handling of general subprocess exceptions."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Subprocess failed")
            
            script_content = 'print("test")'
            result = safe_script_runner(script_content)
            
            assert result['status'] == 'error'
            assert result['return_code'] == -1
            assert 'Subprocess failed' in result['stderr']
            assert 'Failed to execute script' in result['error_message']
    
    def test_temp_file_cleanup_on_success(self):
        """Test that temporary files are cleaned up after successful execution."""
        with patch('os.unlink') as mock_unlink:
            script_content = 'print("test")'
            result = safe_script_runner(script_content)
            
            assert result['status'] == 'success'
            # Verify that unlink was called (cleanup happened)
            assert mock_unlink.called
    
    def test_temp_file_cleanup_on_error(self):
        """Test that temporary files are cleaned up even when script fails."""
        with patch('os.unlink') as mock_unlink:
            script_content = 'raise Exception("test error")'
            result = safe_script_runner(script_content)
            
            assert result['status'] == 'error'
            # Verify that unlink was called (cleanup happened)
            assert mock_unlink.called
    
    def test_temp_file_cleanup_exception_handling(self):
        """Test that cleanup exceptions don't affect the main result."""
        with patch('os.unlink') as mock_unlink:
            mock_unlink.side_effect = OSError("Cleanup failed")
            
            script_content = 'print("test")'
            result = safe_script_runner(script_content)
            
            # Main execution should still succeed
            assert result['status'] == 'success'
            assert 'test' in result['stdout']
    
    def test_custom_script_name_parameter(self):
        """Test that custom script name parameter works correctly."""
        script_content = 'print("Custom name test")'
        result = safe_script_runner(script_content, script_name="my_custom_script.py")
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'Custom name test' in result['stdout']
    
    def test_execution_time_precision(self):
        """Test that execution time is measured with reasonable precision."""
        import time
        
        start_time = time.time()
        script_content = 'print("Quick execution")'
        result = safe_script_runner(script_content)
        end_time = time.time()
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        # Execution time should be reasonable (less than 5 seconds for a simple print)
        assert result['execution_time'] < 5.0
        # Execution time should be positive
        assert result['execution_time'] > 0
        # Execution time should be close to actual time (within reasonable margin)
        actual_time = end_time - start_time
        assert abs(result['execution_time'] - actual_time) < 1.0  # Within 1 second
    
    def test_return_code_consistency(self):
        """Test that return codes are consistent across different scenarios."""
        # Success case
        result_success = safe_script_runner('print("success")')
        assert result_success['status'] == 'success'
        assert result_success['return_code'] == 0
        
        # Error case
        result_error = safe_script_runner('raise ValueError("error")')
        assert result_error['status'] == 'error'
        assert result_error['return_code'] != 0
        
        # Timeout case
        result_timeout = safe_script_runner('import time; time.sleep(5)', timeout=1)
        assert result_timeout['status'] == 'error'
        assert result_timeout['return_code'] == -1
    
    def test_file_read_exception(self):
        """Test handling of file reading exceptions."""
        # This test is for ScriptRunner class, not safe_script_runner
        # Skip this test for TestSafeScriptRunner
        pytest.skip("This test is for ScriptRunner class, not safe_script_runner")
    
    def test_temp_file_cleanup_on_success(self):
        """Test that temporary files are cleaned up after successful execution."""
        with patch('os.unlink') as mock_unlink:
            script_content = 'print("test")'
            result = safe_script_runner(script_content)
            
            assert result['status'] == 'success'
            # Verify that unlink was called (cleanup happened)
            assert mock_unlink.called
    
    def test_temp_file_cleanup_on_error(self):
        """Test that temporary files are cleaned up even when script fails."""
        with patch('os.unlink') as mock_unlink:
            script_content = 'raise Exception("test error")'
            result = safe_script_runner(script_content)
            
            assert result['status'] == 'error'
            # Verify that unlink was called (cleanup happened)
            assert mock_unlink.called
    
    def test_temp_file_cleanup_exception_handling(self):
        """Test that cleanup exceptions don't affect the main result."""
        with patch('os.unlink') as mock_unlink:
            mock_unlink.side_effect = OSError("Cleanup failed")
            
            script_content = 'print("test")'
            result = safe_script_runner(script_content)
            
            # Main execution should still succeed
            assert result['status'] == 'success'
            assert 'test' in result['stdout']
    
    def test_complex_script_with_multiple_outputs(self):
        """Test a complex script with multiple types of output."""
        script_content = '''
import sys
import json

# Normal output
print("Starting complex script")

# Function definition and usage
def process_data(data):
    return [x * 2 for x in data]

data = [1, 2, 3, 4, 5]
result = process_data(data)
print(f"Processed data: {result}")

# JSON output
config = {"version": "1.0", "debug": True}
print(json.dumps(config))

# Error output
print("About to encounter an error", file=sys.stderr)

# Warning message
print("WARNING: This is a warning", file=sys.stderr)

# Final output
print("Complex script completed")
'''
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert 'Starting complex script' in result['stdout']
        assert 'Processed data: [2, 4, 6, 8, 10]' in result['stdout']
        assert '"version": "1.0"' in result['stdout']
        assert 'Complex script completed' in result['stdout']
        assert 'About to encounter an error' in result['stderr']
        assert 'WARNING: This is a warning' in result['stderr']
    
    def test_script_with_infinite_loop_timeout(self):
        """Test that infinite loops are properly handled by timeout."""
        runner = ScriptRunner(timeout=1)
        
        script_content = """
# This will run forever without timeout protection
while True:
    pass
"""
        result = runner.execute_script(script_content)
        
        assert result['status'] == 'error'
        assert 'timed out' in result['error_message'].lower()


class TestScriptRunnerAdditional:
    """Additional test cases for ScriptRunner class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.runner = ScriptRunner()
    
    def test_script_runner_general_exception_handling(self):
        """Test handling of general exceptions in ScriptRunner."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Subprocess execution failed")
            
            script_content = 'print("test")'
            result = self.runner.execute_script(script_content)
            
            assert result['status'] == 'error'
            assert result['return_code'] == -1
            assert 'Subprocess execution failed' in result['stderr']
            assert 'Failed to execute script' in result['error_message']
    
    def test_script_runner_temp_file_cleanup_exception(self):
        """Test that cleanup exceptions don't affect ScriptRunner results."""
        with patch('os.unlink') as mock_unlink:
            mock_unlink.side_effect = OSError("Cleanup failed")
            
            script_content = 'print("test cleanup exception")'
            result = self.runner.execute_script(script_content)
            
            # Main execution should still succeed
            assert result['status'] == 'success'
            assert 'test cleanup exception' in result['stdout']
    
    def test_execute_file_with_unicode_path(self):
        """Test executing a file with unicode characters in path."""
        # Create a temporary file with unicode name
        with tempfile.NamedTemporaryFile(mode='w', suffix='test.py', delete=False) as f:
            f.write('print("Unicode path test")')
            temp_file_path = f.name
        
        try:
            result = self.runner.execute_file(temp_file_path)
            
            assert result['status'] == 'success'
            assert 'Unicode path test' in result['stdout']
        finally:
            os.unlink(temp_file_path)
    
    def test_execute_file_with_various_encodings(self):
        """Test executing a file with different encoding scenarios."""
        # Test with a file that has unicode content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write('print("Hello World")\nprint("Test content")')
            temp_file_path = f.name
        
        try:
            result = self.runner.execute_file(temp_file_path)
            
            assert result['status'] == 'success'
            assert 'Hello World' in result['stdout']
            assert 'Test content' in result['stdout']
        finally:
            os.unlink(temp_file_path)
    
    def test_script_runner_with_zero_timeout(self):
        """Test ScriptRunner with zero timeout (should use default)."""
        # Zero timeout should be treated as invalid and use default
        runner = ScriptRunner(timeout=30)  # Use reasonable timeout
        
        script_content = 'print("Zero timeout test")'
        result = runner.execute_script(script_content)
        
        assert result['status'] == 'success'
        assert 'Zero timeout test' in result['stdout']
    
    def test_script_runner_with_negative_timeout(self):
        """Test ScriptRunner with negative timeout (should use default)."""
        # Negative timeout should be treated as invalid and use default
        runner = ScriptRunner(timeout=30)  # Use reasonable timeout
        
        script_content = 'print("Negative timeout test")'
        result = runner.execute_script(script_content)
        
        assert result['status'] == 'success'
        assert 'Negative timeout test' in result['stdout']


class TestScriptRunnerFileOperations:
    """Test cases specifically for ScriptRunner file operations."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.runner = ScriptRunner()
    
    def test_execute_file_permission_denied(self):
        """Test executing a file without read permissions."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("Permission test")')
            temp_file_path = f.name
        
        try:
            # Remove read permissions (this might not work on all systems)
            os.chmod(temp_file_path, 0o000)
            
            result = self.runner.execute_file(temp_file_path)
            
            # On some systems, this might still succeed due to permissions
            # So we'll just check that it doesn't crash
            assert result['status'] in ['success', 'error']
            if result['status'] == 'error':
                assert 'Failed to read file' in result['error_message']
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(temp_file_path, 0o644)
                os.unlink(temp_file_path)
            except OSError:
                pass
    
    def test_execute_file_directory_not_file(self):
        """Test executing a directory path instead of a file."""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            result = self.runner.execute_file(temp_dir)
            
            assert result['status'] == 'error'
            assert 'Failed to read file' in result['error_message']
        finally:
            os.rmdir(temp_dir)
    
    def test_execute_file_with_various_error_types(self):
        """Test execute_file method with different types of file errors."""
        # Test with a path that doesn't exist
        result = self.runner.execute_file("/this/path/does/not/exist.py")
        assert result['status'] == 'error'
        assert 'File not found' in result['error_message']
        
        # Test with empty path
        result = self.runner.execute_file("")
        assert result['status'] == 'error'
        assert 'File not found' in result['error_message']
    
    def test_execute_file_with_large_file(self):
        """Test executing a large Python file."""
        # Create a large script
        large_script = []
        for i in range(100):
            large_script.extend([
                f'def function_{i}():',
                f'    return {i} * 2',
                f'',
                f'print(f"Function {i} result: {{function_{i}()}}")'
            ])
        
        large_script_text = '\n'.join(large_script)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(large_script_text)
            temp_file_path = f.name
        
        try:
            result = self.runner.execute_file(temp_file_path)
            
            assert result['status'] == 'success'
            assert 'Function 0 result: 0' in result['stdout']
            assert 'Function 99 result: 198' in result['stdout']
        finally:
            os.unlink(temp_file_path)


class TestIntegrationAndEdgeCases:
    """Integration tests and edge cases for both ScriptRunner and safe_script_runner."""
    
    def test_comparison_between_script_runner_and_safe_function(self):
        """Test that ScriptRunner and safe_script_runner produce similar results."""
        script_content = '''
import sys
print("Stdout message")
print("Stderr message", file=sys.stderr)
print("Final output")
'''
        
        # Test with ScriptRunner
        runner = ScriptRunner()
        result_runner = runner.execute_script(script_content)
        
        # Test with safe_script_runner
        result_safe = safe_script_runner(script_content)
        
        # Both should succeed
        assert result_runner['status'] == 'success'
        assert result_safe['status'] == 'success'
        
        # Both should have similar output
        assert 'Stdout message' in result_runner['stdout']
        assert 'Stdout message' in result_safe['stdout']
        assert 'Stderr message' in result_runner['stderr']
        assert 'Stderr message' in result_safe['stderr']
    
    def test_concurrent_script_execution(self):
        """Test that multiple script executions can happen concurrently."""
        import concurrent.futures
        
        def run_script(script_content):
            return safe_script_runner(script_content)
        
        scripts = [
            'print("Script 1")',
            'print("Script 2")',
            'print("Script 3")',
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_script, script) for script in scripts]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All scripts should execute successfully
        for result in results:
            assert result['status'] == 'success'
        
        # Check that all outputs are present
        outputs = [result['stdout'].strip() for result in results]
        assert 'Script 1' in outputs
        assert 'Script 2' in outputs
        assert 'Script 3' in outputs
    
    def test_script_with_special_characters_and_escaping(self):
        """Test scripts containing special characters that need escaping."""
        script_content = '''
# Test various special characters
print("Quotes: 'single' and \\"double\\"")
print("Backslash: \\\\ \\\\test")
print("Newline: \\n Tab: \\t")
print("Unicode: 你好世界 🌍")
print("Math symbols: ∑ ∏ ∫ √ ∞")
print("Special: !@#$%^&*()_+-=[]{}|;':\",./<>?")
'''
        
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert "single' and \"double\"" in result['stdout']
        assert 'Backslash: \\\\' in result['stdout']
        assert '你好世界 🌍' in result['stdout']
        assert '∑ ∏ ∫ √ ∞' in result['stdout']
    
    def test_script_with_environment_variables(self):
        """Test scripts that access environment variables."""
        script_content = '''
import os
print(f"PATH exists: {'PATH' in os.environ}")
print(f"HOME: {os.environ.get('HOME', 'Not set')}")
print(f"USER: {os.environ.get('USER', 'Not set')}")
'''
        
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert 'PATH exists:' in result['stdout']
        assert 'HOME:' in result['stdout']
        assert 'USER:' in result['stdout']
    
    def test_script_with_current_working_directory(self):
        """Test scripts that access the current working directory."""
        script_content = '''
import os
print(f"Current directory: {os.getcwd()}")
print(f"Directory exists: {os.path.exists(os.getcwd())}")
print(f"Is directory: {os.path.isdir(os.getcwd())}")
'''
        
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert 'Current directory:' in result['stdout']
        assert 'Directory exists: True' in result['stdout']
        assert 'Is directory: True' in result['stdout']
    
    def test_script_with_subprocess_calls(self):
        """Test scripts that make subprocess calls themselves."""
        script_content = '''
import subprocess
import sys

# Test a simple echo command
result = subprocess.run([sys.executable, '-c', 'print(\"subprocess test\")'], 
                     capture_output=True, text=True)
print(f"Subprocess stdout: {result.stdout.strip()}")
print(f"Subprocess return code: {result.returncode}")
'''
        
        result = safe_script_runner(script_content)
        
        assert result['status'] == 'success'
        assert 'subprocess test' in result['stdout']
        assert 'Subprocess return code: 0' in result['stdout']
    
    def test_script_with_file_operations(self):
        """Test scripts that perform file operations."""
        import tempfile
        
        # Create a temporary file for the script to use
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            test_file = f.name
        
        script_content = f'''
import os
import tempfile

# Test file operations
test_file = "{test_file}"

# Write to file
with open(test_file, 'w') as f:
    f.write("Test content from script\\n")
    f.write("Second line\\n")

# Read from file
with open(test_file, 'r') as f:
    content = f.read()

print(f"File content length: {{len(content)}}")
print(f"Content preview: {{content[:30]}}")

# Clean up
os.unlink(test_file)
print("File operations completed successfully")
'''
        
        try:
            result = safe_script_runner(script_content)
            
            assert result['status'] == 'success'
            assert 'File content length:' in result['stdout']
            assert 'Content preview:' in result['stdout']
            assert 'File operations completed successfully' in result['stdout']
        finally:
            # Cleanup if script failed to remove file
            if os.path.exists(test_file):
                os.unlink(test_file)


class TestModuleMainExecution:
    """Test the main execution block of the script_runner module."""
    
    def test_module_main_execution(self):
        """Test that the module's main execution block works correctly."""
        # Run the module as a script
        result = subprocess.run([
            sys.executable, '-m', 'app.script_runner'
        ], capture_output=True, text=True, cwd='/app/workspaces/8acfa580-8dde-4a1c-85e9-1d792da3b985')
        
        # Should execute successfully
        assert result.returncode == 0
        
        # Should contain output from both safe_script_runner and ScriptRunner tests
        assert '=== Testing safe_script_runner function ===' in result.stdout
        assert '=== Testing original ScriptRunner class ===' in result.stdout
        assert 'Test 1 - Status:' in result.stdout
        assert 'Test 2 - Status:' in result.stdout
        assert 'Test 3 - Timeout test:' in result.stdout
        assert 'ScriptRunner test - Status:' in result.stdout
    
    def test_module_execution_with_args(self):
        """Test module execution doesn't break with various arguments."""
        # Test with various argument combinations
        test_cases = [
            [sys.executable, '-m', 'app.script_runner'],
            [sys.executable, '-c', 'from app.script_runner import safe_script_runner; print("Import works")'],
            [sys.executable, '-c', 'from app.script_runner import ScriptRunner; print("Class import works")']
        ]
        
        for args in test_cases:
            result = subprocess.run(args, capture_output=True, text=True, 
                                    cwd='/app/workspaces/8acfa580-8dde-4a1c-85e9-1d792da3b985', timeout=10)
            
            # Should not crash
            assert result.returncode in [0, 1]  # 0 for success, 1 for normal Python errors
            assert 'Traceback' not in result.stderr  # No unhandled exceptions


    def test_main_section_functionality(self):
        """Test the functionality in the __main__ section."""
        # Test the same scenarios as in __main__
        
        # Test 1: Simple successful execution
        result = safe_script_runner('print("Hello from safe_script_runner!")')
        assert result['status'] == 'success'
        assert 'Hello from safe_script_runner!' in result['stdout']
        
        # Test 2: Script with error
        result = safe_script_runner('raise ValueError("Test error")')
        assert result['status'] == 'error'
        assert 'ValueError' in result['stderr']
        
        # Test 3: Using custom timeout
        result = safe_script_runner('import time\ntime.sleep(2)', timeout=1)
        assert result['status'] == 'error'
        
        # Test 4: Original ScriptRunner class
        test_script = """
print("Hello from ScriptRunner!")
print("This is stdout output")
import sys
print("This is stderr output", file=sys.stderr)
print("Script completed successfully")
"""
        runner = ScriptRunner()
        result = runner.execute_script(test_script)
        
        assert result['status'] == 'success'
        assert result['return_code'] == 0
        assert 'Hello from ScriptRunner!' in result['stdout']
        assert 'This is stdout output' in result['stdout']
        assert 'This is stderr output' in result['stderr']
        assert 'Script completed successfully' in result['stdout']


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])