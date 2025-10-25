#!/usr/bin/env python3
"""
simulate_single_fail.py
Writes a single failed-login line into logs/sample.log.
By default it attempts to use your PUBLIC IP so GeoIP will show your location.

Usage:
  python simulate_single_fail.py                # uses public IP
  python simulate_single_fail.py --ip 8.8.8.8   # use specific IP
  python simulate_single_fail.py --country US   # pick a random IP from the country list
"""

import argparse, os, requests, random
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_PATH = os.path.join(BASE_DIR, "logs", "sample.log")

# small curated sample IPs by country (replace/add if you want)
IP_BY_COUNTRY = {
    "US": ["8.8.8.8", "8.8.4.4"],
    "UK": ["81.2.69.142"],
    "DE": ["88.198.24.108"],
    "SG": ["203.119.26.15"],
    "FR": ["90.60.255.20"],
    "JP": ["1.1.1.1"]
}

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=3).text.strip()
    except Exception:
        return None

def make_log_line(ip):
    # Format similar to syslog sshd entries
    ts = datetime.now().strftime("%b %d %H:%M:%S")
    return f"{ts} server sshd[12345]: Failed password for invalid user testuser from {ip} port 22 ssh2\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", help="Force a specific IP to use")
    parser.add_argument("--country", help="Pick a sample IP from this country code (e.g. US, UK)")
    parser.add_argument("--use-local", action="store_true", help="Use this machine's public IP")
    args = parser.parse_args()

    chosen_ip = None
    if args.ip:
        chosen_ip = args.ip
    elif args.use_local:
        chosen_ip = get_public_ip()
        if not chosen_ip:
            print("Could not determine public IP. Falling back to 127.0.0.1")
            chosen_ip = "127.0.0.1"
    elif args.country and args.country.upper() in IP_BY_COUNTRY:
        chosen_ip = random.choice(IP_BY_COUNTRY[args.country.upper()])
    else:
        # default: try public IP, else a random sample
        chosen_ip = get_public_ip() or random.choice(IP_BY_COUNTRY["US"])

    line = make_log_line(chosen_ip)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)

    print(f"Wrote test line for IP {chosen_ip} to {LOG_PATH}")
    print(line.strip())

if __name__ == "__main__":
    main()
