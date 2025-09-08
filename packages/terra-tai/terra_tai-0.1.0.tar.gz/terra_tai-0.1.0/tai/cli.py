"""
Command Line Interface for Terra Command AI

This module provides the command-line interface for Terra Command AI,
handling argument parsing and user interaction.
"""

import argparse
import sys

from .core.terra_command import TerraCommand
from .config.settings import Settings
from .config.setup import SetupManager
from .utils.logging import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser for Terra Command AI.

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Terra Command AI - Execute shell commands using natural language with AI",
        prog="tai"
    )

    parser.add_argument(
        "instruction",
        nargs="*",
        help="Natural language instruction (e.g., 'list files', 'go home')"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what command would be executed without running it"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Execute command without confirmation"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List available command patterns and show AI status"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system and AI configuration status"
    )

    parser.add_argument(
        "--setup-ai",
        action="store_true",
        help="Set up OpenAI API key for AI features"
    )

    parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Reset all configuration to defaults"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file"
    )

    return parser


def main() -> int:
    """
    Main entry point for Terra Command AI CLI.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args()

    # Set up logging
    setup_logging(
        level='DEBUG' if args.verbose else 'INFO',
        log_file=args.log_file
    )

    # Initialize settings and Terra Command AI
    settings = Settings()
    settings.set('verbose', args.verbose)
    terra_cmd = TerraCommand(settings)

    try:
        # Handle different command modes
        if args.reset_config:
            if terra_cmd.reset_configuration():
                return 0
            else:
                return 1

        if args.setup_ai:
            if terra_cmd.setup_ai():
                return 0
            else:
                return 1

        if args.status:
            terra_cmd.show_status()
            return 0

        if args.list:
            terra_cmd.list_available_commands()
            return 0

        if not args.instruction:
            terra_cmd.show_welcome()
            return 0

        # Process the instruction
        instruction = " ".join(args.instruction)
        success = terra_cmd.process_instruction(
            instruction,
            dry_run=args.dry_run,
            force=args.force
        )

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
