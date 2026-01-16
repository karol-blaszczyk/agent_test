"""
Pytest configuration and fixtures for Flask application testing.

This module provides test fixtures and configuration for testing the Flask web application.
It includes test client setup, database fixtures, and testing utilities.
"""

import pytest
import tempfile
import os
from app import app as flask_app


@pytest.fixture
def app():
    """
    Create and configure a test Flask application instance.
    
    Returns:
        Flask app instance configured for testing with a temporary database
    """
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure the app for testing
    flask_app.config.update({
        'TESTING': True,  # Enable testing mode
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'DEBUG': False,  # Disable debug mode for tests
    })
    
    yield flask_app
    
    # Cleanup after test
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """
    Create a test client for the Flask application.
    
    Args:
        app: The Flask application fixture
        
    Returns:
        Flask test client instance for making HTTP requests
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Create a test runner for the Flask application.
    
    Args:
        app: The Flask application fixture
        
    Returns:
        Flask test runner instance for CLI commands
    """
    return app.test_cli_runner()


@pytest.fixture
def sample_script_content():
    """
    Provide sample Python script content for testing.
    
    Returns:
        str: Sample Python script content
    """
    return '''#!/usr/bin/env python3
"""
Sample test script for testing Flask endpoints.
"""

def main():
    print("Hello from test script!")
    print("This is a test output.")
    return 0

if __name__ == "__main__":
    main()
'''


@pytest.fixture
def mock_workspace_dir(tmp_path):
    """
    Create a temporary workspace directory for testing.
    
    Returns:
        Path: Temporary directory path
    """
    return tmp_path


class TestConfig:
    """
    Test configuration constants.
    """
    # Test timeout values (in seconds)
    SCRIPT_TIMEOUT = 5
    API_TIMEOUT = 10
    
    # Test script names
    VALID_SCRIPTS = ['hello_world', 'verify_hello_world']
    INVALID_SCRIPT = 'nonexistent_script'
    
    # Expected responses
    SUCCESS_STATUS = 'healthy'
    ERROR_STATUS = 'error'


@pytest.fixture
def test_config():
    """
    Provide test configuration constants.
    
    Returns:
        TestConfig: Test configuration instance
    """
    return TestConfig()


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """
    Automatically set up test environment for all tests.
    
    This fixture is automatically used by all tests to ensure consistent
    test environment setup.
    """
    # Set environment variables for testing
    monkeypatch.setenv('FLASK_ENV', 'testing')
    monkeypatch.setenv('FLASK_DEBUG', '0')
    
    yield


def pytest_configure(config):
    """
    Configure pytest with custom markers and settings.
    
    Args:
        config: Pytest configuration object
    """
    # Add custom markers
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add default markers.
    
    Args:
        config: Pytest configuration object
        items: List of test items
    """
    for item in items:
        # Add unit marker if no marker is specified
        if not any(marker.name in ['integration', 'unit', 'slow'] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)