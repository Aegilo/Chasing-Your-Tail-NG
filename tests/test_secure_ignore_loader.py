"""Test SecureIgnoreLoader functionality."""
import json
import tempfile
from pathlib import Path

from secure_ignore_loader import SecureIgnoreLoader


def test_load_mac_list_json():
    """Test loading MAC addresses from JSON format."""
    test_macs = ["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66", "invalid-mac"]
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_macs, f)
        f.flush()
        
        result = SecureIgnoreLoader.load_mac_list(Path(f.name))
        # Should validate and uppercase valid MACs, skip invalid ones
        assert len(result) == 2
        assert "AA:BB:CC:DD:EE:FF" in result
        assert "11:22:33:44:55:66" in result


def test_load_ssid_list_json():
    """Test loading SSIDs from JSON format."""
    test_ssids = ["MyNetwork", "Guest_WiFi", ""]
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_ssids, f)
        f.flush()
        
        result = SecureIgnoreLoader.load_ssid_list(Path(f.name))
        # Should include valid SSIDs, skip empty ones
        assert len(result) == 2
        assert "MyNetwork" in result
        assert "Guest_WiFi" in result