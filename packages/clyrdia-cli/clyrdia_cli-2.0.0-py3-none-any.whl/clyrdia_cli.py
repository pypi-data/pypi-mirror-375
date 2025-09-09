#!/usr/bin/env python3
"""
Clyrdia CLI - Main entry point for console script execution
"""

import sys
import os

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and run the CLI app directly
from clyrdia.cli import app

def main():
    """Main entry point for clyrdia-cli console script"""
    sys.exit(app())

if __name__ == "__main__":
    main()
