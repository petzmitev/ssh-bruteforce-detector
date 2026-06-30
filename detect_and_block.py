
import re
import subprocess
from datetime import datetime

LOG_FILE = "/var/log/auth.log"
BLOCKED_LOG = "blocked_ips.log"
THRESHOLD = 5

def is_already_blocked(ip):
    try:
        with open(BLOCKED_LOG, "r") as f:
            for line in f:
                if f"Blocked IP: {ip}" in line:
                    return True
    except FileNotFoundError:
        pass
        
    return False


def block_ip(ip):
    if is_already_blocked(ip):
        print(f"[ℹ️] IP вече е блокиран: {ip}")
        return
    
    subprocess.run(["sudo", "ufw", "deny", "from", ip], stdout=subprocess.DEVNULL)
    with open(BLOCKED_LOG, "a") as f:
        f.write(f"{datetime.now()} - Blocked IP: {ip}\n")
    print(f"[⚠️] IP блокиран: {ip}")

def detect_failed_logins():
    
    failed_attempts = {}
    pattern = re.compile(r"Failed password for .* from (\d+\.\d+\.\d+\.\d+)")

    with open(LOG_FILE, "r", errors="ignore") as log:
        for line in log:
            match = pattern.search(line)
            if match:
                ip = match.group(1)
                failed_attempts[ip] = failed_attempts.get(ip, 0) + 1

    for ip, count in failed_attempts.items():
        if count >= THRESHOLD:
            block_ip(ip)

if __name__ == "__main__":
    print("[🔍] Сканиране на логовете за brute-force атаки...")
    detect_failed_logins()
    print("[✅] Сканирането приключи.")
