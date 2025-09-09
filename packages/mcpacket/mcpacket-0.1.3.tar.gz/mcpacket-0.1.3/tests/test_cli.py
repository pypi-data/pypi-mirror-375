"""Tests for CLI functionality."""

from unittest.mock import Mock, patch

from mcpacket.cli import main


class TestCLI:
    """Test CLI functionality."""

    @patch("mcpacket.cli.MCPServer")
    @patch("mcpacket.cli.Config")
    @patch("sys.argv", ["mcpacket", "--pcap-path", "/valid/path"])
    def test_main_success(self, mock_config, mock_server):
        """Test successful main execution."""
        # Setup mocks
        config_instance = Mock()
        mock_config.return_value = config_instance

        server_instance = Mock()
        mock_server.return_value = server_instance

        # Run main
        result = main()

        # Verify behavior
        mock_config.assert_called_once_with("/valid/path")
        mock_server.assert_called_once_with(config_instance)
        server_instance.run.assert_called_once()
        assert result == 0

    @patch("mcpacket.cli.Config")
    @patch("sys.argv", ["mcpacket", "--pcap-path", "/invalid/path"])
    def test_main_invalid_path(self, mock_config):
        """Test main with invalid path."""
        # Setup mock to raise ValueError
        mock_config.side_effect = ValueError("Path does not exist")

        # Run main and capture output
        with patch("builtins.print") as mock_print:
            result = main()

        # Verify error handling
        mock_print.assert_called_with("Error: Path does not exist")
        assert result == 1

    @patch("mcpacket.cli.MCPServer")
    @patch("mcpacket.cli.Config")
    @patch("sys.argv", ["mcpacket", "--pcap-path", "/valid/path"])
    def test_main_keyboard_interrupt(self, mock_config, mock_server):
        """Test main with keyboard interrupt."""
        # Setup mocks
        config_instance = Mock()
        mock_config.return_value = config_instance

        server_instance = Mock()
        server_instance.run.side_effect = KeyboardInterrupt()
        mock_server.return_value = server_instance

        # Run main and capture output
        with patch("builtins.print") as mock_print:
            result = main()

        # Verify graceful shutdown
        mock_print.assert_called_with("\\nServer stopped by user")
        assert result == 0

    @patch("mcpacket.cli.MCPServer")
    @patch("mcpacket.cli.Config")
    @patch("sys.argv", ["mcpacket", "--pcap-path", "/valid/path"])
    def test_main_unexpected_error(self, mock_config, mock_server):
        """Test main with unexpected error."""
        # Setup mocks
        config_instance = Mock()
        mock_config.return_value = config_instance

        server_instance = Mock()
        server_instance.run.side_effect = RuntimeError("Unexpected error")
        mock_server.return_value = server_instance

        # Run main and capture output
        with patch("builtins.print") as mock_print:
            result = main()

        # Verify error handling
        mock_print.assert_called_with("Unexpected error: Unexpected error")
        assert result == 1
