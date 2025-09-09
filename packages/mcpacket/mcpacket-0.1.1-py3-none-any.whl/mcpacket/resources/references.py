"""Reference resources for DNS analysis."""

from fastmcp import FastMCP


def setup_resources(mcp: FastMCP) -> None:
    """Set up reference resources for the MCP server.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.resource("dns-record-types://reference")
    def get_dns_record_types() -> str:
        """Reference guide for DNS record types"""
        return """
# DNS Record Types Reference

## Common Record Types:
- **A (1)**: IPv4 address record
- **AAAA (28)**: IPv6 address record  
- **CNAME (5)**: Canonical name (alias)
- **MX (15)**: Mail exchange record
- **NS (2)**: Name server record
- **PTR (12)**: Pointer record (reverse DNS)
- **SOA (6)**: Start of authority
- **TXT (16)**: Text record
- **SRV (33)**: Service record

## Security-Related Types:
- **DNSKEY (48)**: DNS public key
- **RRSIG (46)**: Resource record signature
- **DS (43)**: Delegation signer
- **NSEC (47)**: Next secure record
"""

    @mcp.resource("dns-flags://reference")
    def get_dns_flags_reference() -> str:
        """Reference guide for DNS flags and their meanings"""
        return """
# DNS Flags Reference

## Header Flags:
- **QR**: Query/Response (0=Query, 1=Response)
- **AA**: Authoritative Answer
- **TC**: Truncated (message was truncated)
- **RD**: Recursion Desired
- **RA**: Recursion Available
- **Z**: Reserved (must be zero)
- **AD**: Authenticated Data
- **CD**: Checking Disabled

## Response Codes (RCODE):
- **0**: No error
- **1**: Format error
- **2**: Server failure
- **3**: Name error (domain doesn't exist)
- **4**: Not implemented
- **5**: Refused
"""

    @mcp.resource("suspicious-domains://indicators")
    def get_suspicious_domain_indicators() -> str:
        """Common indicators of suspicious or malicious domains"""
        return """
# Suspicious Domain Indicators

## Common Patterns:
- Long random-looking subdomains
- Domains with excessive hyphens or numbers
- Recently registered domains
- Domains using punycode (internationalized domains)
- DGA (Domain Generation Algorithm) patterns

## Suspicious TLDs (often abused):
- .tk, .ml, .ga, .cf (free TLDs)
- .bit (blockchain domains)
- Newly introduced gTLDs

## Behavioral Indicators:
- High frequency of DNS queries
- Queries to non-existent domains (NXDOMAIN)
- Unusual query patterns or timing
- Queries for infrastructure domains (.arpa, .root-servers.net)

## DNS Tunneling Indicators:
- Unusually long DNS queries
- High volume of TXT record queries
- Queries with encoded data in subdomain names
"""