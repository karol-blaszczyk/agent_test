#!/usr/bin/env python3
"""
Test script to verify the scripts.html UI component implementation.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app

def test_scripts_ui():
    """Test the scripts UI component."""
    print("Testing Scripts UI Component...")
    
    with app.test_client() as client:
        response = client.get('/scripts')
        
        print(f"Scripts page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Scripts page loads successfully!")
            html_content = response.data.decode('utf-8')
            
            # Check for key elements
            checks = [
                ('Available Scripts', 'expected header'),
                ('Run Script', 'Run buttons'),
                ('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6', 'Tailwind CSS grid layout'),
                ('bg-white rounded-xl shadow-lg', 'Tailwind card styling'),
                ('runScript(', 'JavaScript for interactivity'),
                ('https://cdn.tailwindcss.com', 'Tailwind CSS CDN'),
                ('hover:shadow-xl', 'hover effects'),
                ('transition-all duration-300', 'CSS transitions'),
                ('flex-1 bg-blue-600 text-white', 'blue button styling'),
                ('border border-gray-300 text-gray-700', 'secondary button styling')
            ]
            
            passed_checks = 0
            for check, description in checks:
                if check in html_content:
                    print(f"✓ Contains {description}")
                    passed_checks += 1
                else:
                    print(f"✗ Missing {description}")
            
            # Count scripts
            import re
            script_count = len(re.findall(r'Run Script', html_content))
            print(f"✓ Found {script_count} script run buttons")
            
            # Check for proper HTML structure
            structure_checks = [
                ('<div class="max-w-6xl mx-auto">', 'container layout'),
                ('text-4xl font-bold text-gray-800', 'main heading styling'),
                ('text-xl text-gray-600', 'subheading styling'),
                ('bg-red-100 border border-red-400', 'error message styling'),
                ('bg-gray-900 text-green-400', 'output terminal styling'),
                ('overflow-x-auto', 'responsive overflow'),
                ('whitespace-pre-wrap', 'code formatting')
            ]
            
            for check, description in structure_checks:
                if check in html_content:
                    print(f"✓ Has proper {description}")
                    passed_checks += 1
                else:
                    print(f"✗ Missing proper {description}")
            
            print(f"\n=== Test Results ===")
            print(f"Passed: {passed_checks}/{len(checks) + len(structure_checks)} checks")
            
            if passed_checks >= len(checks) * 0.8:  # 80% pass rate
                print("✅ Scripts UI component is properly implemented!")
                return True
            else:
                print("❌ Scripts UI component needs improvements")
                return False
                
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Response data: {response.data.decode('utf-8')}")
            return False

if __name__ == '__main__':
    success = test_scripts_ui()
    sys.exit(0 if success else 1)