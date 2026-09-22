# tools/__init__.py
import importlib
import os
import pkgutil

# Get the current directory of this __init__.py file
package_dir = os.path.dirname(__file__)

ALL_GROQ_TOOLS = []
TOOL_REGISTRY = {}

# Iterate through all .py files in this folder dynamically
for _, module_name, _ in pkgutil.iter_modules([package_dir]):
    # Use explicit relative import (e.g., .git_lister)
    module = importlib.import_module(f".{module_name}", package=__name__)
    
    # Check if the module exposes the required Groq layout
    if hasattr(module, "GROQ_TOOL_SPEC") and hasattr(module, "execute"):
        ALL_GROQ_TOOLS.append(module.GROQ_TOOL_SPEC)
        
        # Map the tool name to its execution code
        tool_name = module.GROQ_TOOL_SPEC["function"]["name"]
        TOOL_REGISTRY[tool_name] = module.execute
