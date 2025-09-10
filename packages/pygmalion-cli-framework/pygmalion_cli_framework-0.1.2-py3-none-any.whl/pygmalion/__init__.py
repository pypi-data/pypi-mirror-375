"""
Pygmalion CLI Framework - A micro-framework for building adaptive CLI interfaces.

Pygmalion CLI Framework transforms static command-line interfaces into self-evolving CLIs
that learn from user behavior and adapt over time.
"""

__version__ = "0.1.2"
__author__ = "Pygmalion CLI Framework Developers"
__email__ = "developers@pygmalion-cli-framework.dev"

from .core import PygmalionApp
from .decorators import command, group, set_default_app
from .tracker import CommandTracker
from .alias import AliasManager
from .help import AdaptiveHelp
from .storage import StorageBackend, JSONStorage, SQLiteStorage

__all__ = [
    "PygmalionApp",
    "set_default_app",
    "command",
    "group", 
    "CommandTracker",
    "AliasManager",
    "AdaptiveHelp",
    "StorageBackend",
    "JSONStorage",
    "SQLiteStorage",
]
