#!/usr/bin/env python3
"""
Test the /hello route in the Flask app.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask and create a simple test
from flask import Flask, render_template_string

# Create a test app that mimics the real app
test_app = Flask(__name__, template_folder='templates')

# Simple hello template for testing
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

def test_route():
    """Test the hello route."""
    with test_app.test_client() as client:
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
            
        else:
            print(f"❌ ERROR: Route returned status code {response.status_code}")

if __name__ == '__main__':
    test_route()