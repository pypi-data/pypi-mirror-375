"""Base module interface for protocol analyzers."""

from abc import ABC, abstractmethod
from typing import Any

from ..core.config import Config


class BaseModule(ABC):
    """Base class for protocol analysis modules."""

    def __init__(self, config: Config):
        """Initialize the module.

        Args:
            config: Configuration instance
        """
        self.config = config

    @abstractmethod
    def analyze_packets(self, pcap_file: str) -> dict[str, Any]:
        """Analyze packets in a PCAP file.

        Args:
            pcap_file: Path to the PCAP file

        Returns:
            Analysis results as a dictionary
        """
        pass

    @property
    @abstractmethod
    def protocol_name(self) -> str:
        """Return the name of the protocol this module analyzes."""
        pass
