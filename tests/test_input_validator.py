"""Tests for InputValidator simple cases."""
import pytest

from input_validation import InputValidator


@pytest.mark.parametrize("mac,expected", [
    ("AA:BB:CC:DD:EE:FF", True),
    ("aa:bb:cc:dd:ee:ff", True),
    ("AA-BB-CC-DD-EE-FF", True),
    ("AABBCCDDEEFF", False),
    ("GG:HH:II:JJ:KK:LL", False),
    ("", False),
])
def test_validate_mac(mac, expected):
    assert InputValidator.validate_mac_address(mac) is expected


@pytest.mark.parametrize("ssid,expected", [
    ("HomeWiFi", True),
    ("Guest_24G", True),
    (" ", True),
    ("", False),
    ("\x00bad", False),
    ("semi;colon", False),
])
def test_validate_ssid(ssid, expected):
    assert InputValidator.validate_ssid(ssid) is expected
