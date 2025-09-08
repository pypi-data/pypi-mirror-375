"""
Command Executor for Terra Command AI

This module handles the safe execution of shell commands with proper
error handling, timeout management, and output formatting.
"""

import subprocess
import shlex
import sys
import os
from typing import Tuple, Optional

from ..utils.logging import get_logger
from ..utils.helpers import safe_execute, format_command_output, clean_command


class CommandExecutor:
    """
    Safe command execution with proper error handling and formatting.

    This class provides methods to execute shell commands safely with
    timeout support, output capture, and proper error reporting.
    """

    def __init__(self, timeout: int = 30, verbose: bool = False):
        """
        Initialize the command executor.

        Args:
            timeout: Default timeout for command execution (seconds)
            verbose: Enable verbose output
        """
        self.timeout = timeout
        self.verbose = verbose
        self.logger = get_logger(__name__)

    def execute(
        self,
        command: str,
        dry_run: bool = False,
        timeout: Optional[int] = None
    ) -> Tuple[bool, str, str]:
        """
        Execute a shell command.

        Args:
            command: Command to execute
            dry_run: If True, only show what would be executed
            timeout: Override default timeout

        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)
        """
        if dry_run:
            print(f"[DRY RUN] Would execute: {command}")
            return True, "", ""

        if timeout is None:
            timeout = self.timeout

        self.logger.debug(f"Executing command: {command}")

        # Log command execution
        if self.verbose:
            print(f"Executing: {command}")

        # Clean the command before execution
        command = clean_command(command)
        success, stdout, stderr = safe_execute(command, timeout, cwd=os.getcwd())

        if success:
            self.logger.debug("Command executed successfully")
            if stdout:
                # Always show command output for successful commands
                formatted_output = format_command_output(stdout)
                print(formatted_output, flush=True)
        else:
            self.logger.error(f"Command failed: {stderr}")
            if stderr:
                print(f"Error: {stderr}", file=sys.stderr, flush=True)

        return success, stdout, stderr

    def execute_with_confirmation(
        self,
        command: str,
        dry_run: bool = False,
        force: bool = False,
        timeout: Optional[int] = None
    ) -> Tuple[bool, str, str]:
        """
        Execute a command with user confirmation.

        Args:
            command: Command to execute
            dry_run: If True, only show what would be executed
            force: If True, skip confirmation
            timeout: Override default timeout

        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)
        """
        if dry_run:
            return self.execute(command, dry_run=True, timeout=timeout)

        if not force:
            response = input(f"Execute: '{command}'? (Y/n): ").lower().strip()
            if response in ['n', 'no']:
                print("Command cancelled.")
                return False, "", "Command cancelled by user"
            elif response == '' or response in ['y', 'yes']:
                # Empty input or explicit yes - proceed with execution
                pass
            else:
                print(f"Invalid response '{response}'. Proceeding with execution...")
                # For any other input, proceed with execution as well

        return self.execute(command, dry_run=False, timeout=timeout)

    def test_command(self, command: str) -> bool:
        """
        Test if a command is likely to succeed without executing it.

        Args:
            command: Command to test

        Returns:
            bool: True if command appears safe to run
        """
        # Basic safety checks
        from ..utils.helpers import is_safe_command
        return is_safe_command(command)

    def get_command_info(self, command: str) -> dict:
        """
        Get information about a command.

        Args:
            command: Command to analyze

        Returns:
            dict: Command information
        """
        try:
            cmd_parts = shlex.split(command)
            return {
                'command': cmd_parts[0] if cmd_parts else '',
                'args': cmd_parts[1:] if len(cmd_parts) > 1 else [],
                'arg_count': len(cmd_parts) - 1 if cmd_parts else 0,
                'has_pipes': '|' in command,
                'has_redirects': '>' in command or '<' in command,
                'is_complex': len(cmd_parts) > 3 or '|' in command or ';' in command
            }
        except Exception:
            return {
                'command': '',
                'args': [],
                'arg_count': 0,
                'has_pipes': False,
                'has_redirects': False,
                'is_complex': False
            }
