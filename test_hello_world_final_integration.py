#!/usr/bin/env python3
"""
Final integration test for hello world web functionality.
Tests the complete integration between the hello_world.py script and the web interface.
"""

import pytest
import subprocess
import json
import time
import importlib.util

# Import the Flask app from app.py using importlib to avoid package conflicts
spec = importlib.util.spec_from_file_location("flask_app", "app.py")
flask_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flask_app)


class TestHelloWorldFinalIntegration:
    """Final integration tests for hello world functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        flask_app.app.config['TESTING'] = True
        with flask_app.app.test_client() as client:
            yield client
    
    def test_hello_world_script_execution_via_api(self):
        """Test executing hello_world.py script through the API."""
        with flask_app.app.test_client() as client:
            # Test running hello_world script via API
            response = client.post('/api/scripts/hello_world/run')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
            assert data['script_name'] == 'hello_world'
            assert 'stdout' in data
            assert 'Hello from Kortex' in data['stdout']
            assert 'Timestamp:' in data['stdout']
    
    def test_hello_world_script_viewing(self):
        """Test viewing the hello_world.py script source code."""
        with flask_app.app.test_client() as client:
            # Test viewing script source
            response = client.get('/api/scripts/hello_world')
            
            # Should return 404 since this endpoint doesn't exist, but let's test the view endpoint
            response = client.get('/view/hello_world')
            
            assert response.status_code == 200
            assert 'Hello from Kortex' in response.data.decode('utf-8')
            assert 'Timestamp:' in response.data.decode('utf-8')
    
    def test_complete_user_workflow(self, client):
        """Test the complete user workflow from home to hello world."""
        # Step 1: User visits home page
        home_response = client.get('/')
        assert home_response.status_code == 200
        
        # Step 2: User clicks on Hello navigation link
        hello_response = client.get('/hello')
        assert hello_response.status_code == 200
        
        # Step 3: User sees the hello world page
        hello_html = hello_response.data.decode('utf-8')
        assert 'Hello World' in hello_html
        assert 'Welcome to Flask with Tailwind CSS' in hello_html
        
        # Step 4: User can navigate back to home
        home_response2 = client.get('/')
        assert home_response2.status_code == 200
        
        # Step 5: User can navigate to scripts page
        scripts_response = client.get('/scripts')
        assert scripts_response.status_code == 200
    
    def test_hello_world_page_performance(self, client):
        """Test the performance of the hello world page."""
        # Warm up
        client.get('/hello')
        
        # Test multiple requests
        times = []
        for _ in range(5):
            start = time.time()
            response = client.get('/hello')
            end = time.time()
            
            assert response.status_code == 200
            times.append(end - start)
        
        # Average response time should be fast
        avg_time = sum(times) / len(times)
        assert avg_time < 0.1  # Should be under 100ms
    
    def test_hello_world_content_integrity(self, client):
        """Test that hello world content is complete and consistent."""
        response = client.get('/hello')
        html_content = response.data.decode('utf-8')
        
        # Test all expected content elements are present
        expected_elements = [
            'Hello World',
            'Welcome to Flask with Tailwind CSS',
            'Built with Modern Technologies',
            'Flask Backend',
            'Tailwind CSS',
            'Python Scripts',
            'Back to Home',
            'View Scripts',
            'Ready to Get Started?'
        ]
        
        for element in expected_elements:
            assert element in html_content, f"Missing element: {element}"
    
    def test_hello_world_styling_integrity(self, client):
        """Test that all Tailwind CSS styling is properly applied."""
        response = client.get('/hello')
        html_content = response.data.decode('utf-8')
        
        # Test gradient background
        assert 'bg-gradient-to-br' in html_content
        assert 'from-blue-500' in html_content
        assert 'via-purple-500' in html_content
        assert 'to-pink-500' in html_content
        
        # Test text styling
        assert 'text-6xl' in html_content
        assert 'md:text-8xl' in html_content
        assert 'lg:text-9xl' in html_content
        assert 'font-bold' in html_content
        assert 'bg-clip-text' in html_content
        assert 'text-transparent' in html_content
        
        # Test layout
        assert 'min-h-[70vh]' in html_content
        assert 'flex' in html_content
        assert 'items-center' in html_content
        assert 'justify-center' in html_content
        assert 'text-center' in html_content
    
    def test_hello_world_navigation_consistency(self, client):
        """Test navigation consistency across pages."""
        # Get all main pages
        pages = ['/', '/hello', '/scripts']
        
        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            
            html_content = response.data.decode('utf-8')
            
            # All pages should have consistent navigation
            assert 'Python Script Runner' in html_content
            assert 'Home' in html_content
            assert 'Hello' in html_content
            assert 'Scripts' in html_content
    
    def test_hello_world_error_handling(self, client):
        """Test error handling for hello world functionality."""
        # Test invalid HTTP methods
        post_response = client.post('/hello')
        assert post_response.status_code == 405
        
        put_response = client.put('/hello')
        assert put_response.status_code == 405
        
        delete_response = client.delete('/hello')
        assert delete_response.status_code == 405
    
    def test_hello_world_script_independence(self):
        """Test that hello_world.py can run independently of the web app."""
        # Run the script directly
        result = subprocess.run(
            ['python', 'hello_world.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        assert 'Hello from Kortex' in result.stdout
        assert 'Timestamp:' in result.stdout
        assert result.stderr == ''
    
    def test_hello_world_integration_with_flask_app(self):
        """Test that hello world works as part of the Flask application."""
        # Test that the Flask app can be imported and used
        assert hasattr(flask_app, 'app')
        assert flask_app.app.name == 'flask_app'
        
        # Test that hello route is registered
        with flask_app.app.test_client() as client:
            response = client.get('/hello')
            assert response.status_code == 200
            assert 'Hello World' in response.data.decode('utf-8')


class TestHelloWorldEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        flask_app.app.config['TESTING'] = True
        with flask_app.app.test_client() as client:
            yield client
    
    def test_hello_world_response_size(self, client):
        """Test that hello world response is reasonably sized."""
        response = client.get('/hello')
        
        # Response should not be too large (indicating bloat)
        assert len(response.data) < 50000  # 50KB max
        
        # Response should not be too small (indicating missing content)
        assert len(response.data) > 5000  # 5KB min
    
    def test_hello_world_response_size(self, client):
        """Test that hello world response is reasonably sized."""
        response = client.get('/hello')
        
        # Response should not be too large (indicating bloat)
        assert len(response.data) < 50000  # 50KB max
        
        # Response should not be too small (indicating missing content)
        assert len(response.data) > 5000  # 5KB min
    
    def test_hello_world_content_type_headers(self, client):
        """Test proper content type headers."""
        response = client.get('/hello')
        
        assert response.content_type == 'text/html; charset=utf-8'
        assert 'text/html' in response.headers.get('Content-Type', '')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])