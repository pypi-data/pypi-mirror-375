#!/usr/bin/env python3
"""
Git Submodule Tool

Handles Git submodule operations.
Follows ScriptCraft tool patterns for reusability.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import scriptcraft.common as cu

class GitSubmoduleTool(cu.BaseTool):
    """Tool for Git submodule operations."""
    
    def __init__(self):
        super().__init__(
            name="Git Submodule Tool",
            description="Handles Git submodule operations"
        )
    
    def run(self, operation: str = "sync", **kwargs) -> bool:
        """Run Git submodule operations."""
        cu.log_and_print(f"🚀 Starting Git submodule {operation} operation...")
        
        if operation == "sync":
            return self._sync_submodules(**kwargs)
        elif operation == "push":
            return self._push_submodules(**kwargs)
        elif operation == "pull":
            return self._pull_submodules(**kwargs)
        elif operation == "update":
            return self._update_submodules(**kwargs)
        else:
            cu.log_and_print(f"❌ Unknown operation: {operation}", level="error")
            return False
    
    def _sync_submodules(self, **kwargs) -> bool:
        """Sync submodules with their remotes."""
        cu.log_and_print("🔄 Syncing submodules...")
        
        # Check if we're in a Git repository
        if not self._is_git_repo():
            cu.log_and_print("❌ Not a Git repository", level="error")
            return False
        
        # Check if there are submodules
        if not self._has_submodules():
            cu.log_and_print("ℹ️ No submodules found")
            return True
        
        # Sync submodules
        if not self._run_command("git submodule sync", "Syncing submodule URLs"):
            return False
        
        # Update submodules
        if not self._run_command("git submodule update --init --recursive", "Updating submodules"):
            return False
        
        cu.log_and_print("✅ Submodules synced successfully")
        return True
    
    def _push_submodules(self, **kwargs) -> bool:
        """Push submodule changes."""
        cu.log_and_print("📤 Pushing submodule changes...")
        
        if not self._is_git_repo():
            cu.log_and_print("❌ Not a Git repository", level="error")
            return False
        
        if not self._has_submodules():
            cu.log_and_print("ℹ️ No submodules found")
            return True
        
        # Push each submodule
        submodules = self._get_submodules()
        for submodule in submodules:
            cu.log_and_print(f"📤 Pushing submodule: {submodule}")
            if not self._run_command(f"git submodule foreach 'git push origin HEAD'", 
                                   f"Pushing {submodule}"):
                return False
        
        cu.log_and_print("✅ Submodules pushed successfully")
        return True
    
    def _pull_submodules(self, **kwargs) -> bool:
        """Pull submodule changes."""
        cu.log_and_print("📥 Pulling submodule changes...")
        
        if not self._is_git_repo():
            cu.log_and_print("❌ Not a Git repository", level="error")
            return False
        
        if not self._has_submodules():
            cu.log_and_print("ℹ️ No submodules found")
            return True
        
        # Pull each submodule
        if not self._run_command("git submodule foreach 'git pull origin HEAD'", 
                               "Pulling submodules"):
            return False
        
        cu.log_and_print("✅ Submodules pulled successfully")
        return True
    
    def _update_submodules(self, **kwargs) -> bool:
        """Update submodules to latest commits."""
        cu.log_and_print("🔄 Updating submodules...")
        
        if not self._is_git_repo():
            cu.log_and_print("❌ Not a Git repository", level="error")
            return False
        
        if not self._has_submodules():
            cu.log_and_print("ℹ️ No submodules found")
            return True
        
        # Update submodules
        if not self._run_command("git submodule update --remote --merge", 
                               "Updating submodules to latest"):
            return False
        
        cu.log_and_print("✅ Submodules updated successfully")
        return True
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a Git repository."""
        return Path(".git").exists()
    
    def _has_submodules(self) -> bool:
        """Check if repository has submodules."""
        result = subprocess.run(["git", "submodule", "status"], 
                              capture_output=True, text=True)
        return bool(result.stdout.strip())
    
    def _get_submodules(self) -> list:
        """Get list of submodules."""
        result = subprocess.run(["git", "submodule", "status"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return [line.split()[1] for line in result.stdout.strip().split('\n') if line.strip()]
        return []
    
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
