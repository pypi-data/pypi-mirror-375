# 🚀 Sheller - AI-Powered Terminal Command Assistant

> **Transform natural language into executable commands with style!**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)
[![Platform: Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.linux.org/)

## ✨ Features

- 🧠 **Natural Language Processing**: Type requests in plain English
- ⚡ **Smart Command Translation**: Automatic Unix-to-Windows command conversion
- 🎨 **Retro Terminal UI**: Beautiful, nostalgic interface with colors and ASCII art
- ⌨️ **Keyboard Shortcuts**: Ctrl+K for processing, arrow keys for history
- 🔄 **PowerShell Fallback**: Intelligent fallback from CMD to PowerShell
- 📱 **Cross-Platform**: Works on Windows, macOS, and Linux
- 🚀 **Real-time Execution**: See commands execute with live output
- 📚 **Command History**: Navigate through your command history

## 🎯 Use Cases

- **System Administrators**: Quick system diagnostics and management
- **Developers**: Rapid command execution without remembering syntax
- **Power Users**: Streamlined terminal workflow
- **Beginners**: Learn commands through natural language
- **DevOps Engineers**: Efficient system operations

## 🚀 Quick Start

### Prerequisites

Before using Sheller, you need to set up your **Google Gemini API Key**:

#### 1. Get Your Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated API key

#### 2. Set Environment Variable

**Windows (PowerShell):**
```powershell
# Temporary (current session only)
$env:GEMINI_API_KEY="your_api_key_here"

# Permanent (add to user profile)
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your_api_key_here", "User")
```

**Windows (Command Prompt):**
```cmd
# Temporary (current session only)
set GEMINI_API_KEY=your_api_key_here

# Permanent (add to user profile)
setx GEMINI_API_KEY "your_api_key_here"
```

**macOS/Linux:**
```bash
# Temporary (current session only)
export GEMINI_API_KEY="your_api_key_here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

#### 3. Alternative: Create .env File
Create a `.env` file in your project directory:
```bash
# .env file
GEMINI_API_KEY=your_api_key_here
```

### Installation

#### Option 1: Python Package (Recommended for Developers)
```bash
pip install sheller
```

#### Option 2: Windows Installer (Recommended for End Users)
Download the latest `.exe` installer from our [releases page](https://github.com/sheller/sheller/releases).

### Usage

#### Launch the Application
```bash
sheller
```

#### Natural Language Commands
```
Type: "show me all files in this directory"
Press: Ctrl+K
Result: dir /a
Press: Enter to execute
```

#### Direct Commands
```
Type: dir
Press: Enter
Result: Executes immediately
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|---------|
| `Ctrl+K` | Process natural language input |
| `Enter` | Execute command |
| `↑/↓` | Navigate command history |
| `Ctrl+C` | Exit application |
| `Backspace` | Edit current input |
| `Delete` | Remove characters |

## 🔧 Supported Commands

### File Operations
- **List files**: `ls` → `dir`
- **List hidden files**: `ls -a` → `dir /a`
- **View file**: `cat` → `type`
- **Copy file**: `cp` → `copy`
- **Move file**: `mv` → `move`
- **Delete file**: `rm` → `del`

### System Information
- **Process list**: `ps aux` → `tasklist`
- **System info**: `systeminfo`
- **Network config**: `ifconfig` → `ipconfig`
- **Disk space**: `df` → PowerShell equivalent
- **Memory usage**: `wmic` commands

### Network Tools
- **Ping**: `ping`
- **Traceroute**: `traceroute` → `tracert`
- **DNS lookup**: `nslookup`
- **Network connections**: `netstat`

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Natural       │    │   Command        │    │   Execution     │
│   Language      │───▶│   Translation    │───▶│   Engine        │
│   Input         │    │   Engine         │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Retro UI      │    │   Shell          │    │   Output        │
│   Interface     │    │   Detection      │    │   Display       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ Development

### Prerequisites
- Python 3.8+
- pip
- setuptools

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/sheller/sheller.git
cd sheller

# Install development dependencies
pip install -e .

# Run the application
python src/sheller/main.py
```

### Building the Package
```bash
# Build source distribution
python -m build --sdist

# Build wheel
python -m build --wheel

# Install locally
pip install dist/sheller-1.0.0-py3-none-any.whl
```

## 📦 Distribution

### Python Package
- **PyPI**: `pip install sheller`
- **Source**: GitHub releases
- **Wheel**: Pre-built for multiple Python versions

### Windows Installer
- **Inno Setup**: Professional installer with custom branding
- **Auto-updates**: Built-in update mechanism
- **Desktop shortcuts**: Easy access for end users

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Areas
- [ ] Enhanced AI command suggestions
- [ ] Plugin system for custom commands
- [ ] Configuration file support
- [ ] Theme customization
- [ ] Command templates
- [ ] Integration with popular shells

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ASCII Art**: Inspired by retro terminal aesthetics
- **Command Translation**: Based on Unix-to-Windows mappings
- **UI Design**: Firebase terminal inspiration
- **Community**: All contributors and users

## 📞 Support

- **Documentation**: [docs.sheller.com](https://docs.sheller.com)
- **Issues**: [GitHub Issues](https://github.com/sheller/sheller/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sheller/sheller/discussions)
- **Email**: team@sheller.com

## 🚀 Roadmap

### v1.1.0 (Q2 2024)
- [ ] AI-powered command suggestions
- [ ] Plugin architecture
- [ ] Configuration management

### v1.2.0 (Q3 2024)
- [ ] Cloud sync for settings
- [ ] Command templates
- [ ] Advanced theming

### v2.0.0 (Q4 2024)
- [ ] Machine learning integration
- [ ] Cross-device sync
- [ ] Enterprise features

---

**Made with ❤️ by the Sheller Team**

*Transform your terminal experience today!*
