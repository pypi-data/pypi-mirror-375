"""Configuration management for mcpacket."""

import os
from typing import Optional


class Config:
    """Configuration management for mcpacket server."""
    
    def __init__(self, pcap_path: str):
        """Initialize configuration.
        
        Args:
            pcap_path: Path to directory containing PCAP files
        """
        self.pcap_path = pcap_path
        self._validate_pcap_path()
    
    def _validate_pcap_path(self) -> None:
        """Validate that the PCAP path exists and is a directory."""
        if not os.path.exists(self.pcap_path):
            raise ValueError(f"PCAP directory '{self.pcap_path}' does not exist")
        
        if not os.path.isdir(self.pcap_path):
            raise ValueError(f"'{self.pcap_path}' is not a directory")
    
    def get_pcap_file_path(self, pcap_file: str) -> str:
        """Get full path to a PCAP file.
        
        Args:
            pcap_file: Filename or relative path to PCAP file
            
        Returns:
            Full path to the PCAP file
        """
        if os.path.isabs(pcap_file):
            return pcap_file
        return os.path.join(self.pcap_path, pcap_file)
    
    def list_pcap_files(self) -> list[str]:
        """List all PCAP files in the configured directory.
        
        Returns:
            List of PCAP filenames
        """
        try:
            return [
                f for f in os.listdir(self.pcap_path)
                if f.endswith((".pcap", ".pcapng"))
            ]
        except Exception:
            return []