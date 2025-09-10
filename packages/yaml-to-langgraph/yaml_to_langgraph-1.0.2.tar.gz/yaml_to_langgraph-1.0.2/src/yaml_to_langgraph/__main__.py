"""
Entry point for running the converter as a module.

Usage: python -m yaml_to_langgraph <yaml_file>
"""

from .cli import main

if __name__ == "__main__":
    main()
