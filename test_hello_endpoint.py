#!/usr/bin/env python3
"""
Test for Flask hello world endpoint.
Verifies that the /hello endpoint returns the expected HTML content and status code.
"""

import pytest
import sys
import os
import importlib.util

# Import the Flask app from app.py using importlib to avoid package conflicts
spec = importlib.util.spec_from_file_location("flask_app", "app.py")
flask_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flask_app)


class TestHelloEndpoint:
    """Test class for the /hello endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        flask_app.app.config['TESTING'] = True
        with flask_app.app.test_client() as client:
            yield client
    
    def test_hello_endpoint_status_code(self, client):
        """Test that the /hello endpoint returns a 200 status code."""
        response = client.get('/hello')
        assert response.status_code == 200
    
    def test_hello_endpoint_content_type(self, client):
        """Test that the /hello endpoint returns HTML content."""
        response = client.get('/hello')
        assert 'text/html' in response.content_type
    
    def test_hello_endpoint_contains_hello_world(self, client):
        """Test that the /hello endpoint contains 'Hello World' in the response."""
        response = client.get('/hello')
        assert b'Hello World' in response.data
    
    def test_hello_endpoint_contains_welcome_message(self, client):
        """Test that the /hello endpoint contains the welcome message."""
        response = client.get('/hello')
        assert b'Welcome to Flask with Tailwind CSS' in response.data
    
    def test_hello_endpoint_has_back_to_home_link(self, client):
        """Test that the /hello endpoint has a link back to home."""
        response = client.get('/hello')
        assert b'href="/"' in response.data
        assert b'Back to Home' in response.data
    
    def test_hello_endpoint_has_scripts_link(self, client):
        """Test that the /hello endpoint has a link to scripts."""
        response = client.get('/hello')
        assert b'href="/scripts"' in response.data
        assert b'View Scripts' in response.data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])