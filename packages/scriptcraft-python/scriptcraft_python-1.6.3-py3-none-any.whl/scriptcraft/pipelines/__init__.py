"""
ScriptCraft Pipelines Package

This package provides domain-specific pipeline implementations that use
the consolidated ScriptCraft pipeline system from scriptcraft.common.pipeline.

Available pipelines:
- release_pipelines.py: Release and deployment pipelines
- git_pipelines.py: Git operation pipelines

All pipelines follow ScriptCraft patterns and use the centralized
pipeline infrastructure for consistency and DRY compliance.
"""

# Import domain-specific pipelines
from . import release_pipelines
from . import git_pipelines

# Re-export the consolidated pipeline system for convenience
from scriptcraft.common.pipeline import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Domain-specific pipelines
#     'release_pipelines', 'git_pipelines',
#     # Consolidated pipeline system
#     'BasePipeline', 'PipelineStep', 'PipelineFactory',
#     'make_step', 'validate_pipelines', 'run_pipeline'
# ]
