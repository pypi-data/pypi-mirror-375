# Installation

mcpacket requires Python 3.10 or greater.

## Using pip (Recommended)

Install mcpacket from PyPI:

```bash
pip install mcpacket
```

This will install mcpacket and all its dependencies.

## Using uv

If you're using [uv](https://github.com/astral-sh/uv):

```bash
uv add mcpacket
```

## Using uvx (One-time usage)

To run mcpacket without installing it permanently:

```bash
uvx mcpacket --pcap-path /path/to/pcap/files
```

## Development Installation

If you want to contribute to mcpacket or modify it:

```bash
# Clone the repository
git clone https://github.com/danohn/mcpacket.git
cd mcpacket

# Install in development mode with all dependencies
pip install -e ".[dev,docs,test]"
```

## Verify Installation

Verify that mcpacket is installed correctly:

```bash
mcpacket --help
```

You should see the help message showing available command-line options.

## Dependencies

mcpacket depends on:

- **fastmcp**: MCP server framework
- **scapy**: Packet parsing and analysis
- **Python 3.10+**: Modern Python features and type hints

All dependencies are automatically installed when you install mcpacket.

## Troubleshooting

### Permission Issues

On some systems, you might need root privileges to capture packets:

```bash
# On Linux, you might need to run as root or set capabilities
sudo setcap cap_net_raw+ep $(which python)
```

### Import Errors

If you encounter import errors, make sure you're using the correct Python version:

```bash
python --version  # Should be 3.10 or higher
```

### Virtual Environment

It's recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install mcpacket
```