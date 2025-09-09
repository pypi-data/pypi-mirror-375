"""
Sheller - AI-Powered Terminal Command Assistant

A terminal application that converts natural language requests into executable commands.
Supports Windows with intelligent command translation.
"""

__version__ = "1.0.0"
__author__ = "Sheller Team"
__email__ = "team@sheller.com"

from .main import main, TerminalUI, CommandContext

__all__ = ["main", "TerminalUI", "CommandContext"]
