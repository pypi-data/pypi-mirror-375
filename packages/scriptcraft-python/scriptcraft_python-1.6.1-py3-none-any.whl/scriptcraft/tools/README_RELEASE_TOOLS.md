# ScriptCraft Release Tools

This directory contains tools and pipelines for release operations, designed to be shipped to others via the `scriptcraft-python` package.

## 🚀 Quick Start

### Installation
```bash
pip install scriptcraft-python
```

### Basic Usage
```bash
# Test PyPI upload
scriptcraft-release pypi-test

# Release to PyPI
scriptcraft-release pypi-release

# Sync Git repository
scriptcraft-release git-sync

# Full release workflow
scriptcraft-release full-release
```

## 🛠️ Available Tools

### PyPIReleaseTool
Handles PyPI testing and release operations.

**Operations:**
- `test` - Test upload to PyPI test repository
- `release` - Release upload to PyPI
- `validate` - Validate package integrity
- `build` - Build the package

**Usage:**
```python
from scriptcraft.tools.pypi_release_tool import PyPIReleaseTool

tool = PyPIReleaseTool()
tool.run(operation="test")    # Test upload
tool.run(operation="release") # Release upload
```

### GitWorkspaceTool
Handles Git workspace operations.

**Operations:**
- `push` - Push workspace changes
- `pull` - Pull workspace changes
- `status` - Check Git repository status
- `commit` - Commit changes to workspace
- `tag` - Create a Git tag

**Usage:**
```python
from scriptcraft.tools.git_workspace_tool import GitWorkspaceTool

tool = GitWorkspaceTool()
tool.run(operation="push")    # Push changes
tool.run(operation="status")  # Check status
```

### GitSubmoduleTool
Handles Git submodule operations.

**Operations:**
- `sync` - Sync submodules with their remotes
- `push` - Push submodule changes
- `pull` - Pull submodule changes
- `update` - Update submodules to latest commits

**Usage:**
```python
from scriptcraft.tools.git_submodule_tool import GitSubmoduleTool

tool = GitSubmoduleTool()
tool.run(operation="sync")    # Sync submodules
tool.run(operation="push")    # Push submodules
```

## 🔧 Available Pipelines

### PyPI Pipelines
- `create_pypi_test_pipeline()` - Complete PyPI test workflow
- `create_pypi_release_pipeline()` - Complete PyPI release workflow

### Git Pipelines
- `create_submodule_sync_pipeline()` - Submodule sync workflow
- `create_workspace_push_pipeline()` - Workspace push workflow
- `create_full_git_sync_pipeline()` - Combined Git operations

**Usage:**
```python
from scriptcraft.pipelines.git_pipelines import create_pypi_test_pipeline

pipeline = create_pypi_test_pipeline()
pipeline.run()
```

## 📋 CLI Commands

### scriptcraft-release
Simple command-line interface for release operations.

```bash
# PyPI operations
scriptcraft-release pypi-test              # Test PyPI upload
scriptcraft-release pypi-release           # Release to PyPI

# Git operations
scriptcraft-release git-sync               # Sync Git repository
scriptcraft-release git-status             # Check Git status

# Full workflow
scriptcraft-release full-release           # Complete release workflow

# Use pipelines instead of individual tools
scriptcraft-release pypi-test --pipeline   # Use pipeline
```

### Available Commands
```bash
# List all available commands
scriptcraft-release --help

# Get help for specific command
scriptcraft-release pypi-test --help
scriptcraft-release git-sync --help
```

## 🎯 Workflow Examples

### Simple PyPI Release
```python
from scriptcraft.tools.pypi_release_tool import PyPIReleaseTool

tool = PyPIReleaseTool()
success = tool.run(operation="release")
```

### Git Sync Workflow
```python
from scriptcraft.tools.git_submodule_tool import GitSubmoduleTool
from scriptcraft.tools.git_workspace_tool import GitWorkspaceTool

# Sync submodules first
submodule_tool = GitSubmoduleTool()
if submodule_tool.run(operation="sync"):
    # Then push workspace
    workspace_tool = GitWorkspaceTool()
    workspace_tool.run(operation="push")
```

### Pipeline Workflow
```python
from scriptcraft.pipelines.git_pipelines import create_full_git_sync_pipeline

pipeline = create_full_git_sync_pipeline()
pipeline.run()
```

### Custom Workflow
```python
from scriptcraft.tools.pypi_release_tool import PyPIReleaseTool
from scriptcraft.pipelines.git_pipelines import create_full_git_sync_pipeline

# Test → Release → Git Sync
if PyPIReleaseTool().run(operation="test"):
    if PyPIReleaseTool().run(operation="release"):
        create_full_git_sync_pipeline().run()
```

## ⚙️ Configuration

All tools use the ScriptCraft configuration system:

- **Primary**: `config.yaml` at workspace root
- **Fallback**: Environment variables for distributables
- **Logging**: All logs go to `data/logs/` (if available)

### Environment Variables
- `PYTHONIOENCODING=utf-8` - Set automatically for Unicode support
- Standard Git environment variables
- Standard PyPI environment variables

## 🔍 Logging

All tools provide comprehensive logging:

- **Console output**: User-friendly messages with emojis
- **File logging**: Detailed logs to `data/logs/` (if available)
- **Error handling**: Clear error messages and recovery steps

## 🚨 Error Handling

Tools provide robust error handling:

- **Validation**: Check prerequisites before operations
- **Rollback**: Safe failure modes
- **Recovery**: Clear error messages with next steps
- **Logging**: Comprehensive error logging

## 📦 Distribution

These tools are designed to be shipped to others:

1. **Install**: `pip install scriptcraft-python`
2. **Use**: Import tools or use CLI commands
3. **Configure**: Use `config.yaml` or environment variables
4. **Run**: Execute workflows in any Python project

## 🎯 Best Practices

### For Tool Users
- Use pipelines for complex workflows
- Use individual tools for simple operations
- Always test before releasing
- Check Git status before operations

### For Tool Developers
- Follow ScriptCraft patterns (`cu.BaseTool`)
- Use `cu.log_and_print()` for user messages
- Provide comprehensive error handling
- Make tools configurable and reusable

## 🔗 Integration

These tools integrate seamlessly with:

- **ScriptCraft Common**: Configuration, logging, utilities
- **ScriptCraft Pipelines**: Composable workflows
- **ScriptCraft CLI**: Command-line interfaces
- **Existing Tools**: Can be combined with other ScriptCraft tools

## 📚 Usage Examples

### Simple CLI Usage
```bash
# Test PyPI upload
scriptcraft-release pypi-test

# Release to PyPI  
scriptcraft-release pypi-release

# Sync Git repository
scriptcraft-release git-sync

# Full release workflow
scriptcraft-release full-release
```

### Python API Usage
```python
# Individual tools
from scriptcraft.tools.pypi_release_tool import PyPIReleaseTool
tool = PyPIReleaseTool()
tool.run(operation="test")

# Pipelines
from scriptcraft.pipelines.git_pipelines import create_pypi_test_pipeline
pipeline = create_pypi_test_pipeline()
pipeline.run()
```

## 🆘 Support

- **Documentation**: This README and inline docstrings
- **Examples**: This README and inline docstrings
- **CLI Help**: `scriptcraft-release --help`
- **Tool Discovery**: `python -c "from scriptcraft.tools import get_available_tools; print(get_available_tools())"`
