#!/usr/bin/env python3
"""
Release CLI

Simple command-line interface for ScriptCraft release tools.
Provides easy access to release workflows for end users.
"""

import argparse
import sys
from pathlib import Path

import scriptcraft.common as cu
from scriptcraft.pipelines.git_pipelines import (
    create_pypi_test_pipeline,
    create_pypi_release_pipeline,
    create_submodule_sync_pipeline,
    create_workspace_push_pipeline,
    create_full_git_sync_pipeline
)
from scriptcraft.tools.pypi_release_tool import PyPIReleaseTool
from scriptcraft.tools.git_workspace_tool import GitWorkspaceTool
from scriptcraft.tools.git_submodule_tool import GitSubmoduleTool

def pypi_test(args):
    """Run PyPI test workflow."""
    cu.log_and_print("🧪 Running PyPI test workflow...")
    
    if args.pipeline:
        # Use pipeline
        pipeline = create_pypi_test_pipeline()
        success = pipeline.run()
    else:
        # Use individual tool
        tool = PyPIReleaseTool()
        success = tool.run(operation="test")
    
    if success:
        cu.log_and_print("✅ PyPI test completed successfully")
    else:
        cu.log_and_print("❌ PyPI test failed")
        sys.exit(1)

def pypi_release(args):
    """Run PyPI release workflow."""
    cu.log_and_print("🚀 Running PyPI release workflow...")
    
    if args.pipeline:
        # Use pipeline
        pipeline = create_pypi_release_pipeline()
        success = pipeline.run()
    else:
        # Use individual tool
        tool = PyPIReleaseTool()
        success = tool.run(operation="release")
    
    if success:
        cu.log_and_print("✅ PyPI release completed successfully")
    else:
        cu.log_and_print("❌ PyPI release failed")
        sys.exit(1)

def git_sync(args):
    """Run Git sync workflow."""
    cu.log_and_print("🔄 Running Git sync workflow...")
    
    if args.pipeline:
        # Use pipeline
        pipeline = create_full_git_sync_pipeline()
        success = pipeline.run()
    else:
        # Use individual tools
        submodule_tool = GitSubmoduleTool()
        workspace_tool = GitWorkspaceTool()
        
        # Sync submodules first
        if submodule_tool.run(operation="sync"):
            # Then push workspace
            success = workspace_tool.run(operation="push")
        else:
            success = False
    
    if success:
        cu.log_and_print("✅ Git sync completed successfully")
    else:
        cu.log_and_print("❌ Git sync failed")
        sys.exit(1)

def git_status(args):
    """Check Git status."""
    cu.log_and_print("🔍 Checking Git status...")
    
    tool = GitWorkspaceTool()
    success = tool.run(operation="status")
    
    if not success:
        sys.exit(1)

def full_release(args):
    """Run full release workflow (PyPI + Git)."""
    cu.log_and_print("🎯 Running full release workflow...")
    
    # Step 1: PyPI test
    cu.log_and_print("Step 1: PyPI test...")
    if not PyPIReleaseTool().run(operation="test"):
        cu.log_and_print("❌ PyPI test failed, aborting release")
        sys.exit(1)
    
    # Step 2: PyPI release
    cu.log_and_print("Step 2: PyPI release...")
    if not PyPIReleaseTool().run(operation="release"):
        cu.log_and_print("❌ PyPI release failed, aborting release")
        sys.exit(1)
    
    # Step 3: Git sync
    cu.log_and_print("Step 3: Git sync...")
    if not create_full_git_sync_pipeline().run():
        cu.log_and_print("❌ Git sync failed")
        sys.exit(1)
    
    cu.log_and_print("🎉 Full release completed successfully!")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ScriptCraft Release CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scriptcraft-release pypi-test              # Test PyPI upload
  scriptcraft-release pypi-release           # Release to PyPI
  scriptcraft-release git-sync               # Sync Git repository
  scriptcraft-release git-status             # Check Git status
  scriptcraft-release full-release           # Full release workflow
  scriptcraft-release pypi-test --pipeline   # Use pipeline instead of tool
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # PyPI test command
    pypi_test_parser = subparsers.add_parser('pypi-test', help='Test PyPI upload')
    pypi_test_parser.add_argument('--pipeline', action='store_true', 
                                 help='Use pipeline instead of individual tool')
    pypi_test_parser.set_defaults(func=pypi_test)
    
    # PyPI release command
    pypi_release_parser = subparsers.add_parser('pypi-release', help='Release to PyPI')
    pypi_release_parser.add_argument('--pipeline', action='store_true',
                                    help='Use pipeline instead of individual tool')
    pypi_release_parser.set_defaults(func=pypi_release)
    
    # Git sync command
    git_sync_parser = subparsers.add_parser('git-sync', help='Sync Git repository')
    git_sync_parser.add_argument('--pipeline', action='store_true',
                                help='Use pipeline instead of individual tools')
    git_sync_parser.set_defaults(func=git_sync)
    
    # Git status command
    git_status_parser = subparsers.add_parser('git-status', help='Check Git status')
    git_status_parser.set_defaults(func=git_status)
    
    # Full release command
    full_release_parser = subparsers.add_parser('full-release', help='Full release workflow')
    full_release_parser.set_defaults(func=full_release)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        cu.log_and_print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        cu.log_and_print(f"❌ Unexpected error: {e}", level="error")
        sys.exit(1)

if __name__ == "__main__":
    main()
