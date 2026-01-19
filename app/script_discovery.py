"""
Script Discovery Module

This module provides functionality to discover and analyze Python scripts
in the root directory, excluding tests/, app/, and hidden files.
"""

import os
import ast
import glob
from typing import List, Dict, Any, Optional
from pathlib import Path


class ScriptInfo:
    """Represents information about a discovered script."""
    
    def __init__(self, file_path: str, name: str, description: str = "", 
                 has_main: bool = False, imports: List[str] = None, 
                 functions: List[str] = None, classes: List[str] = None):
        self.file_path = file_path
        self.name = name
        self.description = description
        self.has_main = has_main
        self.imports = imports or []
        self.functions = functions or []
        self.classes = classes or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ScriptInfo to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'name': self.name,
            'description': self.description,
            'has_main': self.has_main,
            'is_runnable': self.has_main,  # Convenience property
            'imports': self.imports,
            'functions': self.functions,
            'classes': self.classes,
            'size': os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0
        }


def discover_scripts(root_dir: str = None, exclude_dirs: List[str] = None, 
                     exclude_patterns: List[str] = None) -> List[Dict[str, Any]]:
    """
    Discover Python scripts in the root directory.
    
    Args:
        root_dir: Root directory to scan (default: current working directory)
        exclude_dirs: List of directories to exclude from subdirectories (default: ['tests', 'app', '__pycache__'])
        exclude_patterns: List of filename patterns to exclude (default: ['test_*'])
    
    Returns:
        List of script metadata dictionaries
    """
    if root_dir is None:
        root_dir = os.getcwd()
    
    if exclude_dirs is None:
        exclude_dirs = ['tests', 'app', '__pycache__', '.git', '.pytest_cache']
    
    if exclude_patterns is None:
        exclude_patterns = ['test_*']
    
    scripts = []
    
    # Convert to Path for easier handling
    root_path = Path(root_dir)
    
    # Find all Python files in root directory (not subdirectories)
    for py_file in root_path.glob("*.py"):
        # Skip hidden files
        if py_file.name.startswith('.'):
            continue
            
        # Check exclude patterns (like test_*)
        import fnmatch
        if any(fnmatch.fnmatch(py_file.name, pattern) for pattern in exclude_patterns):
            continue
        
        try:
            script_info = analyze_script(str(py_file))
            scripts.append(script_info.to_dict())
        except Exception as e:
            # If we can't parse a file, add it with minimal info
            scripts.append({
                'file_path': str(py_file),
                'name': py_file.stem,
                'description': f"Unable to parse: {str(e)}",
                'has_main': False,
                'is_runnable': False,
                'imports': [],
                'functions': [],
                'classes': [],
                'size': py_file.stat().st_size if py_file.exists() else 0
            })
    
    return scripts


def analyze_script(file_path: str) -> ScriptInfo:
    """
    Analyze a Python script to extract metadata.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        ScriptInfo object with extracted metadata
    """
    path = Path(file_path)
    
    # Read and parse the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        # If we can't parse the AST, return basic info
        return ScriptInfo(
            file_path=file_path,
            name=path.stem,
            description=f"Syntax error in script: {str(e)}",
            has_main=False
        )
    
    # Extract information from AST
    has_main = False
    imports = []
    functions = []
    classes = []
    docstring = ""
    
    # Get module docstring
    if (isinstance(tree.body[0], ast.Expr) and 
        isinstance(tree.body[0].value, ast.Constant) and
        isinstance(tree.body[0].value.value, str)):
        docstring = tree.body[0].value.value.strip()
    elif (isinstance(tree.body[0], ast.Expr) and 
          isinstance(tree.body[0].value, ast.Str)):
        # Python < 3.8 compatibility
        docstring = tree.body[0].value.s.strip()
    
    for node in ast.walk(tree):
        # Check for if __name__ == "__main__":
        if isinstance(node, ast.If):
            if (isinstance(node.test, ast.Compare) and
                isinstance(node.test.left, ast.Name) and
                node.test.left.id == "__name__"):
                has_main = True
        
        # Extract imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
        
        # Extract function definitions
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        
        # Extract class definitions
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
    
    return ScriptInfo(
        file_path=file_path,
        name=path.stem,
        description=docstring[:200] if docstring else f"Python script: {path.stem}",
        has_main=has_main,
        imports=list(set(imports)),  # Remove duplicates
        functions=functions,
        classes=classes
    )


def get_runnable_scripts(scripts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter scripts to only return runnable ones (those with if __name__ == "__main__").
    
    Args:
        scripts: List of script metadata dictionaries
        
    Returns:
        Filtered list of only runnable scripts
    """
    return [script for script in scripts if script.get('has_main', False)]


def search_scripts(query: str, scripts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Search scripts by name, description, or content.
    
    Args:
        query: Search query string
        scripts: List of script metadata dictionaries
        
    Returns:
        Filtered list of matching scripts
    """
    query = query.lower()
    results = []
    
    for script in scripts:
        # Search in name, description, functions, and classes
        searchable_text = [
            script.get('name', '').lower(),
            script.get('description', '').lower(),
            ' '.join(script.get('functions', [])).lower(),
            ' '.join(script.get('classes', [])).lower()
        ]
        
        if any(query in text for text in searchable_text):
            results.append(script)
    
    return results


# Example usage
if __name__ == "__main__":
    print("Discovering Python scripts...")
    
    # Discover all scripts
    all_scripts = discover_scripts()
    print(f"Found {len(all_scripts)} Python scripts")
    
    # Show runnable scripts
    runnable_scripts = get_runnable_scripts(all_scripts)
    print(f"Found {len(runnable_scripts)} runnable scripts")
    
    # Display script information
    for script in all_scripts:
        print(f"\nScript: {script['name']}")
        print(f"  Path: {script['file_path']}")
        print(f"  Runnable: {script['is_runnable']}")
        print(f"  Functions: {len(script['functions'])}")
        print(f"  Classes: {len(script['classes'])}")
        if script['description']:
            print(f"  Description: {script['description'][:100]}...")
    
    # Example search
    if all_scripts:
        print(f"\nSearching for scripts with 'test' in name...")
        test_scripts = search_scripts('test', all_scripts)
        print(f"Found {len(test_scripts)} matching scripts")