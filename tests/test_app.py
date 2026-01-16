#!/usr/bin/env python3
"""
Unit tests for Flask application routes.
Tests cover home page, script execution routes, and error handling.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for testing script execution."""
    with patch('app.subprocess.run') as mock_run:
        yield mock_run


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


class TestHomePage:
    """Test cases for the home page route."""
    
    def test_index_route_renders_template(self, client):
        """Test that the index route renders the correct template."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
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
        assert data['workspace'] == os.path.dirname(os.path.abspath(__file__ + '/../app.py'))


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
        # Force a 500 error by mocking an internal error
        with patch('app.jsonify') as mock_jsonify:
            mock_jsonify.side_effect = Exception("Internal error")
            response = client.get('/health')
            assert response.status_code == 500
    
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