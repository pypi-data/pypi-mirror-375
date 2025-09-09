#!/usr/bin/env python3
"""
🧪 Package Integrity Tests

Comprehensive tests to ensure package integrity before uploads.
These tests should be run before any PyPI upload or distribution.
"""

import sys
import importlib
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import pytest

# Add the package to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestPackageIntegrity:
    """Test package integrity and basic functionality."""
    
    def test_basic_import(self):
        """Test that the package can be imported."""
        import scriptcraft
        assert hasattr(scriptcraft, '__version__')
        assert scriptcraft.__version__ is not None
        print(f"✅ Package version: {scriptcraft.__version__}")
    
    def test_common_import(self):
        """Test that common utilities can be imported."""
        import scriptcraft.common as cu
        assert hasattr(cu, 'BaseTool')
        assert hasattr(cu, 'Config')
        assert hasattr(cu, 'setup_logger')
        assert hasattr(cu, 'log_and_print')
        print("✅ Common utilities import successfully")
    
    def test_tool_discovery(self):
        """Test that tools can be discovered."""
        from scriptcraft.tools import get_available_tools
        tools = get_available_tools()
        assert len(tools) > 0
        print(f"✅ Discovered {len(tools)} tools")
        
        # Check for key tools
        expected_tools = [
            'automated_labeler',
            'data_content_comparer', 
            'rhq_form_autofiller',
            'dictionary_driven_checker'
        ]
        for tool in expected_tools:
            assert tool in tools, f"Missing expected tool: {tool}"
        print("✅ All expected tools found")
    
    def test_tool_instantiation(self):
        """Test that tools can be instantiated."""
        from scriptcraft.tools import get_available_tools
        tools = get_available_tools()
        
        # Test a few key tools
        test_tools = ['automated_labeler', 'data_content_comparer']
        for tool_name in test_tools:
            if tool_name in tools:
                tool_class = tools[tool_name]
                tool_instance = tool_class()
                assert hasattr(tool_instance, 'name')
                assert hasattr(tool_instance, 'run')
                print(f"✅ {tool_name} instantiates correctly")
    
    def test_config_loading(self):
        """Test configuration loading."""
        import scriptcraft.common as cu
        
        # Test environment-based config (should work without config.yaml)
        config = cu.Config.from_yaml("nonexistent.yaml")
        assert config is not None
        print("✅ Configuration loading works")
    
    def test_console_scripts(self):
        """Test that console scripts are properly configured."""
        # This test checks that the console scripts are defined in pyproject.toml
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        assert pyproject_path.exists()
        
        content = pyproject_path.read_text()
        assert "[project.scripts]" in content
        assert "scriptcraft" in content
        assert "rhq-autofiller" in content
        print("✅ Console scripts configured")
    
    def test_dependencies(self):
        """Test that all dependencies can be imported."""
        critical_deps = [
            'pandas',
            'numpy', 
            'openpyxl'
        ]
        
        optional_deps = [
            'pyyaml',
            'click',
            'rich'
        ]
        
        # Test critical dependencies
        for dep in critical_deps:
            try:
                importlib.import_module(dep)
                print(f"✅ {dep} available")
            except ImportError as e:
                pytest.fail(f"Missing critical dependency: {dep} - {e}")
        
        # Test optional dependencies
        for dep in optional_deps:
            try:
                importlib.import_module(dep)
                print(f"✅ {dep} available")
            except ImportError as e:
                print(f"⚠️ Optional dependency {dep} not available: {e}")
    
    def test_version_consistency(self):
        """Test that version is consistent across files."""
        import scriptcraft
        from scriptcraft._version import __version__
        
        assert scriptcraft.__version__ == __version__
        print(f"✅ Version consistent: {__version__}")
    
    def test_package_structure(self):
        """Test that package structure is correct."""
        package_path = Path(__file__).parent.parent / "scriptcraft"
        
        required_files = [
            "__init__.py",
            "_version.py",
            "common/__init__.py",
            "tools/__init__.py",
            "pipelines/__init__.py"
        ]
        
        for file_path in required_files:
            full_path = package_path / file_path
            assert full_path.exists(), f"Missing required file: {file_path}"
        
        print("✅ Package structure is correct")

class TestToolFunctionality:
    """Test basic tool functionality."""
    
    def test_automated_labeler(self):
        """Test automated labeler tool."""
        from scriptcraft.tools.automated_labeler import AutomatedLabeler
        tool = AutomatedLabeler()
        assert tool.name == "Automated Labeler"
        print("✅ AutomatedLabeler works")
    
    def test_data_content_comparer(self):
        """Test data content comparer tool."""
        from scriptcraft.tools.data_content_comparer import DataContentComparer
        tool = DataContentComparer()
        assert tool.name == "Data Content Comparer"
        print("✅ DataContentComparer works")
    
    def test_rhq_form_autofiller(self):
        """Test RHQ form autofiller tool."""
        from scriptcraft.tools.rhq_form_autofiller import RHQFormAutofiller
        tool = RHQFormAutofiller()
        assert tool.name == "RHQ Form Autofiller"
        print("✅ RHQFormAutofiller works")

def run_integrity_tests():
    """Run all integrity tests."""
    print("🧪 Running Package Integrity Tests...")
    print("=" * 50)
    
    # Run tests
    test_classes = [TestPackageIntegrity, TestToolFunctionality]
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}...")
        test_instance = test_class()
        
        # Get all test methods
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_')]
        
        for test_method in test_methods:
            try:
                getattr(test_instance, test_method)()
            except Exception as e:
                print(f"❌ {test_method} failed: {e}")
                return False
    
    print("\n" + "=" * 50)
    print("✅ All integrity tests passed!")
    return True

if __name__ == "__main__":
    success = run_integrity_tests()
    sys.exit(0 if success else 1)
