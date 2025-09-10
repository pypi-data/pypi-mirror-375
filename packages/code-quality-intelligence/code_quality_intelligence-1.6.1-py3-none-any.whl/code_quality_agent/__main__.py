#!/usr/bin/env python3
"""
Entry point for running the Code Quality Intelligence Agent as a module.

Usage: python -m code_quality_agent [commands]
"""

from .cli import cli

if __name__ == '__main__':
    cli()
