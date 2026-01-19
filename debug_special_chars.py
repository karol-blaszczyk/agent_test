#!/usr/bin/env python3

import sys
sys.path.append('/app/workspaces/8acfa580-8dde-4a1c-85e9-1d792da3b985')
from app.script_runner import safe_script_runner

# Test the problematic script
script_content = '''# Test various special characters
print("Quotes: 'single' and \\\"double\\\"")
print("Backslash: \\\\\\ \\\\\\test")
print("Newline: \\n Tab: \\t")
print("Unicode: 你好世界 🌍")
print("Math symbols: ∑ ∏ ∫ √ ∞")
print("Special: !@#$%^&*()_+-=[]{}|;':\\\",./<>?")
'''

result = safe_script_runner(script_content)
print(f"Status: {result['status']}")
print(f"Stderr: {result['stderr']}")
print(f"Stdout: {result['stdout']}")

# Check if the test assertions would pass
if result['status'] == 'success':
    print("\nChecking assertions:")
    print(f"Contains single and double quotes: {'single' and 'double' in result['stdout']}")
    print(f"Contains backslash: {'Backslash: \\\\ in result['stdout']}")
    print(f"Contains unicode: {'你好世界 🌍' in result['stdout']}")
    print(f"Contains math symbols: {'∑ ∏ ∫ √ ∞' in result['stdout']}")
else:
    print(f"\nScript failed with error: {result['error_message']}")