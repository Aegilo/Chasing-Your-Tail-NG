"""Minimal test for SurveillanceDetector scoring behavior."""
import time

from surveillance_detector import SurveillanceDetector


def test_surveillance_detector_basic_scoring():
    cfg = {}
    det = SurveillanceDetector(cfg)

    now = time.time()
    mac = "AA:BB:CC:DD:EE:FF"

    # 3+ appearances over > 1 hour across 2 locations
    det.add_device_appearance(mac, now - 7200, "loc1")
    det.add_device_appearance(mac, now - 3600, "loc2")
    det.add_device_appearance(mac, now - 60, "loc2")

    suspects = det.analyze_surveillance_patterns()

    # Should flag at least one device as suspicious with non-zero score
    assert any(d.mac == mac and d.persistence_score > 0 for d in suspects)
