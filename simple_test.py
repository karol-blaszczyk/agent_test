#!/usr/bin/env python3
"""
Simple test to verify the scripts UI component.
"""

import os
import sys

# Change to the workspace directory
os.chdir('/app/workspaces/8acfa580-8dde-4a1c-85e9-1d792da3b985')

# Import the Flask app
sys.path.insert(0, '/app/workspaces/8acfa580-8dde-4a1c-85e9-1d792da3b985')
import app as flask_app

def test_scripts_ui():
    """Test the scripts UI component."""
    print("Testing Scripts UI Component...")
    
    with flask_app.app.test_client() as client:
        response = client.get('/scripts')
        
        print(f"Scripts page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Scripts page loads successfully!")
            content = response.data.decode('utf-8')
            
            # Check for key elements
            checks = [
                ('Available Scripts', 'header'),
                ('Run Script', 'Run buttons'),
                ('bg-white rounded-xl shadow-lg', 'Tailwind card styling'),
                ('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3', 'responsive grid'),
                ('runScript(', 'JavaScript interactivity'),
                ('hover:shadow-xl', 'hover effects'),
                ('transition-all duration-300', 'CSS transitions')
            ]
            
            passed = 0
            for check, desc in checks:
                if check in content:
                    print(f"✓ Contains {desc}")
                    passed += 1
            
            # Count scripts
            import re
            script_count = len(re.findall(r'Run Script', content))
            print(f"✓ Found {script_count} script run buttons")
            
            print(f"\n=== Test Results ===")
            print(f"Passed: {passed}/{len(checks)} checks")
            
            if passed >= len(checks) * 0.8:  # 80% pass rate
                print("✅ Scripts UI component is properly implemented!")
                return True
            else:
                print("❌ Scripts UI component needs improvements")
                return False
                
        else:
            print(f"✗ Error: {response.status_code}")
            return False

if __name__ == '__main__':
    success = test_scripts_ui()
    sys.exit(0 if success else 1)