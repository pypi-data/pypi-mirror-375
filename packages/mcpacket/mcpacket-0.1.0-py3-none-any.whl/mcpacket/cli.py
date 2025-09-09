"""CLI entry point for mcpacket.

This module provides the command-line interface for mcpacket, handling argument parsing
and server initialization.
"""

import argparse
from .core import Config, MCPServer


def main():
    """Main function to parse arguments and start the MCP server.
    
    Parses command-line arguments, initializes the configuration and MCP server,
    and handles graceful shutdown and error conditions.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
        
    Raises:
        ValueError: If the provided PCAP path is invalid
        KeyboardInterrupt: If the user interrupts the server
        Exception: For any unexpected errors during server operation
    """
    parser = argparse.ArgumentParser(description="PCAP DNS Analyzer MCP Server")
    parser.add_argument(
        "--pcap-path",
        required=True,
        help="Path to directory containing PCAP files"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize configuration
        config = Config(args.pcap_path)
        
        # Create and start MCP server
        server = MCPServer(config)
        server.run()
        return 0
        
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())