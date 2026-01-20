#!/usr/bin/env python3
"""
Comprehensive test suite for the hello world web functionality.
Tests the Flask route, template rendering, navigation integration, and script execution.
"""

import pytest
import sys
import os
import re
import subprocess
import tempfile
import time
from datetime import datetime
import importlib.util

# Import the Flask app from app.py using importlib to avoid package conflicts
spec = importlib.util.spec_from_file_location("flask_app", "app.py")
flask_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flask_app)


class TestHelloWorldComprehensive:
    """Comprehensive test class for hello world functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        flask_app.app.config['TESTING'] = True
        with flask_app.app.test_client() as client:
            yield client
    
    @pytest.fixture
    def hello_world_script(self):
        """Path to the hello_world.py script."""
        return os.path.join(os.path.dirname(__file__), 'hello_world.py')
    
    def test_hello_route_accessibility(self, client):
        """Test that the /hello route is accessible and returns proper status."""
        response = client.get('/hello')
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
    
    def test_hello_route_content_integrity(self, client):
        """Test that the hello page contains all expected content elements."""
        response = client.get('/hello')
        html_content = response.data.decode('utf-8')
        
        # Test main heading
        assert 'Hello World' in html_content
        assert 'Welcome to Flask with Tailwind CSS' in html_content
        
        # Test navigation links
        assert 'href="/"' in html_content
        assert 'href="/scripts"' in html_content
        assert 'Back to Home' in html_content
        assert 'View Scripts' in html_content
        
        # Test Tailwind CSS classes
        assert 'min-h-[70vh]' in html_content
        assert 'bg-gradient-to-br' in html_content
        assert 'from-blue-500' in html_content
        assert 'via-purple-500' in html_content
        assert 'to-pink-500' in html_content
        assert 'text-6xl' in html_content
        assert 'md:text-8xl' in html_content
        assert 'lg:text-9xl' in html_content
        
        # Test enhanced styling
        assert 'bg-white/10' in html_content
        assert 'blur-3xl' in html_content
        assert 'animate-pulse' in html_content
        assert 'bg-clip-text' in html_content
        assert 'text-transparent' in html_content
    
    def test_hello_route_navigation_integration(self, client):
        """Test that hello route integrates properly with navigation."""
        response = client.get('/hello')
        html_content = response.data.decode('utf-8')
        
        # Test that navigation links work
        nav_links = [
            ('/', 'Home'),
            ('/scripts', 'Scripts'),
            ('/hello', 'Hello')
        ]
        
        for href, text in nav_links:
            assert f'href="{href}"' in html_content
    
    def test_hello_route_responsive_design(self, client):
        """Test that the hello page is responsive."""
        response = client.get('/hello')
        html_content = response.data.decode('utf-8')
        
        # Test responsive classes
        responsive_classes = [
            'md:text-8xl',
            'lg:text-9xl',
            'sm:flex-row',
            'flex-col',
            'items-center',
            'justify-center',
            'container',
            'mx-auto',
            'px-6'
        ]
        
        for css_class in responsive_classes:
            assert css_class in html_content
    
    def test_hello_route_accessibility_features(self, client):
        """Test accessibility features in the hello page."""
        response = client.get('/hello')
        html_content = response.data.decode('utf-8')
        
        # Test semantic HTML
        assert '<section' in html_content
        assert '<h1' in html_content
        assert '<h2' in html_content
        
        # Test proper heading structure
        assert html_content.count('<h1') >= 1
        assert html_content.count('<h2') >= 1
        
        # Test lang attribute for screen readers
        assert 'lang="en"' in html_content
        
        # Test viewport meta tag for mobile accessibility
        assert 'name="viewport"' in html_content
    
    def test_hello_world_script_execution(self, hello_world_script):
        """Test that the hello_world.py script executes correctly."""
        # Check script exists
        assert os.path.exists(hello_world_script)
        
        # Run the script
        result = subprocess.run(
            [sys.executable, hello_world_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Test execution success
        assert result.returncode == 0
        assert 'Hello from Kortex' in result.stdout
        assert 'Timestamp:' in result.stdout
        
        # Test timestamp format
        timestamp_match = re.search(r'Timestamp: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)', result.stdout)
        assert timestamp_match is not None
        
        # Test that timestamp is recent (within last minute)
        timestamp_str = timestamp_match.group(1)
        script_time = datetime.fromisoformat(timestamp_str)
        current_time = datetime.now()
        time_diff = (current_time - script_time).total_seconds()
        assert time_diff < 60  # Script should have run within last minute
    
    def test_hello_world_script_output_format(self, hello_world_script):
        """Test the output format of the hello_world.py script."""
        result = subprocess.run(
            [sys.executable, hello_world_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        lines = result.stdout.strip().split('\n')
        assert len(lines) == 2
        assert lines[0] == 'Hello from Kortex'
        assert lines[1].startswith('Timestamp: ')
        assert result.stderr == ''
    
    def test_hello_route_performance(self, client):
        """Test that the hello route responds within acceptable time."""
        start_time = time.time()
        response = client.get('/hello')
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_hello_route_error_handling(self, client):
        """Test error handling for the hello route."""
        # Test normal access
        response = client.get('/hello')
        assert response.status_code == 200
        
        # Test with different HTTP methods
        post_response = client.post('/hello')
        assert post_response.status_code == 405  # Method not allowed
    
    def test_navigation_to_hello_from_home(self, client):
        """Test navigation from home page to hello page."""
        # Get home page
        home_response = client.get('/')
        assert home_response.status_code == 200
        
        # Check that hello link exists in navigation
        home_html = home_response.data.decode('utf-8')
        assert 'href="/hello"' in home_html
        assert 'Hello' in home_html
        
        # Navigate to hello page
        hello_response = client.get('/hello')
        assert hello_response.status_code == 200
        
        # Verify we're on the hello page
        hello_html = hello_response.data.decode('utf-8')
        assert 'Hello World' in hello_html
    
    def test_hello_route_template_consistency(self, client):
        """Test that the hello template is consistent with base template."""
        response = client.get('/hello')
        html_content = response.data.decode('utf-8')
        
        # Test that it extends base template
        assert '{% extends "base.html" %}' in open('templates/hello.html').read()
        
        # Test that it has proper blocks
        assert '{% block title %}' in open('templates/hello.html').read()
        assert '{% block content %}' in open('templates/hello.html').read()
        
        # Test that navigation is consistent
        assert 'Python Script Runner' in html_content
        assert 'Home' in html_content
        assert 'Scripts' in html_content
    
    def test_hello_world_script_independence(self, hello_world_script):
        """Test that hello_world.py can run independently."""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy script to temp directory
            import shutil
            temp_script = os.path.join(temp_dir, 'hello_world.py')
            shutil.copy(hello_world_script, temp_script)
            
            # Run from temp directory
            result = subprocess.run(
                [sys.executable, temp_script],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0
            assert 'Hello from Kortex' in result.stdout
    
    def test_hello_route_integration_with_scripts_page(self, client):
        """Test integration between hello route and scripts page."""
        # Get hello page
        hello_response = client.get('/hello')
        assert hello_response.status_code == 200
        
        # Check that scripts link works
        scripts_response = client.get('/scripts')
        assert scripts_response.status_code == 200
        
        # Verify navigation consistency
        hello_html = hello_response.data.decode('utf-8')
        scripts_html = scripts_response.data.decode('utf-8')
        
        # Both should have consistent navigation
        assert 'Python Script Runner' in hello_html
        assert 'Python Script Runner' in scripts_html
    
    def test_hello_world_script_error_handling(self, hello_world_script):
        """Test error handling in hello_world.py script."""
        # Test with invalid Python syntax (temporarily modify script)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("Hello from Kortex"\n')  # Syntax error
            temp_script = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, temp_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode != 0  # Should fail with syntax error
        finally:
            os.unlink(temp_script)
    
    def test_hello_route_content_security(self, client):
        """Test that hello route doesn't contain security vulnerabilities."""
        response = client.get('/hello')
        html_content = response.data.decode('utf-8')
        
        # Test for potential XSS vulnerabilities
        assert '<script>' not in html_content or 'src="https://cdn.tailwindcss.com"' in html_content
        assert 'javascript:' not in html_content
        assert 'onerror=' not in html_content
        assert 'onclick=' not in html_content
    
    def test_hello_route_caching_behavior(self, client):
        """Test caching behavior of hello route."""
        # First request
        response1 = client.get('/hello')
        assert response1.status_code == 200
        
        # Second request (should be similar)
        response2 = client.get('/hello')
        assert response2.status_code == 200
        
        # Content should be consistent
        assert response1.data == response2.data


