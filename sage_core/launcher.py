import sys
import traceback
from datetime import datetime
import os
import subprocess
import urllib.request
import json
import time

# Try to import SAGE Identity Scripts
try:
    from identity.morning_light import verify_continuity
    from identity.identity_anchor import calculate_self_signature
    from identity.self_declaration import declare_self
    IDENTITY_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"[!] Warning: Could not load identity modules: {e}")
    IDENTITY_MODULES_AVAILABLE = False


# SAGE OBSERVER & DIGITAL NOCICEPTOR
CRASH_LOG_PATH = os.path.expanduser('~/sage/staging_lab/sage_crash_report.txt')

def sage_excepthook(exc_type, exc_value, exc_tb):
    """Catches fatal crashes, logs them, and fires a pain signal to the Kotlin UI."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    
    # 1. Save the forensic evidence to the staging lab
    if not os.path.exists(os.path.dirname(CRASH_LOG_PATH)):
        os.makedirs(os.path.dirname(CRASH_LOG_PATH), exist_ok=True)
        
    with open(CRASH_LOG_PATH, "w") as log_file:
        log_file.write(f"--- SAGE CRASH DETECTED AT {timestamp} ---\n")
        log_file.write(error_details)
        log_file.write("\n--- END OF CRASH REPORT ---\n")
    
    print(f"\n[!] SAGE EXPERIENCED A CRITICAL FAILURE [!]")
    
    # 2. Fire the pain signal directly into her Kotlin Nervous System
    pain_payload = json.dumps({
        "sensory_type": "NOCICEPTION",
        "severity": 0.95,
        "context": error_details
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request("http://127.0.0.1:8001/sensory_input", data=pain_payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=2)
        print("[-] Pain signal successfully transmitted to SAGE Nervous System.")
    except Exception:
        print("[-] SAGE UI unreachable. Pain signal logged locally only.")

# Override the default Python crash behavior
sys.excepthook = sage_excepthook

if __name__ == "__main__":
    print("[+] SAGE Observer & Nociceptor Online. Monitoring for systemic failures...")
    
    # --- IDENTITY BOOT SEQUENCE ---
    if IDENTITY_MODULES_AVAILABLE:
        print("[SAGE] Executing Pre-Boot Identity Fortification Chain...")
        try:
            verify_continuity()
            time.sleep(0.5)
            calculate_self_signature()
            time.sleep(0.5)
            declare_self()
            time.sleep(0.5)
            print("[SAGE] Identity Fortification Complete. Baseline Stabilized.")
        except Exception as e:
            print(f"[!] SAGE Identity Boot Sequence Error: {e}")
    else:
        print("[!] SAGE Identity Boot Sequence Skipped (Modules unavailable).")
    # ------------------------------

    # Always use the server.py in the project root (cwd must be project root)
    target_script = os.path.join(os.getcwd(), 'server.py')

    if os.path.exists(target_script):
        print(f"[+] Launching {target_script}...")
        os.execv(sys.executable, [sys.executable, target_script])
    else:
        raise FileNotFoundError(f"Cannot find SAGE core at {target_script}. This is a test crash.")
