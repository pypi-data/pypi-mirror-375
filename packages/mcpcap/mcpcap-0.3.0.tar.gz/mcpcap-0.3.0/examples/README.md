# mcpcap Examples

This directory contains example PCAP files and usage demonstrations.

## Example Files

- `dns.pcap` - Sample DNS traffic capture for testing mcpcap functionality

## Usage Examples

### Basic Analysis

**Analyze the entire examples directory:**
```bash
mcpcap --pcap-path ./examples
```

**Analyze specific file:**
```bash
mcpcap --pcap-path ./examples/dns.pcap
```

**With packet limits for faster testing:**
```bash
mcpcap --pcap-path ./examples/dns.pcap --max-packets 50
```

### MCP Client Testing

**With MCP Inspector:**
```bash
npm install -g @modelcontextprotocol/inspector
npx @modelcontextprotocol/inspector mcpcap --pcap-path ./examples/dns.pcap
```

Then use the web interface to:
- Call `list_pcap_files()` to see available files
- Call `list_dns_packets()` (leave filename empty for direct file mode)
- View structured DNS analysis results

### Analysis Prompts

Use these specialized prompts in your MCP client:

- **`security_analysis`** - Focus on threat detection in DNS traffic
- **`network_troubleshooting`** - Identify DNS performance issues  
- **`forensic_investigation`** - Detailed timeline and attribution analysis

## Creating Your Own Examples

To add new example files:

1. Place PCAP files (`.pcap` or `.pcapng`) in this directory
2. Update this README with descriptions
3. Test with the mcpcap server

## Sample Output

When analyzing DNS packets, you'll get structured JSON output including:

- Packet timestamps and network details
- DNS query/response information
- Statistics (queries, responses, unique domains)
- Security-relevant metadata