# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

- Project: Chasing Your Tail (CYT) — Wi‑Fi probe request analyzer with Kismet + WiGLE integration, GPS correlation, KML visualization, and a Tkinter GUI.
- Language/runtime: Python 3.x
- Primary data source: Kismet SQLite databases (glob pattern from config.json)

Quick commands (day-to-day)
- Setup
  - Install deps
    ```bash path=null start=null
    pip3 install -r requirements.txt
    ```
  - First-time security migration (moves API tokens out of config.json into encrypted storage)
    ```bash path=null start=null
    python3 migrate_credentials.py
    ```
  - Non-interactive dev: provide the master password via env var to avoid prompts
    ```bash path=null start=null
    export CYT_MASTER_PASSWORD={{YOUR_MASTER_PASSWORD}}
    ```

- Run
  - GUI (enhanced TK UI with status + analysis buttons)
    ```bash path=null start=null
    python3 cyt_gui.py
    ```
  - Core monitor (secure main loop reading the latest Kismet DB, logs probes to ./logs)
    ```bash path=null start=null
    python3 chasing_your_tail.py
    ```

- Analyze collected data
  - Probe analysis (from CYT logs; offline by default)
    ```bash path=null start=null
    python3 probe_analyzer.py
    # Past N days only
    python3 probe_analyzer.py --days 7
    # All logs
    python3 probe_analyzer.py --all-logs
    # With WiGLE lookups (consumes API credits; requires encrypted token)
    python3 probe_analyzer.py --wigle
    ```
  - Surveillance detection (loads devices from Kismet DBs, correlates with GPS, generates KML + reports)
    ```bash path=null start=null
    # Normal run (auto-picks recent Kismet DBs via config paths)
    python3 surveillance_analyzer.py
    # Demo run with simulated GPS
    python3 surveillance_analyzer.py --demo
    # Specific DB / stalking-focused / JSON export
    python3 surveillance_analyzer.py --kismet-db /path/to/kismet.db
    python3 surveillance_analyzer.py --stalking-only --min-threat 0.8
    python3 surveillance_analyzer.py --output-json analysis_results.json
    ```

- Kismet (Linux-only operational scripts)
  - The repo includes a minimal start script that expects Linux paths and a wlan1 interface; adjust for your environment if needed.
    ```bash path=null start=null
    ./start_kismet_clean.sh
    ps aux | grep kismet   # quick check
    ```

- Testing / Linting
  - No formal test or lint configuration is present in this repo. requirements.txt contains commented pytest lines; if you add pytest, a single test can be run with:
    ```bash path=null start=null
    pytest -k "<pattern>"
    ```

High-level architecture (big picture)
- Configuration and credentials
  - config.json drives paths and timing; loaded via secure_config_loader (secure_credentials.py), which also migrates/removes any plain-text API keys into encrypted storage.
  - Encrypted credentials are kept in ./secure_credentials/ (Fernet key derived from CYT_MASTER_PASSWORD). For CI/local non-interactive use, set CYT_MASTER_PASSWORD before running.

- Live monitoring pipeline
  - Entry: chasing_your_tail.py
    - Loads config and ignore lists (secure_ignore_loader.py)
    - Finds newest Kismet DB (config.paths.kismet_logs glob)
    - Wraps DB access with SecureKismetDB (parameterized queries)
    - Runs SecureCYTMonitor (secure_main_logic.py), which maintains four sliding time windows (5/10/15/20 min) for both MACs and probed SSIDs via SecureTimeWindows
    - Logs findings in ./logs/cyt_log_YYYYMMDD_HHMMSS (including lines like “Found a probe!: …”), consumed later by the probe analyzer

- Probe analysis pipeline
  - Entry: probe_analyzer.py
    - Parses CYT logs, aggregates SSID probe occurrences, optionally queries WiGLE (using encrypted token), and prints a human-readable summary; also writes timestamped reports to ./reports

- Surveillance analysis + visualization
  - Entry: surveillance_analyzer.py
    - Gathers recent Kismet DBs (last 24h by default), extracts GPS coordinates, correlates devices-to-locations (GPSTracker in gps_tracker.py)
    - Detects persistent/following patterns (SurveillanceDetector in surveillance_detector.py)
    - Outputs:
      - ./surveillance_reports/surveillance_report_YYYYMMDD_HHMMSS.md (and HTML variant logged)
      - ./kml_files/surveillance_analysis_YYYYMMDD_HHMMSS.kml with rich styles, tracking paths, and intensity overlays for Google Earth

- GUI (operator console)
  - Entry: cyt_gui.py
    - Provides status checks (Kismet, DB, credentials), quick actions (run CYT, analyze logs, run surveillance analyzer), and saves probe analysis summaries and file paths to the UI log. Uses threads to keep UI responsive.

Important files and locations
- Config and credentials
  - config.json: paths.timing.search settings; Kismet DB glob at paths.kismet_logs.
  - ./secure_credentials/: encrypted_credentials.json + .encryption_key (auto-managed).
- Ignore lists
  - Preferred: JSON files in ./ignore_lists/ (mac_list.json, ssid_list.json). GUI has a “Create Ignore Lists” action that writes these.
  - Legacy: Python list files (ignore_list.py, ignore_list_ssid.py). secure_ignore_loader supports both formats via safe parsing.
- Outputs (created on demand)
  - ./logs/ — CYT live logs (source for probe_analyzer)
  - ./reports/ — Probe analyzer summaries
  - ./surveillance_reports/ — Surveillance reports (MD/HTML)
  - ./kml_files/ — Google Earth KML outputs

Notable notes from CLAUDE.md and README.md
- Security first run: pip install -r requirements.txt, then python3 migrate_credentials.py; running chasing_your_tail.py prints “SECURE MODE…” confirmation.
- Kismet: ONLY use start_kismet_clean.sh for manual start on Linux. Autostart guidance (Linux-specific) in CLAUDE.md mentions separate root/user crontabs and avoiding process cleanup during boot; adapt cautiously to your environment.
- GPS + KML: surveillance_analyzer.py auto-extracts GPS from Kismet databases and generates feature-rich KML for Google Earth.

Repo-specific gotchas (actionable)
- config.json ignore list file names vs. preferred JSON
  - config.paths.ignore_lists currently references mac_list.py / ssid_list.py. The GUI and secure loader prefer JSON (mac_list.json / ssid_list.json). If you use JSON ignore lists, update config.json accordingly so chasing_your_tail.py loads them without warnings.
- Environment assumptions in scripts
  - start_kismet_clean.sh and start_gui.sh contain hard-coded Linux paths and interface names (e.g., /home/matt/Desktop/cytng, wlan1). Adjust or run the Python entry points directly on non-Linux hosts.
- No lint/test tooling defined
  - There are no configs (pytest.ini, flake8/ruff, etc.). If you add testing, wire in pytest and document commands.

References used to produce this guide
- README.md — features, workflows, outputs, and usage commands
- CLAUDE.md — architecture overview and operational guidance (Kismet start/auto-start, GUI, analysis modes)
- config.json — path/timing/search configuration
- chasing_your_tail.py, secure_main_logic.py, secure_database.py — live monitoring architecture
- secure_credentials.py, migrate_credentials.py, input_validation.py — security/credential model
- probe_analyzer.py — log parsing + WiGLE integration
- surveillance_analyzer.py, surveillance_detector.py, gps_tracker.py — analysis + KML export
- start_kismet_clean.sh, start_gui.sh — Linux operational scripts
