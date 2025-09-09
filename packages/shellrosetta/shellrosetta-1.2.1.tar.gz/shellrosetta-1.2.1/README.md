# ShellRosetta Project Analysis & Implementation Summary

**Translate Linux/Bash commands to PowerShell and vice versa—flags, pipes, networking, and more.**

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)
[![Shell](https://img.shields.io/badge/shell-interactive-blue)](#interactive-shell-mode)
[![Tested](https://img.shields.io/badge/Tests-passing-brightgreen)](tests/)
[![PyPI version](https://badge.fury.io/py/shellrosetta.svg)](https://pypi.org/project/shellrosetta/)
[![codecov](https://codecov.io/github/sdirishguy/shellrosetta/branch/main/graph/badge.svg?token=6X3X6MK47L)](https://codecov.io/github/sdirishguy/shellrosetta)

# ShellRosetta v1.2.0

**Enterprise-grade Linux/Bash to PowerShell translator with AI, plugins, and web interface.**

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/shellrosetta.svg)](https://pypi.org/project/shellrosetta/)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## What is ShellRosetta?

ShellRosetta is a comprehensive command translation platform for developers, sysadmins, and anyone working across Windows and Linux environments. It provides intelligent, bidirectional translation between Linux/Bash and PowerShell commands with AI-powered pattern learning.

## Features

### Core Translation
- **Bidirectional translation**: Linux ↔ PowerShell with 100+ command mappings
- **Flag-aware translation**: Understands complex flag combinations (`ls -alh`, `rm -rf`, etc.)
- **Pipeline support**: Handles piped commands (`ls -l | grep foo`)
- **Intelligent mapping**: Contextual notes for platform differences

### Advanced Features (NEW in v1.2.0)
- **Web Interface**: Beautiful, responsive web UI at `http://localhost:5000`
- **Plugin System**: Extensible architecture with Docker, Kubernetes, AWS, Git plugins
- **ML Engine**: Learns from translations and provides smart suggestions
- **Interactive CLI**: REPL-style interface with command history
- **AST Parsing**: Advanced command analysis and structure understanding
- **Security Validation**: Multi-level command safety checking
- **Performance Monitoring**: Caching and performance metrics

### Professional Features
- **Cross-platform**: Windows, Linux, macOS compatibility
- **Tab Completion**: Bash/Zsh autocomplete support
- **Configuration Management**: Customizable settings and preferences
- **Error Handling**: Robust error reporting and recovery
- **API Endpoints**: RESTful API for programmatic access

## Installation

```bash
pip install shellrosetta
```

## Quick Start

### Command Line Usage
```bash
# Linux to PowerShell
shellrosetta lnx2ps "ls -alh | grep error"
# Output: Get-ChildItem -Force | Format-List | Select-String error

# PowerShell to Linux  
shellrosetta ps2lnx "Get-ChildItem -Force"
# Output: ls -a

# Interactive mode
shellrosetta

# Web interface
shellrosetta api
# Open http://localhost:5000 in browser
```

### Python API
```python
from shellrosetta.core import lnx2ps, ps2lnx

# Translate commands
linux_cmd = "ls -la | grep .txt"
powershell_cmd = lnx2ps(linux_cmd)
print(powershell_cmd)
# Output: Get-ChildItem -Force | Format-List | Select-String .txt
```

## Web Interface

Start the web server:
```bash
shellrosetta api
```

Open http://localhost:5000 for an intuitive web interface featuring:
- Real-time command translation
- Syntax highlighting
- Usage examples
- Translation history

## Plugin System

ShellRosetta includes plugins for:
- **Docker**: Container management commands
- **Kubernetes**: Cluster operations (`kubectl`)
- **AWS CLI**: Cloud service commands
- **Git**: Version control operations

List available plugins:
```bash
shellrosetta plugins
```

## Machine Learning

The ML engine learns from your translations:
```bash
# View learning insights
shellrosetta ml

# The system automatically learns patterns and improves suggestions
```

## Configuration

Customize behavior:
```bash
# View current settings
shellrosetta config

# Settings include color output, history size, security levels
```

## Examples

### File Operations
```bash
# Linux → PowerShell
shellrosetta lnx2ps "rm -rf folder/"
# Remove-Item -Recurse -Force folder/

shellrosetta lnx2ps "cp -r src/ dest/"  
# Copy-Item -Recurse src/ dest/
```

### System Information
```bash
# Linux → PowerShell
shellrosetta lnx2ps "ps aux | grep nginx"
# Get-Process | Select-String nginx

shellrosetta lnx2ps "df -h"
# Get-PSDrive
```

### Network Operations
```bash
# Linux → PowerShell
shellrosetta lnx2ps "ping google.com"
# Test-Connection google.com

shellrosetta lnx2ps "curl -X POST https://api.example.com"
# Invoke-WebRequest -Method POST https://api.example.com
```

## Advanced Usage

### Interactive Mode
```bash
shellrosetta
# Provides REPL interface with:
# - Command history
# - Mode switching (lnx2ps ↔ ps2lnx)  
# - Built-in help
# - Tab completion
```

### API Server
```bash
shellrosetta api --port 8080
# Starts Flask server with REST endpoints:
# POST /api/translate - Translate commands
# GET /api/stats - Usage statistics
# GET /api/plugins - Plugin information
```

## Development

### Custom Plugins
```python
from shellrosetta.plugins import CommandPlugin

class MyPlugin(CommandPlugin):
    def get_name(self):
        return "my_plugin"
    
    def translate(self, command, direction):
        # Custom translation logic
        return translated_command
```

### Extending Mappings
Add custom mappings in `shellrosetta/mappings.py`:
```python
CUSTOM_MAPPINGS = {
    "my_command": ("My-PowerShell-Equivalent", "Usage note")
}
```

## Requirements

- Python 3.7+
- Optional: Flask for web interface (`pip install flask flask-cors`)

## Architecture

ShellRosetta features a modular architecture:
- **Core Engine**: Command parsing and translation
- **ML Engine**: Pattern learning and suggestions  
- **Plugin System**: Extensible command handlers
- **Web API**: Flask-based REST interface
- **CLI Interface**: Professional command-line tool

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file.

## Changelog

### v1.2.0 (Latest)
- Added web interface with Flask API
- Implemented plugin system with 4 built-in plugins
- Added ML engine with pattern learning
- Enhanced CLI with interactive mode
- Added comprehensive test suite
- Improved error handling and documentation

### v1.1.x
- Basic command translation
- Core mapping system
- CLI interface

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: Complete API docs in `/docs`
- Examples: See `/examples` directory

Transform your cross-platform command workflow with ShellRosetta!