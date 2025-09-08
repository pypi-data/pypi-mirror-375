"""
Setup Manager for Terra Command AI

This module handles the interactive setup process for configuring
Terra Command AI, including API key setup and initial configuration.
"""

import sys
from typing import Optional
from pathlib import Path

from ..utils.logging import get_logger
from ..utils.helpers import validate_api_key
from .settings import Settings


class SetupManager:
    """
    Interactive setup manager for Terra Command AI configuration.

    This class handles the complete setup process including
    API key configuration and initial preferences.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the setup manager.

        Args:
            settings: Settings instance (optional)
        """
        self.settings = settings or Settings()
        self.logger = get_logger(__name__)

    def run_initial_setup(self) -> bool:
        """
        Run the initial setup process.

        Returns:
            bool: True if setup completed successfully
        """
        print("\n🌟 Welcome to Terra Command AI!")
        print("Terra Command AI uses OpenAI's GPT models to convert natural language into shell commands.")
        print("\n📝 To enable AI features, you'll need an OpenAI API key.")
        print("   • Get your API key from: https://platform.openai.com/api-keys")
        print("   • The key is stored securely in your config directory")

        try:
            choice = self._get_user_choice()
            if choice == 'y':
                return self._setup_api_key()
            else:
                return self._setup_fallback_mode()
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user.")
            return False
        except Exception as e:
            self.logger.error(f"Setup error: {e}")
            print(f"\n❌ Setup failed: {e}")
            return False

    def setup_ai_manually(self) -> bool:
        """
        Manually trigger AI setup.

        Returns:
            bool: True if setup completed successfully
        """
        if self.settings.is_ai_enabled():
            print("ℹ️  AI is already configured!")
            return True

        return self._setup_api_key()

    def _get_user_choice(self) -> str:
        """
        Get user choice for setup.

        Returns:
            str: User choice ('y' or 'n')
        """
        while True:
            choice = input("\n❓ Do you want to set up AI features now? (y/n): ").lower().strip()

            if choice in ['y', 'yes']:
                return 'y'
            elif choice in ['n', 'no']:
                return 'n'
            else:
                print("❌ Please enter 'y' for yes or 'n' for no.")

    def _setup_api_key(self) -> bool:
        """
        Set up the OpenAI API key interactively.

        Returns:
            bool: True if setup completed successfully
        """
        print("\n🔑 Setting up OpenAI API key...")

        while True:
            api_key = input("Enter your OpenAI API key: ").strip()

            if not api_key:
                print("❌ API key cannot be empty. Please try again.")
                continue

            # Validate API key format
            is_valid, message = validate_api_key(api_key)
            if not is_valid:
                print(f"⚠️  {message}")
                retry = input("Do you want to try again? (y/n): ").lower().strip()
                if retry not in ['y', 'yes']:
                    return False
                continue

            # Save API key
            return self._save_api_key(api_key)

    def _save_api_key(self, api_key: str) -> bool:
        """
        Save the API key to configuration.

        Args:
            api_key: OpenAI API key

        Returns:
            bool: True if saved successfully
        """
        try:
            self.settings.set_openai_api_key(api_key)

            if self.settings.save():
                self.logger.info("API key saved successfully")
                print("✅ AI setup complete! Terra Command AI is now enhanced with OpenAI.")
                print("   Your API key is stored securely in your config directory.")
                return True
            else:
                print("❌ Failed to save configuration.")
                return False

        except Exception as e:
            self.logger.error(f"Error saving API key: {e}")
            print(f"❌ Error saving configuration: {e}")
            return False

    def _setup_fallback_mode(self) -> bool:
        """
        Set up fallback mode when user declines AI setup.

        Returns:
            bool: True (fallback mode is always available)
        """
        print("ℹ️  No problem! Terra Command AI will work with fallback commands.")
        print("   You can set up AI features later by running: tai --setup-ai")
        return True

    def reset_configuration(self) -> bool:
        """
        Reset all configuration to defaults.

        Returns:
            bool: True if reset successfully
        """
        try:
            self.settings.reset_to_defaults()
            config_path = Path(self.settings.config_file)
            if config_path.exists():
                config_path.unlink()
            print("✅ Configuration reset to defaults.")
            return True
        except Exception as e:
            print(f"❌ Error resetting configuration: {e}")
            return False
