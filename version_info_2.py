#!/usr/bin/env python3
"""
Version info script that outputs 'Kortex version 1.0' followed by a timestamp in ISO format.
"""

from datetime import datetime

def main():
    """Main function to print version info with ISO timestamp."""
    # Get current timestamp in ISO format
    timestamp = datetime.now().isoformat()
    
    # Print the version info with timestamp (exactly 'Kortex version 1.0' followed by timestamp)
    print(f"Kortex version 1.0")
    print(f"{timestamp}")

if __name__ == "__main__":
    main()