# MCP Client Integration

Learn how to integrate mcpacket with different MCP (Model Context Protocol) clients.

## What is MCP?

The Model Context Protocol (MCP) enables LLMs to securely access external resources and tools. mcpacket implements an MCP server that provides DNS analysis capabilities to any compatible MCP client.

## Available MCP Clients

### Claude Desktop

**Best for**: End users who want AI-powered network analysis

Claude Desktop is Anthropic's official desktop application with built-in MCP support.

#### Setup

1. Install Claude Desktop from [claude.ai](https://claude.ai)
2. Open Claude Desktop settings (Cmd/Ctrl + ,)
3. Add mcpacket to your MCP configuration:

```json
{
  "mcpServers": {
    "mcpacket": {
      "command": "mcpacket",
      "args": ["--pcap-path", "/path/to/your/pcap/files"]
    }
  }
}
```

4. Restart Claude Desktop
5. Start a conversation and you'll see mcpacket tools available

#### Usage Tips

- Ask Claude to "analyze the DNS traffic in malware.pcap"
- Request security-focused analysis: "Look for suspicious domains in this capture"
- Get troubleshooting help: "Why are DNS queries failing in this network?"

### MCP Inspector

**Best for**: Developers and technical users who want to test tools directly

MCP Inspector provides a web-based interface for testing MCP servers.

#### Setup

```bash
# Install globally
npm install -g @modelcontextprotocol/inspector

# Run with mcpacket
npx @modelcontextprotocol/inspector mcpacket --pcap-path /path/to/pcaps
```

#### Features

- Interactive tool testing
- Real-time parameter input
- JSON response viewing
- Resource and prompt exploration

### Custom Python Client

**Best for**: Developers integrating mcpacket into applications

Build your own MCP client using the Python MCP library.

#### Example Implementation

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def analyze_dns():
    # Connect to mcpacket server
    server_params = StdioServerParameters(
        command="mcpacket",
        args=["--pcap-path", "/path/to/pcaps"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [tool.name for tool in tools.tools])
            
            # Call a tool
            result = await session.call_tool(
                "list_dns_packets",
                arguments={"pcap_file": "example.pcap"}
            )
            
            print("Analysis result:", result.content)

# Run the analysis
asyncio.run(analyze_dns())
```

## Available Tools

### `list_pcap_files`

Lists all PCAP files in the configured directory.

**Parameters**: None

**Returns**: List of available .pcap and .pcapng files

### `list_dns_packets`

Analyzes DNS packets in a PCAP file.

**Parameters**:
- `pcap_file` (optional): Filename to analyze (defaults to "example.pcap")

**Returns**: Structured JSON with packet details and statistics

## Available Resources

### DNS Reference Materials

- `dns-record-types://reference`: DNS record types guide
- `dns-flags://reference`: DNS flags and response codes
- `suspicious-domains://indicators`: Security indicators for domains

## Available Prompts

### Analysis Prompts

- `security_analysis`: Security-focused DNS analysis guidance
- `network_troubleshooting`: Network performance troubleshooting
- `forensic_investigation`: Digital forensics approach

## Configuration Options

### Server Configuration

```bash
# Basic usage
mcpacket --pcap-path /path/to/pcaps

# Advanced options (coming soon)
mcpacket --pcap-path /path/to/pcaps --max-packets 1000 --protocols dns,http
```

### Client Configuration Examples

#### Claude Desktop (Extended)

```json
{
  "mcpServers": {
    "mcpacket-production": {
      "command": "mcpacket",
      "args": ["--pcap-path", "/production/captures"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    },
    "mcpacket-analysis": {
      "command": "mcpacket", 
      "args": ["--pcap-path", "/analysis/workspace"]
    }
  }
}
```

#### Environment Variables

```bash
# Set logging level
export LOG_LEVEL=DEBUG

# Set default PCAP path
export MCPACKET_PCAP_PATH=/default/path
```

## Best Practices

### Security

- Never point mcpacket at directories with sensitive captures
- Use read-only permissions for PCAP directories when possible
- Be cautious with captures containing personal information

### Performance

- Use specific filenames instead of analyzing all files at once
- Consider splitting large PCAP files for better performance
- Monitor memory usage with very large captures

### Organization

- Organize PCAP files by date, source, or investigation
- Use descriptive filenames: `malware-sample-2024-01-15.pcap`
- Keep separate directories for different analysis projects

## Troubleshooting

### Common Issues

**Tool not available in Claude Desktop**
- Check MCP configuration syntax
- Restart Claude Desktop after configuration changes
- Verify mcpacket is installed and accessible

**Server connection failed**
- Ensure PCAP directory exists and is readable
- Check that mcpacket command works from terminal
- Verify no other processes are using the same resources

**Empty results**
- Confirm PCAP files contain DNS traffic (`port 53`)
- Check file extensions are `.pcap` or `.pcapng`
- Verify files aren't corrupted with `file` command

**Performance issues**
- Use smaller PCAP files for initial testing
- Consider filtering large captures before analysis
- Monitor system resources during analysis

## Integration Examples

### Security Operations Center (SOC)

```json
{
  "mcpServers": {
    "mcpacket-incident": {
      "command": "mcpacket",
      "args": ["--pcap-path", "/incidents/current"]
    }
  }
}
```

### Network Troubleshooting

```json
{
  "mcpServers": {
    "mcpacket-network": {
      "command": "mcpacket",
      "args": ["--pcap-path", "/network/diagnostics"]
    }
  }
}
```

### Research and Development

```json
{
  "mcpServers": {
    "mcpacket-research": {
      "command": "mcpacket",
      "args": ["--pcap-path", "/research/samples"]
    }
  }
}
```