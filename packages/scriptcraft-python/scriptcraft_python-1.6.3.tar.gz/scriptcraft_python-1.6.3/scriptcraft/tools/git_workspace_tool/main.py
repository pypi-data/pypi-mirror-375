#!/usr/bin/env python3
"""
Git Workspace Tool

Handles Git workspace operations.
Follows ScriptCraft tool patterns for reusability.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import scriptcraft.common as cu

class GitWorkspaceTool(cu.BaseTool):
    """Tool for Git workspace operations."""
    
    def __init__(self):
        super().__init__(
            name="Git Workspace Tool",
            description="Handles Git workspace operations"
        )
    
    def run(self, operation: str = "push", **kwargs) -> bool:
        """Run Git workspace operations."""
        cu.log_and_print(f"🚀 Starting Git workspace {operation} operation...")
        
        if operation == "push":
            return self._push_workspace(**kwargs)
        elif operation == "pull":
            return self._pull_workspace(**kwargs)
        elif operation == "status":
            return self._check_status(**kwargs)
        elif operation == "commit":
            return self._commit_changes(**kwargs)
        elif operation == "tag":
            return self._create_tag(**kwargs)
        else:
            cu.log_and_print(f"❌ Unknown operation: {operation}", level="error")
            return False
    
    def _push_workspace(self, **kwargs) -> bool:
        """Push workspace changes."""
        cu.log_and_print("📤 Pushing workspace changes...")
        
        if not self._is_git_repo():
            cu.log_and_print("❌ Not a Git repository", level="error")
            return False
        
        # Check for uncommitted changes
        if not self._check_status():
            cu.log_and_print("❌ Uncommitted changes found", level="error")
            return False
        
        # Push commits
        if not self._run_command("git push", "Pushing commits"):
            return False
        
        # Push tags if any
        if not self._run_command("git push --tags", "Pushing tags"):
            return False
        
        cu.log_and_print("✅ Workspace pushed successfully")
        return True
    
    def _pull_workspace(self, **kwargs) -> bool:
        """Pull workspace changes."""
        cu.log_and_print("📥 Pulling workspace changes...")
        
        if not self._is_git_repo():
            cu.log_and_print("❌ Not a Git repository", level="error")
            return False
        
        # Pull changes
        if not self._run_command("git pull", "Pulling changes"):
            return False
        
        cu.log_and_print("✅ Workspace pulled successfully")
        return True
    
    def _check_status(self, **kwargs) -> bool:
        """Check Git repository status."""
        cu.log_and_print("🔍 Checking Git status...")
        
        if not self._is_git_repo():
            cu.log_and_print("❌ Not a Git repository", level="error")
            return False
        
        # Check for uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            cu.log_and_print("⚠️ Uncommitted changes found:", level="warning")
            cu.log_and_print(result.stdout, level="warning")
            return False
        
        cu.log_and_print("✅ Git repository is clean")
        return True
    
    def _commit_changes(self, message: str = None, **kwargs) -> bool:
        """Commit changes to workspace."""
        cu.log_and_print("💾 Committing changes...")
        
        if not self._is_git_repo():
            cu.log_and_print("❌ Not a Git repository", level="error")
            return False
        
        # Check for changes to commit
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        if not result.stdout.strip():
            cu.log_and_print("ℹ️ No changes to commit")
            return True
        
        # Add all changes
        if not self._run_command("git add .", "Adding changes"):
            return False
        
        # Commit changes
        commit_message = message or "Auto-commit from ScriptCraft"
        if not self._run_command(f'git commit -m "{commit_message}"', "Committing changes"):
            return False
        
        cu.log_and_print("✅ Changes committed successfully")
        return True
    
    def _create_tag(self, version: str = None, **kwargs) -> bool:
        """Create a Git tag."""
        if not version:
            cu.log_and_print("❌ Version required for tagging", level="error")
            return False
        
        cu.log_and_print(f"🏷️ Creating Git tag: v{version}")
        
        if not self._is_git_repo():
            cu.log_and_print("❌ Not a Git repository", level="error")
            return False
        
        # Create tag
        if not self._run_command(f"git tag v{version}", f"Creating tag v{version}"):
            return False
        
        cu.log_and_print(f"✅ Git tag v{version} created")
        return True
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a Git repository."""
        return Path(".git").exists()
    
    def _run_command(self, cmd: str, description: str) -> bool:
        """Run a command with proper encoding."""
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
                return True
            else:
                cu.log_and_print(f"❌ {description} - FAILED", level="error")
                cu.log_and_print(f"Error: {result.stderr}", level="error")
                return False
        except Exception as e:
            cu.log_and_print(f"❌ {description} - EXCEPTION: {e}", level="error")
            return False
