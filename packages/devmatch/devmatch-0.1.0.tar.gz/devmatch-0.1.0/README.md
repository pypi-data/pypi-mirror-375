# DevMatch CLI

A minimal developer collaborative platform client that runs entirely as a CLI.

## Installation

```bash
pip install devmatch
```

## Usage

### Authentication
```bash
# Login with GitHub via Firebase
devmatch login

# Check your login status
devmatch whoami

# Logout
devmatch logout
```

### Commands
```bash
# Get help
devmatch help

# Get your daily coffee
devmatch coffee

# Find project suggestions
devmatch whatcanibuild

# Set your current vibe
devmatch setvibe "building cool stuff"

# Find your developer match
devmatch getmymatch

# Follow someone on GitHub
devmatch follow username

# Debug information
devmatch debug
```

## Features

- **GitHub OAuth**: Secure authentication via Firebase
- **Dynamic Commands**: Commands are fetched from Firebase Remote Config
- **Token Caching**: Automatic token management and refresh
- **Rich Output**: Beautiful, structured CLI output
- **Cross-platform**: Works on Windows, macOS, and Linux

## Development

### Running locally
```bash
# Clone the repository
git clone https://github.com/devmatch/devmatch-cli
cd devmatch-cli

# Install in development mode
pip install -e .

# Run commands
devmatch help
```

### Testing
```bash
# Run the CLI directly
python -m devmatch help
```

## Configuration

The CLI uses Firebase project `devmatch-fda15` with the following configuration:
- **Region**: us-central1
- **Functions**: onGithubLogin, commandHandler
- **Remote Config**: commands_list

## Requirements

- Python 3.8+
- Internet connection for Firebase services
- Web browser for GitHub OAuth

## License

MIT License