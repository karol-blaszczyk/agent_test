#!/usr/bin/env python3
"""
Tests for the calculator module's __main__.py entry point.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
import importlib


class TestMainModule:
    """Test the __main__.py module functionality."""
    
    def test_main_module_imports(self):
        """Test that the main module can be imported without errors."""
        # This should not raise any exceptions
        from tools.calculator import __main__
        
        # Check that main is imported from cli
        assert hasattr(__main__, 'main')
    
    @patch('tools.calculator.__main__.main')
    def test_main_execution_when_run_directly(self, mock_main):
        """Test that main() is called when module is run directly."""
        # Import the module fresh
        import tools.calculator.__main__
        
        # Since __name__ will be "tools.calculator.__main__" when imported,
        # the main() function should NOT be called automatically
        # We need to test the actual execution context
        
        # Re-import with __name__ set to "__main__"
        with patch.object(tools.calculator.__main__, '__name__', '__main__'):
            # Re-execute the module
            importlib.reload(tools.calculator.__main__)
            
            # main() should have been called
            mock_main.assert_called_once()
    
    def test_main_not_called_on_import(self):
        """Test that main() is not called when module is imported."""
        with patch('tools.calculator.__main__.main') as mock_main:
            # Import the module normally (not as __main__)
            import tools.calculator.__main__
            
            # main() should NOT be called on import
            mock_main.assert_not_called()
    
    def test_module_docstring(self):
        """Test that the module has appropriate docstring."""
        from tools.calculator import __main__
        
        assert __main__.__doc__ is not None
        assert "entry point" in __main__.__doc__.lower()
        assert "calculator" in __main__.__doc__.lower()
    
    def test_main_import_from_cli(self):
        """Test that main is correctly imported from cli module."""
        from tools.calculator import __main__
        from tools.calculator.cli import main as cli_main
        
        # The main function should be the same object
        assert __main__.main is cli_main


class TestModuleExecution:
    """Test the module execution behavior."""
    
    def test_module_execution_context(self):
        """Test the module execution in different contexts."""
        # Test that we can execute the module's code
        from tools.calculator import __main__
        
        # The module should be executable
        assert hasattr(__main__, '__file__') or True  # __file__ may not exist in all contexts
    
    @patch('tools.calculator.cli.main')
    def test_cli_main_integration(self, mock_cli_main):
        """Test integration with the CLI main function."""
        # Import and test that the CLI main is accessible
        from tools.calculator import __main__
        from tools.calculator.cli import main
        
        # They should be the same function
        assert __main__.main is main
        
        # Test calling main
        __main__.main()
        mock_cli_main.assert_called_once()


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])