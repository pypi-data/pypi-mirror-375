# ScratchAgent

A Python agent framework for building intelligent automation tools.

## Description

ScratchAgent is a lightweight and flexible framework designed to help developers create intelligent agents for automation tasks. Whether you're building chatbots, automation scripts, or AI-powered tools, ScratchAgent provides the foundation you need.

## Features

- Simple and intuitive API
- Extensible architecture
- Easy integration with existing Python projects
- Lightweight with minimal dependencies

## Installation

You can install ScratchAgent from PyPI:

```bash
pip install ScratchAgent
```

Or install the development version:

```bash
pip install ScratchAgent[dev]
```

## Quick Start

```python
from agent import greet

# Basic usage
message = greet("World")
print(message)  # Output: Hello, World!
```

## Command Line Usage

After installation, you can use the command line interface:

```bash
scratchagent
```

## Development

To set up for development:

1. Clone the repository:
```bash
git clone https://github.com/AbQaadir/ScratchAgent.git
cd ScratchAgent
```

2. Install in development mode:
```bash
pip install -e .[dev]
```

3. Run tests:
```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

- **Qaadir** - [AbQaadir](https://github.com/AbQaadir)

## Changelog

### Version 0.1.0
- Initial release
- Basic greeting functionality
- Command line interface