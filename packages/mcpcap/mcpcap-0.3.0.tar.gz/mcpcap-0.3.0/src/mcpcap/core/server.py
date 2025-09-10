"""MCP server setup and configuration."""

from fastmcp import FastMCP

from ..modules.dns import DNSModule
from ..resources.references import setup_resources
from .config import Config


class MCPServer:
    """MCP server for PCAP analysis."""

    def __init__(self, config: Config):
        """Initialize MCP server.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.mcp = FastMCP("mcpcap")

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
        import sys

        # Log to stderr to avoid breaking MCP JSON-RPC protocol
        source = (
            self.config.pcap_url if self.config.is_remote else self.config.pcap_path
        )
        source_type = "remote URL" if self.config.is_remote else "directory"
        print(f"Starting MCP server with PCAP {source_type}: {source}", file=sys.stderr)

        self.mcp.run()
