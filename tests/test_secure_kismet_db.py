"""Minimal tests for SecureKismetDB using a temporary SQLite file."""
import json
import sqlite3
import tempfile
import time
from pathlib import Path

from secure_database import SecureKismetDB


def _init_temp_db() -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp_path = Path(tmp.name)
    tmp.close()

    with sqlite3.connect(tmp_path.as_posix()) as con:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE devices (
                devmac TEXT,
                type TEXT,
                device TEXT,
                last_time REAL
            )
            """
        )
        now = time.time()
        device1 = {
            "dot11.device": {
                "dot11.device.last_probed_ssid_record": {
                    "dot11.probedssid.ssid": "TestSSID"
                }
            }
        }
        device2 = {
            "dot11.device": {}
        }
        cur.execute(
            "INSERT INTO devices (devmac, type, device, last_time) VALUES (?,?,?,?)",
            ("00:11:22:33:44:55", "dot11", json.dumps(device1), now - 10),
        )
        cur.execute(
            "INSERT INTO devices (devmac, type, device, last_time) VALUES (?,?,?,?)",
            ("66:77:88:99:AA:BB", "dot11", json.dumps(device2), now - 5),
        )
        con.commit()
    return tmp_path


def test_secure_kismet_db_queries():
    db_path = _init_temp_db()
    try:
        with SecureKismetDB(db_path.as_posix()) as db:
            assert db.validate_connection() is True

            # Fetch devices in the last hour
            start = time.time() - 3600
            devices = db.get_devices_by_time_range(start)
            macs = {d["mac"] for d in devices}
            assert {"00:11:22:33:44:55", "66:77:88:99:AA:BB"}.issubset(macs)

            # Fetch probes in the last hour (only one device has an SSID)
            probes = db.get_probe_requests_by_time_range(start)
            assert any(p["ssid"] == "TestSSID" for p in probes)
    finally:
        try:
            db_path.unlink()
        except Exception:
            pass
