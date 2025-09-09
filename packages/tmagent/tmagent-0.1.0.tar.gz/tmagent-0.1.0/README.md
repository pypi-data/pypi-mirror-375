# tmagent

[![PyPI version](https://badge.fury.io/py/tmagent.svg)](https://badge.fury.io/py/tmagent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**tmagent** is an interactive command-line interface (CLI) tool for managing `tmate` sessions. The main use case is to quickly create and share tmate sessions, making it easy to connect to a session from a mobile device or share it with others for remote pair programming and technical support.

## Features

- 🚀 **Easy Session Management**: Create, view, and destroy tmate sessions with an intuitive interface
- 🎨 **Color-coded Sessions**: Choose from 7 different colors to easily identify your sessions
- 🔗 **SSH Link Display**: Automatically retrieves and displays read-write and read-only SSH links
- 📱 **QR Code Generation**: Generates QR codes for quick mobile access to your sessions
- 🤖 **AI Client Integration**: Automatically detects and integrates with popular AI clients (Gemini, Claude, Qwen, Opencode)
- 📢 **Telegram Notifications**: Send session information directly to Telegram (when configured)
- 🌍 **Internationalization**: Available in English (more languages can be added)

## Screenshots

**Create new session**

<img src="docs/images/01_create_new_session.png" width="500"/>

**Select AI agent**

<img src="docs/images/02_select_ai_agent.png" width="500"/>

**QR codes**

<img src="docs/images/03_qr_codes.png" width="500"/>

**Manage sessions**

<img src="docs/images/04_manage_sessions.png" width="500"/>

**Telegram notification**

<img src="docs/images/05_telegram_notification.png" width="500"/>

## Installation

### Prerequisites

- Python 3.10 or higher
- [tmate](https://tmate.io/) installed and available in your PATH

### Install from PyPI

```bash
pip install tmagent
```

### Install from Source

```bash
git clone https://github.com/aabee-tech/tmagent.git
cd tmagent
pip install -e .
```

## Usage

After installation, simply run:

```bash
tmagent
```

The interactive menu will guide you through all available options:

1. **Create new session**: Start a new tmate session with your preferred color and AI client
2. **Manage existing session**: Connect to, view links for, or destroy existing sessions
3. **Kill all sessions**: Terminate all active tmate sessions at once

### Telegram Integration

To enable Telegram notifications, set the following environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

When creating a new session, you'll be prompted to send a notification if these variables are set.

## Development

### Prerequisites

- Python 3.10 or higher
- [tmate](https://tmate.io/)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/aabee-tech/tmagent.git
cd tmagent

# Install dependencies
pip install -e .[dev]
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/tmate_cli

# Run tests with coverage report
pytest --cov=src/tmate_cli --cov-report=html
```

### Code Quality Checks

```bash
# Run linter
ruff check .

# Run type checker
mypy src/tmate_cli

# Run security scanner
bandit -r src/tmate_cli
```

### Building and Publishing

```bash
# Build the package
./scripts/build.sh

# Publish to PyPI
./scripts/publish.sh
```

## Configuration

The application stores session data in a JSON file located at `~/.tmagent/sessions.json`. This file tracks active sessions and their working directories.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [tmate](https://tmate.io/) - The terminal multiplexer used for session management
- [rich](https://github.com/Textualize/rich) - For beautiful terminal formatting
- [questionary](https://github.com/tmbo/questionary) - For interactive command-line prompts
- [qrcode](https://github.com/lincolnloop/python-qrcode) - For QR code generation