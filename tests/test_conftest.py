"""
Basic test to verify the conftest.py fixtures work correctly.
"""

import pytest


def test_app_fixture(app):
    """Test that the app fixture creates a valid Flask application."""
    assert app is not None
    assert app.config['TESTING'] is True
    assert app.config['SECRET_KEY'] == 'test-secret-key'
    assert app.config['WTF_CSRF_ENABLED'] is False


def test_client_fixture(client):
    """Test that the client fixture creates a valid test client."""
    assert client is not None
    # Test that client can make requests
    response = client.get('/health')
    assert response.status_code == 200


def test_runner_fixture(runner):
    """Test that the runner fixture creates a valid test runner."""
    assert runner is not None


def test_sample_script_content(sample_script_content):
    """Test that the sample script content fixture works."""
    assert sample_script_content is not None
    assert 'Hello from test script!' in sample_script_content
    assert 'def main():' in sample_script_content


def test_mock_workspace_dir(mock_workspace_dir):
    """Test that the mock workspace directory fixture works."""
    assert mock_workspace_dir is not None
    assert mock_workspace_dir.exists()


def test_test_config(test_config):
    """Test that the test configuration fixture works."""
    assert test_config is not None
    assert test_config.SCRIPT_TIMEOUT == 5
    assert test_config.API_TIMEOUT == 10
    assert 'hello_world' in test_config.VALID_SCRIPTS


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'workspace' in data


def test_404_handler(client):
    """Test the 404 error handler."""
    response = client.get('/nonexistent')
    assert response.status_code == 404


def test_index_endpoint(client):
    """Test the index endpoint."""
    response = client.get('/')
    assert response.status_code == 200


class TestConftestFixtures:
    """Test class to verify all conftest fixtures work properly."""
    
    def test_app_in_test_mode(self, app):
        """Verify app is configured for testing."""
        assert app.config['TESTING'] is True
        assert app.config['DEBUG'] is False
    
    def test_client_can_access_routes(self, client):
        """Verify client can access application routes."""
        # Test health endpoint
        response = client.get('/health')
        assert response.status_code == 200
        
        # Test index endpoint
        response = client.get('/')
        assert response.status_code == 200
    
    def test_test_environment_setup(self, setup_test_environment):
        """Verify test environment is properly set up."""
        # This test automatically uses the setup_test_environment fixture
        # which sets up environment variables for testing
        import os
        assert os.environ.get('FLASK_ENV') == 'testing'
        assert os.environ.get('FLASK_DEBUG') == '0'