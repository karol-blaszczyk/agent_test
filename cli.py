#!/usr/bin/env python3
"""
CLI interface for listing and running available Python scripts.

This script provides a command-line interface to:
- List all available Python scripts in the workspace
- Run scripts by name and display their output
- Show detailed execution results including stdout, stderr, and return codes
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the current directory to Python path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.script_runner import ScriptRunner
except ImportError:
    print("Warning: Could not import ScriptRunner. Script execution will be limited.")
    ScriptRunner = None


def find_python_scripts(directory: str = ".") -> List[Dict[str, str]]:
    """
    Find all Python scripts in the specified directory.
    
    Args:
        directory: Directory to search for scripts (default: current directory)
        
    Returns:
        List of dictionaries containing script information
    """
    scripts = []
    directory_path = Path(directory)
    
    # Look for Python files that are executable or have main blocks
    for py_file in directory_path.glob("*.py"):
        if py_file.name.startswith('test_'):
            continue  # Skip test files
            
        script_info = {
            'name': py_file.stem,
            'filename': py_file.name,
            'path': str(py_file.absolute()),
            'description': get_script_description(py_file)
        }
        scripts.append(script_info)
    
    return sorted(scripts, key=lambda x: x['name'])


def get_script_description(py_file: Path) -> str:
    """
    Extract a description from a Python file.
    
    Args:
        py_file: Path to the Python file
        
    Returns:
        Description string or empty string if not found
    """
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Look for docstring in the first few lines
        for line in lines[:10]:
            line = line.strip()
            if line.startswith('"""') or line.startswith("'''"):
                # Extract docstring content
                docstring = line.strip('"\'')
                if docstring and len(docstring) > 10:  # Avoid short docstrings
                    return docstring
        
        # Look for a comment describing the script
        for line in lines[:15]:
            line = line.strip()
            if line.startswith('#') and len(line) > 20:
                return line.strip('# ').strip()
                
    except Exception:
        pass
    
    return "No description available"


def list_scripts(scripts: List[Dict[str, str]]) -> None:
    """
    Display a list of available scripts.
    
    Args:
        scripts: List of script information dictionaries
    """
    if not scripts:
        print("No Python scripts found in the current directory.")
        return
    
    print(f"Available scripts ({len(scripts)} total):")
    print("=" * 60)
    
    for i, script in enumerate(scripts, 1):
        print(f"{i:2d}. {script['name']:<20} - {script['description']}")
    
    print("\nUse 'cli.py run <script_name>' to execute a script")


def run_script(script_name: str, use_script_runner: bool = True) -> int:
    """
    Run a Python script and display its output.
    
    Args:
        script_name: Name of the script to run (without .py extension)
        use_script_runner: Whether to use ScriptRunner if available
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Find the script
    scripts = find_python_scripts()
    script_info = None
    
    for script in scripts:
        if script['name'] == script_name:
            script_info = script
            break
    
    if not script_info:
        print(f"Error: Script '{script_name}' not found.")
        print("Use 'cli.py list' to see available scripts.")
        return 1
    
    script_path = script_info['path']
    
    print(f"Running script: {script_info['filename']}")
    print("=" * 60)
    
    try:
        if use_script_runner and ScriptRunner:
            # Use ScriptRunner for enhanced execution
            runner = ScriptRunner()
            result = runner.execute_file(script_path)
            
            # Display results
            if result['stdout']:
                print(result['stdout'])
            
            if result['stderr']:
                print("STDERR:")
                print(result['stderr'])
            
            if result['status'] == 'error':
                print(f"Script failed with return code: {result['return_code']}")
                if result['error_message']:
                    print(f"Error: {result['error_message']}")
                return result['return_code'] if result['return_code'] != -1 else 1
            
            print(f"Script completed successfully (return code: {result['return_code']})")
            return 0
            
        else:
            # Use subprocess as fallback
            import subprocess
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True
            )
            
            # Display output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            if result.returncode != 0:
                print(f"Script failed with return code: {result.returncode}")
                return result.returncode
            
            print(f"Script completed successfully (return code: {result.returncode})")
            return 0
            
    except KeyboardInterrupt:
        print("\nScript execution interrupted by user.")
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Error executing script: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CLI interface for listing and running Python scripts",
        epilog="Examples:\n"
               "  cli.py list                    # List all available scripts\n"
               "  cli.py run hello_world        # Run hello_world.py\n"
               "  cli.py run --no-runner hello  # Run without ScriptRunner",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all available scripts')
    list_parser.add_argument(
        '--directory', '-d',
        default='.',
        help='Directory to search for scripts (default: current directory)'
    )
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a specific script')
    run_parser.add_argument(
        'script_name',
        help='Name of the script to run (without .py extension)'
    )
    run_parser.add_argument(
        '--no-runner', '--no-script-runner',
        action='store_true',
        help='Run without using ScriptRunner (use subprocess directly)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'list':
        scripts = find_python_scripts(args.directory)
        list_scripts(scripts)
        return 0
        
    elif args.command == 'run':
        return run_script(args.script_name, not args.no_runner)
        
    else:
        # No command specified, show help and list scripts
        parser.print_help()
        print("\n" + "="*60 + "\n")
        scripts = find_python_scripts()
        if scripts:
            list_scripts(scripts)
        return 0


if __name__ == '__main__':
    sys.exit(main())