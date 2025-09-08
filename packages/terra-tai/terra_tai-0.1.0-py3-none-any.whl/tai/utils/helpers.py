"""
Helper Functions for Terra Command AI

This module contains utility functions used throughout Terra Command AI,
including API key validation, safe execution helpers, and common utilities.
"""

import re
import subprocess
import shlex
from typing import Optional, Tuple, List
from pathlib import Path


def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate an OpenAI API key format.

    Args:
        api_key: API key to validate

    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    if not api_key:
        return False, "API key cannot be empty"

    # OpenAI API keys start with 'sk-' or 'sk-proj-'
    if not (api_key.startswith('sk-') or api_key.startswith('sk-proj-')):
        return False, "API key should start with 'sk-' or 'sk-proj-'"

    # Check reasonable length (OpenAI API keys are typically 50-200 characters)
    if len(api_key) < 20:
        return False, "API key seems too short"
    if len(api_key) > 300:
        return False, "API key seems too long"

    # Basic pattern validation for OpenAI API keys
    # Should contain only alphanumeric characters, hyphens, and underscores after the prefix
    remaining = api_key[3:] if api_key.startswith('sk-') else api_key[8:] if api_key.startswith('sk-proj-') else api_key
    if not re.match(r'^[a-zA-Z0-9\-_]+$', remaining):
        return False, "API key contains invalid characters after prefix"

    return True, "API key format appears valid"


def clean_command(command: str) -> str:
    """
    Clean a command string by removing unnecessary quotes and formatting.

    Args:
        command: Raw command string

    Returns:
        str: Cleaned command string
    """
    # Remove surrounding quotes if they exist
    command = command.strip()
    if (command.startswith('"') and command.endswith('"')) or \
       (command.startswith("'") and command.endswith("'")):
        command = command[1:-1]

    # Remove any extra whitespace
    command = command.strip()

    return command


def safe_execute(
    command: str,
    timeout: int = 30,
    cwd: Optional[str] = None
) -> Tuple[bool, str, str]:
    """
    Safely execute a shell command with proper error handling.

    Args:
        command: Command to execute
        timeout: Timeout in seconds
        cwd: Working directory

    Returns:
        Tuple[bool, str, str]: (success, stdout, stderr)
    """
    try:
        # Clean the command first
        command = clean_command(command)

        # Use shlex to properly split the command
        cmd_args = shlex.split(command)

        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            shell=False  # Avoid shell=True for security
        )

        return result.returncode == 0, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except subprocess.CalledProcessError as e:
        return False, e.stdout or "", e.stderr or str(e)
    except Exception as e:
        return False, "", f"Execution error: {str(e)}"


def find_config_file() -> Optional[Path]:
    """
    Find the Terra Command AI configuration file.

    Returns the standard config file location used by Terra Command AI.

    Returns:
        Optional[Path]: Path to config file if it exists
    """
    config_path = Path.home() / '.config' / 'terra-ai' / 'config'
    return config_path if config_path.exists() else None


def ensure_directory(path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def format_command_output(output: str, max_lines: int = 50) -> str:
    """
    Format command output for display.

    Args:
        output: Raw command output
        max_lines: Maximum number of lines to show

    Returns:
        str: Formatted output
    """
    lines = output.strip().split('\n')

    if len(lines) > max_lines:
        truncated = lines[:max_lines]
        truncated.append(f"... ({len(lines) - max_lines} more lines)")
        return '\n'.join(truncated)

    return output.strip()


def parse_command_suggestion(suggestion: str) -> List[str]:
    """
    Parse a command suggestion string into individual commands.

    Args:
        suggestion: Command suggestion (may contain multiple commands)

    Returns:
        List[str]: List of individual commands
    """
    # Split by common separators
    commands = re.split(r'[;&|]\s*', suggestion.strip())

    # Clean up commands
    return [cmd.strip() for cmd in commands if cmd.strip()]


def is_safe_command(command: str) -> bool:
    """
    Perform basic safety check on a command.

    This is a simple heuristic check and should not be relied upon
    for security in production environments.

    Args:
        command: Command to check

    Returns:
        bool: True if command appears safe
    """
    # Dangerous commands and patterns
    dangerous_patterns = [
        r'\brm\s+-rf\s+/',  # rm -rf /
        r'\brm\s+-rf\s+\*',  # rm -rf *
        r'\brm\s+-rf\s+~',  # rm -rf ~
        r'\bdd\s+',  # dd command
        r'\bfdisk\s+',  # fdisk
        r'\bmkfs\s+',  # mkfs
        r'\bformat\s+',  # format
        r'\bshutdown\s+',  # shutdown
        r'\breboot\s+',  # reboot
        r'\bhalt\s+',  # halt
        r'\bpoweroff\s+',  # poweroff
        r'>\s*/dev/',  # redirect to device files
    ]

    command_lower = command.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, command_lower):
            return False

    return True
