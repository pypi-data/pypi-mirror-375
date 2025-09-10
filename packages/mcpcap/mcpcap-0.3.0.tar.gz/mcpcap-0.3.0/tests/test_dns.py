"""Tests for DNS module."""

from unittest.mock import Mock, patch

import pytest

from mcpcap.core.config import Config
from mcpcap.modules.dns import DNSModule


class TestDNSModule:
    """Test DNS analysis module."""

    def test_protocol_name(self):
        """Test that protocol name is correct."""
        config = Mock()
        module = DNSModule(config)
        assert module.protocol_name == "DNS"

    def test_list_pcap_files_empty_directory(self):
        """Test listing PCAP files when directory is empty."""
        config = Mock()
        config.list_pcap_files.return_value = []
        config.pcap_path = "/test/path"
        config.is_remote = False

        module = DNSModule(config)
        result = module.list_pcap_files()

        assert "No PCAP files found" in result
        assert "/test/path" in result

    def test_list_pcap_files_with_files(self):
        """Test listing PCAP files when files exist."""
        config = Mock()
        config.list_pcap_files.return_value = ["test1.pcap", "test2.pcapng"]
        config.pcap_path = "/test/path"
        config.is_remote = False
        config.is_direct_file_path = False

        module = DNSModule(config)
        result = module.list_pcap_files()

        assert "test1.pcap" in result
        assert "test2.pcapng" in result
        assert "/test/path" in result

    def test_list_dns_packets_file_not_found(self):
        """Test analyzing DNS packets when file doesn't exist."""
        config = Mock()
        config.get_pcap_file_path.return_value = "/nonexistent/file.pcap"
        config.list_pcap_files.return_value = ["other.pcap"]
        config.pcap_path = "/test/path"
        config.is_remote = False

        module = DNSModule(config)

        with patch("os.path.exists", return_value=False):
            result = module.list_dns_packets("nonexistent.pcap")

        assert "error" in result
        assert "not found" in result["error"]
        assert result["available_files"] == ["other.pcap"]


class TestConfig:
    """Test configuration management."""

    def test_config_validation_success(self):
        """Test successful config validation."""
        with (
            patch("os.path.exists", return_value=True),
            patch("os.path.isdir", return_value=True),
        ):
            config = Config(pcap_path="/valid/path")
            assert config.pcap_path == "/valid/path"

    def test_config_validation_nonexistent_path(self):
        """Test config validation with nonexistent path."""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(ValueError, match="does not exist"):
                Config(pcap_path="/nonexistent/path")

    def test_config_validation_not_directory(self):
        """Test config validation when path is not a directory."""
        with (
            patch("os.path.exists", return_value=True),
            patch("os.path.isdir", return_value=False),
        ):
            with pytest.raises(ValueError, match="neither a file nor a directory"):
                Config(pcap_path="/path/to/file.txt")

    def test_get_pcap_file_path_absolute(self):
        """Test getting PCAP file path with absolute path."""
        with (
            patch("os.path.exists", return_value=True),
            patch("os.path.isdir", return_value=True),
        ):
            config = Config(pcap_path="/base/path")
            result = config.get_pcap_file_path("/absolute/path/file.pcap")
            assert result == "/absolute/path/file.pcap"

    def test_get_pcap_file_path_relative(self):
        """Test getting PCAP file path with relative path."""
        with (
            patch("os.path.exists", return_value=True),
            patch("os.path.isdir", return_value=True),
        ):
            config = Config(pcap_path="/base/path")
            result = config.get_pcap_file_path("relative.pcap")
            assert result == "/base/path/relative.pcap"