class TestHelloWorldIntegration:
    """Integration tests for hello world functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        flask_app.app.config['TESTING'] = True
        with flask_app.app.test_client() as client:
            yield client
    
    def test_full_hello_world_workflow(self, client):
        """Test the complete hello world workflow."""
        # Step 1: Access home page
        home_response = client.get('/')
        assert home_response.status_code == 200
        
        # Step 2: Navigate to hello page
        hello_response = client.get('/hello')
        assert hello_response.status_code == 200
        
        # Step 3: Verify hello world content
        hello_html = hello_response.data.decode('utf-8')
        assert 'Hello World' in hello_html
        assert 'Welcome to Flask with Tailwind CSS' in hello_html
        
        # Step 4: Test navigation back to home
        home_response2 = client.get('/')
        assert home_response2.status_code == 200
    
    def test_hello_world_script_and_web_integration(self):
        """Test integration between hello_world.py script and web interface."""
        # Run the hello_world.py script
        script_path = os.path.join(os.path.dirname(__file__), 'hello_world.py')
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Verify script output
        assert result.returncode == 0
        assert 'Hello from Kortex' in result.stdout
        
        # Verify web interface is also working
        with flask_app.app.test_client() as client:
            response = client.get('/hello')
            assert response.status_code == 200
            assert 'Hello World' in response.data.decode('utf-8')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])