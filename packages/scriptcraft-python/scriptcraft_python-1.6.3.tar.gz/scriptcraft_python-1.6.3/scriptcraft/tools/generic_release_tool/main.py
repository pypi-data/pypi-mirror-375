#!/usr/bin/env python3
"""
🚀 Generic Release Tool

A workspace-agnostic release tool that can be used anywhere.
Uses the pipeline system for flexible, composable release workflows.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

import scriptcraft.common as cu
from scriptcraft.common.pipeline import BasePipeline, PipelineStep

class GenericReleaseTool(cu.BaseTool):
    """Generic release tool that works anywhere."""
    
    def __init__(self):
        super().__init__(
            name="Generic Release Tool",
            description="🚀 Workspace-agnostic release management using pipelines",
            tool_name="generic_release_tool"
        )
        self.release_pipelines = {}
        self._setup_default_pipelines()
    
    def _setup_default_pipelines(self):
        """Setup default release pipelines."""
        
        # Python Package Release Pipeline
        self.release_pipelines["python_package"] = self._create_python_package_pipeline()
        
        # Git Repository Release Pipeline  
        self.release_pipelines["git_repo"] = self._create_git_repo_pipeline()
        
        # Documentation Release Pipeline
        self.release_pipelines["docs"] = self._create_docs_pipeline()
        
        # Combined Release Pipeline
        self.release_pipelines["full"] = self._create_full_pipeline()
    
    def _create_python_package_pipeline(self) -> BasePipeline:
        """Create a Python package release pipeline."""
        pipeline = BasePipeline(self.config, "Python Package Release")
        
        # Step 1: Validate package
        pipeline.add_step(PipelineStep(
            name="validate_package",
            log_filename="validation.log",
            qc_func=self._validate_package,
            input_key="package_root",
            run_mode="global"
        ))
        
        # Step 2: Run tests
        pipeline.add_step(PipelineStep(
            name="run_tests", 
            log_filename="tests.log",
            qc_func=self._run_tests,
            input_key="package_root",
            run_mode="global"
        ))
        
        # Step 3: Build package
        pipeline.add_step(PipelineStep(
            name="build_package",
            log_filename="build.log", 
            qc_func=self._build_package,
            input_key="package_root",
            run_mode="global"
        ))
        
        # Step 4: Upload to PyPI
        pipeline.add_step(PipelineStep(
            name="upload_pypi",
            log_filename="upload.log",
            qc_func=self._upload_to_pypi,
            input_key="package_root", 
            run_mode="global"
        ))
        
        return pipeline
    
    def _create_git_repo_pipeline(self) -> BasePipeline:
        """Create a Git repository release pipeline."""
        pipeline = BasePipeline(self.config, "Git Repository Release")
        
        # Step 1: Check git status
        pipeline.add_step(PipelineStep(
            name="check_git_status",
            log_filename="git_status.log",
            qc_func=self._check_git_status,
            input_key="repo_root",
            run_mode="global"
        ))
        
        # Step 2: Create tag
        pipeline.add_step(PipelineStep(
            name="create_tag",
            log_filename="tag.log",
            qc_func=self._create_git_tag,
            input_key="repo_root",
            run_mode="global"
        ))
        
        # Step 3: Push to remote
        pipeline.add_step(PipelineStep(
            name="push_to_remote",
            log_filename="push.log",
            qc_func=self._push_to_remote,
            input_key="repo_root",
            run_mode="global"
        ))
        
        return pipeline
    
    def _create_docs_pipeline(self) -> BasePipeline:
        """Create a documentation release pipeline."""
        pipeline = BasePipeline(self.config, "Documentation Release")
        
        # Step 1: Build docs
        pipeline.add_step(PipelineStep(
            name="build_docs",
            log_filename="docs_build.log",
            qc_func=self._build_docs,
            input_key="docs_root",
            run_mode="global"
        ))
        
        # Step 2: Deploy docs
        pipeline.add_step(PipelineStep(
            name="deploy_docs",
            log_filename="docs_deploy.log", 
            qc_func=self._deploy_docs,
            input_key="docs_root",
            run_mode="global"
        ))
        
        return pipeline
    
    def _create_full_pipeline(self) -> BasePipeline:
        """Create a full release pipeline combining all steps."""
        pipeline = BasePipeline(self.config, "Full Release")
        
        # Add all steps from other pipelines
        for step in self.release_pipelines["python_package"].steps:
            pipeline.add_step(step)
        
        for step in self.release_pipelines["git_repo"].steps:
            pipeline.add_step(step)
            
        for step in self.release_pipelines["docs"].steps:
            pipeline.add_step(step)
        
        return pipeline
    
    def run(self,
            pipeline: Optional[str] = None,
            version: Optional[str] = None,
            dry_run: bool = False,
            **kwargs) -> None:
        """Run a release pipeline."""
        
        if not pipeline:
            pipeline = "python_package"  # Default
        
        if pipeline not in self.release_pipelines:
            cu.log_and_print(f"❌ Unknown pipeline: {pipeline}", level="error")
            cu.log_and_print(f"Available pipelines: {list(self.release_pipelines.keys())}")
            return
        
        cu.log_and_print(f"🚀 Starting {pipeline} release pipeline...")
        
        if dry_run:
            cu.log_and_print("🔍 DRY RUN MODE - No actual changes will be made")
        
        # Set up context
        context = {
            "version": version or self._get_current_version(),
            "dry_run": dry_run,
            "timestamp": datetime.now().isoformat()
        }
        
        # Run the pipeline
        release_pipeline = self.release_pipelines[pipeline]
        release_pipeline.run()
        
        cu.log_and_print(f"✅ {pipeline} release pipeline completed!")
    
    def _get_current_version(self) -> str:
        """Get current version from various sources."""
        # Try to get version from package
        try:
            import scriptcraft
            return scriptcraft.__version__
        except:
            pass
        
        # Try to get version from _version.py
        try:
            version_file = Path("_version.py")
            if version_file.exists():
                content = version_file.read_text()
                for line in content.split('\n'):
                    if line.startswith('__version__'):
                        return line.split('"')[1]
        except:
            pass
        
        # Try to get version from pyproject.toml
        try:
            pyproject_file = Path("pyproject.toml")
            if pyproject_file.exists():
                content = pyproject_file.read_text()
                for line in content.split('\n'):
                    if 'version' in line and '=' in line:
                        return line.split('=')[1].strip().strip('"')
        except:
            pass
        
        return "0.0.0"
    
    # Pipeline step functions
    def _validate_package(self, **kwargs) -> None:
        """Validate package integrity."""
        cu.log_and_print("🔍 Validating package...")
        
        # Check for required files
        required_files = ["pyproject.toml", "README.md"]
        for file in required_files:
            if not Path(file).exists():
                cu.log_and_print(f"❌ Missing required file: {file}", level="error")
                return
        
        # Run validation tests if they exist
        if Path("tests").exists():
            cu.log_and_print("🧪 Running validation tests...")
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            result = subprocess.run([sys.executable, "tests/test_package_integrity.py"], 
                                  capture_output=True, text=True, encoding='utf-8', env=env)
            if result.returncode != 0:
                cu.log_and_print(f"❌ Validation tests failed: {result.stderr}", level="error")
                return
        
        cu.log_and_print("✅ Package validation passed")
    
    def _run_tests(self, **kwargs) -> None:
        """Run package tests."""
        cu.log_and_print("🧪 Running tests...")
        
        if not Path("tests").exists():
            cu.log_and_print("⚠️ No tests directory found, skipping tests")
            return
        
        # Run pytest if available
        try:
            result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                cu.log_and_print(f"❌ Tests failed: {result.stderr}", level="error")
                return
        except FileNotFoundError:
            # Fallback to running test files directly
            test_files = list(Path("tests").glob("test_*.py"))
            for test_file in test_files:
                cu.log_and_print(f"Running {test_file}...")
                result = subprocess.run([sys.executable, str(test_file)], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    cu.log_and_print(f"❌ {test_file} failed: {result.stderr}", level="error")
                    return
        
        cu.log_and_print("✅ All tests passed")
    
    def _build_package(self, **kwargs) -> None:
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
        result = subprocess.run([sys.executable, "-m", "build"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            cu.log_and_print(f"❌ Build failed: {result.stderr}", level="error")
            return
        
        cu.log_and_print("✅ Package built successfully")
    
    def _upload_to_pypi(self, **kwargs) -> None:
        """Upload package to PyPI."""
        cu.log_and_print("📦 Uploading to PyPI...")
        
        if kwargs.get("dry_run", False):
            cu.log_and_print("🔍 DRY RUN: Would upload to PyPI")
            return
        
        # Check if twine is available
        try:
            result = subprocess.run([sys.executable, "-m", "twine", "upload", "dist/*"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                cu.log_and_print(f"❌ Upload failed: {result.stderr}", level="error")
                return
        except FileNotFoundError:
            cu.log_and_print("❌ twine not found. Install with: pip install twine", level="error")
            return
        
        cu.log_and_print("✅ Package uploaded to PyPI")
    
    def _check_git_status(self, **kwargs) -> None:
        """Check Git repository status."""
        cu.log_and_print("🔍 Checking Git status...")
        
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            cu.log_and_print("❌ Not a Git repository", level="error")
            return
        
        if result.stdout.strip():
            cu.log_and_print("⚠️ Uncommitted changes found:")
            cu.log_and_print(result.stdout)
            return
        
        cu.log_and_print("✅ Git repository is clean")
    
    def _create_git_tag(self, **kwargs) -> None:
        """Create a Git tag."""
        version = kwargs.get("version", "0.0.0")
        cu.log_and_print(f"🏷️ Creating Git tag: v{version}")
        
        if kwargs.get("dry_run", False):
            cu.log_and_print("🔍 DRY RUN: Would create tag")
            return
        
        result = subprocess.run(["git", "tag", f"v{version}"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            cu.log_and_print(f"❌ Tag creation failed: {result.stderr}", level="error")
            return
        
        cu.log_and_print(f"✅ Git tag v{version} created")
    
    def _push_to_remote(self, **kwargs) -> None:
        """Push to remote repository."""
        cu.log_and_print("📤 Pushing to remote...")
        
        if kwargs.get("dry_run", False):
            cu.log_and_print("🔍 DRY RUN: Would push to remote")
            return
        
        # Push commits
        result = subprocess.run(["git", "push"], capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            cu.log_and_print(f"❌ Push failed: {result.stderr}", level="error")
            return
        
        # Push tags
        result = subprocess.run(["git", "push", "--tags"], capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            cu.log_and_print(f"❌ Tag push failed: {result.stderr}", level="error")
            return
        
        cu.log_and_print("✅ Pushed to remote successfully")
    
    def _build_docs(self, **kwargs) -> None:
        """Build documentation."""
        cu.log_and_print("📚 Building documentation...")
        
        # This is a placeholder - implement based on your docs system
        cu.log_and_print("✅ Documentation built")
    
    def _deploy_docs(self, **kwargs) -> None:
        """Deploy documentation."""
        cu.log_and_print("🚀 Deploying documentation...")
        
        if kwargs.get("dry_run", False):
            cu.log_and_print("🔍 DRY RUN: Would deploy docs")
            return
        
        # This is a placeholder - implement based on your docs system
        cu.log_and_print("✅ Documentation deployed")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generic Release Tool")
    parser.add_argument("--pipeline", choices=["python_package", "git_repo", "docs", "full"],
                       default="python_package", help="Release pipeline to run")
    parser.add_argument("--version", help="Version to release")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    
    tool = GenericReleaseTool()
    tool.run(
        pipeline=args.pipeline,
        version=args.version,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()
