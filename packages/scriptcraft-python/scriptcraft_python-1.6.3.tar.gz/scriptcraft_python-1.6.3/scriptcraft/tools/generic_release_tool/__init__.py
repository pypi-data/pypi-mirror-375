"""
Generic Release Tool

A workspace-agnostic release tool that can be used anywhere.
Uses the pipeline system for flexible, composable release workflows.
"""

from .main import GenericReleaseTool

__all__ = ["GenericReleaseTool"]
