# mcpacket Examples

This directory contains example PCAP files and usage demonstrations.

## Example Files

- `example.pcap` - Sample DNS traffic capture for testing
- `complex_dns.pcapng` - More complex DNS queries with various record types

## Usage Examples

### Basic Analysis

```bash
# Start the MCP server
mcpacket --pcap-path ./examples

# Then use your MCP client to analyze:
# - list_dns_packets("example.pcap")
# - list_pcap_files()
```

### Security Analysis

Use the `security_analysis` prompt to focus on threat detection in DNS traffic.

### Network Troubleshooting

Use the `network_troubleshooting` prompt to identify DNS performance issues.

### Forensic Investigation

Use the `forensic_investigation` prompt for detailed timeline and attribution analysis.

## Creating Your Own Examples

To add new example files:

1. Place PCAP files (`.pcap` or `.pcapng`) in this directory
2. Update this README with descriptions
3. Test with the mcpacket server

## Sample Output

When analyzing DNS packets, you'll get structured JSON output including:

- Packet timestamps and network details
- DNS query/response information
- Statistics (queries, responses, unique domains)
- Security-relevant metadata