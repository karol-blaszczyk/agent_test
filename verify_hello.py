#!/usr/bin/env python3
"""
Verification script that runs hello.py and checks the output contains 'Hello World'
"""

import subprocess
import sys

def verify_hello_world():
    """
    Run hello.py and verify its output contains 'Hello World'
    """
    try:
        # Run the hello.py script
        result = subprocess.run(['python', 'hello.py'], 
                              capture_output=True, text=True, cwd='/app/workspaces/8acfa580-8dde-4a1c-85e9-1d792da3b985')
        
        if result.returncode != 0:
            print(f"❌ Script failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
        
        output = result.stdout.strip()
        
        # Check if output contains 'Hello World'
        if 'Hello World' not in output:
            print(f"❌ Output does not contain 'Hello World'. Got: '{output}'")
            return False
        
        print("✅ Verification passed!")
        print(f"✅ Output contains 'Hello World': '{output}'")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = verify_hello_world()
    exit(0 if success else 1)