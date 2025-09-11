# datapress-client

**⚠️ DEPRECATED: This package has been deprecated in favor of `datapress`.**

## Migration Notice

This package is now just a compatibility wrapper around the `datapress` package. 

**Please update your code to use `datapress` directly:**

```python
# Old (deprecated):
from datapress_client import something

# New (recommended):  
from datapress import something
```

## What This Package Does

This package simply re-exports everything from `datapress` and shows a deprecation warning when imported. It exists solely to provide backwards compatibility for existing code.

## Installation

```bash
pip install datapress-client==2.0.0
```

However, we strongly recommend installing `datapress` directly instead:

```bash
pip install datapress
```

## Version 2.0.0

Version 2.0.0 marks the deprecation of this package. All functionality has been moved to the `datapress` package.

## Support

For support and issues, please refer to the main `datapress` package.