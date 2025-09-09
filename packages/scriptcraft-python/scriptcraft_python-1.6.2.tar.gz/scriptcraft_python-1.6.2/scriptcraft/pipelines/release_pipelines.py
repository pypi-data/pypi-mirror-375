#!/usr/bin/env python3
"""
🚀 Release Pipelines

Composable release pipelines using the ScriptCraft pipeline system.
These can be used anywhere, not just in the ScriptCraft workspace.
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

class ReleasePipelineFactory:
    """Factory for creating release pipelines."""
    
    @staticmethod
    def create_python_package_pipeline(config: Any = None) -> BasePipeline:
        """Create a Python package release pipeline."""
        # Create minimal config for release pipelines if none provided
        if config is None:
            from scriptcraft.common.core.config import Config
            config = Config()
            config.workspace.domains = ["default"]  # Minimal domain for pipeline validation
        
        pipeline = BasePipeline(config, "Python Package Release")
        
        # Step 1: Validate package
        pipeline.add_step(PipelineStep(
            name="validate_package",
            log_filename="validation.log",
            qc_func=ReleasePipelineFactory._validate_package,
            input_key="package_root",
            run_mode="global"
        ))
        
        # Step 2: Run tests
        pipeline.add_step(PipelineStep(
            name="run_tests",
            log_filename="tests.log", 
            qc_func=ReleasePipelineFactory._run_tests,
            input_key="package_root",
            run_mode="global"
        ))
        
        # Step 3: Build package
        pipeline.add_step(PipelineStep(
            name="build_package",
            log_filename="build.log",
            qc_func=ReleasePipelineFactory._build_package,
            input_key="package_root",
            run_mode="global"
        ))
        
        # Step 4: Upload to PyPI
        pipeline.add_step(PipelineStep(
            name="upload_pypi",
            log_filename="upload.log",
            qc_func=ReleasePipelineFactory._upload_to_pypi,
            input_key="package_root",
            run_mode="global"
        ))
        
        return pipeline
    
    @staticmethod
    def create_git_release_pipeline(config: Any = None) -> BasePipeline:
        """Create a Git repository release pipeline."""
        # Create minimal config for release pipelines if none provided
        if config is None:
            from scriptcraft.common.core.config import Config
            config = Config()
            config.workspace.domains = ["default"]  # Minimal domain for pipeline validation
        
        pipeline = BasePipeline(config, "Git Repository Release")
        
        # Step 1: Check git status
        pipeline.add_step(PipelineStep(
            name="check_git_status",
            log_filename="git_status.log",
            qc_func=ReleasePipelineFactory._check_git_status,
            input_key="repo_root",
            run_mode="global"
        ))
        
        # Step 2: Create tag
        pipeline.add_step(PipelineStep(
            name="create_tag",
            log_filename="tag.log",
            qc_func=ReleasePipelineFactory._create_git_tag,
            input_key="repo_root",
            run_mode="global"
        ))
        
        # Step 3: Push to remote
        pipeline.add_step(PipelineStep(
            name="push_to_remote",
            log_filename="push.log",
            qc_func=ReleasePipelineFactory._push_to_remote,
            input_key="repo_root",
            run_mode="global"
        ))
        
        return pipeline
    
    @staticmethod
    def create_documentation_pipeline(config: Any = None) -> BasePipeline:
        """Create a documentation release pipeline."""
        # Create minimal config for release pipelines if none provided
        if config is None:
            from scriptcraft.common.core.config import Config
            config = Config()
            config.workspace.domains = ["default"]  # Minimal domain for pipeline validation
        
        pipeline = BasePipeline(config, "Documentation Release")
        
        # Step 1: Build docs
        pipeline.add_step(PipelineStep(
            name="build_docs",
            log_filename="docs_build.log",
            qc_func=ReleasePipelineFactory._build_docs,
            input_key="docs_root",
            run_mode="global"
        ))
        
        # Step 2: Deploy docs
        pipeline.add_step(PipelineStep(
            name="deploy_docs",
            log_filename="docs_deploy.log",
            qc_func=ReleasePipelineFactory._deploy_docs,
            input_key="docs_root",
            run_mode="global"
        ))
        
        return pipeline
    
    @staticmethod
    def create_full_release_pipeline(config: Any = None) -> BasePipeline:
        """Create a full release pipeline combining all steps."""
        # Create minimal config for release pipelines if none provided
        if config is None:
            from scriptcraft.common.core.config import Config
            config = Config()
            config.workspace.domains = ["default"]  # Minimal domain for pipeline validation
        
        pipeline = BasePipeline(config, "Full Release")
        
        # Add Python package steps
        python_pipeline = ReleasePipelineFactory.create_python_package_pipeline(config)
        for step in python_pipeline.steps:
            pipeline.add_step(step)
        
        # Add Git release steps
        git_pipeline = ReleasePipelineFactory.create_git_release_pipeline(config)
        for step in git_pipeline.steps:
            pipeline.add_step(step)
        
        # Add documentation steps
        docs_pipeline = ReleasePipelineFactory.create_documentation_pipeline(config)
        for step in docs_pipeline.steps:
            pipeline.add_step(step)
        
        return pipeline
    
    # Pipeline step implementations
    @staticmethod
    def _validate_package(**kwargs) -> None:
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
            result = subprocess.run([sys.executable, "tests/test_package_integrity.py"],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                cu.log_and_print(f"❌ Validation tests failed: {result.stderr}", level="error")
                return
        
        cu.log_and_print("✅ Package validation passed")
    
    @staticmethod
    def _run_tests(**kwargs) -> None:
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
    
    @staticmethod
    def _build_package(**kwargs) -> None:
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
    
    @staticmethod
    def _upload_to_pypi(**kwargs) -> None:
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
    
    @staticmethod
    def _check_git_status(**kwargs) -> None:
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
    
    @staticmethod
    def _create_git_tag(**kwargs) -> None:
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
    
    @staticmethod
    def _push_to_remote(**kwargs) -> None:
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
    
    @staticmethod
    def _build_docs(**kwargs) -> None:
        """Build documentation."""
        cu.log_and_print("📚 Building documentation...")
        
        # Check for common documentation systems
        if Path("docs").exists():
            # Try Sphinx
            if Path("docs/conf.py").exists():
                cu.log_and_print("Building Sphinx documentation...")
                result = subprocess.run([sys.executable, "-m", "sphinx", "docs", "docs/_build"],
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    cu.log_and_print(f"❌ Sphinx build failed: {result.stderr}", level="error")
                    return
            # Try MkDocs
            elif Path("mkdocs.yml").exists():
                cu.log_and_print("Building MkDocs documentation...")
                result = subprocess.run([sys.executable, "-m", "mkdocs", "build"],
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    cu.log_and_print(f"❌ MkDocs build failed: {result.stderr}", level="error")
                    return
        
        cu.log_and_print("✅ Documentation built")
    
    @staticmethod
    def _deploy_docs(**kwargs) -> None:
        """Deploy documentation."""
        cu.log_and_print("🚀 Deploying documentation...")
        
        if kwargs.get("dry_run", False):
            cu.log_and_print("🔍 DRY RUN: Would deploy docs")
            return
        
        # Try MkDocs deployment
        if Path("mkdocs.yml").exists():
            cu.log_and_print("Deploying with MkDocs...")
            result = subprocess.run([sys.executable, "-m", "mkdocs", "gh-deploy"],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                cu.log_and_print(f"❌ MkDocs deployment failed: {result.stderr}", level="error")
                return
        
        cu.log_and_print("✅ Documentation deployed")

# Convenience functions for easy usage
def create_python_package_pipeline(config: Any = None) -> BasePipeline:
    """Create a Python package release pipeline."""
    return ReleasePipelineFactory.create_python_package_pipeline(config)

def create_git_release_pipeline(config: Any = None) -> BasePipeline:
    """Create a Git repository release pipeline."""
    return ReleasePipelineFactory.create_git_release_pipeline(config)

def create_documentation_pipeline(config: Any = None) -> BasePipeline:
    """Create a documentation release pipeline."""
    return ReleasePipelineFactory.create_documentation_pipeline(config)

def create_full_release_pipeline(config: Any = None) -> BasePipeline:
    """Create a full release pipeline combining all steps."""
    return ReleasePipelineFactory.create_full_release_pipeline(config)

# CLI interface
def main():
    """CLI interface for release pipelines."""
    parser = argparse.ArgumentParser(description="Release Pipeline Runner")
    parser.add_argument("pipeline", choices=["python_package", "git_repo", "docs", "full"],
                       help="Release pipeline to run")
    parser.add_argument("--version", help="Version to release")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--config", help="Configuration file path")
    
    args = parser.parse_args()
    
    # Load configuration
    config = None
    if args.config:
        config = cu.Config.from_yaml(args.config)
    
    # Create and run pipeline
    pipeline_creators = {
        "python_package": create_python_package_pipeline,
        "git_repo": create_git_release_pipeline,
        "docs": create_documentation_pipeline,
        "full": create_full_release_pipeline
    }
    
    pipeline = pipeline_creators[args.pipeline](config)
    
    # Set up context
    context = {
        "version": args.version or "0.0.0",
        "dry_run": args.dry_run,
        "timestamp": datetime.now().isoformat()
    }
    
    cu.log_and_print(f"🚀 Starting {args.pipeline} release pipeline...")
    pipeline.run()
    cu.log_and_print(f"✅ {args.pipeline} release pipeline completed!")

if __name__ == "__main__":
    main()
