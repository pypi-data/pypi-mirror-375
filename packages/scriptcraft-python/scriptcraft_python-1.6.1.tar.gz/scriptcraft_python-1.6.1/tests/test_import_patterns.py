#!/usr/bin/env python3
"""
🧪 Import Pattern Tests

Test all documented import patterns to ensure they work correctly.
"""

import sys
from pathlib import Path

# Add the package to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_basic_import():
    """Test basic package import."""
    import scriptcraft
    assert hasattr(scriptcraft, '__version__')
    print(f"✅ Basic import works - version: {scriptcraft.__version__}")

def test_common_import():
    """Test common utilities import."""
    import scriptcraft.common as cu
    assert hasattr(cu, 'BaseTool')
    assert hasattr(cu, 'Config')
    assert hasattr(cu, 'setup_logger')
    assert hasattr(cu, 'log_and_print')
    print("✅ Common import works")

def test_specific_imports():
    """Test specific imports from common."""
    from scriptcraft.common import BaseTool, Config, setup_logger, log_and_print
    assert BaseTool is not None
    assert Config is not None
    assert setup_logger is not None
    assert log_and_print is not None
    print("✅ Specific imports work")

def test_tool_imports():
    """Test tool imports."""
    from scriptcraft.tools.automated_labeler import AutomatedLabeler
    from scriptcraft.tools.data_content_comparer import DataContentComparer
    from scriptcraft.tools.rhq_form_autofiller import RHQFormAutofiller
    
    # Test instantiation
    labeler = AutomatedLabeler()
    comparer = DataContentComparer()
    autofiller = RHQFormAutofiller()
    
    assert labeler.name == "Automated Labeler"
    assert comparer.name == "Data Content Comparer"
    assert autofiller.name == "RHQ Form Autofiller"
    print("✅ Tool imports work")

def test_tool_discovery():
    """Test tool discovery."""
    from scriptcraft.tools import get_available_tools, list_tools_by_category
    
    tools = get_available_tools()
    assert len(tools) > 0
    
    categories = list_tools_by_category()
    assert len(categories) > 0
    
    print(f"✅ Tool discovery works - {len(tools)} tools found")

def test_pipeline_imports():
    """Test pipeline imports."""
    from scriptcraft.pipelines import BasePipeline, PipelineStep
    assert BasePipeline is not None
    assert PipelineStep is not None
    print("✅ Pipeline imports work")

def test_config_usage():
    """Test configuration usage."""
    import scriptcraft.common as cu
    
    # Test config loading (should work with environment fallback)
    config = cu.Config.from_yaml("nonexistent.yaml")
    assert config is not None
    
    # Test tool config access
    tool_config = config.get_tool_config("test_tool")
    assert tool_config is not None
    print("✅ Config usage works")

def test_logging_usage():
    """Test logging usage."""
    import scriptcraft.common as cu
    
    # Test logging setup
    logger = cu.setup_logger("test_logger")
    assert logger is not None
    
    # Test log and print
    cu.log_and_print("✅ Test message")
    print("✅ Logging usage works")

def run_all_tests():
    """Run all import pattern tests."""
    print("🧪 Testing Import Patterns...")
    print("=" * 40)
    
    tests = [
        test_basic_import,
        test_common_import,
        test_specific_imports,
        test_tool_imports,
        test_tool_discovery,
        test_pipeline_imports,
        test_config_usage,
        test_logging_usage
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            return False
    
    print("\n" + "=" * 40)
    print("✅ All import pattern tests passed!")
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
