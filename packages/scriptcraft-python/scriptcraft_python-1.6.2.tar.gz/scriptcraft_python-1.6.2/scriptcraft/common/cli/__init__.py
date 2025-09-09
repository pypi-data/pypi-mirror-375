"""
Centralized CLI utilities for consistent command-line interfaces.
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .argument_parsers import *
from .main_runner import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Argument parsing
#     'ArgumentGroups', 'ParserFactory', 'ArgumentValidator',
#     'create_standard_main_function', 'parse_pipeline_args',
#     'parse_tool_args', 'parse_standard_tool_args',
#     'parse_dictionary_workflow_args', 'parse_main_args',
#     # Main runner
#     'main'
# ]

def main() -> None:
    """Main entry point for ScriptCraft CLI - Industry Standard Interface."""
    import argparse
    import sys
    from pathlib import Path
    
    # Create main parser
    parser = argparse.ArgumentParser(
        prog="scriptcraft",
        description="ScriptCraft - Research data processing tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scriptcraft list                    # List all available tools and pipelines
  scriptcraft rhq_form_autofiller     # Run a specific tool
  scriptcraft data_quality            # Run a specific pipeline
  scriptcraft --help                  # Show this help message
  scriptcraft --version               # Show version

For more information, visit: https://github.com/your-org/scriptcraft
        """
    )
    
    # Add version option
    from scriptcraft._version import get_version
    parser.add_argument("--version", action="version", version=f"ScriptCraft {get_version()}")
    
    # Parse arguments - allow any command
    args, unknown = parser.parse_known_args()
    
    # Handle commands
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h', '--version']):
        handle_list_command()
    elif len(sys.argv) == 2 and sys.argv[1] == 'list':
        handle_list_command()
    else:
        # Try to run as tool or pipeline
        command_name = sys.argv[1]
        handle_direct_command(command_name)


def handle_list_command() -> None:
    """Handle the --list command."""
    from scriptcraft.common.registry import get_available_tool_instances
    from scriptcraft.common.core.config import Config
    
    print("🚀 ScriptCraft - Available Tools and Pipelines")
    print("=" * 50)
    
    # List tools
    print("\n📋 Available Tools:")
    tools = get_available_tool_instances()
    for tool_name, tool_instance in tools.items():
        description = getattr(tool_instance, 'description', 'No description')
        print(f"  🔧 {tool_name}: {description}")
    
    # List pipelines (if config available)
    try:
        config = Config()
        if hasattr(config, 'pipelines') and config.pipelines:
            print("\n🔷 Available Pipelines:")
            for pipeline_name, pipeline_config in config.pipelines.items():
                description = pipeline_config.get('description', 'No description')
                print(f"  🔷 {pipeline_name}: {description}")
    except Exception:
        print("\n⚠️  Pipeline information not available (config not loaded)")
    
    print("\n💡 Usage Examples:")
    print("  scriptcraft rhq_form_autofiller")
    print("  scriptcraft data_quality")
    print("  scriptcraft --help")


def handle_direct_command(command_name: str) -> None:
    """Handle direct command execution (industry standard pattern)."""
    from scriptcraft.common.registry import get_available_tool_instances
    from scriptcraft.common.core.config import Config
    from scriptcraft.common.pipeline import BasePipeline
    from scriptcraft.common.logging import log_and_print
    
    # First try as a tool
    tools = get_available_tool_instances()
    if command_name in tools:
        log_and_print(f"🚀 Running tool: {command_name}")
        try:
            tool_instance = tools[command_name]
            success = tool_instance.run()
            if success:
                log_and_print(f"✅ Tool '{command_name}' completed successfully")
            else:
                log_and_print(f"❌ Tool '{command_name}' failed", level="error")
                sys.exit(1)
        except Exception as e:
            log_and_print(f"❌ Error running tool '{command_name}': {e}", level="error")
            sys.exit(1)
        return
    
    # Then try as a pipeline
    try:
        config = Config()
        if hasattr(config, 'pipelines') and command_name in config.pipelines:
            log_and_print(f"🚀 Running pipeline: {command_name}")
            pipeline = BasePipeline(config, command_name)
            success = pipeline.run()
            if success:
                log_and_print(f"✅ Pipeline '{command_name}' completed successfully")
            else:
                log_and_print(f"❌ Pipeline '{command_name}' failed", level="error")
                sys.exit(1)
            return
    except Exception:
        pass
    
    # Command not found
    log_and_print(f"❌ Command '{command_name}' not found", level="error")
    log_and_print("Available commands:", level="info")
    log_and_print("  Tools:", level="info")
    for name in tools.keys():
        log_and_print(f"    - {name}", level="info")
    
    try:
        config = Config()
        if hasattr(config, 'pipelines'):
            log_and_print("  Pipelines:", level="info")
            for name in config.pipelines.keys():
                log_and_print(f"    - {name}", level="info")
    except Exception:
        pass
    
    log_and_print("", level="info")
    log_and_print("Use 'scriptcraft list' to see all available commands", level="info")
    sys.exit(1) 