"""
AI Command Interpreter for Terra Command AI

This module handles AI-powered command generation using OpenAI's GPT models.
It provides intelligent interpretation of natural language instructions into
appropriate shell commands for the detected operating system.
"""

import sys
from typing import Optional

from ..utils.logging import get_logger
from ..utils.helpers import clean_command
from ..core.os_detector import OSDetector
from ..config.settings import Settings

try:
    from openai import OpenAI
    AI_AVAILABLE = True
except ImportError:
    OpenAI = None
    AI_AVAILABLE = False


class AICommandInterpreter:
    """
    AI-powered command interpreter using OpenAI's GPT models.

    This class handles the generation of shell commands from natural language
    instructions using AI, with proper error handling and fallbacks.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the AI command interpreter.

        Args:
            settings: Settings instance (optional)
        """
        self.settings = settings or Settings()
        self.os_detector = OSDetector()
        self.logger = get_logger(__name__)
        self.client = None

        # Configure OpenAI if available
        if AI_AVAILABLE and self.settings.get_openai_api_key():
            try:
                # Create client with explicit httpx configuration to avoid proxy issues
                import httpx
                # Create httpx client without proxy configuration
                http_client = httpx.Client()
                self.client = OpenAI(
                    api_key=self.settings.get_openai_api_key(),
                    http_client=http_client
                )
            except TypeError as e:
                # If httpx client creation fails due to TypeError, try without custom client
                try:
                    self.client = OpenAI(api_key=self.settings.get_openai_api_key())
                except Exception:
                    self.logger.warning("OpenAI client initialization failed. AI features will be disabled.")
                    self.client = None
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    def is_ai_available(self) -> bool:
        """
        Check if AI functionality is available.

        Returns:
            bool: True if AI can be used
        """
        return (
            AI_AVAILABLE and
            self.settings.get_openai_api_key() is not None
        )

    def generate_command(self, instruction: str) -> Optional[str]:
        """
        Generate a shell command from natural language instruction.

        Args:
            instruction: Natural language instruction

        Returns:
            Optional[str]: Generated shell command or None if failed
        """
        if not self.is_ai_available() or not self.client:
            return None

        os_info = self.os_detector.get_os_info()

        prompt = f"""
You are a Terra Command Assistant that converts natural language instructions into appropriate shell commands for {os_info}.

Guidelines:
- Return ONLY the shell command, no explanations or markdown
- Use the correct commands for {os_info}
- If the instruction is unclear, return an empty string
- Prefer safe, non-destructive commands
- Use appropriate flags and options for the OS

Examples:
- "list files" -> "ls -la"
- "go home" -> "cd ~"
- "system info" -> "uname -a"
- "disk usage" -> "df -h"
- "running processes" -> "ps aux"
- "git status" -> "git status"

Instruction: {instruction}
Command:"""

        try:
            ai_config = self.settings.get_ai_config()

            response = self.client.chat.completions.create(
                model=ai_config['model'],
                messages=[
                    {"role": "system", "content": "You are a shell command generator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=ai_config['max_tokens'],
                temperature=ai_config['temperature']
            )

            command = response.choices[0].message.content.strip()

            # Clean up the response
            command = self._clean_command(command)

            # Validate the command
            if command and self._is_valid_command(command):
                # Clean the command before returning
                cleaned_command = clean_command(command)
                self.logger.debug(f"Generated command: {cleaned_command}")
                return cleaned_command

        except Exception as e:
            self.logger.error(f"AI command generation failed: {e}")

        return None

    def _clean_command(self, command: str) -> str:
        """
        Clean up the AI-generated command.

        Args:
            command: Raw command from AI

        Returns:
            str: Cleaned command
        """
        # Remove markdown formatting
        command = command.replace('`', '').strip()

        # Remove common prefixes that AI might add
        prefixes_to_remove = [
            'Command:',
            'Shell command:',
            'Execute:',
            'Run:',
        ]

        for prefix in prefixes_to_remove:
            if command.startswith(prefix):
                command = command[len(prefix):].strip()

        return command

    def _is_valid_command(self, command: str) -> bool:
        """
        Perform basic validation on the generated command.

        Args:
            command: Command to validate

        Returns:
            bool: True if command appears valid
        """
        if not command or len(command) > 500:
            return False

        # Check for explanations instead of commands
        explanation_keywords = [
            'i ', 'the ', 'this ', 'you ', 'here is',
            'command to', 'use the', 'run the'
        ]

        command_lower = command.lower()
        for keyword in explanation_keywords:
            if command_lower.startswith(keyword):
                return False

        return True

    def get_supported_models(self) -> list:
        """
        Get list of supported OpenAI models.

        Returns:
            list: List of supported model names
        """
        return [
            'gpt-4',
            'gpt-4-turbo-preview',
            'gpt-3.5-turbo',
            'gpt-3.5-turbo-16k'
        ]

    def test_connection(self) -> bool:
        """
        Test the connection to OpenAI API.

        Returns:
            bool: True if connection successful
        """
        if not self.is_ai_available() or not self.client:
            return False

        try:
            # Simple test query
            response = self.client.chat.completions.create(
                model=self.settings.get('openai_model'),
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            self.logger.error(f"OpenAI API test failed: {e}")
            return False
