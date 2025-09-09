"""
Clyrdia CLI - State-of-the-Art AI Benchmarking for CI/CD
"""

__version__ = "2.0.0"
__author__ = "Clyrdia Team"
__email__ = "dev@clyrdia.com"
__url__ = "https://clyrdia.com"

# Import main components for easy access
from .cli import app

__all__ = [
    "app",
    "__version__",
    "__author__",
    "__email__"
]
