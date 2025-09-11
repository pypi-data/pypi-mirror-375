# mcpcap Examples

This directory contains example PCAP files and usage demonstrations for different protocol modules.

## Example Files

- `dns.pcap` - Sample DNS traffic capture for testing DNS module functionality
- `dhcp.pcap` - Sample DHCP traffic capture showing complete 4-way handshake (DISCOVER → OFFER → REQUEST → ACK)

## Usage Examples

### Basic Analysis

**Analyze the entire examples directory:**
```bash
mcpcap --pcap-path ./examples
```

**Analyze specific file:**
```bash
# DNS analysis
mcpcap --pcap-path ./examples/dns.pcap

# DHCP analysis  
mcpcap --pcap-path ./examples/dhcp.pcap --modules dhcp
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
- Call `list_dns_packets()` or `list_dhcp_packets()` 
- View structured analysis results

### Analysis Prompts

Use these specialized prompts in your MCP client:

**DNS Module Prompts:**
- **`security_analysis`** - Focus on threat detection in DNS traffic
- **`network_troubleshooting`** - Identify DNS performance issues  
- **`forensic_investigation`** - Detailed timeline and attribution analysis

**DHCP Module Prompts:**
- **`dhcp_network_analysis`** - Network administration and IP management
- **`dhcp_security_analysis`** - Security threats and rogue DHCP detection
- **`dhcp_forensic_investigation`** - Forensic analysis of DHCP transactions

## Creating Your Own Examples

To add new example files:

1. Place PCAP files (`.pcap` or `.pcapng`) in this directory
2. Update this README with descriptions
3. Test with the mcpcap server

## Sample Output

### DNS Analysis
When analyzing DNS packets, you'll get structured JSON output including:
- Packet timestamps and network details
- DNS query/response information
- Statistics (queries, responses, unique domains)
- Security-relevant metadata

### DHCP Analysis
When analyzing DHCP packets, you'll get structured JSON output including:
- Complete DHCP transaction tracking (DISCOVER/OFFER/REQUEST/ACK)
- Client and server identification (MAC addresses, IP addresses)
- Lease information and timing
- DHCP options and configurations
- Network statistics and anomaly detection