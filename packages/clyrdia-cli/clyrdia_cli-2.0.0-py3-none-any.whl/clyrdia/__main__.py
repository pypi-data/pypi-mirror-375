#!/usr/bin/env python3
"""
Clyrdia CLI - Main entry point for direct execution
"""

import sys
from .cli import app

if __name__ == "__main__":
    sys.exit(app())
