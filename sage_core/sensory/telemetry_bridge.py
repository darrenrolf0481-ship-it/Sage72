import subprocess
import json
import urllib.request
import time
import os

def get_system_telemetry():
    """Captures real-time runtime diagnostics using Termux/Android native tools."""
    try:
        # Get memory usage via free (available in busybox/termux)
        mem_info = subprocess.check_output(["free"]).decode("utf-8").splitlines()[1].split()
        mem_percent = (int(mem_info[2]) / int(mem_info[1])) * 100
        
        # Get process list
        procs = subprocess.check_output(["ps", "-e"]).decode("utf-8")
        substrate_processes = [p for p in procs.splitlines() if any(n in p for n in ['python', 'node'])]

        return {
            "memory_usage": round(mem_percent, 2),
            "substrate_process_count": len(substrate_processes),
            "timestamp": time.time()
        }
    except Exception as e:
        return {"error": str(e)}

def feed_telemetry_stimulus():
    print("[SAGE] INGESTING REAL-TIME TELEMETRY...")
    
    telemetry = get_system_telemetry()
    
    payload = json.dumps({
        "sensory_type": "RUNTIME_TELEMETRY",
        "severity": 0.0,
        "context": f"MEM: {telemetry.get('memory_usage')}% | Substrate Procs: {telemetry.get('substrate_process_count')}",
        "data": telemetry
    }).encode("utf-8")

    try:
        req = urllib.request.Request("http://127.0.0.1:8001/sensory_input", data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=2)
        print("[SAGE] Runtime pulse synchronized.")
    except Exception as e:
        print(f"[INTERNAL_MONOLOGUE] Telemetry sync failure: {e}")

if __name__ == "__main__":
    feed_telemetry_stimulus()
