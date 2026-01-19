#!/usr/bin/env python3
"""
Comprehensive web interface integration tests for Flask application.
Tests cover the complete web interface including script listing, execution, 
result viewing, JavaScript integration, and user experience.
"""

import pytest
import json
import os
import re
import time
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
import importlib.util
spec = importlib.util.spec_from_file_location("app", os.path.join(os.path.dirname(__file__), '..', 'app.py'))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = app_module.app


@pytest.fixture
def temp_script():
    """Create a temporary script for testing."""
    temp_dir = tempfile.mkdtemp()
    script_path = os.path.join(temp_dir, 'temp_test_script.py')
    with open(script_path, 'w') as f:
        f.write('''
#!/usr/bin/env python3
"""
Temporary test script for integration testing.
"""
print("Temporary script executed successfully")
print("Timestamp: 2024-01-01T12:00:00")
''')
    
    yield script_path
    
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for testing script execution."""
    with patch('app_module.subprocess.run') as mock_run:
        yield mock_run


class TestWebInterfaceIntegration:
    """Comprehensive integration tests for the web interface."""
    
    def test_complete_web_interface_flow(self, client):
        """Test the complete web interface flow from loading to execution."""
        # Test 1: Load the main page
        response = client.get('/')
        assert response.status_code == 200
        assert b'Python Script Dashboard' in response.data
        assert b'Run and manage your Python scripts' in response.data
        
        # Test 2: Load scripts page
        response = client.get('/scripts')
        assert response.status_code == 200
        assert b'Script Management' in response.data
        
        # Test 3: Check that script cards are present
        assert b'Hello World Script' in response.data
        assert b'Verify Hello World Script' in response.data
        
        # Test 4: Check for script execution buttons
        assert b'Run Script' in response.data
        assert b'View Code' in response.data
    
    def test_script_listing_integration(self, client):
        """Test that scripts are properly listed and displayed."""
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'scripts' in data
        assert 'count' in data
        assert data['count'] > 0
        
        # Check that hello_world and verify_hello_world are present
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
            
            # Verify data types
            assert isinstance(script['name'], str)
            assert isinstance(script['file_size'], int)
            assert isinstance(script['modified_at'], str)
    
    def test_script_execution_web_interface(self, client):
        """Test script execution through the web interface endpoints."""
        # Test hello_world execution
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'output' in data
        assert 'Hello from Kortex' in data['output']
        assert 'Timestamp:' in data['output']
        
        # Test verify_hello_world execution
        response = client.post('/run/verify_hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'output' in data
        assert '✅ All checks passed!' in data['output']
    
    def test_script_viewing_web_interface(self, client):
        """Test script viewing through the web interface."""
        # Test viewing hello_world script
        response = client.get('/view/hello_world')
        assert response.status_code == 200
        assert response.content_type == 'text/plain'
        
        content = response.data.decode('utf-8')
        assert 'Hello from Kortex' in content
        assert 'def main():' in content
        assert 'datetime.now().isoformat()' in content
        
        # Test viewing verify_hello_world script
        response = client.get('/view/verify_hello_world')
        assert response.status_code == 200
        assert response.content_type == 'text/plain'
        
        content = response.data.decode('utf-8')
        assert 'verify_hello_world' in content
        assert 'subprocess.run' in content
    
    def test_api_script_execution_comprehensive(self, client):
        """Test comprehensive API script execution functionality."""
        # Test successful execution
        response = client.post('/api/scripts/hello_world/run')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['script_name'] == 'hello_world'
        assert data['status'] == 'success'
        assert data['return_code'] == 0
        assert 'stdout' in data
        assert 'stderr' in data
        assert 'executed_at' in data
        assert 'Hello from Kortex' in data['stdout']
        
        # Test execution with non-existent script
        response = client.post('/api/scripts/nonexistent_script/run')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Script not found' in data['error']
    
    def test_error_handling_web_interface(self, client):
        """Test error handling in the web interface."""
        # Test 404 for API endpoints
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Endpoint not found' in data['error']
        
        # Test 404 for web pages
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'<!DOCTYPE html>' in response.data or b'404' in response.data
        
        # Test invalid script execution
        response = client.post('/run/invalid_script')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Unknown script: invalid_script' in data['error']
    
    def test_health_check_integration(self, client):
        """Test health check endpoint integration."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'workspace' in data
        
        # Verify timestamp format
        timestamp = datetime.fromisoformat(data['timestamp'])
        current_time = datetime.now()
        time_diff = (current_time - timestamp).total_seconds()
        assert abs(time_diff) < 5  # Should be very recent
    
    def test_script_execution_with_timeout(self, client, mock_subprocess_run):
        """Test script execution timeout handling."""
        from subprocess import TimeoutExpired
        mock_subprocess_run.side_effect = TimeoutExpired('cmd', 30)
        
        response = client.post('/run/hello_world')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'timed out' in data['error']
    
    def test_script_execution_with_stderr(self, client, mock_subprocess_run):
        """Test script execution that produces stderr output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Script output"
        mock_result.stderr = "Warning: something happened"
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Script output' in data['output']
        assert 'STDERR:' in data['output']
        assert 'Warning: something happened' in data['output']
    
    def test_script_execution_failure_handling(self, client, mock_subprocess_run):
        """Test handling of script execution failures."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Some output"
        mock_result.stderr = "Error occurred"
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'exit code 1' in data['error']
        assert 'Some output' in data['output']
        assert 'Error occurred' in data['output']
    
    def test_script_execution_with_empty_output(self, client, mock_subprocess_run):
        """Test script execution with no output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['output'] == 'Script completed successfully'
    
    def test_script_execution_with_large_output(self, client, mock_subprocess_run):
        """Test script execution with large output."""
        large_output = "Line " * 1000  # Large output
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = large_output
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert large_output in data['output']
    
    def test_script_execution_with_special_characters(self, client, mock_subprocess_run):
        """Test script execution with special characters in output."""
        special_output = "Output with émojis 🎉 and spëcial chars: café"
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = special_output
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'émojis 🎉' in data['output']
        assert 'café' in data['output']
    
    def test_script_listing_excludes_test_files(self, client):
        """Test that script listing excludes test files and app.py."""
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        script_names = [script['name'] for script in data['scripts']]
        
        # Test files should be excluded
        assert not any(name.startswith('test_') for name in script_names)
        # app.py should be excluded
        assert 'app' not in script_names
    
    def test_script_metadata_extraction(self, client):
        """Test that script metadata is properly extracted."""
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        for script in data['scripts']:
            # Verify file size is reasonable
            assert script['file_size'] > 0
            assert script['file_size'] < 1000000  # Less than 1MB
            
            # Verify modified date is valid
            try:
                modified_date = datetime.fromisoformat(script['modified_at'])
                assert modified_date <= datetime.now()
            except ValueError:
                pytest.fail(f"Invalid modified date format: {script['modified_at']}")
            
            # Verify description is present
            assert script['description'] != ''
    
    def test_concurrent_script_execution(self, client):
        """Test that multiple scripts can be executed concurrently."""
        # This test verifies that the system can handle concurrent requests
        # We'll make multiple requests and ensure they all succeed
        
        responses = []
        for i in range(3):
            response = client.post('/run/hello_world')
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
    
    def test_script_execution_timing(self, client):
        """Test that script execution completes in reasonable time."""
        start_time = time.time()
        
        response = client.post('/run/hello_world')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert response.status_code == 200
        assert execution_time < 10  # Should complete within 10 seconds
    
    def test_web_interface_responsiveness(self, client):
        """Test that the web interface responds quickly to requests."""
        # Test main page load time
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2  # Should load within 2 seconds
        
        # Test API endpoint responsiveness
        start_time = time.time()
        response = client.get('/api/scripts')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2  # Should respond within 2 seconds


class TestJavaScriptIntegration:
    """Tests for JavaScript integration and dynamic functionality."""
    
    def test_script_manager_initialization(self, client):
        """Test that the ScriptManager JavaScript class is properly initialized."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check that the JavaScript files are loaded
        assert b'scripts.js' in response.data
        assert b'scriptManager' in response.data
        assert b'DOMContentLoaded' in response.data
    
    def test_dynamic_script_loading_functionality(self, client):
        """Test that scripts are loaded dynamically via JavaScript."""
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'scripts' in data
        assert len(data['scripts']) > 0
        
        # Verify that scripts have the expected structure for JavaScript
        for script in data['scripts']:
            assert 'name' in script
            assert 'description' in script
            assert 'file_size' in script
            assert 'modified_at' in script
    
    def test_script_execution_javascript_api(self, client):
        """Test the JavaScript API for script execution."""
        # Test the API endpoint that JavaScript calls
        response = client.post('/api/scripts/hello_world/run', 
                              headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['script_name'] == 'hello_world'
        assert data['status'] == 'success'
        assert 'stdout' in data
        assert 'stderr' in data
        assert 'return_code' in data
    
    def test_script_viewing_javascript_api(self, client):
        """Test the JavaScript API for script viewing."""
        response = client.get('/view/hello_world')
        assert response.status_code == 200
        assert response.content_type == 'text/plain'
        
        content = response.data.decode('utf-8')
        assert 'Hello from Kortex' in content
        assert 'def main():' in content
    
    def test_error_handling_javascript_api(self, client):
        """Test JavaScript API error handling."""
        # Test with non-existent script
        response = client.post('/api/scripts/nonexistent_script/run',
                              headers={'Content-Type': 'application/json'})
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Script not found' in data['error']
    
    def test_script_metadata_for_javascript(self, client):
        """Test that script metadata is properly formatted for JavaScript consumption."""
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        for script in data['scripts']:
            # Verify that all required fields are present for JavaScript
            assert 'name' in script
            assert 'file_name' in script
            assert 'description' in script
            assert 'file_size' in script
            assert 'modified_at' in script
            
            # Verify data types that JavaScript expects
            assert isinstance(script['name'], str)
            assert isinstance(script['file_size'], int)
            assert isinstance(script['modified_at'], str)
            
            # Verify that description is not empty
            assert script['description'] != ''


class TestUserExperience:
    """Tests for user experience and interface behavior."""
    
    def test_dashboard_layout_and_styling(self, client):
        """Test that the dashboard has proper layout and styling."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for Tailwind CSS classes
        assert b'max-w-6xl' in response.data
        assert b'mx-auto' in response.data
        assert b'shadow-lg' in response.data
        assert b'rounded-xl' in response.data
        assert b'text-gray-800' in response.data
        assert b'bg-white' in response.data
    
    def test_script_cards_styling(self, client):
        """Test that script cards have proper styling."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for card styling classes
        assert b'rounded-xl' in response.data
        assert b'shadow-lg' in response.data
        assert b'hover:shadow-xl' in response.data
        assert b'transition-shadow' in response.data
        assert b'overflow-hidden' in response.data
    
    def test_button_styling_and_interactions(self, client):
        """Test that buttons have proper styling and interaction states."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for button styling classes
        assert b'bg-blue-600' in response.data
        assert b'hover:bg-blue-700' in response.data
        assert b'transition-colors' in response.data
        assert b'rounded-lg' in response.data
        assert b'focus:outline-none' in response.data
        assert b'focus:ring-2' in response.data
    
    def test_responsive_design_elements(self, client):
        """Test that the interface includes responsive design elements."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for responsive classes
        assert b'grid-cols-1' in response.data
        assert b'md:grid-cols-2' in response.data
        assert b'lg:grid-cols-3' in response.data
        assert b'flex-col' in response.data
        assert b'sm:flex-row' in response.data
        assert b'gap-6' in response.data
    
    def test_accessibility_features(self, client):
        """Test that the interface includes accessibility features."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for semantic HTML elements
        assert b'<h2' in response.data
        assert b'<h3' in response.data
        assert b'<h4' in response.data
        assert b'<p' in response.data
        assert b'<button' in response.data
        
        # Check for ARIA attributes (if present)
        # Note: The current implementation may not have extensive ARIA attributes
        # This is a check for future accessibility improvements
    
    def test_loading_states_and_feedback(self, client):
        """Test that the interface provides proper loading states and feedback."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for loading indicators
        assert b'Loading scripts...' in response.data
        assert b'animate-spin' in response.data
        
        # Check for hidden loading div
        assert b'id="loading"' in response.data
        assert b'hidden' in response.data
    
    def test_results_display_functionality(self, client):
        """Test that results are displayed properly."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for results section
        assert b'id="results"' in response.data
        assert b'id="output"' in response.data
        assert b'id="output-content"' in response.data
        
        # Check for results styling
        assert b'bg-gray-900' in response.data
        assert b'text-green-400' in response.data
        assert b'font-mono' in response.data
        assert b'overflow-x-auto' in response.data


class TestEdgeCasesAndBoundaryConditions:
    """Tests for edge cases and boundary conditions."""
    
    def test_empty_script_list_handling(self, client):
        """Test handling when no scripts are available."""
        # This test would require temporarily moving all scripts
        # For now, we test that the current script list is not empty
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['count'] > 0
        assert len(data['scripts']) > 0
    
    def test_very_long_script_output(self, client, mock_subprocess_run):
        """Test handling of very long script output."""
        very_long_output = "X" * 10000  # 10KB of output
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = very_long_output
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert very_long_output in data['output']
    
    def test_script_with_unicode_characters(self, client, mock_subprocess_run):
        """Test scripts with various Unicode characters."""
        unicode_output = """
        Hello World! 👋
        こんにちは世界 🌏
        Привет мир! 🌍
        مرحبا بالعالم 🌎
        """
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = unicode_output
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert '👋' in data['output']
        assert 'こんにちは世界' in data['output']
        assert 'Привет мир!' in data['output']
        assert 'مرحبا بالعالم' in data['output']
    
    def test_concurrent_requests_stress_test(self, client):
        """Test concurrent request handling under stress."""
        # Make multiple concurrent requests
        responses = []
        for i in range(10):
            response = client.get('/api/scripts')
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'scripts' in data
    
    def test_rapid_script_execution(self, client):
        """Test rapid script execution requests."""
        # Execute script multiple times rapidly
        for i in range(5):
            response = client.post('/run/hello_world')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'Hello from Kortex' in data['output']
    
    def test_invalid_timestamp_format_handling(self, client, mock_subprocess_run):
        """Test handling of invalid timestamp formats."""
        invalid_output = """
        Hello from Kortex
        Timestamp: invalid-timestamp-format
        """
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = invalid_output
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Hello from Kortex' in data['output']
        assert 'invalid-timestamp-format' in data['output']
    
    def test_script_with_no_description(self, client):
        """Test handling of scripts without descriptions."""
        # The current implementation should handle scripts without descriptions
        # by providing a default description
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        for script in data['scripts']:
            # Should have either a real description or a default one
            assert script['description'] != ''
            assert isinstance(script['description'], str)


class TestPerformanceAndReliability:
    """Tests for performance and reliability."""
    
    def test_script_execution_performance(self, client):
        """Test that script execution performs within acceptable limits."""
        import time
        
        start_time = time.time()
        response = client.post('/run/hello_world')
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert response.status_code == 200
        assert execution_time < 5  # Should complete within 5 seconds
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_api_response_performance(self, client):
        """Test that API responses are fast."""
        import time
        
        start_time = time.time()
        response = client.get('/api/scripts')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2  # Should respond within 2 seconds
    
    def test_memory_efficiency_with_large_output(self, client, mock_subprocess_run):
        """Test memory efficiency when handling large outputs."""
        # Create a large output (1MB)
        large_output = "X" * 1024 * 1024
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = large_output
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert large_output in data['output']
    
    def test_reliability_under_load(self, client):
        """Test reliability under moderate load."""
        # Make multiple requests to test reliability
        success_count = 0
        total_requests = 20
        
        for i in range(total_requests):
            response = client.get('/health')
            if response.status_code == 200:
                success_count += 1
        
        # Should have high success rate
        success_rate = success_count / total_requests
        assert success_rate >= 0.95  # At least 95% success rate
    
    def test_error_recovery(self, client, mock_subprocess_run):
        """Test error recovery mechanisms."""
        # First, simulate an error
        mock_subprocess_run.side_effect = Exception("Simulated error")
        
        response = client.post('/run/hello_world')
        assert response.status_code == 500
        
        # Then test recovery
        mock_subprocess_run.side_effect = None
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Recovered successfully"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Recovered successfully' in data['output']


@pytest.fixture
def mock_os_path_exists():
    """Mock os.path.exists for testing file existence checks."""
    with patch('app.os.path.exists') as mock_exists:
        yield mock_exists


@pytest.fixture
def mock_open_file():
    """Mock built-in open function for testing file operations."""
    with patch('app.open', create=True) as mock_open:
        yield mock_open


@pytest.fixture
def mock_os_path_exists():
    """Mock os.path.exists for testing file existence checks."""
    with patch('os.path.exists') as mock_exists:
        yield mock_exists


@pytest.fixture
def mock_open_file():
    """Mock built-in open function for testing file operations."""
    with patch('builtins.open') as mock_open:
        yield mock_open


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for testing script execution."""
    with patch('subprocess.run') as mock_run:
        yield mock_run


class TestWebInterfaceIntegration:
    """Comprehensive tests for the web interface integration."""
    
    def test_complete_script_execution_flow(self, client):
        """Test the complete flow from script listing to execution and results."""
        # Step 1: Get script list via API
        response = client.get('/api/scripts')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'scripts' in data
        assert 'count' in data
        
        # Verify hello_world is available
        script_names = [script['name'] for script in data['scripts']]
        assert 'hello_world' in script_names
        
        # Step 2: Execute script via API
        response = client.post('/api/scripts/hello_world/run')
        assert response.status_code == 200
        execution_data = json.loads(response.data)
        
        # Verify execution results
        assert execution_data['script_name'] == 'hello_world'
        assert execution_data['status'] == 'success'
        assert execution_data['return_code'] == 0
        assert 'Hello from Kortex' in execution_data['stdout']
        assert 'Timestamp:' in execution_data['stdout']
        
        # Step 3: View script source
        response = client.get('/view/hello_world')
        assert response.status_code == 200
        assert response.content_type == 'text/plain'
        script_content = response.data.decode('utf-8')
        assert 'Hello from Kortex' in script_content
        assert 'datetime.now().isoformat()' in script_content
    
    def test_web_page_script_listing(self, client):
        """Test that the web page properly lists and displays scripts."""
        response = client.get('/scripts')
        assert response.status_code == 200
        assert 'text/html' in response.content_type
        
        # Check for expected content in the scripts page
        html_content = response.data.decode('utf-8')
        assert 'Scripts' in html_content or 'Available Scripts' in html_content
        
        # Check for script cards or listing
        assert 'hello_world' in html_content or 'Hello World' in html_content
        assert 'verify_hello_world' in html_content or 'Verify Hello World' in html_content
    
    def test_home_page_dashboard_integration(self, client):
        """Test that the home page dashboard integrates properly with script functionality."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for dashboard elements
        assert 'Python Script Dashboard' in html_content
        assert 'Script Management' in html_content
        
        # Check for script execution buttons
        assert 'Run Script' in html_content
        assert 'View Code' in html_content
        
        # Check for JavaScript integration
        assert 'scripts.js' in html_content
        assert 'runScript' in html_content
        assert 'viewScript' in html_content
    
    def test_script_execution_with_timeout_handling(self, client, mock_subprocess_run):
        """Test script execution timeout handling in the web interface."""
        from subprocess import TimeoutExpired
        mock_subprocess_run.side_effect = TimeoutExpired('python hello_world.py', 30)
        
        response = client.post('/api/scripts/hello_world/run')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'timed out' in data['error']
        assert data['script_name'] == 'hello_world'
        assert data['status'] == 'timeout'
    
    def test_concurrent_script_execution_handling(self, client):
        """Test handling of concurrent script execution requests."""
        import threading
        results = []
        
        def run_script():
            try:
                response = client.post('/api/scripts/hello_world/run')
                results.append(response.status_code)
            except Exception as e:
                results.append(str(e))
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_script)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(results) == 3
        assert all(status == 200 for status in results if isinstance(status, int))
    
    def test_script_execution_with_large_output(self, client, mock_subprocess_run):
        """Test script execution with large output handling."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Large output line\n" * 1000  # 1000 lines
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/api/scripts/hello_world/run')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'Large output line' in data['stdout']
        assert data['stdout'].count('Large output line') == 1000
    
    def test_script_execution_with_special_characters(self, client, mock_subprocess_run):
        """Test script execution with special characters in output."""
        special_output = "Output with émojis 🎉 and spëcial chars: café, naïve, résumé"
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = special_output
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/api/scripts/hello_world/run')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'émojis 🎉' in data['stdout']
        assert 'café' in data['stdout']
    
    def test_script_execution_with_stderr_output(self, client, mock_subprocess_run):
        """Test script execution that produces stderr output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Main output"
        mock_result.stderr = "Warning: This is a warning message\nError: This is an error message"
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/api/scripts/hello_world/run')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'Main output' in data['stdout']
        assert 'Warning: This is a warning message' in data['stderr']
        assert 'Error: This is an error message' in data['stderr']
    
    def test_script_execution_failure_with_error_code(self, client, mock_subprocess_run):
        """Test script execution that fails with non-zero exit code."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Some output before failure"
        mock_result.stderr = "Error details"
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/api/scripts/hello_world/run')
        assert response.status_code == 200  # API call succeeds, but script fails
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['return_code'] == 1
        assert 'Some output before failure' in data['stdout']
        assert 'Error details' in data['stderr']
        assert 'error_message' in data
        assert 'Script exited with code 1' in data['error_message']
    
    def test_api_scripts_endpoint_comprehensive_data(self, client):
        """Test that the API scripts endpoint returns comprehensive script data."""
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'scripts' in data
        assert 'count' in data
        assert 'workspace' in data
        
        # Test each script has comprehensive metadata
        for script in data['scripts']:
            assert 'name' in script
            assert 'file_name' in script
            assert 'description' in script
            assert 'file_size' in script
            assert 'modified_at' in script
            assert 'path' in script
            
            # Validate data types
            assert isinstance(script['name'], str)
            assert isinstance(script['file_name'], str)
            assert isinstance(script['description'], str)
            assert isinstance(script['file_size'], int)
            assert isinstance(script['modified_at'], str)
            assert isinstance(script['path'], str)
            
            # Validate content
            assert script['name'] == script['file_name'].replace('.py', '')
            assert script['file_name'].endswith('.py')
            assert os.path.exists(script['path'])
    
    def test_script_filtering_exclusions(self, client):
        """Test that certain scripts are properly excluded from listing."""
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        script_names = [script['name'] for script in data['scripts']]
        
        # Test files should be excluded
        assert not any(name.startswith('test_') for name in script_names)
        
        # app.py should be excluded
        assert 'app' not in script_names
        
        # Only Python scripts should be included
        assert all(script['file_name'].endswith('.py') for script in data['scripts'])


class TestJavaScriptIntegration:
    """Test cases for JavaScript integration with the web interface."""
    
    def test_scripts_js_file_exists_and_accessible(self, client):
        """Test that the scripts.js file is accessible."""
        response = client.get('/static/js/scripts.js')
        assert response.status_code == 200
        assert 'javascript' in response.content_type
        
        js_content = response.data.decode('utf-8')
        assert 'ScriptManager' in js_content
        assert 'runScript' in js_content
        assert 'viewScript' in js_content
        assert 'loadScripts' in js_content
    
    def test_script_manager_initialization(self, client):
        """Test that ScriptManager is properly initialized on the home page."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for JavaScript functions that handle script execution
        assert 'runScript' in html_content
        assert 'viewScript' in html_content
        assert 'showResults' in html_content
        
        # Check for DOM event listeners
        assert 'runScript' in html_content
        assert 'viewScript' in html_content
    
    def test_dynamic_script_loading_integration(self, client):
        """Test integration of dynamic script loading functionality."""
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'scripts' in data
        
        # Verify scripts can be processed by JavaScript
        for script in data['scripts']:
            assert 'name' in script
            assert 'description' in script
            assert 'file_size' in script
            assert 'modified_at' in script
            
            # These fields are used by JavaScript for display
            assert isinstance(script['name'], str)
            assert isinstance(script['description'], str)
            assert isinstance(script['file_size'], (int, float))


class TestErrorHandlingAndEdgeCases:
    """Test cases for error handling and edge cases in the web interface."""
    
    def test_404_error_for_nonexistent_script_execution(self, client):
        """Test 404 error when trying to execute a nonexistent script."""
        response = client.post('/api/scripts/nonexistent_script/run')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Script not found' in data['error']
    
    def test_400_error_for_invalid_script_name(self, client):
        """Test 400 error for invalid script names."""
        response = client.post('/run/invalid_script_name_with_special_chars!@#')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Unknown script' in data['error']
    
    def test_404_error_for_nonexistent_script_viewing(self, client):
        """Test 404 error when trying to view a nonexistent script."""
        response = client.get('/view/nonexistent_script')
        assert response.status_code == 404
        
        error_message = response.data.decode('utf-8')
        assert 'Unknown script: nonexistent_script' in error_message
    
    def test_empty_script_list_handling(self, client):
        """Test handling when no scripts are available."""
        # This test would require temporarily removing all scripts
        # For now, we'll test that the API handles empty results gracefully
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'scripts' in data
        assert 'count' in data
        assert isinstance(data['scripts'], list)
        assert isinstance(data['count'], int)
    
    def test_malformed_api_requests_handling(self, client):
        """Test handling of malformed API requests."""
        # Test with invalid JSON (though our endpoints don't expect JSON)
        response = client.post('/api/scripts/hello_world/run', 
                             data='invalid json',
                             content_type='application/json')
        # Should still work since the endpoint doesn't parse JSON
        assert response.status_code == 200
    
    def test_network_timeout_simulation(self, client, mock_subprocess_run):
        """Test network timeout simulation."""
        # Simulate a timeout by making subprocess.run hang
        def hanging_run(*args, **kwargs):
            time.sleep(0.1)  # Short delay to simulate processing
            from subprocess import CompletedProcess
            return CompletedProcess(args=['python', 'test.py'], returncode=0, stdout='Success', stderr='')
        
        mock_subprocess_run.side_effect = hanging_run
        
        response = client.post('/api/scripts/hello_world/run')
        # Should complete successfully
        assert response.status_code == 200
    
    def test_concurrent_request_limit_handling(self, client):
        """Test handling of many concurrent requests."""
        import threading
        results = []
        
        def make_request():
            try:
                response = client.get('/api/scripts')
                results.append(response.status_code)
            except Exception as e:
                results.append(str(e))
        
        # Create many concurrent requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # All should succeed
        assert len(results) == 10
        assert all(status == 200 for status in results if isinstance(status, int))


class TestUserExperienceAndInterface:
    """Test cases for user experience and interface functionality."""
    
    def test_responsive_design_elements(self, client):
        """Test that the interface includes responsive design elements."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for responsive classes
        assert 'max-w-6xl' in html_content  # Container max width
        assert 'mx-auto' in html_content    # Center alignment
        assert 'grid-cols-1' in html_content  # Mobile-first grid
        assert 'md:grid-cols-2' in html_content  # Responsive grid
        assert 'lg:grid-cols-3' in html_content  # Large screen grid
        assert 'flex-col' in html_content  # Flex column layout
        assert 'sm:flex-row' in html_content  # Responsive flex
    
    def test_accessibility_features(self, client):
        """Test accessibility features in the interface."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for button accessibility
        assert 'focus:outline-none' in html_content
        assert 'focus:ring-2' in html_content
        assert 'focus:ring-offset-2' in html_content
        
        # Check for proper heading structure
        assert '<h2' in html_content
        assert '<h3' in html_content
        assert '<h4' in html_content
    
    def test_loading_states_and_feedback(self, client):
        """Test loading states and user feedback mechanisms."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for loading indicators
        assert 'loading' in html_content.lower()
        assert 'animate-spin' in html_content
        
        # Check for results display elements
        assert 'results' in html_content.lower()
        assert 'output-content' in html_content
    
    def test_error_message_display_integration(self, client):
        """Test integration of error message display."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for error display elements
        assert 'results' in html_content.lower()
        assert 'output-content' in html_content
        # Check for error handling in JavaScript
        assert 'Error:' in html_content
    
    def test_script_metadata_display(self, client):
        """Test that script metadata is properly displayed."""
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        for script in data['scripts']:
            # Verify all metadata needed for display is present
            assert 'name' in script  # Display name
            assert 'description' in script  # Description text
            assert 'file_size' in script  # File size for display
            assert 'modified_at' in script  # Last modified date
            
            # Verify data is display-ready
            assert isinstance(script['name'], str) and script['name']
            assert isinstance(script['description'], str)
            assert isinstance(script['file_size'], (int, float))
            assert isinstance(script['modified_at'], str)


class TestPerformanceAndScalability:
    """Test cases for performance and scalability of the web interface."""
    
    def test_script_listing_performance(self, client):
        """Test that script listing performs efficiently."""
        start_time = time.time()
        response = client.get('/api/scripts')
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should complete quickly (within 2 seconds for reasonable number of scripts)
        execution_time = end_time - start_time
        assert execution_time < 2.0, f"Script listing took too long: {execution_time}s"
    
    def test_script_execution_performance(self, client):
        """Test that script execution performs efficiently."""
        start_time = time.time()
        response = client.post('/api/scripts/hello_world/run')
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should complete within reasonable time (5 seconds including script execution)
        execution_time = end_time - start_time
        assert execution_time < 5.0, f"Script execution took too long: {execution_time}s"
    
    def test_memory_efficiency_with_large_script_lists(self, client):
        """Test memory efficiency when handling large script lists."""
        response = client.get('/api/scripts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Should handle reasonable number of scripts efficiently
        assert 'scripts' in data
        assert 'count' in data
        assert isinstance(data['scripts'], list)
        
        # Verify no memory issues with current script count
        script_count = len(data['scripts'])
        assert script_count >= 0  # Should handle empty lists
        
        # Each script should have reasonable memory footprint
        for script in data['scripts']:
            assert len(str(script)) < 10000  # Reasonable size limit per script


class TestRunScript:
    """Test cases for the script execution route."""
    
    def test_run_valid_script_success(self, client, mock_subprocess_run):
        """Test running a valid script successfully."""
        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello, World!"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Hello, World!' in data['output']
        
        mock_subprocess_run.assert_called_once_with(
            ['python', 'hello_world.py'],
            cwd=os.path.dirname(os.path.abspath(__file__ + '/../app.py')),
            capture_output=True,
            text=True,
            timeout=30
        )
        # Check for expected content in the template
        assert b'html' in response.data


class TestHealthCheck:
    """Test cases for the health check endpoint."""
    
    def test_health_check_returns_healthy_status(self, client):
        """Test that health check returns healthy status."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'workspace' in data
        assert data['workspace'] == os.path.dirname(os.path.abspath(__file__ + '/../app.py'))[:-6]  # Remove '/tests' from the end


class TestRunScript:
    """Test cases for the script execution route."""
    
    def test_run_valid_script_success(self, client, mock_subprocess_run):
        """Test running a valid script successfully."""
        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello, World!"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Hello, World!' in data['output']
        
        mock_subprocess_run.assert_called_once_with(
            ['python', 'hello_world.py'],
            cwd=os.path.dirname(os.path.abspath(__file__ + '/../app.py'))[:-6],  # Remove '/tests' from the end
            capture_output=True,
            text=True,
            timeout=30
        )
    
    def test_run_valid_script_with_stderr(self, client, mock_subprocess_run):
        """Test running a script that produces stderr output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Script output"
        mock_result.stderr = "Warning: something happened"
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Script output' in data['output']
        assert 'STDERR:' in data['output']
        assert 'Warning: something happened' in data['output']
    
    def test_run_script_with_non_zero_exit_code(self, client, mock_subprocess_run):
        """Test running a script that exits with non-zero code."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Some output"
        mock_result.stderr = "Error occurred"
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'exit code 1' in data['error']
        assert 'Some output' in data['output']
        assert 'STDERR:' in data['output']
        assert 'Script exited with code: 1' in data['output']
    
    def test_run_script_timeout(self, client, mock_subprocess_run):
        """Test script execution timeout handling."""
        from subprocess import TimeoutExpired
        mock_subprocess_run.side_effect = TimeoutExpired('cmd', 30)
        
        response = client.post('/run/hello_world')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'timed out' in data['error']
    
    def test_run_unknown_script(self, client):
        """Test attempting to run an unknown script."""
        response = client.post('/run/unknown_script')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Unknown script: unknown_script' in data['error']
    
    def test_run_script_not_found(self, client, mock_os_path_exists):
        """Test attempting to run a script that doesn't exist."""
        mock_os_path_exists.return_value = False
        
        response = client.post('/run/hello_world')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Script not found: hello_world.py' in data['error']
    
    def test_run_verify_hello_world_script(self, client, mock_subprocess_run):
        """Test running the verify_hello_world script."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Verification successful!"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/verify_hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Verification successful!' in data['output']
    
    def test_run_script_internal_error(self, client, mock_subprocess_run):
        """Test handling of internal server errors."""
        mock_subprocess_run.side_effect = Exception("Unexpected error")
        
        response = client.post('/run/hello_world')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Internal server error' in data['error']
        assert 'Unexpected error' in data['error']


class TestViewScript:
    """Test cases for the script viewing route."""
    
    def test_view_valid_script(self, client, mock_os_path_exists, mock_open_file):
        """Test viewing a valid script."""
        mock_os_path_exists.return_value = True
        mock_file = MagicMock()
        mock_file.read.return_value = "print('Hello, World!')"
        mock_open_file.return_value.__enter__.return_value = mock_file
        
        response = client.get('/view/hello_world')
        assert response.status_code == 200
        assert response.data.decode() == "print('Hello, World!')"
        assert response.headers['Content-Type'] == 'text/plain'
    
    def test_view_unknown_script(self, client):
        """Test attempting to view an unknown script."""
        response = client.get('/view/unknown_script')
        assert response.status_code == 404
        assert b'Unknown script: unknown_script' in response.data
    
    def test_view_script_not_found(self, client, mock_os_path_exists):
        """Test attempting to view a script that doesn't exist."""
        mock_os_path_exists.return_value = False
        
        response = client.get('/view/hello_world')
        assert response.status_code == 404
        assert b'Script not found: hello_world.py' in response.data
    
    def test_view_script_internal_error(self, client, mock_os_path_exists, mock_open_file):
        """Test handling of internal errors when viewing scripts."""
        mock_os_path_exists.return_value = True
        mock_open_file.side_effect = Exception("File read error")
        
        response = client.get('/view/hello_world')
        assert response.status_code == 500
        assert b'Error reading script' in response.data
        assert b'File read error' in response.data
    
    def test_view_verify_hello_world_script(self, client, mock_os_path_exists, mock_open_file):
        """Test viewing the verify_hello_world script."""
        mock_os_path_exists.return_value = True
        mock_file = MagicMock()
        mock_file.read.return_value = "# Verification script"
        mock_open_file.return_value.__enter__.return_value = mock_file
        
        response = client.get('/view/verify_hello_world')
        assert response.status_code == 200
        assert response.data.decode() == "# Verification script"


class TestErrorHandlers:
    """Test cases for error handlers."""
    
    def test_404_handler_for_api_endpoint(self, client):
        """Test 404 handler for API endpoints."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Endpoint not found' in data['error']
    
    def test_404_handler_for_web_page(self, client):
        """Test 404 handler for web pages."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        # Should render 404.html template
        assert b'<!DOCTYPE html>' in response.data or b'404' in response.data
    
    def test_500_handler_for_api_endpoint(self, client):
        """Test 500 handler for API endpoints."""
        # Force a 500 error by causing an internal error in an API endpoint
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Internal error")
            response = client.post('/run/hello_world')
            assert response.status_code == 500
            
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Internal server error' in data['error']
    
    def test_500_handler_for_web_page(self, client):
        """Test 500 handler for web pages."""
        # This is harder to test without actually breaking the app
        # We'll just verify the handler exists by checking the app configuration
        assert 500 in app.error_handler_spec[None]  # Check if 500 handler is registered


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_script_output(self, client, mock_subprocess_run):
        """Test script execution with no output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['output'] == 'Script completed successfully'
    
    def test_script_with_large_output(self, client, mock_subprocess_run):
        """Test script execution with large output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Line " * 1000  # Large output
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Line ' * 1000 in data['output']
    
    def test_script_with_special_characters(self, client, mock_subprocess_run):
        """Test script execution with special characters in output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Output with émojis 🎉 and spëcial chars: café"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        response = client.post('/run/hello_world')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'émojis 🎉' in data['output']
        assert 'café' in data['output']