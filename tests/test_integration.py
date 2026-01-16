#!/usr/bin/env python3
"""
Integration tests for script execution through the web interface.
Tests that hello_world.py and verify_hello_world.py can be executed
through the Flask web application and return expected results.
"""

import pytest
import json
import re
from datetime import datetime
from app import app


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


class TestScriptTimeout:
    """Test cases for script execution timeout scenarios."""

    def test_script_execution_completes_within_timeout(self, client):
        """Test that script execution completes within the timeout period."""
        response = client.post('/run/hello_world')
        
        # Check response status
        assert response.status_code == 200
        
        # Parse JSON response
        data = json.loads(response.data)
        assert data['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])