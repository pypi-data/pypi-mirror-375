"""
Terra Command Main Interface

This module provides the main interface class for Terra Command AI,
combining all components into a cohesive command-line tool.
"""

import platform
from typing import List

from ..utils.logging import get_logger
from .interpreter import CommandInterpreter
from .os_detector import OSDetector
from ..config.settings import Settings
from ..config.setup import SetupManager


class TerraCommand:
    """
    Main Terra Command AI command interface.

    This class provides the primary interface for the Terra Command AI tool,
    handling command interpretation, execution, and user interaction.
    """

    def __init__(self, settings: Settings = None):
        """
        Initialize Terra Command.

        Args:
            settings: Settings instance (optional)
        """
        self.settings = settings or Settings()
        self.interpreter = CommandInterpreter(self.settings)
        self.setup_manager = SetupManager(self.settings)
        self.os_detector = OSDetector()
        self.logger = get_logger(__name__)

    def process_instruction(
        self,
        instruction: str,
        dry_run: bool = False,
        force: bool = False
    ) -> bool:
        """
        Process a natural language instruction.

        Args:
            instruction: Natural language instruction
            dry_run: If True, only show what would be executed
            force: If True, skip confirmation

        Returns:
            bool: True if processing was successful
        """
        return self.interpreter.execute_instruction(instruction, dry_run, force)

    def show_welcome(self) -> None:
        """Show welcome message and usage information."""
        ai_status = "✓ AI-powered" if self.interpreter.is_ai_enabled() else "✗ Fallback mode"
        os_info = self.os_detector.get_os_info()

        print(f"Terra Command AI - {ai_status}")
        print(f"Operating System: {os_info}")
        print()
        print("Usage: tai <instruction>")
        print("Examples:")
        print("  tai list files")
        print("  tai show me running processes")
        print("  tai check disk usage")
        print("  tai find all python files in current directory")
        print()
        print("Options:")
        print("  --list          Show available commands")
        print("  --status        Show system and AI status")
        print("  --setup-ai      Set up OpenAI API key for AI features")
        print("  --dry-run       Preview commands without executing")
        print("  --force         Execute without confirmation")
        print()
        if not self.interpreter.is_ai_enabled():
            print("Note: AI is not configured. Terra Command AI works with fallback commands,")
            print("      but you can enable AI features with: tai --setup-ai")

    def list_available_commands(self) -> None:
        """Show available command patterns."""
        ai_status = "✓ AI-powered" if self.interpreter.is_ai_enabled() else "✗ Fallback mode"
        os_info = self.os_detector.get_os_info()

        print(f"Terra Command AI - {ai_status}")
        print(f"Operating System: {os_info}")
        print("\nAvailable commands (fallback patterns):")

        commands = self.interpreter.get_available_commands()
        for pattern in sorted(commands):
            print(f"  - {pattern}")

        print("\nWith AI enabled, you can also try natural variations like:")
        print("  - 'show me the files here'")
        print("  - 'what processes are running'")
        print("  - 'go to the parent directory'")
        print("  - 'find all python files'")
        print("  - 'check my ip address'")
        print("  - 'show system temperature'")

        if not self.interpreter.is_ai_enabled():
            print("\nNote: AI is not configured. Terra Command AI works with fallback commands,")
            print("      but you can enable AI features with: tai --setup-ai")

    def show_status(self) -> None:
        """Show system and AI configuration status."""
        os_info = self.os_detector.get_os_info()
        ai_available = self.interpreter.is_ai_enabled()

        print("Terra Command AI Status")
        print("=" * 25)
        print(f"Operating System: {os_info}")
        print(f"Python Version: {platform.python_version()}")

        if ai_available:
            print("AI Status: ✓ Enabled")
            ai_config = self.settings.get_ai_config()
            print(f"AI Model: {ai_config['model']}")
            print(f"AI Connection: {'✓' if self.interpreter.test_ai_connection() else '✗'}")
        else:
            print("AI Status: ✗ Disabled")
            try:
                import openai
                print("  Reason: OPENAI_API_KEY not configured")
            except ImportError:
                print("  Reason: OpenAI package not installed")

        print(f"Available Commands: {self.interpreter.get_command_count()} fallback patterns")

    def setup_ai(self) -> bool:
        """
        Set up AI features interactively.

        Returns:
            bool: True if setup was successful
        """
        return self.setup_manager.setup_ai_manually()

    def reset_configuration(self) -> bool:
        """
        Reset all configuration to defaults.

        Returns:
            bool: True if reset was successful
        """
        return self.setup_manager.reset_configuration()
