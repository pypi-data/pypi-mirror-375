# Quick Start Guide

Get up and running with mcpcap in minutes!

## 1. Install mcpcap

```bash
pip install mcpcap
```

## 2. Choose Your PCAP Source

mcpcap supports multiple PCAP sources:

**Single PCAP file**:
```bash
# Use a specific PCAP file
mcpcap --pcap-path ~/Downloads/capture.pcap
```

**Directory of PCAP files**:
```bash
mkdir ~/pcap-analysis
# Copy your PCAP files to this directory
cp your-capture.pcap ~/pcap-analysis/
mcpcap --pcap-path ~/pcap-analysis
```

**Remote PCAP file**:
```bash
# Direct link to a PCAP file
mcpcap --pcap-url https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/dns.cap
```

## 3. Start the MCP Server

The server will start and display connection information. Keep this terminal open.

**With analysis options**:
```bash
# Limit to first 100 packets for faster analysis
mcpcap --pcap-path ~/pcap-analysis --max-packets 100
```

## 4. Connect with an MCP Client

### Option A: MCP Inspector (Quick Testing)

Install and run MCP Inspector:

```bash
npm install -g @modelcontextprotocol/inspector

# Test with local directory
npx @modelcontextprotocol/inspector mcpcap --pcap-path ~/pcap-analysis

# Test with specific file
npx @modelcontextprotocol/inspector mcpcap --pcap-path ~/capture.pcap

# Test with remote file
npx @modelcontextprotocol/inspector mcpcap --pcap-url https://example.com/dns.cap
```

This opens a web interface where you can test the tools interactively.

### Option B: Claude Desktop

Add mcpcap to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mcpcap": {
      "command": "mcpcap",
      "args": ["--pcap-path", "/path/to/your/pcap/files"]
    }
  }
}
```

Restart Claude Desktop and you'll have access to mcpcap tools.

## 5. Analyze Your Traffic

### List Available Files

Use the `list_pcap_files` tool to see what's available:

```
Available PCAP files:
- dns-traffic.pcap
- web-browsing.pcapng
- malware-sample.pcap
```

### Analyze DNS Packets

Use the `list_dns_packets` tool with a filename:

```json
{
  "file": "/path/to/dns-traffic.pcap",
  "dns_packets_found": 245,
  "statistics": {
    "queries": 122,
    "responses": 123,
    "unique_domains_queried": 15,
    "unique_domains": [
      "google.com",
      "github.com",
      "stackoverflow.com"
    ]
  },
  "packets": ["..."]
}
```

## 6. Use Analysis Prompts

mcpcap includes specialized prompts for different analysis scenarios:

### Security Analysis

Use the `security_analysis` prompt to get guidance on threat detection:

- Look for suspicious domain patterns (DGA, long random strings)
- Identify potential DNS tunneling
- Spot C2 communication patterns

### Network Troubleshooting

Use the `network_troubleshooting` prompt for performance analysis:

- Identify slow DNS responses
- Find failed queries and their causes
- Analyze response times

### Forensic Investigation

Use the `forensic_investigation` prompt for detailed analysis:

- Create chronological event timelines
- Document suspicious activities
- Map communication patterns

## 7. Example Workflow

Here's a typical analysis workflow:

1. **Discover files**: `list_pcap_files()`
2. **Analyze traffic**: `list_dns_packets("suspicious.pcap")`
3. **Review results**: Look for unusual domains or query patterns
4. **Deep dive**: Use analysis prompts for specialized guidance
5. **Document findings**: Export results for reporting

## Next Steps

- Explore the [MCP Integration Guide](mcp-integration.md) for detailed client setup
- Read the [Analysis Guides](analysis-guides.md) for advanced techniques
- Check out the examples directory for real-world scenarios

## Common Issues

### Server Won't Start

```bash
# Check if the path exists and contains PCAP files
ls -la ~/pcap-analysis/

# Verify file extensions are .pcap or .pcapng
file ~/pcap-analysis/*
```

### No DNS Packets Found

Some captures might not contain DNS traffic. Try:

```bash
# Use tcpdump to verify DNS packets exist
tcpdump -r your-file.pcap -c 10 port 53
```

### Connection Issues

Make sure:
- The mcpcap server is still running
- No firewall is blocking connections
- MCP client configuration matches server settings