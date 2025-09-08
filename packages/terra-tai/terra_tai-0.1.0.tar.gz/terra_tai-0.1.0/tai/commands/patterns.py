"""
Command Patterns Module for Terra Command AI

This module contains predefined command patterns that serve as fallbacks
when AI is not available or fails to generate appropriate commands.
"""

from typing import Dict


class CommandPatterns:
    """
    Collection of predefined command patterns for various operations.

    This class provides a comprehensive set of command mappings that work
    across different operating systems and can be used as fallbacks.
    """

    # File operations
    FILE_OPERATIONS = {
        'list files': 'ls -la',
        'show directory': 'ls -la',
        'list directory': 'ls -la',
        'what files are here': 'ls -la',
        'see files': 'ls -la',
        'long list': 'ls -la',
        'detailed list': 'ls -la',
    }

    # Directory navigation
    DIRECTORY_NAVIGATION = {
        'go home': 'cd ~',
        'go to home': 'cd ~',
        'go back': 'cd ..',
        'go up': 'cd ..',
        'go to parent': 'cd ..',
        'parent directory': 'cd ..',
        'up one level': 'cd ..',
    }

    # System information
    SYSTEM_INFO = {
        'who am i': 'whoami',
        'current user': 'whoami',
        'system info': 'uname -a',
        'what system': 'uname -a',
        'kernel info': 'uname -a',
        'os info': 'uname -a',
    }

    # Process management
    PROCESS_MANAGEMENT = {
        'process list': 'ps aux',
        'running processes': 'ps aux',
        'show processes': 'ps aux',
        'cpu info': 'top -n 1',
        'memory info': 'free -h',
        'memory usage': 'free -h',
        'disk usage': 'df -h',
        'disk space': 'df -h',
        'free space': 'df -h',
    }

    # Git operations
    GIT_OPERATIONS = {
        'git status': 'git status',
        'git log': 'git log --oneline -10',
        'git branch': 'git branch',
        'current branch': 'git branch --show-current',
        'git diff': 'git diff',
        'git changes': 'git diff',
    }

    # Network operations
    NETWORK_OPERATIONS = {
        'ping google': 'ping -c 4 google.com',
        'network status': 'ifconfig',
        'wifi info': 'iwconfig',
        'internet connection': 'ping -c 4 8.8.8.8',
        'network interfaces': 'ifconfig',
    }

    def __init__(self):
        """Initialize the command patterns collection."""
        self._patterns = {}
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load all command patterns into a single dictionary."""
        self._patterns.update(self.FILE_OPERATIONS)
        self._patterns.update(self.DIRECTORY_NAVIGATION)
        self._patterns.update(self.SYSTEM_INFO)
        self._patterns.update(self.PROCESS_MANAGEMENT)
        self._patterns.update(self.GIT_OPERATIONS)
        self._patterns.update(self.NETWORK_OPERATIONS)

    def get_pattern(self, instruction: str) -> str:
        """
        Get the command pattern for a given instruction.

        Args:
            instruction: The natural language instruction

        Returns:
            str: The corresponding shell command, or empty string if not found
        """
        return self._patterns.get(instruction.lower().strip(), '')

    def get_all_patterns(self) -> Dict[str, str]:
        """
        Get all available command patterns.

        Returns:
            Dict[str, str]: Dictionary of instruction -> command mappings
        """
        return self._patterns.copy()

    def get_pattern_count(self) -> int:
        """
        Get the total number of available patterns.

        Returns:
            int: Number of command patterns
        """
        return len(self._patterns)

    def search_patterns(self, query: str) -> Dict[str, str]:
        """
        Search for patterns containing the query string.

        Args:
            query: Search term to look for in instructions

        Returns:
            Dict[str, str]: Matching patterns
        """
        query = query.lower()
        return {
            instruction: command
            for instruction, command in self._patterns.items()
            if query in instruction
        }
