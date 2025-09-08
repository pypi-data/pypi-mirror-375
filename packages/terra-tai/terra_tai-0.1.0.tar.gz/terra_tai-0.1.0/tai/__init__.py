"""
Terra Command AI - A natural language shell command tool with AI

Terra Command AI allows you to execute shell commands using natural language instructions,
with optional AI-powered command generation for enhanced capabilities.
"""

__version__ = "0.1.0"
__author__ = "Terra AGI"
__email__ = "contact@terra-agi.com"
__license__ = "MIT"

from .core import CommandInterpreter, TerraCommand
from .config import Settings
from .cli import main

__all__ = [
    "CommandInterpreter",
    "TerraCommand",
    "Settings",
    "main",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]
