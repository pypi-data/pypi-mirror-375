"""Auto-import all tools for registration with FastMCP."""
import os
import importlib
from pathlib import Path
import logging

logger = logging.getLogger("voice-mode")

# Get the directory containing this file
tools_dir = Path(__file__).parent

# Check if we should only load specific tools
# This can be set in .voicemode.env, shell environment, or .mcp.json
allowed_tools = os.environ.get("VOICEMODE_TOOLS", "").strip()

if allowed_tools:
    # Only load specified tools (comma-separated list)
    tool_list = [t.strip() for t in allowed_tools.split(",")]
    
    logger.info(f"Selective tool loading enabled. Loading only: {', '.join(tool_list)}")
    
    for tool_name in tool_list:
        tool_file = tools_dir / f"{tool_name}.py"
        if tool_file.exists():
            logger.debug(f"Loading tool: {tool_name}")
            importlib.import_module(f".{tool_name}", package=__name__)
        else:
            logger.warning(f"Tool module not found: {tool_name}.py")
else:
    # Default behavior: load all tools
    logger.info("Loading all available tools (set VOICEMODE_TOOLS to limit)")
    
    # Import all Python files in this directory (except __init__.py)
    for file in tools_dir.glob("*.py"):
        if file.name != "__init__.py" and not file.name.startswith("_"):
            module_name = file.stem
            logger.debug(f"Loading tool: {module_name}")
            importlib.import_module(f".{module_name}", package=__name__)

    # Import all service tools from subdirectories
    services_dir = tools_dir / "services"
    if services_dir.exists():
        for service_dir in services_dir.iterdir():
            if service_dir.is_dir() and not service_dir.name.startswith("_"):
                # Import all Python files in each service directory
                for file in service_dir.glob("*.py"):
                    if file.name != "__init__.py" and not file.name.startswith("_") and file.name != "helpers.py":
                        module_path = f".services.{service_dir.name}.{file.stem}"
                        logger.debug(f"Loading service tool: {module_path}")
                        importlib.import_module(module_path, package=__name__)