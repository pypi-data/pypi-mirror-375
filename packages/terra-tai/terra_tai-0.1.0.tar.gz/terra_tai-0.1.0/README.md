# Terra Commands AI (tai)

A powerful natural language shell command tool that uses AI to convert human instructions into appropriate shell commands for your operating system.

## Features

- **AI-Powered Command Generation**: Uses OpenAI's GPT models to generate OS-specific commands
- **Interactive Setup**: Easy setup process for OpenAI API key with fallback support
- **Automatic OS Detection**: Adapts commands for Linux, macOS, Windows, and various distributions
- **Natural Language Processing**: Execute commands using plain English instructions
- **Safe Execution**: Commands require confirmation before execution
- **Dry Run Mode**: Test commands without actually executing them
- **Robust Fallback Mode**: Works seamlessly without AI using predefined command patterns
- **Cross-platform**: Native support for Linux, macOS, and Windows

## Installation

### Prerequisites

- Python 3.7+
- OpenAI API key (for AI functionality)

### From Source

1. Clone the repository:

```bash
git clone https://github.com/terra-agi/terra-commands.git
cd terra-commands
```

2. Install using pip:

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

### Configuration

**Easy Setup:**
Terra Command AI provides a simple interactive setup process:

1. **Setup AI Features:**

   ```bash
   tai --setup-ai
   ```

   Follow the prompts to enter your OpenAI API key securely.

2. **Configuration Storage:**
   Your API key and settings are stored securely in:
   - macOS/Linux: `~/.config/terra-ai/config`
   - Windows: `%USERPROFILE%\\.config\\terra-ai\\config`

**Fallback Mode:**
If you choose not to set up AI or if the OpenAI package is not available, Terra Command AI will automatically fall back to using predefined command patterns. All basic functionality will still work without any additional configuration!

### Direct Installation

```bash
pip install git+https://github.com/terra-agi/terra-commands.git
```

## Usage

### Basic Usage

```bash
tai <instruction>
```

### Examples(Without AI)

```bash
# List files in current directory
tai list files
tai show directory
tai what files are here

# Navigate directories
tai go home
tai go back
tai go up

# System information
tai who am i
tai system info
tai disk usage

# Git operations
tai git status
tai git log
tai current branch

# Network operations
tai ping google
tai internet connection
```

### Advanced Options

```bash
# Dry run mode (shows command without executing)
tai --dry-run list files

# Force execution without confirmation
tai --force system info

# List all available commands and AI status
tai --list

# Show system and AI configuration status
tai --status

# Set up OpenAI API key for AI features
tai --setup-ai
```

### AI-Powered Examples

With AI enabled, you can use much more natural and complex instructions:

```bash
tai "find all python files in the current directory and count them"
tai "show me the last 10 lines of system logs"
tai "check if port 80 is open on localhost"
tai "display my public IP address"
tai "find files larger than 100MB in my home directory"
tai "show the current git branch and status"
tai "list all running docker containers"
tai "check disk usage and show only the largest directories"
```

## Available Commands(Without AI)

### File Operations

- `list files`, `show directory`, `list directory`
- `what files are here`, `see files`

### Directory Navigation

- `go home`, `go to home`
- `go back`, `go up`, `go to parent`

### System Information

- `who am i`, `current user`
- `system info`, `what system`
- `disk usage`, `disk space`
- `memory usage`, `memory info`

### Process Management

- `process list`, `running processes`
- `cpu info`

### Git Operations

- `git status`, `git log`, `git branch`
- `current branch`, `git diff`

### Network Operations

- `ping google`, `network status`
- `internet connection`

## Safety Features

- **Confirmation Required**: All commands require user confirmation before execution
- **Dry Run Mode**: Use `--dry-run` to see what command would be executed
- **Force Mode**: Use `--force` to skip confirmation (use with caution)

## Development

### Adding New Commands

Edit the `CommandInterpreter` class in `terra_cmd.py` to add new command patterns:

```python
self.command_patterns = {
    'new command': 'shell_command',
    # Add more patterns here
}
```

### Testing

```bash
# Test without installation
python terra_cmd.py --dry-run list files

# Run tests
python -m pytest tests/  # (if you add tests)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Future Enhancements

- [ ] Integration with more AI language models for better command interpretation
- [ ] Support for complex multi-step commands
- [ ] Command history and favorites
- [ ] Custom command aliases
- [ ] Integration with shell completion
- [ ] Support for Windows commands
- [ ] Plugin system for extending functionality

## Changelog

### v0.1.0

- Initial release with basic natural language command interpretation
- Support for common file, directory, system, and git operations
- Safe execution with confirmation prompts
- Dry run mode for testing
- Installable via pip

Developed by [TerraAGI](https://terra-agi.com/) Team with <3
