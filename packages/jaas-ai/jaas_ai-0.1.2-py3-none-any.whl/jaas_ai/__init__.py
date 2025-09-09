"""
JaaS API Python SDK

A Python SDK for interacting with the JaaS AI evaluation API.
"""

# Import version info first
from .version import __version__, __version_info__

# Import the main client class
try:
    from .main import jaas_client
except ImportError as e:
    # If there's an import error, provide a helpful message
    raise ImportError(
        f"Failed to import jaas_client from main module: {e}. "
        "Please check that the main.py file is properly formatted and contains the jaas_client class."
    ) from e

__all__ = [
    "jaas_client",
    "__version__",
    "__version_info__",
]