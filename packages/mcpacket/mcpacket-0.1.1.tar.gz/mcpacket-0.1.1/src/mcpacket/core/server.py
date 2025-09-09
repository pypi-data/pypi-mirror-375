"""MCP server setup and configuration."""

from fastmcp import FastMCP
from .config import Config
from ..modules.dns import DNSModule
from ..resources.references import setup_resources


class MCPServer:
    """MCP server for PCAP analysis."""
    
    def __init__(self, config: Config):
        """Initialize MCP server.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.mcp = FastMCP("PCAP DNS Analyzer")
        
        # Initialize modules
        self.dns_module = DNSModule(config)
        
        # Register tools
        self._register_tools()
        
        # Setup resources and prompts
        setup_resources(self.mcp)
        self.dns_module.setup_prompts(self.mcp)
    
    def _register_tools(self) -> None:
        """Register all available tools with the MCP server."""
        # Register DNS module tools
        self.mcp.tool(self.dns_module.list_dns_packets)
        self.mcp.tool(self.dns_module.list_pcap_files)
    
    def run(self) -> None:
        """Start the MCP server."""
        print(f"Starting MCP server with PCAP directory: {self.config.pcap_path}")
        self.mcp.run()