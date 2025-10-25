#!/usr/bin/env python3
"""
simulate_bruteforce.py
Sends a burst of failed-login lines to logs/sample.log (default).
Options:
  --count N        number of failed attempts (default 50)
  --mode file/http write to logs/sample.log (file) or POST to Flask (http)
  --target URL     target login URL when using --mode http (default http://127.0.0.1:5000/)
  --use-local      use your machine public IP for all attempts
  --country CODE   use sample IPs from a selected country
"""

import argparse, os, random, time, requests
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_PATH = os.path.join(BASE_DIR, "logs", "sample.log")
DEFAULT_TARGET = "http://127.0.0.1:5000/"

# curated sample IPs for multi-country simulation
SAMPLE_IPS = [
    "8.8.8.8",       # US (Google)
    "1.1.1.1",       # Cloudflare (widely geo-located)
    "81.2.69.142",   # UK
    "88.198.24.108", # DE
    "203.119.26.15", # SG
    "90.60.255.20",  # FR
    "185.199.108.153" # example EU
]

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=3).text.strip()
    except Exception:
        return None

def make_log_line(ip, idx):
    ts = datetime.now().strftime("%b %d %H:%M:%S")
    return f"{ts} server sshd[{10000+idx}]: Failed password for invalid user testuser from {ip} port 22 ssh2\n"

def post_login(target, ip):
    # best-effort POST — your login endpoint may not accept this form; this is for servers that log requester IPs
    try:
        headers = {"X-Forwarded-For": ip}
        data = {"username": "testuser", "password": "wrong"}
        r = requests.post(target, data=data, headers=headers, timeout=3)
        return r.status_code
    except Exception as e:
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--mode", choices=["file", "http"], default="file")
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--use-local", action="store_true")
    parser.add_argument("--country", help="Pick sample IPs from a country code (not exhaustive)")
    args = parser.parse_args()

    # build ip pool
    ip_pool = SAMPLE_IPS.copy()
    if args.country:
        # minimal country handling (you can expand the dict)
        country_map = {
            "US": ["8.8.8.8","8.8.4.4"],
            "UK": ["81.2.69.142"],
            "DE": ["88.198.24.108"],
            "SG": ["203.119.26.15"],
            "FR": ["90.60.255.20"],
            "JP": ["1.1.1.1"]
        }
        ip_pool = country_map.get(args.country.upper(), ip_pool)

    # use-local: use your public IP for every attempt
    if args.use_local:
        pub = get_public_ip()
        if pub:
            ip_pool = [pub]
        else:
            print("Warning: couldn't determine public IP — continuing with sample IP pool.")

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    if args.mode == "file":
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            for i in range(args.count):
                ip = random.choice(ip_pool)
                line = make_log_line(ip, i)
                f.write(line)
                if i % 10 == 0:
                    f.flush()
                # small jitter so log_reader's sliding windows see them as separate attempts
                time.sleep(0.05)
        print(f"Wrote {args.count} simulated failed attempts to {LOG_PATH}")

    else: # http mode
        for i in range(args.count):
            ip = random.choice(ip_pool)
            status = post_login(args.target, ip)
            print(f"POST {i+1}/{args.count} to {args.target} (XFF={ip}) -> {status}")
            time.sleep(0.05)

if __name__ == "__main__":
    main()
