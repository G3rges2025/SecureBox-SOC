#!/usr/bin/env python3
"""
simulate_attack.py

Usage:
  python simulate_attack.py --mode file
  python simulate_attack.py --mode http --login_url http://127.0.0.1:5000/

Behavior:
- Creates 4 IPs: two will be brute-force (5 attempts within 60s) and will trigger block.
- Writes lines to logs/sample.log or posts to HTTP login endpoint (Flask).
- Lines are in the same format as previously used: TIMESTAMP server sshd[PID]: Failed password for ...
"""
import argparse, time, random, os, sys
from datetime import datetime, timedelta

try:
    import requests
except Exception:
    requests = None

# sample IPs (2 will be brute force, 2 single fails). Pick public IPs that geo-lookup will map to the US.
BRUTE_IPS = ["8.8.8.8", "52.87.165.23"]      # these will get 5 attempts -> blocked
SINGLE_IPS = ["13.32.0.1", "3.227.47.238"]  # single failures

DEFAULT_LOG = os.path.join(os.path.dirname(__file__), "..", "logs", "sample.log")

def make_log_line(ip):
    # Example format: "Jul 19 02:16:28 login-system[1234]: Failed password for user admin from 127.0.0.1 port 22 ssh2"
    ts = datetime.utcnow().strftime("%b %d %H:%M:%S")
    # random user names for variety
    user = random.choice(["admin","root","testuser","guest","oracle"])
    return f"{ts} server sshd[12345]: Failed password for invalid user {user} from {ip} port {random.randint(1024,65535)} ssh2\n"

def append_to_file(path, line):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)

def post_to_http(url, ip):
    if not requests:
        raise RuntimeError("requests not installed in this environment.")
    # send as login form to simulate real login (server must accept)
    data = {"username":"invalid", "password":"bad", "remote_addr": ip}
    try:
        r = requests.post(url, data=data, timeout=3)
        return r.status_code, r.text[:200]
    except Exception as e:
        return None, str(e)

def run_file_mode(log_path, speed=0.2):
    # write BRUTE_IPS as 5 consecutive attempts each (to trigger block).
    now = datetime.utcnow()
    for ip in BRUTE_IPS:
        for i in range(5):
            line = make_log_line(ip)
            append_to_file(log_path, line)
            # small sleep to ensure timestamps are slightly different
            time.sleep(speed)
    # write single fails
    for ip in SINGLE_IPS:
        line = make_log_line(ip)
        append_to_file(log_path, line)
    print(f"[simulate_attack] Wrote brute + single fail lines to {log_path}")

def run_http_mode(login_url, speed=0.15):
    if not requests:
        print("requests not available; please pip install requests")
        sys.exit(1)
    for ip in BRUTE_IPS:
        for i in range(5):
            code, txt = post_to_http(login_url, ip)
            print(f"POST {login_url} from {ip} -> {code}")
            time.sleep(speed)
    for ip in SINGLE_IPS:
        code, txt = post_to_http(login_url, ip)
        print(f"POST {login_url} from {ip} -> {code}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["file","http"], default="file")
    p.add_argument("--log", help="Path to sample.log (file mode)", default=DEFAULT_LOG)
    p.add_argument("--login_url", help="Flask login URL (http mode)", default="http://127.0.0.1:5000/")
    p.add_argument("--speed", type=float, default=0.2, help="sleep between writes (sec)")
    args = p.parse_args()
    if args.mode == "file":
        run_file_mode(args.log, speed=args.speed)
    else:
        run_http_mode(args.login_url, speed=args.speed)
