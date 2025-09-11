"""
datapress-client: Deprecated compatibility wrapper

This package has been deprecated in favor of the 'datapress' package.
This module re-exports everything from 'datapress' for backwards compatibility.

Please update your imports to use 'datapress' directly:
    
    # Old (deprecated):
    from datapress_client import something
    
    # New (recommended):
    from datapress import something
"""

import warnings

warnings.warn(
    "datapress-client is deprecated. Use 'datapress' instead. "
    "This package will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

try:
    from datapress import *
except ImportError as e:
    raise ImportError(
        "Failed to import from 'datapress'. Make sure 'datapress' is installed. "
        f"Original error: {e}"
    ) from e