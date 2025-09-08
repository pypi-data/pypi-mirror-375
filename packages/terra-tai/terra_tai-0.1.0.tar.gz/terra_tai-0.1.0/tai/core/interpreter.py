"""
Main Command Interpreter for Terra Command AI

This module provides the primary interface for interpreting natural language
instructions into shell commands, combining AI-powered generation with
fallback patterns and safe execution.
"""

from typing import Optional, List

from ..utils.logging import get_logger
from .os_detector import OSDetector
from .ai_interpreter import AICommandInterpreter
from .executor import CommandExecutor
from ..commands.patterns import CommandPatterns
from ..config.settings import Settings


class CommandInterpreter:
    """
    Main command interpreter that combines AI and pattern-based approaches.

    This class provides the primary interface for converting natural language
    instructions into executable shell commands, with automatic fallbacks.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the command interpreter.

        Args:
            settings: Settings instance (optional)
        """
        self.settings = settings or Settings()
        self.os_detector = OSDetector()
        self.ai_interpreter = AICommandInterpreter(self.settings)
        self.executor = CommandExecutor(
            timeout=self.settings.get('timeout', 30),
            verbose=self.settings.get('verbose', False)
        )
        self.patterns = CommandPatterns()
        self.logger = get_logger(__name__)

    def interpret(self, instruction: str) -> Optional[str]:
        """
        Interpret a natural language instruction into a shell command.

        Args:
            instruction: Natural language instruction

        Returns:
            Optional[str]: Shell command or None if interpretation fails
        """
        instruction = instruction.lower().strip()

        if not instruction:
            return None

        self.logger.debug(f"Interpreting instruction: {instruction}")

        # Try AI first if available
        if self.ai_interpreter.is_ai_available():
            ai_command = self.ai_interpreter.generate_command(instruction)
            if ai_command:
                self.logger.debug(f"AI generated command: {ai_command}")
                return ai_command

        # Fall back to pattern matching
        pattern_command = self.patterns.get_pattern(instruction)
        if pattern_command:
            self.logger.debug(f"Pattern matched command: {pattern_command}")
            return pattern_command

        # Try pattern-based matching for variations
        command = self._pattern_based_matching(instruction)
        if command:
            self.logger.debug(f"Pattern-based command: {command}")
            return command

        self.logger.debug("No command found for instruction")
        return None

    def _pattern_based_matching(self, instruction: str) -> Optional[str]:
        """
        Perform pattern-based matching for instruction variations.

        Args:
            instruction: Instruction to match

        Returns:
            Optional[str]: Matched command or None
        """
        # File operations
        if any(word in instruction for word in ['list', 'show', 'see']) and \
           any(word in instruction for word in ['files', 'directory', 'folder']):
            return 'ls -la'

        # Directory navigation
        if any(word in instruction for word in ['go', 'change', 'move']) and \
           any(word in instruction for word in ['home', 'back', 'up', 'parent']):
            if 'home' in instruction:
                return 'cd ~'
            elif 'back' in instruction or 'up' in instruction or 'parent' in instruction:
                return 'cd ..'

        # System information
        if any(word in instruction for word in ['system', 'os', 'kernel']):
            return 'uname -a'
        elif any(word in instruction for word in ['who', 'user', 'me']):
            return 'whoami'

        # Process management
        if any(word in instruction for word in ['process', 'running', 'cpu']):
            if 'cpu' in instruction:
                return 'top -n 1'
            else:
                return 'ps aux'

        # Disk and memory
        if 'disk' in instruction or 'space' in instruction:
            return 'df -h'
        elif 'memory' in instruction or 'ram' in instruction:
            return 'free -h'

        # Git operations
        if 'git' in instruction:
            if 'status' in instruction:
                return 'git status'
            elif 'log' in instruction:
                return 'git log --oneline -10'
            elif 'branch' in instruction:
                return 'git branch'

        # Network operations
        if any(word in instruction for word in ['ping', 'network', 'internet']):
            if 'ping' in instruction:
                return 'ping -c 4 google.com'
            else:
                return 'ifconfig'

        return None

    def execute_instruction(
        self,
        instruction: str,
        dry_run: bool = False,
        force: bool = False
    ) -> bool:
        """
        Interpret and execute a natural language instruction.

        Args:
            instruction: Natural language instruction
            dry_run: If True, only show what would be executed
            force: If True, skip confirmation prompts

        Returns:
            bool: True if execution was successful
        """
        command = self.interpret(instruction)

        if command is None:
            print(f"I don't understand: '{instruction}'")
            print("Try something like:")
            print("  - list files")
            print("  - go home")
            print("  - git status")
            print("  - system info")
            return False

        success, stdout, stderr = self.executor.execute_with_confirmation(
            command, dry_run, force
        )

        return success

    def get_available_commands(self) -> List[str]:
        """
        Get list of available command patterns.

        Returns:
            List[str]: List of instruction patterns
        """
        return list(self.patterns.get_all_patterns().keys())

    def get_command_count(self) -> int:
        """
        Get the total number of available command patterns.

        Returns:
            int: Number of patterns
        """
        return self.patterns.get_pattern_count()

    def is_ai_enabled(self) -> bool:
        """
        Check if AI functionality is enabled.

        Returns:
            bool: True if AI is available
        """
        return self.ai_interpreter.is_ai_available()

    def test_ai_connection(self) -> bool:
        """
        Test the connection to AI services.

        Returns:
            bool: True if connection successful
        """
        return self.ai_interpreter.test_connection()
