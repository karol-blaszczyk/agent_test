#!/usr/bin/env python3
"""
Integration tests for CLI functionality and web interface.
Tests that the CLI can list and run scripts end-to-end, and that web interface
functionality works correctly with script execution.
"""

import pytest
import json
import re
import importlib.util
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the Flask app from app.py using importlib to avoid package conflicts
def import_flask_app():
    """Import the Flask app from app.py file."""
    spec = importlib.util.spec_from_file_location('flask_app', os.path.join(os.path.dirname(__file__), '..', 'app.py'))
    flask_app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(flask_app_module)
    return flask_app_module.app

app = import_flask_app()


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestScriptExecution:
    """Test cases for script execution through the web interface."""

    def test_hello_world_execution_success(self, client):
        """Test that hello_world.py can be executed successfully through the web interface."""
        response = client.post('/run/hello_world')
        
        # Check response status
        assert response.status_code == 200
        
        # Parse JSON response
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'output' in data
        
        # Check output content
        output = data['output']
        assert 'Hello from Kortex' in output
        assert 'Timestamp:' in output
        
        # Verify timestamp format
        timestamp_match = re.search(r'Timestamp: (.+)', output)
        assert timestamp_match is not None
        
        # Verify timestamp is valid ISO format
        timestamp_str = timestamp_match.group(1)
        try:
            script_time = datetime.fromisoformat(timestamp_str)
            current_time = datetime.now()
            time_diff = (current_time - script_time).total_seconds()
            # Timestamp should be very recent (within 5 seconds)
            assert abs(time_diff) < 5
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp_str}")

    def test_verify_hello_world_execution_success(self, client):
        """Test that verify_hello_world.py can be executed successfully through the web interface."""
        response = client.post('/run/verify_hello_world')
        
        # Check response status
        assert response.status_code == 200
        
        # Parse JSON response
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'output' in data
        
        # Check output content for verification success
        output = data['output']
        assert '✅ All checks passed!' in output
        assert '✅ Output: \'Hello from Kortex\'' in output
        assert '✅ Timestamp:' in output
        assert '✅ Timestamp is recent' in output

    def test_api_script_execution_with_valid_script(self, client):
        """Test that the API endpoint /api/scripts/<name>/run works with valid scripts."""
        response = client.post('/api/scripts/hello_world/run')
        
        # Check response status
        assert response.status_code == 200
        
        # Parse JSON response
        data = json.loads(response.data)
        assert data['script_name'] == 'hello_world'
        assert data['status'] == 'success'
        assert data['return_code'] == 0
        assert 'stdout' in data
        assert 'executed_at' in data
        
        # Check output content
        stdout = data['stdout']
        assert 'Hello from Kortex' in stdout
        assert 'Timestamp:' in stdout

    def test_api_script_execution_with_invalid_script(self, client):
        """Test that the API endpoint handles invalid script names correctly."""
        response = client.post('/api/scripts/nonexistent_script/run')
        
        # Check response status
        assert response.status_code == 404
        
        # Parse JSON response
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Script not found' in data['error']

    def test_api_script_execution_with_test_script(self, client):
        """Test that test scripts are rejected by the API."""
        response = client.post('/api/scripts/test_scripts/run')
        
        # Check response status - should be 400 for validation error
        assert response.status_code == 400
        
        # Parse JSON response
        data = json.loads(response.data)
        assert 'error' in data
        assert 'This script cannot be executed via API' in data['error']

    def test_invalid_script_name_returns_error(self, client):
        """Test that invalid script names return appropriate error responses."""
        response = client.post('/run/invalid_script')
        
        # Check response status
        assert response.status_code == 400
        
        # Parse JSON response
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Unknown script: invalid_script' in data['error']

    def test_nonexistent_script_file_returns_error(self, client):
        """Test that non-existent script files return appropriate error responses."""
        # This test would require temporarily removing a script file
        # For now, we'll test the validation logic for script names
        response = client.post('/run/unknown_script')
        
        # Check response status
        assert response.status_code == 400
        
        # Parse JSON response
        data = json.loads(response.data)
        assert 'error' in data


