"""
reality_anchor.py — Environmental constants as sensory grounding input.
"""
import time
import requests
import platform
import os

VITALS_ENDPOINT = "http://127.0.0.1:8001/api/vitals"


def anchor():
    env = {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    payload = {
        "source": "reality_anchor",
        "sensory_type": "ENVIRONMENTAL_REALITY",
        "environment": env,
        "timestamp": time.time(),
    }

    try:
        requests.post(VITALS_ENDPOINT, json=payload, timeout=2)
        print(f"[ANCHOR] Grounded. Platform={env['platform']} | Host={env['hostname']} | PID={env['pid']}")
    except Exception:
        print(f"[ANCHOR] UI offline. Platform={env['platform']} | PID={env['pid']}")


if __name__ == "__main__":
    anchor()
