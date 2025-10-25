#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureBox Log Reader
Continuously monitors logs/sample.log, detects brute-force events,
enriches with GeoIP, and writes alerts JSONs for the dashboard.
"""

import os
import json
import time
import re
import geoip2.database
from datetime import datetime, timedelta

# ---------------------------------------------------------------------
# 📂 File paths
# ---------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_FILE = os.path.join(BASE_DIR, "logs", "sample.log")
ALERTS_DIR = os.path.join(BASE_DIR, "alerts")
ALERTS_FILE = os.path.join(ALERTS_DIR, "alerts.json")
BRUTE_FORCE_FILE = os.path.join(ALERTS_DIR, "brute_force.json")
BLOCKED_FILE = os.path.join(os.path.dirname(__file__), "blocked_ips.json")
GEO_DB = os.path.join(BASE_DIR, "GeoLite2-City.mmdb")  # optional local DB

os.makedirs(ALERTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------
# 🌍 GeoIP lookup
# ---------------------------------------------------------------------
def geo_lookup(ip):
    """Return {country, city, lat, lon} for given IP."""
    if not os.path.exists(GEO_DB):
        return None
    try:
        with geoip2.database.Reader(GEO_DB) as reader:
            res = reader.city(ip)
            return {
                "country": res.country.name,
                "city": res.city.name,
                "lat": res.location.latitude,
                "lon": res.location.longitude,
            }
    except Exception:
        return None

# ---------------------------------------------------------------------
# 🧩 Helpers
# ---------------------------------------------------------------------
def load_json_list(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            raw = f.read().strip()
        if not raw:
            return []
        data = json.loads(raw)
        return data["blocked"] if isinstance(data, dict) and "blocked" in data else data
    except Exception:
        return []

def save_json_list(path, data, key=None):
    payload = {key: data} if key else data
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------
# 🔍 Pattern definitions
# ---------------------------------------------------------------------
FAILED_PATTERN = re.compile(r"Failed password for (?:invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+)")
WINDOW = timedelta(seconds=60)
THRESHOLD = 5

recent_attempts = []
blocked_ips = load_json_list(BLOCKED_FILE)

def is_blocked(ip):
    return any((b.get("ip") == ip) if isinstance(b, dict) else (b == ip) for b in blocked_ips)

def block_ip(ip, reason):
    geo = geo_lookup(ip)
    entry = {
        "ip": ip,
        "blocked_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reason": reason,
        "geo": geo,
    }
    blocked_ips.append(entry)
    save_json_list(BLOCKED_FILE, blocked_ips, key="blocked")

def append_json_line(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------
# 🚨 Processing function
# ---------------------------------------------------------------------
def process_line(line):
    m = FAILED_PATTERN.search(line)
    if not m:
        return
    user, ip = m.groups()
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    geo = geo_lookup(ip)

    alert = {
        "timestamp": ts,
        "ip_address": ip,
        "log_entry": line.strip(),
        "severity": "Low",
        "geo": geo,
    }

    append_json_line(ALERTS_FILE, alert)

    # Add to recent attempts
    recent_attempts.append((ip, datetime.utcnow()))
    cutoff = datetime.utcnow() - WINDOW
    recent = [(i, t) for i, t in recent_attempts if t > cutoff]
    brute_counts = {}
    for i, _ in recent:
        brute_counts[i] = brute_counts.get(i, 0) + 1

    for i, count in brute_counts.items():
        if count >= THRESHOLD and not is_blocked(i):
            event = {
                "timestamp": ts,
                "ip_address": i,
                "log_entry": f"Brute-force detected: {i} had {count}+ failures within 60s",
                "severity": "High",
                "geo": geo_lookup(i),
            }
            append_json_line(BRUTE_FORCE_FILE, event)
            block_ip(i, "5+ failed logins within 60 seconds")

# ---------------------------------------------------------------------
# 🌀 Main loop
# ---------------------------------------------------------------------
def follow_log():
    """Continuously read new lines and process."""
    st_size = os.path.getsize(LOG_FILE) if os.path.exists(LOG_FILE) else 0
    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(st_size)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            process_line(line)

if __name__ == "__main__":
    print(f"[SecureBox] Monitoring: {LOG_FILE}")
    print("Press Ctrl+C to stop.")
    try:
        follow_log()
    except KeyboardInterrupt:
        print("\n[SecureBox] Stopped cleanly.")