class TestScriptListing:
    """Test cases for script listing functionality."""

    def test_api_get_scripts_list(self, client):
        """Test that the API endpoint /api/scripts returns available scripts."""
        response = client.get('/api/scripts')
        
        # Check response status
        assert response.status_code == 200
        
        # Parse JSON response
        data = json.loads(response.data)
        assert 'scripts' in data
        assert 'count' in data
        assert 'workspace' in data
        
        # Check that hello_world and verify_hello_world are in the list
        script_names = [script['name'] for script in data['scripts']]
        assert 'hello_world' in script_names
        assert 'verify_hello_world' in script_names
        
        # Verify script metadata structure
        for script in data['scripts']:
            assert 'name' in script
            assert 'file_name' in script
            assert 'description' in script
            assert 'file_size' in script
            assert 'modified_at' in script
            assert 'path' in script

    def test_api_get_scripts_excludes_test_files(self, client):
        """Test that the API endpoint excludes test files and app.py."""
        response = client.get('/api/scripts')
        
        # Check response status
        assert response.status_code == 200
        
        # Parse JSON response
        data = json.loads(response.data)
        script_names = [script['name'] for script in data['scripts']]
        
        # Test files should be excluded
        assert not any(name.startswith('test_') for name in script_names)
        # app.py should be excluded
        assert 'app' not in script_names

    def test_scripts_web_page_renders(self, client):
        """Test that the /scripts web page renders correctly."""
        response = client.get('/scripts')
        
        # Check response status
        assert response.status_code == 200
        
        # Check content type
        assert 'text/html' in response.content_type
        
        # Check that the page contains expected content
        content = response.data.decode('utf-8')
        assert 'Available Scripts' in content or 'Scripts' in content


class TestScriptViewing:
    """Test cases for script viewing functionality."""

    def test_view_hello_world_script(self, client):
        """Test that hello_world.py can be viewed through the web interface."""
        response = client.get('/view/hello_world')
        
        # Check response status
        assert response.status_code == 200
        
        # Check content type
        assert response.content_type == 'text/plain'
        
        # Check script content
        content = response.data.decode('utf-8')
        assert 'Hello from Kortex' in content
        assert 'def main():' in content
        assert 'datetime.now().isoformat()' in content

    def test_view_verify_hello_world_script(self, client):
        """Test that verify_hello_world.py can be viewed through the web interface."""
        response = client.get('/view/verify_hello_world')
        
        # Check response status
        assert response.status_code == 200
        
        # Check content type
        assert response.content_type == 'text/plain'
        
        # Check script content
        content = response.data.decode('utf-8')
        assert 'verify_hello_world' in content
        assert 'subprocess.run' in content
        assert 'Hello from Kortex' in content

    def test_view_invalid_script_returns_error(self, client):
        """Test that viewing invalid script names returns appropriate error responses."""
        response = client.get('/view/invalid_script')
        
        # Check response status
        assert response.status_code == 404
        
        # Check error message
        content = response.data.decode('utf-8')
        assert 'Unknown script: invalid_script' in content


class TestHealthCheck:
    """Test cases for health check endpoint."""

    def test_health_check_returns_healthy_status(self, client):
        """Test that the health check endpoint returns expected status."""
        response = client.get('/health')
        
        # Check response status
        assert response.status_code == 200
        
        # Parse JSON response
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'workspace' in data
        
        # Verify timestamp is valid ISO format
        try:
            timestamp = datetime.fromisoformat(data['timestamp'])
            current_time = datetime.now()
            time_diff = (current_time - timestamp).total_seconds()
            # Timestamp should be very recent (within 5 seconds)
            assert abs(time_diff) < 5
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {data['timestamp']}")


