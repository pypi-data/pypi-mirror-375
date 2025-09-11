"""
TOXO - No-Code LLM Training Platform
Public Python Package for .toxo file support

This package allows users to seamlessly use .toxo files created on the TOXO platform.

Usage:
    from toxo import ToxoLayer
    
    # Load your trained model
    layer = ToxoLayer.load("your_model.toxo")
    
    # Set your API key
    layer.setup_api_key("your_api_key_here")
    
    # Query your AI expert
    response = layer.query("Your question here")
"""

__version__ = "1.0.0"
__author__ = "ToxoTune"
__email__ = "support@toxotune.com"
__license__ = "Proprietary"

# Import the main user-facing class
from .core import ToxoLayer

# Import utility functions
from .utils import get_version, check_dependencies

# Public API
__all__ = [
    "ToxoLayer",
    "get_version", 
    "check_dependencies",
    "__version__",
]

# Version check and welcome message
def _check_environment():
    """Check if the environment is properly set up."""
    import sys
    if sys.version_info < (3, 8):
        raise RuntimeError("TOXO requires Python 3.8 or higher")

# Run environment check on import
_check_environment()

# Optional: Print welcome message (can be disabled with environment variable)
import os
if not os.environ.get("TOXO_QUIET", False):
    print(f"🧠 TOXO v{__version__} - No-Code LLM Training Platform")
    print("   Visit https://toxotune.com to create your AI experts")