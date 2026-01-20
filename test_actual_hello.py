#!/usr/bin/env python3
"""
Test the actual Flask app /hello route.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Change to the workspace directory
os.chdir('/app/workspaces/8acfa580-8dde-4a1c-85e9-1d792da3b985')

# Import the Flask app by reading and executing app.py
app_globals = {}
with open('app.py', 'r') as f:
    code = f.read()
    exec(code, app_globals)

# Get the app from the executed code
app = app_globals['app']

def test_actual_hello_route():
    """Test the actual /hello route from the Flask app."""
    with app.test_client() as client:
        response = client.get('/hello')
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.content_type}")
        print(f"Content Length: {len(response.data)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: /hello route is working!")
            html_content = response.data.decode('utf-8')
            
            if 'Hello World' in html_content:
                print("✅ VERIFIED: Contains 'Hello World' in the response")
            else:
                print("❌ WARNING: Does not contain 'Hello World' in the response")
                
            if 'tailwind' in html_content:
                print("✅ VERIFIED: Contains Tailwind CSS")
                
            if 'bg-gradient-to-br' in html_content:
                print("✅ VERIFIED: Contains Tailwind gradient styling")
                
            print(f"\nFull HTML response length: {len(html_content)} characters")
            print("\nFirst 500 characters:")
            print(html_content[:500])
            
        else:
            print(f"❌ ERROR: Route returned status code {response.status_code}")
            print(f"Response: {response.data.decode('utf-8')}")

if __name__ == '__main__':
    test_actual_hello_route()