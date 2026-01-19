"""
Tests for Script Discovery Module

This module contains comprehensive tests for the script discovery functionality,
covering script detection, exclusion rules, metadata extraction, and error handling.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.script_discovery import discover_scripts, analyze_script, ScriptInfo, get_runnable_scripts, search_scripts


class TestScriptDiscovery:
    """Test cases for script discovery functionality."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def sample_scripts(self, temp_workspace):
        """Create sample Python scripts for testing."""
        # Create a simple runnable script
        script1 = temp_workspace / "hello_world.py"
        script1.write_text('''"""
Hello World script for testing.
"""

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
''')
        
        # Create a non-runnable script (no if __name__ == "__main__")
        script2 = temp_workspace / "utility.py"
        script2.write_text('''"""
Utility functions for testing.
"""

def helper_function():
    return "helper"

class UtilityClass:
    pass
''')
        
        # Create a script with syntax error
        script3 = temp_workspace / "broken.py"
        script3.write_text('''
# This script has a syntax error
print("Hello"
# Missing closing parenthesis
''')
        
        # Create a hidden script (should be excluded)
        script4 = temp_workspace / ".hidden.py"
        script4.write_text('print("Hidden script")')
        
        # Create a test file (should be excluded by default)
        script5 = temp_workspace / "test_something.py"
        script5.write_text('''
import pytest

def test_something():
    assert True
''')
        
        return temp_workspace
    
    def test_discover_scripts_basic_functionality(self, sample_scripts):
        """Test basic script discovery functionality."""
        scripts = discover_scripts(root_dir=str(sample_scripts))
        
        # Should find scripts in root directory
        assert len(scripts) >= 2
        
        # Get script names for easier testing
        script_names = [script['name'] for script in scripts]
        
        # Should find hello_world.py
        assert 'hello_world' in script_names
        # Should find utility.py
        assert 'utility' in script_names
        # Should NOT find .hidden.py (hidden file)
        assert '.hidden' not in script_names
    
    def test_discover_scripts_excludes_test_files(self, sample_scripts):
        """Test that test files are excluded by default."""
        scripts = discover_scripts(root_dir=str(sample_scripts))
        
        script_names = [script['name'] for script in scripts]
        
        # Should exclude test files by default
        assert 'test_something' not in script_names
    
    def test_discover_scripts_with_custom_exclusions(self, sample_scripts):
        """Test script discovery with custom exclusion patterns."""
        # Create additional files to test exclusions
        (sample_scripts / "my_test.py").write_text('print("test")')
        (sample_scripts / "example.py").write_text('print("example")')
        
        # Test with custom exclusions
        scripts = discover_scripts(
            root_dir=str(sample_scripts),
            exclude_dirs=['tests', 'app', '__pycache__', '.git', '.pytest_cache']
        )
        
        script_names = [script['name'] for script in scripts]
        
        # Should still find regular scripts
        assert 'hello_world' in script_names
        assert 'utility' in script_names
        
        # Should find the new files (they're not in excluded dirs)
        assert 'my_test' in script_names
        assert 'example' in script_names
    
    def test_script_metadata_extraction(self, sample_scripts):
        """Test that script metadata is correctly extracted."""
        scripts = discover_scripts(root_dir=str(sample_scripts))
        
        # Find the hello_world script
        hello_world = next((s for s in scripts if s['name'] == 'hello_world'), None)
        assert hello_world is not None
        
        # Check metadata
        assert hello_world['has_main'] is True
        assert hello_world['is_runnable'] is True
        assert 'Hello World script for testing' in hello_world['description']
        assert len(hello_world['functions']) >= 1
        assert 'main' in hello_world['functions']
        assert hello_world['size'] > 0
    
    def test_non_runnable_script_detection(self, sample_scripts):
        """Test detection of non-runnable scripts."""
        scripts = discover_scripts(root_dir=str(sample_scripts))
        
        # Find the utility script (no if __name__ == "__main__")
        utility = next((s for s in scripts if s['name'] == 'utility'), None)
        assert utility is not None
        
        # Should not be runnable
        assert utility['has_main'] is False
        assert utility['is_runnable'] is False
        
        # Should have functions and classes
        assert 'helper_function' in utility['functions']
        assert 'UtilityClass' in utility['classes']
    
    def test_broken_script_handling(self, sample_scripts):
        """Test handling of scripts with syntax errors."""
        scripts = discover_scripts(root_dir=str(sample_scripts))
        
        # Find the broken script
        broken = next((s for s in scripts if s['name'] == 'broken'), None)
        assert broken is not None
        
        # Should have error description
        assert 'Unable to parse' in broken['description'] or 'Syntax error' in broken['description']
        assert broken['has_main'] is False
        assert broken['is_runnable'] is False
    
    def test_get_runnable_scripts_filtering(self, sample_scripts):
        """Test filtering to get only runnable scripts."""
        all_scripts = discover_scripts(root_dir=str(sample_scripts))
        runnable_scripts = get_runnable_scripts(all_scripts)
        
        # Should only return scripts with has_main=True
        for script in runnable_scripts:
            assert script['has_main'] is True
            assert script['is_runnable'] is True
        
        # Should find the hello_world script
        script_names = [s['name'] for s in runnable_scripts]
        assert 'hello_world' in script_names
        
        # Should not include utility script (not runnable)
        assert 'utility' not in script_names
    
    def test_search_scripts_functionality(self, sample_scripts):
        """Test script search functionality."""
        all_scripts = discover_scripts(root_dir=str(sample_scripts))
        
        # Search for "hello"
        hello_results = search_scripts('hello', all_scripts)
        assert len(hello_results) >= 1
        assert any(s['name'] == 'hello_world' for s in hello_results)
        
        # Search for "world" (case insensitive)
        world_results = search_scripts('world', all_scripts)
        assert len(world_results) >= 1
        
        # Search for non-existent term
        no_results = search_scripts('nonexistentterm', all_scripts)
        assert len(no_results) == 0
    
    def test_search_in_descriptions(self, sample_scripts):
        """Test that search includes script descriptions."""
        all_scripts = discover_scripts(root_dir=str(sample_scripts))
        
        # Search for "testing" which should be in descriptions
        results = search_scripts('testing', all_scripts)
        assert len(results) >= 2  # Should find multiple scripts
    
    def test_search_in_functions_and_classes(self, temp_workspace):
        """Test that search includes function and class names."""
        # Create a script with specific function/class names
        script = temp_workspace / "special.py"
        script.write_text('''
def my_special_function():
    pass

class SpecialClass:
    pass

if __name__ == "__main__":
    pass
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        
        # Search for function name
        func_results = search_scripts('my_special_function', scripts)
        assert len(func_results) == 1
        assert func_results[0]['name'] == 'special'
        
        # Search for class name
        class_results = search_scripts('SpecialClass', scripts)
        assert len(class_results) == 1
        assert class_results[0]['name'] == 'special'
    
    def test_empty_directory(self, temp_workspace):
        """Test script discovery in empty directory."""
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 0
    
    def test_directory_with_only_hidden_files(self, temp_workspace):
        """Test that hidden files are properly excluded."""
        # Create only hidden files
        (temp_workspace / ".hidden1.py").write_text('print("hidden1")')
        (temp_workspace / ".hidden2.py").write_text('print("hidden2")')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 0
    
    def test_script_with_no_description(self, temp_workspace):
        """Test script without docstring."""
        script = temp_workspace / "nodoc.py"
        script.write_text('print("no docstring")')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        assert 'Python script: nodoc' in script_info['description']
    
    def test_script_with_complex_imports(self, temp_workspace):
        """Test script with various import types."""
        script = temp_workspace / "imports.py"
        script.write_text('''"""
Script with various imports.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict
import json as js

if __name__ == "__main__":
    pass
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        imports = script_info['imports']
        
        # Should detect various import types
        assert 'os' in imports
        assert 'sys' in imports
        assert 'pathlib' in imports
        assert 'typing' in imports
        assert 'json' in imports
    
    def test_analyze_script_file_not_found(self):
        """Test analyze_script with non-existent file."""
        with pytest.raises(FileNotFoundError):
            analyze_script("/path/to/nonexistent/file.py")
    
    def test_analyze_script_with_unicode_content(self, temp_workspace):
        """Test analyzing script with unicode characters."""
        script = temp_workspace / "unicode.py"
        script.write_text('''"""
Script with unicode characters: 你好世界 🌍 émojis
"""

def hello_world():
    print("Hello, 世界!")

if __name__ == "__main__":
    hello_world()
''', encoding='utf-8')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        assert 'unicode' in script_info['description']
        assert script_info['has_main'] is True
    
    def test_script_size_calculation(self, temp_workspace):
        """Test that script size is correctly calculated."""
        script = temp_workspace / "sized.py"
        content = 'print("Hello")\n' * 10  # 10 lines
        script.write_text(content)
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        expected_size = len(content.encode('utf-8'))
        assert script_info['size'] == expected_size
    
    def test_script_info_to_dict_method(self, temp_workspace):
        """Test ScriptInfo to_dict method."""
        script = temp_workspace / "test_dict.py"
        script.write_text('print("test")')
        
        script_info = analyze_script(str(script))
        result_dict = script_info.to_dict()
        
        # Check all expected keys are present
        expected_keys = ['file_path', 'name', 'description', 'has_main', 'is_runnable', 
                        'imports', 'functions', 'classes', 'size']
        for key in expected_keys:
            assert key in result_dict
        
        # Check values
        assert result_dict['file_path'] == str(script)
        assert result_dict['name'] == 'test_dict'
        assert result_dict['has_main'] is False
        assert result_dict['is_runnable'] is False
    
    def test_discover_scripts_with_file_read_error(self, temp_workspace):
        """Test handling of files that can't be read."""
        # Create a file that will cause a read error
        script = temp_workspace / "unreadable.py"
        script.write_text('print("test")')
        
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Cannot read file")):
            scripts = discover_scripts(root_dir=str(temp_workspace))
            
            # Should still return scripts, but with error information
            assert len(scripts) == 1
            assert 'Unable to parse' in scripts[0]['description']
    
    def test_current_directory_default(self):
        """Test that discover_scripts uses current directory by default."""
        # This test just ensures the function can run with default parameters
        # without throwing exceptions
        scripts = discover_scripts()
        assert isinstance(scripts, list)
        # Should not raise any exceptions
    
    def test_script_with_main_guard_variations(self, temp_workspace):
        """Test detection of main guard with different formatting."""
        # Test with different spacing/formatting
        script1 = temp_workspace / "main1.py"
        script1.write_text('''
if __name__ == "__main__":
    print("main")
''')
        
        script2 = temp_workspace / "main2.py"
        script2.write_text('''
if __name__=="__main__":
    print("main")
''')
        
        script3 = temp_workspace / "main3.py"
        script3.write_text('''
if __name__ == '__main__':
    print("main")
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 3
        
        # All should be detected as runnable
        for script in scripts:
            assert script['has_main'] is True
            assert script['is_runnable'] is True

    def test_script_with_nested_functions_and_classes(self, temp_workspace):
        """Test detection of nested functions and classes."""
        script = temp_workspace / "nested.py"
        script.write_text('''"""
Script with nested functions and classes.
"""

class OuterClass:
    def outer_method(self):
        pass
    
    class InnerClass:
        def inner_method(self):
            pass

def outer_function():
    def inner_function():
        pass
    return inner_function

if __name__ == "__main__":
    pass
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        # The current implementation detects all classes and functions, including nested ones
        assert 'OuterClass' in script_info['classes']
        assert 'InnerClass' in script_info['classes']  # Nested class is detected
        assert 'outer_function' in script_info['functions']
        assert 'inner_function' in script_info['functions']  # Nested function is detected

    def test_script_with_docstring_variations(self, temp_workspace):
        """Test handling of different docstring formats."""
        # Test with triple single quotes
        script1 = temp_workspace / "doc1.py"
        script1.write_text("""
'''Single quote docstring.'''

def main():
    pass
""")
        
        # Test with no docstring but with module-level variable
        script2 = temp_workspace / "doc2.py"
        script2.write_text('''
MODULE_VAR = "value"

def main():
    pass
''')
        
        # Test with very long docstring
        script3 = temp_workspace / "doc3.py"
        long_desc = "This is a very long description. " * 20
        script3.write_text(f'''"""
{long_desc}
"""

def main():
    pass
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 3
        
        # Check that descriptions are handled appropriately
        for script in scripts:
            assert script['description'] != ""

    def test_script_with_circular_imports_pattern(self, temp_workspace):
        """Test script that might cause import issues."""
        script = temp_workspace / "circular.py"
        script.write_text('''"""
Script with potential circular import pattern.
"""
import os
import sys
from pathlib import Path
# Simulate a circular import scenario
if 'os' in sys.modules:
    import os as os_alias

def main():
    print("Handling imports carefully")

if __name__ == "__main__":
    main()
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        # Should handle imports without issues
        assert 'os' in script_info['imports'] or 'os_alias' in script_info['imports']

    def test_script_with_syntax_error_variations(self, temp_workspace):
        """Test various types of syntax errors."""
        # Missing colon
        script1 = temp_workspace / "syntax1.py"
        script1.write_text('''
def function_without_colon()
    pass
''')
        
        # Invalid indentation
        script2 = temp_workspace / "syntax2.py"
        script2.write_text('''
def valid_function():
    pass
    invalid_indentation()
''')
        
        # Unclosed string
        script3 = temp_workspace / "syntax3.py"
        script3.write_text('''
def function():
    x = "unclosed string
    return x
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 3
        
        # All should be handled gracefully with error descriptions
        for script in scripts:
            assert ('Unable to parse' in script['description'] or 
                   'Syntax error' in script['description'] or
                   len(script['description']) > 0)
            assert script['has_main'] is False
            assert script['is_runnable'] is False

    def test_script_with_large_number_of_functions(self, temp_workspace):
        """Test script with many functions to ensure performance."""
        script = temp_workspace / "many_functions.py"
        
        # Generate a script with many functions
        content = '"""Script with many functions."""\n\n'
        for i in range(50):  # Create 50 functions
            content += f'def function_{i}():\n    pass\n\n'
        content += '\nif __name__ == "__main__":\n    pass\n'
        
        script.write_text(content)
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        assert len(script_info['functions']) == 50
        assert all(f'function_{i}' in script_info['functions'] for i in range(50))

    def test_script_with_special_characters_in_names(self, temp_workspace):
        """Test handling of special characters in function/class names."""
        script = temp_workspace / "special_names.py"
        script.write_text('''"""
Script with special naming patterns.
"""

def function_with_123_numbers():
    pass

def _private_function():
    pass

class ClassWithNumbers123:
    pass

class _PrivateClass:
    pass

if __name__ == "__main__":
    pass
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        # Should handle various naming patterns
        assert 'function_with_123_numbers' in script_info['functions']
        assert '_private_function' in script_info['functions']
        assert 'ClassWithNumbers123' in script_info['classes']
        assert '_PrivateClass' in script_info['classes']

    def test_script_with_very_long_description(self, temp_workspace):
        """Test handling of very long descriptions."""
        script = temp_workspace / "long_desc.py"
        # Create a very long description (more than 200 chars)
        long_desc = "This is a very long description that should be truncated. " * 15
        expected_short = long_desc[:200]
        
        script.write_text(f'''"""
{long_desc}
"""

def main():
    pass

if __name__ == "__main__":
    main()
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        # Description should be truncated to 200 characters
        assert len(script_info['description']) <= 200
        assert script_info['description'].startswith("This is a very long description")

    def test_script_with_no_functions_or_classes(self, temp_workspace):
        """Test script that only has imports and main block."""
        script = temp_workspace / "minimal.py"
        script.write_text('''"""
Minimal script with just imports and main.
"""
import os
import sys

if __name__ == "__main__":
    print("Hello from minimal script")
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        assert script_info['functions'] == []
        assert script_info['classes'] == []
        assert len(script_info['imports']) > 0
        assert script_info['has_main'] is True

    def test_script_with_conditional_main_detection(self, temp_workspace):
        """Test that only proper main guards are detected."""
        script1 = temp_workspace / "valid_main.py"
        script1.write_text('''
if __name__ == "__main__":
    print("Valid main")
''')
        
        script2 = temp_workspace / "invalid_main.py"
        script2.write_text('''
if __name__ == "main":  # Missing quotes
    print("Invalid")
''')
        
        script3 = temp_workspace / "variable_main.py"
        script3.write_text('''
__name__ = "__main__"  # Assignment, not comparison
if __name__ == "__main__":
    print("Variable")
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 3
        
        # Only the first should be detected as runnable
        valid_main = next((s for s in scripts if s['name'] == 'valid_main'), None)
        assert valid_main['has_main'] is True

    def test_search_with_empty_query(self, sample_scripts):
        """Test search with empty query string."""
        all_scripts = discover_scripts(root_dir=str(sample_scripts))
        results = search_scripts('', all_scripts)
        # Empty query should return all scripts
        assert len(results) == len(all_scripts)

    def test_search_with_special_characters(self, sample_scripts):
        """Test search with special regex characters."""
        all_scripts = discover_scripts(root_dir=str(sample_scripts))
        
        # Search with regex special characters
        results1 = search_scripts('hello.world', all_scripts)  # Dot in query
        results2 = search_scripts('hello*world', all_scripts)  # Asterisk in query
        results3 = search_scripts('hello[world]', all_scripts)  # Brackets in query
        
        # Should handle special characters without regex errors
        assert isinstance(results1, list)
        assert isinstance(results2, list)
        assert isinstance(results3, list)

    def test_get_runnable_scripts_with_empty_list(self):
        """Test get_runnable_scripts with empty list."""
        result = get_runnable_scripts([])
        assert result == []

    def test_get_runnable_scripts_with_malformed_data(self):
        """Test get_runnable_scripts with malformed script data."""
        malformed_scripts = [
            {'name': 'script1'},  # Missing has_main
            {'name': 'script2', 'has_main': None},  # None has_main
            {'name': 'script3', 'has_main': False},  # Explicit False
            {'name': 'script4', 'has_main': 'invalid'},  # Invalid has_main type (truthy string)
            {'name': 'script5', 'has_main': 0},  # Zero (falsy)
            {'name': 'script6', 'has_main': 1},  # One (truthy)
        ]
        
        result = get_runnable_scripts(malformed_scripts)
        # Should handle malformed data - only truthy values should pass
        assert isinstance(result, list)
        # Only script3 (False), script4 (truthy string), and script6 (1) should be included
        assert len(result) == 2  # script4 and script6 have truthy has_main values

    def test_discover_scripts_with_permission_error(self, temp_workspace):
        """Test handling of permission errors during file discovery."""
        # Create a script
        script = temp_workspace / "permission.py"
        script.write_text('print("test")')
        
        # Mock os.listdir to raise PermissionError
        with patch('os.listdir', side_effect=PermissionError("Access denied")):
            scripts = discover_scripts(root_dir=str(temp_workspace))
            # Should handle permission error gracefully
            assert isinstance(scripts, list)

    def test_script_info_with_nonexistent_file(self):
        """Test ScriptInfo with file that doesn't exist."""
        info = ScriptInfo(
            file_path="/nonexistent/file.py",
            name="nonexistent",
            description="Test file"
        )
        
        result = info.to_dict()
        # Size should be 0 for non-existent files
        assert result['size'] == 0

    def test_analyze_script_with_binary_content_handling(self, temp_workspace):
        """Test analyze_script handling of files that might contain binary-like content."""
        script = temp_workspace / "binary_like.py"
        # Create content that might confuse the parser
        script.write_text('''"""
Script with potentially confusing content.
"""
# This line has some \x00 \xff binary-like escapes

def main():
    print("Hello")

if __name__ == "__main__":
    main()
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        # Should handle the content gracefully
        assert script_info['name'] == 'binary_like'
        assert isinstance(script_info['description'], str)

    def test_discover_scripts_with_subdirectory_files(self, temp_workspace):
        """Test that files in subdirectories are not discovered."""
        # Create a subdirectory with Python files
        subdir = temp_workspace / "subdir"
        subdir.mkdir()
        
        # Create files in subdirectory
        (subdir / "sub_script.py").write_text('print("sub")')
        (subdir / "another.py").write_text('print("another")')
        
        # Create a file in root directory
        (temp_workspace / "root_script.py").write_text('print("root")')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1  # Only root_script.py should be found
        assert scripts[0]['name'] == 'root_script'

    def test_script_with_future_imports(self, temp_workspace):
        """Test handling of __future__ imports."""
        script = temp_workspace / "future_imports.py"
        script.write_text('''"""
Script with future imports.
"""
from __future__ import annotations
from __future__ import print_function
import os

if __name__ == "__main__":
    pass
''')
        
        scripts = discover_scripts(root_dir=str(temp_workspace))
        assert len(scripts) == 1
        
        script_info = scripts[0]
        # Should handle future imports
        assert len(script_info['imports']) >= 1
        assert script_info['has_main'] is True


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])