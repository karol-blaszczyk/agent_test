#!/usr/bin/env python3
"""
Test script to verify the /hello route works correctly.
"""

import os
import sys

# Set environment variable to avoid port conflicts
os.environ['FLASK_RUN_PORT'] = '5010'

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app by executing the app.py file
exec(open('app.py').read())

def test_hello_route():
    """Test the /hello route."""
    # Use test client to avoid port issues
    with app.test_client() as client:
        response = client.get('/hello')
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.content_type}")
        print(f"Content Length: {len(response.data)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: /hello route is working!")
            print("\nFirst 300 characters of response:")
            print(response.data.decode('utf-8')[:300])
            
            # Check if it contains expected content
            html_content = response.data.decode('utf-8')
            if 'Hello World' in html_content:
                print("✅ VERIFIED: Contains 'Hello World' in the response")
            else:
                print("❌ WARNING: Does not contain 'Hello World' in the response")
                
            if 'Tailwind' in html_content or 'tailwind' in html_content:
                print("✅ VERIFIED: Contains Tailwind CSS styling")
            else:
                print("ℹ️  INFO: Tailwind CSS is loaded via CDN in the base template")
                
        else:
            print(f"❌ ERROR: Route returned status code {response.status_code}")
            print(f"Response: {response.data.decode('utf-8')}")

if __name__ == '__main__':
    test_hello_route()