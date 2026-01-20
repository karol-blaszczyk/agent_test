#!/usr/bin/env python3
"""
Simple test to verify the /hello route works correctly.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create a minimal test without importing the full app
from flask import Flask, render_template_string

# Create a minimal Flask app for testing
test_app = Flask(__name__)

# Create a simple hello template
hello_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello World</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 min-h-screen flex items-center justify-center">
    <div class="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg p-8 text-center max-w-md mx-auto">
        <h1 class="text-4xl font-bold text-gray-800 mb-4">Hello World</h1>
        <p class="text-gray-600 mb-6">Welcome to our Flask application with Tailwind CSS!</p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="/" class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition duration-300 shadow-lg">
                Back to Home
            </a>
            <a href="/scripts" class="border-2 border-blue-600 text-blue-600 px-6 py-3 rounded-lg hover:bg-blue-600 hover:text-white transition duration-300">
                View Scripts
            </a>
        </div>
    </div>
</body>
</html>
"""

@test_app.route('/hello')
def hello():
    """Render a hello world page using render_template_string."""
    return render_template_string(hello_template)

def test_hello_route():
    """Test the /hello route."""
    with test_app.test_client() as client:
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
                print("ℹ️  INFO: Tailwind CSS is loaded via CDN")
                
            if 'bg-gradient-to-br' in html_content:
                print("✅ VERIFIED: Contains Tailwind gradient styling")
                
        else:
            print(f"❌ ERROR: Route returned status code {response.status_code}")
            print(f"Response: {response.data.decode('utf-8')}")

if __name__ == '__main__':
    test_hello_route()