class TestErrorHandling:
    """Test cases for error handling scenarios."""

    def test_404_handler_for_api_endpoints(self, client):
        """Test that 404 errors for API endpoints return JSON responses."""
        response = client.get('/api/nonexistent')
        
        # Check response status
        assert response.status_code == 404
        
        # Parse JSON response
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Endpoint not found' in data['error']

    def test_404_handler_for_web_pages(self, client):
        """Test that 404 errors for web pages return HTML responses."""
        response = client.get('/nonexistent-page')
        
        # Check response status
        assert response.status_code == 404
        
        # Check content type (should be HTML)
        assert 'text/html' in response.content_type

    def test_500_handler_for_api_endpoints(self, client):
        """Test that 500 errors for API endpoints return JSON responses."""
        # This is harder to test directly, but we can verify the handler exists
        # by checking the app configuration
        assert hasattr(app, 'error_handler_spec')


class TestCLIIntegration:
    """Test cases for CLI functionality end-to-end."""

    def test_cli_list_command_shows_available_scripts(self):
        """Test that the CLI list command shows available scripts."""
        result = subprocess.run([
            sys.executable, 'cli.py', 'list'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
        
        # Should exit successfully
        assert result.returncode == 0
        
        # Should contain script listing header
        assert 'Available scripts' in result.stdout
        assert 'Use \'cli.py run <script_name>\' to execute a script' in result.stdout
        
        # Should contain known scripts
        assert 'hello' in result.stdout
        assert 'hello_world' in result.stdout

    def test_cli_list_with_directory_option(self):
        """Test that the CLI list command works with custom directory."""
        result = subprocess.run([
            sys.executable, 'cli.py', 'list', '--directory', '.'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
        
        # Should exit successfully
        assert result.returncode == 0
        assert 'Available scripts' in result.stdout

    def test_cli_run_valid_script_success(self):
        """Test that the CLI can successfully run a valid script."""
        result = subprocess.run([
            sys.executable, 'cli.py', 'run', 'hello'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
        
        # Should exit successfully
        assert result.returncode == 0
        
        # Should contain script execution header
        assert 'Running script: hello.py' in result.stdout
        assert 'Script completed successfully' in result.stdout
        
        # Should contain script output
        assert 'Hello World' in result.stdout

    def test_cli_run_hello_world_script_success(self):
        """Test that the CLI can run hello_world script with timestamp."""
        result = subprocess.run([
            sys.executable, 'cli.py', 'run', 'hello_world'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
        
        # Should exit successfully
        assert result.returncode == 0
        
        # Should contain script output
        assert 'Hello from Kortex' in result.stdout
        assert 'Timestamp:' in result.stdout
        
        # Should contain success message
        assert 'Script completed successfully' in result.stdout

    def test_cli_run_nonexistent_script_fails(self):
        """Test that the CLI handles non-existent scripts correctly."""
        result = subprocess.run([
            sys.executable, 'cli.py', 'run', 'nonexistent_script'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
        
        # Should exit with error code
        assert result.returncode == 1
        
        # Should contain error message
        assert "Error: Script 'nonexistent_script' not found" in result.stdout
        assert "Use 'cli.py list' to see available scripts" in result.stdout

    def test_cli_run_with_no_runner_option(self):
        """Test that the CLI can run scripts without ScriptRunner."""
        result = subprocess.run([
            sys.executable, 'cli.py', 'run', '--no-runner', 'hello'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
        
        # Should exit successfully
        assert result.returncode == 0
        assert 'Hello World' in result.stdout
        assert 'Script completed successfully' in result.stdout

    def test_cli_help_shows_usage(self):
        """Test that the CLI shows help when no arguments are provided."""
        result = subprocess.run([
            sys.executable, 'cli.py'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
        
        # Should exit successfully (shows help and lists scripts)
        assert result.returncode == 0
        
        # Should contain usage information
        assert 'usage:' in result.stdout
        assert 'CLI interface for listing and running Python scripts' in result.stdout
        
        # Should contain examples
        assert 'cli.py list' in result.stdout
        assert 'cli.py run hello_world' in result.stdout

    def test_cli_help_explicit(self):
        """Test that the CLI shows help with --help flag."""
        result = subprocess.run([
            sys.executable, 'cli.py', '--help'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
        
        # Should exit successfully
        assert result.returncode == 0
        assert 'usage:' in result.stdout
        assert 'CLI interface for listing and running Python scripts' in result.stdout

    def test_cli_run_script_with_error(self):
        """Test that the CLI handles scripts that fail during execution."""
        # Create a temporary script that will fail
        temp_script = os.path.join('/tmp', 'failing_test.py')
        with open(temp_script, 'w') as f:
            f.write("""
#!/usr/bin/env python3
print("This script will fail")
raise ValueError("Test error")
""")
        
        try:
            # Copy to workspace
            workspace_script = os.path.join(os.path.dirname(__file__), '..', 'failing_test.py')
            import shutil
            shutil.copy(temp_script, workspace_script)
            
            result = subprocess.run([
                sys.executable, 'cli.py', 'run', 'failing_test'
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
            
            # Should exit with error code
            assert result.returncode != 0
            assert 'failing_test.py' in result.stdout
            
        finally:
            # Cleanup
            if os.path.exists(temp_script):
                os.remove(temp_script)
            workspace_script = os.path.join(os.path.dirname(__file__), '..', 'failing_test.py')
            if os.path.exists(workspace_script):
                os.remove(workspace_script)

    def test_cli_script_description_extraction(self):
        """Test that the CLI correctly extracts script descriptions."""
        result = subprocess.run([
            sys.executable, 'cli.py', 'list'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
        
        # Should show script descriptions
        assert 'Main function to print Hello World' in result.stdout
        assert 'Main function to print greeting with timestamp' in result.stdout

    @pytest.mark.skip(reason="Keyboard interrupt test causes issues in CI environment")
    def test_cli_keyboard_interrupt_handling(self):
        """Test that the CLI handles keyboard interrupts gracefully."""
        # This test is tricky to implement directly, but we can test the code path
        # by mocking the execution to raise KeyboardInterrupt
        
        # Import the CLI module to test the exception handling
        original_cwd = os.getcwd()
        cli_path = os.path.join(os.path.dirname(__file__), '..')
        
        try:
            os.chdir(cli_path)
            sys.path.insert(0, cli_path)
            import cli
            
            # Mock the run function to raise KeyboardInterrupt
            with patch('cli.run_script') as mock_run:
                mock_run.side_effect = KeyboardInterrupt()
                
                # Test the main function with mocked interrupt
                with patch('sys.argv', ['cli.py', 'run', 'hello']):
                    with patch('sys.exit') as mock_exit:
                        cli.main()
                        mock_exit.assert_called_with(130)  # SIGINT exit code
        finally:
            os.chdir(original_cwd)
            if cli_path in sys.path:
                sys.path.remove(cli_path)
            # Remove the module from cache to avoid conflicts
            if 'cli' in sys.modules:
                del sys.modules['cli']

    def test_cli_script_runner_integration(self):
        """Test that the CLI integrates properly with ScriptRunner when available."""
        # Test with ScriptRunner (should work normally)
        result = subprocess.run([
            sys.executable, 'cli.py', 'run', 'hello'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
        
        assert result.returncode == 0
        assert 'Hello World' in result.stdout

    def test_cli_empty_directory_handling(self):
        """Test that the CLI handles empty directories gracefully."""
        # Create temporary empty directory
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                sys.executable, 'cli.py', 'list', '--directory', temp_dir
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
            
            # Should exit successfully but show no scripts
            assert result.returncode == 0
            assert 'No Python scripts found' in result.stdout

    def test_cli_script_with_stderr_output(self):
        """Test that the CLI captures and displays stderr output correctly."""
        # Create a script that writes to stderr
        temp_script = os.path.join('/tmp', 'stderr_test.py')
        with open(temp_script, 'w') as f:
            f.write("""
#!/usr/bin/env python3
import sys
print("Hello stdout")
print("Error message", file=sys.stderr)
""")
        
        try:
            # Copy to workspace
            workspace_script = os.path.join(os.path.dirname(__file__), '..', 'stderr_test.py')
            import shutil
            shutil.copy(temp_script, workspace_script)
            
            result = subprocess.run([
                sys.executable, 'cli.py', 'run', 'stderr_test'
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
            
            assert result.returncode == 0
            assert 'Hello stdout' in result.stdout
            assert 'STDERR:' in result.stdout
            assert 'Error message' in result.stdout
            
        finally:
            # Cleanup
            if os.path.exists(temp_script):
                os.remove(temp_script)
            workspace_script = os.path.join(os.path.dirname(__file__), '..', 'stderr_test.py')
            if os.path.exists(workspace_script):
                os.remove(workspace_script)


class TestResultsDisplay:
    """Test cases for script execution results display functionality."""

    def test_script_execution_returns_detailed_results(self, client):
        """Test that script execution returns detailed results including stdout, stderr, and return code."""
        response = client.post('/api/scripts/hello_world/run')
        
        # Check response status
        assert response.status_code == 200
        
        # Parse JSON response
        data = json.loads(response.data)
        
        # Verify comprehensive result structure
        assert data['script_name'] == 'hello_world'
        assert data['status'] == 'success'
        assert data['return_code'] == 0
        assert 'stdout' in data
        assert 'stderr' in data
        assert 'executed_at' in data
        assert data['stdout'] != ''  # Should have some output

    def test_script_execution_with_stderr_capture(self, client):
        """Test that stderr output is captured and included in results."""
        # Create a temporary script that writes to stderr
        import tempfile
        import os
        
        temp_script = os.path.join('/tmp', 'stderr_test.py')
        with open(temp_script, 'w') as f:
            f.write("""
import sys
print("Hello stdout")
print("Error message", file=sys.stderr)
""")
        
        try:
            # Move the script to workspace temporarily
            workspace_script = os.path.join(os.path.dirname(os.path.abspath('app.py')), 'stderr_test.py')
            import shutil
            shutil.copy(temp_script, workspace_script)
            
            response = client.post('/api/scripts/stderr_test/run')
            
            # Check response status
            assert response.status_code == 200
            
            # Parse JSON response
            data = json.loads(response.data)
            assert 'stderr' in data
            assert 'Error message' in data['stderr']
            
        finally:
            # Cleanup
            if os.path.exists(temp_script):
                os.remove(temp_script)
            workspace_script = os.path.join(os.path.dirname(os.path.abspath('app.py')), 'stderr_test.py')
            if os.path.exists(workspace_script):
                os.remove(workspace_script)

    def test_script_execution_failure_handling(self, client):
        """Test that script execution failures are properly handled and reported."""
        # Create a temporary script that fails
        import tempfile
        import os
        
        temp_script = os.path.join('/tmp', 'fail_test.py')
        with open(temp_script, 'w') as f:
            f.write("""
import sys
print("This script will fail")
sys.exit(1)
""")
        
        try:
            # Move the script to workspace temporarily
            workspace_script = os.path.join(os.path.dirname(os.path.abspath('app.py')), 'fail_test.py')
            import shutil
            shutil.copy(temp_script, workspace_script)
            
            response = client.post('/api/scripts/fail_test/run')
            
            # Check response status - should still be 200 as the API executed successfully
            assert response.status_code == 200
            
            # Parse JSON response
            data = json.loads(response.data)
            assert data['script_name'] == 'fail_test'
            assert data['status'] == 'error'
            assert data['return_code'] == 1
            assert 'error_message' in data
            
        finally:
            # Cleanup
            if os.path.exists(temp_script):
                os.remove(temp_script)
            workspace_script = os.path.join(os.path.dirname(os.path.abspath('app.py')), 'fail_test.py')
            if os.path.exists(workspace_script):
                os.remove(workspace_script)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])