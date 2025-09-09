#!/usr/bin/env python3
"""
PyPI Release Tool

Handles PyPI testing and release operations.
Follows ScriptCraft tool patterns for reusability.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import scriptcraft.common as cu

class PyPIReleaseTool(cu.BaseTool):
    """Tool for PyPI testing and release operations."""
    
    def __init__(self):
        super().__init__(
            name="PyPI Release Tool",
            description="Handles PyPI testing and release operations"
        )
    
    def run(self, operation: str = "test", **kwargs) -> bool:
        """Run PyPI operations."""
        cu.log_and_print(f"🚀 Starting PyPI {operation} operation...")
        
        if operation == "test":
            return self._test_upload(**kwargs)
        elif operation == "release":
            return self._release_upload(**kwargs)
        elif operation == "validate":
            return self._validate_package(**kwargs)
        elif operation == "build":
            return self._build_package(**kwargs)
        else:
            cu.log_and_print(f"❌ Unknown operation: {operation}", level="error")
            return False
    
    def _validate_package(self, **kwargs) -> bool:
        """Validate package integrity."""
        cu.log_and_print("🔍 Validating package...")
        
        # Check for required files
        required_files = ["pyproject.toml", "README.md"]
        for file in required_files:
            if not Path(file).exists():
                cu.log_and_print(f"❌ Missing required file: {file}", level="error")
                return False
        
        # Run validation tests if they exist
        if Path("tests").exists():
            cu.log_and_print("🧪 Running validation tests...")
            test_files = list(Path("tests").glob("test_*.py"))
            if test_files:
                for test_file in test_files:
                    if not self._run_command(f"python {test_file}", f"Running {test_file}"):
                        return False
        
        cu.log_and_print("✅ Package validation passed")
        return True
    
    def _build_package(self, **kwargs) -> bool:
        """Build the package."""
        cu.log_and_print("🔨 Building package...")
        
        # Clean previous builds
        for artifact in ["build", "dist", "*.egg-info"]:
            artifact_path = Path(artifact)
            if artifact_path.exists():
                if artifact_path.is_dir():
                    import shutil
                    shutil.rmtree(artifact_path)
                else:
                    artifact_path.unlink()
        
        # Build package
        if not self._run_command("python -m build", "Building package"):
            return False
        
        cu.log_and_print("✅ Package built successfully")
        return True
    
    def _test_upload(self, **kwargs) -> bool:
        """Test upload to PyPI test repository."""
        cu.log_and_print("🧪 Testing PyPI upload...")
        
        # Build package first
        if not self._build_package():
            return False
        
        # Test upload to PyPI test
        if not self._run_command("python -m twine upload --repository testpypi dist/*", 
                                "Testing upload to PyPI test"):
            cu.log_and_print("❌ Test upload failed", level="error")
            return False
        
        cu.log_and_print("✅ Test upload successful")
        return True
    
    def _release_upload(self, **kwargs) -> bool:
        """Release upload to PyPI."""
        cu.log_and_print("📦 Releasing to PyPI...")
        
        # Build package first
        if not self._build_package():
            return False
        
        # Upload to PyPI
        if not self._run_command("python -m twine upload dist/*", "Uploading to PyPI"):
            cu.log_and_print("❌ Release upload failed", level="error")
            return False
        
        cu.log_and_print("✅ Release upload successful")
        return True
    
    def _run_command(self, cmd: str, description: str) -> bool:
        """Run a command with proper encoding and logging."""
        cu.log_and_print(f"🔍 {description}...")
        
        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                env=env
            )
            
            if result.returncode == 0:
                cu.log_and_print(f"✅ {description} - SUCCESS")
                # Log to file for distributables
                self.logger.info(f"{description} - SUCCESS")
                return True
            else:
                cu.log_and_print(f"❌ {description} - FAILED", level="error")
                cu.log_and_print(f"Error: {result.stderr}", level="error")
                self.logger.error(f"{description} - FAILED: {result.stderr}")
                return False
        except Exception as e:
            cu.log_and_print(f"❌ {description} - EXCEPTION: {e}", level="error")
            self.logger.error(f"{description} - EXCEPTION: {e}")
            return False
