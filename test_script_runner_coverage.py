#!/usr/bin/env python3
"""
Test script to improve coverage for script_runner.py
"""

import sys
import os
sys.path.append('/app/workspaces/8acfa580-8dde-4a1c-85e9-1d792da3b985')

from app.script_runner import safe_script_runner, ScriptRunner

def test_safe_script_runner():
    """Test the safe_script_runner function."""
    print('=== Testing safe_script_runner function ===')
    
    # Test 1: Simple successful execution
    result = safe_script_runner('print("Hello from safe_script_runner!")')
    print(f"Test 1 - Status: {result['status']}, Output: {result['stdout'].strip()}")
    assert result['status'] == 'success'
    
    # Test 2: Script with error
    result = safe_script_runner('raise ValueError("Test error")')
    print(f"Test 2 - Status: {result['status']}, Error: {'ValueError' in result['stderr']}")
    assert result['status'] == 'error'
    assert 'ValueError' in result['stderr']
    
    # Test 3: Using custom timeout
    result = safe_script_runner('import time\ntime.sleep(2)', timeout=1)
    print(f"Test 3 - Timeout test: {result['status']}")
    assert result['status'] == 'error'
    assert 'timed out' in result['error_message']
    
    print('All safe_script_runner tests passed!')

def test_script_runner_class():
    """Test the ScriptRunner class."""
    print('\n=== Testing ScriptRunner class ===')
    
    # Create a test script
    test_script = '''print("Hello from ScriptRunner!")
print("This is stdout output")
import sys
print("This is stderr output", file=sys.stderr)
print("Script completed successfully")'''
    
    # Create a runner and execute the test script
    runner = ScriptRunner()
    result = runner.execute_script(test_script)
    
    print(f"ScriptRunner test - Status: {result['status']}")
    print(f"Return code: {result['return_code']}")
    print(f"Stdout: {result['stdout']}")
    print(f"Stderr: {result['stderr']}")
    
    assert result['status'] == 'success'
    assert result['return_code'] == 0
    assert 'Hello from ScriptRunner!' in result['stdout']
    
    # Test timeout with ScriptRunner
    runner_timeout = ScriptRunner(timeout=1)
    result_timeout = runner_timeout.execute_script('import time\ntime.sleep(2)')
    assert result_timeout['status'] == 'error'
    assert 'timed out' in result_timeout['error_message']
    
    # Test execute_file method
    # Create a temporary script file
    with open('temp_test_script.py', 'w') as f:
        f.write('print("File execution test")')
    
    result_file = runner.execute_file('temp_test_script.py')
    assert result_file['status'] == 'success'
    assert 'File execution test' in result_file['stdout']
    
    # Test execute_file with non-existent file
    result_missing = runner.execute_file('nonexistent_script.py')
    assert result_missing['status'] == 'error'
    assert 'File not found' in result_missing['error_message']
    
    # Clean up
    try:
        os.unlink('temp_test_script.py')
    except OSError:
        pass
    
    print('All ScriptRunner tests passed!')

if __name__ == '__main__':
    test_safe_script_runner()
    test_script_runner_class()
    print('\n=== All tests completed successfully! ===')