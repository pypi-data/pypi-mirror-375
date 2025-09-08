"""
OS Detection Module for Terra Command AI

This module provides operating system detection and OS-specific information
to help generate appropriate shell commands for different platforms.
"""

import platform
from typing import Optional


class OSDetector:
    """
    Detects the operating system and provides OS-specific information.

    This class analyzes the current system and provides formatted OS information
    that can be used by AI models to generate appropriate shell commands.
    """

    def __init__(self) -> None:
        """Initialize the OS detector."""
        self.system = platform.system().lower()
        self.distro = self._get_distro()
        self.version = platform.version()
        self.machine = platform.machine()

    def _get_distro(self) -> str:
        """
        Get Linux distribution information if applicable.

        Returns:
            str: Distribution name or the base system name
        """
        if self.system == 'linux':
            try:
                with open('/etc/os-release', 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('ID='):
                            return line.split('=')[1].strip().strip('"')
            except (FileNotFoundError, PermissionError, OSError):
                pass
        return self.system

    def get_os_info(self) -> str:
        """
        Get formatted OS information for display.

        Returns:
            str: Human-readable OS information
        """
        if self.system == 'linux':
            return f"Linux ({self.distro})"
        elif self.system == 'darwin':
            return "macOS"
        elif self.system == 'windows':
            return "Windows"
        else:
            return self.system.title()

    def get_detailed_info(self) -> dict:
        """
        Get detailed OS information.

        Returns:
            dict: Dictionary containing detailed OS information
        """
        return {
            'system': self.system,
            'distro': self.distro,
            'version': self.version,
            'machine': self.machine,
            'display_name': self.get_os_info()
        }

    def is_linux(self) -> bool:
        """Check if the system is Linux."""
        return self.system == 'linux'

    def is_macos(self) -> bool:
        """Check if the system is macOS."""
        return self.system == 'darwin'

    def is_windows(self) -> bool:
        """Check if the system is Windows."""
        return self.system == 'windows'

    def get_shell_type(self) -> str:
        """
        Get the default shell type for the system.

        Returns:
            str: Shell name (bash, zsh, cmd, powershell)
        """
        if self.is_windows():
            return 'cmd'
        else:
            # Most Unix-like systems default to bash
            return 'bash'
