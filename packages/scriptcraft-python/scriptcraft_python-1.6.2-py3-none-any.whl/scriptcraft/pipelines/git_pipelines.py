#!/usr/bin/env python3
"""
Git Pipelines

Reusable Git operation pipelines using the ScriptCraft pipeline system.
Follows DRY principles and integrates with existing infrastructure.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import scriptcraft.common as cu
from scriptcraft.common.pipeline import BasePipeline, PipelineStep

class GitPipelineFactory:
    """Factory for creating Git operation pipelines."""
    
    @staticmethod
    def _sync_submodules(**kwargs) -> None:
        """Sync Git submodules."""
        from scriptcraft.tools.git_submodule_tool import GitSubmoduleTool
        tool = GitSubmoduleTool()
        tool.run(operation="sync")
    
    @staticmethod
    def _push_workspace(**kwargs) -> None:
        """Push workspace changes."""
        from scriptcraft.tools.git_workspace_tool import GitWorkspaceTool
        tool = GitWorkspaceTool()
        tool.run(operation="push")
    
    @staticmethod
    def _check_git_status(**kwargs) -> None:
        """Check Git status."""
        from scriptcraft.tools.git_workspace_tool import GitWorkspaceTool
        tool = GitWorkspaceTool()
        tool.run(operation="status")
    
    @staticmethod
    def _validate_package(**kwargs) -> None:
        """Validate package."""
        from scriptcraft.tools.pypi_release_tool import PyPIReleaseTool
        tool = PyPIReleaseTool()
        tool.run(operation="validate")
    
    @staticmethod
    def _build_package(**kwargs) -> None:
        """Build package."""
        from scriptcraft.tools.pypi_release_tool import PyPIReleaseTool
        tool = PyPIReleaseTool()
        tool.run(operation="build")
    
    @staticmethod
    def _test_upload(**kwargs) -> None:
        """Test PyPI upload."""
        from scriptcraft.tools.pypi_release_tool import PyPIReleaseTool
        tool = PyPIReleaseTool()
        tool.run(operation="test")
    
    @staticmethod
    def _release_upload(**kwargs) -> None:
        """Release to PyPI."""
        from scriptcraft.tools.pypi_release_tool import PyPIReleaseTool
        tool = PyPIReleaseTool()
        tool.run(operation="release")
    
    @staticmethod
    def create_submodule_sync_pipeline(config: Any = None) -> BasePipeline:
        """Create a submodule sync pipeline."""
        # Create minimal config for Git pipelines if none provided
        if config is None:
            from scriptcraft.common.core.config import Config
            config = Config()
            config.workspace.domains = ["default"]  # Minimal domain for pipeline validation
        
        pipeline = BasePipeline(config, "Git Submodule Sync")
        
        # Step 1: Sync submodule URLs
        pipeline.add_step(PipelineStep(
            name="sync_submodule_urls",
            log_filename="submodule_sync.log",
            qc_func=GitPipelineFactory._sync_submodules,
            input_key="repo_root",
            run_mode="global"
        ))
        
        return pipeline
    
    @staticmethod
    def create_workspace_push_pipeline(config: Any = None) -> BasePipeline:
        """Create a workspace push pipeline."""
        # Create minimal config for Git pipelines if none provided
        if config is None:
            from scriptcraft.common.core.config import Config
            config = Config()
            config.workspace.domains = ["default"]  # Minimal domain for pipeline validation
        
        pipeline = BasePipeline(config, "Git Workspace Push")
        
        # Step 1: Check Git status
        pipeline.add_step(PipelineStep(
            name="check_git_status",
            log_filename="git_status.log",
            qc_func=GitPipelineFactory._check_git_status,
            input_key="repo_root",
            run_mode="global"
        ))
        
        # Step 2: Push workspace
        pipeline.add_step(PipelineStep(
            name="push_workspace",
            log_filename="workspace_push.log",
            qc_func=GitPipelineFactory._push_workspace,
            input_key="repo_root",
            run_mode="global"
        ))
        
        return pipeline
    
    @staticmethod
    def create_full_git_sync_pipeline(config: Any = None) -> BasePipeline:
        """Create a full Git sync pipeline (submodules + workspace)."""
        # Create minimal config for Git pipelines if none provided
        if config is None:
            from scriptcraft.common.core.config import Config
            config = Config()
            config.workspace.domains = ["default"]  # Minimal domain for pipeline validation
        
        pipeline = BasePipeline(config, "Full Git Sync")
        
        # Step 1: Sync submodules
        submodule_pipeline = GitPipelineFactory.create_submodule_sync_pipeline(config)
        for step in submodule_pipeline.steps:
            pipeline.add_step(step)
        
        # Step 2: Push workspace
        workspace_pipeline = GitPipelineFactory.create_workspace_push_pipeline(config)
        for step in workspace_pipeline.steps:
            pipeline.add_step(step)
        
        return pipeline
    
    @staticmethod
    def create_pypi_test_pipeline(config: Any = None) -> BasePipeline:
        """Create a PyPI test pipeline."""
        # Create minimal config for pipelines if none provided
        if config is None:
            from scriptcraft.common.core.config import Config
            config = Config()
            config.workspace.domains = ["default"]  # Minimal domain for pipeline validation
        
        pipeline = BasePipeline(config, "PyPI Test")
        
        # Step 1: Validate package
        pipeline.add_step(PipelineStep(
            name="validate_package",
            log_filename="package_validation.log",
            qc_func=GitPipelineFactory._validate_package,
            input_key="package_root",
            run_mode="global"
        ))
        
        # Step 2: Build package
        pipeline.add_step(PipelineStep(
            name="build_package",
            log_filename="package_build.log",
            qc_func=GitPipelineFactory._build_package,
            input_key="package_root",
            run_mode="global"
        ))
        
        # Step 3: Test upload
        pipeline.add_step(PipelineStep(
            name="test_upload",
            log_filename="pypi_test.log",
            qc_func=GitPipelineFactory._test_upload,
            input_key="package_root",
            run_mode="global"
        ))
        
        return pipeline
    
    @staticmethod
    def create_pypi_release_pipeline(config: Any = None) -> BasePipeline:
        """Create a PyPI release pipeline."""
        # Create minimal config for pipelines if none provided
        if config is None:
            from scriptcraft.common.core.config import Config
            config = Config()
            config.workspace.domains = ["default"]  # Minimal domain for pipeline validation
        
        pipeline = BasePipeline(config, "PyPI Release")
        
        # Step 1: Validate package
        pipeline.add_step(PipelineStep(
            name="validate_package",
            log_filename="package_validation.log",
            qc_func=GitPipelineFactory._validate_package,
            input_key="package_root",
            run_mode="global"
        ))
        
        # Step 2: Build package
        pipeline.add_step(PipelineStep(
            name="build_package",
            log_filename="package_build.log",
            qc_func=GitPipelineFactory._build_package,
            input_key="package_root",
            run_mode="global"
        ))
        
        # Step 3: Release upload
        pipeline.add_step(PipelineStep(
            name="release_upload",
            log_filename="pypi_release.log",
            qc_func=GitPipelineFactory._release_upload,
            input_key="package_root",
            run_mode="global"
        ))
        
        return pipeline

# Convenience functions for easy pipeline creation
def create_submodule_sync_pipeline(config: Any = None) -> BasePipeline:
    """Create a submodule sync pipeline."""
    return GitPipelineFactory.create_submodule_sync_pipeline(config)

def create_workspace_push_pipeline(config: Any = None) -> BasePipeline:
    """Create a workspace push pipeline."""
    return GitPipelineFactory.create_workspace_push_pipeline(config)

def create_full_git_sync_pipeline(config: Any = None) -> BasePipeline:
    """Create a full Git sync pipeline."""
    return GitPipelineFactory.create_full_git_sync_pipeline(config)

def create_pypi_test_pipeline(config: Any = None) -> BasePipeline:
    """Create a PyPI test pipeline."""
    return GitPipelineFactory.create_pypi_test_pipeline(config)

def create_pypi_release_pipeline(config: Any = None) -> BasePipeline:
    """Create a PyPI release pipeline."""
    return GitPipelineFactory.create_pypi_release_pipeline(config)
